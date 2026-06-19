#!/usr/bin/env python3
"""State file I/O, locks, and atomic writes for BEO state.json.

Public symbols: ``artifact_dir``, ``initial_state``, ``atomic_write_json``,
``read_state``, ``initialize_state``. Underscore-prefixed helpers are
internal and consumed directly by ``beo_state_update``; they are not part
of the ``beo_state`` facade's public surface.
"""
from __future__ import annotations

import fcntl
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from beo_io import now


def artifact_dir(root: Path, issue_id: str) -> Path:
    from beo_paths import artifact_dir as safe_artifact_dir

    return safe_artifact_dir(root, issue_id)


def initial_state(issue_id: str) -> dict[str, Any]:
    return {
        "version": 1,
        "issue_id": issue_id,
        "phase": "planned",
        "phase_sequence_id": 1,
        "approval": {
            "status": "pending",
            "approved_by": None,
            "actor": None,
            "ticket_file_hash": None,
            "approval_projection_hash": None,
            "repo_head": None,
            "prestate": {},
            "failure_category": None,
            "approved_phase_sequence_id": None,
        },
        "execution": {
            "actor": None,
            "started_at": None,
            "completed_at": None,
            "changed_files": [],
            "verify_results": [],
            "evidence_refs": [],
            "trace_tier": None,
            "interventions": [],
        },
        "review": {
            "actor": None,
            "verdict": None,
            "route_condition_id": None,
            "findings": [],
            "done_criteria_coverage": [],
            "repair_count": 0,
            "closed_in_br": False,
            "reviewed_by": "beo-review",
        },
        "metadata": {
            "last_owner": None,
            "updated_at": None,
        },
    }


def _locked(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = open(lock_path, "w", encoding="utf-8")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX)
    except Exception:
        handle.close()
        raise
    return handle


def _unlock(handle) -> None:
    fcntl.flock(handle, fcntl.LOCK_UN)
    handle.close()


def _fsync_dir(path: Path) -> None:
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write_json(path: Path, data: Any) -> None:
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must be an object")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
        _fsync_dir(path.parent)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def _read_state_unlocked(path: Path, issue_id: str) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"state_artifact_missing: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("state.json must be an object")
    # Lazy import to avoid a hard cycle with beo_state_validate at module load.
    from beo_state_validate import validate_state

    validate_state(data, issue_id)
    return data


def read_state(root: Path, issue_id: str) -> dict[str, Any]:
    base = artifact_dir(root, issue_id)
    lock = _locked(base / "state.lock")
    try:
        return _read_state_unlocked(base / "state.json", issue_id)
    finally:
        _unlock(lock)


def initialize_state(root: Path, issue_id: str, *, owner: str = "beo-plan", overwrite: bool = False) -> dict[str, Any]:
    if owner != "beo-plan":
        raise ValueError("only beo-plan may initialize state")
    base = artifact_dir(root, issue_id)
    lock = _locked(base / "state.lock")
    try:
        path = base / "state.json"
        if path.exists() and not overwrite:
            raise FileExistsError(f"state.json already exists: {path}")
        state = initial_state(issue_id)
        state["metadata"]["updated_at"] = now()
        state["metadata"]["last_owner"] = owner
        # Lazy import to avoid a hard cycle with beo_state_validate at module load.
        from beo_state_validate import validate_state

        validate_state(state, issue_id)
        atomic_write_json(path, state)
        return state
    finally:
        _unlock(lock)
