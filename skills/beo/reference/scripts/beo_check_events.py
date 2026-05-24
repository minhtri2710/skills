#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

from beo_utils import actor_identity, issue_field, claim_valid
from beo_registry_context import RegistryContext

def validate_runtime_events(
    ticket: dict[str, Any],
    issue_id: str,
    ctx: RegistryContext,
    root: Path | None = None,
    issue: dict[str, Any] | None = None
) -> list[str]:
    errors: list[str] = []
    active_actor = actor_identity()
    claimed_actor = str(issue_field(issue or {}, "assignee", "owner", default="") or "")
    claim_is_current = claim_valid(issue or {}) if issue is not None else None
    raw_events = ticket.get("runtime_events")
    events: list[dict[str, Any]] = []
    if raw_events is None:
        events = []
    elif not isinstance(raw_events, list):
        errors.append("runtime_events must be a list")
    else:
        for index, raw_event in enumerate(raw_events):
            if not isinstance(raw_event, dict):
                errors.append(f"runtime_events[{index}] must be an object")
                continue
            events.append(raw_event)
            
    latest_handoff: dict[str, dict[str, Any]] = {}
    latest_debug_return_index: int | None = None
    latest_review_route_index: int | None = None
    debug_return_ids: set[str] = set()
    review_route_ids: set[str] = set()
    
    required = ["id", "kind", "created_at", "owner", "issue_id", "condition_id", "basis_ref", "message"]
    review_route_conditions = {
        "repair_same_scope", "repair_rescope", "cannot_deliver", "abandoned",
        "root_cause_diagnosis_needed", "repair_budget_exceeded", "entry_blocked_execution_evidence_incomplete"
    }
    
    schema_event = ctx.schema.get("runtime_event", {})
    learning_case_types = schema_event.get("learning_case_types")

    for index, event in enumerate(events):
        prefix = f"runtime_events[{index}]"
        for field in required:
            if not event.get(field):
                errors.append(f"{prefix}.{field} is required")
        kind = event.get("kind")
        owner = event.get("owner")
        subtype = event.get("subtype")
        
        if owner and owner not in ctx.runtime_event_owners:
            errors.append(f"{prefix}.owner is not a runtime event owner: {owner}")
        if event.get("issue_id") and event.get("issue_id") != issue_id:
            errors.append(f"{prefix}.issue_id must match selected bead")
            
        if kind == "handoff":
            if subtype != "debug":
                errors.append(f"{prefix}.subtype is not registered for handoff: {subtype}")
            for field in ["caller_owner", "return_to"]:
                if not event.get(field):
                    errors.append(f"{prefix}.{field} is required for handoff")
            if event.get("return_to") != event.get("caller_owner"):
                errors.append(f"{prefix}.return_to must match caller_owner")
            if subtype == "debug":
                for field in ["caller_actor", "return_condition_id", "question"]:
                    if not event.get(field):
                        errors.append(f"{prefix}.{field} is required for debug handoff")
                if event.get("caller_owner") not in {"beo-execute", "beo-review"}:
                    errors.append(f"{prefix}.caller_owner must be beo-execute or beo-review for debug handoff")
                if issue is not None:
                    if claim_is_current is not True:
                        errors.append(f"{prefix} requires current claim by BR_ACTOR/BEO_ACTOR")
                    if active_actor and event.get("caller_actor") != active_actor:
                        errors.append(f"{prefix}.caller_actor must match BR_ACTOR/BEO_ACTOR")
                    if claimed_actor and event.get("caller_actor") != claimed_actor:
                        errors.append(f"{prefix}.caller_actor must match the current Beads claim")
            if isinstance(subtype, str):
                latest_handoff[subtype] = event
                
        elif kind == "return":
            if subtype != "debug":
                errors.append(f"{prefix}.subtype is not registered for return: {subtype}")
            expected_owner = {"debug": "beo-debug"}.get(str(subtype))
            if expected_owner and owner != expected_owner:
                errors.append(f"{prefix}.owner must be {expected_owner} for {subtype} return")
            for field in ["caller_owner", "return_to"]:
                if not event.get(field):
                    errors.append(f"{prefix}.{field} is required for return")
            handoff = latest_handoff.get(str(subtype))
            if handoff is None:
                errors.append(f"{prefix} requires a prior {subtype} handoff")
            else:
                for field in ["caller_owner", "return_to"]:
                    if event.get(field) != handoff.get(field):
                        errors.append(f"{prefix}.{field} must match latest {subtype} handoff")
            if subtype == "debug":
                for field in ["caller_actor", "return_condition_id", "diagnosis_status", "diagnosis_ref"]:
                    if not event.get(field):
                        errors.append(f"{prefix}.{field} is required for debug return")
                if event.get("diagnosis_status") not in ctx.diagnosis_statuses:
                    errors.append(f"{prefix}.diagnosis_status is not registered")
                if handoff is not None:
                    if event.get("return_condition_id") != handoff.get("return_condition_id"):
                        errors.append(f"{prefix}.return_condition_id must match latest debug handoff")
                    if event.get("caller_actor") != handoff.get("caller_actor"):
                        errors.append(f"{prefix}.caller_actor must match latest debug handoff")
                if event.get("id"):
                    debug_return_ids.add(str(event["id"]))
                if issue is not None:
                    if claim_is_current is not True:
                        errors.append(f"{prefix} requires current claim by BR_ACTOR/BEO_ACTOR")
                    if active_actor and event.get("caller_actor") != active_actor:
                        errors.append(f"{prefix}.caller_actor must match BR_ACTOR/BEO_ACTOR")
                    if claimed_actor and event.get("caller_actor") != claimed_actor:
                        errors.append(f"{prefix}.caller_actor must match the current Beads claim")
                latest_debug_return_index = index
                
        elif kind == "abandon":
            if event.get("abandon_reason") not in ctx.abandon_reasons:
                errors.append(f"{prefix}.abandon_reason is required and must be registered")
                
        elif kind == "change_request":
            if subtype not in {"scope_delta", "repair_same_scope", "repair_rescope"}:
                errors.append(f"{prefix}.subtype is not registered for change_request: {subtype}")
            if subtype == "scope_delta" and event.get("condition_id") not in {"scope_delta_required", "repair_rescope"}:
                errors.append(f"{prefix}.condition_id must route to plan for scope_delta")
            if subtype == "repair_same_scope":
                if event.get("requested_by") != "beo-review" or owner != "beo-review":
                    errors.append(f"{prefix} repair_same_scope change_request must be owned and requested by beo-review")
                for field in ["finding_refs", "prior_approval_ref", "unchanged_boundaries"]:
                    if not event.get(field):
                        errors.append(f"{prefix}.{field} is required for repair_same_scope")
            if owner == "beo-review" and event.get("condition_id") in review_route_conditions:
                latest_review_route_index = index
                if event.get("id"):
                    review_route_ids.add(str(event["id"]))
                    
        elif kind == "user_stop":
            if not event.get("reason") and not event.get("message"):
                errors.append(f"{prefix}.reason or message is required for user_stop")
                
        elif kind == "learning_candidate":
            if owner not in {"beo-review", "beo-debug"}:
                errors.append(f"{prefix}.owner must be beo-review or beo-debug for learning_candidate")
            if isinstance(learning_case_types, list) and event.get("case_type") not in learning_case_types:
                errors.append(f"{prefix}.case_type is not registered")
            source_phase = event.get("source_phase")
            if not source_phase:
                errors.append(f"{prefix}.source_phase is required for learning_candidate")
            elif source_phase not in {"beo-review", "beo-debug"}:
                errors.append(f"{prefix}.source_phase must be beo-review or beo-debug")
            elif source_phase != owner:
                errors.append(f"{prefix}.source_phase must match owner")
            source_event_id = event.get("source_event_id")
            if not source_event_id:
                errors.append(f"{prefix}.source_event_id is required for learning_candidate")
            elif not any(candidate.get("id") == source_event_id for candidate in events[:index]):
                errors.append(f"{prefix}.source_event_id must reference a prior runtime event")
            if owner == "beo-debug":
                if latest_debug_return_index is None:
                    errors.append(f"{prefix} requires a prior debug return event")
                if source_event_id and str(source_event_id) not in debug_return_ids:
                    errors.append(f"{prefix}.source_event_id must reference a prior debug return event")
            review = ticket.get("review") if isinstance(ticket.get("review"), dict) else {}
            if owner == "beo-review":
                if not review.get("verdict") and latest_review_route_index is None:
                    errors.append(f"{prefix} requires a prior review verdict or routing event")
                if source_event_id and str(source_event_id) not in review_route_ids:
                    errors.append(f"{prefix}.source_event_id must reference a prior review route event")
        elif kind not in {"user_stop", "handoff", "return", "change_request", "abandon", "learning_candidate"}:
            errors.append(f"{prefix}.kind is not registered: {kind}")
            
    return errors
