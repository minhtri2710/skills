#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

from beo_utils import claim_valid
from beo_registry_context import RegistryContext
from beo_check_identity import is_parent_or_non_atomic

def validate_plan(
    root: Path,
    ticket: dict[str, Any],
    issue: dict[str, Any],
    ctx: RegistryContext,
    allow_paths_func: Any,
    verify_commands_func: Any,
    forbid_patterns_func: Any,
    path_list_func: Any,
    expanded_posture_func: Any,
    validate_path_token_func: Any,
    is_broad_glob_func: Any,
    strict_artifact_hashes_func: Any,
    strict_side_effect_profiles_func: Any,
    check_path_reservations_func: Any,
    current_reservation_required_func: Any,
    require_reservation: bool = False
) -> list[str]:
    errors: list[str] = []
    
    if ticket.get("mode") not in ctx.modes:
        errors.append(f"mode must be one of {sorted(ctx.modes)}")
        
    gates = ticket.get("human_gates")
    if not isinstance(gates, dict):
        errors.append("human_gates must be an object")
    elif gates.get("status") == "unresolved":
        errors.append("Human Gates are unresolved")
    elif gates.get("status") not in {"not_applicable", "resolved"}:
        errors.append("human_gates.status must be not_applicable, resolved, or unresolved")
        
    if isinstance(gates, dict):
        for index, gate in enumerate(gates.get("gates", []) if isinstance(gates.get("gates"), list) else []):
            if isinstance(gate, dict) and gate.get("type") in {"authorization", "external_side_effect_authorization", "stateful_system_authorization"}:
                for field in ["scope", "approver_handle"]:
                    if not gate.get(field):
                        errors.append(f"human_gates.gates[{index}].{field} is required for authorization gates")
                if not gate.get("valid_for_issue_id") and not gate.get("expires_at"):
                    errors.append(f"human_gates.gates[{index}] must include valid_for_issue_id or expires_at")
                    
    if is_parent_or_non_atomic(issue, ticket):
        errors.append("selected bead is not atomic; decompose before approval")
        
    atomicity = ticket.get("atomicity") if isinstance(ticket.get("atomicity"), dict) else {}
    if atomicity.get("decision") != "atomic":
        errors.append("atomicity.decision must be atomic before PASS_EXECUTE")
    if not atomicity.get("reason"):
        errors.append("atomicity.reason is required")
    if atomicity.get("rejects_multi_task") is not True:
        errors.append("atomicity.rejects_multi_task must be true")
        
    if not ticket.get("done_target"):
        errors.append("done_target is required for one atomic completion target")
    if not isinstance(ticket.get("done"), list) or not ticket.get("done"):
        errors.append("done must be a non-empty list of subcriteria for done_target")
        
    allowed_p = allow_paths_func(ticket)
    if not allowed_p:
        errors.append("scope.files.allow is required")
    if not verify_commands_func(ticket):
        errors.append("scope.verify.commands is required")
    if not ticket.get("acceptance_criteria"):
        errors.append("acceptance_criteria is required")
        
    strict_mode = ticket.get("mode") == "strict"
    for path in allowed_p:
        errors.extend(validate_path_token_func(root, path, strict_mode=strict_mode))
        if is_broad_glob_func(path):
            gate_resolved = isinstance(gates, dict) and gates.get("status") == "resolved"
            gate_list = gates.get("gates", []) if isinstance(gates, dict) else []
            authorized = gate_resolved and any(
                isinstance(g, dict) and g.get("type") == "authorization" and 
                (path in str(g.get("message") or "") or "glob" in str(g.get("message") or "").lower())
                for g in gate_list
            )
            if not authorized:
                errors.append(f"broad glob requires resolved human authorization gate mentioning the glob: {path}")

    posture = expanded_posture_func(ticket)
    for path in path_list_func(posture.get("generated_outputs")):
        errors.extend(validate_path_token_func(root, path, strict_mode=strict_mode))
        if is_broad_glob_func(path):
            gate_resolved = isinstance(gates, dict) and gates.get("status") == "resolved"
            gate_list = gates.get("gates", []) if isinstance(gates, dict) else []
            authorized = gate_resolved and any(
                isinstance(g, dict) and g.get("type") == "authorization" and 
                (path in str(g.get("message") or "") or "glob" in str(g.get("message") or "").lower())
                for g in gate_list
            )
            if not authorized:
                errors.append(f"broad glob in generated_outputs requires resolved human authorization gate: {path}")

    for pattern in forbid_patterns_func(ticket):
        errors.extend(validate_path_token_func(root, pattern, pattern=True, strict_mode=True))
        
    if not posture.get("risk_scope"):
        errors.append("risk_scope is required or must be profile-expanded")
    if not posture.get("rollback_boundary"):
        errors.append("rollback_boundary is required or must be profile-expanded")
        
    external = posture.get("external_side_effects")
    stateful = posture.get("stateful_external_systems")
    has_external = isinstance(external, dict) and external.get("status") == "declared"
    has_stateful = isinstance(stateful, dict) and stateful.get("status") == "declared"

    if has_stateful:
        systems = stateful.get("systems", []) if isinstance(stateful, dict) else []
        if not systems:
            errors.append("stateful_external_systems.systems must be a non-empty list when status is declared")
        effects = external.get("effects", []) if isinstance(external, dict) else []
        if not effects:
            errors.append("external_side_effects.effects must be declared when stateful systems are declared")
        effect_targets = {str(e.get("target")) for e in (effects if isinstance(effects, list) else []) if isinstance(e, dict) and e.get("target")}
        for index, system in enumerate(systems if isinstance(systems, list) else []):
            if not isinstance(system, dict):
                continue
            effect_ref = system.get("effect_ref")
            if not effect_ref:
                errors.append(f"stateful_external_systems.systems[{index}].effect_ref is required")
                continue
            if str(effect_ref) not in effect_targets:
                errors.append(f"stateful_external_systems.systems[{index}].effect_ref '{effect_ref}' not found in external_side_effects.effects targets")

    commands = "\n".join(verify_commands_func(ticket))
    detected_side_effect = bool(ctx.side_effect_patterns.search(commands))
    if ticket.get("mode") in {"quick", "standard"} and (has_external or has_stateful or detected_side_effect):
        errors.append("quick/standard mode cannot include external side effects or stateful system mutations")
        
    if ticket.get("mode") == "strict":
        strict = ticket.get("strict") if isinstance(ticket.get("strict"), dict) else {}
        if not strict.get("reason"):
            errors.append("strict.reason is required in strict mode")
        if not ticket.get("authorization_refs") and not strict.get("authorization_refs"):
            errors.append("authorization_refs are required in strict mode")
        declared_hashes = strict.get("artifact_hashes") if isinstance(strict.get("artifact_hashes"), dict) else {}
        for name, current_hash in strict_artifact_hashes_func(root, ticket).items():
            if current_hash == "missing":
                errors.append(f"{name} is required in strict mode")
            elif declared_hashes.get(name) != current_hash:
                errors.append(f"strict.artifact_hashes.{name} must match current {name}")
        default_fields, profiles = strict_side_effect_profiles_func(root)
        effects = external.get("effects") if isinstance(external, dict) else []
        for index, effect in enumerate(effects if isinstance(effects, list) else []):
            if not isinstance(effect, dict):
                errors.append(f"external_side_effects.effects[{index}] must be an object")
                continue
            effect_type = str(effect.get("type") or "")
            required_fields = profiles.get(effect_type, default_fields)
            if not required_fields:
                errors.append("strict side-effect profile registry is unavailable")
                continue
            for field in required_fields:
                if not effect.get(field):
                    errors.append(f"external_side_effects.effects[{index}].{field} is required for {effect_type or 'unknown'}")
                    
    review = ticket.get("review") if isinstance(ticket.get("review"), dict) else {}
    final_verdict = review.get("verdict") in {"accept", "abandoned", "cannot_deliver"}
    reservation_errors = check_path_reservations_func(root, ticket, require_current=False)
    require_current_reservation = require_reservation or current_reservation_required_func(root, ticket, reservation_errors, final_verdict=final_verdict)
    if require_current_reservation:
        reservation_errors = check_path_reservations_func(root, ticket, require_current=True)
    errors.extend(reservation_errors)
    return errors

