#!/usr/bin/env python3
"""Refuse a push unless every pushed ref is covered by review PASS ranges and by recorded Human authority.

`--digest LEDGER REPO` (repeatable) instead prints, read-only, every project's open
push gates as one range per branch with its review coverage and push authority, flags a
checkout with unpushed commits no open push gate covers as UNGATED, then asks one question
with one numbered item per ready branch and an `items:` hash of those items.

`--digest ... --grant <all|N[,N...]> --items <hash> --quote "<Human words>"` is the
Supervisor's recording tool for a Human's answer: it recomputes the digest, refuses unless
the items hash still matches, and writes one open push-grant row per selected item through
gate_row in-process. It authorizes nothing by itself.
"""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import NamedTuple

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


def remote_refs(repo: Path, remote: str) -> dict[str, str]:
    """Every ref the remote holds, by name, from one ls-remote; never local tracking refs."""
    return {ref: sha for sha, ref in (line.split("\t") for line in git(repo, "ls-remote", remote).splitlines())}


def require_first_publication(ref: str, held: dict[str, str]) -> None:
    """Admit a zero-based tag range only when the remote has no refs at all."""
    if not held:
        return
    raise GuardError(
        f"ref {ref} has no remote base — the review-coverage range is undefined, "
        "and this guard admits a tag only as the first publication to an empty remote"
    )


def remote_held_tips(repo: Path, remote: str, held: dict[str, str]) -> list[str]:
    """The remote's ref tips as local objects, refusing any tip this repository lacks."""
    tips = sorted(set(held.values()))
    for sha in tips:
        try:
            git(repo, "cat-file", "-e", sha)
        except GuardError:
            names = ", ".join(sorted(ref for ref, value in held.items() if value == sha))
            raise GuardError(f"{remote} holds {sha} ({names}), which is not a local object: "
                             "the published set is undefined until it is fetched") from None
    return tips


def new_branch_base(repo: Path, tip: str, exclude: list[str], source: str) -> str:
    """The single base of a new branch's published set, or refuse naming why.

    The published set is `rev-list <tip> --not <exclude>`: the guard passes the tips
    the remote holds, the digest its local tracking-ref estimate. It is publishable
    as base..tip when it holds no root commit and every parent outside the set is
    one commit, the base; base..tip is then exactly the set.
    """
    published = git(repo, "rev-list", "--parents", tip, "--not", *exclude).splitlines()
    if not published:
        raise GuardError(f"new branch at {tip} publishes no commit outside {source}")
    shas = {line.split()[0] for line in published}
    boundary = {p for line in published for p in line.split()[1:] if p not in shas}
    roots = [line.split()[0] for line in published if len(line.split()) == 1]
    if roots:
        raise GuardError(f"new branch at {tip} publishes root commit {roots[0]}, which only "
                         "a first publication to an empty remote may")
    if len(boundary) != 1:
        raise GuardError(f"new branch at {tip} leaves {source} at {len(boundary)} "
                         f"boundary commits ({', '.join(sorted(boundary))}), not one base")
    return boundary.pop()


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
    held: dict[str, str] | None = None
    if pairs is None:
        branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
        head = git(repo, "rev-parse", "HEAD")
        ref = f"refs/heads/{branch}"
        held = remote_refs(repo, remote)
        pairs = [(ref, held.get(ref, ZERO), head)]
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
            if base == ZERO and tip != ZERO:
                if held is None:
                    held = remote_refs(repo, remote)
                if held and ref.startswith("refs/heads/"):
                    base = new_branch_base(repo, tip, remote_held_tips(repo, remote, held),
                                           f"the tips {remote} holds")
            gate_row.require_push_authority(rows, repo, remote, ref, base, tip, now)
            if tip == ZERO:
                continue
            if base == ZERO:
                require_first_publication(ref, held)
            elif not gate_row.is_ancestor(repo, base, tip):
                base = git(repo, "merge-base", base, tip)  # a force push publishes merge-base..tip
                if base == tip:
                    continue  # a rewind publishes no commit
            gate_row.require_review_coverage(rows, repo, base, tip)
        except gate_row.RowError as exc:
            raise GuardError(str(exc)) from None
    return [tip for _, _, tip in pairs]


