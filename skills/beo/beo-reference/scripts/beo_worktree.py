#!/usr/bin/env python3
"""
beo_worktree.py — Git worktree isolation for strict-mode BEO beads.

Commands:
  create   --issue <id> --actor <name>  Create a worktree, return its path
  merge    --issue <id>                 Merge worktree branch into main repo
  cleanup  --issue <id> [--reason ...]  Remove worktree and delete its branch
  status   --issue <id>                 Report worktree status for an issue

All commands operate from the repo root (--root, default: ".").
"""

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional


WORKTREE_BASE = Path(os.environ.get("BEO_WORKTREE_BASE", "/tmp/beo-worktrees"))
SAFE_ISSUE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,120}$")
SAFE_BRANCH_CHAR = re.compile(r"[^A-Za-z0-9._-]")


def now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")


def run_git(args: list[str], cwd: Optional[Path] = None) -> subprocess.CompletedProcess:
    """Run a git command, return completed process. Raise on failure."""
    result = subprocess.run(
        ["git"] + args,
        capture_output=True,
        text=True,
        cwd=cwd or os.getcwd(),
    )
    if result.returncode != 0:
        print(json.dumps({
            "status": "failed",
            "error": f"git {' '.join(args)} failed",
            "stderr": result.stderr.strip(),
            "stdout": result.stdout.strip(),
        }, indent=2))
        sys.exit(1)
    return result


def check_clean_tree(root: Path) -> None:
    """Check that the working tree is clean."""
    result = run_git(["status", "--porcelain"], cwd=root)
    if result.stdout.strip():
        print(json.dumps({
            "status": "failed",
            "error": "Working tree is not clean",
            "dirty": result.stdout.strip().split("\n"),
        }, indent=2))
        sys.exit(1)


def worktree_path(issue_id: str) -> Path:
    if not SAFE_ISSUE_ID.fullmatch(issue_id):
        raise ValueError(f"issue_id {issue_id!r} contains characters that are unsafe for a filesystem path")
    return WORKTREE_BASE / issue_id


def worktree_branch(issue_id: str, actor: str, timestamp: str) -> str:
    if not SAFE_ISSUE_ID.fullmatch(issue_id):
        raise ValueError(f"issue_id {issue_id!r} contains characters that are unsafe for a git branch name")
    safe_actor = SAFE_BRANCH_CHAR.sub("-", actor).strip("-") or "unknown"
    if safe_actor.startswith(".") or safe_actor.endswith(".lock") or ".." in safe_actor:
        raise ValueError(
            f"actor {actor!r} sanitizes to invalid branch component {safe_actor!r}: "
            "must not start with '.', end with '.lock', or contain '..'"
        )
    return f"beo/{issue_id}/{safe_actor}/{timestamp}"


def ensure_beads_symlink(root: Path, wt_path: Path) -> None:
    """Symlink worktree's .beads to main repo's .beads. Raises on failure.

    State sharing is required for the BEO workflow: state.json, TICKET.yaml,
    and runtime-events.jsonl written inside the worktree must be visible to
    the main repo where the next phase runs. A silent fallback that lets the
    worktree have an isolated .beads directory breaks the entire pipeline.
    """
    main_beads = (root / ".beads").resolve()
    worktree_beads = wt_path / ".beads"
    if main_beads.exists() and not main_beads.is_dir():
        raise RuntimeError(
            f"{main_beads} exists but is not a directory; BEO requires .beads to be a directory"
        )
    if not main_beads.exists():
        return
    if worktree_beads.is_symlink():
        if worktree_beads.resolve() == main_beads:
            return
        worktree_beads.unlink()
    elif worktree_beads.exists():
        raise RuntimeError(
            f"{worktree_beads} is a real directory in the worktree, not a symlink to "
            f"{main_beads}. BEO requires .beads to be shared between the worktree and the "
            f"main repo. Common causes: .beads is tracked by git (remove it from tracking "
            f"and add it to .gitignore), or a previous run created a real .beads directory. "
            f"Clean up with `beo_worktree.py cleanup --issue <issue-id>` and retry."
        )
    try:
        worktree_beads.symlink_to(main_beads, target_is_directory=True)
    except OSError as exc:
        raise RuntimeError(
            f"Failed to symlink {worktree_beads} -> {main_beads}: {exc}. "
            "BEO requires .beads to be shared between the worktree and the main repo. "
            "Clean up with `beo_worktree.py cleanup --issue <id>` and retry."
        ) from exc


