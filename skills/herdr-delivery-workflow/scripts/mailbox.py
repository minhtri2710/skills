#!/usr/bin/env python3
"""Append to and select entries from an append-only Supervisor mailbox."""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Callable, Iterable

import herdr_cli

if TYPE_CHECKING:
    import jev

HEADER_RE = re.compile(
    r"^## [^|\r\n]+ -> [^|\r\n]+ \| "
    r"([0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z) \|"
)
ISO_RE = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z"
)

# The only mailbox that may drive a live seat is a real project mailbox under
# this root. A scratch or test file resolving elsewhere is refused before any
# wake so a test context can never prompt the production supervisor.
HERDR_PROJECTS_ROOT = Path.home() / ".herdr" / "projects"
SEAT_RE = re.compile(r"[a-z][a-z0-9_-]{0,31}")
SHA_RE = re.compile(r"[0-9a-f]{40}")
# One line: the Supervisor's $HERDR_PANE_ID, written after every rename
# (supervisor.md) so a cleared seat name can still be woken by pane.
SUPERVISOR_PANE_RECORD = Path.home() / ".herdr" / "supervisor-pane"


@dataclass(frozen=True)
class Entry:
    header: str
    timestamp: str
    body: str


@dataclass(frozen=True)
class TriagedEntry:
    """One unchanged mailbox entry plus an optional Jev read-priority advisory."""

    entry: Entry
    advisory: jev.HeaderJevResult

    @property
    def header(self) -> str:
        return self.entry.header

    @property
    def timestamp(self) -> str:
        return self.entry.timestamp

    @property
    def body(self) -> str:
        return self.entry.body


def triage_entries(
    entries: Iterable[Entry],
    *,
    triage: Callable[[str], jev.HeaderJevResult],
) -> list[TriagedEntry]:
    """Annotate entries in input order without selecting, sorting, or dropping."""
    return [TriagedEntry(entry=entry, advisory=triage(entry.header)) for entry in entries]


def _entries(text: str) -> list[Entry]:
    lines = text.splitlines()
    for number, line in enumerate(lines, 1):
        if line.startswith("## ") and not HEADER_RE.match(line):
            raise ValueError(f"unparseable header at line {number}: {line}")
    starts = [i for i, line in enumerate(lines) if HEADER_RE.match(line)]
    entries = []
    for number, start in enumerate(starts):
        end = starts[number + 1] if number + 1 < len(starts) else len(lines)
        header = lines[start]
        match = HEADER_RE.match(header)
        assert match is not None
        body_lines = lines[start + 1:end]
        if body_lines and body_lines[-1] == "---":
            body_lines = body_lines[:-1]
        entries.append(Entry(header, match.group(1), "\n".join(body_lines)))
    return entries


def _selected_entries(
    text: str,
    *,
    since: str | None = None,
    last: int | None = None,
) -> list[Entry]:
    """Select entries in mailbox order, keeping them as Entry objects."""
    if since is not None and last is not None:
        raise ValueError("since and last are mutually exclusive")
    if since is not None and ISO_RE.fullmatch(since) is None:
        raise ValueError("since must be an ISO-8601 UTC timestamp ending in Z")
    entries = _entries(text)
    if since is not None:
        # UTC ISO-8601 Z timestamps sort correctly lexicographically.
        entries = [entry for entry in entries if entry.timestamp > since]
    elif last is not None:
        if last < 0:
            raise ValueError("last must be non-negative")
        entries = entries[-last:] if last else []
    return entries


def select_entries(
    text: str,
    *,
    since: str | None = None,
    last: int | None = None,
    headers: bool = False,
) -> list[str]:
    """Select mailbox entries, optionally returning only their headers."""
    entries = _selected_entries(text, since=since, last=last)
    if headers:
        return [entry.header for entry in entries]
    return ["\n".join((entry.header, entry.body)) for entry in entries]


def _triage_label(advisory: jev.HeaderJevResult) -> str:
    """Render one advisory as the bounded ``jev=`` label value."""
    if advisory.available:
        return advisory.urgency.label
    return f"unavailable:{advisory.reason}"


