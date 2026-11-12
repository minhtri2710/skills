"""The delivery scripts' one git runner and the commit questions they share."""
from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Callable
from pathlib import Path

from bounded_run import stop_group

NULL_OID = "0" * 40
FULL_SHA = r"[0-9a-f]{40}"
SHA_RE = re.compile(FULL_SHA)


class GitError(Exception):
    pass


def git(repo: Path, *args: str, stdin: str | None = None, timeout: float | None = None) -> str:
    """Run `git -C repo args`; return stdout without its final newline, or raise GitError.

    Git never prompts. A `timeout` kills git's whole process group at the limit and raises GitError.
    """
    try:
        proc = subprocess.Popen(
            ["git", "-C", str(repo), *args], stdin=subprocess.DEVNULL if stdin is None else subprocess.PIPE,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8",
            start_new_session=True, env={**os.environ, "GIT_TERMINAL_PROMPT": "0"},
        )
    except OSError as exc:
        raise GitError(f"could not run git: {exc}") from exc
    try:
        out, err = proc.communicate(stdin, timeout=timeout)
    except subprocess.TimeoutExpired:
        stop_group(proc, 5)
        proc.communicate()
        raise GitError(f"git {' '.join(args)} passed its {timeout:g}s limit; its process group was killed") from None
    if proc.returncode != 0:
        raise GitError(f"git {' '.join(args)} failed: {err.strip()}")
    return out.rstrip("\n")


Runner = Callable[..., str]


def is_ancestor(repo: Path, ancestor: str, descendant: str) -> bool:
    try:
        git(repo, "merge-base", "--is-ancestor", ancestor, descendant)
    except GitError:
        return False
    return True


def range_commits(
    repo: Path, base: str, head: str, *, oldest_first: bool = False, run: Runner = git,
) -> list[str]:
    order = ["--reverse"] if oldest_first else []
    if base == NULL_OID:
        commits = run(repo, "rev-list", *order, head).splitlines()
    else:
        run(repo, "merge-base", "--is-ancestor", base, head)
        commits = run(repo, "rev-list", *order, f"{base}..{head}").splitlines()
    if not commits:
        raise GitError(f"range {base}..{head} carries no commit")
    return commits


def landed_commits(repo: Path, head: str, commits: set[str], *, run: Runner = git) -> set[str]:
    """The commits already reachable from origin/HEAD, the remote's product line; none without it."""
    try:
        tip = run(repo, "rev-parse", "--verify", "refs/remotes/origin/HEAD^{commit}")
    except GitError:
        return set()
    return commits - set(run(repo, "rev-list", head, "--not", tip).split())


def clean_merge_parents(repo: Path, sha: str, *, run: Runner = git) -> list[str] | None:
    """The two parents of a merge commit whose tree is exactly their automatic merge, else None."""
    parents = run(repo, "rev-list", "--parents", "-n", "1", sha).split()[1:]
    if len(parents) != 2:
        return None
    try:
        merged = run(repo, "merge-tree", "--write-tree", *parents).split()[0]
    except GitError:
        return None
    return parents if merged == run(repo, "rev-parse", f"{sha}^{{tree}}") else None
