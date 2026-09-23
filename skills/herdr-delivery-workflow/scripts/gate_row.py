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
      [| resolves=<id>[,<id>...]]
      [| op=<command> | after=<branch>@<head>]
      [| who=<delegate> | scope=<scope> | conditions=<conditions> | expiry=<expiry>]
      [| finding=<identity>] [| archive=<sha256 of gates.legacy.md>] [| prev_hash=<64 lowercase hex>]
      | words=<seat|human|selected|none>
      | note=<one line> | quote="<verbatim>"

`quote=` is terminal and holds verbatim text — the Human's words on a gate row,
the refused command on a denial row — so a `|` inside it is data, not a
separator. `note=` is the seat's own words and refuses `|` and `"`.
"""
from __future__ import annotations

import argparse
import fcntl
import hashlib
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
HEAD_ARG_RE = re.compile(r"^(?P<branch>[^ |@]+)@(?P<head>[0-9a-f]{40})$")
PUSH_RE = re.compile(
    r'^push=(?P<base>[0-9a-f]{7,40})\.\.(?P<head>[0-9a-f]{7,40}) '
    r'count=(?P<count>\d+) boundary="(?P<declared>[^"]*)" '
    r'boundary-check="(?P<boundary>[^"]*)"$'
)
REVIEW_RE = re.compile(
    r'^review=(?P<base>[0-9a-f]{7,40})\.\.(?P<head>[0-9a-f]{7,40}) '
    r'count=(?P<count>\d+)$'
)
# Row discovery is namespace-agnostic. G<n> is only the local ID generator's shape.
ID_RE = re.compile(r"^(?P<id>\S+) \|")
LOCAL_ID_RE = re.compile(r"^G(\d+)$")
RESOLVE_ID_RE = re.compile(r'^[^,\s|"]+$')
RECORD_VALUES = ("timely", "reconstruction")
WORDS_VALUES = ("seat", "human", "selected", "none")
LOCAL_OPS_STATUS = "recorded:local-ops"
STANDING_DELEGATION_STATUS = "recorded:standing-delegation"
HANDOFF_STATUS = "recorded:handoff"
CUTOVER_STATUS = "recorded:cutover"
LEGACY_LEDGER = "gates.legacy.md"
ARCHIVE_RE = re.compile(r"^[0-9a-f]{64}$")
FINDING_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
MAILBOX_ATTENTION_RE = re.compile(
    r"^## .+ -> supervisor \| \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z "
    r"\| ATTENTION (?P<text>.+?) \| HEAD (?P<head>[0-9a-f]{7,40})\s*$"
)
HUMAN_GATE_KINDS = frozenset({
    "push", "merge", "deploy", "push-gate", "merge-gate", "deploy-gate",
})
SEAT_PERMISSION_GATE_KINDS = frozenset({"push-gate", "merge-gate", "deploy-gate"})


class RowError(Exception):
    """A row is malformed, or a derived field disagrees with git."""


def validate_row_encodings(
    *, kind: str, status: str, channel: str, words: str, quote: str, note: str,
) -> None:
    """Enforce the author encoding carried by channel and denial rows."""
    if channel.endswith(":dialog") and words != "selected":
        raise RowError(
            f"channel={channel} requires words=selected, not words={words}"
        )
    if (
        kind in SEAT_PERMISSION_GATE_KINDS
        and status == "open"
        and "blocked:seat-permission" in note
        and (words != "none" or quote != "")
    ):
        quote_shape = "empty" if quote == "" else "non-empty"
        raise RowError(
            f"kind={kind} status=open note contains blocked:seat-permission; "
            f"requires words=none and quote=empty, got words={words} and quote={quote_shape}"
        )


def mailbox_token(text: str, token: str) -> bool:
    """Match a gate id or SHA as a complete mailbox token, not a substring."""
    return re.search(
        rf"(?<![A-Za-z0-9_-]){re.escape(token)}(?![A-Za-z0-9_-])", text
    ) is not None


def require_mailbox_attention(gid: str, head: str, mailbox: Path) -> None:
    """Require one exact-shape ATTENTION header naming this gate id or SHA."""
    try:
        text = mailbox.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise RowError(f"mailbox {mailbox} could not be read: {exc}") from None
    for line in text.splitlines():
        match = MAILBOX_ATTENTION_RE.fullmatch(line)
        if not match:
            continue
        if (
            mailbox_token(match.group("text"), gid)
            or mailbox_token(match.group("text"), head)
        ):
            return
    raise RowError(
        f"open gate {gid} has no matching ATTENTION entry in mailbox {mailbox}; "
        f"a header must name gate id {gid} or exact head SHA {head}"
    )


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True, text=True, check=False,
    )
    if proc.returncode != 0:
        raise RowError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


PREV_HASH_RE = re.compile(r"^[0-9a-f]{64}$")


def row_hash(row: str) -> str:
    """Hash the exact row text returned by ``ledger_rows``."""
    return hashlib.sha256(row.encode("utf-8")).hexdigest()


def verify_chain(rows: list[str]) -> None:
    """Verify the hash chain: the first row is unhashed, every later row chains to its predecessor."""
    for index, row in enumerate(rows):
        fields, _ = split_row(row)
        hashes = [field for field in fields if field.startswith("prev_hash=")]
        if len(hashes) > 1:
            raise RowError(f"row {fields[0]!r} carries more than one prev_hash=")
        if index == 0:
            if hashes:
                raise RowError(f"row {fields[0]!r} carries prev_hash= without a predecessor")
            continue
        if not hashes:
            raise RowError(f"row {fields[0]!r} is missing prev_hash=; every row after the first is chained")
        value = hashes[0].split("=", 1)[1]
        if not PREV_HASH_RE.fullmatch(value):
            raise RowError(f"field {hashes[0]!r} is not a 64-character lowercase hex prev_hash=")
        expected = row_hash(rows[index - 1])
        if value != expected:
            raise RowError(
                f"prev_hash mismatch at row {fields[0]!r}: expected {expected}, got {value}"
            )


def text_rows(text: str) -> list[str]:
    """Every gate row in the text, in order, without verifying a chain."""
    return [line for line in text.splitlines() if ID_RE.match(line)]


def ledger_rows(text: str) -> list[str]:
    """Return rows and fail closed when the hash chain is broken."""
    rows = text_rows(text)
    verify_chain(rows)
    return rows


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


def legacy_archive(ledger: Path) -> tuple[str, str] | None:
    """The id and SHA-256 a cutover row derives from the archive's bytes; None without archive rows."""
    path = ledger.parent / LEGACY_LEDGER
    try:
        data = path.read_bytes()
        rows = text_rows(data.decode("utf-8"))
    except FileNotFoundError:
        return None
    except (OSError, UnicodeError) as exc:
        raise RowError(f"archive {path} could not be read: {exc}") from None
    if not rows:
        return None
    return f"G{next_id_from_rows(rows)}", hashlib.sha256(data).hexdigest()


