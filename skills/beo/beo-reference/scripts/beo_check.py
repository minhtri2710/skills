#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shlex
import subprocess
from pathlib import Path
from typing import Any

from beo_approval import allow_paths, approval_projection_hash, forbid_patterns, generated_outputs, verify_commands
from beo_io import actor_identity, file_hash, repo_head_sentinel, sha256_text, stable_json
from beo_paths import (
    detect_broad_globs,
    has_glob,
    is_protected_path,
    match_allowed_paths,
    normalize_posix,
    normalize_posix_path,
    path_matches_pattern,
    path_token_covers,
    path_tokens_overlap,
    reject_unsafe_path,
)
from beo_reservation import validate_reservation_record
from beo_state import execution_entry_is_current, read_events, read_state, validate_event_schema
from beo_ticket import read_ticket, ticket_path as ticket_path_for

HELPER_VERSION = "beo-check/v5"


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
        errors.append(f"unsupported TICKET.json version: {ticket.get('version')}")
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


def validate_runtime_events(events: Any, issue_id: str) -> list[str]:
    if events is None:
        return []
    if not isinstance(events, list):
        return ["runtime events must be a list"]
    if not events:
        return []
    errors: list[str] = []
    for event in events:
        if not isinstance(event, dict):
            errors.append("runtime event must be an object")
            continue
        try:
            validate_event_schema(event)
        except ValueError as exc:
            errors.append(str(exc))
        if event.get("issue_id") != issue_id:
            errors.append("runtime event issue_id mismatch")
    return errors


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


def run_structural_check(root: Path, ticket: dict[str, Any]) -> list[str]:
    """Run an optional scope.structural_check feedforward gate (computational).

    Declared command is exec'd via execve (shell=False). Non-zero exit is a
    validation failure that blocks PASS_EXECUTE. Absence is advisory (no error).
    Used for boundary/import/architecture checks ahead of execution.
    """
    gate = ticket.get("scope", {}).get("structural_check")
    if not isinstance(gate, dict):
        return []
    command = gate.get("command")
    if not isinstance(command, str) or not command.strip():
        return ["scope.structural_check.command is declared but empty"]
    argv = shlex.split(command)
    if not argv:
        return [f"scope.structural_check.command could not be parsed: {command}"]
    try:
        proc = subprocess.run(argv, cwd=root, shell=False, text=True, capture_output=True, check=False)
    except FileNotFoundError:
        return [f"scope.structural_check command not found: {argv[0]}"]
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "").strip()
        msg = f"scope.structural_check failed (exit {proc.returncode}): {command}"
        if detail:
            msg += f" — {detail[:300]}"
        return [msg]
    return []


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


def _result_passed(result: dict[str, Any]) -> bool:
    """A verify/gate result passes on a passing status OR exit_code 0.

    Producers differ: beo_verify/beo_run emit exit_code; some callers write a
    status field. Accept either so enforcement does not depend on an
    undocumented convention.
    """
    status = str(result.get("status", "")).lower()
    if status in {"passed", "success", "ok"}:
        return True
    exit_code = result.get("exit_code")
    return isinstance(exit_code, int) and exit_code == 0


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
    result_by_command = {result.get("command"): result for result in results if isinstance(result, dict)}
    for command in verify_commands(ticket):
        result = result_by_command.get(command)
        if result is None:
            errors.append(f"verification command missing result: {command}")
            continue
        if not _result_passed(result):
            errors.append(f"verification command did not pass: {command}")
    # Optional behaviour_gate (scope.behaviour_gate) — computationally enforced.
    gate = ticket.get("scope", {}).get("behaviour_gate")
    if isinstance(gate, dict):
        gate_command = gate.get("command")
        if isinstance(gate_command, str) and gate_command:
            result = result_by_command.get(gate_command)
            if result is None:
                errors.append(f"behaviour_gate command missing result: {gate_command}")
            elif not _result_passed(result):
                errors.append(f"behaviour_gate command did not pass: {gate_command}")
    # Strict-mode cross_check at acceptance (kernel §15): enforce only once a
    # verdict_accept route is recorded, so review-entry preconditions do not
    # fire before the reviewer has acted.
    if ticket.get("mode") == "strict":
        review = state.get("review") if isinstance(state.get("review"), dict) else {}
        if review.get("route_condition_id") == "verdict_accept":
            cross = review.get("cross_check")
            if not isinstance(cross, dict):
                errors.append("strict mode verdict_accept requires review.cross_check (kernel §15)")
            elif cross.get("verdict") != "agree":
                errors.append(f"strict mode verdict_accept requires review.cross_check.verdict == 'agree' (got {cross.get('verdict')!r})")
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
            errors.extend(run_structural_check(root, ticket))
            errors.extend(validate_working_tree_prestate(root, ticket))
            try:
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
