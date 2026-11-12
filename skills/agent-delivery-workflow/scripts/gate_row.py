#!/usr/bin/env python3
"""Write, check, and derive gate-ledger rows.

Every number in a row is derived here from git, never typed by a seat, and every
row this script appends is re-read from disk and re-derived before the command
exits. `--check` applies the same derivation to a row that already exists.

Row shape, one line, ` | ` between fields: `<id> | <ISO time> | kind=<kind> | <branch>@<head> |
status=<status>`, then the fields of FIELDS in table order, then the terminal `quote="<seat text>"`.

`quote=` is terminal and holds the seat's own verbatim text — the act, the refused
command on a denial row — so a `|` inside it is data, not a separator. The Human's words
are never stored: a `words=human` or `words=selected` row carries `brief=`, the Agent
brief restating them, and an empty `quote=`. Every other row has no `brief=`. `note=`
and `brief=` are the seat's own words and refuse `|` and `"`.

FIELDS is the ordered field table and KINDS the per-kind table; `parse_row` reads a
stored row by them, `build` writes one by them, and `check` applies the rules that need
git or the rows before it.
"""
from __future__ import annotations

import argparse
import dataclasses
import fcntl
import functools
import hashlib
import os
import re
import subprocess
import sys
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable, NamedTuple

import gitops
import state_root
from bounded_run import stop_group
from mailbox import parse_header

NOTE_MAX = 200
BRIEF_MAX = 500
KIND_RE = re.compile(r"^[a-z][a-z-]*$")
STATUS_RE = re.compile(r"^(open|(resolved|recorded):[a-z0-9-]+)$")
CHANNEL_RE = re.compile(r"^(direct-seat-pane|supervisor-relay):(typed|dialog)$")
WRITER_RE = re.compile(r"^[a-z][a-z0-9_-]*$")
SKILL_NAME_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
BRANCH_HEAD_RE = re.compile(rf"^(?P<branch>[^ |@]+)@(?P<head>{gitops.FULL_SHA})$")
# One feature-branch push lands in seconds; two minutes covers a slow link or a large first
# pack, and bounds how long a hung push or ls-remote can hold the ledger lock against every other writer.
PUSH_TIMEOUT_S = 120
PUSH_RE = re.compile(
    rf'^push=(?P<base>{gitops.FULL_SHA})\.\.(?P<head>{gitops.FULL_SHA}) '
    r'count=(?P<count>\d+) boundary="(?P<declared>[^"]*)" '
    r'boundary-check="(?P<boundary>[^"]*)"$'
)
REVIEW_RE = re.compile(
    rf'^review=(?P<base>{gitops.FULL_SHA})\.\.(?P<head>{gitops.FULL_SHA}) '
    r'count=(?P<count>\d+)$'
)
ID_RE = re.compile(r"^(?P<id>G[0-9]+) \|")
ROW_RE = re.compile(r"^(?P<id>\S+) \|")
LOCAL_ID_RE = re.compile(r"^G([0-9]+)$")
RESOLVE_ID_RE = re.compile(r'^[^,\s|"]+$')
RECORD_VALUES = ("timely", "reconstruction")
WORDS_VALUES = ("seat", "human", "selected", "none")
# The Human's words: typed in the pane, or the option the Human picked from a dialog.
HUMAN_WORDS = ("human", "selected")
LOCAL_OPS_STATUS = "recorded:local-ops"
STANDING_DELEGATION_STATUS = "recorded:standing-delegation"
CUTOVER_STATUS = "recorded:cutover"
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
FINDING_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]*$")
ISO_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
# Every character str.splitlines() splits on; a row is one line, so no field holds one.
LINE_BREAKS = "\n\r\x0b\x0c\x1c\x1d\x1e\x85  "


class RowError(Exception):
    pass


class GitRowError(RowError, gitops.GitError):
    """A failed git question inside a ledger operation: a RowError to gate_row's callers, a GitError to gitops."""


@dataclasses.dataclass
class RowRequest:
    """The values a row is built from; the CLI flags of the same names fill it."""
    kind: str | None = None
    status: str | None = None
    channel: str | None = None
    writer: str | None = None
    op: str | None = None
    after: str | None = None
    who: str | None = None
    scope: str | None = None
    conditions: str | None = None
    expiry: str | None = None
    finding: str | None = None
    skills: list[str] = dataclasses.field(default_factory=list)
    void: list[str] = dataclasses.field(default_factory=list)
    record: str | None = None
    head: str | None = None
    push_base: str | None = None
    review_base: str | None = None
    boundary: list[str] = dataclasses.field(default_factory=list)
    resolves: list[str] = dataclasses.field(default_factory=list)
    under: str | None = None
    words: str | None = None
    note: str = ""
    brief: str | None = None
    quote: str = ""
    quote_file: str = ""


class KindRule(NamedTuple):
    statuses: frozenset[str] = frozenset()  # the statuses the kind may carry; empty: any
    human_gate: bool = False  # an open row needs a supervisor ATTENTION mailbox entry
    seat_permission: bool = False  # a runtime-denial row: words=none, empty quote
    timely_at_ancestor: bool = False  # a past head is timely when it is an ancestor of HEAD
    human_words: bool = False  # words must be the Human's
    genesis: bool = False  # valid only as the stored first row, and then with any G<n> id


COMPLETED_DEPLOY = frozenset({"recorded:deploy", "resolved:deploy", "resolved:human"})
KINDS = {
    "push": KindRule(human_gate=True, timely_at_ancestor=True),
    "merge": KindRule(human_gate=True),
    "deploy": KindRule(COMPLETED_DEPLOY, human_gate=True, timely_at_ancestor=True),
    "push-gate": KindRule(human_gate=True, seat_permission=True),
    "merge-gate": KindRule(human_gate=True, seat_permission=True),
    "deploy-gate": KindRule(human_gate=True, seat_permission=True, timely_at_ancestor=True),
    "review": KindRule(timely_at_ancestor=True),
    "handoff": KindRule(frozenset({"recorded:handoff"}), timely_at_ancestor=True),
    "correction": KindRule(frozenset({"recorded:correction"})),
    "local-ops": KindRule(frozenset({LOCAL_OPS_STATUS})),
    "standing-delegation": KindRule(frozenset({STANDING_DELEGATION_STATUS}), human_words=True),
    "cutover": KindRule(frozenset({CUTOVER_STATUS}), genesis=True),
}


