#!/usr/bin/env python3
"""Check the dispatch-critical fields in a charter and staffing record."""
from __future__ import annotations

import argparse
import hashlib
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path
from typing import NamedTuple

import backend

DISPOSITION_RE = re.compile(
    r"^\s*[*#`_-]*\s*Disposition:\s*[*_`]*\s*(Engineer|Reviewer|Architect)\b",
    re.IGNORECASE | re.MULTILINE,
)
HEAD_RE = re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])", re.IGNORECASE)
RANGE_RE = re.compile(
    r"(?<![0-9a-f])([0-9a-f]{40})\.\.\.?([0-9a-f]{40})(?![0-9a-f])", re.IGNORECASE
)
STAFFED_HEAD_RE = re.compile(
    r"(?:^\s*HEAD:\s*|\bhead=)(?:\S*@)?([0-9a-f]{40})(?![0-9a-f])",
    re.IGNORECASE | re.MULTILINE,
)
NULL_OID = "0" * 40
SPLICE_PREFIX = 7
PRIOR_RE = re.compile(r"^\W*Prior reviews?\W*:?[ \t]*(.*)$", re.IGNORECASE | re.MULTILINE)
PRIOR_GLOSS_RE = re.compile(r"\(`none`, or the prior FAIL report[^)]*\)")
UNIT_RANGE_RE = re.compile(
    r"^\W*Reviewed unit\W*:?.*?(?<![0-9a-f])([0-9a-f]{7,40})\.\.\.?([0-9a-f]{7,40})(?![0-9a-f])",
    re.IGNORECASE | re.MULTILINE,
)
SHORT_SHA_RE = re.compile(r"(?<![0-9a-f])[0-9a-f]{7,40}(?![0-9a-f])", re.IGNORECASE)
REPORT_FILE_RE = re.compile(r"/[^\s\"'`$\\]*/report-[^\s/\"'`$\\]+\.md")
STAFFING_TEMPLATE = Path(__file__).resolve().parents[1] / "templates" / "reviewer-staffing-record.txt"
SEAT_RE = re.compile(r"^[ \t]*(ENGINEER|REVIEWER|ARCHITECT):(.*)$", re.IGNORECASE | re.MULTILINE)
_FIELD = r"(?:^|\s)([a-z][a-z-]*)=(\S*)"
# The keys that identify a seat; every other key all seat lines of the template share is evidence checked here.
IDENTITY_KEYS = ("kind", "model", "seat", "workspace")
PLACEHOLDER_RE = re.compile(r"<[^>\r\n]+>")
WAKE_GUARD_RE = re.compile(
    r"never\s+run\s+`?mailbox\.py\s+--wake`?\s+against\s+a\s+real\s+seat",
    re.IGNORECASE,
)
OCR_STEP_RES = (
    re.compile(r"ocr\s+delegate\s+preview", re.IGNORECASE),
    re.compile(r"ocr\s+delegate\s+rule", re.IGNORECASE),
)
KILL_GUARD_RE = re.compile(r"never\s+kill\s+a\s+process\s+by\s+pattern", re.IGNORECASE)
TAKEOVER_GUARD_RE = re.compile(
    r"never\s+stop,\s+remove,\s+or\s+take\s+over\s+a\s+container,\s+process,\s+or\s+port",
    re.IGNORECASE,
)
REVIEW_ORDER_RE = re.compile(
    r"only\s+then\s+read\s+the\s+implementation\s+reports", re.IGNORECASE
)
TIME_LIMIT_RE = re.compile(
    r"^\s*time\s+limit:[^\n]*BLOCKED\s+\(time\s+limit\)", re.IGNORECASE | re.MULTILINE
)


class StaffedSeat(NamedTuple):
    role: str  # ENGINEER, REVIEWER or ARCHITECT
    name: str
    fields: dict[str, str]  # lowercase key -> value, first occurrence
    line: str


def fields_of(text: str) -> dict[str, str]:
    """The `key=value` tokens of a staffing-record line, keys lowercased, the first occurrence of a key kept."""
    fields: dict[str, str] = {}
    for key, value in re.findall(_FIELD, text, re.IGNORECASE):
        fields.setdefault(key.lower(), value)
    return fields


def staffed_seats(text: str) -> list[StaffedSeat]:
    """Every ENGINEER, REVIEWER and ARCHITECT line of a staffing record, in order."""
    return [
        StaffedSeat(match.group(1).upper(), (match.group(2).split() or [""])[0],
                    fields_of(match.group(2)), match.group(0))
        for match in SEAT_RE.finditer(text)
    ]


