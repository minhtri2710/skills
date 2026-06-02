#!/usr/bin/env python3
from __future__ import annotations
import json
from datetime import datetime, timezone
from pathlib import Path
import subprocess
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

def compact_text(text: str, limit: int = 600) -> str:
    """Truncate *text* to *limit* characters, appending an ellipsis marker."""
    text = text.strip()
    if len(text) <= limit:
        return text
    return f"{text[:limit]}...[truncated]"

def stable_json(value: Any) -> str:
    """Calculates a stable, canonical JSON string representation."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"))

def sha256_text(text: str) -> str:
    """Calculates the sha256 digest of a text string."""
    import hashlib
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
