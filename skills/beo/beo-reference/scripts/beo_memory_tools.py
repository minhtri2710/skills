#!/usr/bin/env python3
from __future__ import annotations
import os
from pathlib import Path

def resolve_obsidian_env() -> dict[str, str | Path | None]:
    """Resolve Obsidian and QMD environment variables with safe defaults."""
    vault_name = os.environ.get("BEO_OBSIDIAN_VAULT_NAME") or os.environ.get("BEO_OBSIDIAN_VAULT_ID") or None
    vault_path_str = os.environ.get("BEO_OBSIDIAN_VAULT")

    if vault_path_str:
        vault_path = Path(vault_path_str).expanduser().resolve()
    else:
        vault_path = None

    qmd_collection = os.environ.get("BEO_QMD_COLLECTION") or vault_name or "beo-learnings"
    learning_dir = vault_path / "beo-learnings" if vault_path else None

    return {
        "vault_name": vault_name,
        "vault_path": vault_path,
        "qmd_collection": qmd_collection,
        "learning_dir": learning_dir,
    }

def obsidian_create_available() -> bool:
    """Check if the obsidian CLI is present and executable."""
    import shutil
    return shutil.which("obsidian") is not None
