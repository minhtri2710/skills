#!/usr/bin/env python3
from __future__ import annotations
from typing import Any

from beo_io import stable_json, sha256_text


def path_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


def scope(ticket: dict[str, Any]) -> dict[str, Any]:
    return ticket.get("scope") if isinstance(ticket.get("scope"), dict) else {}


def allow_paths(ticket: dict[str, Any]) -> list[str]:
    files = scope(ticket).get("files") if isinstance(scope(ticket).get("files"), dict) else {}
    return path_list(files.get("allow"))


def forbid_patterns(ticket: dict[str, Any]) -> list[str]:
    files = scope(ticket).get("files") if isinstance(scope(ticket).get("files"), dict) else {}
    return path_list(files.get("forbid"))


def generated_outputs(ticket: dict[str, Any]) -> list[str]:
    return path_list(scope(ticket).get("generated_outputs"))


def verify_commands(ticket: dict[str, Any]) -> list[str]:
    verify = scope(ticket).get("verify") if isinstance(scope(ticket).get("verify"), dict) else {}
    return [str(cmd) for cmd in path_list(verify.get("commands"))]


def approval_projection(
    ticket: dict[str, Any],
    *,
    ticket_file_hash: str | None = None,
    repo_head: str | None = None,
    reservation_evidence: Any = None,
) -> dict[str, Any]:
    from beo_ticket import approval_projection_input

    proj = approval_projection_input(ticket)
    if ticket_file_hash is not None:
        proj["ticket_file_hash"] = ticket_file_hash
    if repo_head is not None:
        proj["repo_head"] = repo_head
    if ticket.get("mode") == "strict" and reservation_evidence is not None:
        proj["reservation"] = reservation_evidence
    return proj


def approval_projection_hash(
    ticket: dict[str, Any],
    *,
    ticket_file_hash: str | None = None,
    repo_head: str | None = None,
    reservation_evidence: Any = None,
) -> str:
    return sha256_text(stable_json(approval_projection(
        ticket,
        ticket_file_hash=ticket_file_hash,
        repo_head=repo_head,
        reservation_evidence=reservation_evidence,
    )))
