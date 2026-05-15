#!/usr/bin/env python3
"""Read-only strict BEO approval/integrity evidence verifier."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

try:
    import yaml
    from yaml.events import AliasEvent
except Exception as exc:  # noqa: BLE001
    yaml = None
    AliasEvent = None
    _YAML_ERROR = str(exc)
else:
    _YAML_ERROR = None

REGISTRY_ROOT = Path(__file__).resolve().parents[1] / "registry"
RFC3339_UTC_RE = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")
AUTHORITY_FENCE_RE = re.compile(r"```(?P<kind>[^\s`]+)\s+(?P<schema>beo\.[\w_.-]+)\n(?P<body>.*?)\n```", re.S)

_REGISTRY_ERROR: str | None = None
try:
    VOCAB = json.loads((REGISTRY_ROOT / "vocabulary.json").read_text())
    APPROVAL_ENVELOPE = json.loads((REGISTRY_ROOT / "approval-envelope.json").read_text())
    ARTIFACT_SCHEMAS = json.loads((REGISTRY_ROOT / "artifact-schemas.json").read_text())
except Exception as exc:  # noqa: BLE001
    VOCAB = {}
    APPROVAL_ENVELOPE = {}
    ARTIFACT_SCHEMAS = {}
    _REGISTRY_ERROR = str(exc)
if _YAML_ERROR and not _REGISTRY_ERROR:
    _REGISTRY_ERROR = _YAML_ERROR


def registry_unavailable(message: str) -> None:
    global _REGISTRY_ERROR
    if not _REGISTRY_ERROR:
        _REGISTRY_ERROR = message


def registry_string_list(payload: Any, field: str, default: list[str]) -> list[str]:
    if not isinstance(payload, dict):
        registry_unavailable("registry payload must be an object")
        return default
    value = payload.get(field, default)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        registry_unavailable(f"registry field {field} must be a list of strings")
        return default
    return value


def approval_required_fields() -> list[dict[str, Any]]:
    if not isinstance(APPROVAL_ENVELOPE, dict):
        registry_unavailable("approval-envelope registry must be an object")
        return []
    if "required_fields" not in APPROVAL_ENVELOPE:
        registry_unavailable("approval-envelope required_fields must be a list of objects")
        return []
    fields = APPROVAL_ENVELOPE.get("required_fields")
    if not isinstance(fields, list) or not all(isinstance(field, dict) for field in fields):
        registry_unavailable("approval-envelope required_fields must be a list of objects")
        return []
    for index, field in enumerate(fields):
        if not isinstance(field.get("id"), str) or not field.get("id"):
            registry_unavailable(f"approval-envelope required_fields[{index}].id must be a non-empty string")
            return []
    return fields


def registry_required_string_list(payload: Any, object_field: str, list_field: str) -> list[str]:
    if not isinstance(payload, dict) or object_field not in payload:
        registry_unavailable(f"registry field {object_field} must be an object")
        return []
    value = payload.get(object_field)
    if not isinstance(value, dict):
        registry_unavailable(f"registry field {object_field} must be an object")
        return []
    if list_field not in value:
        registry_unavailable(f"registry field {object_field}.{list_field} must be a list of strings")
        return []
    return registry_string_list(value, list_field, [])


def required_readiness(default: str = "PASS_EXECUTE") -> str:
    for field in approval_required_fields():
        if field.get("id") != "readiness":
            continue
        value = field.get("required_value")
        if isinstance(value, str) and value:
            return value
        registry_unavailable("approval-envelope readiness required_value must be a string")
        return default
    registry_unavailable("approval-envelope readiness required field is missing")
    return default


SUPPORTED_DENSITIES = set(registry_string_list(VOCAB, "artifact_density", ["compact", "full"]))
SUPPORTED_MODES = set(registry_string_list(VOCAB, "execution_mode", []))
SUPPORTED_EXECUTION_SET_KINDS = set(registry_string_list(VOCAB, "execution_set_kind", []))
SUPPORTED_LIFECYCLE_STATUSES = set(registry_string_list(VOCAB, "lifecycle_status", []))
SUPPORTED_MANIFEST_OWNERS = set(registry_string_list(VOCAB, "runtime_owners", [])) | set(registry_string_list(VOCAB, "utilities", []))
HUMAN_GATE_TYPES = set(registry_string_list(VOCAB, "human_gate_type", []))
HUMAN_GATE_AFFECTS = set(registry_string_list(VOCAB, "human_gate_affects", []))
INTEGRITY_STATUSES = set(registry_string_list(VOCAB, "integrity_status", ["verified", "invalid", "unavailable"]))
REQUIRED_READINESS = required_readiness()
APPROVAL_PROJECTION_RULES = registry_string_list(APPROVAL_ENVELOPE, "approval_projection_rule", [])
APPROVAL_REF_REQUIRED_FIELDS = registry_required_string_list(APPROVAL_ENVELOPE, "approval_ref_schema", "required")
MANIFEST_REQUIRED_FIELDS = registry_required_string_list(ARTIFACT_SCHEMAS, "manifest_schema", "required")


class StrictYamlLoader(yaml.SafeLoader if yaml is not None else object):
    def compose_node(self, parent: Any, index: Any) -> Any:
        event = self.peek_event()
        if AliasEvent is not None and self.check_event(AliasEvent):
            raise yaml.YAMLError(f"YAML aliases are not supported: {event.anchor}")
        anchor = getattr(event, "anchor", None)
        if anchor is not None:
            raise yaml.YAMLError(f"YAML anchors are not supported: {anchor}")
        node = super().compose_node(parent, index)
        allowed_tags = {
            "tag:yaml.org,2002:map",
            "tag:yaml.org,2002:seq",
            "tag:yaml.org,2002:str",
            "tag:yaml.org,2002:int",
            "tag:yaml.org,2002:float",
            "tag:yaml.org,2002:bool",
            "tag:yaml.org,2002:null",
        }
        if node.tag not in allowed_tags:
            raise yaml.YAMLError(f"unsupported YAML tag: {node.tag}")
        return node


def construct_mapping_no_duplicates(loader: StrictYamlLoader, node: yaml.nodes.MappingNode, deep: bool = False) -> dict[Any, Any]:
    mapping: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if not isinstance(key, str):
            raise yaml.YAMLError(f"mapping keys must be strings: {key!r}")
        if key in mapping:
            raise yaml.YAMLError(f"duplicate key: {key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


if yaml is not None:
    StrictYamlLoader.add_constructor(
        yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
        construct_mapping_no_duplicates,
    )


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def stable_hash(data: Any) -> str:
    return sha256_bytes(json.dumps(data, sort_keys=True, separators=(",", ":")).encode())


def projection_rule_for_density(density: str) -> str:
    return "compact_shorthand_derived" if density == "compact" else "full_plan_explicit"


def approval_bearing_projection_hash(values: dict[str, Any]) -> str:
    return stable_hash(approval_fields_from_values(values, include_ref=True))


def integrity_status(value: Any) -> str | None:
    return value.get("status") if isinstance(value, dict) and isinstance(value.get("status"), str) else None


def validate_integrity(value: Any, path: str = "integrity") -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if not isinstance(value, dict):
        return [err("INTEGRITY_INVALID_SHAPE", path, "object with status and evidence_ref", type(value).__name__)]
    status = value.get("status")
    if status not in INTEGRITY_STATUSES:
        errors.append(err("MISMATCH", f"{path}.status", sorted(INTEGRITY_STATUSES), status))
    if status == "verified" and missing_non_empty_value(value.get("evidence_ref")):
        errors.append(err("MISSING_FIELD", f"{path}.evidence_ref", "non-empty value when status is verified", value.get("evidence_ref", "missing")))
    if status != "verified" and value.get("evidence_ref"):
        errors.append(err("MISMATCH", f"{path}.evidence_ref", "absent unless status is verified", value.get("evidence_ref")))
    return errors


def validate_pre_execution_integrity_check(value: Any, path: str = "pre_execution_integrity_check") -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if not isinstance(value, dict):
        return [err("MISSING_FIELD", path, "object", value if value is not None else "missing")]
    if value.get("helper") != "beo_approval_check":
        errors.append(err("MISMATCH", f"{path}.helper", "beo_approval_check", value.get("helper")))
    if missing_non_empty_value(value.get("evidence_ref")):
        errors.append(err("MISSING_FIELD", f"{path}.evidence_ref", "non-empty value", value.get("evidence_ref", "missing")))
    if value.get("approval_envelope_status") != "complete":
        errors.append(err("MISMATCH", f"{path}.approval_envelope_status", "complete", value.get("approval_envelope_status")))
    return errors


def sanitize_approval_ref(value: Any) -> Any:
    if not isinstance(value, dict):
        return value
    sanitized = json.loads(json.dumps(value))
    sanitized.pop("envelope_hash", None)
    sanitized.pop("artifact_hashes", None)
    return sanitized


def approval_fields_from_values(values: dict[str, Any], include_ref: bool = True) -> dict[str, Any]:
    projection: dict[str, Any] = {}
    for field in approval_required_fields():
        field_id = field.get("id")
        if not field_id or (field_id == "approval_ref" and not include_ref):
            continue
        value = values.get(field_id)
        if value is None:
            continue
        projection[field_id] = sanitize_approval_ref(value) if field_id == "approval_ref" else value
    return projection


def approval_envelope_hash(values: dict[str, Any]) -> str:
    return stable_hash(approval_fields_from_values(values, include_ref=True))


def err(code: str, path: str, expected: Any, observed: Any) -> dict[str, Any]:
    return {"code": code, "path": path, "expected": expected, "observed": observed}


def read_json(path: Path) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    try:
        parsed = json.loads(path.read_text())
    except FileNotFoundError:
        return None, err("MISSING_FIELD", str(path), "readable JSON object", "missing")
    except Exception as exc:  # noqa: BLE001
        return None, err("INVALID_JSON", str(path), "valid JSON object", str(exc))
    if not isinstance(parsed, dict):
        return None, err("INVALID_JSON", str(path), "JSON object", type(parsed).__name__)
    return parsed, None


def read_text(path: Path) -> tuple[str | None, dict[str, Any] | None]:
    try:
        return path.read_text(), None
    except FileNotFoundError:
        return None, err("MISSING_FIELD", str(path), "readable file", "missing")
    except Exception as exc:  # noqa: BLE001
        return None, err("UNREADABLE_FIELD", str(path), "readable file", str(exc))


def get_path(data: Any, dotted: str) -> Any:
    cur = data
    for part in dotted.split("."):
        if isinstance(cur, dict) and part in cur:
            cur = cur[part]
        else:
            return None
    return cur


def direct_key(data: Any, key: str) -> Any:
    if isinstance(data, dict):
        return data.get(key)
    return None


def parse_simple_yaml(body: str) -> Any:
    return yaml.load(body, Loader=StrictYamlLoader)


def authority_blocks(text: str, schema: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    blocks: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for match in AUTHORITY_FENCE_RE.finditer(text):
        matched_schema = match.group("schema")
        kind = match.group("kind").lower()
        if kind not in {"yaml", "yml"}:
            errors.append(err(
                "INVALID_AUTHORITY_BLOCK",
                matched_schema,
                f"```yaml {matched_schema}``` authority block",
                f"```{match.group('kind')} {matched_schema}```",
            ))
            continue
        if matched_schema != schema:
            continue
        body = match.group("body")
        try:
            parsed = parse_simple_yaml(body)
        except Exception as exc:  # noqa: BLE001
            errors.append(err("INVALID_AUTHORITY_BLOCK", schema, "parseable structured block", str(exc)))
            continue
        if not isinstance(parsed, dict):
            errors.append(err("INVALID_AUTHORITY_BLOCK", schema, "object", type(parsed).__name__))
            continue
        blocks.append(parsed)
    if len(blocks) > 1:
        errors.append(err("DUPLICATE_AUTHORITY_BLOCK", schema, "exactly one block", len(blocks)))
    return blocks, errors


def markdown_sections(text: str) -> dict[str, str]:
    sections: dict[str, list[str]] = {}
    current: str | None = None
    for line in text.splitlines():
        match = re.match(r"^##\s+(.+?)\s*$", line)
        if match:
            current = match.group(1).strip().lower()
            sections.setdefault(current, [])
            continue
        if current is not None:
            sections[current].append(line)
    return {key: "\n".join(lines).strip() for key, lines in sections.items()}


def state_feature_slug(root: Path) -> str | None:
    state, state_error = read_json(root / ".beads" / "STATE.json")
    if state_error or not state:
        return None
    candidates = [
        state.get("feature_slug"),
        state.get("feature"),
    ]
    active = state.get("active")
    if isinstance(active, dict):
        candidates.extend([active.get("feature_slug"), active.get("feature")])
    for candidate in candidates:
        if isinstance(candidate, str) and candidate.strip():
            return candidate.strip()
    return None


def validate_manifest_values(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    slug = manifest.get("feature_slug")
    if "schema_version" in manifest and manifest.get("schema_version") != ARTIFACT_SCHEMAS.get("manifest_schema", {}).get("schema_version"):
        errors.append(err("MISMATCH", "FEATURE.json.schema_version", ARTIFACT_SCHEMAS.get("manifest_schema", {}).get("schema_version"), manifest.get("schema_version")))
    if "feature_slug" in manifest and (not isinstance(slug, str) or not slug):
        errors.append(err("MISMATCH", "FEATURE.json.feature_slug", "non-empty string", slug))
    if isinstance(slug, str) and slug and "artifact_root" in manifest:
        expected_root = f".beads/artifacts/{slug}"
        if manifest.get("artifact_root") != expected_root:
            errors.append(err("MISMATCH", "FEATURE.json.artifact_root", expected_root, manifest.get("artifact_root")))
    if "beo_contract_version" in manifest and missing_non_empty_value(manifest.get("beo_contract_version")):
        errors.append(err("MISSING_FIELD", "FEATURE.json.beo_contract_version", "non-empty value", manifest.get("beo_contract_version")))
    if "lifecycle_status" in manifest and manifest.get("lifecycle_status") not in SUPPORTED_LIFECYCLE_STATUSES:
        errors.append(err("MISMATCH", "FEATURE.json.lifecycle_status", sorted(SUPPORTED_LIFECYCLE_STATUSES), manifest.get("lifecycle_status")))
    if "current_owner" in manifest and manifest.get("current_owner") not in SUPPORTED_MANIFEST_OWNERS:
        errors.append(err("MISMATCH", "FEATURE.json.current_owner", sorted(SUPPORTED_MANIFEST_OWNERS), manifest.get("current_owner")))
    for field in ["created_at", "updated_at"]:
        value = manifest.get(field)
        if field in manifest and (not isinstance(value, str) or not RFC3339_UTC_RE.match(value)):
            errors.append(err("INVALID_TIMESTAMP", f"FEATURE.json.{field}", "RFC3339 UTC Z", value))
    artifacts = manifest.get("artifacts")
    if "artifacts" in manifest and (not isinstance(artifacts, list) or not artifacts or not all(isinstance(item, str) and item for item in artifacts)):
        errors.append(err("MISMATCH", "FEATURE.json.artifacts", "non-empty list of strings", artifacts))
    return errors


def resolve_manifest(root: Path, feature_slug: str | None) -> tuple[Path | None, dict[str, Any] | None, list[dict[str, Any]]]:
    errors: list[dict[str, Any]] = []
    candidates: list[Path] = []
    if not feature_slug:
        feature_slug = state_feature_slug(root)
    if feature_slug:
        candidates.append(root / ".beads" / "artifacts" / feature_slug / "FEATURE.json")
        candidates.append(root / "FEATURE.json")
    else:
        candidates.extend(sorted((root / ".beads" / "artifacts").glob("*/FEATURE.json")) if (root / ".beads" / "artifacts").exists() else [])
        candidates.append(root / "FEATURE.json")
    existing = [p for p in candidates if p.exists()]
    if not existing:
        errors.append(err("MISSING_FEATURE_MANIFEST", str(root), "FEATURE.json under .beads/artifacts/<feature_slug>", "missing"))
        return None, None, errors
    if len(existing) > 1 and not feature_slug:
        errors.append(err("AMBIGUOUS_FEATURE_MANIFEST", str(root), "one FEATURE.json or feature_slug", [str(p) for p in existing]))
        return None, None, errors
    manifest_path = existing[0]
    manifest, json_error = read_json(manifest_path)
    if json_error:
        errors.append(json_error)
        return manifest_path.parent, None, errors
    assert manifest is not None
    for field in MANIFEST_REQUIRED_FIELDS:
        if field not in manifest:
            errors.append(err("MISSING_FIELD", f"FEATURE.json.{field}", "present", "missing"))
    errors.extend(validate_manifest_values(manifest))
    slug = manifest.get("feature_slug")
    direct_artifact_root = manifest_path.parent.resolve() == root.resolve()
    if direct_artifact_root:
        expected_root = root.resolve()
    else:
        expected_root = Path(str(root / ".beads" / "artifacts" / str(slug))).resolve() if slug else None
    if expected_root and manifest_path.parent.resolve() != expected_root:
        errors.append(err("INVALID_ARTIFACT_ROOT", str(manifest_path.parent), str(expected_root), str(manifest_path.parent.resolve())))
    if feature_slug and slug and feature_slug != slug:
        errors.append(err("MISMATCH", "FEATURE.json.feature_slug", feature_slug, slug))
    density = manifest.get("artifact_density")
    if density not in SUPPORTED_DENSITIES:
        errors.append(err("MISMATCH", "FEATURE.json.artifact_density", sorted(SUPPORTED_DENSITIES), density))
    return manifest_path.parent, manifest, errors


def validate_approval_ref(value: Any, density: str, selected: Any, mode: Any, hashes: dict[str, str]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if not isinstance(value, dict):
        return [err("APPROVAL_REF_INVALID_SHAPE", "approval_ref", "object", type(value).__name__)]
    required = APPROVAL_REF_REQUIRED_FIELDS
    missing = [field for field in required if field not in value]
    if missing:
        errors.append(err("MISSING_FIELD", "approval_ref", required, {"missing": missing}))
    for field in required:
        if field in value and missing_non_empty_value(value.get(field)):
            errors.append(err("MISSING_FIELD", f"approval_ref.{field}", "non-empty value", value.get(field)))
    if value.get("schema_version") != "beo.approval_ref.v1":
        errors.append(err("MISMATCH", "approval_ref.schema_version", "beo.approval_ref.v1", value.get("schema_version")))
    if value.get("approved_by_owner") != "beo-validate":
        errors.append(err("MISMATCH", "approval_ref.approved_by_owner", "beo-validate", value.get("approved_by_owner")))
    if not missing_non_empty_value(value.get("approved_at")) and not RFC3339_UTC_RE.match(str(value.get("approved_at"))):
        errors.append(err("INVALID_TIMESTAMP", "approval_ref.approved_at", "RFC3339 UTC Z", value.get("approved_at")))
    for key, expected in {"artifact_density": density, "selected_execution_set": selected, "execution_mode": mode, "approval_projection_rule": projection_rule_for_density(density)}.items():
        if value.get(key) != expected:
            errors.append(err("MISMATCH", f"approval_ref.{key}", expected, value.get(key)))
    if isinstance(APPROVAL_PROJECTION_RULES, list) and value.get("approval_projection_rule") not in APPROVAL_PROJECTION_RULES:
        errors.append(err("MISMATCH", "approval_ref.approval_projection_rule", APPROVAL_PROJECTION_RULES, value.get("approval_projection_rule")))
    expected_envelope_hash = hashes.get("approval_envelope")
    if expected_envelope_hash is not None and value.get("envelope_hash") != expected_envelope_hash:
        errors.append(err("MISMATCH", "approval_ref.envelope_hash", expected_envelope_hash, value.get("envelope_hash")))
    artifact_hashes = value.get("artifact_hashes")
    if not isinstance(artifact_hashes, dict):
        errors.append(err("MISMATCH", "approval_ref.artifact_hashes", "object", artifact_hashes))
    else:
        forbidden_keys = [key for key in artifact_hashes if "#approval_bearing_projection" in key or key in {"CONTEXT.md", "TICKET.md", "PLAN.md"}]
        if forbidden_keys:
            errors.append(err("DEPRECATED_FIELD", "approval_ref.artifact_hashes", "logical key approval_bearing_projection only", forbidden_keys))
        current = hashes.get("approval_bearing_projection")
        approved = artifact_hashes.get("approval_bearing_projection")
        if approved != current:
            errors.append(err("MISMATCH", "approval_ref.artifact_hashes.approval_bearing_projection", current, approved))
    return errors


def execution_set_ids(execution_sets: Any) -> set[str]:
    if not isinstance(execution_sets, list):
        return set()
    return {item["id"] for item in execution_sets if isinstance(item, dict) and isinstance(item.get("id"), str) and item.get("id")}


def approval_ref_id(value: Any) -> Any:
    return value.get("id") if isinstance(value, dict) else None


def validate_human_gates(gates: Any) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if not isinstance(gates, dict):
        return [err("HUMAN_GATES_INVALID_SHAPE", "human_gates", "object with status and gates", gates if gates is not None else "missing")]
    status = gates.get("status")
    gate_items = gates.get("gates", [])
    if status not in {"resolved", "unresolved", "not_applicable"}:
        errors.append(err("MISMATCH", "human_gates.status", ["resolved", "unresolved", "not_applicable"], status))
    if not isinstance(gate_items, list):
        errors.append(err("MISMATCH", "human_gates.gates", "list", type(gate_items).__name__))
        return errors
    unresolved = False
    for index, gate in enumerate(gate_items):
        if not isinstance(gate, dict):
            errors.append(err("MISMATCH", f"human_gates.gates[{index}]", "object", type(gate).__name__))
            unresolved = True
            continue
        for field in ["id", "question", "resolution_ref"]:
            if missing_non_empty_value(gate.get(field)):
                errors.append(err("MISSING_FIELD", f"human_gates.gates[{index}].{field}", "non-empty value", gate.get(field, "missing")))
                unresolved = True
        gate_type = gate.get("type")
        if gate_type not in HUMAN_GATE_TYPES:
            errors.append(err("MISMATCH", f"human_gates.gates[{index}].type", sorted(HUMAN_GATE_TYPES), gate_type))
            unresolved = True
        affects = gate.get("affects")
        if not isinstance(affects, list) or not affects:
            errors.append(err("MISMATCH", f"human_gates.gates[{index}].affects", "non-empty list", affects if affects is not None else "missing"))
            unresolved = True
        else:
            invalid_affects = [item for item in affects if item not in HUMAN_GATE_AFFECTS]
            if invalid_affects:
                errors.append(err("MISMATCH", f"human_gates.gates[{index}].affects", sorted(HUMAN_GATE_AFFECTS), invalid_affects))
                unresolved = True
        resolution_status = gate.get("resolution_status")
        if resolution_status not in {"resolved", "unresolved"}:
            errors.append(err("MISMATCH", f"human_gates.gates[{index}].resolution_status", ["resolved", "unresolved"], resolution_status))
            unresolved = True
        elif resolution_status != "resolved":
            unresolved = True
    expected = "not_applicable" if not gate_items else "unresolved" if unresolved else "resolved"
    if status != expected:
        errors.append(err("MISMATCH", "human_gates.status", expected, status))
    if status == "unresolved":
        errors.append(err("MISMATCH", "human_gates", "resolved or not_applicable", status))
    return errors


def gates_unresolved(gates: Any) -> bool:
    return bool(validate_human_gates(gates)) or (isinstance(gates, dict) and gates.get("status") == "unresolved")


def path_from_entry(value: Any) -> str | None:
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        path = value.get("path") or value.get("file")
        if isinstance(path, str):
            return path
    return None


def as_path_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if not isinstance(value, list):
        return []
    return [path for item in value if (path := path_from_entry(item)) is not None]


def validate_path_list_shape(value: Any, path: str) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    if value is None or isinstance(value, str):
        return errors
    if not isinstance(value, list):
        return [err("MISMATCH", path, "string or list of strings/path objects", type(value).__name__)]
    for index, item in enumerate(value):
        if path_from_entry(item) is None:
            errors.append(err("MISMATCH", f"{path}[{index}]", "string or object with string path/file", item))
    return errors


def unsafe_path(path: str) -> bool:
    normalized = path.replace("\\", "/")
    return path != path.strip() or normalized.startswith("/") or any(part in {"", ".", ".."} for part in normalized.split("/"))


def path_matches(path: str, pattern: str) -> bool:
    path = path.replace("\\", "/").rstrip("/")
    pattern = pattern.replace("\\", "/").rstrip("/")
    return path == pattern or path.startswith(pattern + "/")


def execution_set_file_entries(execution_set: dict[str, Any]) -> list[tuple[str, str]]:
    entries = [("execution_sets[].files", path) for path in as_path_list(execution_set.get("files"))]
    items = execution_set.get("items")
    if isinstance(items, list):
        for item in items:
            if isinstance(item, dict):
                entries.extend(("execution_sets[].items[].files", path) for path in as_path_list(item.get("files")))
    return entries


def selected_execution_files(values: dict[str, Any]) -> set[str]:
    selected = values.get("selected_execution_set")
    execution_sets = values.get("execution_sets")
    if not isinstance(selected, str) or not selected or not isinstance(execution_sets, list):
        return set()
    for execution_set in execution_sets:
        if not isinstance(execution_set, dict) or execution_set.get("id") != selected:
            continue
        return {path for _, path in execution_set_file_entries(execution_set)}
    return set()


def execution_file_entries(execution_sets: Any) -> list[tuple[str, str]]:
    entries: list[tuple[str, str]] = []
    if not isinstance(execution_sets, list):
        return entries
    for execution_set in execution_sets:
        if isinstance(execution_set, dict):
            entries.extend(execution_set_file_entries(execution_set))
    return entries


def validate_execution_sets(values: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    execution_sets = values.get("execution_sets")
    if not isinstance(execution_sets, list):
        return errors
    ids = execution_set_ids(execution_sets)
    for index, execution_set in enumerate(execution_sets):
        if not isinstance(execution_set, dict):
            errors.append(err("MISMATCH", f"execution_sets[{index}]", "object", type(execution_set).__name__))
            continue
        execution_set_id = execution_set.get("id")
        if not isinstance(execution_set_id, str) or not execution_set_id:
            errors.append(err("MISMATCH", f"execution_sets[{index}].id", "non-empty string", execution_set_id))
        if "files" in execution_set:
            errors.extend(validate_path_list_shape(execution_set.get("files"), f"execution_sets[{index}].files"))
        items = execution_set.get("items")
        if isinstance(items, list):
            for item_index, item in enumerate(items):
                if isinstance(item, dict) and "files" in item:
                    errors.extend(validate_path_list_shape(item.get("files"), f"execution_sets[{index}].items[{item_index}].files"))
        kind = execution_set.get("kind")
        if kind not in SUPPORTED_EXECUTION_SET_KINDS:
            errors.append(err("MISMATCH", f"execution_sets[{index}].kind", sorted(SUPPORTED_EXECUTION_SET_KINDS), kind))
        if kind == "rollback" and missing_non_empty_value(execution_set.get("rollback_from_execution_set")):
            errors.append(err("MISSING_FIELD", f"execution_sets[{index}].rollback_from_execution_set", "non-empty value", "missing"))
        if kind == "rollback" and execution_set.get("rollback_from_execution_set") not in ids:
            errors.append(err("MISMATCH", f"execution_sets[{index}].rollback_from_execution_set", "existing execution_sets[].id", execution_set.get("rollback_from_execution_set")))
        if "scope_relation" in execution_set:
            errors.append(err("DEPRECATED_FIELD", f"execution_sets[{index}].scope_relation", "omit field; file-scope validation is authoritative", execution_set.get("scope_relation")))
    return errors


def validate_projection_file_scope(values: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    errors.extend(validate_path_list_shape(values.get("declared_files"), "declared_files"))
    errors.extend(validate_path_list_shape(values.get("forbidden_paths"), "forbidden_paths"))
    declared = as_path_list(values.get("declared_files"))
    forbidden = as_path_list(values.get("forbidden_paths"))
    declared_set = set(declared)
    for field, paths in {"declared_files": declared, "forbidden_paths": forbidden}.items():
        for path in paths:
            if unsafe_path(path):
                errors.append(err("INVALID_PATH", field, "relative normalized path", path))
    errors.extend(validate_execution_sets(values))
    for field, path in execution_file_entries(values.get("execution_sets")):
        if unsafe_path(path):
            errors.append(err("INVALID_PATH", field, "relative normalized path", path))
        if path not in declared_set:
            errors.append(err("OUT_OF_SCOPE_EXECUTION_FILE", field, "member of declared_files", path))
        if any(path_matches(path, forbidden_path) for forbidden_path in forbidden):
            errors.append(err("FORBIDDEN_EXECUTION_FILE", field, "not under forbidden_paths", path))
    return errors


def validate_changed_file_scope(values: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    errors.extend(validate_path_list_shape(values.get("changed_files"), "changed_files"))
    changed = as_path_list(values.get("changed_files"))
    declared = as_path_list(values.get("declared_files"))
    forbidden = as_path_list(values.get("forbidden_paths"))
    selected_files = selected_execution_files(values)
    declared_set = set(declared)
    for path in changed:
        if unsafe_path(path):
            errors.append(err("INVALID_PATH", "changed_files", "relative normalized path", path))
    for path in changed:
        if path not in declared_set:
            errors.append(err("OUT_OF_SCOPE_CHANGED_FILE", "changed_files", "member of declared_files", path))
        if selected_files and path not in selected_files:
            errors.append(err("OUT_OF_SCOPE_CHANGED_FILE", "changed_files", "member of selected execution set files", path))
        if any(path_matches(path, forbidden_path) for forbidden_path in forbidden):
            errors.append(err("FORBIDDEN_CHANGED_FILE", "changed_files", "not under forbidden_paths", path))
    return errors


def active_blocker(value: Any) -> bool:
    if value in (None, False, "", [], {}, "none", "not_applicable"):
        return False
    if isinstance(value, str):
        return value.strip().lower() not in {"none", "not_applicable", "no active blockers", "no_active_blockers"}
    if isinstance(value, list):
        return any(active_blocker(item) for item in value)
    if isinstance(value, dict):
        status = value.get("status") or value.get("blocker_status")
        if status in {"none", "resolved", "not_applicable", "no_active_blockers"}:
            return False
        return True
    return True


def validate_compact_density(values: dict[str, Any]) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    execution_sets = values.get("execution_sets")
    if not isinstance(execution_sets, list) or len(execution_sets) != 1:
        errors.append(err("COMPACT_DENSITY_VIOLATION", "execution_sets", "exactly one execution set", execution_sets))
        return errors
    execution_set = execution_sets[0]
    items = execution_set.get("items") if isinstance(execution_set, dict) else None
    if not isinstance(items, list) or len(items) != 1:
        errors.append(err("COMPACT_DENSITY_VIOLATION", "execution_sets[].items", "exactly one bounded item", items))
    if not as_path_list(values.get("declared_files")):
        errors.append(err("COMPACT_DENSITY_VIOLATION", "declared_files", "non-empty explicit narrow files", values.get("declared_files")))
    verification = values.get("verification_contract")
    commands = verification.get("commands") if isinstance(verification, dict) else None
    if not isinstance(commands, list) or not commands:
        errors.append(err("COMPACT_DENSITY_VIOLATION", "verification_contract", "direct verification commands", verification))
    if len(as_path_list(values.get("generated_outputs"))) > 1:
        errors.append(err("COMPACT_DENSITY_VIOLATION", "generated_outputs", "zero or one simple generated output", values.get("generated_outputs")))
    risk = values.get("risk_scope")
    if isinstance(risk, str) and "broad" in risk.lower():
        errors.append(err("COMPACT_DENSITY_VIOLATION", "risk_scope", "bounded risk", risk))
    if gates_unresolved(values.get("human_gates")):
        errors.append(err("COMPACT_DENSITY_VIOLATION", "human_gates", "resolved or not_applicable", values.get("human_gates")))
    return errors


def set_or_reject_projection(values: dict[str, Any], errors: list[dict[str, Any]], field: str, expected: Any) -> None:
    observed = values.get(field)
    if observed is None:
        values[field] = expected
    elif observed != expected:
        errors.append(err("CONTRADICTORY_PROJECTION", field, expected, observed))


def validate_forbidden_target_fields(data: dict[str, Any], errors: list[dict[str, Any]]) -> None:
    for field in ["micro_repair_scope", "scope_relation", "projection_operator_editable", "projection_generated_by"]:
        if direct_key(data, field) is not None:
            errors.append(err("DEPRECATED_FIELD", field, "omit field in target schema", direct_key(data, field)))
    if isinstance(direct_key(data, "approval"), dict):
        errors.append(err("DEPRECATED_FIELD", "approval", "flat approval fields", "nested approval object"))


def validate_forbidden_compact_projection_fields(data: dict[str, Any], errors: list[dict[str, Any]]) -> None:
    for field in ["declared_files", "forbidden_paths", "execution_sets", "acceptance_criteria", "verification_contract"]:
        if direct_key(data, field) is not None:
            errors.append(err("DEPRECATED_FIELD", field, "compact operators write scope/done shorthand; helper derives projection", direct_key(data, field)))


def derive_compact_values(data: dict[str, Any], values: dict[str, Any], errors: list[dict[str, Any]]) -> None:
    if values.get("generated_outputs") is None:
        values["generated_outputs"] = "not_applicable"
    non_goals = direct_key(data, "non_goals")
    if non_goals is not None:
        set_or_reject_projection(values, errors, "non_goal_constraints", non_goals)
    elif values.get("non_goal_constraints") is None:
        values["non_goal_constraints"] = []
    if values.get("risk_scope") is None:
        values["risk_scope"] = "not_applicable"
    if values.get("rollback_boundary") is None:
        values["rollback_boundary"] = "not_applicable"

    scope = direct_key(data, "scope")
    if not isinstance(scope, dict):
        return
    allowed = get_path(scope, "files.allow")
    forbidden = get_path(scope, "files.forbid")
    item = scope.get("item")
    verify = scope.get("verify")
    if allowed is not None:
        set_or_reject_projection(values, errors, "declared_files", allowed)
    if forbidden is not None:
        set_or_reject_projection(values, errors, "forbidden_paths", forbidden)
    else:
        errors.append(err("MISSING_FIELD", "scope.files.forbid", "explicit forbidden paths", "missing"))
    if allowed is not None and item is not None:
        set_or_reject_projection(values, errors, "execution_sets", [
            {
                "id": "set-1",
                "kind": "normal",
                "files": allowed,
                "items": [
                    {
                        "id": "item-1",
                        "description": item,
                    }
                ],
            }
        ])
    done = direct_key(data, "done")
    if done is not None:
        set_or_reject_projection(values, errors, "acceptance_criteria", done)
    if verify is not None:
        set_or_reject_projection(values, errors, "verification_contract", verify)


def missing_required_value(field: str, value: Any) -> bool:
    if value is None or value == "":
        return True
    non_empty_fields = {"declared_files", "execution_sets", "acceptance_criteria", "verification_contract"}
    if field not in non_empty_fields:
        return False
    if value in ([], {}):
        return True
    if field == "verification_contract":
        commands = value.get("commands") if isinstance(value, dict) else None
        return not isinstance(commands, list) or not commands
    return False


def approval_field_ids(owner: str | None = None) -> list[str]:
    return [
        field["id"]
        for field in approval_required_fields()
        if owner is None or field.get("owner") == owner
    ]


def missing_non_empty_value(value: Any) -> bool:
    return value is None or value == "" or (isinstance(value, list) and not value) or (isinstance(value, dict) and not value)


def build_payload(status: str, density: str, feature_slug: str, errors: list[dict[str, Any]], warnings: list[str], values: dict[str, Any], hashes: dict[str, str]) -> dict[str, Any]:
    missing_paths = {error.get("path") for error in errors if error.get("code") == "MISSING_FIELD"}
    return {
        "feature_slug": feature_slug,
        "artifact_density": density,
        "readiness_seen": values.get("readiness"),
        "integrity": {"complete": "verified", "invalid": "invalid", "unavailable": "unavailable"}.get(status, "invalid"),
        "integrity_status_seen": integrity_status(values.get("integrity")),
        "approval_ref_seen": values.get("approval_ref"),
        "selected_execution_set_seen": values.get("selected_execution_set"),
        "execution_mode_seen": values.get("execution_mode"),
        "pre_execution_integrity_check_seen": values.get("pre_execution_integrity_check"),
        "approval_envelope_complete": not errors and status == "complete",
        "approval_envelope_status": status,
        "field_status": {k: ("missing" if k in missing_paths or missing_required_value(k, v) else "complete") for k, v in values.items()},
        "machine_hashes": hashes,
        "errors": errors,
        "warnings": warnings,
    }


def verify(root: Path, feature_slug: str | None, check: str) -> dict[str, Any]:
    if _REGISTRY_ERROR:
        return build_payload("unavailable", "unknown", feature_slug or "unknown", [err("REGISTRY_UNAVAILABLE", str(REGISTRY_ROOT), "readable registry", _REGISTRY_ERROR)], [], {}, {})
    artifact_root, manifest, errors = resolve_manifest(root, feature_slug)
    if not artifact_root or not manifest:
        return build_payload("unavailable", "unknown", feature_slug or "unknown", errors, [], {}, {})
    density = str(manifest.get("artifact_density"))
    slug = str(manifest.get("feature_slug"))
    values: dict[str, Any] = {"artifact_density": density}
    hashes: dict[str, str] = {"FEATURE.json": sha256_bytes((artifact_root / "FEATURE.json").read_bytes())}
    warnings: list[str] = []

    compact_exists = (artifact_root / "TICKET.md").exists()
    full_exists = any((artifact_root / name).exists() for name in ("CONTEXT.md", "PLAN.md", "TRACKER.json", "REVIEW.md"))
    if density == "compact" and full_exists or density == "full" and compact_exists:
        errors.append(err("MIXED_DENSITY_ARTIFACTS", str(artifact_root), f"only {density} artifacts", "compact and full artifacts present"))

    if density == "compact":
        ticket_text, text_error = read_text(artifact_root / "TICKET.md")
        used_documented_sections = False
        if text_error:
            errors.append(text_error)
            data = {}
        else:
            blocks, block_errors = authority_blocks(ticket_text or "", "beo.ticket.v1")
            errors.extend(block_errors)
            if blocks:
                data = blocks[0]
            else:
                data = {}
                if markdown_sections(ticket_text or ""):
                    used_documented_sections = True
                    warnings.append("TICKET.md uses documented markdown sections without beo.ticket.v1 authority block")
                else:
                    errors.append(err("MISSING_AUTHORITY_BLOCK", "TICKET.md", "```yaml beo.ticket.v1```", "missing"))
            if used_documented_sections:
                errors.append(err(
                    "MISSING_AUTHORITY_BLOCK",
                    "TICKET.md",
                    "add ```yaml beo.ticket.v1``` structured authority block for approval-bearing checks",
                    "documented markdown sections are draft-only",
                ))
        values.update({
            "request": direct_key(data, "request"),
            "human_gates": direct_key(data, "human_gates"),
            "declared_files": direct_key(data, "declared_files"),
            "forbidden_paths": direct_key(data, "forbidden_paths"),
            "generated_outputs": direct_key(data, "generated_outputs"),
            "non_goal_constraints": direct_key(data, "non_goal_constraints"),
            "risk_scope": direct_key(data, "risk_scope"),
            "rollback_boundary": direct_key(data, "rollback_boundary"),
            "execution_sets": direct_key(data, "execution_sets"),
            "acceptance_criteria": direct_key(data, "acceptance_criteria"),
            "verification_contract": direct_key(data, "verification_contract"),
            "readiness": direct_key(data, "readiness"),
            "approval_ref": direct_key(data, "approval_ref"),
            "integrity": direct_key(data, "integrity"),
            "selected_execution_set": direct_key(data, "selected_execution_set"),
            "execution_mode": direct_key(data, "execution_mode"),
            "pre_execution_integrity_check": direct_key(data, "pre_execution_integrity_check"),
            "changed_files": direct_key(data, "changed_files"),
            "verification_evidence": direct_key(data, "verification_evidence"),
            "review_status": direct_key(data, "review_status"),
            "blocker": direct_key(data, "blocker"),
        })
        validate_forbidden_target_fields(data, errors)
        validate_forbidden_compact_projection_fields(data, errors)
        derive_compact_values(data, values, errors)
        hashes["approval_bearing_projection"] = approval_bearing_projection_hash(values)
    else:
        context_text, context_error = read_text(artifact_root / "CONTEXT.md")
        plan_text, plan_error = read_text(artifact_root / "PLAN.md")
        for e in (context_error, plan_error):
            if e:
                errors.append(e)
        context_data: dict[str, Any] = {}
        plan_data: dict[str, Any] = {}
        if context_text is not None:
            hashes["CONTEXT.md"] = sha256_bytes(context_text.replace("\r\n", "\n").encode())
            blocks, block_errors = authority_blocks(context_text, "beo.context.v1")
            errors.extend(block_errors)
            context_data = blocks[0] if blocks else {}
            if not blocks:
                errors.append(err("MISSING_AUTHORITY_BLOCK", "CONTEXT.md", "```yaml beo.context.v1```", "missing"))
        if plan_text is not None:
            blocks, block_errors = authority_blocks(plan_text, "beo.plan.v1")
            errors.extend(block_errors)
            plan_data = blocks[0] if blocks else {}
            if not blocks:
                errors.append(err("MISSING_AUTHORITY_BLOCK", "PLAN.md", "```yaml beo.plan.v1```", "missing"))
            validate_forbidden_target_fields(plan_data, errors)
        values.update({
            "request": direct_key(context_data, "request"),
            "human_gates": direct_key(context_data, "human_gates"),
            "declared_files": direct_key(plan_data, "declared_files"),
            "forbidden_paths": direct_key(plan_data, "forbidden_paths"),
            "generated_outputs": direct_key(plan_data, "generated_outputs"),
            "non_goal_constraints": direct_key(plan_data, "non_goal_constraints"),
            "risk_scope": direct_key(plan_data, "risk_scope"),
            "rollback_boundary": direct_key(plan_data, "rollback_boundary"),
            "execution_sets": direct_key(plan_data, "execution_sets"),
            "acceptance_criteria": direct_key(plan_data, "acceptance_criteria"),
            "verification_contract": direct_key(plan_data, "verification_contract"),
            "readiness": direct_key(plan_data, "readiness"),
            "approval_ref": direct_key(plan_data, "approval_ref"),
            "integrity": direct_key(plan_data, "integrity"),
            "selected_execution_set": direct_key(plan_data, "selected_execution_set"),
            "execution_mode": direct_key(plan_data, "execution_mode"),
        })

    hashes["approval_bearing_projection"] = approval_bearing_projection_hash(values)
    hashes["approval_envelope"] = approval_envelope_hash(values)

    validate_approval_fields = {"readiness", "approval_ref", "integrity", "selected_execution_set", "execution_mode"}
    validate_required = approval_field_ids()
    for field in validate_required:
        values.setdefault(field, None)
    required = [field for field in validate_required if check != "validate" or field not in validate_approval_fields]
    for field in required:
        if missing_required_value(field, values.get(field)):
            errors.append(err("MISSING_FIELD", field, "non-empty value", "missing"))
    errors.extend(validate_projection_file_scope(values))
    if density == "compact" and check in {"validate", "execute", "review"}:
        errors.extend(validate_compact_density(values))
    if check in {"validate", "execute", "review"}:
        errors.extend(validate_human_gates(values.get("human_gates")))
    if values.get("integrity") is not None:
        errors.extend(validate_integrity(values.get("integrity")))
    if check in {"execute", "review"}:
        if values.get("readiness") != REQUIRED_READINESS:
            errors.append(err("MISMATCH", "readiness", REQUIRED_READINESS, values.get("readiness")))
        if integrity_status(values.get("integrity")) != "verified":
            errors.append(err("MISMATCH", "integrity.status", "verified", integrity_status(values.get("integrity"))))
        execution_mode = values.get("execution_mode")
        if not isinstance(execution_mode, str) or execution_mode not in SUPPORTED_MODES:
            errors.append(err("MISMATCH", "execution_mode", sorted(SUPPORTED_MODES), execution_mode))
        selected = values.get("selected_execution_set")
        if not missing_required_value("selected_execution_set", selected):
            if not isinstance(selected, str) or selected not in execution_set_ids(values.get("execution_sets")):
                errors.append(err("MISMATCH", "selected_execution_set", "execution_sets[].id", selected))
        errors.extend(validate_approval_ref(values.get("approval_ref"), density, selected, execution_mode, hashes))
        errors.extend(validate_changed_file_scope(values))
    if check == "review":
        if density == "compact":
            for field in ["pre_execution_integrity_check", "changed_files", "verification_evidence", "review_status", "blocker"]:
                if missing_non_empty_value(values.get(field)):
                    errors.append(err("MISSING_FIELD", field, "non-empty value", "missing"))
            if values.get("review_status") != "ready_for_review":
                errors.append(err("MISMATCH", "review_status", "ready_for_review", values.get("review_status")))
            if active_blocker(values.get("blocker")):
                errors.append(err("MISMATCH", "blocker", "no active blockers", values.get("blocker")))
            errors.extend(validate_pre_execution_integrity_check(values.get("pre_execution_integrity_check")))
        else:
            tracker, tracker_error = read_json(artifact_root / "TRACKER.json")
            if tracker_error:
                errors.append(tracker_error)
            elif tracker is not None:
                ledger_required = [
                    "schema_version",
                    "feature_slug",
                    "artifact_root",
                    "approval_ref_id",
                    "ledger_status",
                    "pre_execution_integrity_check",
                    "selected_execution_set",
                    "execution_mode",
                    "items",
                    "changed_files",
                    "observations",
                    "blockers",
                    "scope_delta_requests",
                    "repair_budget",
                    "resume_point",
                    "rollback_status",
                ]
                for field in ledger_required:
                    if field in {"blockers", "observations", "scope_delta_requests"}:
                        if field not in tracker:
                            errors.append(err("MISSING_FIELD", f"TRACKER.json.{field}", "present list", "missing"))
                        elif not isinstance(tracker.get(field), list):
                            errors.append(err("MISSING_FIELD", f"TRACKER.json.{field}", "list", type(tracker.get(field)).__name__))
                    elif missing_non_empty_value(tracker.get(field)):
                        errors.append(err("MISSING_FIELD", f"TRACKER.json.{field}", "non-empty value", "missing"))
                if tracker.get("schema_version") != "beo.execution_ledger.v1":
                    errors.append(err("MISMATCH", "TRACKER.json.schema_version", "beo.execution_ledger.v1", tracker.get("schema_version")))
                if tracker.get("ledger_status") != "ready_for_review":
                    errors.append(err("MISMATCH", "TRACKER.json.ledger_status", "ready_for_review", tracker.get("ledger_status")))
                if active_blocker(tracker.get("blockers")):
                    errors.append(err("MISMATCH", "TRACKER.json.blockers", "no active blockers", tracker.get("blockers")))
                if tracker.get("approval_ref_id") != approval_ref_id(values.get("approval_ref")):
                    errors.append(err("MISMATCH", "TRACKER.json.approval_ref_id", approval_ref_id(values.get("approval_ref")), tracker.get("approval_ref_id")))
                if tracker.get("selected_execution_set") != values.get("selected_execution_set"):
                    errors.append(err("MISMATCH", "TRACKER.json.selected_execution_set", values.get("selected_execution_set"), tracker.get("selected_execution_set")))
                if tracker.get("execution_mode") != values.get("execution_mode"):
                    errors.append(err("MISMATCH", "TRACKER.json.execution_mode", values.get("execution_mode"), tracker.get("execution_mode")))
                errors.extend(validate_pre_execution_integrity_check(tracker.get("pre_execution_integrity_check"), "TRACKER.json.pre_execution_integrity_check"))
                values["changed_files"] = direct_key(tracker, "changed_files")
                if missing_non_empty_value(values.get("changed_files")):
                    errors.append(err("MISSING_FIELD", "TRACKER.json.changed_files", "non-empty value", "missing"))
                errors.extend(validate_changed_file_scope(values))
    status = "complete" if not errors else "invalid"
    return build_payload(status, density, slug, errors, warnings, values, hashes)


def main() -> int:
    class Parser(argparse.ArgumentParser):
        def exit(self, status: int = 0, message: str | None = None) -> None:
            if message:
                self._print_message(message, sys.stderr)
            raise SystemExit(3 if status == 2 else status)

    parser = Parser(description="BEO approval checker (read-only, strict runtime mode)")
    parser.add_argument("feature_slug", nargs="?")
    parser.add_argument("--artifact-root", "--root", dest="artifact_root", type=Path, default=Path("."))
    parser.add_argument("--check", choices=["validate", "execute", "review"], default="validate")
    args = parser.parse_args()
    payload = verify(args.artifact_root, args.feature_slug, args.check)
    print(json.dumps(payload, indent=2))
    if payload.get("approval_envelope_status") == "complete":
        return 0
    if payload.get("approval_envelope_status") == "unavailable":
        return 2
    return 1


if __name__ == "__main__":
    sys.exit(main())
