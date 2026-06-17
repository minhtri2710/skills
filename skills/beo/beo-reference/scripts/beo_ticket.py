#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
from typing import Any, Literal

TICKET_ARTIFACT = "TICKET.yaml"
TICKET_VERSION = 1


@dataclass(frozen=True)
class TicketReadResult:
    data: dict[str, Any]
    path: Path
    artifact: Literal["TICKET.yaml"]
    version: int
    ticket_file_hash: str


def ticket_path(root: Path, issue_id: str) -> Path:
    from beo_paths import artifact_dir

    return artifact_dir(root, issue_id) / TICKET_ARTIFACT


def ticket_file_hash(path: Path) -> str:
    raw = path.read_bytes()
    normalized = raw.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return "sha256-lf-normalized:" + hashlib.sha256(normalized).hexdigest()


def _load_plan_schema() -> dict[str, Any]:
    schema_path = Path(__file__).resolve().parents[1] / "registry" / "ticket.schema.json"
    import json

    try:
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
    except Exception as exc:
        raise ValueError(f"failed to load ticket.schema.json: {exc}") from exc
    if not isinstance(schema, dict):
        raise ValueError("ticket.schema.json must be a JSON object")
    return schema


def _as_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise ValueError(f"{field} must be a list")
    return value


def _require_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{field} must be a non-empty string")
    return value


def _reject_unknown(mapping: dict[str, Any], allowed: set[str], field: str) -> None:
    unknown = sorted(set(mapping) - allowed)
    if unknown:
        raise ValueError(f"{field} contains unknown field(s): {', '.join(unknown)}")


def _validate_path_values(values: list[Any], field: str) -> None:
    from beo_paths import reject_unsafe_path

    for value in values:
        _require_string(value, field)
        try:
            reject_unsafe_path(value)
        except ValueError as exc:
            raise ValueError(f"{field} contains unsafe path: {exc}") from exc


def _scope(data: dict[str, Any]) -> dict[str, Any]:
    scope = data.get("scope")
    if not isinstance(scope, dict):
        raise ValueError("scope must be an object")
    _reject_unknown(scope, {"files", "generated_outputs", "verify"}, "scope")
    files = scope.get("files")
    if not isinstance(files, dict):
        raise ValueError("scope.files must be an object")
    _reject_unknown(files, {"allow", "forbid"}, "scope.files")
    allow = _as_list(files.get("allow"), "scope.files.allow")
    forbid = _as_list(files.get("forbid"), "scope.files.forbid")
    generated = _as_list(scope.get("generated_outputs"), "scope.generated_outputs")
    verify = scope.get("verify")
    if not isinstance(verify, dict):
        raise ValueError("scope.verify must be an object")
    _reject_unknown(verify, {"commands"}, "scope.verify")
    commands = _as_list(verify.get("commands"), "scope.verify.commands")
    if not allow:
        raise ValueError("scope.files.allow must contain at least one explicit path")
    if not commands:
        raise ValueError("scope.verify.commands must contain at least one command")
    for field, values in {
        "scope.files.allow": allow,
        "scope.files.forbid": forbid,
        "scope.generated_outputs": generated,
    }.items():
        _validate_path_values(values, field)
    for command in commands:
        _require_string(command, "scope.verify.commands")
    return scope


def validate_human_gates(data: dict[str, Any], issue_id: str) -> None:
    gates = data.get("human_gates")
    if gates is None:
        return
    if not isinstance(gates, dict):
        raise ValueError("human_gates must be an object")
    _reject_unknown(gates, {"status", "gates"}, "human_gates")
    status = gates.get("status")
    if status not in {"resolved", "unresolved", "not_applicable"}:
        raise ValueError("human_gates.status is invalid")
    gate_entries = _as_list(gates.get("gates"), "human_gates.gates")
    if status == "resolved" and not gate_entries:
        raise ValueError("resolved human_gates requires at least one gate")
    gate_required = {"type", "scope", "approver_handle", "valid_for_issue_id", "reason"}
    gate_allowed = gate_required | {"revocation_ref"}
    for index, gate in enumerate(gate_entries):
        if not isinstance(gate, dict):
            raise ValueError("human_gates.gates entries must be objects")
        _reject_unknown(gate, gate_allowed, f"human_gates.gates[{index}]")
        missing = sorted(field for field in gate_required if field not in gate)
        if missing:
            raise ValueError(f"human_gates.gates[{index}] missing required field(s): {', '.join(missing)}")
        for field in sorted(gate_required):
            _require_string(gate.get(field), f"human_gates.gates[{index}].{field}")
        if "revocation_ref" in gate:
            value = gate["revocation_ref"]
            if value is not None and not isinstance(value, str):
                raise ValueError(f"human_gates.gates[{index}].revocation_ref must be a string or null")
        if gate.get("valid_for_issue_id") != issue_id:
            raise ValueError(f"human_gates.gates[{index}].valid_for_issue_id must match issue_id")


