#!/usr/bin/env python3
"""Append to and select entries from an append-only Supervisor mailbox."""
from __future__ import annotations

import argparse
import os
import re
import subprocess
import sys
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

import backend
import state_root

ISO_RE = re.compile(
    r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z"
)
HEADER_RE = re.compile(
    r"^## (?P<sender>[^|\r\n]+) -> (?P<recipient>[^|\r\n]+) \| "
    rf"(?P<timestamp>{ISO_RE.pattern}) \|"
    r"(?P<event>.*?)(?: \| HEAD (?P<head>[0-9a-f]{7,40}))?\s*$"
)
ATTENTION = "ATTENTION "

SEAT_RE = re.compile(r"[a-z][a-z0-9_-]{0,31}")
SHA_RE = re.compile(r"[0-9a-f]{40}")


@dataclass(frozen=True)
class Header:
    line: str
    sender: str
    recipient: str
    timestamp: str
    event: str
    head: str | None
    attention: str | None


@dataclass(frozen=True)
class Entry:
    header: Header
    body: str


def parse_header(line: str) -> Header | None:
    """The fields of a header line this module writes, or None when the line is not one."""
    match = HEADER_RE.match(line)
    if match is None:
        return None
    event = match["event"].strip()
    attention = event[len(ATTENTION):] if event.startswith(ATTENTION) else None
    return Header(
        line, match["sender"], match["recipient"], match["timestamp"], event,
        match["head"], attention or None,
    )


def attention_text(slug: str, kind: str, event: str) -> str:
    return f"{ATTENTION}{slug} {kind}: {event}"


def _entries(text: str) -> list[Entry]:
    lines = text.splitlines()
    headers = []
    for number, line in enumerate(lines, 1):
        header = parse_header(line)
        if header is not None:
            headers.append((number - 1, header))
        elif line.startswith("## "):
            raise ValueError(f"unparseable header at line {number}: {line}")
    entries = []
    for index, (start, header) in enumerate(headers):
        end = headers[index + 1][0] if index + 1 < len(headers) else len(lines)
        body_lines = lines[start + 1:end]
        if body_lines and body_lines[-1] == "---":
            body_lines = body_lines[:-1]
        entries.append(Entry(header, "\n".join(body_lines)))
    return entries


def _selected_entries(
    text: str,
    *,
    since: str | None = None,
    last: int | None = None,
) -> list[Entry]:
    if since is not None and ISO_RE.fullmatch(since) is None:
        raise ValueError("since must be an ISO-8601 UTC timestamp ending in Z")
    entries = _entries(text)
    if since is not None:
        entries = [entry for entry in entries if entry.header.timestamp > since]
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
    entries = _selected_entries(text, since=since, last=last)
    if headers:
        return [entry.header.line for entry in entries]
    return ["\n".join((entry.header.line, entry.body)) for entry in entries]


def _project_slug(path: str, flag: str) -> str:
    # The only mailbox that may drive a live seat is a real project mailbox under
    # the state root. A scratch or test file resolving elsewhere is refused before
    # any wake so a test context can never prompt the production supervisor.
    try:
        return state_root.mailbox_slug(path)
    except ValueError as exc:
        raise ValueError(
            f"{flag} refused: {exc}; a scratch or test mailbox must never drive a live seat"
        ) from exc


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
    body: str | None,
) -> str:
    slug = _project_slug(path, "--append")
    if SEAT_RE.fullmatch(sender) is None:
        raise ValueError(f"--from {sender!r} is not a seat name: {SEAT_RE.pattern}")
    state_root.seat_record(slug, recipient)
    text = _one_line("--event", event)
    if attention is not None:
        text = attention_text(slug, _one_line("--attention", attention), text)
    body = None if body is None else body.rstrip("\n")
    if body is not None and not body.strip():
        raise ValueError("stdin body must be non-empty")
    for line in (body or "").splitlines():
        # Every "## " line a script writes is a header; readers fail closed on any other.
        if line.startswith("## "):
            raise ValueError("stdin body must not contain a line starting '## '")
    proc = subprocess.run(
        ["git", "-C", repo, "rev-parse", "HEAD"],
        capture_output=True, text=True, encoding="utf-8", check=False,
    )
    head = proc.stdout.strip()
    if proc.returncode != 0 or SHA_RE.fullmatch(head) is None:
        raise ValueError(f"--repo {repo}: git rev-parse HEAD failed: {proc.stderr.strip()}")
    stamp = _now().strftime("%Y-%m-%dT%H:%M:%SZ")
    header = f"## {sender} -> {recipient} | {stamp} | {text} | HEAD {head}"
    data = f"---\n{header}\n" + ("" if body is None else f"{body}\n")
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


