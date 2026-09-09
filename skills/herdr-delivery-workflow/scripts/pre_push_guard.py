#!/usr/bin/env python3
"""Refuse a push until a review row names the current HEAD."""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

import gate_row


class GuardError(Exception):
    """The ledger cannot prove that this HEAD is eligible for push."""


def git(repo: Path, *args: str) -> str:
    proc = subprocess.run(
        ["git", "-C", str(repo), *args],
        capture_output=True,
        text=True,
        check=False,
    )
    if proc.returncode:
        raise GuardError(f"git {' '.join(args)} failed: {proc.stderr.strip()}")
    return proc.stdout.strip()


def row_evidence(row: str) -> tuple[str, str, str]:
    fields, _ = gate_row.split_row(row)
    if len(fields) < 5:
        raise GuardError(f"malformed ledger row: {row}")
    kind = fields[2]
    head = fields[3]
    status = fields[4]
    if not kind.startswith("kind="):
        raise GuardError(f"ledger row has no kind=: {row}")
    if not gate_row.HEAD_RE.fullmatch(head):
        raise GuardError(f"ledger row has no valid branch@sha: {row}")
    if not status.startswith("status="):
        raise GuardError(f"ledger row has no status=: {row}")
    return kind.split("=", 1)[1], head.split("@", 1)[1], status.split("=", 1)[1]


def check(ledger: Path, repo: Path) -> None:
    head = git(repo, "rev-parse", "HEAD")
    try:
        rows = gate_row.ledger_rows(ledger.read_text(encoding="utf-8"))
    except OSError as exc:
        raise GuardError(f"cannot read ledger {ledger}: {exc}") from None

    review = False
    for row in rows:
        kind, row_head, status = row_evidence(row)
        if row_head != head:
            continue
        if kind == "review" and (
            status.startswith("recorded:review") or status.startswith("resolved")
        ):
            review = True
    missing = []
    if not review:
        missing.append("review PASS row")
    if missing:
        raise GuardError(f"refusing push for HEAD {head}: missing {', '.join(missing)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        check(args.ledger, args.repo)
    except GuardError as exc:
        print(f"pre_push_guard: {exc}", file=sys.stderr)
        return 1
    print(f"pre_push_guard: HEAD {git(args.repo, 'rev-parse', 'HEAD')} has a passing review row")
    return 0


if __name__ == "__main__":
    sys.exit(main())
