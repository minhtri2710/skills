#!/usr/bin/env python3
"""Write and check one gate-ledger row.

Every number in a row is derived here from git, never typed by a seat, and every
row this script appends is re-read from disk and re-derived before the command
exits. `--check` applies the same derivation to a row that already exists.

Row shape, one line, ` | ` between fields:

    G<id> | <ISO time> | kind=<kind> | <branch>@<head> | status=<status>
      [| channel=<channel>] [| writer=<seat>] | record=<timely|reconstruction>
      [| push=<base>..<head> count=<n> boundary-check="<paths outside the boundary>"]
      | note=<one line> | quote="<verbatim>"

`quote=` is terminal and holds verbatim text — the Human's words on a gate row,
the refused command on a denial row — so a `|` inside it is data, not a
separator. `note=` is the seat's own words and refuses `|` and `"`.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

NOTE_MAX = 200
KIND_RE = re.compile(r"^[a-z][a-z-]*$")
STATUS_RE = re.compile(r"^(open|(resolved|recorded):[a-z0-9-]+)$")
CHANNEL_RE = re.compile(r"^(direct-seat-pane|supervisor-relay):(typed|dialog)$")
WRITER_RE = re.compile(r"^[a-z][a-z0-9_-]*$")
HEAD_RE = re.compile(r"^(?P<branch>[^ |@]+)@(?P<head>[0-9a-f]{7,40})$")
PUSH_RE = re.compile(
    r'^push=(?P<base>[0-9a-f]{7,40})\.\.(?P<head>[0-9a-f]{7,40}) '
    r'count=(?P<count>\d+) boundary-check="(?P<boundary>[^"]*)"$'
)
ID_RE = re.compile(r"^G(\d+) ")


class RowError(Exception):
    """A row is malformed, or a derived field disagrees with git."""


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        raise RowError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def next_id(ledger: Path) -> int:
    """One more than the highest id in the file. The only read of an old row."""
    if not ledger.exists():
        return 1
    ids = [int(m.group(1)) for m in
           (ID_RE.match(line) for line in ledger.read_text().splitlines()) if m]
    return max(ids) + 1 if ids else 1


def derive_push(repo: Path, base: str, head: str, boundary: list[str]) -> str:
    git(repo, "merge-base", "--is-ancestor", base, head)  # raises when base is not an ancestor
    count = git(repo, "rev-list", "--count", f"{base}..{head}")
    if count == "0":
        raise RowError(f"push range {base}..{head} carries no commit")
    changed = [p for p in git(repo, "diff", "--name-only", f"{base}..{head}").splitlines() if p]
    outside = [p for p in changed
               if not any(p == b or p.startswith(b.rstrip("/") + "/") for b in boundary)]
    if any('"' in p or "|" in p for p in outside):
        raise RowError("a path outside the boundary contains a delimiter character")
    return f'push={base}..{head} count={count} boundary-check="{" ".join(outside)}"'


def build(args: argparse.Namespace, repo: Path, ledger: Path) -> str:
    if not KIND_RE.match(args.kind):
        raise RowError(f"kind={args.kind!r} is not a lowercase token")
    if not STATUS_RE.match(args.status):
        raise RowError(f"status={args.status!r} is not open, resolved:<x> or recorded:<x>")
    if args.channel and not CHANNEL_RE.match(args.channel):
        raise RowError(f"channel={args.channel!r} is not a known channel")
    if args.writer and not WRITER_RE.match(args.writer):
        raise RowError(f"writer={args.writer!r} is not a seat name")
    note = args.note.strip()
    if not note:
        raise RowError("note= is required and is the row's one-line finding")
    if len(note) > NOTE_MAX:
        raise RowError(
            f"note= is {len(note)} chars, over the {NOTE_MAX} cap — "
            "narrative belongs in the workspace record, not the ledger"
        )
    if "|" in note or '"' in note or "\n" in note:
        raise RowError('note= refuses | and " — they are the row\'s delimiters')
    quote = args.quote or ""
    if "\n" in quote:
        raise RowError("quote= is one line")
    if not quote and args.status != "open":
        raise RowError("quote= is required unless status=open")
    if args.record == "reconstruction" and not note:
        raise RowError("a reconstruction row names its source in note=")

    branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    head = git(repo, "rev-parse", "HEAD")
    fields = [
        f"G{next_id(ledger)}",
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        f"kind={args.kind}",
        f"{branch}@{head}",
        f"status={args.status}",
    ]
    if args.channel:
        fields.append(f"channel={args.channel}")
    if args.writer:
        fields.append(f"writer={args.writer}")
    fields.append(f"record={args.record}")
    if args.push_base:
        pushed = git(repo, "rev-parse", "HEAD")
        remote = git(repo, "ls-remote", "origin", f"refs/heads/{branch}").split()
        if not remote or remote[0] != pushed:
            raise RowError(
                f"origin/{branch} is {remote[0] if remote else 'absent'}, not {pushed} — "
                "the push this row claims has not landed"
            )
        fields.append(derive_push(repo, args.push_base, pushed, args.boundary))
    fields.append(f"note={note}")
    fields.append(f'quote="{quote}"')
    return " | ".join(fields)


def check(row: str, repo: Path) -> None:
    """Re-derive every derived field in an existing row and compare."""
    if not ID_RE.match(row):
        raise RowError("row does not start with a gate id")
    quote = None
    if "quote=" in row:
        prefix, _, rest = row.partition(" | quote=")
        if not rest.startswith('"') or not rest.endswith('"'):
            raise RowError("quote= is not the terminal field, or is unbalanced")
        quote, row = rest[1:-1], prefix
    fields = row.split(" | ")
    if len(fields) < 6:
        raise RowError(f"row has {len(fields)} fields, expected at least 6 before quote=")
    gid, when, kind, head_field, status, *rest = fields
    for name, value, pattern in (
        ("kind", kind, KIND_RE), ("status", status, STATUS_RE),
    ):
        if not value.startswith(f"{name}=") or not pattern.match(value.split("=", 1)[1]):
            raise RowError(f"field {value!r} is not a valid {name}=")
    if not re.match(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$", when):
        raise RowError(f"time {when!r} is not an ISO UTC timestamp")
    m = HEAD_RE.match(head_field)
    if not m:
        raise RowError(f"field {head_field!r} is not <branch>@<head>")
    git(repo, "rev-parse", "--verify", f"{m.group('head')}^{{commit}}")

    known = ("channel=", "writer=", "record=", "push=", "note=")
    for field in rest:
        if not field.startswith(known):
            raise RowError(f"field {field.split('=')[0]!r} is not in the row schema")
    if not any(f.startswith("record=") for f in rest):
        raise RowError("record= is missing")
    for field in rest:
        if not field.startswith("push="):
            continue
        p = PUSH_RE.match(field)
        if not p:
            raise RowError(f"push block {field!r} is malformed")
        base, phead = p.group("base"), p.group("head")
        actual = git(repo, "rev-list", "--count", f"{base}..{phead}")
        if actual != p.group("count"):
            raise RowError(
                f"count={p.group('count')} but {base}..{phead} carries {actual} commits"
            )
    note = next((f[len("note="):] for f in rest if f.startswith("note=")), None)
    if note is None or not note.strip():
        raise RowError("note= is missing or empty")
    if len(note) > NOTE_MAX:
        raise RowError(f"note= is {len(note)} chars, over the {NOTE_MAX} cap")
    if quote is None and status.split("=", 1)[1] != "open":
        raise RowError("quote= is required unless status=open")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ledger", required=True, type=Path,
                        help="path to gates.md; the Reviewer round-trips against a scratch file")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--check", action="store_true",
                        help="check the ledger's last row instead of appending one")
    parser.add_argument("--kind")
    parser.add_argument("--status")
    parser.add_argument("--channel")
    parser.add_argument("--writer")
    parser.add_argument("--record", choices=("timely", "reconstruction"), default="timely")
    parser.add_argument("--push-base", help="the intake's recorded merge-base; the head is derived")
    parser.add_argument("--boundary", action="append", default=[],
                        help="a declared boundary path; repeatable")
    parser.add_argument("--note", default="")
    parser.add_argument("--quote", default="")
    args = parser.parse_args(argv)

    try:
        if args.check:
            rows = [l for l in args.ledger.read_text().splitlines() if ID_RE.match(l)]
            if not rows:
                raise RowError(f"{args.ledger} holds no gate row")
            check(rows[-1], args.repo)
            print(f"ok: {rows[-1].split(' | ')[0]} checks out")
            return 0
        if not args.kind or not args.status:
            parser.error("--kind and --status are required to append a row")
        row = build(args, args.repo, args.ledger)
        with args.ledger.open("a") as fh:
            fh.write(row + "\n")
        stored = [l for l in args.ledger.read_text().splitlines() if ID_RE.match(l)][-1]
        if stored != row:
            raise RowError("the row read back from disk is not the row written")
        check(stored, args.repo)
        print(stored)
        return 0
    except RowError as exc:
        print(f"gate_row: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