def find_existing_worktree(root: Path, issue_id: str) -> Optional[str]:
    """Check if a worktree already exists for this issue. Return branch name or None."""
    result = run_git(["worktree", "list", "--porcelain"], cwd=root)
    wt_path = str(worktree_path(issue_id).resolve())
    lines = result.stdout.strip().split("\n")
    i = 0
    while i < len(lines):
        listed = lines[i]
        if listed.startswith("worktree "):
            listed_path = listed.removeprefix("worktree ")
            if os.path.realpath(listed_path) == wt_path:
                for j in range(i + 1, min(i + 4, len(lines))):
                    if lines[j].startswith("branch "):
                        return lines[j].removeprefix("branch refs/heads/").strip()
        i += 1
    return None


def cmd_create(root: Path, issue_id: str, actor: str) -> int:
    wt_path = worktree_path(issue_id)
    timestamp = now_utc()
    branch = worktree_branch(issue_id, actor, timestamp)

    existing = find_existing_worktree(root, issue_id)
    if existing:
        if not wt_path.is_dir():
            # Worktree is registered with git but the path is missing or
            # not a directory (stale entry). Clear the stale path and the
            # git registration, then fall through to fresh creation.
            if wt_path.is_symlink() or wt_path.exists():
                wt_path.unlink()
            subprocess.run(
                ["git", "worktree", "prune"],
                capture_output=True, text=True, cwd=root, check=False,
            )
        else:
            ensure_beads_symlink(root, wt_path)
            result = run_git(["rev-parse", existing], cwd=root)
            print(json.dumps({
                "status": "exists",
                "worktree_path": str(wt_path),
                "branch": existing,
                "head_ref": result.stdout.strip(),
            }, indent=2))
            return 0

    # New worktree creation requires a clean main-repo tree so the worktree
    # branch starts from a known state. Re-entry above does not modify the
    # main repo, so it does not require a clean tree.
    check_clean_tree(root)

    # Create the worktree. `git worktree add -b` creates the branch in one step
    # without changing the main repo's HEAD. For an existing branch, add the
    # worktree directly. Either way, the main repo stays on its original branch.
    wt_path.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(
        ["git", "rev-parse", "--verify", "--quiet", branch],
        capture_output=True, cwd=root,
    )
    if result.returncode == 0:
        run_git(["worktree", "add", str(wt_path), branch], cwd=root)
    else:
        run_git(["worktree", "add", "-b", branch, str(wt_path)], cwd=root)

    ensure_beads_symlink(root, wt_path)

    head_ref = run_git(["rev-parse", branch], cwd=root)

    print(json.dumps({
        "status": "success",
        "worktree_path": str(wt_path),
        "branch": branch,
        "head_ref": head_ref.stdout.strip(),
    }, indent=2))
    return 0


def cmd_merge(root: Path, issue_id: str) -> int:
    wt_path = worktree_path(issue_id)
    if not wt_path.is_dir():
        print(json.dumps({
            "status": "not_found",
            "error": f"No worktree found for issue {issue_id} at {wt_path}",
        }, indent=2))
        return 1

    existing = find_existing_worktree(root, issue_id)
    if not existing:
        print(json.dumps({
            "status": "not_found",
            "error": f"No worktree branch found for issue {issue_id}",
        }, indent=2))
        return 1

    branch = existing

    # Check if worktree branch has commits the main branch doesn't
    result = run_git(["rev-list", "--count", f"HEAD..{branch}"], cwd=root)
    commits_in_branch_not_in_main = int(result.stdout.strip())
    if commits_in_branch_not_in_main == 0:
        print(json.dumps({
            "status": "no_changes",
            "branch": branch,
            "message": "No new commits on worktree branch, nothing to merge",
        }, indent=2))
        return 0

    # Merge worktree branch into current branch. git merge itself is the
    # conflict detector; on conflict we abort and report. Pre-merge
    # detection via `git merge-tree` was tried and dropped because the
    # output format is a combined diff that requires a fragile parser.
    # Use a non-exiting variant so we can abort on failure.
    merge_proc = subprocess.run(
        ["git", "merge", "--no-ff", branch, "-m", f"merge beo worktree {issue_id}"],
        capture_output=True, text=True, cwd=root,
    )
    if merge_proc.returncode != 0:
        # Abort the failed merge
        subprocess.run(
            ["git", "merge", "--abort"],
            capture_output=True, text=True, cwd=root, check=False,
        )
        print(json.dumps({
            "status": "failed",
            "branch": branch,
            "error": f"git merge failed and was aborted: {merge_proc.stderr.strip()}",
            "stdout": merge_proc.stdout.strip(),
        }, indent=2))
        return 1

    print(json.dumps({
        "status": "success",
        "branch": branch,
        "message": f"Merged {branch} into current branch",
    }, indent=2))
    return 0


