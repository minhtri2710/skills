#!/usr/bin/env python3
"""Validate BEO registry cross-file consistency."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

DEFAULT_REGISTRY_ROOT = Path(__file__).resolve().parents[1] / "registry"
REGISTRY_ROOT = DEFAULT_REGISTRY_ROOT
SKILLS_ROOT = Path(__file__).resolve().parents[2]


def load_json(name: str) -> dict[str, Any]:
    return json.loads((REGISTRY_ROOT / name).read_text())


def error(errors: list[str], message: str) -> None:
    errors.append(message)


def require_object(errors: list[str], filename: str, data: Any, fields: list[str]) -> None:
    if not isinstance(data, dict):
        error(errors, f"{filename} schema error at <root>: expected object")
        return
    for field in fields:
        if field not in data:
            error(errors, f"{filename} schema error at <root>: missing required field {field}")


def require_array(errors: list[str], filename: str, data: dict[str, Any], field: str) -> None:
    if field in data and not isinstance(data[field], list):
        error(errors, f"{filename} schema error at {field}: expected array")


def resolve_schema_ref(schema: Any, root_schema: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(schema, dict):
        return {}
    ref = schema.get("$ref")
    definitions = root_schema.get("definitions", {})
    if isinstance(ref, str) and ref.startswith("#/definitions/") and isinstance(definitions, dict):
        resolved = definitions.get(ref.rsplit("/", 1)[-1], {})
        return resolved if isinstance(resolved, dict) else {}
    return schema


def validate_schema_node(errors: list[str], filename: str, path: str, data: Any, schema: Any, root_schema: dict[str, Any]) -> None:
    schema = resolve_schema_ref(schema, root_schema)
    if not schema:
        error(errors, f"{filename} schema error at {path}: invalid registry schema node")
        return
    expected_type = schema.get("type")
    if expected_type not in {"object", "array", "string", "boolean"}:
        error(errors, f"registry.schema.json schema error at {path}.type: expected supported type")
        return
    min_length = schema.get("minLength")
    if "minLength" in schema and (not isinstance(min_length, int) or isinstance(min_length, bool) or min_length < 0):
        error(errors, f"registry.schema.json schema error at {path}.minLength: expected non-negative integer")
    enum_values = schema.get("enum")
    if "enum" in schema and not isinstance(enum_values, list):
        error(errors, f"registry.schema.json schema error at {path}.enum: expected array")
    elif isinstance(enum_values, list) and data not in enum_values:
        error(errors, f"{filename} schema error at {path}: expected one of {enum_values}")
    if expected_type == "object":
        if not isinstance(data, dict):
            error(errors, f"{filename} schema error at {path}: expected object")
            return
        required = schema.get("required", [])
        if not isinstance(required, list):
            error(errors, f"registry.schema.json schema error at {path}.required: expected array")
            required = []
        for field in required:
            if not isinstance(field, str):
                error(errors, f"registry.schema.json schema error at {path}.required: expected string entries")
            elif field not in data:
                error(errors, f"{filename} schema error at {path}: missing required field {field}")
        properties = schema.get("properties", {})
        if not isinstance(properties, dict):
            error(errors, f"registry.schema.json schema error at {path}.properties: expected object")
            properties = {}
        additional_properties = schema.get("additionalProperties")
        if "additionalProperties" in schema and not isinstance(additional_properties, (bool, dict)):
            error(errors, f"registry.schema.json schema error at {path}.additionalProperties: expected boolean or object")
        for key, value in data.items():
            if key in properties:
                validate_schema_node(errors, filename, f"{path}.{key}" if path != "<root>" else key, value, properties[key], root_schema)
            elif additional_properties is False:
                error(errors, f"{filename} schema error at {path}: unexpected field {key}")
            elif isinstance(additional_properties, dict):
                validate_schema_node(errors, filename, f"{path}.{key}" if path != "<root>" else key, value, additional_properties, root_schema)
    elif expected_type == "array":
        min_items = schema.get("minItems")
        if "minItems" in schema and (not isinstance(min_items, int) or isinstance(min_items, bool) or min_items < 0):
            error(errors, f"registry.schema.json schema error at {path}.minItems: expected non-negative integer")
        item_schema = schema.get("items")
        if "items" in schema and not isinstance(item_schema, dict):
            error(errors, f"registry.schema.json schema error at {path}.items: expected object")
        if not isinstance(data, list):
            error(errors, f"{filename} schema error at {path}: expected array")
            return
        if isinstance(min_items, int) and not isinstance(min_items, bool) and len(data) < min_items:
            error(errors, f"{filename} schema error at {path}: expected at least {min_items} item(s)")
        if isinstance(item_schema, dict):
            for index, item in enumerate(data):
                validate_schema_node(errors, filename, f"{path}[{index}]", item, item_schema, root_schema)
    elif expected_type == "string":
        if not isinstance(data, str):
            error(errors, f"{filename} schema error at {path}: expected string")
        elif isinstance(min_length, int) and not isinstance(min_length, bool) and len(data) < min_length:
            error(errors, f"{filename} schema error at {path}: expected at least {min_length} character(s)")
    elif expected_type == "boolean" and not isinstance(data, bool):
        error(errors, f"{filename} schema error at {path}: expected boolean")


def validate_registry_schemas(errors: list[str], schema: dict[str, Any], registries: dict[str, tuple[str, dict[str, Any]]]) -> None:
    definitions = schema.get("definitions", {})
    if not isinstance(definitions, dict):
        error(errors, "registry.schema.json schema error at definitions: expected object")
        return
    for filename, (definition, payload) in registries.items():
        definition_schema = definitions.get(definition)
        if not isinstance(definition_schema, dict):
            error(errors, f"{filename} schema definition missing: {definition}")
            continue
        validate_schema_node(errors, filename, "<root>", payload, definition_schema, schema)


def validate_basic_shapes(errors: list[str], registries: dict[str, tuple[str, dict[str, Any]]]) -> None:
    required = {
        "vocabulary.json": ["runtime_owners", "owner_classes", "utilities", "terminal_targets", "meta_targets", "artifact_density", "artifact_density_output", "readiness", "execution_mode", "integrity_status", "field_status", "debug_unblock_class"],
        "learning-vocabulary.json": ["learning_case_status", "learning_pattern_status", "learning_case_types", "learning_runtime_status"],
        "approval-envelope.json": ["approval_projection_rule", "required_fields"],
        "artifact-schemas.json": ["artifact_densities"],
        "command-contracts.json": ["commands"],
        "helper-output-schema.json": ["fields"],
        "pipeline.json": ["normal_path", "virtual_sources", "transitions", "invalid_transitions"],
    }
    array_fields = {
        "vocabulary.json": ["runtime_owners", "utilities", "terminal_targets", "meta_targets", "artifact_density", "artifact_density_output", "readiness", "execution_mode", "integrity_status", "field_status", "debug_unblock_class"],
        "approval-envelope.json": ["required_fields"],
        "command-contracts.json": ["commands"],
        "pipeline.json": ["normal_path", "virtual_sources", "transitions", "invalid_transitions"],
    }
    for filename, (_, payload) in registries.items():
        require_object(errors, filename, payload, required.get(filename, []))
        if isinstance(payload, dict):
            for field in array_fields.get(filename, []):
                require_array(errors, filename, payload, field)


def string_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str)}


def skill_name(text: str) -> str | None:
    match = re.search(r"(?m)^name:\s*(\S+)\s*$", text)
    return match.group(1) if match else None


def skill_exit_pairs(text: str) -> list[tuple[str, str]]:
    exits_section_match = re.search(r"(?ms)^## Exits\b(?P<body>.*?)(?=^## |\Z)", text)
    exits_text = exits_section_match.group("body") if exits_section_match else None
    if exits_text is None:
        contract_match = re.search(r"(?ms)^## Contract\b(?P<body>.*?)(?=^## |\Z)", text)
        if not contract_match:
            return []
        exits_match = re.search(r"(?ms)^Exits:\n(?P<body>(?:^- .*\n?)+)", contract_match.group("body"))
        if not exits_match:
            return []
        exits_text = exits_match.group("body")
    else:
        exits_match = re.search(r"(?ms)(?P<body>(?:^- .*\n?)+)", exits_text)
        if not exits_match:
            return []
        exits_text = exits_match.group("body")
    pairs: list[tuple[str, str]] = []
    for line in exits_text.splitlines():
        match = re.match(r"- `([^`]+)` -> `([^`]+)`", line)
        if match:
            pairs.append((match.group(1), match.group(2)))
    return pairs


def require_markers(errors: list[str], filename: str, text: str, markers: list[str]) -> None:
    for marker in markers:
        if marker not in text:
            error(errors, f"{filename} missing required marker: {marker}")


def validate_skill_contracts(errors: list[str], owners: set[str], utilities: set[str], pipeline: dict[str, Any]) -> None:
    transition_pairs = {
        (str(t.get("from")), str(t.get("condition_id")), str(t.get("to")))
        for t in pipeline.get("transitions", [])
        if isinstance(t, dict)
    }
    for path in sorted(SKILLS_ROOT.glob("*/SKILL.md")):
        text = path.read_text()
        owner = skill_name(text)
        rel = path.relative_to(SKILLS_ROOT)
        if owner not in owners and owner not in utilities:
            error(errors, f"{rel}: skill owner is not registered: {owner}")
            continue
        if owner in utilities:
            continue
        if "emit only condition IDs legal from" in text:
            error(errors, f"{rel}: exits must list explicit condition_id -> target pairs")
        exits = skill_exit_pairs(text)
        if not exits:
            error(errors, f"{rel}: no parseable exit condition_id -> target pairs")
        for condition_id, target in exits:
            if (owner, condition_id, target) not in transition_pairs:
                error(errors, f"{rel}: exit is not in pipeline: {condition_id} -> {target}")


def validate_operator_navigation_surfaces(errors: list[str], registry_root: Path) -> None:
    references = registry_root.parent / "references"
    required_files = {
        "operator-cockpit.md": [
            "<!-- beo:operator-cockpit -->",
            "<!-- beo:operator-cockpit:lane -->",
            "<!-- beo:operator-cockpit:owner -->",
            "<!-- beo:operator-cockpit:authority -->",
            "<!-- beo:operator-cockpit:mutation -->",
            "<!-- beo:operator-cockpit:human-gates -->",
            "<!-- beo:operator-cockpit:density -->",
            "<!-- beo:operator-cockpit:condition -->",
        ],
        "resume-resolution.md": [
            "<!-- beo:resume-resolution -->",
            "<!-- beo:resume-resolution:rule -->",
            "<!-- beo:resume-resolution:owner-orientation -->",
            "<!-- beo:resume-resolution:output -->",
            "<!-- beo:resume-resolution:route-boundary -->",
        ],
        "glossary.md": [
            "Authority: canonical terminology only",
            "PASS_EXECUTE",
            "Meta-target",
        ],
        "README.md": [
            "<!-- beo:reference-index -->",
            "<!-- beo:reference-tier:operator -->",
            "<!-- beo:reference-tier:runtime-authority -->",
            "<!-- beo:reference-tier:machine-registry-repair -->",
        ],
        "route-resolution.md": [
            "<!-- beo:route-resolution -->",
            "<!-- beo:route-resolution:meta-targets -->",
            "<!-- beo:route-resolution:operator-output -->",
        ],
    }
    for filename, required_markers in required_files.items():
        path = references / filename
        try:
            text = path.read_text()
        except FileNotFoundError:
            error(errors, f"{filename} is missing")
            continue
        require_markers(errors, filename, text, required_markers)
        if filename == "route-resolution.md":
            forbidden = [
                "<!-- beo:route-resolution:owner-table -->",
                "## Owner Resolution Table",
                "setup/usage request found in resume/repair artifacts",
            ]
            for forbidden_text in forbidden:
                if forbidden_text in text:
                    error(errors, f"route-resolution.md contains forbidden normal-resume content: {forbidden_text}")

    agents_template = registry_root.parent / "assets" / "AGENTS.template.md"
    try:
        text = agents_template.read_text()
    except FileNotFoundError:
        error(errors, "AGENTS.template.md is missing")
        return
    if "<!-- beo:agents:start-cockpit -->" not in text:
        error(errors, "AGENTS.template.md missing required marker: <!-- beo:agents:start-cockpit -->")
def validate_helper_output_refs(errors: list[str], helper_schema: dict[str, Any], vocabulary: dict[str, Any]) -> None:
    fields = helper_schema.get("fields", {})
    for field_name, field in fields.items():
        allowed_values_ref = field.get("allowed_values_ref")
        if allowed_values_ref is None:
            continue
        values = vocabulary.get(allowed_values_ref)
        if not isinstance(values, list) or not all(isinstance(item, str) for item in values):
            error(errors, f"helper-output-schema.json fields.{field_name}.allowed_values_ref points to unknown string-list vocabulary field: {allowed_values_ref}")


def validate_approval_required_fields(errors: list[str], approval_envelope: Any, vocabulary: dict[str, Any]) -> None:
    if not isinstance(approval_envelope, dict):
        return
    fields = approval_envelope.get("required_fields", [])
    if not isinstance(fields, list):
        return
    readiness_seen = False
    for index, field in enumerate(fields):
        if not isinstance(field, dict):
            continue
        field_id = field.get("id")
        if isinstance(field_id, str) and not field_id.strip():
            error(errors, f"approval-envelope.json required_fields[{index}].id must be non-blank")
        required_value = field.get("required_value")
        if field_id == "readiness":
            readiness_seen = True
            if not isinstance(required_value, str):
                error(errors, f"approval-envelope.json required_fields[{index}].readiness required_value is required")
                continue
        if isinstance(required_value, str):
            if not required_value.strip():
                error(errors, f"approval-envelope.json required_fields[{index}].required_value must be non-blank")
            elif required_value != required_value.strip():
                error(errors, f"approval-envelope.json required_fields[{index}].required_value must not have surrounding whitespace")
            elif field_id == "readiness" and required_value not in string_set(vocabulary.get("readiness", [])):
                error(errors, f"approval-envelope.json required_fields[{index}].required_value is not registered readiness: {required_value}")
    if not readiness_seen:
        error(errors, "approval-envelope.json readiness required field is missing")


def validate_invalid_transition_conflicts(errors: list[str], pipeline: dict[str, Any]) -> None:
    transitions = pipeline.get("transitions", [])
    invalid_transitions = pipeline.get("invalid_transitions", [])
    if not isinstance(transitions, list) or not isinstance(invalid_transitions, list):
        return
    for invalid in invalid_transitions:
        if not isinstance(invalid, dict):
            continue
        source = invalid.get("from")
        target = invalid.get("to")
        condition = invalid.get("condition_id")
        if not all(isinstance(item, str) for item in [source, target, condition]):
            continue
        for transition in transitions:
            if not isinstance(transition, dict):
                continue
            legal_condition = transition.get("condition_id")
            if (
                transition.get("from") == source
                and transition.get("to") == target
                and (condition == "any" or condition == legal_condition)
            ):
                error(
                    errors,
                    f"pipeline invalid transition conflicts with legal transition: {source} {condition} -> {target} conflicts with {legal_condition}",
                )
                break


def validate_forbidden_aliases(errors: list[str], style_policy: dict[str, Any], vocabulary: dict[str, Any]) -> None:
    aliases = style_policy.get("forbidden_aliases", {})
    enum_values = {
        item
        for key, values in vocabulary.items()
        if isinstance(values, list)
        for item in values
        if isinstance(item, str)
    }
    for alias, guidance in aliases.items():
        if alias in enum_values and guidance == "invalid":
            error(errors, f"style-policy.json forbidden_aliases.{alias} conflicts with registered vocabulary value")
        if guidance.startswith("invalid"):
            continue
        match = re.match(r"use\s+(\S+)", guidance)
        if match and match.group(1) not in enum_values:
            error(errors, f"style-policy.json forbidden_aliases.{alias} points to unknown value: {match.group(1)}")


def main() -> int:
    global REGISTRY_ROOT
    if len(sys.argv) > 2:
        print(json.dumps({"status": "invalid", "errors": ["usage: beo_registry_check.py [registry-root]"]}, indent=2))
        return 2
    if len(sys.argv) == 2:
        REGISTRY_ROOT = Path(sys.argv[1])
    errors: list[str] = []
    try:
        schema = load_json("registry.schema.json")
        vocabulary = load_json("vocabulary.json")
        pipeline = load_json("pipeline.json")
        artifact_schemas = load_json("artifact-schemas.json")
        approval_envelope = load_json("approval-envelope.json")
        helper_output_schema = load_json("helper-output-schema.json")
        style_policy = load_json("style-policy.json")
        registries = {
            "vocabulary.json": ("core-vocabulary", vocabulary),
            "style-policy.json": ("style-policy", style_policy),
            "learning-vocabulary.json": ("learning-vocabulary", load_json("learning-vocabulary.json")),
            "approval-envelope.json": ("approval-envelope", approval_envelope),
            "artifact-schemas.json": ("artifact-schemas", artifact_schemas),
            "command-contracts.json": ("command-contracts", load_json("command-contracts.json")),
            "helper-output-schema.json": ("helper-output-schema", helper_output_schema),
            "pipeline.json": ("pipeline", pipeline),
        }
    except Exception as exc:  # noqa: BLE001
        print(json.dumps({"status": "invalid", "errors": [f"registry load failed: {exc}"]}, indent=2))
        return 2

    if not isinstance(schema, dict):
        print(json.dumps({"status": "invalid", "errors": ["registry.schema.json schema error at <root>: expected object"]}, indent=2))
        return 1

    validate_basic_shapes(errors, registries)
    validate_registry_schemas(errors, schema, registries)
    validate_approval_required_fields(errors, approval_envelope, vocabulary)
    if errors:
        print(json.dumps({"status": "invalid", "errors": errors}, indent=2))
        return 1

    validate_operator_navigation_surfaces(errors, REGISTRY_ROOT)
    owners = string_set(vocabulary.get("runtime_owners", []))
    utilities = string_set(vocabulary.get("utilities", []))
    terminal_targets = string_set(vocabulary.get("terminal_targets", []))
    meta_targets = string_set(vocabulary.get("meta_targets", []))
    virtual_sources = string_set(pipeline.get("virtual_sources", []))
    all_targets = owners | utilities | terminal_targets | meta_targets
    all_sources = owners | virtual_sources

    owner_classes = vocabulary.get("owner_classes", {})
    if isinstance(owner_classes, dict):
        assignments: dict[str, list[str]] = {}
        for class_name, values in owner_classes.items():
            if not isinstance(values, list):
                continue
            for item in values:
                if isinstance(item, str):
                    assignments.setdefault(item, []).append(str(class_name))
        classified = set(assignments)
        duplicates = {owner: classes for owner, classes in assignments.items() if len(classes) > 1}
        if duplicates:
            error(errors, f"owner_classes assigns owners to multiple classes: {duplicates}")
        expected_classified = owners | utilities
        if classified != expected_classified:
            error(errors, f"owner_classes must partition runtime owners and utilities: expected {sorted(expected_classified)}, got {sorted(classified)}")
        utility_class = string_set(owner_classes.get("utility", []))
        if utility_class != utilities:
            error(errors, f"owner_classes.utility must match utilities: expected {sorted(utilities)}, got {sorted(utility_class)}")

    for required_owner in ["beo-explore", "beo-plan", "beo-validate", "beo-execute", "beo-review"]:
        if required_owner not in owners:
            error(errors, f"missing owner: {required_owner}")

    for terminal in ["done", "user"]:
        if terminal not in terminal_targets:
            error(errors, f"missing terminal target: {terminal}")
        if terminal in owners:
            error(errors, f"terminal target listed as owner: {terminal}")
        if terminal in utilities:
            error(errors, f"terminal target listed as utility: {terminal}")

    if "beo-reference" in owners:
        error(errors, "beo-reference must be a utility, not a runtime owner")
    if "beo-reference" not in utilities:
        error(errors, "missing utility: beo-reference")

    for meta in ["return_to_caller", "restored_owner"]:
        if meta not in meta_targets:
            error(errors, f"missing meta target: {meta}")

    for unblock_class in ["bounded_plan_repair", "user_owned", "return_to_caller", "inconclusive"]:
        if unblock_class not in string_set(vocabulary.get("debug_unblock_class", [])):
            error(errors, f"missing debug_unblock_class: {unblock_class}")

    for transition in pipeline.get("transitions", []):
        target = transition.get("to")
        source = transition.get("from")
        if target not in all_targets:
            error(errors, f"pipeline transition target is not registered: {target}")
        if source not in all_sources:
            error(errors, f"pipeline transition source is not registered: {source}")
        if source in utilities:
            error(errors, f"utility must not appear as pipeline source: {source}")
        target_class = transition.get("target_class")
        expected_class = (
            "runtime_owner" if target in owners else
            "utility" if target in utilities else
            "terminal" if target in terminal_targets else
            "meta" if target in meta_targets else
            None
        )
        if expected_class and target_class != expected_class:
            error(errors, f"pipeline target_class mismatch for {source} {transition.get('condition_id')} -> {target}: expected {expected_class}, got {target_class!r}")

    validate_invalid_transition_conflicts(errors, pipeline)
    validate_skill_contracts(errors, owners, utilities, pipeline)
    validate_helper_output_refs(errors, helper_output_schema, vocabulary)
    validate_forbidden_aliases(errors, style_policy, vocabulary)

    densities = artifact_schemas.get("artifact_densities", {})
    if "human_gate_shape" not in artifact_schemas.get("shared_shapes", {}):
        error(errors, "shared_shapes missing human_gate_shape")
    else:
        gate_items = artifact_schemas.get("shared_shapes", {}).get("human_gate_shape", {}).get("gates", [])
        if gate_items and isinstance(gate_items[0], dict):
            for forbidden in ["severity", "blocking", "approval_bearing"]:
                if forbidden in gate_items[0]:
                    error(errors, f"human_gate_shape must not define {forbidden}; Human Gates are approval-bearing by definition")
    if "human_gate_shape" in densities.get("compact", {}):
        error(errors, "compact artifact density must not define human_gate_shape; use shared_shapes.human_gate_shape")

    compact = densities.get("compact", {})
    compact_authority_blocks = compact.get("authority_blocks", []) if isinstance(compact, dict) else []
    if compact_authority_blocks != ["yaml beo.ticket"]:
        error(errors, f"compact authority_blocks must be yaml beo.ticket only, got {compact_authority_blocks!r}")
    compact_field_ownership = compact.get("field_ownership") if isinstance(compact, dict) else None
    if not isinstance(compact_field_ownership, dict) or not compact_field_ownership:
        error(errors, "compact field_ownership must be a non-empty object")
    else:
        invalid_compact_owners = sorted(owner for owner in compact_field_ownership if owner not in owners)
        if invalid_compact_owners:
            error(errors, f"compact field_ownership owners must be runtime owners: {invalid_compact_owners}")
        malformed_compact_fields = sorted(
            owner for owner, fields in compact_field_ownership.items()
            if not isinstance(fields, list)
            or not fields
            or any(not isinstance(field, str) or not field.strip() for field in fields)
        )
        if malformed_compact_fields:
            error(errors, f"compact field_ownership fields must be non-empty strings for owners: {malformed_compact_fields}")
        expected_compact_owners = string_set(owner_classes.get("runtime_delivery", []) if isinstance(owner_classes, dict) else []) | {"beo-route"}
        if set(compact_field_ownership) != expected_compact_owners:
            error(errors, f"compact field_ownership keys must match compact artifact owners: expected {sorted(expected_compact_owners)}, got {sorted(compact_field_ownership)}")
        identity_seed_fields = {"artifact_density", "phase_status", "current_owner", "owner"}
        explore_fields = string_set(compact_field_ownership.get("beo-explore", []))
        missing_seed_fields = sorted(identity_seed_fields - explore_fields)
        if missing_seed_fields:
            error(errors, f"compact field_ownership.beo-explore missing identity seed fields: {missing_seed_fields}")
        handoff_identity_fields = {"phase_status", "current_owner", "owner"}
        for owner in sorted(expected_compact_owners):
            owner_fields = string_set(compact_field_ownership.get(owner, []))
            missing_handoff_fields = sorted(handoff_identity_fields - owner_fields)
            if missing_handoff_fields:
                error(errors, f"compact field_ownership.{owner} missing handoff identity fields: {missing_handoff_fields}")

    if "compact_derived" not in string_set(approval_envelope.get("approval_projection_rule", [])):
        error(errors, "approval_projection_rule missing compact_derived")
    if approval_envelope.get("compact_input_rule") != "compact_derived":
        error(errors, f"compact_input_rule must be compact_derived, got {approval_envelope.get('compact_input_rule')!r}")
    non_compact_authority_sources = [
        field.get("compact_source")
        for field in approval_envelope.get("required_fields", [])
        if isinstance(field, dict)
        and isinstance(field.get("compact_source"), str)
        and not field.get("compact_source", "").startswith("TICKET.md `beo.ticket` ")
    ]
    if non_compact_authority_sources:
        error(errors, f"approval envelope compact sources must use exact TICKET.md `beo.ticket` authority source: {non_compact_authority_sources}")

    for density in ["compact", "full"]:
        phase_sections = densities.get(density, {}).get("phase_sections", {})
        plan = phase_sections.get("plan", {})
        plan_fields = plan.get("required_after_owner_exit", [])
        projection = plan.get("derived_approval_projection", {}) if isinstance(plan, dict) else {}
        fields_or_projection = set(plan_fields)
        if isinstance(projection, dict):
            fields_or_projection.update(projection)
        if "execution_sets" not in fields_or_projection:
            error(errors, f"{density} plan fields missing execution_sets")
        if "acceptance_criteria" not in fields_or_projection:
            error(errors, f"{density} plan fields missing acceptance_criteria")
        if "acceptance_refs" in fields_or_projection:
            error(errors, f"{density} plan fields must use acceptance_criteria as canonical field")

    compact_projection = densities.get("compact", {}).get("phase_sections", {}).get("plan", {}).get("derived_approval_projection", {})
    if isinstance(compact_projection, dict) and compact_projection.get("acceptance_criteria") != "acceptance_criteria":
        error(errors, f"compact acceptance_criteria projection must use plan-owned acceptance_criteria, got {compact_projection.get('acceptance_criteria')!r}")

    approval_fields = {
        field.get("id") for field in approval_envelope.get("required_fields", [])
        if isinstance(field, dict)
    }
    for required in ["acceptance_criteria", "execution_sets"]:
        if required not in approval_fields:
            error(errors, f"approval envelope missing {required}")
    if "acceptance_refs" in approval_fields:
        error(errors, "approval envelope must use acceptance_criteria as canonical field")

    human_gates = [
        field for field in approval_envelope.get("required_fields", [])
        if isinstance(field, dict) and field.get("id") == "human_gates"
    ]
    if not human_gates:
        error(errors, "approval envelope missing human_gates")
    else:
        full_source = human_gates[0].get("full_source")
        if full_source != "CONTEXT.md#human_gates":
            error(errors, f"human_gates full_source must be CONTEXT.md#human_gates, got {full_source!r}")

    if errors:
        print(json.dumps({"status": "invalid", "errors": errors}, indent=2))
        return 1

    print(json.dumps({"status": "valid", "errors": []}, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
