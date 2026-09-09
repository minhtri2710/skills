#!/usr/bin/env python3
"""Write, check, and derive gate-ledger rows.

Every number in a row is derived here from git, never typed by a seat, and every
row this script appends is re-read from disk and re-derived before the command
exits. `--check` applies the same derivation to a row that already exists.

Row shape, one line, ` | ` between fields:

    <id> | <ISO time> | kind=<kind> | <branch>@<head> | status=<status>
      [| channel=<channel>] [| writer=<seat>] | record=<timely|reconstruction>
      [| push=<base>..<head> count=<n> boundary="<declared paths>"
         boundary-check="<paths outside the boundary>"]
      [| resolves=<id>[,<id>...]] | words=<seat|human|selected|none>
      | note=<one line> | quote="<verbatim>"

`quote=` is terminal and holds verbatim text — the Human's words on a gate row,
the refused command on a denial row — so a `|` inside it is data, not a
separator. `note=` is the seat's own words and refuses `|` and `"`.
"""
from __future__ import annotations

import argparse
import fcntl
import re
import subprocess
import sys
from contextlib import contextmanager
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
    r'count=(?P<count>\d+) boundary="(?P<declared>[^"]*)" '
    r'boundary-check="(?P<boundary>[^"]*)"$'
)
# Row discovery is namespace-agnostic. G<n> is only the local ID generator's shape.
ID_RE = re.compile(r"^(?P<id>\S+) \|")
LOCAL_ID_RE = re.compile(r"^G(\d+)$")
RESOLVE_ID_RE = re.compile(r'^[^,\s|"]+$')
RECORD_VALUES = ("timely", "reconstruction")
WORDS_VALUES = ("seat", "human", "selected", "none")


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


def ledger_rows(text: str) -> list[str]:
    """Return ledger rows without treating headers or prose as rows."""
    return [line for line in text.splitlines() if ID_RE.match(line)]


def next_id_from_rows(rows: list[str]) -> int:
    """One more than the highest local G<n> id in the file."""
    ids = []
    for line in rows:
        match = ID_RE.match(line)
        if match:
            local = LOCAL_ID_RE.match(match.group("id"))
            if local:
                ids.append(int(local.group(1)))
    return max(ids) + 1 if ids else 1


def split_row(row: str) -> tuple[list[str], str]:
    """Split fields while preserving every character in terminal quote=."""
    prefix, marker, quoted = row.partition(" | quote=")
    if (not marker or not quoted.startswith('"') or not quoted.endswith('"')
            or not ID_RE.match(row)):
        raise RowError("quote= is not the terminal field, or the row has no namespace-agnostic id")
    return prefix.split(" | "), quoted[1:-1]


def parse_resolves(value: str) -> list[str]:
    ids = value.split(",")
    if not value or any(not RESOLVE_ID_RE.fullmatch(gid) for gid in ids):
        raise RowError(f"resolves={value!r} contains an empty or malformed id")
    if len(ids) != len(set(ids)):
        raise RowError(f"resolves={value!r} names an id more than once")
    return ids


def resolve_ids(values: list[str]) -> list[str]:
    ids: list[str] = []
    for value in values:
        ids.extend(parse_resolves(value))
    if len(ids) != len(set(ids)):
        raise RowError("--resolves names an id more than once")
    return ids


def structured_row(row: str) -> tuple[str, str, list[str]]:
    """Read only the structured fields needed for open-gate derivation."""
    fields, _ = split_row(row)
    status_fields = [field for field in fields if field.startswith("status=")]
    if len(status_fields) != 1:
        raise RowError(f"row {fields[0]!r} does not carry exactly one status=")
    status = status_fields[0].split("=", 1)[1]
    if not STATUS_RE.fullmatch(status):
        raise RowError(f"field {status_fields[0]!r} is not a valid status=")
    resolve_fields = [field for field in fields if field.startswith("resolves=")]
    if len(resolve_fields) > 1:
        raise RowError(f"row {fields[0]!r} carries more than one resolves=")
    resolves = parse_resolves(resolve_fields[0].split("=", 1)[1]) if resolve_fields else []
    return fields[0], status, resolves