def kind_rule(kind: str | None) -> KindRule:
    return KINDS.get(kind, KindRule())


class PushBlock(NamedTuple):
    base: str
    head: str
    count: str
    declared: tuple[str, ...]
    boundary: str


class ReviewBlock(NamedTuple):
    base: str
    head: str
    count: str


def value_of(field: str) -> str:
    return field.split("=", 1)[1]


def tagged(field: str, name: str, pattern: re.Pattern[str]) -> str:
    if not field.startswith(f"{name}=") or not pattern.fullmatch(value_of(field)):
        raise RowError(f"field {field!r} is not a valid {name}=")
    return value_of(field)


def shaped(pattern: re.Pattern[str], noun: str) -> Callable[[str], str]:
    def parse(field: str) -> str:
        if not pattern.fullmatch(value_of(field)):
            raise RowError(f"field {field!r} is not {noun}")
        return value_of(field)
    return parse


def one_of(values: tuple[str, ...]) -> Callable[[str], str]:
    def parse(field: str) -> str:
        if value_of(field) not in values:
            raise RowError(f"field {field!r} is not one of {values}")
        return value_of(field)
    return parse


def text_of(name: str) -> Callable[[str], str]:
    return lambda field: field_text(name, value_of(field))


def field_text(name: str, value: str | None) -> str:
    value = (value or "").strip()
    if not value:
        raise RowError(f"{name}= is required")
    if "|" in value or '"' in value:
        raise RowError(f"{name}= refuses | and \" — it is a structured row field")
    return value


def parse_resolves(field: str) -> tuple[str, ...]:
    value = value_of(field)
    ids = value.split(",")
    if not value or any(not RESOLVE_ID_RE.fullmatch(gid) for gid in ids):
        raise RowError(f"resolves={value!r} contains an empty or malformed id")
    if len(ids) != len(set(ids)):
        raise RowError(f"resolves={value!r} names an id more than once")
    return tuple(ids)


def parse_skills(field: str) -> tuple[str, ...]:
    targets = value_of(field).split()
    if (not targets or targets != sorted(set(targets))
            or any(not SKILL_NAME_RE.fullmatch(item) for item in targets)):
        raise RowError("skills= must contain sorted, unique top-level skill names")
    return tuple(targets)


def parse_void(field: str) -> str:
    if not RESOLVE_ID_RE.fullmatch(value_of(field)):
        raise RowError(f"void={value_of(field)!r} is an empty or malformed id")
    return value_of(field)


def parse_after(field: str) -> str:
    value = field_text("after", value_of(field))
    if not BRANCH_HEAD_RE.fullmatch(value):
        raise RowError(f"after={value!r} is not <branch>@<head>")
    return value


def parse_finding(field: str) -> str:
    value = field_text("finding", value_of(field))
    if not FINDING_RE.fullmatch(value):
        raise RowError(
            f"finding={value!r} is not an identity token; use letters, digits, '.', '_', ':' or '-'")
    return value


def parse_push(field: str) -> PushBlock:
    match = PUSH_RE.fullmatch(field)
    if not match:
        raise RowError(f"push block {field!r} is malformed")
    declared = tuple(match.group("declared").split())
    if not declared:
        raise RowError(
            'this row declares boundary="" — an empty boundary puts every touched '
            "path outside it, which passes any row claiming the whole changed set"
        )
    return PushBlock(match.group("base"), match.group("head"), match.group("count"),
                     declared, match.group("boundary"))


def parse_review(field: str) -> ReviewBlock:
    match = REVIEW_RE.fullmatch(field)
    if not match:
        raise RowError(f"review block {field!r} is malformed")
    return ReviewBlock(match.group("base"), match.group("head"), match.group("count"))


class Field(NamedTuple):
    name: str
    parse: Callable[[str], object]
    kinds: frozenset[str] | None = None  # the kinds that carry it; None: every kind
    required: bool = False  # required wherever it is carried
    missing: str | None = None


def only(kind: str) -> frozenset[str]:
    return frozenset({kind})


# The ordered trailing fields of a row, after id, time, kind, branch@head and status.
FIELDS = (
    Field("channel", shaped(CHANNEL_RE, "a valid channel=")),
    Field("writer", shaped(WRITER_RE, "a valid writer=")),
    Field("record", one_of(RECORD_VALUES), required=True),
    Field("skills", parse_skills, only("deploy")),
    Field("push", parse_push, only("push"), True,
          "this row is kind=push and carries no push block — the range, count and "
          "boundary-check are the whole of what a push row is checked against, so a "
          "row without them is checked against nothing and passes vacuously"),
    Field("review", parse_review, only("review"), True,
          "this row is kind=review and carries no review block — the range it covers "
          "is what a stacked push is checked against, so a review row without it "
          "contributes no coverage and leaves its commits unverified"),
    Field("resolves", parse_resolves),
    Field("under", value_of),
    Field("void", parse_void, only("correction"), True,
          "kind=correction requires exactly one void= field after resolves="),
    Field("op", text_of("op"), only("local-ops"), True),
    Field("after", parse_after, only("local-ops"), True),
    Field("who", text_of("who"), only("standing-delegation"), True),
    Field("scope", text_of("scope"), only("standing-delegation"), True),
    Field("conditions", text_of("conditions"), only("standing-delegation"), True),
    Field("expiry", text_of("expiry"), only("standing-delegation"), True),
    Field("finding", parse_finding, only("repair-grant"), True),
    Field("archive", shaped(SHA256_RE, "a 64-character lowercase hex archive="), only("cutover"), True),
    Field("prev_hash", shaped(SHA256_RE, "a 64-character lowercase hex prev_hash=")),
    Field("words", one_of(WORDS_VALUES), required=True),
    Field("brief", value_of),
    Field("note", value_of, required=True),
)
FIELD_NAMES = tuple(entry.name for entry in FIELDS)
FLAG_FIELDS = ("channel", "writer", "skills", "resolves", "under", "void",
               "op", "after", "who", "scope", "conditions", "expiry", "finding")
FLAG_NAMES = {"skills": "--skill"}