def ungated_lines(repo: Path, remote: str, gate_tips: list[str]) -> list[str]:
    """Flag the commits of a checkout that neither its upstream (or every tracking ref) nor an open push-gate tip holds."""
    head = git(repo, "rev-parse", "HEAD")
    if any(gate_row.is_ancestor(repo, head, tip) for tip in gate_tips):
        return []
    branch = git(repo, "rev-parse", "--abbrev-ref", "HEAD")
    try:
        upstream = git(repo, "rev-parse", "--verify", "@{upstream}")
    except GuardError:
        exclude, rng = ["--remotes"], f"{head} (no upstream; outside every remote-tracking ref)"
    else:
        exclude, rng = [upstream], f"{upstream}..{head}"
    commits = git(repo, "rev-list", head, "--not", *exclude, *gate_tips).splitlines()
    if gate_tips and gate_row.is_ancestor(repo, gate_tips[-1], head):
        rng = f"{gate_tips[-1]}..{head}"
    elif gate_tips:
        rng += f", excluding open push-gate tips {' '.join(gate_tips)}"
    if not commits:
        return []
    return [f"UNGATED: branch {branch}, {len(commits)} commits, range {rng}",
            "no open push-gate: the Lead has not gated this work"]


def tracking_tip(repo: Path, remote: str, branch: str) -> str | None:
    """The local remote-tracking tip of a branch, or None for a new branch."""
    try:
        return git(repo, "rev-parse", "--verify", f"refs/remotes/{remote}/{branch}^{{commit}}")
    except GuardError:
        return None


class Item(NamedTuple):
    text: str
    ledger: Path
    repo: Path
    branch: str
    base: str
    tip: str


def digest_project(ledger: Path, repo: Path, remote: str, now: datetime,
                   offered: int) -> tuple[list[str], list[Item]]:
    """One project's digest lines and one question item per branch whose range is fully reviewed.

    Items are numbered from offered + 1. A new branch whose tip descends from another
    open-gate branch's tip is stacked on it: those tips are excluded from its base, and
    it is offered only when every branch it is stacked on is offered.
    """
    with gate_row.locked_ledger(ledger, exclusive=False) as handle:
        rows = gate_row.ledger_rows(gate_row.handle_text(handle))
    open_ids = set(gate_row.open_gate_ids(rows))
    gates = [row for row in rows if row.split(" | ")[0] in open_ids
             and gate_row.row_evidence(row)[0] == "push-gate"]
    heads = [gate_row.split_row(row)[0][3].split("@") for row in gates]
    tips = [git(repo, "rev-parse", "--verify", f"{sha}^{{commit}}") for _, sha in heads]
    ungated = ungated_lines(repo, remote, tips)
    if not gates:
        return ungated, []
    branch_gates: dict[str, list[str]] = {}
    branch_tip: dict[str, str] = {}
    for row, (branch, _), tip in zip(gates, heads, tips):
        branch_gates.setdefault(branch, []).append(row)
        branch_tip[branch] = tip
    deps = {branch: [] if tracking_tip(repo, remote, branch) else [
        other for other in branch_gates if branch_tip[other] != tip
        and gate_row.is_ancestor(repo, branch_tip[other], tip)
    ] for branch, tip in branch_tip.items()}
    blocks = {branch: gated_lines(rows, branch_gates[branch], branch, branch_tip[branch],
                                  [branch_tip[dep] for dep in deps[branch]], ledger, repo, remote, now)
              for branch in branch_gates}
    for branch in sorted(branch_gates, key=lambda b: len(deps[b])):  # a dependency has fewer
        if any(blocks[dep][1] is None for dep in deps[branch]):
            blocks[branch] = ([*blocks[branch][0], "NOT READY: a branch it is stacked on is not offered"], None)
    numbers = {}
    for branch in branch_gates:
        if blocks[branch][1]:
            numbers[branch] = offered + len(numbers) + 1
    lines, items = [], []
    for branch in branch_gates:
        block, item = blocks[branch]
        stacked = [f"stacked on {dep} ({f'item {numbers[dep]}' if dep in numbers else 'NOT READY'}): push after it"
                   for dep in deps[branch]]
        lines += [*block[:2], *stacked, *block[2:]]
        if item:
            items.append(item._replace(text=", ".join([item.text, *stacked])))
    return [*lines, *ungated], items


