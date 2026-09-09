#!/usr/bin/env python3
"""Refuse a push until each pushed SHA has a passing review row."""
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


def push_shas() -> list[str] | None:
    """Return pushed local SHAs, or None when invoked manually."""
    if sys.stdin.isatty():
        return None
    text = sys.stdin.read()
    if not text.strip():
        return None

    shas = []
    for line in text.splitlines():
        if not line.strip():
            continue
        fields = line.split()
        if len(fields) != 4:
            raise GuardError(f"malformed pre-push ref line: {line}")
        local_sha = fields[1]
        if local_sha != "0" * 40:
            shas.append(local_sha)
    return shas


def check(ledger: Path, repo: Path, targets: list[str] | None = None) -> list[str]:
    if targets is None:
        targets = [git(repo, "rev-parse", "HEAD")]
    try:
        rows = gate_row.ledger_rows(ledger.read_text(encoding="utf-8"))
    except OSError as exc:
        raise GuardError(f"cannot read ledger {ledger}: {exc}") from None

    reviewed = set()
    for row in rows:
        kind, row_head, status = row_evidence(row)
        if kind == "review" and status == "recorded:review-pass":
            reviewed.add(row_head)
    missing = [sha for sha in targets if sha not in reviewed]
    if missing:
        raise GuardError(
            f"refusing push for {', '.join(missing)}: missing review PASS row"
        )
    return targets


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        targets = push_shas()
        checked = check(args.ledger, args.repo, targets)
    except GuardError as exc:
        print(f"pre_push_guard: {exc}", file=sys.stderr)
        return 1
    if targets is None:
        print(f"pre_push_guard: HEAD {checked[0]} has a passing review row")
    else:
        print(f"pre_push_guard: {len(checked)} pushed SHA(s) have passing review rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
