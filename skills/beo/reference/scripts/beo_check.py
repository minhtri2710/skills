#!/usr/bin/env python3
from __future__ import annotations

import argparse
import fnmatch
import hashlib
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

SCHEMA_VERSION = "beo-beads/v3"
HELPER_VERSION = "beo_check.py@beo-beads/v3.0"
OWNERS = {"beo-plan", "beo-validate", "beo-execute", "beo-review", "beo-debug", "beo-recall", "beo-learn", "beo-author", "beo-setup", "beo-reference"}
DELIVERY_OWNERS = {"beo-plan", "beo-validate", "beo-execute", "beo-review"}
RUNTIME_EVENT_OWNERS = DELIVERY_OWNERS | {"beo-debug", "beo-recall"}
ABANDON_REASONS = {"user_cancelled", "pre_mutation_abandon", "post_mutation_preserved", "superseded", "unsafe_environment"}
DIAGNOSIS_STATUSES = {"root_cause_proven", "diagnosis_inconclusive", "blocker_is_user_owned"}
RECALL_RESULT_STATUSES = {"memory_recalled", "no_relevant_memory", "memory_unavailable"}
LEARNING_CASE_TYPES = {"success_pattern", "failure_pattern", "near_miss", "recurring_mistake", "cannot_deliver_pattern", "debug_pattern", "authoring_candidate"}
PHASE_ALIASES = {
    "plan": "beo-plan",
    "validate": "beo-validate",
    "execute": "beo-execute",
    "review": "beo-review",
    "debug": "beo-debug",
    "recall": "beo-recall",
    "beo-plan": "beo-plan",
    "beo-validate": "beo-validate",
    "beo-execute": "beo-execute",
    "beo-review": "beo-review",
    "beo-debug": "beo-debug",
    "beo-recall": "beo-recall",
}
FUTURE_FIELDS = {
    "beo-plan": {"readiness", "approval_ref", "integrity", "execution", "review"},
    "beo-validate": {"execution", "review"},
    "beo-execute": {"review"},
}
PROTECTED_PATTERNS = [
    ".git/**",
    ".env",
    ".env.*",
    "**/.env",
    "**/.env.*",
    "secrets/**",
    "credentials/**",
    "*.pem",
    "*.key",
    "*.p12",
    "*.pfx",
    "id_rsa",
    "id_ed25519",
    ".beads/beads.db",
]
MODES = {"quick", "standard", "strict"}
SIDE_EFFECT_PATTERNS = re.compile(
    r"\b(deploy|migration|migrate|publish|email|payment|billing)\b|terraform\s+apply|kubectl\s+apply|npm\s+publish|third-party\s+write",
    re.IGNORECASE,
)


class DuplicateKeyLoader(yaml.SafeLoader if yaml else object):
    pass


if yaml:
    def construct_mapping(loader: DuplicateKeyLoader, node: Any, deep: bool = False) -> dict[str, Any]:
        mapping: dict[str, Any] = {}
        for key_node, value_node in node.value:
            key = loader.construct_object(key_node, deep=deep)
            if key in mapping:
                raise ValueError(f"duplicate YAML key: {key}")
            mapping[key] = loader.construct_object(value_node, deep=deep)
        return mapping

    DuplicateKeyLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, construct_mapping)


def now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def stable_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_text(text: str) -> str:
    return "sha256:" + hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_hash(path: Path) -> str:
    if not path.exists():
        return "missing"
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def strict_artifact_hashes(root: Path, ticket: dict[str, Any]) -> dict[str, str]:
    issue_id = str(ticket.get("issue_id") or "")
    base = root / ".beads" / "artifacts" / issue_id
    return {
        "STRICT.md": file_hash(base / "STRICT.md"),
        "ROLLBACK.md": file_hash(base / "ROLLBACK.md"),
    }


def load_registry(root: Path, name: str) -> dict[str, Any]:
    path = root / "skills" / "beo" / "reference" / "registry" / f"{name}.json"
    if not path.exists():
        path = Path(__file__).resolve().parents[1] / "registry" / f"{name}.json"
    return load_json(path, {})