def _reject_glob_in_allow_paths(data: dict[str, Any]) -> None:
    from beo_paths import has_glob
    mode = data.get("mode")
    fast_track = data.get("fast_track")
    if mode == "quick" and fast_track is True:
        allow_paths = data.get("scope", {}).get("files", {}).get("allow", [])
        for path in allow_paths:
            if has_glob(path):
                raise ValueError(f"fast-track ticket with mode=quick must not use glob paths in scope.files.allow: {path}")


def validate_plan_only(data: dict[str, Any]) -> None:
    schema = _load_plan_schema()

    allowed_top = set(schema.get("properties", {}))
    if allowed_top:
        _reject_unknown(data, allowed_top, "TICKET.yaml")

    required = set(schema.get("required", []))
    missing = sorted(k for k in required if k not in data)
    if missing:
        raise ValueError(f"TICKET.yaml missing required plan field(s): {', '.join(missing)}")

    if data.get("version") != TICKET_VERSION:
        raise ValueError(f"unsupported TICKET.yaml version: {data.get('version')!r}; expected {TICKET_VERSION}")
    issue_id = _require_string(data.get("issue_id"), "issue_id")
    from beo_paths import reject_unsafe_issue_id
    reject_unsafe_issue_id(issue_id)
    mode = data.get("mode")
    if mode not in {"quick", "standard", "strict"}:
        raise ValueError("mode must be one of: quick, standard, strict")
    _require_string(data.get("request"), "request")
    done_criteria = _as_list(data.get("done_criteria"), "done_criteria")
    if not done_criteria:
        raise ValueError("done_criteria must contain at least one criterion")
    for criterion in done_criteria:
        _require_string(criterion, "done_criteria")
    _scope(data)
    validate_human_gates(data, issue_id)
    _reject_glob_in_allow_paths(data)

    if mode == "quick":
        for field in ["risk", "strict"]:
            if field in data:
                raise ValueError(f"quick mode must not include {field}")
    if mode in {"standard", "strict"}:
        risk = data.get("risk")
        if not isinstance(risk, dict):
            raise ValueError("risk is required for standard and strict modes")
        _reject_unknown(risk, {"summary", "rollback"}, "risk")
        _require_string(risk.get("summary"), "risk.summary")
        _require_string(risk.get("rollback"), "risk.rollback")
    if mode == "strict":
        gates = data.get("human_gates")
        if not isinstance(gates, dict) or gates.get("status") != "resolved":
            raise ValueError("strict mode requires resolved human_gates")
        strict = data.get("strict")
        if not isinstance(strict, dict):
            raise ValueError("strict mode requires strict contract")
        _reject_unknown(strict, {"reason", "authorization_refs", "rollback_refs", "external_side_effects", "stateful_external_systems", "worktree_isolation"}, "strict")
        for field in ["reason"]:
            _require_string(strict.get(field), f"strict.{field}")
        worktree_isolation = strict.get("worktree_isolation")
        if worktree_isolation is not None and not isinstance(worktree_isolation, bool):
            raise ValueError("strict.worktree_isolation must be a boolean")
        for field in ["authorization_refs", "rollback_refs", "external_side_effects", "stateful_external_systems"]:
            values = _as_list(strict.get(field), f"strict.{field}")
            if not values:
                raise ValueError(f"strict.{field} must not be empty")
        effect_required = {"type", "target", "authorization_ref", "precheck", "rollback_or_compensation", "postcheck", "blast_radius"}
        effect_targets: set[str] = set()
        for index, effect in enumerate(strict["external_side_effects"]):
            if not isinstance(effect, dict):
                raise ValueError("strict.external_side_effects entries must be objects")
            _reject_unknown(effect, effect_required, f"strict.external_side_effects[{index}]")
            missing = sorted(field for field in effect_required if field not in effect)
            if missing:
                raise ValueError(f"strict.external_side_effects[{index}] missing required field(s): {', '.join(missing)}")
            for field in sorted(effect_required):
                _require_string(effect.get(field), f"strict.external_side_effects[{index}].{field}")
            effect_targets.add(effect["target"])
        system_required = {"name", "effect_ref"}
        for index, system in enumerate(strict["stateful_external_systems"]):
            if not isinstance(system, dict):
                raise ValueError("strict.stateful_external_systems entries must be objects")
            _reject_unknown(system, system_required, f"strict.stateful_external_systems[{index}]")
            missing = sorted(field for field in system_required if field not in system)
            if missing:
                raise ValueError(f"strict.stateful_external_systems[{index}] missing required field(s): {', '.join(missing)}")
            for field in sorted(system_required):
                _require_string(system.get(field), f"strict.stateful_external_systems[{index}].{field}")
            if system["effect_ref"] not in effect_targets:
                raise ValueError(f"strict.stateful_external_systems[{index}].effect_ref must match an external_side_effects target")

    if data.get("issue_id") != issue_id:
        raise ValueError("issue_id normalization failed")


