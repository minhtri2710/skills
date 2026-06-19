#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any

from beo_io import stable_json, sha256_text
from beo_paths import detect_broad_globs, has_glob, is_protected_path, match_allowed_paths, normalize_posix, reject_unsafe_path
from beo_state import execution_entry_is_current, read_events, read_state
from beo_ticket import read_ticket, ticket_path as ticket_path_for
from beo_approval import allow_paths, forbid_patterns, generated_outputs, verify_commands
from beo_check_approval import validate_approval_envelope, validate_working_tree_prestate
from beo_check_events import validate_runtime_events
from beo_check_identity import issue_has_blockers, issue_is_closed, labels_of, validate_identity

HELPER_VERSION = "beo-check/v5"


def load_profiles(root: Path) -> dict[str, Any]:
    registry_path = root / "skills" / "beo" / "beo-reference" / "registry" / "profiles.json"
    if not registry_path.exists():
        registry_path = Path(__file__).resolve().parents[1] / "registry" / "profiles.json"
    try:
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"failed to load profiles.json: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError("profiles.json must be a JSON object")
    return payload


def run_br_show(root: Path, issue_id: str) -> tuple[dict[str, Any], str | None]:
    try:
        proc = subprocess.run(["br", "show", issue_id, "--json"], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    except FileNotFoundError:
        return {}, "br executable not found"
    if proc.returncode != 0:
        return {}, f"br show failed: {proc.stderr.strip() or proc.stdout.strip()}"
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError as exc:
        return {}, f"br show returned invalid JSON: {exc}"
    if isinstance(payload, list) and payload:
        payload = payload[0]
    if isinstance(payload, dict) and isinstance(payload.get("issue"), dict):
        payload = payload["issue"]
    return (payload, None) if isinstance(payload, dict) else ({}, "br show JSON must be an object")


def issue_field(issue: dict[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in issue:
            return issue[name]
    return default


def drift_observation_hash(issue: dict[str, Any]) -> str:
    return sha256_text(stable_json({"title": issue_field(issue, "title", default=""), "labels": issue_field(issue, "labels", default=[])}))


def validate_path_token(root: Path, token: str, *, reject_protected: bool = False) -> list[str]:
    try:
        reject_unsafe_path(token)
    except ValueError as exc:
        return [str(exc)]
    errors = []
    if not has_glob(token):
        try:
            (root / normalize_posix(token)).resolve().relative_to(root.resolve())
        except ValueError:
            errors.append(f"path escapes repo: {token}")
    if reject_protected:
        try:
            profiles = load_profiles(root)
        except ValueError as exc:
            errors.append(str(exc))
        else:
            if is_protected_path(token, profiles):
                errors.append(f"path matches protected pattern: {token}")
    return errors


def validate_plan(root: Path, ticket: dict[str, Any], issue: dict[str, Any] | None = None) -> list[str]:
    errors: list[str] = []
    try:
        import beo_ticket
        beo_ticket.validate_plan_only(ticket)
    except Exception as exc:
        errors.append(str(exc))
    if issue and issue_field(issue, "type", "issue_type", default="atomic") in {"epic", "feature"}:
        errors.append("issue must be decomposed before validation")
    for path in allow_paths(ticket) + generated_outputs(ticket):
        errors.extend(validate_path_token(root, path, reject_protected=True))
    for path in forbid_patterns(ticket):
        errors.extend(validate_path_token(root, path))
    broad = detect_broad_globs(allow_paths(ticket))
    gates = ticket.get("human_gates") if isinstance(ticket.get("human_gates"), dict) else {}
    gate_entries = gates.get("gates") if isinstance(gates.get("gates"), list) else []
    for broad_path in broad:
        authorized = gates.get("status") == "resolved" and any(
            isinstance(gate, dict)
            and gate.get("type") == "broad_scope_authorization"
            and normalize_posix(str(gate.get("scope"))) == normalize_posix(broad_path)
            for gate in gate_entries
        )
        if not authorized:
            errors.append(f"broad glob requires matching Human Gate authorization: {broad_path}")
    return errors


def changed_files(root: Path) -> list[str]:
    from beo_check_scope import changed_files as scope_changed_files

    return scope_changed_files(root)


def validate_issue_freshness(ticket: dict[str, Any], issue: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if issue_is_closed(issue):
        errors.append("br issue is closed or terminal")
    if issue_has_blockers(issue):
        errors.append("br issue has blocking dependencies")
    issue_request = issue_field(issue, "request", "planned_request", default=None)
    request = str(ticket.get("request") or "")
    if isinstance(issue_request, str) and request and issue_request and issue_request != request:
        errors.append("br issue request differs from TICKET.json request")
    ticket_labels = set(labels_of(issue))
    if "non-atomic" in ticket_labels or "needs-decomposition" in ticket_labels:
        errors.append("br issue is marked non-atomic")
    return errors


def validate_execute_entry(ticket: dict[str, Any], state: dict[str, Any] | None = None, issue: dict[str, Any] | None = None) -> list[str]:
    errors = validate_issue_freshness(ticket, issue or {})
    state = state or {}
    if state.get("phase") != "approved":
        errors.append("execute-entry requires approved state")
    approval = state.get("approval") if isinstance(state.get("approval"), dict) else {}
    if approval.get("status") != "PASS_EXECUTE":
        errors.append("current PASS_EXECUTE approval is required")
    if state and not execution_entry_is_current(state):
        errors.append("PASS_EXECUTE approval is stale for execution entry")
    return errors


def validate_containment(root: Path, ticket: dict[str, Any]) -> list[str]:
    try:
        current_changes = changed_files(root)
    except RuntimeError as exc:
        return [f"unable to inspect working tree: {exc}"]
    result = match_allowed_paths(current_changes, allow_paths(ticket), generated_outputs(ticket), forbid_patterns(ticket))
    return result.errors


def validate_review(root: Path, ticket: dict[str, Any], state: dict[str, Any] | None = None) -> list[str]:
    errors = validate_containment(root, ticket)
    state = state or {}
    if state.get("phase") not in {"executed", "reviewing"}:
        errors.append("review-entry requires executed or reviewing state")
    execution = state.get("execution") if isinstance(state.get("execution"), dict) else {}
    recorded_changes = execution.get("changed_files", [])
    if not isinstance(recorded_changes, list):
        errors.append("execution.changed_files must be a list")
    elif recorded_changes:
        errors.extend(match_allowed_paths(recorded_changes, allow_paths(ticket), generated_outputs(ticket), forbid_patterns(ticket)).errors)
    results = execution.get("verify_results")
    if not isinstance(results, list) or not results:
        errors.append("execution verify_results are required before review")
        return errors
    passed_statuses = {"passed", "success", "ok"}
    result_by_command = {result.get("command"): result for result in results if isinstance(result, dict)}
    for command in verify_commands(ticket):
        result = result_by_command.get(command)
        if result is None:
            errors.append(f"verification command missing result: {command}")
            continue
        if str(result.get("status", "")).lower() not in passed_statuses:
            errors.append(f"verification command did not pass: {command}")
    return errors


def build_output(issue_id: str, issue: dict[str, Any], check_name: str, errors: list[str], warnings: list[str]) -> dict[str, Any]:
    return {
        "ok": not errors,
        "check": check_name,
        "issue_id": issue_id,
        "errors": errors,
        "warnings": warnings,
        "drift_observation_hash": drift_observation_hash(issue),
        "helper_version": HELPER_VERSION,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="BEO four-phase helper checks")
    parser.add_argument("--check", choices=["validate", "execute-entry", "containment", "review-entry", "status"], default="status")
    parser.add_argument("--issue", required=True)
    parser.add_argument("--root", default=".")
    args = parser.parse_args()
    root = Path(args.root).resolve()
    issue, issue_error = run_br_show(root, args.issue)
    ticket_path = ticket_path_for(root, args.issue)
    errors: list[str] = []
    warnings: list[str] = []
    if issue_error:
        errors.append(issue_error)
    try:
        ticket = read_ticket(root, args.issue).data
        state = read_state(root, args.issue)
    except Exception as exc:
        ticket = {}
        state = {}
        errors.append(str(exc))
    if ticket:
        if args.check != "status":
            errors.extend(validate_identity(root, args.issue, ticket_path, ticket, issue, ticket_path_for))
        if args.check == "validate":
            errors.extend(validate_plan(root, ticket, issue))
            errors.extend(validate_working_tree_prestate(root, ticket))
            try:
                from beo_check_approval import compute_approval_fields
                compute_approval_fields(root, ticket_path, ticket)
            except ValueError as exc:
                errors.append(str(exc))
        elif args.check == "execute-entry":
            errors.extend(validate_approval_envelope(root, ticket_path, ticket, state))
            errors.extend(validate_execute_entry(ticket, state, issue))
        elif args.check == "containment":
            errors.extend(validate_containment(root, ticket))
        elif args.check == "review-entry":
            errors.extend(validate_review(root, ticket, state))
        errors.extend(validate_runtime_events(read_events(root, args.issue), args.issue))
    print(json.dumps(build_output(args.issue, issue, args.check, errors, warnings), indent=2, sort_keys=True))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