def sync_constants_with_registry(root: Path) -> None:
    global OWNERS, DELIVERY_OWNERS, RUNTIME_EVENT_OWNERS, ABANDON_REASONS, DIAGNOSIS_STATUSES, RECALL_RESULT_STATUSES, LEARNING_CASE_TYPES, FUTURE_FIELDS
    schema = load_registry(root, "ticket-schema.json")
    if not schema:
        return

    # Derive owners from pipeline.json (canonical home for owner_classes)
    pipeline = load_registry(root, "pipeline.json")
    if pipeline:
        classes = pipeline.get("owner_classes", {})
        if isinstance(classes, dict):
            all_owners = set()
            for cls_members in classes.values():
                if isinstance(cls_members, list):
                    all_owners.update(str(o) for o in cls_members)
            if all_owners:
                OWNERS = all_owners
            if "delivery" in classes and isinstance(classes["delivery"], list):
                DELIVERY_OWNERS = set(str(o) for o in classes["delivery"])
            if "support_runtime" in classes and isinstance(classes["support_runtime"], list):
                RUNTIME_EVENT_OWNERS = DELIVERY_OWNERS | set(str(o) for o in classes["support_runtime"])

    event = schema.get("runtime_event", {})
    if isinstance(event, dict):
        reasons = event.get("abandon_reason")
        if isinstance(reasons, list):
            ABANDON_REASONS = set(str(r) for r in reasons)
        statuses = event.get("diagnosis_status")
        if isinstance(statuses, list):
            DIAGNOSIS_STATUSES = set(str(s) for s in statuses)
        recall = event.get("recall_result_status")
        if isinstance(recall, list):
            RECALL_RESULT_STATUSES = set(str(s) for s in recall)

    future = schema.get("future_owned_field_rule")
    if isinstance(future, dict):
        FUTURE_FIELDS = {str(k): set(str(v) for v in val) for k, val in future.items() if isinstance(val, list)}