def open_state(rows: list[str]) -> tuple[dict[str, tuple[int, str]], set[str], dict[str, int]]:
    """Return latest own rows, ids ever opened, and latest resolver positions."""
    latest: dict[str, tuple[int, str]] = {}
    ever_open: set[str] = set()
    resolved_at: dict[str, int] = {}
    for index, row in enumerate(rows):
        gid, status, resolves = structured_row(row)
        latest[gid] = (index, status)
        if status == "open":
            ever_open.add(gid)
        for target in resolves:
            resolved_at[target] = index
    return latest, ever_open, resolved_at


def open_gate_ids(rows: list[str]) -> list[str]:
    latest, _, resolved_at = open_state(rows)
    open_rows = [
        (index, gid)
        for gid, (index, status) in latest.items()
        if status == "open" and resolved_at.get(gid, -1) <= index
    ]
    return [gid for _, gid in sorted(open_rows)]


def require_open_targets(rows: list[str], targets: list[str]) -> None:
    latest, ever_open, resolved_at = open_state(rows)
    for target in targets:
        own = latest.get(target)
        if target not in ever_open:
            raise RowError(f"resolves={target} refused: never-open")
        if own is None or own[1] != "open" or resolved_at.get(target, -1) > own[0]:
            raise RowError(f"resolves={target} refused: already-closed")


def derive_push(repo: Path, base: str, head: str, boundary: list[str]) -> tuple[str, list[str]]:
    """The push block's two derived values, for whichever path asks: build or check.

    `outside` is the union of paths touched by every commit in the range, merge
    commits included, minus the declared boundary — not the diff of the two end
    trees, which misses a path added by one commit in the range and deleted by
    another. `lead.md` ("Gates and closeout") specifies the union; one derivation
    serves both callers so neither can drift from it alone.
    """
    for b in boundary:
        if not b or b.split() != [b]:
            raise RowError(
                f"boundary path {b!r} is empty or holds whitespace — --boundary is one flag "
                "per path, and a path with a space cannot be read back out of boundary-check"
            )
    git(repo, "merge-base", "--is-ancestor", base, head)
    count = git(repo, "rev-list", "--count", f"{base}..{head}")
    if count == "0":
        raise RowError(f"push range {base}..{head} carries no commit")
    changed: set[str] = set()
    for commit in git(repo, "rev-list", f"{base}..{head}").splitlines():
        changed.update(
            path for path in git(
                repo, "diff-tree", "--root", "-m", "--no-commit-id", "--name-only", "-r", commit,
            ).splitlines() if path
        )
    outside = sorted(path for path in changed
                     if not any(b == "." or path == b or path.startswith(b.rstrip("/") + "/")
                                for b in boundary))
    if any('"' in path or "|" in path or path.split() != [path] for path in outside):
        raise RowError("a path outside the boundary contains a delimiter character")
    return count, outside


def push_field(base: str, head: str, count: str,
               boundary: list[str], outside: list[str]) -> str:
    """The push block, carrying the derivation's input beside its output."""
    return (f'push={base}..{head} count={count} '
            f'boundary="{" ".join(boundary)}" boundary-check="{" ".join(outside)}"')