def gated_lines(rows: list[str], gates: list[str], branch: str, tip: str, stacked_tips: list[str],
                ledger: Path, repo: Path, remote: str, now: datetime) -> tuple[list[str], Item | None]:
    ref = f"refs/heads/{branch}"
    lines = [
        f"gates: {' '.join(row.split(' | ')[0] for row in gates)}",
        f"branch: {branch}",
    ]
    base = tracking_tip(repo, remote, branch)
    label = ""
    if base is None and git(repo, "rev-list", "--max-parents=0", tip, "--not", f"--remotes={remote}",
                            *stacked_tips) and not remote_refs(repo, remote):
        base, label = ZERO, " first publication"  # the guard's ls-remote admits a zero base only here
    elif base is None:
        label = " new branch"
        try:
            base = new_branch_base(repo, tip, [f"--remotes={remote}", *stacked_tips],
                                   f"{remote}'s tracking refs (local estimate)")
        except GuardError as exc:
            return [*lines, f"NOT READY: new branch: {exc}"], None
    try:
        commits = gate_row.range_commits(repo, base, tip)
        gate_row.require_review_coverage(rows, repo, base, tip)
    except gate_row.RowError as exc:
        return [*lines, f"range:{label} {base}..{tip}", f"NOT READY: {exc}"], None
    reviews = []
    for row in rows:
        kind, _, status = gate_row.row_evidence(row)
        rng = gate_row.review_range(row) if kind == "review" and status == "recorded:review-pass" else None
        if rng and rng[1] in commits:
            reviews.append(row.split(" | ")[0])
    lines += [
        f"range:{label} {base}..{tip} ({len(commits)} commits)",
        f"review rows: {' '.join(reviews)}; coverage ok",
    ]
    try:
        lines.append(f"authority: granted by {gate_row.require_push_authority(rows, repo, remote, ref, base, tip, now)}")
    except gate_row.RowError as exc:
        lines.append(f"authority: needs push-grant: {exc}")
    text = f"{ledger.parent.name} {branch}{label} {base[:7]}..{tip[:7]} ({len(commits)} commits)"
    return lines, Item(text, ledger, repo, branch, base, tip)


def items_hash(items: list[Item]) -> str:
    """The hash of the numbered question items: number, project, branch and full range."""
    text = "".join(f"{n} {item.ledger.parent.name} {item.branch} {item.base}..{item.tip}\n"
                   for n, item in enumerate(items, 1))
    return hashlib.sha256(text.encode()).hexdigest()


def collect(pairs: list[list[str]], remote: str) -> tuple[list[str], list[Item], int]:
    now = datetime.now(timezone.utc)
    out: list[str] = []
    ready: list[Item] = []
    errors = 0
    for ledger_text, repo_text in pairs:
        ledger, repo = Path(ledger_text), Path(repo_text)
        try:
            lines, items = digest_project(ledger, repo, remote, now, len(ready))
        except (OSError, UnicodeError, gate_row.RowError, GuardError) as exc:
            errors += 1
            lines, items = [f"ERROR: {exc}"], []
        if not lines:
            continue
        out.append(f"== {ledger.parent.name} (ledger {ledger}, repo {repo})")
        out += [f"  {line}" for line in lines]
        ready += items
    return out, ready, errors


