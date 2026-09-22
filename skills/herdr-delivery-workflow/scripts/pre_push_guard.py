#!/usr/bin/env python3
"""Refuse a push until every commit in the pushed range is covered by a review PASS range."""
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


ZERO = "0" * 40


def first_publication_pair(repo: Path, ref: str, local_sha: str) -> tuple[str, str]:
    """Return a zero-based range only when origin has no refs at all."""
    if not git(repo, "ls-remote", "origin").splitlines():
        return ZERO, local_sha
    raise GuardError(
        f"ref {ref} has no remote base — the review-coverage range is undefined, "
        "and this guard does not admit the first push of a ref"
    )


def push_refs(repo: Path) -> list[tuple[str, str]] | None:
    """Return (remote base, local tip) pairs from the pre-push stdin, or None when empty.

    The base is fields[3], the remote SHA git is about to move — the range the push
    publishes is base..tip, so the guard checks the whole stack, not only the tip.
    """
    text = sys.stdin.read()
    if not text.strip():
        return None

    pairs: list[tuple[str, str]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        fields = line.split()
        if len(fields) != 4:
            raise GuardError(f"malformed pre-push ref line: {line}")
        local_sha, remote_sha = fields[1], fields[3]
        if local_sha == ZERO:
            continue  # a deletion pushes no commit
        if remote_sha == ZERO:
            pairs.append(first_publication_pair(repo, fields[0], local_sha))
        else:
            pairs.append((remote_sha, local_sha))
    return pairs


def check(ledger: Path, repo: Path, pairs: list[tuple[str, str]] | None = None) -> list[str]:
    if pairs is None:
        branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
        head = git(repo, "rev-parse", "HEAD")
        remote = git(repo, "ls-remote", "origin", f"refs/heads/{branch}").split()
        if not remote:
            pairs = [first_publication_pair(repo, f"origin/{branch}", head)]
        else:
            pairs = [(remote[0], head)]
    try:
        with gate_row.locked_ledger(ledger, exclusive=False) as handle:
            rows = gate_row.ledger_rows(gate_row.handle_text(handle))
    except OSError as exc:
        raise GuardError(f"cannot read ledger {ledger}: {exc}") from None
    except gate_row.RowError as exc:
        raise GuardError(str(exc)) from None

    for base, tip in pairs:
        try:
            gate_row.require_review_coverage(rows, repo, base, tip)
        except gate_row.RowError as exc:
            raise GuardError(str(exc)) from None
    return [tip for _, tip in pairs]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    args = parser.parse_args(argv)
    try:
        pairs = push_refs(args.repo)
        checked = check(args.ledger, args.repo, pairs)
    except GuardError as exc:
        print(f"pre_push_guard: {exc}", file=sys.stderr)
        return 1
    print(f"pre_push_guard: {len(checked)} pushed range(s) fully covered by review PASS rows")
    return 0


if __name__ == "__main__":
    sys.exit(main())
