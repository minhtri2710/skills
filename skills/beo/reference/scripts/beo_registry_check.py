#!/usr/bin/env python3
from __future__ import annotations

import sys
from pathlib import Path

from beo_utils import load_json

# Import split submodules
import beo_registry_commands
import beo_registry_pipeline
import beo_registry_profiles

DEFAULT_REGISTRY = Path(__file__).resolve().parents[1] / "registry"
REFERENCE_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_REGISTRIES = [
    "command-contracts.json",
    "pipeline.json",
    "profiles.json",
    "ticket-schema.json",
    "registry.schema.json",
]

NEW_REFERENCES = [
    "doctrine-map.md",
    "kernel.md",
    "lifecycle.md",
    "safety.md",
    "degraded-tools.md",
    "registry-authoring.md",
]

def validate_schema_targets(registry: Path, errors: list[str]) -> None:
    schema_path = registry / "registry.schema.json"
    for name in REQUIRED_REGISTRIES:
        data = load_json(registry / name, {})
        schema_ref = data.get("$schema")
        if isinstance(schema_ref, str) and schema_ref.startswith("./registry.schema.json") and not schema_path.exists():
            errors.append(f"{name} references missing registry.schema.json")

def validate_refs(errors: list[str]) -> None:
    refs = REFERENCE_ROOT / "references"
    for name in NEW_REFERENCES:
        if not (refs / name).exists():
            errors.append(f"missing reference: {name}")
    safety = refs / "safety.md"
    if safety.exists():
        text = safety.read_text()
        if "profiles.json` `protected_path_defaults` is the canonical source" not in text:
            errors.append("safety.md must defer protected path defaults to profiles.json")

def validate_ticket_schema(registry: Path, errors: list[str]) -> None:
    schema = load_json(registry / "ticket-schema.json", {})
    future = schema.get("future_owned_field_rule")
    if not isinstance(future, dict):
        errors.append("ticket-schema.future_owned_field_rule must be object")
    if "learning" in schema:
        errors.append("ticket-schema must not define a normal learning delivery field")
    owner_fields = schema.get("owner_fields")
    if isinstance(owner_fields, dict):
        for owner, fields in owner_fields.items():
            if isinstance(fields, list) and "learning" in fields:
                errors.append(f"ticket-schema.owner_fields.{owner} must not include normal learning field")
            if isinstance(fields, list) and "runtime_events" in fields:
                errors.append(f"ticket-schema.owner_fields.{owner} must not include runtime_events; use events_file")
    if "done_target" not in schema.get("required_plan_intake_fields", []):
        errors.append("ticket-schema.required_plan_intake_fields must include done_target")
    if not isinstance(schema.get("done_semantics"), dict):
        errors.append("ticket-schema.done_semantics is required")
    if not schema.get("soft_field_rule"):
        errors.append("ticket-schema.soft_field_rule is required")
    human_gates = schema.get("human_gates") if isinstance(schema.get("human_gates"), dict) else {}
    if not human_gates.get("authorization_gate_required_fields") or not human_gates.get("authorization_gate_validity"):
        errors.append("ticket-schema.human_gates must define authorization gate scope/validity fields")
    if not isinstance(schema.get("prestate_refs"), dict):
        errors.append("ticket-schema.prestate_refs is required")
    if set(schema.get("validation_failure_subreasons", [])) != {"fail_atomicity", "fail_scope", "fail_profile", "fail_human_gate", "fail_schema"}:
        errors.append("ticket-schema.validation_failure_subreasons must match canonical validation taxonomy")
    minimal = schema.get("minimal_ticket", {}).get("beo.ticket", {}) if isinstance(schema.get("minimal_ticket"), dict) else {}
    forbidden = {"readiness", "approval_ref", "integrity", "execution", "review"}
    present = sorted(forbidden & set(minimal))
    if present:
        errors.append(f"minimal ticket contains future-owned fields: {present}")

def main(argv: list[str]) -> int:
    if argv and (argv[0].startswith("-") or len(argv) > 1):
        print("Usage: beo_registry_check.py [registry_directory_path]", file=sys.stderr)
        return 1
    registry = Path(argv[0]).resolve() if argv else DEFAULT_REGISTRY
    errors: list[str] = []

    for name in REQUIRED_REGISTRIES:
        if not (registry / name).exists():
            errors.append(f"missing registry: {name}")

    validate_schema_targets(registry, errors)
    beo_registry_commands.validate_commands(registry, errors)
    beo_registry_pipeline.validate_pipeline(registry, errors)
    beo_registry_profiles.validate_profiles(registry, errors)
    validate_ticket_schema(registry, errors)
    validate_refs(errors)

    if errors:
        for message in errors:
            print(f"ERROR: {message}", file=sys.stderr)
        return 1
    print("BEO registry check passed")
    return 0

if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
