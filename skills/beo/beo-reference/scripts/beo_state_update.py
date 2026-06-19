#!/usr/bin/env python3
"""Locked state.json updater and runtime-events.jsonl reader/append.

This module owns the phase-transition mechanics: copy-on-update with
owner-field authority, sequence-id bump, and event I/O. The validation
contracts and I/O primitives live in ``beo_state_validate`` and
``beo_state_io`` respectively.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
from typing import Any, Callable

from beo_io import now
from beo_state_io import _locked, _unlock, _fsync_dir, _read_state_unlocked, artifact_dir, atomic_write_json


OWNER_FIELDS = {
    "beo-plan": {"initialize"},
    "beo-validate": {"phase", "approval"},
    "beo-execute": {"phase", "execution", "review"},
    "beo-review": {"phase", "review"},
    "beo-debug": set(),
    "beo-learn": set(),
    "beo-author": set(),
    "beo-setup": set(),
    "beo-reference": set(),
}
SYSTEM_FIELDS = {"version", "issue_id", "phase_sequence_id", "metadata"}


def _reject_caller_system_fields(before: dict[str, Any], after: dict[str, Any]) -> None:
    if after.get("phase_sequence_id") != before.get("phase_sequence_id"):
        raise ValueError("state updater must not set phase_sequence_id")
    before_meta = before.get("metadata") if isinstance(before.get("metadata"), dict) else {}
    after_meta = after.get("metadata") if isinstance(after.get("metadata"), dict) else {}
    for field in ["updated_at", "last_owner"]:
        if after_meta.get(field) != before_meta.get(field):
            raise ValueError(f"state updater must not set metadata.{field}")
    before_approval = before.get("approval") if isinstance(before.get("approval"), dict) else {}
    after_approval = after.get("approval") if isinstance(after.get("approval"), dict) else {}
    if after_approval.get("approved_phase_sequence_id") != before_approval.get("approved_phase_sequence_id"):
        raise ValueError("state updater must not set approval.approved_phase_sequence_id")


def _reject_unowned_changes(before: dict[str, Any], after: dict[str, Any], owner: str) -> None:
    owned = OWNER_FIELDS.get(owner)
    if owned is None:
        raise ValueError(f"unknown state owner: {owner}")
    allowed = owned | SYSTEM_FIELDS
    changed = {key for key in set(before) | set(after) if before.get(key) != after.get(key)}
    unowned = sorted(changed - allowed)
    if unowned:
        raise ValueError(f"{owner} cannot write state field(s): {', '.join(unowned)}")
    if owner in {"beo-debug", "beo-learn"} and changed - SYSTEM_FIELDS:
        raise ValueError(f"{owner} may not write delivery state")


def locked_update_state(
    root: Path,
    issue_id: str,
    owner: str,
    updater: Callable[[dict[str, Any]], dict[str, Any] | None],
) -> dict[str, Any]:
    if owner not in OWNER_FIELDS:
        raise ValueError(f"unknown state owner: {owner}")
    if not OWNER_FIELDS[owner]:
        raise ValueError(f"{owner} may not update delivery state")
    base = artifact_dir(root, issue_id)
    lock = _locked(base / "state.lock")
    try:
        path = base / "state.json"
        before = _read_state_unlocked(path, issue_id)
        candidate = copy.deepcopy(before)
        after = updater(candidate)
        if after is None:
            after = candidate
        if not isinstance(after, dict):
            raise ValueError("state updater must return an object")
        _reject_caller_system_fields(before, after)
        _reject_unowned_changes(before, after, owner)
        if owner == "beo-execute":
            if before.get("phase") == "approved":
                if before.get("approval", {}).get("status") != "PASS_EXECUTE":
                    raise ValueError("current PASS_EXECUTE approval is required")
                if not execution_entry_is_current(before):
                    raise ValueError("PASS_EXECUTE approval is stale for execution entry")
                execution = after.get("execution") if isinstance(after.get("execution"), dict) else {}
                if after.get("phase") != "executing":
                    raise ValueError("beo-execute must durably enter executing state before product mutation")
                if not isinstance(execution.get("actor"), str) or not execution["actor"].strip():
                    raise ValueError("execution start requires execution.actor")
                if not isinstance(execution.get("started_at"), str) or not execution["started_at"].strip():
                    raise ValueError("execution start requires execution.started_at")
            elif before.get("phase") not in {"executing", "executed"}:
                raise ValueError("beo-execute requires approved/executing/executed state")
            review = after.get("review") if isinstance(after.get("review"), dict) else {}
            if review.get("route_condition_id") == "verdict_accept":
                raise ValueError("beo-execute may not emit verdict_accept; that route signals br close and is beo-review only")
            if review.get("closed_in_br"):
                raise ValueError("beo-execute may not set review.closed_in_br; beo-execute is not authorized to close in br")
        after["phase_sequence_id"] = int(before["phase_sequence_id"]) + 1
        after.setdefault("metadata", {})["updated_at"] = now()
        after["metadata"]["last_owner"] = owner
        if owner == "beo-validate" and after.get("approval", {}).get("status") == "PASS_EXECUTE":
            if after.get("phase") != "approved":
                raise ValueError("PASS_EXECUTE approval must explicitly set phase to approved")
            after["approval"]["approved_phase_sequence_id"] = after["phase_sequence_id"]
        # Lazy import to avoid a hard cycle with beo_state_validate at module load.
        from beo_state_validate import validate_state

        validate_state(after, issue_id)
        atomic_write_json(path, after)
        return after
    finally:
        _unlock(lock)


def execution_entry_is_current(state: dict[str, Any]) -> bool:
    return state.get("phase_sequence_id") == state.get("approval", {}).get("approved_phase_sequence_id")


def read_events(root: Path, issue_id: str) -> list[dict[str, Any]]:
    base = artifact_dir(root, issue_id)
    path = base / "runtime-events.jsonl"
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
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


def append_event(root: Path, issue_id: str, event: dict[str, Any]) -> None:
    if event.get("issue_id") != issue_id:
        raise ValueError("runtime event issue_id mismatch")
    # Lazy import to avoid a hard cycle with beo_state_validate at module load.
    from beo_state_validate import validate_event_schema

    validate_event_schema(event)
    base = artifact_dir(root, issue_id)
    base.mkdir(parents=True, exist_ok=True)
    lock = _locked(base / "runtime-events.lock")
    try:
        path = base / "runtime-events.jsonl"
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True, separators=(",", ":")))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        _fsync_dir(base)
    finally:
        _unlock(lock)
