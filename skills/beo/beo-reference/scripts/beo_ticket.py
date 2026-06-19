#!/usr/bin/env python3
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Any, Literal

TICKET_ARTIFACT = "TICKET.json"
TICKET_VERSION = 1


@dataclass(frozen=True)
class TicketReadResult:
    data: dict[str, Any]
    path: Path
    artifact: Literal["TICKET.json"]
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

    for path in values:
        if not isinstance(path, str) or not path.strip():
            raise ValueError(f"{field} entries must be non-empty strings")
        try:
            reject_unsafe_path(path)
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
            raise ValueError(f"human_gates.gates[{index}] entries must be objects")
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
        _reject_unknown(data, allowed_top, "TICKET.json")

    required = set(schema.get("required", []))
    missing = sorted(k for k in required if k not in data)
    if missing:
        raise ValueError(f"TICKET.json missing required plan field(s): {', '.join(missing)}")

    if data.get("version") != TICKET_VERSION:
        raise ValueError(f"unsupported TICKET.json version: {data.get('version')!r}; expected {TICKET_VERSION}")
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


def read_ticket(root: Path, issue_id: str) -> TicketReadResult:
    """Read and validate a TICKET.json file for ``issue_id`` under ``root``.

    JSON's grammar forbids duplicate keys, anchors, aliases, and
    multi-document streams natively, so no additional security checks are
    required at parse time. Schema-level validation still runs through
    ``validate_plan_only``.
    """
    path = ticket_path(root, issue_id)
    if not path.exists():
        raise FileNotFoundError(f"ticket_artifact_missing: {path}")
    try:
        raw = path.read_bytes()
    except Exception as exc:
        raise ValueError(f"Failed to read TICKET.json: {exc}") from exc
    try:
        data = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Failed to parse TICKET.json: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError("TICKET.json must be a JSON object")
    if data.get("issue_id") != issue_id:
        raise ValueError("TICKET.json issue_id must match artifact issue_id")
    validate_plan_only(data)
    return TicketReadResult(data=data, path=path, artifact=TICKET_ARTIFACT, version=TICKET_VERSION, ticket_file_hash=ticket_file_hash(path))


def write_ticket(root: Path, issue_id: str, data: dict[str, Any], *, overwrite: bool = False) -> Path:
    validate_plan_only(data)
    if data.get("issue_id") != issue_id:
        raise ValueError("TICKET.json issue_id must match artifact issue_id")
    path = ticket_path(root, issue_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and not overwrite:
        raise FileExistsError(f"TICKET.json already exists: {path}")
    json_content = json.dumps(data, indent=2, sort_keys=False) + "\n"
    path.write_text(json_content, encoding="utf-8")
    return path
