#!/usr/bin/env python3
from __future__ import annotations

import fnmatch
import json
import os
import subprocess
from pathlib import Path
from typing import Any

def run_cmd(args: list[str], strip: bool = True, cwd: Path | str | None = None) -> tuple[int, str, str]:
    """Execute a subprocess command, capturing exit code, stdout, and stderr."""
    try:
        proc = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False, cwd=cwd)
        stdout = proc.stdout.strip() if strip else proc.stdout
        stderr = proc.stderr.strip() if strip else proc.stderr
        return proc.returncode, stdout, stderr
    except FileNotFoundError:
        return -1, "", f"Command not found: {args[0]}"

def resolve_obsidian_env() -> dict[str, str | Path | None]:
    """Resolve Obsidian and QMD environment variables with safe defaults.

    Returns None for vault_name/vault_path/learning_dir when no explicit
    configuration exists. Callers must check for None and use local fallback.
    """
    vault_name = os.environ.get("BEO_OBSIDIAN_VAULT_NAME") or os.environ.get("BEO_OBSIDIAN_VAULT_ID") or None
    vault_path_str = os.environ.get("BEO_OBSIDIAN_VAULT")

    if vault_path_str:
        vault_path = Path(vault_path_str).expanduser().resolve()
    elif vault_name:
        vault_path = Path.home() / vault_name
    else:
        vault_path = None

    qmd_collection = os.environ.get("BEO_QMD_COLLECTION") or vault_name
    learning_dir = vault_path / "beo-learnings" if vault_path else None

    return {
        "vault_name": vault_name,
        "vault_path": vault_path,
        "qmd_collection": qmd_collection,
        "learning_dir": learning_dir,
    }

def obsidian_create_available() -> bool:
    """Check if the obsidian CLI is present and supports the 'create' subcommand."""
    try:
        proc = subprocess.run(["obsidian", "help"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        create_proc = subprocess.run(["obsidian", "help", "create"], text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    except FileNotFoundError:
        return False
    help_text = f"{proc.stdout}\n{proc.stderr}"
    create_help_text = f"{create_proc.stdout}\n{create_proc.stderr}"
    return (
        proc.returncode == 0
        and create_proc.returncode == 0
        and "vault=" in help_text
        and all(token in create_help_text for token in ["path=", "content="])
    )


# ---------------------------------------------------------------------------
# Shared helpers — canonical home for functions used by multiple BEO scripts.
# Import from here instead of duplicating in beo_check.py / beo_recall.py.
# ---------------------------------------------------------------------------

def compact_text(text: str, limit: int = 600) -> str:
    """Truncate *text* to *limit* characters, appending an ellipsis marker."""
    text = text.strip()
    if len(text) <= limit:
        return text
    return f"{text[:limit]}...[truncated]"


def actor_identity() -> str | None:
    """Return the current BEO/Beads actor identity from environment."""
    for name in ["BR_ACTOR", "BEO_ACTOR", "AGENT_NAME", "BR_AGENT_NAME", "ACTOR"]:
        value = os.environ.get(name)
        if value:
            return value
    return None


def issue_field(issue: dict[str, Any], *names: str, default: Any = None) -> Any:
    """Return the first matching field from *issue*, falling back to *default*."""
    for name in names:
        if name in issue:
            return issue[name]
    return default


def claim_valid(issue: dict[str, Any]) -> bool:
    """Check whether the current actor holds a valid claim on *issue*."""
    status = str(issue_field(issue, "status", default="")).lower()
    assignee = str(issue_field(issue, "assignee", "owner", default="") or "")
    if status != "in_progress" or not assignee:
        return False
    actor = actor_identity()
    return bool(actor) and assignee == actor


def load_json(path: Path, default: Any = None) -> Any:
    """Load JSON from a file with safe default fallback."""
    if not path.exists():
        return default
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


def normalize_posix(path: str) -> str:
    """Normalize a file path to POSIX style, stripping relative dots and slashes."""
    path = path.replace("\\", "/")
    if path.startswith("./"):
        path = path[2:]
    return path.strip("/")


def path_tokens_overlap(left: str, right: str) -> bool:
    """Check if two POSIX paths or patterns overlap or nested."""
    left = normalize_posix(left).rstrip("/")
    right = normalize_posix(right).rstrip("/")
    if not left or not right:
        return False
    if left == right:
        return True
    try:
        left_p = Path(left)
        right_p = Path(right)
        if right_p.is_relative_to(left_p) or left_p.is_relative_to(right_p):
            return True
    except (ValueError, RuntimeError):
        pass
    if any(char in left for char in "*?[") and fnmatch.fnmatch(right, left):
        return True
    if any(char in right for char in "*?[") and fnmatch.fnmatch(left, right):
        return True
    return False