def _required_keys() -> tuple[str, ...]:
    seats = staffed_seats(STAFFING_TEMPLATE.read_text(encoding="utf-8"))
    return tuple(
        key for key in seats[0].fields
        if key not in IDENTITY_KEYS and all(key in seat.fields for seat in seats)
    )


REQUIRED_KEYS = _required_keys()


def _read(path: Path, label: str) -> tuple[str, bytes]:
    try:
        content = path.read_bytes()
        return content.decode("utf-8"), content
    except (OSError, UnicodeError) as exc:
        raise ValueError(f"could not read {label} {path}: {exc}") from exc


def _send_block_problems(text: str, lead: str, seats: backend.Backend) -> list[str]:
    paths = list(dict.fromkeys(REPORT_FILE_RE.findall(text)))
    if not paths:
        return ["missing report-by-prompt block: absolute <run-dir>/report-<peer>.md path"]
    try:
        blocks = [seats.send_block(lead, path) for path in paths]
    except ValueError as exc:
        return [f"report-by-prompt block cannot be rendered: {exc}"]
    if any(
        block.send_command in text and (block.failure_notice is None or block.failure_notice in text)
        for block in blocks
    ):
        return []
    return [f"missing report-by-prompt block, as {seats.name} renders it:\n{blocks[0].text}"]


def _disposition(text: str) -> str | None:
    match = DISPOSITION_RE.search(text)
    return match.group(1).lower() if match else None


def _charter_problems(text: str, lead: str, seats: backend.Backend) -> list[str]:
    problems: list[str] = []
    disposition = _disposition(text)
    if disposition is None:
        problems.append("missing Disposition: Engineer / Reviewer / Architect line")

    if disposition == "engineer" and not re.search(r"owned paths", text, re.IGNORECASE):
        problems.append("missing owned paths section")
    if disposition == "reviewer" and HEAD_RE.search(text) is None:
        problems.append("missing exact-head 40-hex SHA")
    if disposition == "reviewer" and WAKE_GUARD_RE.search(text) is None:
        problems.append(
            "missing live-wake guard: Never run `mailbox.py --wake` against a real seat"
        )

    if disposition == "reviewer" and not all(r.search(text) for r in OCR_STEP_RES):
        problems.append("missing OCR delegate step: ocr delegate preview and ocr delegate rule")
    if disposition == "reviewer" and REVIEW_ORDER_RE.search(text) is None:
        problems.append(
            "missing review order: only then read the implementation reports"
        )
    if disposition == "reviewer" and TIME_LIMIT_RE.search(text) is None:
        problems.append("missing time limit: BLOCKED (time limit)")
    if KILL_GUARD_RE.search(text) is None:
        problems.append("missing pattern-kill guard: Never kill a process by pattern")
    if TAKEOVER_GUARD_RE.search(text) is None:
        problems.append(
            "missing takeover guard: Never stop, remove, or take over a container, process, or port"
        )

    problems.extend(_send_block_problems(text, lead, seats))
    if "SEND-FAILED" not in text:
        problems.append("missing report-by-prompt block: SEND-FAILED fallback")
    return problems


def _sandbox_exec_available() -> bool:
    return shutil.which("sandbox-exec") is not None


def _charter_allows_docker(charter: str) -> bool:
    for clause in re.split(r"[;.!?:\n]", charter):
        if not re.search(r"\bdocker\b", clause, re.IGNORECASE):
            continue
        prohibited = re.search(
            r"\b(?:no|never|not|without|prohibit\w*|forbid\w*)\b[^,]*\bdocker\b"
            r"|\bdocker\b[^,]*\b(?:not allowed|prohibit\w*|forbid\w*)\b",
            clause,
            re.IGNORECASE,
        )
        if prohibited is not None:
            continue
        if re.search(
            r"\bdocker\s+(?:run|compose|exec|build|ps|pull|push|image|container|volume|"
            r"network|logs|inspect|start|stop|rm|create|version)\b"
            r"|\ballows?\s+(?:containers|docker)\b"
            r"|\bdocker\s+(?:is\s+)?allowed\b",
            clause,
            re.IGNORECASE,
        ):
            return True
    return False