def approval_envelope_status(
    ticket: dict[str, Any],
    issue: dict[str, Any],
    plan_hash: str,
    bead_hash: str,
    contracts_hash: str,
    ctx: RegistryContext,
    approval_hash_func: Any,
    repo_head_sentinel_func: Any,
    schema_version_val: str,
    helper_version_val: str,
    root: Path | None = None
) -> str:
    ref = ticket.get("approval_ref") if isinstance(ticket.get("approval_ref"), dict) else {}
    integrity = ticket.get("integrity") if isinstance(ticket.get("integrity"), dict) else {}
    if ticket.get("readiness") != "PASS_EXECUTE" or not ref or not integrity:
        return "incomplete"
    required_ticket = ["selected_execution_set", "execution_mode"]
    required_ref = [
        "id",
        "approved_by_owner",
        "approved_at",
        "issue_id",
        "ticket_schema_version",
        "approval_projection_rule",
        "approval_projection_hash",
        "plan_input_hash",
        "bead_snapshot_hash",
        "command_contracts_hash",
        "helper_version",
        "helper_run_id",
        "repo_head",
    ]
    required_integrity = ["status", "evidence_ref"]
    if any(not ticket.get(field) for field in required_ticket):
        return "incomplete"
    if any(not ref.get(field) for field in required_ref):
        return "incomplete"
    if any(not integrity.get(field) for field in required_integrity):
        return "incomplete"
    if ref.get("approved_by_owner") != "beo-validate" or integrity.get("status") != "verified":
        return "invalid"
    if ref.get("issue_id") != ticket.get("issue_id") or ref.get("ticket_schema_version") != schema_version_val:
        return "invalid"
    if ref.get("approval_projection_rule") != "plan_input_execution_binding":
        return "invalid"
    if ref.get("helper_version") != helper_version_val:
        return "invalid"
    expected = {
        "approval_projection_hash": approval_hash_func(ticket, issue, bead_hash, contracts_hash),
        "plan_input_hash": plan_hash,
        "bead_snapshot_hash": bead_hash,
        "command_contracts_hash": contracts_hash,
    }
    for key, value in expected.items():
        if ref.get(key) != value:
            return "invalid"
    if ref.get("repo_head") != repo_head_sentinel_func(root or Path.cwd()):
        return "invalid"
    return "complete"