def build(args: argparse.Namespace, repo: Path, ledger: Path,
          existing_rows: list[str] | None = None) -> str:
    if not KIND_RE.fullmatch(args.kind):
        raise RowError(f"kind={args.kind!r} is not a lowercase token")
    if not STATUS_RE.fullmatch(args.status):
        raise RowError(f"status={args.status!r} is not open, resolved:<x> or recorded:<x>")
    if args.channel and not CHANNEL_RE.fullmatch(args.channel):
        raise RowError(f"channel={args.channel!r} is not a known channel")
    if args.writer and not WRITER_RE.fullmatch(args.writer):
        raise RowError(f"writer={args.writer!r} is not a seat name")
    if args.words not in WORDS_VALUES:
        raise RowError("--words is required when appending a row")
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
    if args.quote and args.quote_file:
        raise RowError("--quote and --quote-file are mutually exclusive")
    if args.quote_file:
        try:
            with Path(args.quote_file).open("r", encoding="utf-8", newline="") as handle:
                quote = handle.read()
        except (OSError, UnicodeError) as exc:
            raise RowError(f"--quote-file {args.quote_file!r} could not be read: {exc}") from None
        if quote.endswith("\r\n"):
            quote = quote[:-2]
        elif quote.endswith("\n"):
            quote = quote[:-1]
    else:
        quote = args.quote
    if "\n" in quote:
        raise RowError("quote= is one line")
    if (args.words == "none") != (quote == ""):
        raise RowError("words=none iff quote= is empty")
    if not quote and args.status != "open":
        raise RowError("quote= is required unless status=open")
    record = args.record or "timely"
    if record == "reconstruction" and not note:
        raise RowError("a reconstruction row names its source in note=")

    rows = existing_rows if existing_rows is not None else (
        ledger_rows(ledger.read_text()) if ledger.exists() else []
    )
    targets = resolve_ids(args.resolves)
    if targets:
        require_open_targets(rows, targets)

    branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    head = git(repo, "rev-parse", "HEAD")
    fields = [
        f"G{next_id_from_rows(rows)}",
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        f"kind={args.kind}",
        f"{branch}@{head}",
        f"status={args.status}",
    ]
    if args.channel:
        fields.append(f"channel={args.channel}")
    if args.writer:
        fields.append(f"writer={args.writer}")
    fields.append(f"record={record}")
    if args.kind == "push":
        if not args.push_base:
            raise RowError(
                "a push row needs --push-base: the range, count and boundary-check are "
                "derived from it, and a push row carrying none of them asserts that a "
                "push happened while holding no evidence that it did"
            )
        pushed = git(repo, "rev-parse", "HEAD")
        remote = git(repo, "ls-remote", "origin", f"refs/heads/{branch}").split()
        if not remote or remote[0] != pushed:
            raise RowError(
                f"origin/{branch} is {remote[0] if remote else 'absent'}, not {pushed} — "
                "the push this row claims has not landed"
            )
        if not args.boundary:
            raise RowError(
                "a push row needs --boundary: the declared paths the push was judged "
                "against are part of the row, and refusing here keeps the bad row out "
                "of an append-only file rather than rejecting it after it lands"
            )
        count, outside = derive_push(repo, args.push_base, pushed, args.boundary)
        fields.append(push_field(args.push_base, pushed, count, args.boundary, outside))
    elif args.push_base or args.boundary:
        flag = "--push-base" if args.push_base else "--boundary"
        raise RowError(
            f"{flag} is only meaningful on a push row, and this row is kind={args.kind} "
            "— an argument accepted and silently dropped is how a row loses the evidence "
            "it claims to carry"
        )
    if targets:
        fields.append(f"resolves={','.join(targets)}")
    fields.append(f"words={args.words}")
    fields.append(f"note={note}")
    fields.append(f'quote="{quote}"')
    return " | ".join(fields)