def digest(pairs: list[list[str]], remote: str) -> int:
    out, ready, errors = collect(pairs, remote)
    if ready:
        out.append("Question: approve which pushes? Answer all, none, or the numbers.")
        out += [f"  {n}. {item.text}" for n, item in enumerate(ready, 1)]
        out.append(f"items: {items_hash(ready)}")
    else:
        out.append("Question: none — no push is ready.")
    print("\n".join(out))
    return 1 if errors else 0


def grant(pairs: list[list[str]], remote: str, selection: str, expected: str,
          quote: str, channel: str) -> int:
    """Write one open push-grant row per selected item; nothing unless every input holds."""
    _, ready, _ = collect(pairs, remote)
    if not quote.strip() or "\n" in quote:
        raise GuardError("--quote must be the Human's verbatim words on one non-empty line")
    if items_hash(ready) != expected:
        raise GuardError("--items does not match the current question items; rerun --digest and ask again")
    if selection == "all":
        numbers = list(range(1, len(ready) + 1))
    else:
        try:
            numbers = sorted({int(n) for n in selection.split(",")})
        except ValueError:
            raise GuardError(f"--grant {selection!r} is not all or N[,N...]") from None
    unknown = [n for n in numbers if not 1 <= n <= len(ready)]
    if unknown or not numbers:
        raise GuardError(f"--grant names no ready item: {unknown or selection}")
    for item in (ready[n - 1] for n in numbers):
        if not item.ledger.is_absolute():
            raise GuardError(f"ledger {item.ledger} is not absolute")
    written: list[str] = []
    for n in numbers:
        item = ready[n - 1]
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = gate_row.main([
                "--ledger", str(item.ledger), "--repo", str(item.repo),
                "--kind", "push-grant", "--status", "open",
                "--writer", "supervisor", "--channel", channel,
                "--grant", f"{remote} refs/heads/{item.branch} push {item.base}..{item.tip}",
                "--words", "human",
                "--note", f"Human grants push of {item.branch} {item.base[:7]}..{item.tip[:7]}",
                "--quote", quote,
            ])
        if code:
            raise GuardError(f"item {n}: {err.getvalue().strip()}; rows written before it: "
                             f"{' '.join(written) or 'none'}")
        written.append(out.getvalue().split(" | ")[0])
        print(f"item {n}: wrote {written[-1]} to {item.ledger}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ledger", type=Path)
    parser.add_argument("--digest", nargs=2, action="append", metavar=("LEDGER", "REPO"),
                        help="print the open push gates of this project; repeatable; read-only")
    parser.add_argument("--grant", metavar="all|N[,N...]",
                        help="with --digest: record the Human's grant of these items as push-grant rows")
    parser.add_argument("--items", help="with --grant: the items: hash the digest printed")
    parser.add_argument("--quote", help="with --grant: the Human's verbatim words")
    parser.add_argument("--channel", default="supervisor-relay:typed", help="with --grant: the relay channel")
    parser.add_argument("--repo", type=Path, default=Path.cwd())
    # git runs the hook as `<hook> <remote> <url>`; manual runs pass neither.
    parser.add_argument("remote", nargs="?", default="origin")
    parser.add_argument("url", nargs="?")
    args = parser.parse_args(argv)
    if args.digest:
        if args.ledger or args.url:
            parser.error("--digest takes no --ledger or url")
        if args.grant is None:
            if args.items or args.quote is not None:
                parser.error("--items and --quote require --grant")
            return digest(args.digest, args.remote)
        if not args.items or args.quote is None:
            parser.error("--grant requires --items and --quote")
        try:
            return grant(args.digest, args.remote, args.grant, args.items, args.quote, args.channel)
        except GuardError as exc:
            print(f"pre_push_guard: {exc}", file=sys.stderr)
            return 1
    if args.grant or args.items or args.quote is not None:
        parser.error("--grant, --items and --quote require --digest")
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