def approval_projection_input(data: dict[str, Any]) -> dict[str, Any]:
    validate_plan_only(data)
    projection = {
        "issue_id": data["issue_id"],
        "request": data["request"],
        "done_criteria": data["done_criteria"],
        "scope.files.allow": data["scope"]["files"]["allow"],
        "scope.files.forbid": data["scope"]["files"]["forbid"],
        "scope.generated_outputs": data["scope"]["generated_outputs"],
        "scope.verify.commands": data["scope"]["verify"]["commands"],
    }
    if "human_gates" in data:
        projection["human_gates"] = data["human_gates"]
    if data["mode"] in {"standard", "strict"}:
        projection["risk.summary"] = data["risk"]["summary"]
        projection["risk.rollback"] = data["risk"]["rollback"]
    if data["mode"] == "strict":
        strict = data["strict"]
        projection.update({
            "strict.reason": strict["reason"],
            "strict.authorization_refs": strict["authorization_refs"],
            "strict.rollback_refs": strict["rollback_refs"],
            "strict.external_side_effects": strict["external_side_effects"],
            "strict.stateful_external_systems": strict["stateful_external_systems"],
        })
    return projection


def _reject_yaml_features(raw_content: str) -> None:
    import yaml

    docs = list(yaml.compose_all(raw_content))
    if len(docs) != 1:
        raise ValueError("TICKET.yaml must contain exactly one YAML document")
    for token in yaml.scan(raw_content):
        if isinstance(token, (yaml.tokens.AnchorToken, yaml.tokens.AliasToken)):
            raise ValueError("TICKET.yaml must not contain YAML anchors or aliases")


def _reject_duplicate_keys(node: Any, path: str = "TICKET.yaml") -> None:
    import yaml

    if isinstance(node, yaml.MappingNode):
        keys: set[Any] = set()
        for key_node, value_node in node.value:
            key = key_node.value
            if key in keys:
                raise ValueError(f"duplicate key in {path}: {key}")
            keys.add(key)
            _reject_duplicate_keys(value_node, f"{path}.{key}")
    elif isinstance(node, yaml.SequenceNode):
        for index, item_node in enumerate(node.value):
            _reject_duplicate_keys(item_node, f"{path}[{index}]")


def read_ticket_yaml(path: Path) -> TicketReadResult:
    import yaml

    raw_content = path.read_text(encoding="utf-8")
    try:
        _reject_yaml_features(raw_content)
        node = yaml.compose(raw_content)
        if node is not None:
            _reject_duplicate_keys(node)
        data = yaml.safe_load(raw_content) or {}
    except Exception as exc:
        raise ValueError(f"Failed to parse TICKET.yaml: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("TICKET.yaml must be a YAML mapping")
    validate_plan_only(data)
    return TicketReadResult(data=data, path=path, artifact=TICKET_ARTIFACT, version=TICKET_VERSION, ticket_file_hash=ticket_file_hash(path))


def read_ticket(root: Path, issue_id: str) -> TicketReadResult:
    path = ticket_path(root, issue_id)
    if not path.exists():
        raise FileNotFoundError(f"ticket_artifact_missing: {path}")
    result = read_ticket_yaml(path)
    if result.data.get("issue_id") != issue_id:
        raise ValueError("TICKET.yaml issue_id must match artifact issue_id")
    return result


def write_ticket(root: Path, issue_id: str, data: dict[str, Any], *, overwrite: bool = False) -> Path:
    import yaml

    validate_plan_only(data)
    if data.get("issue_id") != issue_id:
        raise ValueError("TICKET.yaml issue_id must match artifact issue_id")
    path = ticket_path(root, issue_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise FileExistsError(f"TICKET.yaml already exists: {path}")
    yaml_content = yaml.safe_dump(data, sort_keys=False, default_flow_style=False)
    if not yaml_content.endswith("\n"):
        yaml_content += "\n"
    path.write_text(yaml_content, encoding="utf-8")
    return path