def check(row: str, repo: Path, prior_rows: list[str] | None = None) -> None:
    """Re-derive every derived field in an existing row and compare."""
    fields, quote = split_row(row)
    if len(fields) < 5:
        raise RowError(f"row has {len(fields)} fields before quote=, expected at least 5")
    gid, when, kind, head_field, status, *rest = fields
    if not ID_RE.match(row) or gid != ID_RE.match(row).group("id"):
        raise RowError("row does not start with a namespace-agnostic gate id")
    for name, value, pattern in (
        ("kind", kind, KIND_RE), ("status", status, STATUS_RE),
    ):
        if not value.startswith(f"{name}=") or not pattern.fullmatch(value.split("=", 1)[1]):
            raise RowError(f"field {value!r} is not a valid {name}=")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", when):
        raise RowError(f"time {when!r} is not an ISO UTC timestamp")
    m = HEAD_RE.fullmatch(head_field)
    if not m:
        raise RowError(f"field {head_field!r} is not <branch>@<head>")
    # The object, not the ref: a merge that deletes the branch must not make a
    # landed row permanently uncheckable. Retrievability belongs to the object.
    git(repo, "rev-parse", "--verify", f"{m.group('head')}^{{commit}}")

    known = ("channel=", "writer=", "record=", "push=", "resolves=", "words=", "note=")
    for field in rest:
        if not field.startswith(known):
            raise RowError(f"field {field.split('=')[0]!r} is not in the row schema")

    index = 0
    if index < len(rest) and rest[index].startswith("channel="):
        value = rest[index].split("=", 1)[1]
        if not CHANNEL_RE.fullmatch(value):
            raise RowError(f"field {rest[index]!r} is not a valid channel=")
        index += 1
    if index < len(rest) and rest[index].startswith("writer="):
        value = rest[index].split("=", 1)[1]
        if not WRITER_RE.fullmatch(value):
            raise RowError(f"field {rest[index]!r} is not a valid writer=")
        index += 1
    if index >= len(rest) or not rest[index].startswith("record="):
        raise RowError("record= is missing or out of order")
    if rest[index].split("=", 1)[1] not in RECORD_VALUES:
        raise RowError(f"field {rest[index]!r} is not one of {RECORD_VALUES}")
    index += 1

    push = None
    if index < len(rest) and rest[index].startswith("push="):
        push = rest[index]
        index += 1
    if kind.split("=", 1)[1] == "push" and push is None:
        raise RowError(
            "this row is kind=push and carries no push block — the range, count and "
            "boundary-check are the whole of what a push row is checked against, so a "
            "row without them is checked against nothing and passes vacuously"
        )

    resolves: list[str] = []
    if index < len(rest) and rest[index].startswith("resolves="):
        resolves = parse_resolves(rest[index].split("=", 1)[1])
        index += 1

    if index >= len(rest) or not rest[index].startswith("words="):
        raise RowError("words= is missing or out of order")
    words = rest[index].split("=", 1)[1]
    if words not in WORDS_VALUES:
        raise RowError(f"field {rest[index]!r} is not one of {WORDS_VALUES}")
    index += 1

    if index >= len(rest) or not rest[index].startswith("note="):
        raise RowError("note= is missing or out of order")
    note = rest[index][len("note="):]
    index += 1
    if index != len(rest):
        raise RowError(f"field {rest[index].split('=')[0]!r} is out of order or duplicated")
    if not note.strip():
        raise RowError("note= is missing or empty")
    if len(note) > NOTE_MAX:
        raise RowError(f"note= is {len(note)} chars, over the {NOTE_MAX} cap")
    if "|" in note or '"' in note or "\n" in note:
        raise RowError('note= refuses | and " — they are the row\'s delimiters')
    if "\n" in quote:
        raise RowError("quote= is one line")
    if (words == "none") != (quote == ""):
        raise RowError("words=none iff quote= is empty")
    status_value = status.split("=", 1)[1]
    if not quote and status_value != "open":
        raise RowError("quote= is required unless status=open")

    if push is not None:
        p = PUSH_RE.fullmatch(push)
        if not p:
            raise RowError(f"push block {push!r} is malformed")
        base, phead = p.group("base"), p.group("head")
        boundary = p.group("declared").split()
        if not boundary:
            raise RowError(
                'this row declares boundary="" — an empty boundary puts every touched '
                "path outside it, which passes any row claiming the whole changed set"
            )
        count, outside = derive_push(repo, base, phead, boundary)
        if count != p.group("count"):
            raise RowError(
                f"count={p.group('count')} but {base}..{phead} carries {count} commits"
            )
        if " ".join(outside) != p.group("boundary"):
            raise RowError(
                f'boundary-check="{p.group("boundary")}" but the union over {base}..{phead} '
                f'outside the declared boundary is "{" ".join(outside)}"'
            )

    if resolves:
        require_open_targets(prior_rows or [], resolves)


