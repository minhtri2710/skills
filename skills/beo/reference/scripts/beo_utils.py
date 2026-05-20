#!/usr/bin/env python3
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

def run_cmd(args: list[str], strip: bool = True) -> tuple[int, str, str]:
    """Execute a subprocess command, capturing exit code, stdout, and stderr."""
    try:
        proc = subprocess.run(args, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        stdout = proc.stdout.strip() if strip else proc.stdout
        stderr = proc.stderr.strip() if strip else proc.stderr
        return proc.returncode, stdout, stderr
    except FileNotFoundError:
        return -1, "", f"Command not found: {args[0]}"

def resolve_obsidian_env() -> dict[str, str | Path]:
    """Resolve Obsidian and QMD environment variables with safe defaults."""
    vault_name = os.environ.get("BEO_OBSIDIAN_VAULT_NAME") or os.environ.get("BEO_OBSIDIAN_VAULT_ID") or "second-brain"
    vault_path_str = os.environ.get("BEO_OBSIDIAN_VAULT")
    
    if vault_path_str:
        vault_path = Path(vault_path_str).expanduser().resolve()
    else:
        vault_path = Path.home() / vault_name
        
    qmd_collection = os.environ.get("BEO_QMD_COLLECTION") or vault_name
    learning_dir = vault_path / "beo-learnings"
    
    return {
        "vault_name": vault_name,
        "vault_path": vault_path,
        "qmd_collection": qmd_collection,
        "learning_dir": learning_dir
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