@dataclasses.dataclass(frozen=True)
class Row:
    """A stored row read by the field table; absent optional fields are None or empty."""
    text: str
    gid: str
    when: str
    kind: str
    branch: str
    head: str
    status: str
    quote: str
    record: str
    words: str
    note: str
    channel: str | None = None
    writer: str | None = None
    skills: tuple[str, ...] = ()
    push: PushBlock | None = None
    review: ReviewBlock | None = None
    resolves: tuple[str, ...] = ()
    under: str | None = None
    void: str | None = None
    op: str | None = None
    after: str | None = None
    who: str | None = None
    scope: str | None = None
    conditions: str | None = None
    expiry: str | None = None
    finding: str | None = None
    archive: str | None = None
    prev_hash: str | None = None
    brief: str | None = None


def validate_row_encodings(
    *, kind: str, status: str, channel: str, words: str, quote: str, note: str,
    brief: str | None,
) -> None:
    """Enforce the note, brief, words, quote, channel and denial encodings on both append and check."""
    if not note.strip():
        raise RowError("note= is required and is the row's one-line finding")
    if len(note) > NOTE_MAX:
        raise RowError(
            f"note= is {len(note)} chars, over the {NOTE_MAX} cap — "
            "narrative belongs in the workspace record, not the ledger"
        )
    if "|" in note or '"' in note:
        raise RowError('note= refuses | and " — they are the row\'s delimiters')
    if words in HUMAN_WORDS:
        if brief is None or not brief.strip():
            raise RowError(
                f"brief= is required with words={words} — the Human's words are "
                "recorded as an Agent brief"
            )
        if len(brief) > BRIEF_MAX:
            raise RowError(f"brief= is {len(brief)} chars, over the {BRIEF_MAX} cap")
        if "|" in brief or '"' in brief:
            raise RowError('brief= refuses | and " — they are the row\'s delimiters')
    elif brief is not None:
        raise RowError(f"brief= is only on words=human or words=selected rows, not words={words}")
    if words in HUMAN_WORDS:
        if quote:
            raise RowError(
                f"words={words} stores no Human text: quote= must be empty, "
                "the Agent brief is brief="
            )
    elif (words == "none") != (quote == ""):
        raise RowError("words=none iff quote= is empty")
    if not quote and brief is None and status != "open":
        raise RowError("quote= or brief= is required unless status=open")
    if channel.endswith(":dialog"):
        if words != "selected":
            raise RowError(
                f"channel={channel} requires words=selected, not words={words}"
            )
        if not status.startswith("recorded:"):
            raise RowError(
                f"channel={channel} requires status=recorded:<kind>, not status={status}"
            )
    if (
        kind_rule(kind).seat_permission
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
    return re.search(
        rf"(?<![A-Za-z0-9_-]){re.escape(token)}(?![A-Za-z0-9_-])", text
    ) is not None


def require_mailbox_attention(gid: str, head: str, mailbox: Path) -> None:
    try:
        text = mailbox.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise RowError(f"mailbox {mailbox} could not be read: {exc}") from None
    for line in text.splitlines():
        header = parse_header(line)
        if (
            header is None or header.recipient != "supervisor"
            or header.head is None or header.attention is None
        ):
            continue
        if mailbox_token(header.attention, gid) or mailbox_token(header.attention, head):
            return
    raise RowError(
        f"open gate {gid} has no matching ATTENTION entry in mailbox {mailbox}; "
        f"a header must name gate id {gid} or exact head SHA {head}"
    )


GIT_MEMO: dict[tuple[str, tuple[str, ...], str | None], tuple[bool, str]] | None = None


@contextmanager
def memoized_git():
    global GIT_MEMO
    outer, GIT_MEMO = GIT_MEMO, {}
    try:
        yield
    finally:
        GIT_MEMO = outer


def memo_key(repo: Path, args: tuple[str, ...], stdin: str | None = None) -> tuple[str, tuple[str, ...], str | None]:
    return (str(repo), args, stdin)


def git(repo: Path, *args: str, stdin: str | None = None, timeout: float | None = None) -> str:
    key = memo_key(repo, args, stdin)
    if GIT_MEMO is not None and key in GIT_MEMO:
        ok, text = GIT_MEMO[key]
    else:
        try:
            ok, text = True, gitops.git(repo, *args, stdin=stdin, timeout=timeout)
        except gitops.GitError as exc:
            ok, text = False, str(exc)
        if GIT_MEMO is not None:
            GIT_MEMO[key] = (ok, text)
    if not ok:
        raise GitRowError(text)
    return text


def commit_query(name: str) -> tuple[str, ...]:
    return ("rev-parse", "--verify", f"{name}^{{commit}}")


def commit_of(repo: Path, name: str) -> str:
    return git(repo, *commit_query(name))


def warm_head_commits(repo: Path, rows: list[str]) -> None:
    """Resolve every row's head in one cat-file call, memoizing the hits only.

    Only a commit answer is memoized. A miss, an ambiguous name, or a failed call
    stays out of the memo, so the commit_of() call that asks for that head runs
    rev-parse and raises the message it always raised.
    """
    names = list(dict.fromkeys(parse_row(row).head for row in rows))
    if not names:
        return
    try:
        out = gitops.git(repo, "cat-file", "--batch-check", stdin="".join(f"{name}^{{commit}}\n" for name in names))
    except gitops.GitError:
        return
    lines = out.splitlines()
    if len(lines) != len(names):
        return
    for name, line in zip(names, lines):
        fields = line.split()
        if len(fields) == 3 and fields[1] == "commit":
            GIT_MEMO[memo_key(repo, commit_query(name))] = (True, fields[0])


def row_hash(row: str) -> str:
    return hashlib.sha256(row.encode("utf-8")).hexdigest()


def verify_chain(rows: list[str]) -> None:
    parse_prev_hash = next(entry.parse for entry in FIELDS if entry.name == "prev_hash")
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
        value = parse_prev_hash(hashes[0])
        expected = row_hash(rows[index - 1])
        if value != expected:
            raise RowError(
                f"prev_hash mismatch at row {fields[0]!r}: expected {expected}, got {value}"
            )


def text_rows(text: str) -> list[str]:
    """Every gate row in the text, in order, without verifying a chain.

    Rows end at "\n" only, so a row holding \x0b, \x0c, \x1c-\x1e, \x85, U+2028 or U+2029
    stays one row and split_row refuses it by field. The ledger read (newline=None, C3)
    has already turned a "\r" into "\n", so a CR row splits and is refused as malformed.
    """
    return [line for line in text.split("\n") if ROW_RE.match(line)]


def ledger_rows(text: str) -> list[str]:
    rows = text_rows(text)
    verify_chain(rows)
    return rows


def deployed_head(state: "LedgerState", skill: str, repo: Path) -> tuple[str, str, str]:
    """Select the newest deploy row of a validated ledger that names `skill`."""
    candidates = [row for row in state.parsed if row.kind == "deploy" and skill in row.skills]
    if not candidates:
        raise RowError(f"no completed target-bearing deploy row for skill {skill!r}")
    row = candidates[-1]
    return row.branch, commit_of(repo, row.head), row.text


def validate_ledger(rows: list[str], repo: Path) -> "LedgerState":
    cutovers = [index for index, row in enumerate(rows)
                if kind_rule(split_row(row)[0][2].removeprefix("kind=")).genesis]
    if cutovers and cutovers != [0]:
        raise RowError("kind=cutover is only valid as the first row")
    state = LedgerState()
    with memoized_git():
        warm_head_commits(repo, rows)
        for row in rows:
            check(row, repo, state)
            state.add(row)
    return state


def read_ledger_state(ledger: Path, repo: Path) -> "LedgerState":
    """Read the whole hash-chained ledger under a shared lock and validate it against `repo`."""
    with locked_ledger(ledger, exclusive=False) as handle:
        return validate_ledger(ledger_rows(handle_text(handle)), repo)


def reviewed_unpushed(state: "LedgerState", repo: Path) -> set[str]:
    """Commits in `repo` that are not pushed, are covered by a review PASS, and no open push-gate row names."""
    tips = open_push_gate_tips(state, repo)
    head = git(repo, "rev-parse", "HEAD")
    try:
        exclude = [git(repo, "rev-parse", "--verify", "@{upstream}")]
    except gitops.GitError:
        exclude = ["--remotes"]
    unpushed = set(git(repo, "rev-list", head, "--not", *exclude, *tips).splitlines())
    return state.covered_by_reviews(repo, unpushed) & unpushed


def select_deployed_head(ledger: Path, skill: str, repo: Path) -> tuple[str, str, str]:
    return deployed_head(read_ledger_state(ledger, repo), skill, repo)


def split_row(row: str) -> tuple[list[str], str]:
    prefix, marker, quoted = row.partition(" | quote=")
    if (not marker or not quoted.startswith('"') or not quoted.endswith('"')
            or not ID_RE.match(row)):
        raise RowError("quote= is not the terminal field, or the row has no G id")
    fields, quote = prefix.split(" | "), quoted[1:-1]
    gid = fields[0]
    if gid != ID_RE.match(row).group("id"):
        raise RowError("row does not start with a G id")
    if len(fields) < 5:
        raise RowError(f"row {gid!r} has {len(fields)} fields before quote=, expected at least 5")
    for position, field in enumerate(fields, 1):
        if not field or "|" in field:
            raise RowError(f"row {gid!r} field {position} is empty or holds |")
    for position, field in enumerate([*fields, f"quote={quote}"], 1):
        name, eq, _ = field.partition("=")
        breaks = [ch for ch in field if ch in LINE_BREAKS]
        if breaks:
            label = f"{name}=" if eq else f"field {position}"
            raise RowError(f"row {gid!r} {label} is one line; it holds line separator {breaks[0]!r}")
    return fields, quote


@functools.lru_cache(maxsize=None)
def parse_row(text: str) -> Row:
    """Read a stored row by FIELDS and KINDS; every refusal here needs neither git nor the rows before it."""
    fields, quote = split_row(text)
    gid, when, kind_field, head_field, status_field, *rest = fields
    kind = tagged(kind_field, "kind", KIND_RE)
    status = tagged(status_field, "status", STATUS_RE)
    if not ISO_RE.fullmatch(when):
        raise RowError(f"time {when!r} is not an ISO UTC timestamp")
    head = BRANCH_HEAD_RE.fullmatch(head_field)
    if not head:
        raise RowError(f"field {head_field!r} is not <branch>@<head>")
    for field in rest:
        if not field.startswith(tuple(f"{name}=" for name in FIELD_NAMES)):
            raise RowError(f"field {field.split('=')[0]!r} is not in the row schema")

    values: dict[str, object] = {}
    position = 0
    for entry in FIELDS:
        present = position < len(rest) and rest[position].startswith(f"{entry.name}=")
        carried = entry.kinds is None or kind in entry.kinds
        if present and not carried:
            raise RowError(f"{entry.name}= is only on a kind={'/'.join(sorted(entry.kinds))} row, not kind={kind}")
        if present:
            values[entry.name] = entry.parse(rest[position])
            position += 1
        elif entry.required and carried:
            if position < len(rest) and rest[position].split("=")[0] in values:
                raise RowError(f"field {rest[position].split('=')[0]!r} is out of order or duplicated")
            raise RowError(entry.missing or (
                f"{entry.name}= is missing or out of order" if entry.kinds is None
                else f"kind={kind} requires {entry.name}= field"))
    if position != len(rest):
        raise RowError(f"field {rest[position].split('=')[0]!r} is out of order or duplicated")

    rule = kind_rule(kind)
    if rule.statuses and status not in rule.statuses:
        if len(rule.statuses) == 1:
            raise RowError(f"kind={kind} requires status={next(iter(rule.statuses))}")
        raise RowError(f"kind={kind} requires a completed {kind} status")
    if rule.human_words and values["words"] not in HUMAN_WORDS:
        raise RowError(f"kind={kind} requires words=human or words=selected")
    validate_row_encodings(
        kind=kind, status=status, channel=values.get("channel") or "",
        words=values["words"], quote=quote, note=values["note"], brief=values.get("brief"),
    )
    return Row(
        text=text, gid=gid, when=when, kind=kind, branch=head.group("branch"), head=head.group("head"),
        status=status, quote=quote, **values,
    )


def range_commits(repo: Path, base: str, head: str) -> list[str]:
    try:
        return gitops.range_commits(repo, base, head, run=git)
    except gitops.GitError as exc:
        raise RowError(str(exc)) from None


class LedgerState:
    def __init__(self) -> None:
        self.rows: list[str] = []
        self.parsed: list[Row] = []
        self.last_when = ""
        self.max_id = 0
        self.latest: dict[str, tuple[int, str]] = {}  # gid -> (index, status) of its row
        self.kinds: dict[str, str] = {}
        self.ever_open: set[str] = set()
        self.resolved_at: dict[str, int] = {}  # gid -> index of the row that closed it
        self.voided_by: dict[str, str] = {}  # gid -> the correction that voided it
        self.standing: dict[str, int] = {}  # standing-delegation gid -> index
        # Review PASS rows by reviewed head: (index, gid, reviewed range base).
        self.reviews: dict[str, list[tuple[int, str, str]]] = {}
        self.repair_findings: set[str] = set()

    @property
    def next_id(self) -> int:
        return self.max_id + 1

    def add(self, text: str) -> None:
        row = parse_row(text)
        index = len(self.rows)
        self.rows.append(text)
        self.parsed.append(row)
        self.last_when = row.when
        local = LOCAL_ID_RE.fullmatch(row.gid)
        if local:
            self.max_id = max(self.max_id, int(local.group(1)))
        self.latest[row.gid] = (index, row.status)
        self.kinds[row.gid] = row.kind
        if row.status == "open":
            self.ever_open.add(row.gid)
        if row.kind == "standing-delegation":
            self.standing[row.gid] = index
        for target in row.resolves:
            self.resolved_at[target] = index
        if row.void is not None:
            self.voided_by[row.void] = row.gid
            self.resolved_at[row.void] = index
        if row.kind == "review" and row.status == "recorded:review-pass":
            self.reviews.setdefault(row.review.head, []).append((index, row.gid, row.review.base))
        if (row.status == "recorded:review-pass" or row.kind == "push"
                or (row.kind == "merge" and row.status.startswith("resolved:"))
                or row.kind == "repair-cap-gate"):
            self.repair_findings.clear()
        elif row.kind == "repair-grant":
            self.repair_findings.add(row.finding)

    def validate_void(self, target: str) -> None:
        if target not in self.latest:
            raise RowError(f"void={target} refused: target is not an earlier row of this ledger")
        kind, status = self.kinds[target], self.latest[target][1]
        if not (kind == "review" and status == "recorded:review-pass"):
            raise RowError(
                f"void={target} refused: target must be a kind=review status=recorded:review-pass row"
            )
        if target in self.voided_by:
            raise RowError(f"void={target} refused: already voided by {self.voided_by[target]}")

    def require_open(self, targets: tuple[str, ...]) -> None:
        for target in targets:
            if target in self.standing:
                if self.resolved_at.get(target, -1) > self.standing[target]:
                    raise RowError(f"resolves={target} refused: already-revoked")
                continue
            if target not in self.ever_open:
                raise RowError(f"resolves={target} refused: never-open; supersede by citing its id in note=")
            own = self.latest.get(target)
            if own is None or own[1] != "open" or self.resolved_at.get(target, -1) > own[0]:
                raise RowError(f"resolves={target} refused: already-closed")

    def require_in_force(self, target: str, when: str) -> None:
        if self.kinds.get(target) != "standing-delegation":
            raise RowError(f"under={target} is not an earlier kind=standing-delegation row")
        index = self.standing[target]
        if self.resolved_at.get(target, -1) > index:
            raise RowError(f"under={target} refused: the delegation is revoked")
        expiry = self.parsed[index].expiry
        if ISO_RE.fullmatch(expiry) and when >= expiry:
            raise RowError(f"under={target} refused: the delegation expired at {expiry}")

    def require_repair_progress(self, finding: str) -> None:
        if finding in self.repair_findings:
            raise RowError(
                f"repair cap reached (finding={finding} repeated since the last progress "
                "boundary): record kind=repair-cap-gate and route the Human instead of "
                "another kind=repair-grant"
            )

    def open_gate_ids(self) -> list[str]:
        open_rows = [
            (index, gid)
            for gid, (index, status) in self.latest.items()
            if status == "open" and self.resolved_at.get(gid, -1) <= index
        ]
        return [gid for _, gid in sorted(open_rows)]

    def covered_by_reviews(self, repo: Path, commits: set[str]) -> set[str]:
        covered: set[str] = set()
        for sha in commits:
            for _, gid, rbase in self.reviews.get(sha, []):
                if gid not in self.voided_by:
                    covered.update(range_commits(repo, rbase, sha))
        return covered

    def require_review_coverage(self, repo: Path, base: str, head: str) -> None:
        pushed = set(range_commits(repo, base, head))
        covered = self.covered_by_reviews(repo, pushed) | gitops.landed_commits(repo, head, pushed, run=git)
        grew = True
        while grew:
            grew = False
            for sha in pushed - covered:
                parents = gitops.clean_merge_parents(repo, sha, run=git)
                if parents and all(p in covered or p not in pushed for p in parents):
                    covered.add(sha)
                    grew = True
        missing = [sha for sha in pushed if sha not in covered]
        if missing:
            voided = sorted(
                (index, f"{gid} review row is void ({self.voided_by[gid]})")
                for sha in pushed
                for index, gid, _ in self.reviews.get(sha, [])
                if gid in self.voided_by
            )
            detail = f"; {', '.join(text for _, text in voided)}" if voided else ""
            raise RowError(
                f"refusing push of {base}..{head}: {', '.join(sorted(missing))} "
                f"is not covered by any review PASS range{detail}"
            )


def open_push_gate_tips(state: LedgerState, repo: Path) -> list[str]:
    open_ids = set(state.open_gate_ids())
    return [commit_of(repo, row.head) for row in state.parsed
            if row.gid in open_ids and row.kind == "push-gate"]


def derive_push(repo: Path, base: str, head: str, boundary: list[str]) -> tuple[str, list[str]]:
    for b in boundary:
        if not b or b.split() != [b]:
            raise RowError(
                f"boundary path {b!r} is empty or holds whitespace — --boundary is one flag "
                "per path, and a path with a space cannot be read back out of boundary-check"
            )
    commits = range_commits(repo, base, head)
    count = str(len(commits))
    changed = set(path for path in git(
        repo, "diff-tree", "--root", "-m", "--no-commit-id", "--name-only", "-r", "-z", "--stdin",
        stdin="\n".join(commits) + "\n",
    ).split("\0") if path)
    outside = sorted(path for path in changed
                     if not any(b == "." or path == b or path.startswith(b.rstrip("/") + "/")
                                for b in boundary))
    if any('"' in path or "|" in path or path.split() != [path] for path in outside):
        raise RowError("a path outside the boundary contains a delimiter character")
    return count, outside


def resolve_row_head(request: RowRequest, repo: Path) -> tuple[str, str]:
    current_branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    current_head = git(repo, "rev-parse", "HEAD")
    requested = request.head
    if not requested:
        return current_branch, current_head
    match = BRANCH_HEAD_RE.fullmatch(requested)
    if not match:
        raise RowError(
            f"--head {requested!r} is not <branch>@<full 40-hex commit SHA>"
        )
    branch, head = match.group("branch"), match.group("head")
    commit_of(repo, head)
    if head != current_head:
        timely_at_ancestor = (
            kind_rule(request.kind).timely_at_ancestor
            and gitops.is_ancestor(repo, head, current_head)
        )
        if not timely_at_ancestor and request.record != "reconstruction":
            raise RowError(
                f"--head {requested} differs from repository HEAD {current_head}; "
                "use --record reconstruction to record a past head"
            )
    return branch, head


def push_head(repo: Path, branch: str, head: str) -> str:
    try:
        product = git(repo, "symbolic-ref", "--short", "refs/remotes/origin/HEAD")
    except gitops.GitError:
        raise RowError(
            "--push refused: origin/HEAD is unset, so the product line is unknown; "
            "run git remote set-head origin --auto"
        ) from None
    if branch in {"HEAD", product.split("/", 1)[1]}:
        raise RowError(
            f"--push refused: {branch} is not a feature branch; the product line "
            f"{product} moves only by merge"
        )
    refspec = f"{head}:refs/heads/{branch}"
    proc = subprocess.Popen(
        ["git", "-C", str(repo), "push", "--no-follow-tags", "--recurse-submodules=no", "origin", refspec],
        stdin=subprocess.DEVNULL, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8",
        start_new_session=True, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
    )
    try:
        _, err = proc.communicate(timeout=PUSH_TIMEOUT_S)
    except subprocess.TimeoutExpired:
        stop_group(proc, 5)
        proc.communicate()
        raise RowError(
            f"git push origin {refspec} passed its {PUSH_TIMEOUT_S}s limit; its process group was "
            "killed and no row was written; read git ls-remote origin before retrying"
        ) from None
    if proc.returncode:
        raise RowError(f"git push origin {refspec} failed: {err.strip()}")
    return refspec


def derived_blocks(request: RowRequest, repo: Path, branch: str, head: str,
                   landed: bool) -> tuple[str | None, str | None]:
    """The push= and review= values a push or review row derives from its range flags."""
    if request.kind == "push":
        if not request.push_base:
            raise RowError(
                "a push row needs --push-base: the range, count and boundary-check are "
                "derived from it, and a push row carrying none of them asserts that a "
                "push happened while holding no evidence that it did"
            )
        if landed:
            remote = git(
                repo, "ls-remote", "origin", f"refs/heads/{branch}", timeout=PUSH_TIMEOUT_S).split()
            if not remote:
                raise RowError(
                    f"origin/{branch} is absent — the push this row claims has not landed"
                )
            remote_tip = remote[0]
            try:
                commit_of(repo, remote_tip)
            except gitops.GitError:
                raise RowError(
                    f"origin/{branch} points to {remote_tip}, which is not present locally — "
                    "the Lead must git fetch it; gate_row never fetches"
                ) from None
            if not gitops.is_ancestor(repo, head, remote_tip):
                raise RowError(
                    f"origin/{branch} is {remote_tip}, but {head} is not an ancestor of "
                    "the remote tip — the push this row claims has not landed"
                )
        if not request.boundary:
            raise RowError(
                "a push row needs --boundary: the declared paths the push was judged "
                "against are part of the row, and refusing here keeps the bad row out "
                "of an append-only file rather than rejecting it after it lands"
            )
        count, outside = derive_push(repo, request.push_base, head, request.boundary)
        return (f'{request.push_base}..{head} count={count} boundary="{" ".join(request.boundary)}" '
                f'boundary-check="{" ".join(outside)}"'), None
    if request.kind == "review":
        if not request.review_base:
            raise RowError(
                "a review row needs --review-base: the range it covers is the whole of "
                "what a stacked push is checked against, so a review row naming no range "
                "leaves the commits it reviewed uncovered when the push walks the stack"
            )
        if request.push_base or request.boundary:
            raise RowError("--push-base and --boundary are only meaningful on a push row")
        commits = range_commits(repo, request.review_base, head)
        return None, f"{request.review_base}..{head} count={len(commits)}"
    if request.review_base:
        raise RowError(
            f"--review-base is only meaningful on a review row, and this row is "
            f"kind={request.kind} — an argument accepted and silently dropped is how a row "
            "loses the evidence it claims to carry"
        )
    if request.push_base or request.boundary:
        flag = "--push-base" if request.push_base else "--boundary"
        raise RowError(
            f"{flag} is only meaningful on a push row, and this row is kind={request.kind} "
            "— an argument accepted and silently dropped is how a row loses the evidence "
            "it claims to carry"
        )
    return None, None


def flag_values(request: RowRequest) -> dict[str, str]:
    """The field values the request's flags name, refused on a kind that does not carry the field."""
    if len(request.void) > 1:
        raise RowError("kind=correction takes exactly one --void <id>")
    supplied: dict[str, str] = {}
    for entry in (entry for entry in FIELDS if entry.name in FLAG_FIELDS):
        raw = getattr(request, entry.name)
        if not raw:
            continue
        flag = FLAG_NAMES.get(entry.name, f"--{entry.name}")
        if entry.kinds is not None and request.kind not in entry.kinds:
            raise RowError(
                f"{flag} is only meaningful on kind={'/'.join(sorted(entry.kinds))}, not kind={request.kind}")
        if entry.name == "skills":
            for skill in raw:
                if not SKILL_NAME_RE.fullmatch(skill):
                    raise RowError(f"--skill {skill!r} is not a top-level skill name")
            raw = " ".join(sorted(raw))
        elif entry.name == "resolves":
            raw = ",".join(raw)
            parse_resolves(f"resolves={raw}")
        elif entry.name == "void":
            raw = raw[0]
            parse_void(f"void={raw}")
        supplied[entry.name] = field_text(entry.name, raw)
    return supplied


def request_words(request: RowRequest) -> str:
    """The row's words, refusing a request too incomplete to build a row from."""
    if not request.kind or not request.status:
        raise RowError("--kind and --status are required to append a row")
    if request.words is None:
        raise RowError("--words is required when appending a row")
    return request.words


def build(request: RowRequest, repo: Path, state: LedgerState,
          target: tuple[str, str], landed: bool = True) -> str:
    words = request_words(request)
    note = request.note.strip()
    brief = None if request.brief is None else request.brief.strip()
    if request.quote and request.quote_file:
        raise RowError("--quote and --quote-file are mutually exclusive")
    if request.quote_file:
        try:
            with Path(request.quote_file).open("r", encoding="utf-8", newline="") as handle:
                quote = handle.read()
        except (OSError, UnicodeError) as exc:
            raise RowError(f"--quote-file {request.quote_file!r} could not be read: {exc}") from None
        if quote.endswith("\r\n"):
            quote = quote[:-2]
        elif quote.endswith("\n"):
            quote = quote[:-1]
    else:
        quote = request.quote
    # note, brief and quote are serialized below, so their delimiters are refused before they can reshape the row.
    validate_row_encodings(
        kind=request.kind, status=request.status, channel=request.channel or "",
        words=words, quote=quote, note=note, brief=brief,
    )
    if kind_rule(request.kind).genesis:
        raise RowError("kind=cutover is valid only as a stored first-row genesis and cannot be appended")
    branch, head = target
    values = flag_values(request)
    values["record"] = request.record or "timely"
    values["push"], values["review"] = derived_blocks(request, repo, branch, head, landed)
    if state.rows:
        values["prev_hash"] = row_hash(state.rows[-1])
    values.update(words=words, brief=brief, note=note)
    fields = [
        f"G{state.next_id}",
        datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        f"kind={request.kind}",
        f"{branch}@{head}",
        f"status={request.status}",
        *(f"{name}={values[name]}" for name in FIELD_NAMES if values.get(name) is not None),
        f'quote="{quote}"',
    ]
    row = " | ".join(fields)
    check(row, repo, state)
    return row


def check(text: str, repo: Path, state: LedgerState) -> None:
    row = parse_row(text)
    if state.rows and row.when < state.last_when:
        raise RowError(
            f"timestamp regression: predecessor {state.last_when} -> this row {row.when}"
        )
    # The object, not the ref: a merge that deletes the branch must not make a
    # landed row permanently uncheckable. Retrievability belongs to the object.
    commit_of(repo, row.head)
    if kind_rule(row.kind).genesis and not state.rows:
        local_id = LOCAL_ID_RE.fullmatch(row.gid)
        if local_id is None or int(local_id.group(1)) < 1:
            raise RowError("kind=cutover genesis id must be G<n> with n at least 1")
    elif row.gid != f"G{state.next_id}":
        raise RowError(f"gate id {row.gid} is not the next local id G{state.next_id}")
    if row.skills:
        deployed_skills = git(repo, "ls-tree", "-d", "--name-only", f"{row.head}:skills").splitlines()
        if not set(row.skills) <= set(deployed_skills):
            raise RowError("skills= contains a target absent from the deploy row head")
    if row.void is not None:
        state.validate_void(row.void)
    if row.after is not None:
        commit_of(repo, row.after.split("@", 1)[1])
    if row.under is not None:
        if row.words != "seat":
            raise RowError(f"under={row.under} records the seat's own decision and requires words=seat")
        state.require_in_force(row.under, row.when)
    if row.finding is not None:
        state.require_repair_progress(row.finding)

    if row.push is not None:
        push = row.push
        count, outside = derive_push(repo, push.base, push.head, list(push.declared))
        if push.head != row.head:
            raise RowError(f"push head {push.head} does not match row head {row.head}")
        if count != push.count:
            raise RowError(f"count={push.count} but {push.base}..{push.head} carries {count} commits")
        if " ".join(outside) != push.boundary:
            raise RowError(
                f'boundary-check="{push.boundary}" but the union over {push.base}..{push.head} '
                f'outside the declared boundary is "{" ".join(outside)}"'
            )
        state.require_review_coverage(repo, push.base, row.head)

    if row.review is not None:
        review = row.review
        commits = range_commits(repo, review.base, review.head)
        if review.head != row.head:
            raise RowError(f"review head {review.head} does not match row head {row.head}")
        if str(len(commits)) != review.count:
            raise RowError(
                f"count={review.count} but {review.base}..{review.head} carries {len(commits)} commits"
            )

    if row.resolves:
        state.require_open(row.resolves)


def check_mailbox_for_open_gate(row: Row, mailbox: Path | None) -> None:
    if mailbox is None or not kind_rule(row.kind).human_gate or row.status != "open":
        return
    require_mailbox_attention(row.gid, row.head, mailbox)


def require_absolute(ledger: Path) -> None:
    if not ledger.is_absolute():
        raise RowError(
            f"--ledger {ledger} is not absolute; the live ledger is "
            f"{state_root.STATE_ROOT}/<slug>/{state_root.LEDGER} and a relative path resolves "
            "against the shell cwd, silently starting a stray G1"
        )


@contextmanager
def locked_ledger(ledger: Path, exclusive: bool):
    require_absolute(ledger)
    if not exclusive and not ledger.exists():
        raise RowError(f"{ledger} holds no gate ledger")
    mode = "a+" if exclusive else "r"
    try:
        with ledger.open(mode, encoding="utf-8") as handle:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX if exclusive else fcntl.LOCK_SH)
            try:
                yield handle
            finally:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)
    except FileNotFoundError:
        raise RowError(f"{ledger} holds no gate ledger") from None