def cutover_binding(ledger: Path | None, prior_rows: list[str]) -> tuple[str, str]:
    """The id and archive hash a kind=cutover row must carry, or the named refusal."""
    if prior_rows:
        raise RowError("kind=cutover refused: the ledger already holds rows; a cutover is only a fresh ledger's first row")
    derived = legacy_archive(ledger) if ledger is not None else None
    if derived is None:
        raise RowError(f"kind=cutover refused: no {LEGACY_LEDGER} with at least one row beside the ledger")
    return derived


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


def row_evidence(row: str) -> tuple[str, str, str]:
    """Read the kind, SHA, and status used by review and push gates."""
    fields, _ = split_row(row)
    if len(fields) < 5:
        raise RowError(f"malformed ledger row: {row}")
    kind = fields[2]
    head = fields[3]
    status = fields[4]
    if not kind.startswith("kind="):
        raise RowError(f"ledger row has no kind=: {row}")
    if not HEAD_RE.fullmatch(head):
        raise RowError(f"ledger row has no valid branch@sha: {row}")
    if not status.startswith("status="):
        raise RowError(f"ledger row has no status=: {row}")
    return kind.split("=", 1)[1], head.split("@", 1)[1], status.split("=", 1)[1]


def review_range(row: str) -> tuple[str, str] | None:
    """The (base, head) a review row records, or None when the row carries no review block."""
    fields, _ = split_row(row)
    for field in fields:
        if field.startswith("review="):
            m = REVIEW_RE.fullmatch(field)
            if not m:
                raise RowError(f"review block {field!r} is malformed")
            return m.group("base"), m.group("head")
    return None


