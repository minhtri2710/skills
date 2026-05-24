#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

from beo_utils import issue_field
from beo_registry_context import RegistryContext

def labels_of(issue: dict[str, Any]) -> list[str]:
    labels = issue_field(issue, "labels", "label", default=[])
    if isinstance(labels, str):
        return [item.strip() for item in labels.split(",") if item.strip()]
    if isinstance(labels, list):
        return [str(item) for item in labels]
    return []

def is_parent_or_non_atomic(issue: dict[str, Any], ticket: dict[str, Any]) -> bool:
    issue_type = str(issue_field(issue, "issue_type", "type", default="")).lower()
    labels = {label.lower() for label in labels_of(issue)}
    if "beo:atomic" in labels:
        return False
    if issue_type in {"epic", "feature"}:
        return True
    if labels & {"beo:epic", "beo:feature"}:
        return True
    return False

def validate_identity(
    root: Path,
    issue_id: str,
    ticket_path: Path,
    ticket: dict[str, Any],
    issue: dict[str, Any],
    ctx: RegistryContext,
    ticket_path_for_func: Any,
    read_ticket_func: Any
) -> list[str]:
    errors: list[str] = []
    issue_actual = str(issue_field(issue, "id", default=issue_id))
    if issue_actual != issue_id:
        errors.append(f"br issue id mismatch: expected {issue_id}, got {issue_actual}")
    
    expected_path = ticket_path_for_func(root, issue_id).resolve()
    if ticket_path.resolve() != expected_path:
        try:
            rel = expected_path.relative_to(root.resolve())
        except ValueError:
            rel = expected_path
        errors.append(f"ticket path must be {rel}")
    
    if ticket.get("issue_id") != issue_id:
        errors.append("ticket issue_id does not match selected bead")
    
    schema_ver = ctx.schema.get("schema_version", "beo-beads/v3")
    if ticket.get("schema_version") != schema_ver:
        errors.append(f"unsupported ticket schema_version: {ticket.get('schema_version')}")
    
    artifacts_dir = root / ".beads" / "artifacts"
    if artifacts_dir.exists():
        for duplicate in artifacts_dir.glob("*/TICKET.md"):
            if duplicate.resolve() == ticket_path.resolve():
                continue
            try:
                other = read_ticket_func(duplicate)
            except Exception:
                continue
            if other.get("issue_id") == issue_id:
                errors.append(f"duplicate ticket for issue {issue_id}: {duplicate}")
                
    if is_parent_or_non_atomic(issue, ticket) and ticket.get("readiness") == "PASS_EXECUTE":
        errors.append("parent/feature/epic beads must not receive PASS_EXECUTE")
        
    return errors
