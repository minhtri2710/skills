#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

from beo_registry_context import RegistryContext
from beo_check_approval import validate_execute

def validate_repair_budget(ticket: dict[str, Any], review: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    verdict = review.get("verdict")
    if verdict not in {"repair_same_scope", "repair_rescope"}:
        return errors

    mode = ticket.get("mode")
    mode_budgets = {"quick": 1, "standard": 2}
    if mode not in mode_budgets:
        return errors

    repair_counter = review.get("repair_counter", 0)
    mode_budget = mode_budgets[mode]
    if isinstance(repair_counter, bool) or not isinstance(repair_counter, int):
        errors.append("review.repair_counter must be an integer")
        return errors
    if repair_counter < 0:
        errors.append("review.repair_counter must be non-negative")
        return errors

    if repair_counter >= mode_budget:
        errors.append(f"repair_counter {repair_counter} >= mode_budget {mode_budget}; should route repair_budget_exceeded instead of {verdict}")

    return errors

def validate_review_verdict(review: dict[str, Any], ctx: RegistryContext) -> list[str]:
    errors: list[str] = []
    verdict = review.get("verdict")
    
    review_verdict_allowed = ctx.schema.get("review_verdict", ["accept", "repair_same_scope", "repair_rescope", "cannot_deliver", "abandoned"])
    if verdict and verdict not in review_verdict_allowed:
        errors.append(f"review.verdict is not legal: {verdict}")
        
    reason_class = review.get("reason_class")
    review_reason_class_allowed = ctx.schema.get("review_reason_class", ["user_owned", "unsafe", "not_deliverable"])
    if reason_class and reason_class not in review_reason_class_allowed:
        errors.append(f"review.reason_class is not legal: {reason_class}")
        
    if verdict == "cannot_deliver":
        if reason_class not in review_reason_class_allowed:
            errors.append("review.reason_class is required for cannot_deliver verdict")
        cannot_deliver_reason = review.get("cannot_deliver_reason")
        
        registered_reasons_obj = ctx.schema.get("cannot_deliver_reasons", {})
        registered_reasons = registered_reasons_obj.get("reasons", ["scope_invalid", "tool_missing", "unavailable_dependency", "unsafe_environment", "user_owned"])
        if not cannot_deliver_reason:
            errors.append("review.cannot_deliver_reason is required for cannot_deliver verdict")
        elif cannot_deliver_reason not in registered_reasons:
            errors.append(f"review.cannot_deliver_reason must be one of {', '.join(registered_reasons)}: got {cannot_deliver_reason}")
            
    return errors

def validate_review(
    root: Path,
    ticket: dict[str, Any],
    issue: dict[str, Any],
    envelope_status: str,
    ctx: RegistryContext,
    allow_paths_func: Any,
    verify_commands_func: Any,
    forbid_patterns_func: Any,
    path_list_func: Any,
    expanded_posture_func: Any,
    validate_path_token_func: Any,
    file_hash_func: Any,
    normalize_posix_func: Any,
    changed_files_func: Any,
    glob_match_func: Any,
    is_allowed_func: Any
) -> list[str]:
    errors = validate_execute(root, ticket, issue, envelope_status, path_list_func, file_hash_func, normalize_posix_func)
    execution = ticket.get("execution") if isinstance(ticket.get("execution"), dict) else {}
    review = ticket.get("review") if isinstance(ticket.get("review"), dict) else {}
    verdict = review.get("verdict")
    strict_accept_check = verdict in {None, "", "accept"}
    
    if execution.get("status") != "ready_for_review":
        errors.append("execution.status must be ready_for_review")
        
    verification = execution.get("verification") if isinstance(execution.get("verification"), list) else []
    if not verification:
        errors.append("execution.verification evidence is required")
        
    if strict_accept_check:
        for item in verification:
            if not isinstance(item, dict) or item.get("status") != "passed":
                errors.append("all required verification evidence must be passed before accept")
                
    generated = path_list_func(expanded_posture_func(ticket).get("generated_outputs"))
    try:
        c_files = changed_files_func(root, ticket, path_list_func)
    except Exception as exc:
        errors.append(f"VCS changed files verification failed: {exc}")
        c_files = []
        
    for changed in c_files:
        for err in validate_path_token_func(root, changed, strict_mode=ticket.get("mode") == "strict"):
            errors.append(f"changed file {err}")
        if any(glob_match_func(changed, pattern) for pattern in forbid_patterns_func(ticket)):
            errors.append(f"changed file matches forbidden path: {changed}")
        if not is_allowed_func(changed, allow_paths_func(ticket), generated):
            errors.append(f"changed file outside approved scope: {changed}")
            
    errors.extend(validate_review_verdict(review, ctx))
    errors.extend(validate_repair_budget(ticket, review))
    
    if review.get("verdict") == "accept":
        for finding in review.get("findings", []) if isinstance(review.get("findings"), list) else []:
            if isinstance(finding, dict) and finding.get("severity") == "blocking":
                errors.append("blocking findings cannot produce accept verdict")
                
    return errors
