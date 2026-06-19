#!/usr/bin/env python3
"""State.json and runtime-events.jsonl validation for BEO.

This module owns the contract-level validation logic: enums, field
allow-lists, payload contracts, and harness-proposal write authority.

It is intentionally free of any I/O. File reads/writes live in
``beo_state_io``; locked updates and event appends live in
``beo_state_update``.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PHASES = {"planned", "approved", "executing", "executed", "reviewing", "reviewed", "blocked", "abandoned"}
APPROVAL_STATUSES = {"pending", "PASS_EXECUTE", "failed", "blocked", "stale"}
REVIEW_VERDICTS = {None, "accept", "repair_same_scope", "repair_rescope", "cannot_deliver", "abandoned"}
REVIEW_FINDING_SEVERITIES = {"blocker", "major", "minor", "info"}
REVIEW_FINDING_CATEGORIES = {"scope", "verification", "done_criteria", "safety", "evidence", "regression", "process"}
REVIEW_FINDING_ROUTES = {"repair_same_scope", "repair_rescope", "cannot_deliver", "root_cause_diagnosis_needed", "none"}


# Per-field authority for harness_proposal writes.
# Key: field name. Value: set of actors allowed to write that field.
# Three actors (beo-execute, beo-review, beo-author) claim harness_proposal
# in artifact_write_authorities; status is restricted to beo-author only.
HARNESS_PROPOSAL_FIELD_AUTHORITY: dict[str, set[str]] = {
    "version": {"beo-execute", "beo-review", "beo-author"},
    "proposal_id": {"beo-execute", "beo-review", "beo-author"},
    "source_issue_id": {"beo-execute", "beo-review", "beo-author"},
    "target": {"beo-execute", "beo-review", "beo-author"},
    "change_type": {"beo-execute", "beo-review", "beo-author"},
    "rationale": {"beo-execute", "beo-review", "beo-author"},
    "proposed_diff": {"beo-execute", "beo-review", "beo-author"},
    "safety_note": {"beo-execute", "beo-review", "beo-author"},
    "status": {"beo-author"},
}


def _reject_unknown_fields(mapping: dict[str, Any], allowed: set[str], field: str) -> None:
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        raise ValueError(f"{field} contains unknown field(s): {', '.join(unknown)}")


def _validate_optional_string(value: Any, field: str) -> None:
    if value is not None and not isinstance(value, str):
        raise ValueError(f"{field} must be a string or null")


def _validate_list(value: Any, field: str) -> None:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")


def _validate_safe_path_list(value: Any, field: str) -> None:
    _validate_list(value, field)
    # Lazy import to avoid a hard cycle with beo_paths at module load.
    from beo_paths import reject_unsafe_path

    for entry in value:
        if not isinstance(entry, str):
            raise ValueError(f"{field} entries must be strings")
        try:
            reject_unsafe_path(entry)
        except ValueError as exc:
            raise ValueError(f"{field} contains unsafe path: {exc}") from exc


def _load_pipeline() -> dict[str, Any]:
    pipeline_path = Path(__file__).resolve().parents[1] / "registry" / "pipeline.json"
    try:
        return json.loads(pipeline_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"failed to load pipeline.json: {exc}") from exc


def _load_state_schema() -> dict[str, Any]:
    schema_path = Path(__file__).resolve().parents[1] / "registry" / "state.schema.json"
    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"failed to load state.schema.json: {exc}") from exc
    if not isinstance(schema, dict):
        raise ValueError("state.schema.json must be a JSON object")
    return schema


def _approval_failure_categories() -> set[Any]:
    schema = _load_state_schema()
    try:
        values = schema["properties"]["approval"]["properties"]["failure_category"]["enum"]
    except KeyError as exc:
        raise ValueError("state.schema.json lacks approval.failure_category enum") from exc
    if not isinstance(values, list):
        raise ValueError("state.schema.json approval.failure_category enum must be a list")
    return set(values)


def validate_state(state: dict[str, Any], issue_id: str | None = None) -> None:
    required = {"version", "issue_id", "phase", "phase_sequence_id", "approval", "execution", "review", "metadata"}
    missing = sorted(required - set(state))
    if missing:
        raise ValueError(f"state.json missing required field(s): {', '.join(missing)}")
    _reject_unknown_fields(state, required, "state.json")
    if state.get("version") != 1:
        raise ValueError("state.json version must be 1")
    if issue_id is not None and state.get("issue_id") != issue_id:
        raise ValueError("state.json issue_id mismatch")
    if state.get("phase") not in PHASES:
        raise ValueError(f"invalid state phase: {state.get('phase')}")
    if type(state.get("phase_sequence_id")) is not int or state["phase_sequence_id"] < 1:
        raise ValueError("phase_sequence_id must be a positive integer")
    approval = state.get("approval")
    execution = state.get("execution")
    review = state.get("review")
    metadata = state.get("metadata")
    approval_fields = {"status", "approved_by", "actor", "ticket_file_hash", "approval_projection_hash", "repo_head", "prestate", "failure_category", "approved_phase_sequence_id"}
    execution_fields = {"actor", "started_at", "completed_at", "changed_files", "verify_results", "evidence_refs", "trace_tier", "interventions"}
    review_fields = {"actor", "verdict", "route_condition_id", "findings", "done_criteria_coverage", "repair_count", "closed_in_br", "reviewed_by"}
    metadata_fields = {"last_owner", "updated_at"}
    if not isinstance(approval, dict) or approval.get("status") not in APPROVAL_STATUSES:
        raise ValueError("approval.status is invalid")
    _reject_unknown_fields(approval, approval_fields, "approval")
    missing_approval = sorted(approval_fields - set(approval))
    if missing_approval:
        raise ValueError(f"approval missing required field(s): {', '.join(missing_approval)}")
    for field in ["approved_by", "actor", "ticket_file_hash", "approval_projection_hash", "repo_head", "failure_category"]:
        _validate_optional_string(approval.get(field), f"approval.{field}")
    if not isinstance(approval.get("prestate"), dict):
        raise ValueError("approval.prestate must be an object")

    valid_failures = _approval_failure_categories()
    if approval.get("failure_category") not in valid_failures:
        raise ValueError(f"invalid approval.failure_category: {approval.get('failure_category')}")

    sequence = approval.get("approved_phase_sequence_id")
    if sequence is not None and (type(sequence) is not int or sequence < 1):
        raise ValueError("approval.approved_phase_sequence_id must be a positive integer or null")
    if not isinstance(execution, dict):
        raise ValueError("execution must be an object")
    _reject_unknown_fields(execution, execution_fields, "execution")
    missing_execution = sorted(execution_fields - set(execution))
    if missing_execution:
        raise ValueError(f"execution missing required field(s): {', '.join(missing_execution)}")
    for field in ["actor", "started_at", "completed_at", "trace_tier"]:
        _validate_optional_string(execution.get(field), f"execution.{field}")
    trace_tier_value = execution.get("trace_tier")
    if trace_tier_value is not None and trace_tier_value not in {"minimal", "standard", "detailed"}:
        raise ValueError("execution.trace_tier must be one of minimal, standard, detailed or null")
    _validate_safe_path_list(execution.get("changed_files"), "execution.changed_files")
    _validate_list(execution.get("verify_results"), "execution.verify_results")
    _validate_safe_path_list(execution.get("evidence_refs"), "execution.evidence_refs")
    if not all(isinstance(result, dict) for result in execution.get("verify_results", [])):
        raise ValueError("execution.verify_results entries must be objects")
    _validate_list(execution.get("interventions"), "execution.interventions")
    for index, intervention in enumerate(execution.get("interventions", [])):
        if not isinstance(intervention, dict):
            raise ValueError(f"execution.interventions[{index}] must be an object")
        intervention_keys = set(intervention.keys())
        allowed_keys = {"type", "source", "impact", "description", "recorded_at", "trace_id", "story_id"}
        unknown = sorted(intervention_keys - allowed_keys)
        if unknown:
            raise ValueError(f"execution.interventions[{index}] contains unknown field(s): {', '.join(unknown)}")
        intervention_type = intervention.get("type")
        if intervention_type not in {"human", "reviewer", "ci", "agent"}:
            raise ValueError(f"execution.interventions[{index}].type is invalid: {intervention_type}")
        impact = intervention.get("impact")
        if impact not in {"informational", "blocking", "helpful"}:
            raise ValueError(f"execution.interventions[{index}].impact is invalid: {impact}")
        for string_field in ("source", "description", "recorded_at"):
            value = intervention.get(string_field)
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"execution.interventions[{index}].{string_field} must be a non-empty string")
    if not isinstance(review, dict):
        raise ValueError("review must be an object")
    _reject_unknown_fields(review, review_fields, "review")
    missing_review = sorted(review_fields - set(review))
    if missing_review:
        raise ValueError(f"review missing required field(s): {', '.join(missing_review)}")
    _validate_optional_string(review.get("actor"), "review.actor")
    reviewed_by = review.get("reviewed_by")
    if reviewed_by not in {"beo-execute", "beo-review"}:
        raise ValueError("review.reviewed_by must be 'beo-execute' or 'beo-review'")
    _validate_list(review.get("findings"), "review.findings")
    for index, finding in enumerate(review.get("findings", [])):
        if not isinstance(finding, dict):
            raise ValueError("review.findings entries must be objects")
        finding_fields = {"severity", "category", "message", "evidence_refs", "recommended_route"}
        _reject_unknown_fields(finding, finding_fields, f"review.findings[{index}]")
        missing_keys = sorted(finding_fields - set(finding))
        if missing_keys:
            raise ValueError(f"review.findings[{index}] missing required field(s): {', '.join(missing_keys)}")
        for key in ["message"]:
            if not isinstance(finding.get(key), str) or not finding[key].strip():
                raise ValueError(f"review.findings[{index}].{key} must be a non-empty string")
        if finding.get("severity") not in REVIEW_FINDING_SEVERITIES:
            raise ValueError(f"review.findings[{index}].severity is invalid: {finding.get('severity')}")
        if finding.get("category") not in REVIEW_FINDING_CATEGORIES:
            raise ValueError(f"review.findings[{index}].category is invalid: {finding.get('category')}")
        if finding.get("recommended_route") not in REVIEW_FINDING_ROUTES:
            raise ValueError(f"review.findings[{index}].recommended_route is invalid: {finding.get('recommended_route')}")
        if finding.get("severity") in {"blocker", "major"} and finding.get("recommended_route") == "none":
            raise ValueError(f"review.findings[{index}].recommended_route cannot be none for blocker/major findings")
        _validate_safe_path_list(finding.get("evidence_refs"), f"review.findings[{index}].evidence_refs")

    _validate_list(review.get("done_criteria_coverage"), "review.done_criteria_coverage")
    for index, item in enumerate(review.get("done_criteria_coverage", [])):
        if not isinstance(item, dict):
            raise ValueError("review.done_criteria_coverage entries must be objects")
        coverage_fields = {"criterion", "status", "evidence_refs"}
        _reject_unknown_fields(item, coverage_fields, f"review.done_criteria_coverage[{index}]")
        missing_keys = sorted(coverage_fields - set(item))
        if missing_keys:
            raise ValueError(f"review.done_criteria_coverage[{index}] missing field(s): {', '.join(missing_keys)}")
        if item.get("status") not in {"covered", "not_covered", "not_applicable"}:
            raise ValueError(f"review.done_criteria_coverage[{index}] has invalid status: {item.get('status')}")
        if not isinstance(item.get("criterion"), str) or not item["criterion"].strip():
            raise ValueError(f"review.done_criteria_coverage[{index}].criterion must be a non-empty string")
        _validate_safe_path_list(item.get("evidence_refs"), f"review.done_criteria_coverage[{index}].evidence_refs")

    if type(review.get("repair_count")) is not int or review["repair_count"] < 0:
        raise ValueError("review.repair_count must be a non-negative integer")
    if not isinstance(review.get("closed_in_br"), bool):
        raise ValueError("review.closed_in_br must be a boolean")
    if review.get("verdict") not in REVIEW_VERDICTS:
        raise ValueError("review.verdict is invalid")
    route_condition = review.get("route_condition_id")
    verdict = review.get("verdict")

    pipeline = _load_pipeline()
    mapping = pipeline.get("review_route_mapping", {})
    verdict_to_condition = mapping.get("verdict_to_condition", {})
    null_verdict_conditions = set(mapping.get("null_verdict_conditions", []))

    valid_conditions = {t["condition_id"] for t in pipeline.get("transitions", [])} | {None}
    if route_condition not in valid_conditions:
        raise ValueError(f"review.route_condition_id is invalid: {route_condition}")

    if verdict is not None:
        expected_condition = verdict_to_condition.get(verdict)
        if expected_condition is None:
            raise ValueError(f"unknown verdict in pipeline: {verdict}")
        if route_condition != expected_condition:
            raise ValueError(f"{verdict} verdict must route through {expected_condition}, got {route_condition}")
    else:
        if route_condition not in null_verdict_conditions and route_condition is not None:
            raise ValueError(f"{route_condition} route condition requires a non-null verdict")

    if route_condition == "verdict_accept" and not review.get("closed_in_br"):
        raise ValueError("review.closed_in_br must be true for verdict_accept")
    if review.get("closed_in_br"):
        if route_condition != "verdict_accept":
            raise ValueError(f"review.closed_in_br cannot be true for route: {route_condition}")

    if not isinstance(metadata, dict):
        raise ValueError("metadata must be an object")
    _reject_unknown_fields(metadata, metadata_fields, "metadata")
    missing_metadata = sorted(metadata_fields - set(metadata))
    if missing_metadata:
        raise ValueError(f"metadata missing required field(s): {', '.join(missing_metadata)}")
    _validate_optional_string(metadata.get("last_owner"), "metadata.last_owner")
    _validate_optional_string(metadata.get("updated_at"), "metadata.updated_at")


def _validate_payload_property(kind: str, field: str, value: Any, schema: dict[str, Any]) -> None:
    expected_type = schema.get("type")
    if expected_type == "string":
        if not isinstance(value, str):
            raise ValueError(f"{kind}.{field} must be a string")
        if schema.get("minLength", 0) and len(value) < schema["minLength"]:
            raise ValueError(f"{kind}.{field} must be a non-empty string")
    elif expected_type == "array":
        if schema.get("items", {}).get("type") == "safe_evidence_ref":
            _validate_safe_path_list(value, f"{kind}.{field}")
        elif not isinstance(value, list):
            raise ValueError(f"{kind}.{field} must be a list")
    elif expected_type == "object" and not isinstance(value, dict):
        raise ValueError(f"{kind}.{field} must be an object")
    if "enum" in schema and value not in schema["enum"]:
        raise ValueError(f"{kind}.{field} is invalid: {value}")


def _load_event_schema() -> dict[str, Any]:
    schema_path = Path(__file__).resolve().parents[1] / "registry" / "runtime-event.schema.json"
    try:
        return json.loads(schema_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"failed to load runtime-event.schema.json: {exc}") from exc


def validate_event_schema(event: dict[str, Any]) -> None:
    allowed_event_fields = {"issue_id", "kind", "phase", "actor", "timestamp", "payload"}
    unknown_event_fields = sorted(set(event) - allowed_event_fields)
    if unknown_event_fields:
        raise ValueError(f"runtime event contains unknown field(s): {', '.join(unknown_event_fields)}")
    string_fields = ["issue_id", "kind", "phase", "actor", "timestamp"]
    missing = [field for field in [*string_fields, "payload"] if field not in event or event[field] in (None, "")]
    if missing:
        raise ValueError(f"runtime event missing required field(s): {', '.join(missing)}")
    for field in string_fields:
        if not isinstance(event.get(field), str) or not event[field].strip():
            raise ValueError(f"runtime event {field} must be a non-empty string")

    kind = event.get("kind")
    pipeline = _load_pipeline()
    forbidden_kinds = set(pipeline.get("runtime_event_policy", {}).get("forbidden_normal_event_conditions", []))
    if kind in forbidden_kinds:
        raise ValueError(f"normal transition must not be a runtime event: {kind}")

    schema = _load_event_schema()
    allowed_kinds = set(schema["properties"]["kind"]["enum"])
    if kind not in allowed_kinds:
        raise ValueError(f"invalid event kind: {kind}")

    allowed_phases = set(schema["properties"]["phase"]["enum"])
    if event.get("phase") not in allowed_phases:
        raise ValueError(f"invalid event phase: {event.get('phase')}")
    payload = event.get("payload")
    if not isinstance(payload, dict):
        raise ValueError("runtime event payload must be an object")

    # Owner / Actor rules
    metadata = schema.get("beo_contract_metadata", {})
    owner_rules = metadata.get("owner_rules", {})
    actor = event.get("actor")
    actor_rules = owner_rules.get(actor)
    if actor_rules is None:
        raise ValueError(f"runtime event actor must be one of: {', '.join(sorted(owner_rules.keys()))}")
    may_emit = set(actor_rules.get("may_emit", []))
    must_not_emit = set(actor_rules.get("must_not_emit", []))
    if kind not in may_emit or kind in must_not_emit:
        raise ValueError(f"{actor} may emit only: {', '.join(sorted(may_emit))}")

    # Payload contracts validation
    payload_contracts = metadata.get("payload_contracts", {})
    contract = payload_contracts.get(kind)
    if contract:
        required_payload = contract.get("required", [])
        missing_payload = [f for f in required_payload if f not in payload]
        if missing_payload:
            raise ValueError(f"payload for event kind '{kind}' missing required field(s): {', '.join(missing_payload)}")
        valid_conditions = {t["condition_id"] for t in pipeline.get("transitions", [])}
        properties = contract.get("properties", {})
        missing_properties = sorted(field for field in required_payload if field not in properties)
        if missing_properties:
            raise ValueError(f"payload contract for event kind '{kind}' lacks schema for required field(s): {', '.join(missing_properties)}")
        if contract.get("additionalProperties") is not True:
            unknown_payload = sorted(set(payload) - set(properties))
            if unknown_payload:
                raise ValueError(f"payload for event kind '{kind}' contains unknown field(s): {', '.join(unknown_payload)}")
        for field, field_schema in properties.items():
            if field in payload:
                _validate_payload_property(kind, field, payload[field], field_schema)
        for field, field_schema in properties.items():
            if field_schema.get("registry") == "pipeline.condition_id" and payload.get(field) not in valid_conditions:
                raise ValueError(f"{kind} {field} is not a registered pipeline condition: {payload.get(field)}")
        if kind == "handoff":
            cond_id = payload.get("condition_id")
            if cond_id in forbidden_kinds:
                raise ValueError(f"handoff condition_id must not be a normal transition: {cond_id}")


def validate_harness_proposal_write(data: dict[str, Any], actor: str) -> None:
    """Validate that the given actor may write each field in the harness proposal data.

    `data` is a dict of fields the caller intends to write (not the full proposal).
    `actor` is the BEO skill name requesting the write.
    Raises ValueError if any field is not writable by the given actor.
    """
    for field in data:
        allowed_actors = HARNESS_PROPOSAL_FIELD_AUTHORITY.get(field)
        if allowed_actors is None:
            raise ValueError(f"unknown harness_proposal field: {field}")
        if actor not in allowed_actors:
            raise ValueError(f"{actor} may not write harness_proposal.{field}; allowed: {', '.join(sorted(allowed_actors))}")