def review_field(base: str, head: str, count: str) -> str:
    """The review block: the exact commit range one review PASS covers."""
    return f"review={base}..{head} count={count}"


def require_review_coverage(rows: list[str], repo: Path, base: str, head: str) -> None:
    """Require every commit in the pushed range to be covered by a review PASS range.

    A single review covers its whole range, so a delivery's intra-run intermediates
    (one commit per scope, `lead.md` "Quiesce and commit") ride their reviewed head
    without their own rows. Stacked deliveries tile the range with one row each; a
    gap — an unreviewed delivery riding a reviewed tip's push — leaves its commits
    uncovered and is refused. The tip is covered only if it is itself a reviewed
    head, so a tip-unreviewed push is refused here too.
    """
    pushed = set(range_commits(repo, base, head))
    covered: set[str] = set()
    for row in rows:
        kind, _row_head, status = row_evidence(row)
        if kind != "review" or status != "recorded:review-pass":
            continue
        rng = review_range(row)
        if rng is None:
            continue
        rbase, rhead = rng
        if rhead not in pushed:
            continue
        covered.update(range_commits(repo, rbase, rhead))
    missing = [sha for sha in pushed if sha not in covered]
    if missing:
        raise RowError(
            f"refusing push of {base}..{head}: {', '.join(sorted(missing))} "
            "is not covered by any review PASS range"
        )


def field_text(name: str, value: str | None) -> str:
    value = (value or "").strip()
    if not value:
        raise RowError(f"{name}= is required")
    if "|" in value or '"' in value or "\n" in value:
        raise RowError(f"{name}= refuses |, \" and newlines — it is a structured row field")
    return value


def finding_value(value: str) -> str:
    value = field_text("finding", value)
    if not FINDING_RE.fullmatch(value):
        raise RowError(
            f"finding={value!r} is not an identity token; use letters, digits, '.', '_', ':' or '-'")
    return value


def required_fields(rest: list[str], index: int, names: tuple[str, ...], kind: str) -> tuple[dict[str, str], int]:
    values: dict[str, str] = {}
    for name in names:
        if index >= len(rest) or not rest[index].startswith(f"{name}="):
            raise RowError(f"kind={kind} requires {name}= field")
        field = rest[index]
        values[name] = field_text(name, field.split("=", 1)[1])
        index += 1
    return values, index


def reject_special_fields(args: argparse.Namespace, kind: str) -> None:
    allowed = {
        "local-ops": {"--op", "--after"},
        "standing-delegation": {"--who", "--scope", "--conditions", "--expiry"},
        "repair-grant": {"--finding"},
    }.get(kind, set())
    supplied = (
        ("--op", getattr(args, "op", "")), ("--after", getattr(args, "after", "")),
        ("--who", getattr(args, "who", "")), ("--scope", getattr(args, "scope", "")),
        ("--conditions", getattr(args, "conditions", "")),
        ("--expiry", getattr(args, "expiry", "")),
        ("--finding", getattr(args, "finding", "")),
    )
    for flag, value in supplied:
        if value and flag not in allowed:
            raise RowError(f"{flag} is only meaningful on its corresponding special row, not kind={kind}")


def validate_after(value: str, repo: Path) -> None:
    match = HEAD_RE.fullmatch(value)
    if not match:
        raise RowError(f"after={value!r} is not <branch>@<head>")
    git(repo, "rev-parse", "--verify", f"{match.group('head')}^{{commit}}")


