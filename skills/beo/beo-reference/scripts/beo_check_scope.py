#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

from beo_paths import normalize_posix_path


def _git_output_text(output: bytes | str) -> str:
    if isinstance(output, bytes):
        return output.decode("utf-8", errors="replace")
    return output


def changed_files(root: Path) -> list[str]:
    proc = subprocess.run(["git", "status", "--porcelain=v1", "-z", "--untracked-files=all"], cwd=root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        message = _git_output_text(proc.stderr).strip() or _git_output_text(proc.stdout).strip() or "git status failed"
        raise RuntimeError(message)
    files: list[str] = []
    entries = [entry for entry in proc.stdout.split(b"\0") if entry]
    index = 0
    while index < len(entries):
        entry = entries[index].decode("utf-8", errors="surrogateescape")
        status = entry[:2]
        path = entry[3:] if len(entry) > 3 else entry
        if status.startswith("R") or status.startswith("C"):
            if index + 1 >= len(entries):
                raise RuntimeError("malformed git status porcelain rename/copy entry")
            index += 1
        files.append(normalize_posix_path(path))
        index += 1
    return files