def handle_text(handle) -> str:
    handle.seek(0)
    try:
        return handle.read()
    except UnicodeError as exc:
        raise RowError(f"ledger is not UTF-8: {exc}") from None


def preview_row(ledger: Path, repo: Path, request: RowRequest) -> str:
    """The row `request` would append to `ledger`, built and checked against it; nothing is written."""
    request_words(request)
    if ledger.exists():
        with locked_ledger(ledger, exclusive=False) as handle:
            state = validate_ledger(ledger_rows(handle_text(handle)), repo)
    else:
        require_absolute(ledger)
        state = LedgerState()
    return build(request, repo, state, resolve_row_head(request, repo))


def append_row(ledger: Path, repo: Path, request: RowRequest, push: bool = False) -> str:
    """Build, check, append and read back the row for `request`; `push` pushes the row's head first."""
    request_words(request)
    pushed = ""
    with locked_ledger(ledger, exclusive=True) as handle:
        before = handle_text(handle)
        state = validate_ledger(ledger_rows(before), repo)
        target = resolve_row_head(request, repo)
        try:
            if push:
                if request.kind != "push":
                    raise RowError(f"--push is only meaningful on kind=push, not kind={request.kind}")
                build(request, repo, state, target, landed=False)
                pushed = push_head(repo, *target)
            row = build(request, repo, state, target)
            if before and not before.endswith("\n"):
                handle.seek(0, 2)
                handle.write("\n")
            handle.seek(0, 2)
            handle.write(row + "\n")
            handle.flush()
            stored_rows = ledger_rows(handle_text(handle))
            if not stored_rows or stored_rows[-1] != row:
                raise RowError("the row read back from disk is not the row written")
        except RowError as exc:
            if pushed:
                raise RowError(f"git push origin {pushed} ran, but {exc}") from None
            raise
    return row


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--ledger", required=True, type=Path,
                        help="path to gates.md; the Reviewer round-trips against a scratch file")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true",
                      help="check every row of the ledger against its predecessors, then report the last")
    parser.add_argument("--mailbox", type=Path,
                        help="with --check, require a matching open-gate ATTENTION header")
    mode.add_argument("--open-gates", action="store_true",
                      help="print the structured open-gate id set, one id per line")
    mode.add_argument("--deployed-head", metavar="SKILL",
                      help="select the latest applicable completed deploy row for SKILL after full ledger verification")
    parser.add_argument("--kind")
    parser.add_argument("--status")
    parser.add_argument("--channel")
    parser.add_argument("--writer")
    parser.add_argument("--op", help="the one local operation named by a local-ops row")
    parser.add_argument("--after", help="the merge/head a local operation followed")
    parser.add_argument("--who", help="the delegate named by a standing-delegation row")
    parser.add_argument("--scope", help="the delegated scope")
    parser.add_argument("--conditions", help="the delegation conditions")
    parser.add_argument("--expiry", help="the granting Human's expiry; an ISO-8601 UTC timestamp "
                        "is enforced by --under")
    parser.add_argument("--finding", help="the repair-grant finding identity")
    parser.add_argument("--skill", dest="skills", action="append", default=[],
                        help="top-level skill deployed; repeat for each exact target")
    parser.add_argument("--void", action="append", default=[],
                        help="the earlier review-pass row a correction voids")
    parser.add_argument("--record", choices=RECORD_VALUES)
    parser.add_argument("--head", help="the row head as <branch>@<full 40-hex commit SHA>; "
                        "a past head is timely when its kind is marked timely_at_ancestor in "
                        "KINDS and it is an ancestor of HEAD, otherwise use --record reconstruction")
    parser.add_argument("--push-base", help="the push base — the remote tip the stack lands on "
                        "under batching, not the intake merge-base; the head is derived")
    parser.add_argument("--review-base", help="the base of the reviewed range on a kind=review "
                        "row; the head is HEAD and the range is what a stacked push is checked against")
    parser.add_argument("--push", action="store_true",
                        help="on kind=push: check the row, then run the non-force git push of "
                        "<head> to origin/<branch> (never the product line), then append the row")
    parser.add_argument("--boundary", action="append", default=[],
                        help="a declared boundary path; repeatable, required to append a push "
                             "row, and written into the row so --check derives against the "
                             "same paths without being told them")
    parser.add_argument("--resolves", action="append", default=[],
                        help="an open gate id to resolve; repeatable and comma-separated")
    parser.add_argument("--under", help="the in-force kind=standing-delegation id a row answered "
                        "under it names; the row requires --words seat")
    parser.add_argument("--words", choices=WORDS_VALUES,
                        help="whose words the row records; required when appending")
    parser.add_argument("--note", default="")
    parser.add_argument("--brief",
                        help="the English Agent brief restating the Human's words; required with "
                        "--words human or selected, refused otherwise")
    parser.add_argument("--quote", default="")
    parser.add_argument("--quote-file", default="",
                        help="read the seat's verbatim text from a UTF-8 file")
    args = parser.parse_args(argv)
    request = RowRequest(**{f.name: getattr(args, f.name) for f in dataclasses.fields(RowRequest)})

    try:
        read_mode = ("--check" if args.check else "--open-gates" if args.open_gates
                     else "--deployed-head" if args.deployed_head else None)
        if args.mailbox is not None and not args.check:
            raise RowError("--mailbox requires --check")
        if read_mode and (any(vars(request).values()) or args.push):
            raise RowError(f"{read_mode} cannot be combined with append arguments")
        if args.deployed_head:
            branch, head, source_row = select_deployed_head(args.ledger, args.deployed_head, args.repo)
            print(f"{branch}@{head}\n{source_row}")
            return 0
        if args.open_gates:
            ids = read_ledger_state(args.ledger, args.repo).open_gate_ids()
            sys.stdout.write("".join(f"{gid}\n" for gid in ids))
            return 0

        if args.check:
            state = read_ledger_state(args.ledger, args.repo)
            if not state.rows:
                raise RowError(f"{args.ledger} holds no gate row")
            check_mailbox_for_open_gate(state.parsed[-1], args.mailbox)
            print(f"ok: {state.parsed[-1].gid} checks out")
            return 0

        print(append_row(args.ledger, args.repo, request, push=args.push))
        return 0
    except RowError as exc:
        print(f"gate_row: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