def _default_wake_text(seat: str, mailbox_path: str, header: str) -> str:
    return f"Seat {seat}: read project mailbox {mailbox_path} for the latest entry ({header})."


def wake(role: str, mailbox_path: str, open_backend: Callable[[], backend.Backend]) -> int:
    slug = _project_slug(mailbox_path, "--wake")
    text = Path(mailbox_path).read_text(encoding="utf-8")
    output = select_entries(text, last=1, headers=True)
    if not output:
        print("mailbox: UNSENT: no parseable last header; wake not attempted", file=sys.stderr)
        return 1
    wake_text = _default_wake_text(role, mailbox_path, output[0])
    try:
        record = state_root.seat_record(slug, role)
        try:
            recorded = backend.read_seat_record(record)
        except (OSError, ValueError) as exc:
            raise ValueError(f"no usable {role} seat record: {exc}") from exc
        seats = open_backend()
        if recorded.name != seats.name:
            raise ValueError(
                f"{role} seat record names {recorded.name}, this seat runs under {seats.name}; "
                "no cross-backend wake"
            )
        seats.prompt(recorded.handle, wake_text)
    except (backend.BackendError, ValueError) as exc:
        print(f"mailbox: wake failed: {exc}", file=sys.stderr)
        return 1
    print(f"mailbox: prompted {recorded.handle} on {seats.name}", file=sys.stderr)
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="select Supervisor mailbox entries")
    parser.add_argument("--file", required=True, metavar="PATH", help="mailbox file")
    selectors = parser.add_mutually_exclusive_group()
    selectors.add_argument("--since", metavar="ISO")
    selectors.add_argument("--last", metavar="N", type=int)
    parser.add_argument("--headers", action="store_true")
    parser.add_argument("--wake", metavar="ROLE", help="read the last header and re-wake the seat of this role")
    parser.add_argument("--append", action="store_true",
                        help="append one entry, header only unless --stdin, then wake --to")
    parser.add_argument("--from", dest="sender", metavar="SEAT")
    parser.add_argument("--to", dest="recipient", metavar="SEAT")
    parser.add_argument("--repo", metavar="PATH", help="checkout whose HEAD the header carries")
    parser.add_argument("--event", metavar="LINE", help="the header's one-line event or answer")
    parser.add_argument("--attention", metavar="EVENT_KIND", help="make the header an ATTENTION event of this kind")
    parser.add_argument("--stdin", action="store_true", help="read the entry body from stdin")
    backend.add_backend_option(parser)
    args = parser.parse_args(argv)
    open_backend = lambda: backend.open_backend(os.environ, args.backend)  # noqa: E731

    append_args = (args.sender, args.recipient, args.repo, args.event)
    if args.append:
        if None in append_args:
            parser.error("--append requires --from, --to, --repo and --event")
        if args.since is not None or args.last is not None or args.headers:
            parser.error("--append cannot be combined with mailbox selectors")
        if args.wake is not None:
            parser.error("--append wakes its --to seat; --wake is only a standalone re-wake")
    elif any(value is not None for value in append_args) or args.attention or args.stdin:
        parser.error("--from, --to, --repo, --event, --attention and --stdin require --append")

    try:
        if args.append:
            header = append_entry(
                args.file, sender=args.sender, recipient=args.recipient, repo=args.repo,
                event=args.event, attention=args.attention,
                body=sys.stdin.read() if args.stdin else None,
            )
            print(header)
            return wake(args.recipient, args.file, open_backend)
        if args.wake is not None:
            if args.since is not None or args.last is not None or args.headers:
                raise ValueError("--wake cannot be combined with mailbox selectors")
            return wake(args.wake, args.file, open_backend)
        text = Path(args.file).read_text(encoding="utf-8")

        if args.since is None and args.last is None and not args.headers:
            raise ValueError("at least one of --headers, --since, or --last is required")
        output = select_entries(text, since=args.since, last=args.last, headers=args.headers)
    except (OSError, ValueError) as exc:
        print(f"mailbox: {args.file}: {exc}", file=sys.stderr)
        return 1

    if output:
        print(("\n" if args.headers else "\n\n").join(output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