def _staffing_problems(
    text: str, disposition: str | None, staffing_path: Path, charter: str
) -> list[str]:
    staffed = staffed_seats(text)
    if not staffed:
        return ["staffing record has no ENGINEER, REVIEWER, or ARCHITECT seat lines"]

    problems: list[str] = []
    for seat_line in staffed:
        seat, line, fields = seat_line.role, seat_line.line, seat_line.fields
        for key in REQUIRED_KEYS:
            if key not in fields:
                problems.append(f"{seat} seat missing {key}=")
        dialog = fields.get("dialog")
        evidence = [fields.get(key) for key in ("dialog-tools", "dialog-deny", "dialog-source")]
        if dialog and dialog.lower() not in {"denied", "absent"}:
            problems.append(f"{seat} seat cannot have dialog={dialog}")
        elif dialog and all(evidence):
            tool_names, deny, source = evidence
            if source.lower() == "none":
                problems.append(f"{seat} seat dialog-source must identify inventory evidence")
            if dialog.lower() == "absent":
                if tool_names.lower() != "none" or deny.lower() != "none":
                    problems.append(f"{seat} dialog=absent requires dialog-tools=none and dialog-deny=none")
            elif tool_names.lower() == "none" or deny.lower() == "none":
                problems.append(f"{seat} dialog=denied requires tool names and a deny pattern")
            else:
                names = tool_names.split(",")
                patterns = deny.split(",")
                for name in names:
                    if not name or not any(
                        re.fullmatch(re.escape(pattern).replace(r"\*", ".*"), name)
                        for pattern in patterns
                    ):
                        problems.append(f"{seat} dialog-deny does not cover {name or 'empty tool name'}")
        if (
            disposition == seat.lower()
            and seat in {"REVIEWER", "ARCHITECT"}
            and re.search(r"(?:^|\s)fence=sandbox-exec(?:\s|\()", line, re.IGNORECASE)
            and _charter_allows_docker(charter)
            and re.search(r"\bresidual\s+docker-daemon\s+writes\b", line, re.IGNORECASE) is None
        ):
            problems.append(f"{seat} fenced seat missing residual docker-daemon writes")
        if disposition == seat.lower() and PLACEHOLDER_RE.search(line):
            problems.append(f"{seat} seat still contains a placeholder token")

        if seat in {"REVIEWER", "ARCHITECT"}:
            fence_match = re.search(
                r"(?:^|\s)fence=(sandbox-exec|none)",
                line,
                re.IGNORECASE,
            )
            if fence_match is None:
                problems.append(f"{seat} seat missing fence=")
                continue
            fence = fence_match.group(1)
            evidence = None
            fence_open = fence_match.end()
            if fence_open < len(line) and line[fence_open] == "(":
                depth = 0
                first_close = None
                for index in range(fence_open, len(line)):
                    if line[index] == "(":
                        depth += 1
                    elif line[index] == ")":
                        depth -= 1
                        if first_close is None:
                            first_close = index
                        if depth == 0:
                            evidence = line[fence_open + 1:index]
                            break
                else:
                    if first_close is not None:
                        evidence = line[fence_open + 1:first_close]
            if fence.lower() == "none":
                if evidence is None or not evidence.strip():
                    problems.append(f"{seat} fence=none requires a reason in parentheses")
                    continue
                needs_fence = (
                    fields.get("kind", "").lower() == "pi"
                    or fields.get("posture", "").lower() in {"bypassed", "none"}
                )
                if needs_fence and _sandbox_exec_available():
                    problems.append(
                        f"{seat} fence=none is not allowed for a seat requiring a fence "
                        "when sandbox-exec is available"
                    )
                continue

            profile_text, separator, probe_text = (evidence or "").partition(";")
            probe_match = re.search(r"\bprobe\s+(.+?)\s*->\s*(.+)", probe_text, re.IGNORECASE)
            profile_name = profile_text.strip()
            profile_path = Path(profile_name)
            if not profile_path.is_absolute():
                profile_path = staffing_path.parent / profile_path
            if (
                not separator
                or not profile_name.endswith(".sb")
                or probe_match is None
                or "Operation not permitted" not in probe_match.group(2)
                or not profile_path.is_file()
            ):
                problems.append(
                    f"{seat} fence=sandbox-exec must record an existing .sb file and a probe "
                    "result containing 'Operation not permitted'"
                )
    return problems


def _git(repo: Path, args: list[str], stdin: str = "") -> subprocess.CompletedProcess[str]:
    try:
        return subprocess.run(
            ["git", "-C", str(repo), *args], input=stdin, capture_output=True, text=True,
            encoding="utf-8",
        )
    except OSError as exc:
        raise ValueError(f"could not run git: {exc}") from exc


def _missing_objects(repo: Path, shas: list[str]) -> set[str]:
    proc = _git(repo, ["cat-file", "--batch-check"], "".join(f"{sha}\n" for sha in shas))
    if proc.returncode != 0:
        raise ValueError(f"could not read repo {repo}: {proc.stderr.strip()}")
    return {line.split()[0] for line in proc.stdout.splitlines() if line.endswith(" missing")}


