#!/usr/bin/env python3
"""Flag diff moves that lower a repository's quality bar.

Compares the working tree (staged, unstaged, and untracked files) against the
merge base with ``--base``. Reports rule and location only, never line text, so
a secret on a flagged line never reaches the transcript. A complete exception
row in CONSTRAINTS.md (id, rule or ``*``, path glob, reason, removal condition)
suppresses matching findings; an incomplete row is itself a finding.

Exit codes: 0 clean, 1 at least one violation, 2 the guard could not run.
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from collections import Counter
from fnmatch import fnmatch
from dataclasses import dataclass
from pathlib import Path

SUPPRESSION = re.compile(
    r"@ts-ignore|@ts-nocheck|@ts-expect-error|eslint-disable|biome-ignore|"
    r"#\s*noqa|#\s*type:\s*ignore|#\s*pyright:\s*ignore|#\s*pragma:\s*no cover|"
    r"//\s*nolint|#\[allow\(|@SuppressWarnings|istanbul ignore|c8 ignore|"
    r"nosemgrep|gitleaks:allow|Stryker disable"
)
STUB = re.compile(
    r"raise NotImplementedError|throw new Error\(.*not implemented|"
    r"\btodo!\(|\bunimplemented!\(|panic\(\"not implemented|"
    r"catch\s*(\([^)]*\))?\s*\{\s*\}|except\b[^:]*:\s*pass\b",
    re.IGNORECASE,
)
# Only a TODO/FIXME inside a comment marker counts; the words are ordinary vocabulary elsewhere.
TODO_MARK = re.compile(r"(?:#|//|/\*|<!--|\*|--|;)\s*(?:TODO|FIXME)\b")
SKIP = re.compile(
    r"\b(it|test|describe|context)\.(skip|todo|only)\(|\bxit\(|\bxdescribe\(|@pytest\.mark\.(skip|xfail)|"
    r"@unittest\.skip|\bt\.Skip\(|#\[ignore\]"
)
ASSERTION = re.compile(r"\b(expect|assert\w*|should)\b")
TEST_PATH = re.compile(r"(^|/)(tests?|__tests__|spec)/|(^|/)test_[^/]*$|_test\.|\.(test|spec)\.")
HUNK = re.compile(r"^@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@")
CONSTRAINTS = "CONSTRAINTS.md"


@dataclass(frozen=True)
class Line:
    path: str
    number: int
    text: str


@dataclass(frozen=True)
class Finding:
    rule: str
    path: str
    number: int

    def render(self) -> str:
        return f"[{self.rule}] {self.path}:{self.number}"


class GuardError(Exception):
    pass


def _git(repo: Path, *args: str) -> str:
    try:
        result = subprocess.run(["git", *args], cwd=repo, capture_output=True, text=True)
    except OSError as exc:
        raise GuardError(f"git unavailable: {exc}") from exc
    if result.returncode != 0:
        raise GuardError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout


def parse_diff(diff: str) -> tuple[list[Line], list[Line]]:
    """Split a ``--unified=0`` diff into added and removed lines."""
    added: list[Line] = []
    removed: list[Line] = []
    old_path = new_path = ""
    new_number = old_number = 0
    in_header = False
    for raw in diff.splitlines():
        if raw.startswith("diff --git "):
            in_header = True
        elif in_header and raw.startswith("--- "):
            old_path = raw[6:] if raw.startswith("--- a/") else ""
        elif in_header and raw.startswith("+++ "):
            new_path = raw[6:] if raw.startswith("+++ b/") else ""
        elif raw.startswith("@@"):
            in_header = False
            match = HUNK.match(raw)
            if match:
                new_number = int(match.group(1))
                old_number = int(raw.split()[1].lstrip("-").split(",")[0])
        elif in_header:
            continue
        elif raw.startswith("+"):
            added.append(Line(new_path, new_number, raw[1:]))
            new_number += 1
        elif raw.startswith("-"):
            removed.append(Line(new_path or old_path, old_number, raw[1:]))
            old_number += 1
    return added, removed


def _row_key(text: str) -> str | None:
    cells = [c.strip() for c in text.strip().strip("|").split("|")]
    if not text.lstrip().startswith("|") or not cells or not cells[0] or set(cells[0]) <= set("-: "):
        return None
    return cells[0]


def _bound(text: str) -> tuple[str, float] | None:
    match = re.search(r"(>=|<=|≥|≤)\s*(\d+(?:\.\d+)?)", text)
    if not match:
        return None
    op = ">=" if match.group(1) in (">=", "≥") else "<="
    return op, float(match.group(2))


def check_constraints(added: list[Line], removed: list[Line]) -> list[Finding]:
    findings: list[Finding] = []
    new = [line for line in added if Path(line.path).name == CONSTRAINTS]
    old = [line for line in removed if Path(line.path).name == CONSTRAINTS]
    new_rows = {_row_key(line.text): line for line in new if _row_key(line.text)}
    new_bullets = {line.text.strip() for line in new}
    for line in old:
        key = _row_key(line.text)
        if key is None:
            if line.text.lstrip().startswith("- ") and line.text.strip() not in new_bullets:
                findings.append(Finding("floor-rule-removed", line.path, line.number))
            continue
        replacement = new_rows.get(key)
        if replacement is None:
            if not re.fullmatch(r"E\d+", key):
                findings.append(Finding("constraint-removed", line.path, line.number))
            continue
        before, after = _bound(line.text), _bound(replacement.text)
        if before and (
            after is None
            or after[0] != before[0]
            or (before[0] == ">=" and after[1] < before[1])
            or (before[0] == "<=" and after[1] > before[1])
        ):
            findings.append(Finding("threshold-loosened", replacement.path, replacement.number))
    return findings


@dataclass(frozen=True)
class Exception_:
    rule: str
    path_glob: str


def parse_exceptions(text: str) -> tuple[list[Exception_], list[int]]:
    """Read ``| E<n> | rule | path | reason | removal condition |`` rows.

    Returns the usable exceptions and the line numbers of rows missing a reason
    or a removal condition; those rows suppress nothing.
    """
    usable: list[Exception_] = []
    incomplete: list[int] = []
    for number, raw in enumerate(text.splitlines(), start=1):
        key = _row_key(raw)
        if key is None or not re.fullmatch(r"E\d+", key):
            continue
        cells = [c.strip() for c in raw.strip().strip("|").split("|")]
        if len(cells) < 5 or not cells[3] or not cells[4]:
            incomplete.append(number)
            continue
        usable.append(Exception_(cells[1], cells[2]))
    return usable, incomplete


def _excepted(finding: Finding, exceptions: list[Exception_]) -> bool:
    return any(
        (e.rule in ("*", finding.rule)) and fnmatch(finding.path, e.path_glob)
        for e in exceptions
    )


def check(
    added: list[Line], removed: list[Line], deleted: list[str], constraints: str = ""
) -> list[Finding]:
    exceptions, incomplete = parse_exceptions(constraints)
    findings: list[Finding] = []
    for line in added:
        if Path(line.path).name == CONSTRAINTS:
            continue
        if SUPPRESSION.search(line.text):
            findings.append(Finding("silenced-checker", line.path, line.number))
        if STUB.search(line.text) or TODO_MARK.search(line.text):
            findings.append(Finding("unfinished-work", line.path, line.number))
        if SKIP.search(line.text):
            findings.append(Finding("test-made-easier", line.path, line.number))

    for path in deleted:
        if TEST_PATH.search(path):
            findings.append(Finding("test-deleted", path, 0))

    lost = Counter(l.path for l in removed if TEST_PATH.search(l.path) and ASSERTION.search(l.text))
    gained = Counter(l.path for l in added if TEST_PATH.search(l.path) and ASSERTION.search(l.text))
    for path, count in sorted(lost.items()):
        if path not in deleted and count > gained[path]:
            first = next(l for l in removed if l.path == path and ASSERTION.search(l.text))
            findings.append(Finding("assertion-removed", path, first.number))

    findings = [f for f in findings if not _excepted(f, exceptions)]
    findings += [Finding("exception-incomplete", CONSTRAINTS, n) for n in incomplete]
    return findings + check_constraints(added, removed)


def collect(repo: Path, base: str) -> tuple[list[Line], list[Line], list[str], str]:
    merge_base = _git(repo, "merge-base", base, "HEAD").strip()
    added, removed = parse_diff(_git(repo, "diff", "--no-color", "--unified=0", merge_base, "--"))
    deleted = [p for p in _git(repo, "diff", "--name-only", "-z", "--diff-filter=D", merge_base, "--").split("\0") if p]
    for name in _git(repo, "ls-files", "--others", "--exclude-standard", "-z").split("\0"):
        if not name:
            continue
        try:
            text = (repo / name).read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        added.extend(Line(name, i, t) for i, t in enumerate(text.splitlines(), start=1))
    try:
        constraints = (repo / CONSTRAINTS).read_text(encoding="utf-8")
    except OSError:
        constraints = ""
    return added, removed, deleted, constraints


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base", default="origin/main", help="ref whose merge base is compared (default: origin/main)")
    parser.add_argument("--repo", type=Path, default=Path.cwd(), help="repository root (default: cwd)")
    args = parser.parse_args(argv)
    try:
        findings = check(*collect(args.repo, args.base))
    except GuardError as exc:
        print(f"floor-guard: cannot run: {exc}", file=sys.stderr)
        return 2
    if not findings:
        print("floor-guard: clean")
        return 0
    print(f"floor-guard: {len(findings)} violation(s)", file=sys.stderr)
    for finding in findings:
        print(f"  {finding.render()}", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main())