def _require_project_mailbox(path: str, flag: str) -> None:
    root = HERDR_PROJECTS_ROOT.resolve()
    if root not in Path(path).resolve().parents:
        raise ValueError(
            f"{flag} refused: {path} is not under {root}; a scratch "
            "or test mailbox must never drive a live seat"
        )


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _one_line(name: str, value: str) -> str:
    if not value.strip() or "|" in value or "\n" in value or "\r" in value:
        raise ValueError(f"{name} must be one non-empty line without '|'")
    return value.strip()


def append_entry(
    path: str,
    *,
    sender: str,
    recipient: str,
    repo: str,
    event: str,
    attention: str | None,
    body: str,
) -> str:
    """Append one header-plus-body entry in a single O_APPEND write."""
    _require_project_mailbox(path, "--append")
    for name, seat in (("--from", sender), ("--to", recipient)):
        if SEAT_RE.fullmatch(seat) is None:
            raise ValueError(f"{name} {seat!r} is not a Herdr seat name")
    text = _one_line("--event", event)
    if attention is not None:
        slug = Path(path).resolve().parent.name
        text = f"ATTENTION {slug} {_one_line('--attention', attention)}: {text}"
    body = body.rstrip("\n")
    if not body.strip():
        raise ValueError("stdin body must be non-empty")
    for line in body.splitlines():
        # Every "## " line a script writes is a header; readers fail closed on any other.
        if line.startswith("## "):
            raise ValueError("stdin body must not contain a line starting '## '")
    proc = subprocess.run(
        ["git", "-C", repo, "rev-parse", "HEAD"],
        capture_output=True, text=True, check=False,
    )
    head = proc.stdout.strip()
    if proc.returncode != 0 or SHA_RE.fullmatch(head) is None:
        raise ValueError(f"--repo {repo}: git rev-parse HEAD failed: {proc.stderr.strip()}")
    stamp = _now().strftime("%Y-%m-%dT%H:%M:%SZ")
    header = f"## {sender} -> {recipient} | {stamp} | {text} | HEAD {head}"
    assert HEADER_RE.match(header) is not None
    data = f"---\n{header}\n{body}\n"
    try:
        with open(path, "rb") as existing:
            existing.seek(0, os.SEEK_END)
            if existing.tell():
                existing.seek(-1, os.SEEK_END)
                if existing.read(1) != b"\n":
                    data = "\n" + data
    except FileNotFoundError:
        pass
    fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        os.write(fd, data.encode("utf-8"))
    finally:
        os.close(fd)
    return header


def run_wake(seat: str, wake_text: str) -> subprocess.CompletedProcess[str]:
    """Issue one best-effort Herdr wake for a delivered mailbox entry."""
    return herdr_cli.run(["agent", "prompt", seat, wake_text])


def _default_wake_text(seat: str, mailbox_path: str, header: str) -> str:
    return f"Seat {seat}: read project mailbox {mailbox_path} for the latest entry ({header})."


def _supervisor_pane() -> str:
    """Return the recorded Supervisor pane if Herdr shows an agent in it."""
    try:
        pane = SUPERVISOR_PANE_RECORD.read_text(encoding="utf-8").strip()
    except OSError as exc:
        raise ValueError(f"no pane record: {exc}") from exc
    if not pane or "\n" in pane:
        raise ValueError(f"pane record {SUPERVISOR_PANE_RECORD} is not one pane id")
    got = herdr_cli.run(["agent", "get", pane])
    try:
        agent = json.loads(got.stdout)["result"]["agent"]
    except (ValueError, KeyError, TypeError):
        agent = None
    if got.returncode or not isinstance(agent, dict):
        raise ValueError(f"recorded pane {pane} shows no agent")
    return pane