def _sha_problems(repo: Path, texts: dict[str, str]) -> list[str]:
    found: dict[str, str] = {}
    critical: set[str] = set()
    for label, text in texts.items():
        for sha in HEAD_RE.findall(text):
            found.setdefault(sha.lower(), label)
        critical.update(sha.lower() for pair in RANGE_RE.findall(text) for sha in pair)
        critical.update(sha.lower() for sha in STAFFED_HEAD_RE.findall(text))
    missing = _missing_objects(repo, list(found))
    missing.discard(NULL_OID)
    anchors = {sha[:SPLICE_PREFIX] for sha in critical - missing if sha != NULL_OID}
    return [
        f"unresolved SHA {sha} in {label}: not an object in {repo}"
        for sha, label in found.items()
        if sha in missing and (sha in critical or sha[:SPLICE_PREFIX] in anchors)
    ]


def _repair_range_problems(repo: Path, charter: str) -> list[str]:
    prior = PRIOR_RE.search(charter)
    line = PRIOR_GLOSS_RE.sub("", prior.group(1)) if prior else ""
    if not re.search(r"\bFAIL", line):
        return []
    unit = UNIT_RANGE_RE.search(charter)
    if unit is None:
        return ["repair re-review has no Reviewed unit range"]
    base, head = unit.groups()
    names = "".join(f"{sha}^{{commit}}\n" for sha in SHORT_SHA_RE.findall(line))
    named = {out.split()[0] for out in _git(repo, ["cat-file", "--batch-check"], names).stdout.splitlines()
             if out.split()[1:2] == ["commit"]}
    if not named:
        return ["repair re-review Prior review names a FAIL but no commit in --repo"]
    listed = _git(repo, ["rev-list", f"{base}..{head}"])
    if listed.returncode != 0:
        return [f"repair re-review range {base}..{head} does not resolve in {repo}"]
    below_head = set(listed.stdout.split()[1:])  # rev-list lists the head first; naming it proves nothing
    if not named.isdisjoint(below_head):
        return []
    for commit in named:
        divergence = _git(repo, ["merge-base", commit, head])
        if divergence.returncode != 0:
            continue
        merge_base = divergence.stdout.strip()
        if merge_base in {commit, head}:
            continue
        kept = _git(repo, ["merge-base", "--is-ancestor", base, merge_base])
        if kept.returncode == 0:
            return []
    return [
        f"repair re-review range {base}..{head} must keep the slice base: "
        "no commit named on the Prior review line lies inside it below its head, or was rewritten with the range starting at or below where the head diverged from it"
    ]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Lint the charter and optional staffing record supplied for dispatch."
    )
    parser.add_argument("--charter", required=True, type=Path, help="path to the charter")
    parser.add_argument("--lead", required=True, help="Lead seat name or handle used by the report block")
    parser.add_argument("--staffing", type=Path, help="optional staffing record")
    parser.add_argument(
        "--repo", required=True, type=Path, help="checkout whose objects the SHAs must name"
    )
    backend.add_backend_option(parser)
    args = parser.parse_args(argv)

    try:
        seats = backend.open_backend(os.environ, args.backend)
        charter, charter_bytes = _read(args.charter, "charter")
        problems = _charter_problems(charter, args.lead, seats)
        disposition = _disposition(charter)
        if disposition in ("engineer", "reviewer", "architect") and args.staffing is None:
            problems.append(
                "staffing record is required for an Engineer/Reviewer/Architect disposition"
            )
        texts = {"charter": charter}
        digests = {"charter": hashlib.sha256(charter_bytes).hexdigest()}
        if args.staffing is not None:
            staffing, staffing_bytes = _read(args.staffing, "staffing record")
            texts["staffing record"] = staffing
            digests["staffing record"] = hashlib.sha256(staffing_bytes).hexdigest()
            problems.extend(_staffing_problems(staffing, disposition, args.staffing, charter))
        problems.extend(_sha_problems(args.repo, texts))
        problems.extend(_repair_range_problems(args.repo, charter))
    except (ValueError, backend.BackendError) as exc:
        print(f"charter_lint: {exc}", file=sys.stderr)
        return 1

    if problems:
        for problem in problems:
            print(f"charter_lint: {problem}", file=sys.stderr)
        return 1

    digest_text = "; ".join(f"{label} sha256={digest}" for label, digest in digests.items())
    print(f"OK: {digest_text}; dispatch requirements linted")
    return 0


if __name__ == "__main__":
    sys.exit(main())