@contextmanager
def locked_ledger(ledger: Path, exclusive: bool):
    if not exclusive and not ledger.exists():
        raise RowError(f"{ledger} holds no gate ledger")
    mode = "a+" if exclusive else "r"
    try:
        with ledger.open(mode) as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
            try:
                yield handle
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    except FileNotFoundError:
        raise RowError(f"{ledger} holds no gate ledger") from None


def handle_text(handle) -> str:
    handle.seek(0)
    return handle.read()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ledger", required=True, type=Path,
                        help="path to gates.md; the Reviewer round-trips against a scratch file")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    parser.add_argument("--check", action="store_true",
                        help="check the ledger's last row instead of appending one")
    parser.add_argument("--open-gates", action="store_true",
                        help="print the structured open-gate id set, one id per line")
    parser.add_argument("--kind")
    parser.add_argument("--status")
    parser.add_argument("--channel")
    parser.add_argument("--writer")
    parser.add_argument("--record", choices=RECORD_VALUES)
    parser.add_argument("--push-base", help="the intake's recorded merge-base; the head is derived")
    parser.add_argument("--boundary", action="append", default=[],
                        help="a declared boundary path; repeatable, required to append a push "
                             "row, and written into the row so --check derives against the "
                             "same paths without being told them")
    parser.add_argument("--resolves", action="append", default=[],
                        help="an open gate id to resolve; repeatable and comma-separated")
    parser.add_argument("--words", choices=WORDS_VALUES,
                        help="who authored quote=; required when appending")
    parser.add_argument("--note", default="")
    parser.add_argument("--quote", default="")
    parser.add_argument("--quote-file", default="",
                        help="read the verbatim quote from a UTF-8 file")
    args = parser.parse_args(argv)

    try:
        if args.check and args.open_gates:
            raise RowError("--check and --open-gates are mutually exclusive")
        if args.open_gates:
            ignored = (
                args.kind, args.status, args.channel, args.writer, args.record, args.push_base,
                args.boundary, args.resolves, args.words, args.note, args.quote,
                args.quote_file,
            )
            if any(ignored):
                raise RowError("--open-gates cannot be combined with append arguments")
            with locked_ledger(args.ledger, exclusive=False) as handle:
                ids = open_gate_ids(ledger_rows(handle_text(handle)))
            sys.stdout.write("".join(f"{gid}\n" for gid in ids))
            return 0

        if args.check:
            with locked_ledger(args.ledger, exclusive=False) as handle:
                rows = ledger_rows(handle_text(handle))
                if not rows:
                    raise RowError(f"{args.ledger} holds no gate row")
                check(rows[-1], args.repo, rows[:-1])
                print(f"ok: {rows[-1].split(' | ')[0]} checks out")
            return 0

        if not args.kind or not args.status:
            raise RowError("--kind and --status are required to append a row")
        if args.words is None:
            raise RowError("--words is required when appending a row")

        with locked_ledger(args.ledger, exclusive=True) as handle:
            before = handle_text(handle)
            existing_rows = ledger_rows(before)
            row = build(args, args.repo, args.ledger, existing_rows)
            if before and not before.endswith("\n"):
                handle.seek(0, 2)
                handle.write("\n")
            handle.seek(0, 2)
            handle.write(row + "\n")
            handle.flush()
            stored_rows = ledger_rows(handle_text(handle))
            if not stored_rows or stored_rows[-1] != row:
                raise RowError("the row read back from disk is not the row written")
            check(row, args.repo, existing_rows)
        print(row)
        return 0
    except RowError as exc:
        print(f"gate_row: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
