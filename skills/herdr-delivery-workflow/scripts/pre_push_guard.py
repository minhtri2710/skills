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


def push_shas() -> list[str] | None:
    """Return pushed local SHAs, or None when stdin is empty."""
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

    try:
        gate_row.require_review_pass(rows, targets)
    except gate_row.RowError as exc:
        raise GuardError(str(exc)) from None
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