def repair_findings_since_boundary(rows: list[str]) -> set[str]:
    """Return repair findings after the latest progress boundary, rejecting repeats."""
    findings: set[str] = set()
    for previous_row in reversed(rows):
        previous_kind, _, previous_status = row_evidence(previous_row)
        if (
            previous_status == "recorded:review-pass"
            or previous_kind == "push"
            or (
                previous_kind == "merge"
                and previous_status.startswith("resolved:")
            )
            or previous_kind == "repair-cap-gate"
        ):
            break
        if previous_kind == "repair-grant":
            previous_fields, _ = split_row(previous_row)
            matching = [field for field in previous_fields if field.startswith("finding=")]
            if len(matching) != 1:
                raise RowError("kind=repair-grant requires exactly one finding= field")
            finding = finding_value(matching[0].split("=", 1)[1])
            if finding in findings:
                refuse_repair_cap(finding)
            findings.add(finding)
    return findings


def refuse_repair_cap(finding: str) -> None:
    raise RowError(
        f"repair cap reached (finding={finding} repeated since the last progress "
        "boundary): record kind=repair-cap-gate and route the Human instead of "
        "another kind=repair-grant"
    )


def require_repair_progress(rows: list[str], finding: str) -> None:
    previous_findings = repair_findings_since_boundary(rows)
    if finding in previous_findings:
        refuse_repair_cap(finding)


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


def range_commits(repo: Path, base: str, head: str) -> list[str]:
    """The commits in base..head, newest first; the one range derivation both blocks share.

    A zero base means the whole history of head, including its root commit. Other
    bases must be ancestors of head, and every range must carry at least one commit.
    """
    if base == "0" * 40:
        commits = git(repo, "rev-list", head).splitlines()
    else:
        git(repo, "merge-base", "--is-ancestor", base, head)
        commits = git(repo, "rev-list", f"{base}..{head}").splitlines()
    if not commits:
        raise RowError(f"range {base}..{head} carries no commit")
    return commits


def derive_push(repo: Path, base: str, head: str, boundary: list[str]) -> tuple[str, list[str]]:
    """The push block's two derived values, for whichever path asks: build or check.

    `outside` is the union of paths touched by every commit in the range, merge
    commits included, minus the declared boundary — not the diff of the two end
    trees, which misses a path added by one commit in the range and deleted by
    another. `lead.md` ("Gates and ledger") specifies the union; one derivation
    serves both callers so neither can drift from it alone.
    """
    for b in boundary:
        if not b or b.split() != [b]:
            raise RowError(
                f"boundary path {b!r} is empty or holds whitespace — --boundary is one flag "
                "per path, and a path with a space cannot be read back out of boundary-check"
            )
    commits = range_commits(repo, base, head)
    count = str(len(commits))
    changed: set[str] = set()
    for commit in commits:
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


def resolve_row_head(args: argparse.Namespace, repo: Path, record: str) -> tuple[str, str]:
    current_branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    current_head = git(repo, "rev-parse", "HEAD")
    requested = args.head
    if not requested:
        return current_branch, current_head
    match = HEAD_ARG_RE.fullmatch(requested)
    if not match:
        raise RowError(
            f"--head {requested!r} is not <branch>@<full 40-hex commit SHA>"
        )
    branch, head = match.group("branch"), match.group("head")
    git(repo, "rev-parse", "--verify", f"{head}^{{commit}}")
    if head != current_head and record != "reconstruction":
        raise RowError(
            f"--head {requested} differs from repository HEAD {current_head}; "
            "use --record reconstruction to record a past head"
        )
    return branch, head


