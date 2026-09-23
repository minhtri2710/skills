#!/usr/bin/env python3
"""Refuse a push unless every pushed ref is covered by review PASS ranges and by recorded Human authority."""
from __future__ import annotations

import argparse
import subprocess
import sys
from datetime import datetime, timezone
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


def require_first_publication(repo: Path, remote: str, ref: str) -> None:
    """Admit a zero-based range only when the remote has no refs at all."""
    if not git(repo, "ls-remote", remote).splitlines():
        return
    raise GuardError(
        f"ref {ref} has no remote base — the review-coverage range is undefined, "
        "and this guard does not admit the first push of a ref"
    )


def push_refs() -> list[tuple[str, str, str]] | None:
    """Return (remote ref, remote base, local tip) from the pre-push stdin, or None when empty.

    The base is fields[3], the remote SHA git is about to move — the range the push
    publishes is base..tip, so the guard checks the whole stack, not only the tip.
    A deletion carries a zero tip and publishes no commit, but still needs authority.
    """
    text = sys.stdin.read()
    if not text.strip():
        return None

    pairs: list[tuple[str, str, str]] = []
    for line in text.splitlines():
        if not line.strip():
            continue
        fields = line.split()
        if len(fields) != 4:
            raise GuardError(f"malformed pre-push ref line: {line}")
        pairs.append((fields[2], fields[3], fields[1]))
    return pairs


def check(
    ledger: Path, repo: Path, remote: str,
    pairs: list[tuple[str, str, str]] | None = None,
) -> list[str]:
    if pairs is None:
        branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
        head = git(repo, "rev-parse", "HEAD")
        ref = f"refs/heads/{branch}"
        remote_tip = git(repo, "ls-remote", remote, ref).split()
        pairs = [(ref, remote_tip[0] if remote_tip else ZERO, head)]
    try:
        with gate_row.locked_ledger(ledger, exclusive=False) as handle:
            rows = gate_row.ledger_rows(gate_row.handle_text(handle))
    except OSError as exc:
        raise GuardError(f"cannot read ledger {ledger}: {exc}") from None
    except gate_row.RowError as exc:
        raise GuardError(str(exc)) from None

    now = datetime.now(timezone.utc)
    for ref, base, tip in pairs:
        try:
            gate_row.require_push_authority(rows, repo, remote, ref, base, tip, now)
            if tip == ZERO:
                continue
            if base == ZERO:
                require_first_publication(repo, remote, ref)
            elif not gate_row.is_ancestor(repo, base, tip):
                base = git(repo, "merge-base", base, tip)  # a force push publishes merge-base..tip
                if base == tip:
                    continue  # a rewind publishes no commit
            gate_row.require_review_coverage(rows, repo, base, tip)
        except gate_row.RowError as exc:
            raise GuardError(str(exc)) from None
    return [tip for _, _, tip in pairs]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", required=True, type=Path)
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    # git runs the hook as `<hook> <remote> <url>`; manual runs pass neither.
    parser.add_argument("remote", nargs="?", default="origin")
    parser.add_argument("url", nargs="?")
    args = parser.parse_args(argv)
    try:
        pairs = push_refs()
        checked = check(args.ledger, args.repo, args.remote, pairs)
    except GuardError as exc:
        print(f"pre_push_guard: {exc}", file=sys.stderr)
        return 1
    print(f"pre_push_guard: {len(checked)} pushed ref(s) covered by review PASS rows and a Human grant")
    return 0


if __name__ == "__main__":
    sys.exit(main())
