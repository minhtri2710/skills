#!/usr/bin/env python3
from __future__ import annotations

import copy
import fcntl
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Callable

from beo_io import now

PHASES = {"planned", "approved", "executing", "executed", "reviewing", "reviewed", "blocked", "abandoned"}
APPROVAL_STATUSES = {"pending", "PASS_EXECUTE", "failed", "blocked", "stale"}
REVIEW_VERDICTS = {None, "accept", "repair_same_scope", "repair_rescope", "cannot_deliver", "abandoned"}
REVIEW_FINDING_SEVERITIES = {"blocker", "major", "minor", "info"}
REVIEW_FINDING_CATEGORIES = {"scope", "verification", "done_criteria", "safety", "evidence", "regression", "process"}
REVIEW_FINDING_ROUTES = {"repair_same_scope", "repair_rescope", "cannot_deliver", "root_cause_diagnosis_needed", "none"}
OWNER_FIELDS = {
    "beo-plan": {"initialize"},
    "beo-validate": {"phase", "approval"},
    "beo-execute": {"phase", "execution"},
    "beo-review": {"phase", "review"},
    "beo-debug": set(),
    "beo-learn": set(),
    "beo-author": set(),
    "beo-setup": set(),
    "beo-reference": set(),
}
SYSTEM_FIELDS = {"version", "issue_id", "phase_sequence_id", "metadata"}


def artifact_dir(root: Path, issue_id: str) -> Path:
    from beo_paths import artifact_dir as safe_artifact_dir

    return safe_artifact_dir(root, issue_id)


def initial_state(issue_id: str) -> dict[str, Any]:
    return {
        "version": 1,
        "issue_id": issue_id,
        "phase": "planned",
        "phase_sequence_id": 1,
        "approval": {
            "status": "pending",
            "approved_by": None,
            "actor": None,
            "ticket_file_hash": None,
            "approval_projection_hash": None,
            "repo_head": None,
            "prestate": {},
            "failure_category": None,
            "approved_phase_sequence_id": None,
        },
        "execution": {
            "actor": None,
            "started_at": None,
            "completed_at": None,
            "changed_files": [],
            "verify_results": [],
            "evidence_refs": [],
        },
        "review": {
            "actor": None,
            "verdict": None,
            "route_condition_id": None,
            "findings": [],
            "done_criteria_coverage": [],
            "repair_count": 0,
            "closed_in_br": False,
        },
        "metadata": {
            "last_owner": None,
            "updated_at": None,
        },
    }


def _locked(lock_path: Path):
    lock_path.parent.mkdir(parents=True, exist_ok=True)
    handle = open(lock_path, "w", encoding="utf-8")
    try:
        fcntl.flock(handle, fcntl.LOCK_EX)
    except Exception:
        handle.close()
        raise
    return handle


def _unlock(handle) -> None:
    fcntl.flock(handle, fcntl.LOCK_UN)
    handle.close()


def _fsync_dir(path: Path) -> None:
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    finally:
        os.close(fd)


def atomic_write_json(path: Path, data: Any) -> None:
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must be an object")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))
    tmp_path = Path(tmp_name)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp_path, path)
        _fsync_dir(path.parent)
    except Exception:
        try:
            tmp_path.unlink()
        except FileNotFoundError:
            pass
        raise


def _read_state_unlocked(path: Path, issue_id: str) -> dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"state_artifact_missing: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("state.json must be an object")
    validate_state(data, issue_id)
    return data


def read_state(root: Path, issue_id: str) -> dict[str, Any]:
    base = artifact_dir(root, issue_id)
    lock = _locked(base / "state.lock")
    try:
        return _read_state_unlocked(base / "state.json", issue_id)
    finally:
        _unlock(lock)


def initialize_state(root: Path, issue_id: str, *, owner: str = "beo-plan", overwrite: bool = False) -> dict[str, Any]:
    if owner != "beo-plan":
        raise ValueError("only beo-plan may initialize state")
    base = artifact_dir(root, issue_id)
    lock = _locked(base / "state.lock")
    try:
        path = base / "state.json"
        if path.exists() and not overwrite:
            raise FileExistsError(f"state.json already exists: {path}")
        state = initial_state(issue_id)
        state["metadata"]["updated_at"] = now()
        state["metadata"]["last_owner"] = owner
        validate_state(state, issue_id)
        atomic_write_json(path, state)
        return state
    finally:
        _unlock(lock)


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
    import json
    try:
        return json.loads(pipeline_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"failed to load pipeline.json: {exc}") from exc


def _load_state_schema() -> dict[str, Any]:
    schema_path = Path(__file__).resolve().parents[1] / "registry" / "state.schema.json"
    import json
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
    execution_fields = {"actor", "started_at", "completed_at", "changed_files", "verify_results", "evidence_refs"}
    review_fields = {"actor", "verdict", "route_condition_id", "findings", "done_criteria_coverage", "repair_count", "closed_in_br"}
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
    for field in ["actor", "started_at", "completed_at"]:
        _validate_optional_string(execution.get(field), f"execution.{field}")
    _validate_safe_path_list(execution.get("changed_files"), "execution.changed_files")
    _validate_list(execution.get("verify_results"), "execution.verify_results")
    _validate_safe_path_list(execution.get("evidence_refs"), "execution.evidence_refs")
    if not all(isinstance(result, dict) for result in execution.get("verify_results", [])):
        raise ValueError("execution.verify_results entries must be objects")
    if not isinstance(review, dict):
        raise ValueError("review must be an object")
    _reject_unknown_fields(review, review_fields, "review")
    missing_review = sorted(review_fields - set(review))
    if missing_review:
        raise ValueError(f"review missing required field(s): {', '.join(missing_review)}")
    _validate_optional_string(review.get("actor"), "review.actor")
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


