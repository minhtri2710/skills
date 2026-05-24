#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import sys
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

# Import shared BEO helpers
from beo_utils import (
    actor_identity,
    issue_field,
    claim_valid,
    load_json,
    normalize_posix,
    path_tokens_overlap,
)

# Import sub-modules
from beo_registry_context import RegistryContext
import beo_check_identity
import beo_check_scope
import beo_check_approval
import beo_check_review
import beo_check_events
import beo_command

validate_review_verdict = beo_check_review.validate_review_verdict
validate_repair_budget = beo_check_review.validate_repair_budget

HELPER_VERSION = "beo-check/v3"
PHASE_ALIASES = {
    "plan": "beo-plan",
    "validate": "beo-validate",
    "execute": "beo-execute",
    "review": "beo-review",
    "debug": "beo-debug",
    "beo-plan": "beo-plan",
    "beo-validate": "beo-validate",
    "beo-execute": "beo-execute",
    "beo-review": "beo-review",
    "beo-debug": "beo-debug",
}

# ---------------------------------------------------------------------------
# Utility & Hashing Helpers
# ---------------------------------------------------------------------------

def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"))

def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()

def file_hash(path: Path) -> str:
    if not path.exists():
        return "missing"
    h = hashlib.sha256()
    try:
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                h.update(chunk)
        return "sha256:" + h.hexdigest()
    except Exception:
        return "missing"

def strict_artifact_hashes(root: Path, ticket: dict[str, Any]) -> dict[str, str]:
    hashes = {}
    strict = ticket.get("strict", {}) if isinstance(ticket.get("strict"), dict) else {}
    artifacts = strict.get("artifacts", ["TICKET.md", "STRICT.md", "ROLLBACK.md"])
    for name in artifacts:
        path = root / ".beads" / "artifacts" / str(ticket.get("issue_id", "")) / name
        hashes[name] = file_hash(path)
    return hashes

def repo_head_sentinel(root: Path) -> str:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=False,
            capture_output=True,
            text=True,
        )
    except OSError:
        return "no-vcs"
    if result.returncode == 128:
        stderr = result.stderr.lower()
        if "not a git repository" in stderr or "outside repository" in stderr:
            return "no-vcs"
    if result.returncode != 0:
        return "git-error:" + sha256_text(result.stderr.strip() or result.stdout.strip())
    return result.stdout.strip() or "no-vcs"

def validation_subreasons(errors: list[str]) -> list[str]:
    subreasons = set()
    for error in errors:
        text = error.lower()
        if "atomic" in text or "decompose" in text or "parent/feature/epic" in text or "multi_task" in text:
            subreasons.add("fail_atomicity")
        if any(token in text for token in ["path", "scope", "glob", "forbid", "protected", "reservation", "generated_outputs", "contain", "overlap", "side_effect"]):
            subreasons.add("fail_scope")
        if any(token in text for token in ["mode", "profile", "risk_scope", "rollback_boundary", "strict", "authorization_refs", "external_side_effects", "stateful_external_systems"]):
            subreasons.add("fail_profile")
        if "human_gates" in text or "human gate" in text or "authorization gate" in text or "unresolved" in text:
            subreasons.add("fail_human_gate")
        if any(token in text for token in ["schema_version", "required", "must be", "must include", "must match", "duplicate yaml", "parse failed", "ticket issue_id", "acceptance_criteria", "done_target", "verify.commands"]):
            subreasons.add("fail_schema")
    return sorted(subreasons)

def plan_input_hash(ticket: dict[str, Any]) -> str:
    plan_fields = [
        "schema_version",
        "issue_id",
        "mode",
        "request",
        "done_target",
        "done",
        "human_gates",
        "constraints",
        "scope",
        "acceptance_criteria",
        "atomicity",
        "flow_profile",
        "posture_profile",
        "generated_outputs",
        "external_side_effects",
        "stateful_external_systems",
        "risk_scope",
        "rollback_boundary",
        "authorization_refs",
        "strict",
    ]
    scrubbed = {key: ticket[key] for key in plan_fields if key in ticket}
    return sha256_text(stable_json(scrubbed))

def extract_ticket_block(text: str) -> dict[str, Any]:
    match = re.search(r"```yaml\s+beo\.ticket\s*\n(?P<body>.*?)\n```", text, re.DOTALL)
    source = match.group("body") if match else text
    import yaml
    parsed = yaml.safe_load(source) or {}
    if isinstance(parsed, dict) and "beo.ticket" in parsed:
        parsed = parsed["beo.ticket"]
    if not isinstance(parsed, dict):
        raise ValueError("ticket YAML must be an object")
    return parsed