def validate_execute(
    root: Path,
    ticket: dict[str, Any],
    issue: dict[str, Any],
    envelope_status: str,
    path_list_func: Any,
    file_hash_func: Any,
    normalize_posix_func: Any
) -> list[str]:
    errors: list[str] = []
    if envelope_status != "complete":
        errors.append("approval envelope is not complete for execute")
    if not claim_valid(issue):
        errors.append("br claim for current actor/session is missing or invalid")
    execution = ticket.get("execution") if isinstance(ticket.get("execution"), dict) else {}
    prestate = execution.get("prestate_refs") if isinstance(execution.get("prestate_refs"), dict) else None
    changed = path_list_func(execution.get("changed_files"))
    if changed and not prestate:
        errors.append("execution.prestate_refs is required when changed_files are recorded")
    def strip_prefix(h: Any) -> str:
        if isinstance(h, str) and h.startswith("sha256:"):
            return h[7:]
        return str(h)

    if prestate:
        files = prestate.get("files") if isinstance(prestate.get("files"), dict) else {}
        for path, recorded in files.items():
            normalized = normalize_posix_func(path)
            current = file_hash_func(root / normalized)
            if isinstance(recorded, dict):
                kind = recorded.get("kind")
                recorded_hash = recorded.get("hash")
                if kind not in {"existing", "expected_missing", "generated_declared"}:
                    errors.append(f"execution.prestate_refs.files.{path}.kind is invalid")
                    continue
                if not recorded_hash:
                    errors.append(f"execution.prestate_refs.files.{path}.hash is required")
                    continue
                if kind == "existing" and recorded_hash == "missing":
                    errors.append(f"execution.prestate_refs.files.{path}.hash must not be missing for existing")
                if recorded_hash == "missing" and current != "missing" and normalized not in changed:
                    errors.append(f"unexplained prestate drift before mutation: {path}")
                elif recorded_hash != "missing" and current != strip_prefix(recorded_hash) and normalized not in changed:
                    errors.append(f"unexplained prestate drift before mutation: {path}")
            elif recorded == "missing" and current != "missing" and normalized not in changed:
                errors.append(f"unexplained prestate drift before mutation: {path}")
            elif recorded != "missing" and current != strip_prefix(recorded) and normalized not in changed:
                errors.append(f"unexplained prestate drift before mutation: {path}")
        recorded_paths = {normalize_posix_func(path) for path in files}
        for changed_path in changed:
            if normalize_posix_func(changed_path) not in recorded_paths:
                errors.append(f"changed file is missing prestate hash: {changed_path}")
    return errors
