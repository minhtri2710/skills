#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def labels_of(issue: dict[str, Any]) -> list[str]:
    labels = issue.get("labels", [])
    if isinstance(labels, str):
        return [labels]
    return [str(label) for label in labels] if isinstance(labels, list) else []


def is_parent_or_non_atomic(issue: dict[str, Any]) -> bool:
    issue_type = str(issue.get("issue_type") or issue.get("type") or "task").lower()
    return issue_type in {"epic", "feature"}


def issue_is_closed(issue: dict[str, Any]) -> bool:
    status = str(issue.get("status") or issue.get("state") or "").lower()
    if status in {"closed", "done", "resolved", "terminal", "abandoned", "cancelled", "canceled"}:
        return True
    return bool(issue.get("closed") or issue.get("is_closed"))


def issue_has_blockers(issue: dict[str, Any]) -> bool:
    for field in ["blocked_by", "open_blockers", "unresolved_blockers", "active_blockers"]:
        value = issue.get(field)
        if isinstance(value, list) and value:
            return True
    for field in ["blocked", "is_blocked", "has_open_blockers"]:
        if issue.get(field):
            return True
    return False


def actor_identity() -> str | None:
    return os.environ.get("BR_ACTOR") or os.environ.get("BEO_ACTOR")


def normalized_claim(issue: dict[str, Any]) -> str | None:
    for field in ["assignee", "claimed_by", "owner", "claim", "claimed"]:
        claim = issue.get(field)
        if isinstance(claim, str):
            return claim
        if isinstance(claim, dict):
            for key in ["actor", "name", "id", "handle", "user"]:
                value = claim.get(key)
                if isinstance(value, str) and value:
                    return value
    return None


def claim_valid(issue: dict[str, Any], actor: str) -> bool:
    return normalized_claim(issue) == actor


def validate_identity(root: Path, issue_id: str, ticket_path: Path, ticket: dict[str, Any], issue: dict[str, Any], ticket_path_for) -> list[str]:
    errors: list[str] = []
    if ticket.get("version") != 1:
        errors.append(f"unsupported TICKET.yaml version: {ticket.get('version')}")
    if ticket.get("issue_id") != issue_id:
        errors.append("ticket issue_id must match selected issue")
    expected_path = ticket_path_for(root, issue_id)
    if ticket_path != expected_path:
        errors.append(f"ticket path must be {expected_path}")
    if is_parent_or_non_atomic(issue):
        errors.append("issue is not atomic; route to beo-plan decomposition")
    actor = actor_identity()
    if not actor:
        errors.append("BR_ACTOR or BEO_ACTOR is required for claim validation")
    elif not claim_valid(issue, actor):
        errors.append("br issue claim does not match acting actor")
    return errors