def resolve_ticket_meta(path: Path) -> tuple[Path, str]:
    return path, path.name

def read_state(root: Path, issue_id: str) -> dict[str, Any]:
    path = root / ".beads" / "artifacts" / issue_id / "state.json"
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as handle:
        state = json.load(handle)
    if not isinstance(state, dict):
        raise ValueError("state.json must be an object")
    return state

def read_events(root: Path, issue_id: str) -> list[dict[str, Any]]:
    path = root / ".beads" / "artifacts" / issue_id / "runtime-events.jsonl"
    events: list[dict[str, Any]] = []
    if not path.exists():
        return events
    with open(path, "r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            if not line.strip():
                continue
            event = json.loads(line)
            if not isinstance(event, dict):
                raise ValueError(f"runtime-events.jsonl line {line_number} must be an object")
            events.append(event)
    return events

def read_case_bundle(path: Path) -> dict[str, Any]:
    return load_json(path, {})

def read_ticket(path: Path, root: Path | None = None, issue_id: str | None = None) -> dict[str, Any]:
    if not path.exists():
        return {}
    content = path.read_text(encoding="utf-8")
    frontmatter = re.match(r"^---\s*\n(?P<body>.*?)\n---\s*\n", content, re.DOTALL)
    if frontmatter:
        ticket = extract_ticket_block(frontmatter.group("body"))
    elif re.search(r"```yaml\s+beo\.ticket\s*\n", content):
        ticket = extract_ticket_block(content)
    else:
        ticket = {}

    resolved_issue_id = issue_id or ticket.get("issue_id") or path.parent.name
    resolved_root = root or path.parents[3]
    ticket["state.json"] = read_state(resolved_root, resolved_issue_id)
    ticket["runtime_events"] = read_events(resolved_root, resolved_issue_id)
    return ticket

def ticket_path_for(root: Path, issue_id: str) -> Path:
    return root / ".beads" / "artifacts" / issue_id / "TICKET.md"

def command_contracts_hash(root: Path) -> str:
    path = root / "skills" / "beo" / "reference" / "registry" / "command-contracts.json"
    if not path.exists():
        path = Path(__file__).resolve().parents[1] / "registry" / "command-contracts.json"
    return file_hash(path)

def command_contracts(root: Path) -> dict[str, Any]:
    path = root / "skills" / "beo" / "reference" / "registry" / "command-contracts.json"
    if not path.exists():
        path = Path(__file__).resolve().parents[1] / "registry" / "command-contracts.json"
    return load_json(path, {})

def strict_side_effect_profiles(root: Path) -> tuple[list[str], dict[str, list[str]]]:
    schema = load_json(root / "skills" / "beo" / "reference" / "registry" / "ticket-schema.json", {})
    if not schema:
        schema = load_json(Path(__file__).resolve().parents[1] / "registry" / "ticket-schema.json", {})
    default_fields = ["target", "type", "description"]
    profiles = {}
    return default_fields, profiles

def run_br_show(root: Path, issue_id: str) -> tuple[dict[str, Any], str | None]:
    try:
        try:
            adapter = beo_command.CommandAdapter(root)
            argv = adapter.build_argv("br.show", owner="beo-validate", issue_id=issue_id)
        except Exception:
            argv = ["br", "show", issue_id, "--json"]
        proc = subprocess.run(
            argv,
            cwd=root,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
    except FileNotFoundError:
        return {}, "br executable not found"
    if proc.returncode != 0:
        return {}, f"br show failed: {proc.stderr.strip() or proc.stdout.strip()}"
    try:
        payload = json.loads(proc.stdout or "{}")
    except json.JSONDecodeError as exc:
        return {}, f"br show returned invalid JSON: {exc}"
    if isinstance(payload, list):
        matches = [item for item in payload if isinstance(item, dict) and str(issue_field(item, "id", default="")) == issue_id]
        if matches:
            payload = matches[0]
        elif len(payload) == 1 and isinstance(payload[0], dict):
            payload = payload[0]
    if isinstance(payload, dict) and isinstance(payload.get("issue"), dict):
        payload = payload["issue"]
    if not isinstance(payload, dict):
        return {}, "br show JSON must be an object"
    return payload, None

def hard_bead_snapshot(issue: dict[str, Any]) -> dict[str, Any]:
    return {
        "id": issue_field(issue, "id"),
        "type": issue_field(issue, "issue_type", "type"),
        "description": issue_field(issue, "description", "body"),
        "dependencies": issue_field(issue, "dependencies", "deps", "blocked_by", default=[]),
    }

def drift_observation(issue: dict[str, Any], ticket: dict[str, Any] = None) -> dict[str, Any]:
    ticket = ticket or {}
    return {
        "title": issue_field(issue, "title", default=""),
        "labels": sorted(labels_of(issue)),
        "assumptions": ticket.get("assumptions"),
        "non_goals": ticket.get("non_goals"),
    }

def bead_snapshot(issue: dict[str, Any]) -> dict[str, Any]:
    return {
        **hard_bead_snapshot(issue),
        **drift_observation(issue),
    }

def labels_of(issue: dict[str, Any]) -> list[str]:
    labels = issue_field(issue, "labels", "label", default=[])
    if isinstance(labels, str):
        return [item.strip() for item in labels.split(",") if item.strip()]
    if isinstance(labels, list):
        return [str(item) for item in labels]
    return []

# ---------------------------------------------------------------------------
# Scope & Posture Mapping Helpers
# ---------------------------------------------------------------------------

def path_list(value: Any) -> list[str]:
    if value is None:
        return []
    if value == "none":
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]

def scope(ticket: dict[str, Any]) -> dict[str, Any]:
    return ticket.get("scope") if isinstance(ticket.get("scope"), dict) else {}

def allow_paths(ticket: dict[str, Any]) -> list[str]:
    files = scope(ticket).get("files") if isinstance(scope(ticket).get("files"), dict) else {}
    return path_list(files.get("allow"))

def forbid_patterns(ticket: dict[str, Any]) -> list[str]:
    files = scope(ticket).get("files") if isinstance(scope(ticket).get("files"), dict) else {}
    return path_list(files.get("forbid"))

def verify_commands(ticket: dict[str, Any]) -> list[str]:
    verify = scope(ticket).get("verify") if isinstance(scope(ticket).get("verify"), dict) else {}
    return [str(cmd) for cmd in path_list(verify.get("commands"))]

def expanded_posture(ticket: dict[str, Any]) -> dict[str, Any]:
    # We load standard profiles dynamically
    ctx = RegistryContext(Path.cwd())
    posture = ticket.get("posture_profile")
    if posture is None and ticket.get("mode") == "quick":
        posture = "repo_only_low_risk"
    expanded: dict[str, Any] = {}
    profiles = ctx.profiles.get("posture_profiles", {})
    if isinstance(profiles, dict):
        profile = profiles.get(str(posture))
        if isinstance(profile, dict) and isinstance(profile.get("expands"), dict):
            expanded.update(profile["expands"])
    for key in ["generated_outputs", "external_side_effects", "stateful_external_systems", "risk_scope", "rollback_boundary"]:
        if key in ticket:
            expanded[key] = ticket[key]
    return expanded

def selected_execution_set(ticket: dict[str, Any]) -> str:
    return str(ticket.get("selected_execution_set") or "set-1")

def execution_mode(ticket: dict[str, Any]) -> str:
    if ticket.get("execution_mode"):
        return str(ticket["execution_mode"])
    return "strict" if ticket.get("mode") == "strict" else "normal"

def approval_projection(ticket: dict[str, Any], issue: dict[str, Any], bead_hash: str, contracts_hash: str) -> dict[str, Any]:
    description = str(issue_field(issue, "description", "body", default="") or "")
    dependencies = issue_field(issue, "dependencies", "deps", "blocked_by", default=[])
    posture = expanded_posture(ticket)
    strict = ticket.get("strict") if isinstance(ticket.get("strict"), dict) else {}
    artifact_hashes = strict.get("artifact_hashes") if isinstance(strict.get("artifact_hashes"), dict) else {}
    return {
        "issue_id": ticket.get("issue_id"),
        "issue_type": issue_field(issue, "issue_type", "type", default=""),
        "issue_description_hash": sha256_text(description),
        "dependency_snapshot_hash": sha256_text(stable_json(dependencies)),
        "ticket_schema_version": ticket.get("schema_version"),
        "request": ticket.get("request"),
        "done_target": ticket.get("done_target"),
        "done": ticket.get("done"),
        "human_gates": ticket.get("human_gates"),
        "constraints": ticket.get("constraints", []),
        "atomicity": ticket.get("atomicity"),
        "scope.files.allow": allow_paths(ticket),
        "scope.files.forbid": forbid_patterns(ticket),
        "generated_outputs": posture.get("generated_outputs", []),
        "external_side_effects": posture.get("external_side_effects", {"status": "none", "effects": []}),
        "stateful_external_systems": posture.get("stateful_external_systems", {"status": "none", "systems": []}),
        "risk_scope": posture.get("risk_scope"),
        "rollback_boundary": posture.get("rollback_boundary"),
        "strict.artifact_hashes.STRICT.md": artifact_hashes.get("STRICT.md"),
        "strict.artifact_hashes.ROLLBACK.md": artifact_hashes.get("ROLLBACK.md"),
        "acceptance_criteria": ticket.get("acceptance_criteria"),
        "scope.verify.commands": verify_commands(ticket),
        "flow_profile_expansion": {"selected_execution_set": selected_execution_set(ticket), "execution_mode": execution_mode(ticket)},
        "posture_profile_expansion": posture,
        "selected_execution_set": selected_execution_set(ticket),
        "execution_mode": execution_mode(ticket),
        "bead_snapshot_hash": bead_hash,
        "command_contracts_hash": contracts_hash,
    }

def approval_hash(ticket: dict[str, Any], issue: dict[str, Any], bead_hash: str, contracts_hash: str) -> str:
    return sha256_text(stable_json(approval_projection(ticket, issue, bead_hash, contracts_hash)))

def drift_observation_hash(issue: dict[str, Any], ticket: dict[str, Any] = None) -> str:
    return sha256_text(stable_json(drift_observation(issue, ticket)))

# ---------------------------------------------------------------------------
# Delegated Checker Wrappers
# ---------------------------------------------------------------------------

def validate_identity(root: Path, issue_id: str, ticket_path: Path, ticket: dict[str, Any], issue: dict[str, Any]) -> list[str]:
    ctx = RegistryContext(root)
    return beo_check_identity.validate_identity(
        root, issue_id, ticket_path, ticket, issue, ctx, ticket_path_for, read_ticket
    )

def validate_path_token(root: Path, token: str, *, pattern: bool = False, strict_mode: bool = False) -> list[str]:
    ctx = RegistryContext(root)
    errors: list[str] = []
    path = normalize_posix(token)
    if not path:
        return ["path is empty"]
    if "\x00" in path:
        errors.append(f"path contains NUL: {path}")
    if path == ".":
        errors.append("path must not be .")
    if Path(path).is_absolute():
        errors.append(f"path must be relative: {path}")
    if ".." in Path(path).parts:
        errors.append(f"path must not contain ..: {path}")
    removed_learning_tree = "skills/beo/reference" + "/learnings"
    if path == removed_learning_tree or path.startswith(removed_learning_tree + "/"):
        errors.append("path must not target removed curated learning notes")
    if not pattern:
        candidate = (root / path)
        target = candidate.resolve() if candidate.exists() else candidate.parent.resolve() / candidate.name
        try:
            target.relative_to(root.resolve())
        except ValueError:
            errors.append(f"path resolves outside repo: {path}")
    for protected in ctx.protected_patterns:
        if fnmatch.fnmatch(path, protected):
            errors.append(f"path matches protected pattern {protected}: {path}")
            break
    return errors

def active_scope_conflicts(root: Path, ticket: dict[str, Any]) -> tuple[list[str], list[str]]:
    ctx = RegistryContext(root)
    return beo_check_scope.active_scope_conflicts(
        root, ticket, ctx, allow_paths, path_list, expanded_posture, read_ticket
    )

def changed_files(root: Path, ticket: dict[str, Any]) -> list[str]:
    return beo_check_scope.changed_files(root, ticket, path_list)

def check_path_reservations(root: Path, ticket: dict[str, Any], *, require_current: bool = False) -> list[str]:
    issue_id = str(ticket.get("issue_id") or "")
    if not issue_id:
        return []
    paths = allow_paths(ticket) + path_list(expanded_posture(ticket).get("generated_outputs"))
    paths = [p for p in paths if p]
    if not paths:
        return []

    res_file = root / ".beads" / "beo-reservations.jsonl"
    if not res_file.exists():
        return ["active path reservation is required before PASS_EXECUTE"] if require_current else []

    current_time = datetime.now(timezone.utc)
    active_leases = []
    try:
        with open(res_file, "r", encoding="utf-8") as f:
            for line_number, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                if not isinstance(r, dict):
                    return [f"path reservation entry on line {line_number} must be an object"]
                if r.get("status") == "active":
                    expires_ts = r.get("expires_at")
                    if not expires_ts:
                        return [f"active path reservation on line {line_number} missing expires_at"]
                    expires_at = datetime.strptime(expires_ts, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
                    if current_time > expires_at:
                        continue
                    if not isinstance(r.get("paths"), list) or not all(isinstance(p, str) for p in r.get("paths", [])):
                        return [f"active path reservation on line {line_number} must include string paths"]
                    active_leases.append(r)
    except Exception as exc:
        return [f"path reservation read failed: {exc}"]

    errors = []
    actor = actor_identity()
    current_leases = [r for r in active_leases if r.get("issue_id") == issue_id and (not actor or r.get("actor") == actor)]
    same_issue_other_actor = [r for r in active_leases if r.get("issue_id") == issue_id and actor and r.get("actor") != actor]
    if require_current:
        if not actor:
            errors.append("active path reservation requires BR_ACTOR/BEO_ACTOR to match the claim actor")
        elif same_issue_other_actor and not current_leases:
            errors.append("active path reservation belongs to a different actor than BR_ACTOR/BEO_ACTOR")
        elif not current_leases:
            errors.append("active path reservation is required before PASS_EXECUTE")
        else:
            reserved_paths = [p for r in current_leases for p in r.get("paths", [])]
            missing_paths = [p for p in paths if not any(path_tokens_overlap(rp, p) for rp in reserved_paths)]
            if missing_paths:
                errors.append(f"active path reservation does not cover planned paths: {sorted(missing_paths)}")
    for r in active_leases:
        if r.get("issue_id") == issue_id:
            continue
        conflicted_paths = []
        for rp in r.get("paths", []):
            for cp in paths:
                if path_tokens_overlap(rp, cp):
                    conflicted_paths.append(cp)
                    break
        if conflicted_paths:
            errors.append(f"Paths {sorted(conflicted_paths)} are currently reserved by concurrent issue {r['issue_id']}")

    return errors

def declares_parallel_risk(ticket: dict[str, Any]) -> bool:
    constraints = ticket.get("constraints", [])
    if isinstance(constraints, list):
        for c in constraints:
            if isinstance(c, str) and "parallel" in c.lower():
                return True
    return False

def current_reservation_required(root: Path, ticket: dict[str, Any], validation_errors: list[str], *, final_verdict: bool = False) -> bool:
    ctx = RegistryContext(root)
    policy = ctx.profiles.get("reservation_policy", {})
    if not policy or final_verdict:
        return False
    requires = policy.get("require_current_reservation_when", [])
    if "mode_is_strict" in requires and ticket.get("mode") == "strict":
        return True
    if "parallel_execution_risk_declared" in requires and declares_parallel_risk(ticket):
        return True
    if "active_overlap_or_concurrency_risk_detected" in requires:
        if any("currently reserved by concurrent issue" in err for err in validation_errors):
            return True
        if any(beo_check_scope.is_broad_glob(path) for path in allow_paths(ticket) + path_list(expanded_posture(ticket).get("generated_outputs"))):
            return True
    return False

def validate_plan(root: Path, ticket: dict[str, Any], issue: dict[str, Any], *, require_reservation: bool = False) -> list[str]:
    ctx = RegistryContext(root)
    return beo_check_approval.validate_plan(
        root, ticket, issue, ctx,
        allow_paths, verify_commands, forbid_patterns, path_list, expanded_posture,
        validate_path_token, beo_check_scope.is_broad_glob, strict_artifact_hashes,
        strict_side_effect_profiles, check_path_reservations, current_reservation_required,
        require_reservation
    )

def approval_envelope_status(ticket: dict[str, Any], issue: dict[str, Any], plan_hash: str, bead_hash: str, contracts_hash: str, root: Path | None = None) -> str:
    ctx = RegistryContext(root or Path.cwd())
    schema_ver = ctx.schema.get("schema_version", "beo-beads/v3")
    return beo_check_approval.approval_envelope_status(
        ticket, issue, plan_hash, bead_hash, contracts_hash, ctx,
        approval_hash, repo_head_sentinel, schema_ver, HELPER_VERSION, root
    )

def approval_envelope_diagnostics(
    ticket: dict[str, Any], issue: dict[str, Any], plan_hash: str, bead_hash: str, contracts_hash: str, root: Path | None = None
) -> dict[str, Any]:
    status = approval_envelope_status(ticket, issue, plan_hash, bead_hash, contracts_hash, root)
    if status != "invalid":
        return {"status": status, "invalid_reasons": [], "next_legal_action": None}

    reasons = []
    ref = ticket.get("approval_ref") if isinstance(ticket.get("approval_ref"), dict) else {}
    expected = {
        "approval_projection_hash": approval_hash(ticket, issue, bead_hash, contracts_hash),
        "plan_input_hash": plan_hash,
        "bead_snapshot_hash": bead_hash,
        "command_contracts_hash": contracts_hash,
        "repo_head": repo_head_sentinel(root or Path.cwd()),
    }
    field_descriptions = {
        "approval_projection_hash": "Approval projection (scope, criteria, or posture) changed",
        "plan_input_hash": "Plan input fields changed after approval",
        "bead_snapshot_hash": "Beads issue description, type, or dependencies changed",
        "command_contracts_hash": "Command contracts registry was updated",
        "repo_head": "Repo HEAD changed since approval",
    }
    for key, value in expected.items():
        if ref.get(key) != value:
            reasons.append({
                "field": key,
                "expected_hash": value,
                "current_hash": ref.get(key, "missing"),
                "message": field_descriptions.get(key, f"{key} changed after approval"),
            })

    if ref.get("helper_version") != HELPER_VERSION:
        reasons.append({
            "field": "helper_version",
            "expected_hash": HELPER_VERSION,
            "current_hash": ref.get("helper_version", "missing"),
            "message": "Helper script version changed since approval",
        })

    return {
        "status": "invalid",
        "invalid_reasons": reasons,
        "next_legal_action": "route_to_beo-validate",
    }

def validate_execute(root: Path, ticket: dict[str, Any], issue: dict[str, Any], envelope_status: str) -> list[str]:
    ctx = RegistryContext(root)
    return beo_check_approval.validate_execute(
        root, ticket, issue, envelope_status, path_list, file_hash, normalize_posix
    )

def validate_review(root: Path, ticket: dict[str, Any], issue: dict[str, Any], envelope_status: str) -> list[str]:
    ctx = RegistryContext(root)
    return beo_check_review.validate_review(
        root, ticket, issue, envelope_status, ctx,
        allow_paths, verify_commands, forbid_patterns, path_list, expanded_posture,
        validate_path_token, file_hash, normalize_posix, changed_files,
        beo_check_scope.glob_match, beo_check_scope.is_allowed
    )

def validate_runtime_events(ticket: dict[str, Any], issue_id: str, root: Path | None = None, issue: dict[str, Any] | None = None) -> list[str]:
    ctx = RegistryContext(root or Path.cwd())
    return beo_check_events.validate_runtime_events(
        ticket, issue_id, ctx, root, issue
    )

def validate_phase_boundary(ticket: dict[str, Any], phase: str) -> list[str]:
    ctx = RegistryContext(Path.cwd())
    errors = []
    future = ctx.future_fields
    for key, value in ticket.items():
        if key in {"state.json", "runtime_events"}:
            continue
        # If field belongs to a future phase, flag it
        for fut_owner, fields in future.items():
            if fut_owner == phase and key in fields:
                errors.append(f"field {key} belongs to future owner {fut_owner}")
    return errors

# ---------------------------------------------------------------------------
# Status and Action Orchestrator
# ---------------------------------------------------------------------------

def determine_owner_and_action(
    ticket: dict[str, Any], issue: dict[str, Any], envelope_status: str, validation_errors: list[str]
) -> tuple[str, str, str]:
    status = issue_field(issue, "status", default="").lower()
    if not claim_valid(issue):
        return "system", "claim_required", "Issue claim is missing or belongs to another actor. Run br update --claim."
    
    if not ticket:
        return "beo-plan", "intake_required", "TICKET.md is missing. Create it from a standard template."
    
    readiness = ticket.get("readiness")
    if readiness != "PASS_EXECUTE" or envelope_status != "complete":
        if validation_errors:
            return "beo-plan", "scoping_required", "TICKET.md contains validation errors. Refine scoping."
        return "beo-validate", "approval_required", "Ticket is scoped. Run beo-validate to verify and issue PASS_EXECUTE."
        
    execution = ticket.get("execution") if isinstance(ticket.get("execution"), dict) else {}
    review = ticket.get("review") if isinstance(ticket.get("review"), dict) else {}
    
    exec_status = execution.get("status")
    verdict = review.get("verdict")
    
    if not exec_status:
        return "beo-execute", "execution_required", "PASS_EXECUTE is valid. Implement approved changes and run verification."
        
    if exec_status == "ready_for_review":
        if not verdict:
            return "beo-review", "review_required", "Execution is complete. Run beo-review to audit and record verdict."
            
    return "system", "closed", "Workflow is complete or halted waiting for manual routing."

def build_status_output(
    root: Path,
    issue_id: str,
    ticket_path: Path,
    ticket: dict[str, Any],
    issue: dict[str, Any],
    validation_errors: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    plan_hash = plan_input_hash(ticket) if ticket else file_hash(ticket_path)
    bead_hash = sha256_text(stable_json(hard_bead_snapshot(issue)))
    contracts_hash = command_contracts_hash(root)
    envelope = approval_envelope_status(ticket, issue, plan_hash, bead_hash, contracts_hash, root)
    diagnostics = approval_envelope_diagnostics(ticket, issue, plan_hash, bead_hash, contracts_hash, root)
    owner, action, guidance = determine_owner_and_action(ticket, issue, envelope, validation_errors)
    
    # Active reservation details
    reservation_status = {"status": "none", "lease": None}
    res_file = root / ".beads" / "beo-reservations.jsonl"
    if res_file.exists():
        reservation_status["status"] = "inactive"
        
    # Get artifact list
    artifact_paths = [str(ticket_path.relative_to(root))] if ticket else []
    
    return {
        "issue_id": issue_id,
        "ticket_path": str(ticket_path.relative_to(root) if ticket_path.is_relative_to(root) else ticket_path),
        "beads_status": issue_field(issue, "status"),
        "claim_actor": issue_field(issue, "assignee", "owner"),
        "claim_valid": claim_valid(issue),
        "workflow": {
            "owner": owner,
            "action": action,
            "guidance": guidance,
        },
        "approval_envelope": diagnostics,
        "artifact_paths": artifact_paths,
        "reservation_status": reservation_status,
        "errors": validation_errors,
        "warnings": warnings,
        "created_at": now(),
    }

def build_output(root: Path, issue_id: str, ticket_path: Path, ticket: dict[str, Any], issue: dict[str, Any], check: str, errors: list[str], warnings: list[str]) -> dict[str, Any]:
    plan_hash = plan_input_hash(ticket) if ticket else file_hash(ticket_path)
    bead_hash = sha256_text(stable_json(hard_bead_snapshot(issue)))
    contracts_hash = command_contracts_hash(root)
    envelope = approval_envelope_status(ticket, issue, plan_hash, bead_hash, contracts_hash, root)
    projection_hash = approval_hash(ticket, issue, bead_hash, contracts_hash) if check in {"validate", "execute", "review"} else ""
    drift_hash = drift_observation_hash(issue, ticket) if check in {"validate", "execute", "review"} else ""
    strict_hashes = strict_artifact_hashes(root, ticket) if ticket.get("mode") == "strict" else {}
    repo_head = repo_head_sentinel(root)
    
    import hashlib
    run_id = f"beo_check:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}:{hashlib.sha1(os.urandom(8)).hexdigest()[:8]}"
    subreasons = validation_subreasons(errors) if check == "validate" and errors else []
    
    return {
        "run_id": run_id,
        "helper_version": HELPER_VERSION,
        "check": check,
        "status": "failed" if errors else "passed",
        "issue_id": issue_id,
        "ticket_path": str(ticket_path.relative_to(root) if ticket_path.is_relative_to(root) else ticket_path),
        "approval_envelope_status": envelope,
        "approval_projection_hash": projection_hash,
        "drift_observation_hash": drift_hash,
        "plan_input_hash": plan_hash,
        "bead_snapshot_hash": bead_hash,
        "command_contracts_hash": contracts_hash,
        "helper_run_id": run_id,
        "strict_artifact_hashes": strict_hashes,
        "repo_head": repo_head,
        "validation_subreasons": subreasons,
        "machine_hashes": {
            "approval_projection_hash": projection_hash,
            "drift_observation_hash": drift_hash,
            "plan_input_hash": plan_hash,
            "bead_snapshot_hash": bead_hash,
            "command_contracts_hash": contracts_hash,
            "strict_artifact_hashes": strict_hashes,
            "repo_head": repo_head,
        },
        "errors": errors,
        "warnings": warnings,
        "created_at": now(),
    }

def write_output(root: Path, issue_id: str, output: dict[str, Any]) -> None:
    checks = root / ".beads" / "artifacts" / issue_id / "checks"
    checks.mkdir(parents=True, exist_ok=True)
    safe_id = output["run_id"].replace(":", "-")
    (checks / f"{safe_id}.json").write_text(json.dumps(output, indent=2, sort_keys=True) + "\n")

# ---------------------------------------------------------------------------
# CLI Entry Point
# ---------------------------------------------------------------------------

def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="BEO-on-Beads integrity checker")
    parser.add_argument("--issue", required=True)
    parser.add_argument("--ticket")
    parser.add_argument("--root", default=".")
    parser.add_argument("--check", choices=["identity", "validate", "execute", "review", "status"], required=True)
    parser.add_argument("--phase", choices=sorted(PHASE_ALIASES), help="Optional owner-boundary check for future-owned fields")
    parser.add_argument("--format", choices=["json"], default="json")
    parser.add_argument("--no-write", action="store_true", help="Do not persist helper evidence; intended for unit tests only")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    ticket_path = Path(args.ticket).resolve() if args.ticket else ticket_path_for(root, args.issue).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    try:
        ticket = read_ticket(ticket_path, root, args.issue)
    except Exception as exc:
        ticket = {}
        errors.append(f"ticket parse failed: {exc}")
    issue, issue_error = run_br_show(root, args.issue)
    if issue_error:
        errors.append(issue_error)
        issue = {"id": args.issue}

    if args.check == "status":
        status_errors = []
        if errors:
            status_errors.extend(errors)
        if ticket:
            status_errors.extend(validate_identity(root, args.issue, ticket_path, ticket, issue))
            status_errors.extend(validate_runtime_events(ticket, args.issue, root, issue))
            status_errors.extend(validate_plan(root, ticket, issue))
            overlap_errors, overlap_warnings = active_scope_conflicts(root, ticket)
            status_errors.extend(overlap_errors)
            warnings.extend(overlap_warnings)
            
            readiness = ticket.get("readiness")
            plan_hash = plan_input_hash(ticket) if ticket else file_hash(ticket_path)
            bead_hash = sha256_text(stable_json(hard_bead_snapshot(issue)))
            contracts_hash = command_contracts_hash(root)
            envelope = approval_envelope_status(ticket, issue, plan_hash, bead_hash, contracts_hash, root)
            
            if readiness == "PASS_EXECUTE":
                execution = ticket.get("execution") if isinstance(ticket.get("execution"), dict) else {}
                changed = execution.get("changed_files")
                evidence = execution.get("execution_evidence") or execution.get("prestate_refs")
                if changed or evidence:
                    status_errors.extend(validate_review(root, ticket, issue, envelope))
                else:
                    status_errors.extend(validate_execute(root, ticket, issue, envelope))
        
        output = build_status_output(root, args.issue, ticket_path, ticket, issue, status_errors, warnings)
        if not args.no_write:
            write_output(root, args.issue, output)
        print(json.dumps(output, indent=2, sort_keys=True))
        return 1 if status_errors else 0

    if ticket:
        errors.extend(validate_identity(root, args.issue, ticket_path, ticket, issue))
        errors.extend(validate_runtime_events(ticket, args.issue, root, issue))
        if args.phase:
            errors.extend(validate_phase_boundary(ticket, PHASE_ALIASES[args.phase]))
    if args.check in {"validate", "execute", "review"} and ticket:
        errors.extend(validate_plan(root, ticket, issue))
    if args.check == "validate" and ticket:
        if not claim_valid(issue):
            errors.append("br claim for current actor/session is missing or invalid")
        overlap_errors, overlap_warnings = active_scope_conflicts(root, ticket)
        errors.extend(overlap_errors)
        warnings.extend(overlap_warnings)
    output = build_output(root, args.issue, ticket_path, ticket, issue, args.check, [], warnings)
    if args.check == "execute" and ticket:
        errors.extend(validate_execute(root, ticket, issue, output["approval_envelope_status"]))
    elif args.check == "review" and ticket:
        errors.extend(validate_review(root, ticket, issue, output["approval_envelope_status"]))
    output = build_output(root, args.issue, ticket_path, ticket, issue, args.check, errors, warnings)
    if not args.no_write:
        write_output(root, args.issue, output)
    print(json.dumps(output, indent=2, sort_keys=True))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
