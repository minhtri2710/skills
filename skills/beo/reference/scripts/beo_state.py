#!/usr/bin/env python3
from __future__ import annotations

import fcntl
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Callable

def load_owner_fields(root: Path) -> dict[str, set[str]]:
    schema_path = root / "skills" / "beo" / "reference" / "registry" / "ticket-schema.json"
    if not schema_path.exists():
        schema_path = Path(__file__).resolve().parents[1] / "registry" / "ticket-schema.json"
    
    if schema_path.exists():
        try:
            with open(schema_path, "r", encoding="utf-8") as f:
                schema = json.load(f)
                owner_fields = schema.get("owner_fields", {})
                if owner_fields:
                    return {str(k): set(str(v) for v in val) for k, val in owner_fields.items() if isinstance(val, list)}
        except Exception:
            pass
            
    # Fallback to prevent bootstrap failure
    return {
        "beo-validate": {"readiness", "selected_execution_set", "execution_mode", "approval_ref", "integrity"},
        "beo-execute": {"execution"},
        "beo-review": {"review"},
        "beo-debug": {"debug"},
    }


def _artifact_dir(root: Path, issue_id: str) -> Path:
    return root / ".beads" / "artifacts" / issue_id


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


def _read_state_unlocked(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("state.json must be an object")
    return data


def locked_read_state(root: Path, issue_id: str) -> dict[str, Any]:
    base = _artifact_dir(root, issue_id)
    lock = _locked(base / "state.lock")
    try:
        return _read_state_unlocked(base / "state.json")
    finally:
        _unlock(lock)


def _reject_unowned_changes(root: Path, before: dict[str, Any], after: dict[str, Any], owner: str) -> None:
    owner_fields = load_owner_fields(root)
    allowed = owner_fields.get(owner)
    if allowed is None:
        raise ValueError(f"unknown state owner: {owner}")
    changed = {key for key in set(before) | set(after) if before.get(key) != after.get(key)}
    unowned = sorted(changed - allowed)
    if unowned:
        raise ValueError(f"{owner} cannot write state field(s): {', '.join(unowned)}")


def locked_update_state(
    root: Path,
    issue_id: str,
    owner: str,
    updater: Callable[[dict[str, Any]], dict[str, Any]],
) -> dict[str, Any]:
    base = _artifact_dir(root, issue_id)
    lock = _locked(base / "state.lock")
    try:
        path = base / "state.json"
        before = _read_state_unlocked(path)
        after = updater(dict(before))
        if not isinstance(after, dict):
            raise ValueError("state updater must return an object")
        _reject_unowned_changes(root, before, after, owner)
        atomic_write_json(path, after)
        return after
    finally:
        _unlock(lock)


def read_events(root: Path, issue_id: str) -> list[dict[str, Any]]:
    base = _artifact_dir(root, issue_id)
    lock = _locked(base / "runtime-events.lock")
    try:
        path = base / "runtime-events.jsonl"
        events: list[dict[str, Any]] = []
        if not path.exists():
            return events
        with open(path, "r", encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                line = line.strip()
                if not line:
                    continue
                event = json.loads(line)
                if not isinstance(event, dict):
                    raise ValueError(f"runtime-events.jsonl line {line_number} must be an object")
                events.append(event)
        return events
    finally:
        _unlock(lock)


def append_event(root: Path, issue_id: str, event: dict[str, Any]) -> None:
    if not isinstance(event, dict):
        raise ValueError("runtime event must be an object")
    base = _artifact_dir(root, issue_id)
    lock = _locked(base / "runtime-events.lock")
    try:
        base.mkdir(parents=True, exist_ok=True)
        path = base / "runtime-events.jsonl"
        line = json.dumps(event, sort_keys=True) + "\n"
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(line)
            handle.flush()
            os.fsync(handle.fileno())
        _fsync_dir(path.parent)
    finally:
        _unlock(lock)
