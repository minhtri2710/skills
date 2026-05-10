#!/usr/bin/env python3
"""Read-only BEO approval/integrity evidence verifier."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

SUPPORTED_MODES = {"single", "ordered_batch"}
SUPPORTED_LANES = {"beo_tiny", "standard"}
SCHEMA_VERSION = 2


def sha256_text(text: str) -> str:
    normalized = text.replace("\r\n", "\n").replace("\r", "\n")
    return "sha256:" + hashlib.sha256(normalized.encode()).hexdigest()


def sha256_ticket_approval_bearing(text: str) -> str:
    normalized_lines = []
    for line in text.replace("\r\n", "\n").replace("\r", "\n").splitlines():
        stripped = line.strip()
        if stripped.startswith("Machine hashes:") or stripped.startswith("Baseline hashes:"):
            continue
        normalized_lines.append(line)
    return "sha256:" + hashlib.sha256(("\n".join(normalized_lines) + "\n").encode()).hexdigest()


def err(code: str, path: str, expected: Any, observed: Any) -> dict[str, Any]:
    return {"code": code, "path": path, "expected": expected, "observed": observed}


def read_text(path: Path) -> tuple[str | None, dict[str, Any] | None]:
    if not path.exists():
        return None, err("MISSING_FIELD", str(path), "readable file", "missing")
    try:
        return path.read_text(), None
    except Exception as exc:  # noqa: BLE001
        return None, err("MISSING_FIELD", str(path), "readable file", f"unreadable: {exc}")


def read_json(path: Path) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    if not path.exists():
        return None, err("MISSING_FIELD", str(path), "readable json", "missing")
    try:
        data = json.loads(path.read_text())
    except Exception as exc:  # noqa: BLE001
        return None, err("MISMATCH", str(path), "valid json", f"invalid json: {exc}")
    if not isinstance(data, dict):
        return None, err("MISMATCH", str(path), "json object", type(data).__name__)
    return data, None


def section(text: str | None, heading: str) -> str | None:
    if text is None:
        return None
    lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines(keepends=True)
    start = None
    level = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped == heading:
            start = i
            level = len(stripped) - len(stripped.lstrip("#"))
            break
    if start is None or level is None:
        return None
    end = len(lines)
    for j in range(start + 1, len(lines)):
        stripped = lines[j].strip()
        if stripped.startswith("#"):
            next_level = len(stripped) - len(stripped.lstrip("#"))
            if next_level <= level:
                end = j
                break
    return "".join(lines[start:end])


def field_value(text: str | None, label: str) -> str | None:
    if text is None:
        return None
    prefix = f"{label}:"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith(prefix):
            return stripped[len(prefix):].strip()
    return None


def list_after(text: str | None, heading: str) -> list[str]:
    if text is None:
        return []
    lines = text.splitlines()
    result: list[str] = []
    active = False
    for line in lines:
        stripped = line.strip()
        if stripped == heading or stripped.startswith(f"{heading}:"):
            active = True
            inline = stripped[len(heading):].lstrip(":").strip()
            if inline and inline.lower() not in {"n/a", "none"}:
                result.extend([x.strip() for x in inline.split(",") if x.strip()])
            continue
        if active:
            if stripped.startswith("- "):
                value = stripped[2:].strip()
                if value and value.lower() not in {"n/a", "none"}:
                    result.append(value)
            elif stripped == "":
                continue
            elif stripped.startswith("#") or re.match(r"^[A-Za-z].*:$", stripped):
                break
    return result


def table_rows(section_text: str | None) -> list[list[str]]:
    if not section_text:
        return []
    rows = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped.startswith("|") or "---" in stripped:
            continue
        cols = [c.strip() for c in stripped.strip("|").split("|")]
        if cols:
            rows.append(cols)
    return rows


def table_col_values(section_text: str | None, col_name: str) -> list[str]:
    rows = table_rows(section_text)
    if len(rows) < 2:
        return []
    header = rows[0]
    try:
        idx = header.index(col_name)
    except ValueError:
        return []
    values = []
    for row in rows[1:]:
        if idx < len(row):
            values.append(row[idx])
    return values


def split_values(values: list[str]) -> set[str]:
    out: set[str] = set()
    for value in values:
        for part in re.split(r"[,;]", value):
            clean = part.strip().strip("`")
            if clean and clean.lower() not in {"n/a", "none", "..."}:
                out.add(clean)
    return out


def baseline_hashes(integrity: dict[str, Any] | None, approval_section: str | None = None) -> dict[str, str]:
    if integrity:
        for key in ("machine_hashes", "baseline_hashes", "hashes"):
            value = integrity.get(key)
            if isinstance(value, dict):
                return {str(k): str(v) for k, v in value.items()}
    if approval_section:
        baseline = field_value(approval_section, "Machine hashes") or field_value(approval_section, "Baseline hashes")
        if baseline and baseline not in {"N/A", "none"}:
            try:
                parsed = json.loads(baseline)
                if isinstance(parsed, dict):
                    return {str(k): str(v) for k, v in parsed.items()}
            except json.JSONDecodeError:
                return {"ticket_hash": baseline}
    return {}


def compare_hashes(current: dict[str, str], baseline: dict[str, str], errors: list[dict[str, Any]]) -> None:
    if not baseline:
        errors.append(err("MISSING_FIELD", "integrity.machine_hashes", "baseline hashes", "missing"))
        return
    for key, current_hash in current.items():
        expected = baseline.get(key)
        if not expected:
            errors.append(err("MISSING_FIELD", f"integrity.machine_hashes.{key}", current_hash, "missing"))
        elif expected != current_hash:
            errors.append(err("HASH_MISMATCH", f"integrity.machine_hashes.{key}", expected, current_hash))


def output_status(errors: list[dict[str, Any]], unavailable: bool) -> str:
    if unavailable:
        return "unavailable"
    if any(e["code"] in {"HASH_MISMATCH", "STALE"} for e in errors):
        return "stale"
    if errors:
        return "invalid"
    return "verified"


def result(status: str, lane: str, feature_slug: str, errors: list[dict[str, Any]], **fields: Any) -> dict[str, Any]:
    from datetime import datetime, timezone
    payload = {
        "schema_version": SCHEMA_VERSION,
        "feature_slug": feature_slug,
        "lane": lane,
        "readiness": fields.get("readiness"),
        "approval_ref": fields.get("approval_ref"),
        "selected_execution_set": fields.get("selected_execution_set_id"),
        "integrity": status,
        "approval_bearing_hash": fields.get("approval_bearing_hash"),
        "checked_at": datetime.now(timezone.utc).isoformat(),
        "declared_files_status": fields.get("declared_files_status", "missing"),
        "forbidden_paths_status": fields.get("forbidden_paths_status", "missing"),
        "generated_outputs_status": fields.get("generated_outputs_status", "missing"),
        "verification_contract_status": fields.get("verification_contract_status", "missing"),
        "execution_mode": fields.get("execution_mode"),
        "safe_for_execute": status == "verified" and fields.get("readiness") == "PASS_EXECUTE",
        "helper_authority": "advisory_integrity_check",
        "machine_hashes": fields.get("machine_hashes", {}),
        "errors": errors,
        "warnings": fields.get("warnings", []),
    }
    return payload


def verify_tiny(feature_slug: str, artifact_root: Path) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    ticket_text, ticket_error = read_text(artifact_root / "TICKET.md")
    if ticket_error:
        return result("unavailable", "beo_tiny", feature_slug, [ticket_error], declared_files_status="unavailable", forbidden_paths_status="unavailable", generated_outputs_status="unavailable", verification_contract_status="unavailable")

    request = section(ticket_text, "## Request")
    acceptance = section(ticket_text, "## Acceptance")
    plan = section(ticket_text, "## Plan")
    approval = section(ticket_text, "## Approval")
    scope = section(ticket_text, "## Scope")

    if not request or not request.strip():
        errors.append(err("MISSING_FIELD", "TICKET.md#Request", "locked request", "missing"))
    if not acceptance or not acceptance.strip():
        errors.append(err("MISSING_FIELD", "TICKET.md#Acceptance", "locked acceptance", "missing"))

    bead_ids = [line.split(":", 1)[1].strip() for line in (plan or "").splitlines() if line.strip().startswith("- ID:")]
    if len(bead_ids) != 1:
        errors.append(err("MISMATCH", "TICKET.md#Plan.Bead", "exactly one selected bead", len(bead_ids)))

    approval_status = field_value(approval, "Readiness") or field_value(approval, "Status")
    integrity_status = field_value(approval, "Integrity") or field_value(approval, "Integrity status")
    approval_ref = field_value(approval, "Approval ref")
    selected_set = field_value(approval, "Approved execution set")
    execution_mode = field_value(approval, "Execution mode")

    if not approval_status or approval_status not in {"PASS_EXECUTE"}:
        errors.append(err("STALE", "TICKET.md#Approval.Readiness", "PASS_EXECUTE", approval_status or "missing"))
    if integrity_status != "verified":
        errors.append(err("STALE", "TICKET.md#Approval.Integrity", "verified", integrity_status or "missing"))
    if not approval_ref or approval_ref == "N/A":
        errors.append(err("MISSING_FIELD", "TICKET.md#Approval.Approval ref", "non-empty ref", approval_ref or "missing"))
    if not selected_set:
        errors.append(err("MISSING_FIELD", "TICKET.md#Approval.Approved execution set", "selected execution set", "missing"))
    if execution_mode not in SUPPORTED_MODES:
        errors.append(err("UNSUPPORTED", "TICKET.md#Approval.Execution mode", "single or ordered_batch", execution_mode or "missing"))

    allowed_files = list_after(scope, "Allowed files")
    forbidden_paths = list_after(scope, "Forbidden paths")
    generated_outputs = list_after(scope, "Generated outputs")
    verification = field_value(plan, "Verification")
    if not verification and plan:
        for line in plan.splitlines():
            stripped = line.strip()
            if stripped.startswith("- Verification:"):
                verification = stripped.split(":", 1)[1].strip()
                break
    if not allowed_files:
        errors.append(err("MISSING_FIELD", "TICKET.md#Scope.Allowed files", "non-empty declared files", "missing"))
    if not forbidden_paths:
        errors.append(err("MISSING_FIELD", "TICKET.md#Scope.Forbidden paths", "explicit forbidden paths", "missing"))
    if generated_outputs == [] and scope and "Generated outputs" not in scope:
        errors.append(err("MISSING_FIELD", "TICKET.md#Scope.Generated outputs", "declared outputs or N/A", "missing"))
    if not verification:
        errors.append(err("MISSING_FIELD", "TICKET.md#Plan.Verification", "non-empty verification contract", "missing"))

    current_hashes = {"ticket_hash": sha256_ticket_approval_bearing(ticket_text or "")}
    compare_hashes(current_hashes, baseline_hashes(None, approval), errors)
    status = output_status(errors, False)
    approval_bearing_hash = current_hashes.get("ticket_hash")

    readiness_value = None
    if approval:
        readiness_value = field_value(approval, "Readiness") or field_value(approval, "Status")
    return result(
        status,
        "beo_tiny",
        feature_slug,
        errors,
        readiness=readiness_value,
        approval_ref=approval_ref,
        selected_execution_set_id=selected_set,
        execution_mode=execution_mode,
        approval_bearing_hash=approval_bearing_hash,
        declared_files_status="complete" if allowed_files else "missing",
        forbidden_paths_status="complete" if forbidden_paths else "missing",
        generated_outputs_status="complete" if scope and "Generated outputs" in scope else "missing",
        verification_contract_status="complete" if verification else "missing",
        machine_hashes=current_hashes,
    )


def verify_standard(feature_slug: str, artifact_root: Path) -> dict[str, Any]:
    errors: list[dict[str, Any]] = []
    unavailable_errors: list[dict[str, Any]] = []
    context_text, context_error = read_text(artifact_root / "CONTEXT.md")
    plan_text, plan_error = read_text(artifact_root / "PLAN.md")
    tracker, tracker_error = read_json(artifact_root / "TRACKER.json")
    for e in (context_error, plan_error, tracker_error):
        if e:
            if e["code"] == "MISSING_FIELD" and (e["observed"] == "missing" or str(e["observed"]).startswith("unreadable:")):
                unavailable_errors.append(e)
            else:
                errors.append(e)
    if unavailable_errors:
        return result("unavailable", "standard", feature_slug, unavailable_errors, declared_files_status="unavailable", forbidden_paths_status="unavailable", generated_outputs_status="unavailable", verification_contract_status="unavailable")
    if errors:
        return result("invalid", "standard", feature_slug, errors, declared_files_status="invalid", forbidden_paths_status="invalid", generated_outputs_status="invalid", verification_contract_status="invalid")
    tracker = tracker or {}

    readiness = tracker.get("readiness", {}) if isinstance(tracker.get("readiness"), dict) else {}
    approval = tracker.get("approval", {}) if isinstance(tracker.get("approval"), dict) else {}
    integrity = tracker.get("integrity", {}) if isinstance(tracker.get("integrity"), dict) else {}

    readiness_status = readiness.get("status")
    approval_ref = approval.get("approval_ref")
    selected_set_id = readiness.get("selected_execution_set_id")
    execution_mode = readiness.get("execution_mode")
    selected_beads = readiness.get("selected_beads") or []
    selected_br_tasks = readiness.get("selected_br_tasks") or []

    if readiness_status != "PASS_EXECUTE":
        errors.append(err("STALE", "TRACKER.json.readiness.status", "PASS_EXECUTE", readiness_status or "missing"))
    if not approval_ref:
        errors.append(err("MISSING_FIELD", "TRACKER.json.approval.approval_ref", "non-empty ref", "missing"))
    if not selected_set_id:
        errors.append(err("MISSING_FIELD", "TRACKER.json.readiness.selected_execution_set_id", "selected execution set", "missing"))
    if execution_mode not in SUPPORTED_MODES:
        errors.append(err("UNSUPPORTED", "TRACKER.json.readiness.execution_mode", "single or ordered_batch", execution_mode or "missing"))
    if not selected_beads:
        errors.append(err("MISSING_FIELD", "TRACKER.json.readiness.selected_beads", "non-empty selected beads", "missing"))

    exec_sets = section(plan_text, "## Execution sets")
    set_rows = table_rows(exec_sets)
    set_found = False
    if selected_set_id and len(set_rows) >= 2:
        headers = set_rows[0]
        for row in set_rows[1:]:
            row_map = {headers[i]: row[i] for i in range(min(len(headers), len(row)))}
            if row_map.get("Set ID") == selected_set_id:
                set_found = True
                if execution_mode and row_map.get("Mode") != execution_mode:
                    errors.append(err("MISMATCH", "PLAN.md#Execution sets.Mode", row_map.get("Mode"), execution_mode))
                plan_beads = split_values([row_map.get("Beads", "")])
                if set(selected_beads) and plan_beads and set(selected_beads) != plan_beads:
                    errors.append(err("MISMATCH", "PLAN.md#Execution sets.Beads", sorted(plan_beads), selected_beads))
                break
    elif selected_set_id and exec_sets and re.search(rf"\b{re.escape(selected_set_id)}\b", exec_sets):
        set_found = True
    if selected_set_id and not set_found:
        errors.append(err("MISMATCH", "PLAN.md#Execution sets", f"selected set {selected_set_id}", "not found"))

    declared_files = set(approval.get("approved_declared_files") or [])
    forbidden_paths = set(approval.get("approved_forbidden_paths") or [])
    generated_outputs = set(approval.get("approved_generated_outputs") or [])
    verification_ref = approval.get("verification_contract_ref")

    plan_declared = split_values(list_after(section(plan_text, "## Declared files"), "## Declared files") or table_col_values(section(plan_text, "## Execution beads"), "Declared files"))
    plan_generated = split_values(list_after(section(plan_text, "## Generated outputs"), "## Generated outputs") or table_col_values(section(plan_text, "## Execution beads"), "Generated outputs"))
    plan_forbidden = split_values(list_after(section(plan_text, "## Forbidden paths"), "## Forbidden paths"))
    plan_verification = section(plan_text, "## Verification contract")

    if not declared_files:
        errors.append(err("MISSING_FIELD", "TRACKER.json.approval.approved_declared_files", "non-empty declared files", "missing"))
    elif plan_declared and not declared_files.issubset(plan_declared):
        errors.append(err("OUT_OF_SCOPE", "TRACKER.json.approval.approved_declared_files", sorted(plan_declared), sorted(declared_files)))
    if not forbidden_paths:
        errors.append(err("MISSING_FIELD", "TRACKER.json.approval.approved_forbidden_paths", "explicit forbidden paths", "missing"))
    elif plan_forbidden and forbidden_paths != plan_forbidden:
        errors.append(err("MISMATCH", "TRACKER.json.approval.approved_forbidden_paths", sorted(plan_forbidden), sorted(forbidden_paths)))
    if generated_outputs and plan_generated and not generated_outputs.issubset(plan_generated):
        errors.append(err("UNDECLARED_OUTPUT", "TRACKER.json.approval.approved_generated_outputs", sorted(plan_generated), sorted(generated_outputs)))
    if not verification_ref or not plan_verification:
        errors.append(err("MISSING_FIELD", "TRACKER.json.approval.verification_contract_ref", "verification contract matching PLAN.md", verification_ref or "missing"))

    if integrity.get("status") != "verified":
        errors.append(err("STALE", "TRACKER.json.integrity.status", "verified", integrity.get("status") or "missing"))

    # BR descriptions are optional, but if tracker references them and embeds per-task metadata, they must not expand PLAN scope.
    br_descriptions = tracker.get("br_descriptions") if isinstance(tracker.get("br_descriptions"), dict) else {}
    for br_id in selected_br_tasks:
        desc = br_descriptions.get(br_id)
        if not desc:
            continue
        br_files = set(desc.get("declared_files") or [])
        br_outputs = set(desc.get("generated_outputs") or [])
        if br_files and declared_files and not br_files.issubset(declared_files):
            errors.append(err("OUT_OF_SCOPE", f"TRACKER.json.br_descriptions.{br_id}.declared_files", sorted(declared_files), sorted(br_files)))
        if br_outputs and generated_outputs and not br_outputs.issubset(generated_outputs):
            errors.append(err("UNDECLARED_OUTPUT", f"TRACKER.json.br_descriptions.{br_id}.generated_outputs", sorted(generated_outputs), sorted(br_outputs)))

    current_hashes = {
        "context_hash": sha256_text(context_text or ""),
        "plan_hash": sha256_text(plan_text or ""),
    }
    compare_hashes(current_hashes, baseline_hashes(integrity), errors)
    status = output_status(errors, False)
    approval_bearing_hash = current_hashes.get("context_hash")
    return result(
        status,
        "standard",
        feature_slug,
        errors,
        readiness=readiness_status,
        approval_ref=approval_ref,
        selected_execution_set_id=selected_set_id,
        execution_mode=execution_mode,
        approval_bearing_hash=approval_bearing_hash,
        declared_files_status="complete" if declared_files and not any(e["path"].endswith("approved_declared_files") for e in errors) else "missing",
        forbidden_paths_status="complete" if forbidden_paths and not any(e["path"].endswith("approved_forbidden_paths") for e in errors) else "missing",
        generated_outputs_status="complete" if not any(e["code"] == "UNDECLARED_OUTPUT" for e in errors) else "invalid",
        verification_contract_status="complete" if verification_ref and plan_verification else "missing",
        machine_hashes=current_hashes,
    )


def apply_review_checks(payload: dict[str, Any], artifact_root: Path) -> dict[str, Any]:
    errors = list(payload["errors"])
    tracker, tracker_error = read_json(artifact_root / "TRACKER.json")
    if tracker_error:
        errors.append(tracker_error)
    tracker = tracker or {}
    execution = tracker.get("execution", {}) if isinstance(tracker.get("execution"), dict) else {}
    review_packet = execution.get("review_packet", {}) if isinstance(execution.get("review_packet"), dict) else {}
    verification_evidence = execution.get("verification_evidence") or review_packet.get("verification_evidence_refs") or []
    ready_for_review = execution.get("ready_for_review") or review_packet.get("ready_for_review")
    if not ready_for_review:
        errors.append(err("MISSING_FIELD", "TRACKER.json.execution.ready_for_review", True, ready_for_review or "missing"))
    if not verification_evidence:
        errors.append(err("MISSING_FIELD", "TRACKER.json.execution.verification_evidence", "non-empty verification evidence", "missing"))
    status = output_status(errors, payload["integrity"] == "unavailable")
    payload = dict(payload)
    payload["errors"] = errors
    payload["integrity"] = status
    payload["safe_for_execute"] = status == "verified" and payload.get("readiness") == "PASS_EXECUTE"
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description="Compute read-only BEO approval/integrity evidence")
    parser.add_argument("feature_slug", nargs="?", help="Feature slug; defaults to STATE.json active_feature")
    parser.add_argument("--root", default=".", help="Repository root")
    parser.add_argument("--feature", help="Feature slug (alternative to positional arg)")
    parser.add_argument("--lane", choices=sorted(SUPPORTED_LANES), help="Lane override")
    parser.add_argument("--artifact-root", help="Artifact root override")
    parser.add_argument("--state", help="Path to STATE.json")
    parser.add_argument("--check", choices=["validate", "execute", "review"], default="validate", help="Check intent mode")
    parser.add_argument("--output-json", action="store_true", default=True, help="Output JSON to stdout (default)")
    parser.add_argument("--strict", action="store_true", default=True, help="Fail closed on missing baselines and contradictions (default)")
    try:
        args = parser.parse_args()
    except SystemExit as exc:
        return 3 if exc.code else 0

    root = Path(args.root).resolve()
    state_path = Path(args.state).resolve() if args.state else root / ".beads" / "STATE.json"
    state, _ = read_json(state_path)
    state = state or {}
    feature_slug = args.feature or args.feature_slug or state.get("active_feature") or state.get("feature_slug")
    if args.feature and args.feature_slug and args.feature != args.feature_slug:
        print("error: conflicting feature slug values", file=sys.stderr)
        return 3
    if not feature_slug:
        payload = result("unavailable", args.lane or "standard", "", [err("MISSING_FIELD", "feature_slug", "non-empty slug", "missing")])
        print(json.dumps(payload, indent=2, sort_keys=True))
        return 2

    artifact_root = Path(args.artifact_root).resolve() if args.artifact_root else root / ".beads" / "artifacts" / feature_slug
    lane = args.lane
    if not lane:
        lane = "beo_tiny" if (artifact_root / "TICKET.md").exists() and not (artifact_root / "TRACKER.json").exists() else "standard"

    payload = verify_tiny(feature_slug, artifact_root) if lane == "beo_tiny" else verify_standard(feature_slug, artifact_root)
    if args.check == "review" and lane == "standard":
        payload = apply_review_checks(payload, artifact_root)
    print(json.dumps(payload, indent=2, sort_keys=True))
    if payload["integrity"] == "verified" and payload["safe_for_execute"]:
        return 0
    if payload["integrity"] == "unavailable":
        return 2
    if payload["integrity"] in {"invalid", "stale"}:
        return 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
