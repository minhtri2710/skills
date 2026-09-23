#!/usr/bin/env python3
"""Refuse a push unless every pushed ref is covered by review PASS ranges and by recorded Human authority.

`--digest LEDGER REPO` (repeatable) instead prints, read-only, every project's open
push gates as one range with its review coverage and push authority, then one question.
"""
from __future__ import annotations

import argparse
import shlex
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


def digest_project(ledger: Path, repo: Path, remote: str, now: datetime) -> tuple[list[str], str | None]:
    """One project's digest lines and, when its range is fully reviewed, its question item."""
    with gate_row.locked_ledger(ledger, exclusive=False) as handle:
        rows = gate_row.ledger_rows(gate_row.handle_text(handle))
    open_ids = set(gate_row.open_gate_ids(rows))
    gates = [row for row in rows if row.split(" | ")[0] in open_ids
             and gate_row.row_evidence(row)[0] == "push-gate"]
    if not gates:
        return [], None
    heads = [gate_row.split_row(row)[0][3].split("@") for row in gates]
    branches = {branch for branch, _ in heads}
    if len(branches) != 1:
        raise gate_row.RowError(f"open push gates name more than one branch: {', '.join(sorted(branches))}")
    branch = branches.pop()
    tip = git(repo, "rev-parse", "--verify", f"{heads[-1][1]}^{{commit}}")
    try:
        base = git(repo, "rev-parse", "--verify", f"refs/remotes/{remote}/{branch}^{{commit}}")
    except GuardError:
        raise GuardError(f"no remote-tracking ref refs/remotes/{remote}/{branch}: a first publication "
                         "or an unfetched branch, and the digest uses no network") from None
    ref = f"refs/heads/{branch}"
    lines = [
        f"gates: {' '.join(row.split(' | ')[0] for row in gates)}",
        f"branch: {branch}",
    ]
    try:
        commits = gate_row.range_commits(repo, base, tip)
        gate_row.require_review_coverage(rows, repo, base, tip)
    except gate_row.RowError as exc:
        return [*lines, f"range: {base}..{tip}", f"NOT READY: {exc}"], None
    reviews = []
    for row in rows:
        kind, _, status = gate_row.row_evidence(row)
        rng = gate_row.review_range(row) if kind == "review" and status == "recorded:review-pass" else None
        if rng and rng[1] in commits:
            reviews.append(row.split(" | ")[0])
    lines += [
        f"range: {base}..{tip} ({len(commits)} commits)",
        f"review rows: {' '.join(reviews)}; coverage ok",
    ]
    try:
        lines.append(f"authority: granted by {gate_row.require_push_authority(rows, repo, remote, ref, base, tip, now)}")
    except gate_row.RowError as exc:
        command = shlex.join([
            "python3", str(Path(gate_row.__file__).resolve()),
            "--ledger", str(ledger), "--repo", str(repo),
            "--kind", "push-grant", "--status", "open",
            "--writer", "supervisor", "--channel", "supervisor-relay:typed",
            "--grant", f"{remote} {ref} push {base}..{tip}", "--words", "human",
            "--note", f"Human grants push of {branch} {base[:7]}..{tip[:7]}",
            "--quote", "<HUMAN-WORDS>",
        ])
        lines += [f"authority: needs push-grant: {exc}", f"grant: {command}"]
    return lines, f"{ledger.parent.name} {branch} {base[:7]}..{tip[:7]} ({len(commits)} commits)"


def digest(pairs: list[list[str]], remote: str) -> int:
    now = datetime.now(timezone.utc)
    ready: list[str] = []
    errors = 0
    for ledger_text, repo_text in pairs:
        ledger, repo = Path(ledger_text), Path(repo_text)
        try:
            lines, item = digest_project(ledger, repo, remote, now)
        except (OSError, UnicodeError, gate_row.RowError, GuardError) as exc:
            errors += 1
            lines, item = [f"ERROR: {exc}"], None
        if not lines:
            continue
        print(f"== {ledger.parent.name} (ledger {ledger}, repo {repo})")
        print("\n".join(f"  {line}" for line in lines))
        if item:
            ready.append(item)
    if ready:
        print("Question: approve which pushes? Answer all, none, or the numbers.")
        print("\n".join(f"  {n}. {item}" for n, item in enumerate(ready, 1)))
    else:
        print("Question: none — no push is ready.")
    return 1 if errors else 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--digest", nargs=2, action="append", metavar=("LEDGER", "REPO"),
                        help="print the open push gates of this project; repeatable; read-only")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    # git runs the hook as `<hook> <remote> <url>`; manual runs pass neither.
    parser.add_argument("remote", nargs="?", default="origin")
    parser.add_argument("url", nargs="?")
    args = parser.parse_args(argv)
    if args.digest:
        if args.ledger or args.url:
            parser.error("--digest takes no --ledger or url")
        return digest(args.digest, args.remote)
    if not args.ledger:
        parser.error("--ledger is required")
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