def build(args: argparse.Namespace, repo: Path,
          existing_rows: list[str]) -> str:
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
    validate_row_encodings(
        kind=args.kind, status=args.status, channel=args.channel or "",
        words=args.words, quote=quote, note=note,
    )
    record = args.record or "timely"
    branch, head = resolve_row_head(args, repo, record)

    kind = args.kind
    reject_special_fields(args, kind)
    special_fields: list[str] = []
    if kind == "local-ops":
        if args.status != LOCAL_OPS_STATUS:
            raise RowError(f"kind=local-ops requires status={LOCAL_OPS_STATUS}")
        if not getattr(args, "op", ""):
            raise RowError("kind=local-ops requires op= field")
        if not getattr(args, "after", ""):
            raise RowError("kind=local-ops requires after= field")
        op = field_text("op", args.op)
        after = field_text("after", args.after)
        validate_after(after, repo)
        special_fields.extend((f"op={op}", f"after={after}"))
    elif kind == "standing-delegation":
        if args.status != STANDING_DELEGATION_STATUS:
            raise RowError(f"kind=standing-delegation requires status={STANDING_DELEGATION_STATUS}")
        if args.words != "human":
            raise RowError("kind=standing-delegation requires words=human for the Human's quote")
        for name in ("who", "scope", "conditions", "expiry"):
            if not getattr(args, name, ""):
                raise RowError(f"kind=standing-delegation requires {name}= field")
            value = field_text(name, getattr(args, name))
            special_fields.append(f"{name}={value}")
    elif kind == "handoff":
        if args.status != HANDOFF_STATUS:
            raise RowError(f"kind=handoff requires status={HANDOFF_STATUS}")
    elif kind == "repair-grant":
        if not getattr(args, "finding", ""):
            raise RowError("kind=repair-grant requires finding= field")
        finding = finding_value(args.finding)
        special_fields.append(f"finding={finding}")

    rows = existing_rows
    gid = f"G{next_id_from_rows(rows)}"
    if kind == "cutover":
        gid, archive = cutover_binding(args.ledger, rows)
        special_fields.append(f"archive={archive}")
    targets = resolve_ids(args.resolves)
    if targets:
        require_open_targets(rows, targets)
    if kind == "repair-grant":
        require_repair_progress(rows, finding)

    fields = [
        gid,
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
        remote = git(repo, "ls-remote", "origin", f"refs/heads/{branch}").split()
        if not remote:
            raise RowError(
                f"origin/{branch} is absent — the push this row claims has not landed"
            )
        remote_tip = remote[0]
        try:
            git(repo, "rev-parse", "--verify", f"{remote_tip}^{{commit}}")
        except RowError:
            raise RowError(
                f"origin/{branch} points to {remote_tip}, which is not present locally — "
                "the Lead must git fetch it; gate_row never fetches"
            ) from None
        try:
            git(repo, "merge-base", "--is-ancestor", head, remote_tip)
        except RowError:
            raise RowError(
                f"origin/{branch} is {remote_tip}, but {head} is not an ancestor of "
                "the remote tip — the push this row claims has not landed"
            ) from None
        if not args.boundary:
            raise RowError(
                "a push row needs --boundary: the declared paths the push was judged "
                "against are part of the row, and refusing here keeps the bad row out "
                "of an append-only file rather than rejecting it after it lands"
            )
        count, outside = derive_push(repo, args.push_base, head, args.boundary)
        fields.append(push_field(args.push_base, head, count, args.boundary, outside))
        require_review_coverage(rows, repo, args.push_base, head)
    elif args.kind == "review":
        if not args.review_base:
            raise RowError(
                "a review row needs --review-base: the range it covers is the whole of "
                "what a stacked push is checked against, so a review row naming no range "
                "leaves the commits it reviewed uncovered when the push walks the stack"
            )
        if args.push_base or args.boundary:
            raise RowError("--push-base and --boundary are only meaningful on a push row")
        reviewed = head
        commits = range_commits(repo, args.review_base, reviewed)
        fields.append(review_field(args.review_base, reviewed, str(len(commits))))
    elif args.review_base:
        raise RowError(
            f"--review-base is only meaningful on a review row, and this row is "
            f"kind={args.kind} — an argument accepted and silently dropped is how a row "
            "loses the evidence it claims to carry"
        )
    elif args.push_base or args.boundary:
        flag = "--push-base" if args.push_base else "--boundary"
        raise RowError(
            f"{flag} is only meaningful on a push row, and this row is kind={args.kind} "
            "— an argument accepted and silently dropped is how a row loses the evidence "
            "it claims to carry"
        )
    if targets:
        fields.append(f"resolves={','.join(targets)}")
    if special_fields:
        fields.extend(special_fields)
    if rows:
        fields.append(f"prev_hash={row_hash(rows[-1])}")
    fields.append(f"words={args.words}")
    fields.append(f"note={note}")
    fields.append(f'quote="{quote}"')
    return " | ".join(fields)


def check(row: str, repo: Path, prior_rows: list[str] | None = None,
          ledger: Path | None = None) -> None:
    """Re-derive every derived field in an existing row and compare.

    `ledger` locates the sibling archive a first row is judged against.
    """
    fields, quote = split_row(row)
    if len(fields) < 5:
        raise RowError(f"row has {len(fields)} fields before quote=, expected at least 5")
    gid, when, kind, head_field, status, *rest = fields
    id_match = ID_RE.match(row)
    if not id_match or gid != id_match.group("id"):
        raise RowError("row does not start with a namespace-agnostic gate id")
    for name, value, pattern in (
        ("kind", kind, KIND_RE), ("status", status, STATUS_RE),
    ):
        if not value.startswith(f"{name}=") or not pattern.fullmatch(value.split("=", 1)[1]):
            raise RowError(f"field {value!r} is not a valid {name}=")
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z", when):
        raise RowError(f"time {when!r} is not an ISO UTC timestamp")
    if prior_rows:
        predecessor_fields, _ = split_row(prior_rows[-1])
        predecessor_when = predecessor_fields[1]
        if when < predecessor_when:
            raise RowError(
                f"timestamp regression: predecessor {predecessor_when} -> this row {when}"
            )
    m = HEAD_RE.fullmatch(head_field)
    if not m:
        raise RowError(f"field {head_field!r} is not <branch>@<head>")
    # The object, not the ref: a merge that deletes the branch must not make a
    # landed row permanently uncheckable. Retrievability belongs to the object.
    git(repo, "rev-parse", "--verify", f"{m.group('head')}^{{commit}}")

    known = (
        "channel=", "writer=", "record=", "push=", "review=", "resolves=", "op=", "after=",
        "who=", "scope=", "conditions=", "expiry=", "finding=", "archive=", "prev_hash=", "words=", "note=",
    )
    for field in rest:
        if not field.startswith(known):
            raise RowError(f"field {field.split('=')[0]!r} is not in the row schema")

    index = 0
    channel = ""
    if index < len(rest) and rest[index].startswith("channel="):
        channel = rest[index].split("=", 1)[1]
        if not CHANNEL_RE.fullmatch(channel):
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
    review = None
    if index < len(rest) and rest[index].startswith("review="):
        review = rest[index]
        index += 1
    row_kind = kind.split("=", 1)[1]
    if row_kind == "push" and push is None:
        raise RowError(
            "this row is kind=push and carries no push block — the range, count and "
            "boundary-check are the whole of what a push row is checked against, so a "
            "row without them is checked against nothing and passes vacuously"
        )
    if row_kind == "review" and review is None:
        raise RowError(
            "this row is kind=review and carries no review block — the range it covers "
            "is what a stacked push is checked against, so a review row without it "
            "contributes no coverage and leaves its commits unverified"
        )
    if push is not None and row_kind != "push":
        raise RowError(f"push= is only on a kind=push row, not kind={row_kind}")
    if review is not None and row_kind != "review":
        raise RowError(f"review= is only on a kind=review row, not kind={row_kind}")

    resolves: list[str] = []
    if index < len(rest) and rest[index].startswith("resolves="):
        resolves = parse_resolves(rest[index].split("=", 1)[1])
        index += 1

    if row_kind == "local-ops":
        values, index = required_fields(rest, index, ("op", "after"), row_kind)
        validate_after(values["after"], repo)
        if status != f"status={LOCAL_OPS_STATUS}":
            raise RowError(f"kind=local-ops requires status={LOCAL_OPS_STATUS}")
    elif row_kind == "standing-delegation":
        values, index = required_fields(
            rest, index, ("who", "scope", "conditions", "expiry"), row_kind
        )
        if status != f"status={STANDING_DELEGATION_STATUS}":
            raise RowError(f"kind=standing-delegation requires status={STANDING_DELEGATION_STATUS}")
    elif row_kind == "handoff":
        if status != f"status={HANDOFF_STATUS}":
            raise RowError(f"kind=handoff requires status={HANDOFF_STATUS}")
    elif row_kind == "repair-grant":
        if index >= len(rest) or not rest[index].startswith("finding="):
            raise RowError("kind=repair-grant requires finding= field")
        current_finding = finding_value(rest[index].split("=", 1)[1])
        index += 1
    elif row_kind == "cutover":
        if status != f"status={CUTOVER_STATUS}":
            raise RowError(f"kind=cutover requires status={CUTOVER_STATUS}")
        if index >= len(rest) or not rest[index].startswith("archive="):
            raise RowError("kind=cutover requires archive= field")
        archive = rest[index].split("=", 1)[1]
        if not ARCHIVE_RE.fullmatch(archive):
            raise RowError(f"field {rest[index]!r} is not a 64-character lowercase hex archive=")
        index += 1
        expected_gid, expected_archive = cutover_binding(ledger, prior_rows or [])
        if gid != expected_gid:
            raise RowError(f"cutover id {gid} is not the archive's next local id {expected_gid}")
        if archive != expected_archive:
            raise RowError(f"archive= mismatch: {LEGACY_LEDGER} hashes to {expected_archive}; it was edited or truncated")
        current_finding = None
    else:
        current_finding = None
    if (row_kind != "cutover" and not prior_rows and ledger is not None
            and legacy_archive(ledger) is not None):
        raise RowError(
            f"kind={row_kind} refused as the first row beside a non-empty {LEGACY_LEDGER}: "
            "it would restart ids at G1; the first row must be kind=cutover"
        )

    if prior_rows and LOCAL_ID_RE.fullmatch(gid):
        expected_gid = f"G{next_id_from_rows(prior_rows)}"
        if gid != expected_gid:
            raise RowError(f"gate id {gid} is not the next local id {expected_gid}")

    prev_hash = None
    if index < len(rest) and rest[index].startswith("prev_hash="):
        prev_hash = rest[index].split("=", 1)[1]
        if not PREV_HASH_RE.fullmatch(prev_hash):
            raise RowError(f"field {rest[index]!r} is not a 64-character lowercase hex prev_hash=")
        if not prior_rows:
            raise RowError("prev_hash= is present without a predecessor")
        if prev_hash != row_hash(prior_rows[-1]):
            raise RowError(
                f"prev_hash mismatch: expected {row_hash(prior_rows[-1])}, got {prev_hash}"
            )
        index += 1
    elif prior_rows:
        raise RowError("prev_hash= is missing; every row after the first is chained")

    if index >= len(rest) or not rest[index].startswith("words="):
        raise RowError("words= is missing or out of order")
    words = rest[index].split("=", 1)[1]
    if words not in WORDS_VALUES:
        raise RowError(f"field {rest[index]!r} is not one of {WORDS_VALUES}")
    index += 1

    if row_kind == "repair-grant":
        require_repair_progress(prior_rows or [], current_finding)

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
    validate_row_encodings(
        kind=row_kind, status=status_value, channel=channel,
        words=words, quote=quote, note=note,
    )

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
        if phead != m.group("head"):
            raise RowError(
                f"push head {phead} does not match row head {m.group('head')}"
            )
        if count != p.group("count"):
            raise RowError(
                f"count={p.group('count')} but {base}..{phead} carries {count} commits"
            )
        if " ".join(outside) != p.group("boundary"):
            raise RowError(
                f'boundary-check="{p.group("boundary")}" but the union over {base}..{phead} '
                f'outside the declared boundary is "{" ".join(outside)}"'
            )
        if row_kind == "push":
            require_review_coverage(prior_rows or [], repo, base, m.group("head"))

    if review is not None:
        r = REVIEW_RE.fullmatch(review)
        if not r:
            raise RowError(f"review block {review!r} is malformed")
        rbase, rhead = r.group("base"), r.group("head")
        commits = range_commits(repo, rbase, rhead)
        if rhead != m.group("head"):
            raise RowError(
                f"review head {rhead} does not match row head {m.group('head')}"
            )
        if str(len(commits)) != r.group("count"):
            raise RowError(
                f"count={r.group('count')} but {rbase}..{rhead} carries {len(commits)} commits"
            )

    if resolves:
        require_open_targets(prior_rows or [], resolves)


def check_mailbox_for_open_gate(row: str, mailbox: Path | None) -> None:
    """Apply opt-in S2 mailbox enforcement to an open human-gate row."""
    if mailbox is None:
        return
    kind, head, status = row_evidence(row)
    if kind not in HUMAN_GATE_KINDS or status != "open":
        return
    fields, _ = split_row(row)
    gid = fields[0]
    require_mailbox_attention(gid, head, mailbox)


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
    parser.add_argument("--mailbox", type=Path,
                        help="with --check, require a matching open-gate ATTENTION header")
    parser.add_argument("--open-gates", action="store_true",
                        help="print the structured open-gate id set, one id per line")
    parser.add_argument("--kind")
    parser.add_argument("--status")
    parser.add_argument("--channel")
    parser.add_argument("--writer")
    parser.add_argument("--op", help="the one local operation named by a local-ops row")
    parser.add_argument("--after", help="the merge/head a local operation followed")
    parser.add_argument("--who", help="the delegate named by a standing-delegation row")
    parser.add_argument("--scope", help="the delegated scope")
    parser.add_argument("--conditions", help="the delegation conditions")
    parser.add_argument("--expiry", help="the granting Human's expiry text")
    parser.add_argument("--finding", help="the repair-grant finding identity")
    parser.add_argument("--record", choices=RECORD_VALUES)
    parser.add_argument("--head", help="the row head as <branch>@<full 40-hex commit SHA>; "
                        "a past head requires --record reconstruction")
    parser.add_argument("--push-base", help="the push base — the remote tip the stack lands on "
                        "under batching, not the intake merge-base; the head is derived")
    parser.add_argument("--review-base", help="the base of the reviewed range on a kind=review "
                        "row; the head is HEAD and the range is what a stacked push is checked against")
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
        if not args.ledger.is_absolute():
            raise RowError(
                f"--ledger {args.ledger} is not absolute; the live ledger is "
                "~/.herdr/projects/<slug>/gates.md and a relative path resolves "
                "against the shell cwd, silently starting a stray G1"
            )
        if args.check and args.open_gates:
            raise RowError("--check and --open-gates are mutually exclusive")
        if args.open_gates:
            ignored = (
                args.kind, args.status, args.channel, args.writer, args.op, args.after,
                args.who, args.scope, args.conditions, args.expiry, args.finding,
                args.record, args.head, args.push_base, args.review_base, args.boundary, args.resolves, args.words,
                args.note, args.quote, args.quote_file, args.mailbox,
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
                check(rows[-1], args.repo, rows[:-1], args.ledger)
                check_mailbox_for_open_gate(rows[-1], args.mailbox)
                print(f"ok: {rows[-1].split(' | ')[0]} checks out")
            return 0

        if args.mailbox is not None:
            raise RowError("--mailbox requires --check")
        if not args.kind or not args.status:
            raise RowError("--kind and --status are required to append a row")
        if args.words is None:
            raise RowError("--words is required when appending a row")

        with locked_ledger(args.ledger, exclusive=True) as handle:
            before = handle_text(handle)
            existing_rows = ledger_rows(before)
            row = build(args, args.repo, existing_rows)
            check(row, args.repo, existing_rows, args.ledger)
            if before and not before.endswith("\n"):
                handle.seek(0, 2)
                handle.write("\n")
            handle.seek(0, 2)
            handle.write(row + "\n")
            handle.flush()
            stored_rows = ledger_rows(handle_text(handle))
            if not stored_rows or stored_rows[-1] != row:
                raise RowError("the row read back from disk is not the row written")
        print(row)
        return 0
    except RowError as exc:
        print(f"gate_row: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
