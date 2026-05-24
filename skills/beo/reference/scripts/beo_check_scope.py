#!/usr/bin/env python3
from __future__ import annotations

import fnmatch
import subprocess
from pathlib import Path
from typing import Any

from beo_utils import normalize_posix, path_tokens_overlap
from beo_registry_context import RegistryContext

def is_broad_glob(path: str) -> bool:
    path = normalize_posix(path)
    return path in {"**", "*"} or path.endswith("/**") or path.endswith("/*")

def glob_match(path: str, pattern: str) -> bool:
    path = normalize_posix(path)
    pattern = normalize_posix(pattern)
    return fnmatch.fnmatch(path, pattern) or (pattern.endswith("/") and path.startswith(pattern))

def is_allowed(path: str, allowed: list[str], generated: list[str]) -> bool:
    path = normalize_posix(path)
    for item in allowed + generated:
        item = normalize_posix(item)
        if path == item or fnmatch.fnmatch(path, item) or (item.endswith("/") and path.startswith(item)):
            return True
    return False

def scope_tokens(ticket: dict[str, Any], allow_paths_func: Any, path_list_func: Any, expanded_posture_func: Any) -> list[str]:
    return [normalize_posix(item) for item in allow_paths_func(ticket) + path_list_func(expanded_posture_func(ticket).get("generated_outputs")) if item]

def active_scope_conflicts(
    root: Path,
    ticket: dict[str, Any],
    ctx: RegistryContext,
    allow_paths_func: Any,
    path_list_func: Any,
    expanded_posture_func: Any,
    read_ticket_func: Any
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    current_issue = str(ticket.get("issue_id") or "")
    current_tokens = scope_tokens(ticket, allow_paths_func, path_list_func, expanded_posture_func)
    artifacts = root / ".beads" / "artifacts"
    if not artifacts.exists() or not current_tokens:
        return errors, warnings

    scope_block = ticket.get("scope", {}) if isinstance(ticket.get("scope"), dict) else {}
    scope_overlap = scope_block.get("scope_overlap")
    safe_overlaps = []
    if isinstance(scope_overlap, dict) and scope_overlap.get("status") == "safe":
        safe_overlaps = scope_overlap.get("overlaps", [])
        if not isinstance(safe_overlaps, list):
            safe_overlaps = []

    for other_path in artifacts.glob("*/TICKET.md"):
        try:
            other = read_ticket_func(other_path)
        except Exception:
            continue
        other_issue = str(other.get("issue_id") or other_path.parent.name)
        if other_issue == current_issue:
            continue
        if other.get("readiness") != "PASS_EXECUTE":
            continue
        review = other.get("review") if isinstance(other.get("review"), dict) else {}
        if review.get("verdict") in {"accept", "abandoned", "cannot_deliver"}:
            continue
        other_tokens = scope_tokens(other, allow_paths_func, path_list_func, expanded_posture_func)

        for left in current_tokens:
            for right in other_tokens:
                if path_tokens_overlap(left, right):
                    overlap_str = f"{left} overlaps {right}"
                    is_safe = False
                    for entry in safe_overlaps:
                        if not isinstance(entry, dict):
                            continue
                        if entry.get("issue_id") == other_issue:
                            safe_reason = entry.get("safe_reason")
                            evidence_ref = entry.get("evidence_ref")
                            if safe_reason not in {"dependency_ordered", "disjoint_region", "user_authorized"}:
                                continue
                            if not evidence_ref:
                                continue
                            paths = entry.get("paths", [])
                            if not isinstance(paths, list):
                                continue
                            
                            match_found = False
                            for path_entry in paths:
                                if isinstance(path_entry, dict):
                                    curr = path_entry.get("current")
                                    oth = path_entry.get("other")
                                    if curr == left and oth == right:
                                        match_found = True
                                        break
                            if match_found:
                                warnings.append(f"ignoring declared safe scope overlap with {other_issue}: {overlap_str} (reason: {safe_reason})")
                                is_safe = True
                                break
                    if not is_safe:
                        errors.append(f"active scope conflict with {other_issue}: {overlap_str}")
    return errors, warnings

def changed_files(root: Path, ticket: dict[str, Any], path_list_func: Any) -> list[str]:
    files: set[str] = set()
    execution = ticket.get("execution") if isinstance(ticket.get("execution"), dict) else {}
    for item in path_list_func(execution.get("changed_files")):
        files.add(normalize_posix(item))
    git_dir = root / ".git"
    if git_dir.exists():
        commands = [
            ["git", "diff", "--name-only"],
            ["git", "diff", "--cached", "--name-only"],
            ["git", "status", "--porcelain"],
        ]
        for command in commands:
            try:
                proc = subprocess.run(command, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
                if proc.returncode != 0:
                    # Task 3.5: Fail-closed VCS checks
                    raise RuntimeError(f"Git execution failed ({command}): {proc.stderr.strip()}")
            except OSError as exc:
                raise RuntimeError(f"Git command execution failed ({command}): {exc}")
            for line in proc.stdout.splitlines():
                if command[-1] == "--porcelain":
                    if not line:
                        continue
                    path = line[3:] if len(line) > 3 else line
                    if " -> " in path:
                        path = path.rsplit(" -> ", 1)[1]
                    files.add(normalize_posix(path))
                elif line.strip():
                    files.add(normalize_posix(line.strip()))
    return sorted(file for file in files if file)
