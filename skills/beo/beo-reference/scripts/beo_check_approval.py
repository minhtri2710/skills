#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from beo_approval import allow_paths, forbid_patterns, generated_outputs, approval_projection_hash
from beo_paths import has_glob, normalize_posix_path, path_matches_pattern, path_token_covers, path_tokens_overlap
from beo_check_identity import actor_identity
from beo_check_scope import changed_files
from beo_git import file_hash, repo_head_sentinel
from beo_reservation import validate_reservation_record, now_utc, parse_iso


def validate_working_tree_prestate(root: Path, ticket: dict[str, Any]) -> list[str]:
    approved = allow_paths(ticket) + generated_outputs(ticket)
    forbidden = forbid_patterns(ticket)
    try:
        dirty = set(changed_files(root))
    except RuntimeError as exc:
        return [f"unable to inspect working tree: {exc}"]
    dirty_approved = sorted(path for path in dirty if any(path_matches_pattern(path, pattern) for pattern in approved))
    dirty_forbidden = sorted(path for path in dirty_approved if any(path_matches_pattern(path, pattern) for pattern in forbidden))
    if dirty_forbidden:
        return [f"forbidden-scope path is dirty before validation: {path}" for path in dirty_forbidden]
    if dirty_approved:
        return [f"approved-scope path is dirty before validation: {path}" for path in dirty_approved]
    return []


def _safe_file_hash(root: Path, relative_path: str) -> str:
    path = root / relative_path
    root_resolved = root.resolve()
    current = root_resolved
    for part in Path(relative_path).parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(f"approved path is a symlink: {relative_path}")
    resolved = path.resolve()
    try:
        resolved.relative_to(root_resolved)
    except ValueError as exc:
        raise ValueError(f"approved path escapes repo: {relative_path}") from exc
    return file_hash(path)


def compute_prestate(root: Path, ticket: dict[str, Any]) -> dict[str, Any]:
    prestate: dict[str, Any] = {}
    for path_token in allow_paths(ticket) + generated_outputs(ticket):
        normalized_token = normalize_posix_path(path_token)
        if has_glob(normalized_token):
            forbidden = forbid_patterns(ticket)
            matches: list[str] = []
            for path in root.rglob("*"):
                relative = normalize_posix_path(str(path.relative_to(root)))
                if ".git" in path.relative_to(root).parts or not path_matches_pattern(relative, normalized_token):
                    continue
                if any(path_matches_pattern(relative, pattern) for pattern in forbidden):
                    continue
                if path.is_symlink():
                    raise ValueError(f"approved path is a symlink: {relative}")
                if path.is_file():
                    matches.append(relative)
            matches.sort()
            prestate[f"{normalized_token}#matches"] = matches
            for match in matches:
                prestate[match] = _safe_file_hash(root, match)
            continue
        path = root / normalized_token
        prestate[normalized_token] = _safe_file_hash(root, normalized_token) if path.exists() or path.is_symlink() else None
    return prestate


def active_reservation_evidence(root: Path, ticket: dict[str, Any]) -> list[dict[str, Any]] | None:
    if ticket.get("mode") != "strict":
        return None
    reservation_path = root / ".beads" / "beo-reservations.jsonl"
    if not reservation_path.exists():
        raise ValueError("strict approval requires an active reservation")
    approved_paths = allow_paths(ticket) + generated_outputs(ticket)
    actor = actor_identity()
    if not actor:
        raise ValueError("BR_ACTOR or BEO_ACTOR is required for strict reservation validation")
    records: list[dict[str, Any]] = []
    wrong_actor_records: list[dict[str, Any]] = []
    with reservation_path.open("r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid reservation JSON on line {line_number}: {exc}") from exc
            if not isinstance(record, dict):
                raise ValueError(f"reservation entry on line {line_number} must be an object")
            validate_reservation_record(record, line_number)
            if record.get("status") != "active":
                continue
            overlaps_approved = any(path_tokens_overlap(path, approved_path) for path in record.get("paths", []) for approved_path in approved_paths)
            if not overlaps_approved:
                continue
            if record.get("issue_id") != ticket.get("issue_id"):
                raise ValueError(f"active reservation conflicts with another issue: {record.get('issue_id')}")
            if record.get("actor") != actor:
                wrong_actor_records.append(record)
                continue
            records.append({
                "reservation_id": record.get("reservation_id"),
                "issue_id": record.get("issue_id"),
                "actor": record.get("actor"),
                "paths": record.get("paths"),
                "status": record.get("status"),
            })
    reserved_paths = [path for record in records for path in record.get("paths", [])]
    missing_paths = [path for path in approved_paths if not any(path_token_covers(reserved_path, path) for reserved_path in reserved_paths)]
    if missing_paths:
        wrong_actor_covers_missing = any(
            path_token_covers(path, missing_path)
            for record in wrong_actor_records
            for path in record.get("paths", [])
            for missing_path in missing_paths
        )
        if wrong_actor_covers_missing:
            raise ValueError("active same-issue reservation belongs to a different actor")
        raise ValueError(f"active reservation does not cover approved path(s): {', '.join(missing_paths)}")
    return sorted(records, key=lambda item: str(item.get("reservation_id") or ""))


def compute_approval_fields(root: Path, ticket_path: Path, ticket: dict[str, Any]) -> dict[str, Any]:
    ticket_hash = file_hash(ticket_path) if ticket_path.exists() else "missing"
    repo_head = repo_head_sentinel(root)
    reservation_evidence = active_reservation_evidence(root, ticket)
    return {
        "ticket_file_hash": ticket_hash,
        "repo_head": repo_head,
        "approval_projection_hash": approval_projection_hash(ticket, ticket_file_hash=ticket_hash, repo_head=repo_head, reservation_evidence=reservation_evidence),
        "prestate": compute_prestate(root, ticket),
    }


def validate_approval_envelope(root: Path, ticket_path: Path, ticket: dict[str, Any], state: dict[str, Any]) -> list[str]:
    approval = state.get("approval") if isinstance(state.get("approval"), dict) else {}
    if approval.get("status") != "PASS_EXECUTE":
        return ["approval.status must be PASS_EXECUTE"]
    try:
        fields = compute_approval_fields(root, ticket_path, ticket)
    except ValueError as exc:
        return [str(exc)]
    errors = []
    for field, expected in fields.items():
        if approval.get(field) != expected:
            errors.append(f"approval.{field} is stale")
    if approval.get("approved_phase_sequence_id") != state.get("phase_sequence_id") and state.get("phase") == "approved":
        errors.append("approval sequence binding is stale")
    return errors
