#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path


def repo_head_sentinel(root: Path) -> str:
    try:
        proc = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    except FileNotFoundError:
        return "git:unavailable"
    if proc.returncode != 0:
        return "git:no-head"
    return proc.stdout.strip()


def file_hash(path: Path) -> str:
    raw = path.read_bytes()
    normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return "sha256-lf-normalized:" + hashlib.sha256(normalized).hexdigest()