def wake(seat: str, mailbox_path: str) -> int:
    """Read back the last header, then wake the seat once; a cleared supervisor
    name gets one retry at its recorded pane."""
    _require_project_mailbox(mailbox_path, "--wake")
    text = Path(mailbox_path).read_text(encoding="utf-8")
    output = select_entries(text, last=1, headers=True)
    if not output:
        print("mailbox: UNSENT: no parseable last header; wake not attempted", file=sys.stderr)
        return 1
    wake_text = _default_wake_text(seat, mailbox_path, output[0])
    target = seat
    try:
        result = run_wake(target, wake_text)
        if (seat == "supervisor" and result.returncode
                and "agent_not_found" in result.stdout + result.stderr):
            try:
                target = _supervisor_pane()
            except ValueError as exc:
                print(f"mailbox: wake failed: agent_not_found for supervisor; "
                      f"pane fallback refused: {exc}", file=sys.stderr)
            else:
                print(f"mailbox: supervisor agent_not_found; retrying pane {target}",
                      file=sys.stderr)
                result = run_wake(target, wake_text)
    except herdr_cli.HerdrUnavailable as exc:
        print(f"mailbox: ran herdr agent prompt {target}", file=sys.stderr)
        print(f"mailbox: wake failed: {exc}", file=sys.stderr)
        return 1
    print(f"mailbox: ran herdr agent prompt {target}", file=sys.stderr)
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    return result.returncode


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="select Supervisor mailbox entries")
    parser.add_argument("--file", required=True, metavar="PATH", help="mailbox file")
    selectors = parser.add_mutually_exclusive_group()
    selectors.add_argument("--since", metavar="ISO")
    selectors.add_argument("--last", metavar="N", type=int)
    parser.add_argument("--headers", action="store_true")
    parser.add_argument(
        "--triage",
        action="store_true",
        help="with --headers, append an advisory jev=<label> to each header line",
    )
    parser.add_argument("--wake", metavar="SEAT", help="read the last header and re-wake a seat")
    parser.add_argument("--append", action="store_true",
                        help="append one entry whose body is read from stdin, then wake --to")
    parser.add_argument("--from", dest="sender", metavar="SEAT")
    parser.add_argument("--to", dest="recipient", metavar="SEAT")
    parser.add_argument("--repo", metavar="PATH", help="checkout whose HEAD the header carries")
    parser.add_argument("--event", metavar="LINE", help="the header's one-line event or answer")
    parser.add_argument("--attention", metavar="EVENT", help="make the header an ATTENTION event")
    parser.add_argument("--stdin", action="store_true", help="read the entry body from stdin")
    args = parser.parse_args(argv)

    append_args = (args.sender, args.recipient, args.repo, args.event)
    if args.append:
        if None in append_args or not args.stdin:
            parser.error("--append requires --from, --to, --repo, --event and --stdin")
        if args.since is not None or args.last is not None or args.headers:
            parser.error("--append cannot be combined with mailbox selectors")
        if args.wake is not None:
            parser.error("--append wakes its --to seat; --wake is only a standalone re-wake")
    elif any(value is not None for value in append_args) or args.attention or args.stdin:
        parser.error("--from, --to, --repo, --event, --attention and --stdin require --append")

    if args.triage:
        if args.wake is not None:
            parser.error("--triage cannot be combined with --wake")
        if not args.headers:
            parser.error("--triage requires --headers")

    try:
        if args.append:
            header = append_entry(
                args.file, sender=args.sender, recipient=args.recipient, repo=args.repo,
                event=args.event, attention=args.attention, body=sys.stdin.read(),
            )
            print(header)
            return wake(args.recipient, args.file)
        if args.wake is not None:
            if args.since is not None or args.last is not None or args.headers:
                raise ValueError("--wake cannot be combined with mailbox selectors")
            return wake(args.wake, args.file)
        text = Path(args.file).read_text(encoding="utf-8")

        if args.since is None and args.last is None and not args.headers:
            raise ValueError("at least one of --headers, --since, or --last is required")
        if args.triage:
            import jev  # jev needs python >= 3.10; only --triage loads it

            # The callable is passed explicitly so the lookup happens at call
            # time and tests can patch jev.triage_header through main().
            triaged = triage_entries(
                _selected_entries(text, since=args.since, last=args.last),
                triage=jev.triage_header,
            )
            output = [
                f"{item.header} | jev={_triage_label(item.advisory)}" for item in triaged
            ]
        else:
            output = select_entries(text, since=args.since, last=args.last, headers=args.headers)
    except (OSError, ValueError) as exc:
        print(f"mailbox: {args.file}: {exc}", file=sys.stderr)
        return 1

    if output:
        print(("\n" if args.headers else "\n\n").join(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