def _reject_caller_system_fields(before: dict[str, Any], after: dict[str, Any]) -> None:
    if after.get("phase_sequence_id") != before.get("phase_sequence_id"):
        raise ValueError("state updater must not set phase_sequence_id")
    before_meta = before.get("metadata") if isinstance(before.get("metadata"), dict) else {}
    after_meta = after.get("metadata") if isinstance(after.get("metadata"), dict) else {}
    for field in ["updated_at", "last_owner"]:
        if after_meta.get(field) != before_meta.get(field):
            raise ValueError(f"state updater must not set metadata.{field}")
    before_approval = before.get("approval") if isinstance(before.get("approval"), dict) else {}
    after_approval = after.get("approval") if isinstance(after.get("approval"), dict) else {}
    if after_approval.get("approved_phase_sequence_id") != before_approval.get("approved_phase_sequence_id"):
        raise ValueError("state updater must not set approval.approved_phase_sequence_id")


def _reject_unowned_changes(before: dict[str, Any], after: dict[str, Any], owner: str) -> None:
    owned = OWNER_FIELDS.get(owner)
    if owned is None:
        raise ValueError(f"unknown state owner: {owner}")
    allowed = owned | SYSTEM_FIELDS
    changed = {key for key in set(before) | set(after) if before.get(key) != after.get(key)}
    unowned = sorted(changed - allowed)
    if unowned:
        raise ValueError(f"{owner} cannot write state field(s): {', '.join(unowned)}")
    if owner in {"beo-debug", "beo-learn"} and changed - SYSTEM_FIELDS:
        raise ValueError(f"{owner} may not write delivery state")


def locked_update_state(
    root: Path,
    issue_id: str,
    owner: str,
    updater: Callable[[dict[str, Any]], dict[str, Any] | None],
) -> dict[str, Any]:
    if owner not in OWNER_FIELDS:
        raise ValueError(f"unknown state owner: {owner}")
    if not OWNER_FIELDS[owner]:
        raise ValueError(f"{owner} may not update delivery state")
    base = artifact_dir(root, issue_id)
    lock = _locked(base / "state.lock")
    try:
        path = base / "state.json"
        before = _read_state_unlocked(path, issue_id)
        candidate = copy.deepcopy(before)
        after = updater(candidate)
        if after is None:
            after = candidate
        if not isinstance(after, dict):
            raise ValueError("state updater must return an object")
        _reject_caller_system_fields(before, after)
        _reject_unowned_changes(before, after, owner)
        if owner == "beo-execute":
            if before.get("phase") == "approved":
                if before.get("approval", {}).get("status") != "PASS_EXECUTE":
                    raise ValueError("current PASS_EXECUTE approval is required")
                if not execution_entry_is_current(before):
                    raise ValueError("PASS_EXECUTE approval is stale for execution entry")
                execution = after.get("execution") if isinstance(after.get("execution"), dict) else {}
                if after.get("phase") != "executing":
                    raise ValueError("beo-execute must durably enter executing state before product mutation")
                if not isinstance(execution.get("actor"), str) or not execution["actor"].strip():
                    raise ValueError("execution start requires execution.actor")
                if not isinstance(execution.get("started_at"), str) or not execution["started_at"].strip():
                    raise ValueError("execution start requires execution.started_at")
            elif before.get("phase") not in {"executing", "executed"}:
                raise ValueError("beo-execute requires approved/executing/executed state")
        after["phase_sequence_id"] = int(before["phase_sequence_id"]) + 1
        after.setdefault("metadata", {})["updated_at"] = now()
        after["metadata"]["last_owner"] = owner
        if owner == "beo-validate" and after.get("approval", {}).get("status") == "PASS_EXECUTE":
            if after.get("phase") != "approved":
                raise ValueError("PASS_EXECUTE approval must explicitly set phase to approved")
            after["approval"]["approved_phase_sequence_id"] = after["phase_sequence_id"]
        validate_state(after, issue_id)
        atomic_write_json(path, after)
        return after
    finally:
        _unlock(lock)


def execution_entry_is_current(state: dict[str, Any]) -> bool:
    return state.get("phase_sequence_id") == state.get("approval", {}).get("approved_phase_sequence_id")


def read_events(root: Path, issue_id: str) -> list[dict[str, Any]]:
    base = artifact_dir(root, issue_id)
    path = base / "runtime-events.jsonl"
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    with open(path, "r", encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            event = json.loads(line)
            if not isinstance(event, dict):
                raise ValueError(f"runtime-events.jsonl line {line_number} must be an object")
            events.append(event)
    return events


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
    import json
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


def append_event(root: Path, issue_id: str, event: dict[str, Any]) -> None:
    if event.get("issue_id") != issue_id:
        raise ValueError("runtime event issue_id mismatch")
    validate_event_schema(event)
    base = artifact_dir(root, issue_id)
    base.mkdir(parents=True, exist_ok=True)
    lock = _locked(base / "runtime-events.lock")
    try:
        path = base / "runtime-events.jsonl"
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(event, sort_keys=True, separators=(",", ":")))
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        _fsync_dir(base)
    finally:
        _unlock(lock)