def cmd_cleanup(root: Path, issue_id: str, reason: str) -> int:
    """Remove worktree and delete its branch."""
    wt_path = worktree_path(issue_id)
    existing = find_existing_worktree(root, issue_id)

    errors = []

    # Remove worktree. If the path is a non-directory file or symlink,
    # remove it directly; git worktree remove requires a directory.
    if wt_path.is_dir():
        result = subprocess.run(
            ["git", "worktree", "remove", "--force", str(wt_path)],
            capture_output=True, text=True, cwd=root,
        )
        if result.returncode != 0:
            errors.append(f"worktree remove: {result.stderr.strip()}")
    elif wt_path.is_symlink() or wt_path.is_file():
        wt_path.unlink()

    # Prune worktree metadata (collect errors, don't exit on failure)
    result = subprocess.run(
        ["git", "worktree", "prune"],
        capture_output=True, text=True, cwd=root,
    )
    if result.returncode != 0:
        errors.append(f"worktree prune: {result.stderr.strip()}")

    # Delete branch
    if existing:
        result = subprocess.run(
            ["git", "branch", "-D", existing],
            capture_output=True, text=True, cwd=root,
        )
        if result.returncode != 0:
            errors.append(f"branch delete {existing} failed: {result.stderr.strip()}")

    status = "success" if not errors else "partial"
    result = {
        "status": status,
        "issue_id": issue_id,
        "reason": reason,
    }
    if errors:
        result["errors"] = errors
    if existing:
        result["branch"] = existing

    print(json.dumps(result, indent=2))
    return 0 if status == "success" else 1


def cmd_status(root: Path, issue_id: str) -> int:
    """Report worktree status for an issue."""
    wt_path = worktree_path(issue_id)
    existing = find_existing_worktree(root, issue_id)

    status = "not_found"
    details = {}

    if existing:
        if wt_path.is_dir():
            status = "active"
            details["branch"] = existing
            details["worktree_path"] = str(wt_path)

            # Get latest commit on worktree branch
            result = subprocess.run(
                ["git", "log", "-1", "--oneline", existing],
                capture_output=True, text=True, cwd=root,
            )
            details["latest_commit"] = result.stdout.strip() if result.returncode == 0 else None
        else:
            # Worktree is registered with git but the path is missing or
            # not a directory. Caller should run `git worktree prune` (or
            # our `cleanup`) to clear it.
            status = "stale"
            details["branch"] = existing

    print(json.dumps({
        "status": status,
        "issue_id": issue_id,
        **details,
    }, indent=2))
    return 0


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="BEO git worktree isolation manager")
    parser.add_argument("--root", default=".")

    subparsers = parser.add_subparsers(dest="command", required=True)

    p_create = subparsers.add_parser("create")
    p_create.add_argument("--issue", required=True)
    p_create.add_argument("--actor", required=True)

    p_merge = subparsers.add_parser("merge")
    p_merge.add_argument("--issue", required=True)

    p_cleanup = subparsers.add_parser("cleanup")
    p_cleanup.add_argument("--issue", required=True)
    p_cleanup.add_argument("--reason", default="completed")

    p_status = subparsers.add_parser("status")
    p_status.add_argument("--issue", required=True)

    args = parser.parse_args(argv)
    root = Path(args.root).resolve()

    try:
        if args.command == "create":
            return cmd_create(root, args.issue, args.actor)
        elif args.command == "merge":
            return cmd_merge(root, args.issue)
        elif args.command == "cleanup":
            return cmd_cleanup(root, args.issue, args.reason)
        elif args.command == "status":
            return cmd_status(root, args.issue)
    except Exception as exc:
        print(json.dumps({
            "status": "failed",
            "error": str(exc),
        }, indent=2))
        return 1

    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