def plan_input_hash(ticket: dict[str, Any]) -> str:
    # Approval must not self-invalidate when validate or later owners append
    # readiness, execution, review, debug, or runtime-event evidence. Hash only
    # approval-bearing plan inputs; triage provenance is informational.
    plan_fields = [
        "schema_version",
        "issue_id",
        "mode",
        "request",
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


def load_json(path: Path, default: Any) -> Any:
    try:
        return json.loads(path.read_text())
    except FileNotFoundError:
        return default


def extract_ticket_block(text: str) -> dict[str, Any]:
    if yaml is None:
        raise RuntimeError("PyYAML is required")
    match = re.search(r"```yaml\s+beo\.ticket\s*\n(?P<body>.*?)\n```", text, re.DOTALL)
    source = match.group("body") if match else text
    parsed = yaml.load(source, Loader=DuplicateKeyLoader)
    if not isinstance(parsed, dict):
        raise ValueError("ticket YAML must be an object")
    if "beo.ticket" in parsed:
        parsed = parsed["beo.ticket"]
    if not isinstance(parsed, dict):
        raise ValueError("beo.ticket must be an object")
    return parsed


def read_ticket(path: Path) -> dict[str, Any]:
    return extract_ticket_block(path.read_text())


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
    data = load_json(path, {})
    return data if isinstance(data, dict) else {}


def strict_side_effect_profiles(root: Path) -> tuple[list[str], dict[str, list[str]]]:
    strict = command_contracts(root).get("strict_side_effects")
    if not isinstance(strict, dict):
        return [], {}
    default = strict.get("default_requires")
    profiles = strict.get("profiles")
    normalized_profiles: dict[str, list[str]] = {}
    if isinstance(profiles, dict):
        for name, fields in profiles.items():
            if isinstance(fields, list):
                normalized_profiles[str(name)] = [str(field) for field in fields]
    return [str(field) for field in default] if isinstance(default, list) else [], normalized_profiles


def run_br_show(root: Path, issue_id: str) -> tuple[dict[str, Any], str | None]:
    try:
        proc = subprocess.run(
            ["br", "show", issue_id, "--json"],
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
    # Legacy snapshot for backward compatibility in non-approval contexts
    return {
        **hard_bead_snapshot(issue),
        **drift_observation(issue),
    }


def issue_field(issue: dict[str, Any], *names: str, default: Any = None) -> Any:
    for name in names:
        if name in issue:
            return issue[name]
    return default


def labels_of(issue: dict[str, Any]) -> list[str]:
    labels = issue_field(issue, "labels", "label", default=[])
    if isinstance(labels, str):
        return [item.strip() for item in labels.split(",") if item.strip()]
    if isinstance(labels, list):
        return [str(item) for item in labels]
    return []


def is_parent_or_non_atomic(issue: dict[str, Any], ticket: dict[str, Any]) -> bool:
    issue_type = str(issue_field(issue, "issue_type", "type", default="")).lower()
    labels = {label.lower() for label in labels_of(issue)}
    if "beo:atomic" in labels:
        return False
    if issue_type in {"epic", "feature"}:
        return True
    if labels & {"beo:epic", "beo:feature"}:
        return True
    return False


def actor_identity() -> str | None:
    for name in ["BR_ACTOR", "BEO_ACTOR", "AGENT_NAME", "BR_AGENT_NAME", "ACTOR"]:
        value = os.environ.get(name)
        if value:
            return value
    return None


def claim_valid(issue: dict[str, Any]) -> bool:
    status = str(issue_field(issue, "status", default="")).lower()
    assignee = str(issue_field(issue, "assignee", "owner", default="") or "")
    if status != "in_progress" or not assignee:
        return False
    actor = actor_identity()
    return bool(actor) and assignee == actor


def normalize_posix(path: str) -> str:
    return path.replace("\\", "/").strip()


def validate_path_token(root: Path, token: str, *, pattern: bool = False, strict_mode: bool = False) -> list[str]:
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
    for protected in PROTECTED_PATTERNS:
        if fnmatch.fnmatch(path, protected):
            errors.append(f"path matches protected pattern {protected}: {path}")
            break
    return errors


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
    posture = ticket.get("posture_profile")
    if posture is None and ticket.get("mode") == "quick":
        posture = "repo_only_low_risk"
    expanded: dict[str, Any] = {}
    if posture == "repo_only_low_risk":
        expanded.update({
            "generated_outputs": [],
            "external_side_effects": {"status": "none", "effects": []},
            "stateful_external_systems": {"status": "none", "systems": []},
            "risk_scope": "low: bounded edits to declared repo files only",
            "rollback_boundary": "revert_declared_file_changes",
        })
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


def validate_phase_boundary(ticket: dict[str, Any], phase: str) -> list[str]:
    errors: list[str] = []
    future = FUTURE_FIELDS.get(phase, set())
    present = sorted(field for field in future if field in ticket)
    if present:
        errors.append(f"{phase} boundary contains future-owned fields: {present}")
    return errors


def runtime_events(ticket: dict[str, Any]) -> list[dict[str, Any]]:
    events = ticket.get("runtime_events")
    return [event for event in events if isinstance(event, dict)] if isinstance(events, list) else []


def validate_same_scope_repair_request(ticket: dict[str, Any]) -> list[str]:
    review = ticket.get("review") if isinstance(ticket.get("review"), dict) else {}
    if review.get("verdict") != "repair_same_scope":
        return []
    errors: list[str] = []
    events = runtime_events(ticket)
    repair_index = next(
        (
            index
            for index in range(len(events) - 1, -1, -1)
            if events[index].get("kind") == "change_request"
            and events[index].get("subtype") == "repair_same_scope"
            and events[index].get("condition_id") == "repair_same_scope"
        ),
        None,
    )
    if repair_index is None:
        return ["repair_same_scope requires a runtime_events[] change_request with subtype repair_same_scope"]
    event = events[repair_index]
    for later in events[repair_index + 1:]:
        if later.get("kind") == "abandon" or (later.get("kind") == "change_request" and later.get("subtype") in {"scope_delta", "repair_rescope"}):
            errors.append(f"same-scope change_request is superseded by later {later.get('kind')} event")
        if later.get("condition_id") in {"repair_rescope", "scope_delta_required", "abandoned"}:
            errors.append(f"same-scope change_request is superseded by later {later.get('condition_id')} condition")
    if event.get("requested_by") != "beo-review":
        errors.append("same-scope change_request.requested_by must be beo-review")
    finding_refs = event.get("finding_refs")
    if not isinstance(finding_refs, list) or not finding_refs:
        errors.append("same-scope change_request.finding_refs must be a non-empty list")
    if not event.get("prior_approval_ref"):
        errors.append("same-scope change_request.prior_approval_ref is required")
    boundaries = event.get("unchanged_boundaries")
    required = [
        "scope.files.allow",
        "generated_outputs",
        "human_gates",
        "acceptance_criteria",
        "external_side_effects",
        "stateful_external_systems",
        "scope.files.forbid",
        "scope.verify.commands",
    ]
    if not isinstance(boundaries, dict):
        errors.append("same-scope change_request.unchanged_boundaries must be an object")
    else:
        for key in required:
            if boundaries.get(key) is not True:
                errors.append(f"same-scope change_request.unchanged_boundaries.{key} must be true")
    return errors


def validate_runtime_events(ticket: dict[str, Any], issue_id: str, root: Path | None = None) -> list[str]:
    errors: list[str] = []
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
    required = ["id", "kind", "created_at", "owner", "issue_id", "condition_id", "basis_ref", "message"]
    recall_callers = DELIVERY_OWNERS | {"beo-debug"}
    review_route_conditions = {"repair_same_scope", "repair_rescope", "cannot_deliver", "abandoned", "root_cause_diagnosis_needed", "repair_budget_exceeded", "entry_blocked_execution_evidence_incomplete"}
    for index, event in enumerate(events):
        prefix = f"runtime_events[{index}]"
        for field in required:
            if not event.get(field):
                errors.append(f"{prefix}.{field} is required")
        kind = event.get("kind")
        owner = event.get("owner")
        subtype = event.get("subtype")
        if owner and owner not in RUNTIME_EVENT_OWNERS:
            errors.append(f"{prefix}.owner is not a runtime event owner: {owner}")
        if event.get("issue_id") and event.get("issue_id") != issue_id:
            errors.append(f"{prefix}.issue_id must match selected bead")
        if kind == "handoff":
            if subtype not in {"debug", "recall"}:
                errors.append(f"{prefix}.subtype is not registered for handoff: {subtype}")
            for field in ["caller_owner", "return_to"]:
                if not event.get(field):
                    errors.append(f"{prefix}.{field} is required for handoff")
            if event.get("return_to") != event.get("caller_owner"):
                errors.append(f"{prefix}.return_to must match caller_owner")
            if subtype == "debug":
                for field in ["return_condition_id", "question"]:
                    if not event.get(field):
                        errors.append(f"{prefix}.{field} is required for debug handoff")
                if event.get("caller_owner") not in {"beo-execute", "beo-review"}:
                    errors.append(f"{prefix}.caller_owner must be beo-execute or beo-review for debug handoff")
            elif subtype == "recall":
                if not event.get("query"):
                    errors.append(f"{prefix}.query is required for recall handoff")
                if event.get("caller_owner") not in recall_callers:
                    errors.append(f"{prefix}.caller_owner is not allowed for recall handoff")
            if isinstance(subtype, str):
                latest_handoff[subtype] = event
        elif kind == "return":
            if subtype not in {"debug", "recall"}:
                errors.append(f"{prefix}.subtype is not registered for return: {subtype}")
            expected_owner = {"debug": "beo-debug", "recall": "beo-recall"}.get(str(subtype))
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
                for field in ["return_condition_id", "diagnosis_status", "diagnosis_ref"]:
                    if not event.get(field):
                        errors.append(f"{prefix}.{field} is required for debug return")
                if event.get("diagnosis_status") not in DIAGNOSIS_STATUSES:
                    errors.append(f"{prefix}.diagnosis_status is not registered")
                if handoff is not None and event.get("return_condition_id") != handoff.get("return_condition_id"):
                    errors.append(f"{prefix}.return_condition_id must match latest debug handoff")
                latest_debug_return_index = index
            elif subtype == "recall":
                for field in ["result_status", "recall_ref"]:
                    if not event.get(field):
                        errors.append(f"{prefix}.{field} is required for recall return")
                if event.get("result_status") not in RECALL_RESULT_STATUSES:
                    errors.append(f"{prefix}.result_status is not registered")
                expected = f".beads/artifacts/{issue_id}/recall/RECALL_SUMMARY.md"
                if event.get("recall_ref") and event.get("recall_ref") != expected:
                    errors.append(f"{prefix}.recall_ref must point to canonical RECALL_SUMMARY.md")
                if root is not None and event.get("recall_ref") == expected and not (root / expected).exists():
                    errors.append(f"{prefix}.recall_ref file is missing")
        elif kind == "abandon":
            if event.get("abandon_reason") not in ABANDON_REASONS:
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
        elif kind == "user_stop":
            if not event.get("reason") and not event.get("message"):
                errors.append(f"{prefix}.reason or message is required for user_stop")
        elif kind == "learning_candidate":
            if owner not in {"beo-review", "beo-debug"}:
                errors.append(f"{prefix}.owner must be beo-review or beo-debug for learning_candidate")
            if event.get("case_type") not in LEARNING_CASE_TYPES:
                errors.append(f"{prefix}.case_type is not registered")
            if not event.get("source_phase"):
                errors.append(f"{prefix}.source_phase is required for learning_candidate")
            source_event_id = event.get("source_event_id")
            if source_event_id and not any(candidate.get("id") == source_event_id for candidate in events[:index]):
                errors.append(f"{prefix}.source_event_id must reference a prior runtime event")
            if owner == "beo-debug" and latest_debug_return_index is None:
                errors.append(f"{prefix} requires a prior debug return event")
            review = ticket.get("review") if isinstance(ticket.get("review"), dict) else {}
            if owner == "beo-review" and not review.get("verdict") and latest_review_route_index is None:
                errors.append(f"{prefix} requires a prior review verdict or routing event")
        elif kind not in {"user_stop", "handoff", "return", "change_request", "abandon", "learning_candidate"}:
            errors.append(f"{prefix}.kind is not registered: {kind}")
    return errors


def is_broad_glob(path: str) -> bool:
    path = normalize_posix(path)
    return path in {"**", "*"} or path.endswith("/**") or path.endswith("/*")


def glob_match(path: str, pattern: str) -> bool:
    path = normalize_posix(path)
    pattern = normalize_posix(pattern)
    return fnmatch.fnmatch(path, pattern) or (pattern.endswith("/") and path.startswith(pattern))


def is_allowed(path: str, allowed: list[str], generated: list[str]) -> bool:
    path = normalize_posix(path)
    for item in allowed + generated:
        item = normalize_posix(item)
        if path == item or fnmatch.fnmatch(path, item) or (item.endswith("/") and path.startswith(item)):
            return True
    return False


def scope_tokens(ticket: dict[str, Any]) -> list[str]:
    return [normalize_posix(item) for item in allow_paths(ticket) + path_list(expanded_posture(ticket).get("generated_outputs")) if item]


def path_tokens_overlap(left: str, right: str) -> bool:
    left = normalize_posix(left).rstrip("/")
    right = normalize_posix(right).rstrip("/")
    if not left or not right:
        return False
    # Exact match
    if left == right:
        return True
    # Tree overlap: Dir-File, Parent-Child
    try:
        left_p = Path(left)
        right_p = Path(right)
        if right_p.is_relative_to(left_p) or left_p.is_relative_to(right_p):
            return True
    except (ValueError, RuntimeError):
        pass
    # Glob match: Glob-Dir, Glob-File
    if any(char in left for char in "*?[") and fnmatch.fnmatch(right, left):
        return True
    if any(char in right for char in "*?[") and fnmatch.fnmatch(left, right):
        return True
    return False


def active_scope_conflicts(root: Path, ticket: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    current_issue = str(ticket.get("issue_id") or "")
    current_tokens = scope_tokens(ticket)
    artifacts = root / ".beads" / "artifacts"
    if not artifacts.exists() or not current_tokens:
        return errors, warnings

    scope_overlap = scope(ticket).get("scope_overlap")
    safe_overlaps = []
    if isinstance(scope_overlap, dict) and scope_overlap.get("status") == "safe":
        safe_overlaps = scope_overlap.get("overlaps", [])
        if not isinstance(safe_overlaps, list):
            safe_overlaps = []

    for other_path in artifacts.glob("*/TICKET.md"):
        try:
            other = read_ticket(other_path)
        except Exception:
            continue
        other_issue = str(other.get("issue_id") or other_path.parent.name)
        if other_issue == current_issue:
            continue
        if other.get("readiness") != "PASS_EXECUTE":
            continue
        review = other.get("review") if isinstance(other.get("review"), dict) else {}
        if review.get("verdict") in {"accept", "abandoned", "cannot_deliver"}:
            continue
        other_tokens = scope_tokens(other)

        for left in current_tokens:
            for right in other_tokens:
                if path_tokens_overlap(left, right):
                    overlap_str = f"{left} overlaps {right}"
                    is_safe = False
                    for entry in safe_overlaps:
                        if not isinstance(entry, dict):
                            continue
                        if entry.get("issue_id") == other_issue:
                            safe_reason = entry.get("safe_reason")
                            evidence_ref = entry.get("evidence_ref")
                            if safe_reason not in {"dependency_ordered", "disjoint_region", "user_authorized"}:
                                continue
                            if not evidence_ref:
                                continue
                            paths = entry.get("paths", [])
                            if not isinstance(paths, list):
                                continue
                            
                            # Match structured path entry
                            match_found = False
                            for path_entry in paths:
                                if isinstance(path_entry, dict):
                                    curr = path_entry.get("current")
                                    oth = path_entry.get("other")
                                    if curr == left and oth == right:
                                        match_found = True
                                        break
                            if match_found:
                                warnings.append(f"ignoring declared safe scope overlap with {other_issue}: {overlap_str} (reason: {safe_reason})")
                                is_safe = True
                                break
                    if not is_safe:
                        errors.append(f"active scope conflict with {other_issue}: {overlap_str}")
    return errors, warnings


def changed_files(root: Path, ticket: dict[str, Any]) -> list[str]:
    files: set[str] = set()
    execution = ticket.get("execution") if isinstance(ticket.get("execution"), dict) else {}
    for item in path_list(execution.get("changed_files")):
        files.add(normalize_posix(item))
    git_dir = root / ".git"
    if git_dir.exists():
        commands = [
            ["git", "diff", "--name-only"],
            ["git", "diff", "--cached", "--name-only"],
            ["git", "status", "--porcelain"],
        ]
        for command in commands:
            proc = subprocess.run(command, cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            if proc.returncode != 0:
                continue
            for line in proc.stdout.splitlines():
                if command[-1] == "--porcelain":
                    if not line:
                        continue
                    path = line[3:] if len(line) > 3 else line
                    if " -> " in path:
                        path = path.rsplit(" -> ", 1)[1]
                    files.add(normalize_posix(path))
                elif line.strip():
                    files.add(normalize_posix(line.strip()))
    return sorted(file for file in files if file)


def validate_identity(root: Path, issue_id: str, ticket_path: Path, ticket: dict[str, Any], issue: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    issue_actual = str(issue_field(issue, "id", default=issue_id))
    if issue_actual != issue_id:
        errors.append(f"br issue id mismatch: expected {issue_id}, got {issue_actual}")
    expected_path = ticket_path_for(root, issue_id).resolve()
    if ticket_path.resolve() != expected_path:
        errors.append(f"ticket path must be {expected_path.relative_to(root.resolve())}")
    if ticket.get("issue_id") != issue_id:
        errors.append("ticket issue_id does not match selected bead")
    if ticket.get("schema_version") != SCHEMA_VERSION:
        errors.append(f"unsupported ticket schema_version: {ticket.get('schema_version')}")
    for duplicate in (root / ".beads" / "artifacts").glob("*/TICKET.md") if (root / ".beads" / "artifacts").exists() else []:
        if duplicate.resolve() == ticket_path.resolve():
            continue
        try:
            other = read_ticket(duplicate)
        except Exception:
            continue
        if other.get("issue_id") == issue_id:
            errors.append(f"duplicate ticket for issue {issue_id}: {duplicate}")
    if is_parent_or_non_atomic(issue, ticket) and ticket.get("readiness") == "PASS_EXECUTE":
        errors.append("parent/feature/epic beads must not receive PASS_EXECUTE")
    return errors


def validate_plan(root: Path, ticket: dict[str, Any], issue: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if ticket.get("mode") not in MODES:
        errors.append(f"mode must be one of {sorted(MODES)}")
    gates = ticket.get("human_gates")
    if not isinstance(gates, dict):
        errors.append("human_gates must be an object")
    elif gates.get("status") == "unresolved":
        errors.append("Human Gates are unresolved")
    elif gates.get("status") not in {"not_applicable", "resolved"}:
        errors.append("human_gates.status must be not_applicable, resolved, or unresolved")
    if is_parent_or_non_atomic(issue, ticket):
        errors.append("selected bead is not atomic; decompose before approval")
    atomicity = ticket.get("atomicity") if isinstance(ticket.get("atomicity"), dict) else {}
    if atomicity.get("decision") != "atomic":
        errors.append("atomicity.decision must be atomic before PASS_EXECUTE")
    if not atomicity.get("reason"):
        errors.append("atomicity.reason is required")
    if atomicity.get("rejects_multi_task") is not True:
        errors.append("atomicity.rejects_multi_task must be true")
    if not allow_paths(ticket):
        errors.append("scope.files.allow is required")
    if not verify_commands(ticket):
        errors.append("scope.verify.commands is required")
    if not ticket.get("acceptance_criteria"):
        errors.append("acceptance_criteria is required")
    strict_mode = ticket.get("mode") == "strict"
    for path in allow_paths(ticket):
        errors.extend(validate_path_token(root, path, strict_mode=strict_mode))
        if is_broad_glob(path):
            gate_resolved = isinstance(gates, dict) and gates.get("status") == "resolved"
            gate_list = gates.get("gates", []) if isinstance(gates, dict) else []
            authorized = gate_resolved and any(
                isinstance(g, dict) and g.get("type") == "authorization" and 
                (path in str(g.get("message") or "") or "glob" in str(g.get("message") or "").lower())
                for g in gate_list
            )
            if not authorized:
                errors.append(f"broad glob requires resolved human authorization gate mentioning the glob: {path}")

    for path in path_list(expanded_posture(ticket).get("generated_outputs")):
        errors.extend(validate_path_token(root, path, strict_mode=strict_mode))
        if is_broad_glob(path):
            gate_resolved = isinstance(gates, dict) and gates.get("status") == "resolved"
            gate_list = gates.get("gates", []) if isinstance(gates, dict) else []
            authorized = gate_resolved and any(
                isinstance(g, dict) and g.get("type") == "authorization" and 
                (path in str(g.get("message") or "") or "glob" in str(g.get("message") or "").lower())
                for g in gate_list
            )
            if not authorized:
                errors.append(f"broad glob in generated_outputs requires resolved human authorization gate: {path}")
    for pattern in forbid_patterns(ticket):
        errors.extend(validate_path_token(root, pattern, pattern=True, strict_mode=True))
    posture = expanded_posture(ticket)
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

    commands = "\n".join(verify_commands(ticket))
    detected_side_effect = bool(SIDE_EFFECT_PATTERNS.search(commands))
    if ticket.get("mode") in {"quick", "standard"} and (has_external or has_stateful or detected_side_effect):
        errors.append("quick/standard mode cannot include external side effects or stateful system mutations")
    if ticket.get("mode") == "strict":
        strict = ticket.get("strict") if isinstance(ticket.get("strict"), dict) else {}
        if not strict.get("reason"):
            errors.append("strict.reason is required in strict mode")
        if not ticket.get("authorization_refs") and not strict.get("authorization_refs"):
            errors.append("authorization_refs are required in strict mode")
        declared_hashes = strict.get("artifact_hashes") if isinstance(strict.get("artifact_hashes"), dict) else {}
        for name, current_hash in strict_artifact_hashes(root, ticket).items():
            if current_hash == "missing":
                errors.append(f"{name} is required in strict mode")
            elif declared_hashes.get(name) != current_hash:
                errors.append(f"strict.artifact_hashes.{name} must match current {name}")
        default_fields, profiles = strict_side_effect_profiles(root)
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
    return errors


def approval_envelope_status(ticket: dict[str, Any], issue: dict[str, Any], plan_hash: str, bead_hash: str, contracts_hash: str) -> str:
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
    if ref.get("issue_id") != ticket.get("issue_id") or ref.get("ticket_schema_version") != SCHEMA_VERSION:
        return "invalid"
    if ref.get("approval_projection_rule") != "plan_input_execution_binding":
        return "invalid"
    if ref.get("helper_version") != HELPER_VERSION:
        return "invalid"
    expected = {
        "approval_projection_hash": approval_hash(ticket, issue, bead_hash, contracts_hash),
        "plan_input_hash": plan_hash,
        "bead_snapshot_hash": bead_hash,
        "command_contracts_hash": contracts_hash,
    }
    for key, value in expected.items():
        if ref.get(key) != value:
            return "invalid"
    return "complete"


def validate_execute(root: Path, ticket: dict[str, Any], issue: dict[str, Any], envelope_status: str) -> list[str]:
    errors: list[str] = []
    if envelope_status != "complete":
        errors.append("approval envelope is not complete for execute")
    if not claim_valid(issue):
        errors.append("br claim for current actor/session is missing or invalid")
    execution = ticket.get("execution") if isinstance(ticket.get("execution"), dict) else {}
    prestate = execution.get("prestate_refs") if isinstance(execution.get("prestate_refs"), dict) else None
    changed = path_list(execution.get("changed_files"))
    if changed and not prestate:
        errors.append("execution.prestate_refs is required when changed_files are recorded")
    if prestate:
        files = prestate.get("files") if isinstance(prestate.get("files"), dict) else {}
        for path, recorded in files.items():
            normalized = normalize_posix(path)
            current = file_hash(root / normalized)
            if recorded == "missing" and current != "missing" and normalized not in changed:
                errors.append(f"unexplained prestate drift before mutation: {path}")
            elif recorded != "missing" and current != recorded and normalized not in changed:
                errors.append(f"unexplained prestate drift before mutation: {path}")
        recorded_paths = {normalize_posix(path) for path in files}
        for changed_path in changed:
            if normalize_posix(changed_path) not in recorded_paths:
                errors.append(f"changed file is missing prestate hash: {changed_path}")
    return errors


def validate_review_verdict(review: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    verdict = review.get("verdict")
    if verdict and verdict not in {"accept", "repair_same_scope", "repair_rescope", "cannot_deliver", "abandoned"}:
        errors.append(f"review.verdict is not legal: {verdict}")
    reason_class = review.get("reason_class")
    if reason_class and reason_class not in {"user_owned", "unsafe", "not_deliverable"}:
        errors.append(f"review.reason_class is not legal: {reason_class}")
    if verdict == "cannot_deliver" and reason_class not in {"user_owned", "unsafe", "not_deliverable"}:
        errors.append("review.reason_class is required for cannot_deliver verdict")
    return errors


def validate_review(root: Path, ticket: dict[str, Any], issue: dict[str, Any], envelope_status: str) -> list[str]:
    errors = validate_execute(root, ticket, issue, envelope_status)
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
    generated = path_list(expanded_posture(ticket).get("generated_outputs"))
    for changed in changed_files(root, ticket):
        for err in validate_path_token(root, changed, strict_mode=ticket.get("mode") == "strict"):
            errors.append(f"changed file {err}")
        if any(glob_match(changed, pattern) for pattern in forbid_patterns(ticket)):
            errors.append(f"changed file matches forbidden path: {changed}")
        if not is_allowed(changed, allow_paths(ticket), generated):
            errors.append(f"changed file outside approved scope: {changed}")
    errors.extend(validate_review_verdict(review))
    if review.get("verdict") == "accept":
        for finding in review.get("findings", []) if isinstance(review.get("findings"), list) else []:
            if isinstance(finding, dict) and finding.get("severity") == "blocking":
                errors.append("blocking findings cannot produce accept verdict")
    return errors


def build_output(root: Path, issue_id: str, ticket_path: Path, ticket: dict[str, Any], issue: dict[str, Any], check: str, errors: list[str], warnings: list[str]) -> dict[str, Any]:
    plan_hash = plan_input_hash(ticket) if ticket else file_hash(ticket_path)
    bead_hash = sha256_text(stable_json(hard_bead_snapshot(issue)))
    contracts_hash = command_contracts_hash(root)
    envelope = approval_envelope_status(ticket, issue, plan_hash, bead_hash, contracts_hash)
    projection_hash = approval_hash(ticket, issue, bead_hash, contracts_hash) if check in {"validate", "execute", "review"} else ""
    drift_hash = drift_observation_hash(issue, ticket) if check in {"validate", "execute", "review"} else ""
    strict_hashes = strict_artifact_hashes(root, ticket) if ticket.get("mode") == "strict" else {}
    run_id = f"beo_check:{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')}:{hashlib.sha1(os.urandom(8)).hexdigest()[:8]}"
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
        "helper_version": HELPER_VERSION,
        "helper_run_id": run_id,
        "strict_artifact_hashes": strict_hashes,
        "machine_hashes": {
            "approval_projection_hash": projection_hash,
            "drift_observation_hash": drift_hash,
            "plan_input_hash": plan_hash,
            "bead_snapshot_hash": bead_hash,
            "command_contracts_hash": contracts_hash,
            "strict_artifact_hashes": strict_hashes,
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


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description="BEO-on-Beads integrity checker")
    parser.add_argument("--issue", required=True)
    parser.add_argument("--ticket")
    parser.add_argument("--root", default=".")
    parser.add_argument("--check", choices=["identity", "validate", "execute", "review"], required=True)
    parser.add_argument("--phase", choices=sorted(PHASE_ALIASES), help="Optional owner-boundary check for future-owned fields")
    parser.add_argument("--format", choices=["json"], default="json")
    parser.add_argument("--no-write", action="store_true", help="Do not persist helper evidence; intended for unit tests only")
    args = parser.parse_args(argv)

    root = Path(args.root).resolve()
    sync_constants_with_registry(root)
    ticket_path = Path(args.ticket).resolve() if args.ticket else ticket_path_for(root, args.issue).resolve()
    errors: list[str] = []
    warnings: list[str] = []
    try:
        ticket = read_ticket(ticket_path)
    except Exception as exc:
        ticket = {}
        errors.append(f"ticket parse failed: {exc}")
    issue, issue_error = run_br_show(root, args.issue)
    if issue_error:
        errors.append(issue_error)
        issue = {"id": args.issue}
    if ticket:
        errors.extend(validate_identity(root, args.issue, ticket_path, ticket, issue))
        errors.extend(validate_runtime_events(ticket, args.issue, root))
        if args.phase:
            errors.extend(validate_phase_boundary(ticket, PHASE_ALIASES[args.phase]))
    if args.check in {"validate", "execute", "review"} and ticket:
        errors.extend(validate_plan(root, ticket, issue))
    if args.check == "validate" and ticket:
        errors.extend(validate_same_scope_repair_request(ticket))
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
