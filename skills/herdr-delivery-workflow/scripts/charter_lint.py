#!/usr/bin/env python3
"""Check the dispatch-critical fields in a Herdr charter and staffing record."""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

DISPOSITION_RE = re.compile(
    r"^\s*[*#`_-]*\s*Disposition:\s*[*_`]*\s*(Engineer|Reviewer|Architect)\b",
    re.IGNORECASE | re.MULTILINE,
)
HEAD_RE = re.compile(r"(?<![0-9a-f])[0-9a-f]{40}(?![0-9a-f])", re.IGNORECASE)
REPORT_PATH_RE = re.compile(r"report-[^\s/]+\.md")
SEAT_RE = re.compile(r"^\s*(ENGINEER|REVIEWER):.*$", re.IGNORECASE | re.MULTILINE)


def _read(path: Path, label: str) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise ValueError(f"could not read {label} {path}: {exc}") from exc


def _charter_problems(text: str, lead: str) -> list[str]:
    problems: list[str] = []
    disposition_match = DISPOSITION_RE.search(text)
    if disposition_match is None:
        problems.append("missing Disposition: Engineer / Reviewer / Architect line")
        disposition = None
    else:
        disposition = disposition_match.group(1).lower()

    if disposition == "engineer" and not re.search(r"owned paths", text, re.IGNORECASE):
        problems.append("missing owned paths section")
    if disposition == "reviewer" and HEAD_RE.search(text) is None:
        problems.append("missing exact-head 40-hex SHA")

    if f"herdr agent prompt {lead}" not in text:
        problems.append(f"missing report-by-prompt block: herdr agent prompt {lead}")
    if REPORT_PATH_RE.search(text) is None:
        problems.append("missing report-by-prompt block: report-*.md path")
    return problems


def _staffing_problems(text: str) -> list[str]:
    seats = SEAT_RE.findall(text)
    if not seats:
        return ["staffing record has no ENGINEER or REVIEWER seat lines"]

    problems: list[str] = []
    for line in text.splitlines():
        match = re.match(r"^\s*(ENGINEER|REVIEWER):", line, re.IGNORECASE)
        if match is None:
            continue
        seat = match.group(1).upper()
        for key in ("posture=", "dialog=", "skills=", "extensions="):
            if key not in line:
                problems.append(f"{seat} seat missing {key}")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Lint a Herdr charter before dispatch.")
    parser.add_argument("--charter", required=True, type=Path, help="path to the charter")
    parser.add_argument("--lead", required=True, help="Lead agent name used by the report block")
    parser.add_argument("--staffing", type=Path, help="optional staffing record")
    args = parser.parse_args(argv)

    try:
        problems = _charter_problems(_read(args.charter, "charter"), args.lead)
        if args.staffing is not None:
            problems.extend(_staffing_problems(_read(args.staffing, "staffing record")))
    except ValueError as exc:
        print(f"charter_lint: {exc}", file=sys.stderr)
        return 1

    if problems:
        for problem in problems:
            print(f"charter_lint: {problem}", file=sys.stderr)
        return 1

    print("OK: charter and staffing record contain dispatch requirements")
    return 0


if __name__ == "__main__":
    sys.exit(main())
