#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import re
import sys
import tempfile
from pathlib import Path
from typing import Any

DEFAULT_REGISTRY = Path(__file__).resolve().parents[1] / "registry"
SKILLS_ROOT = Path(__file__).resolve().parents[2]
REFERENCE_ROOT = Path(__file__).resolve().parents[1]

REQUIRED_REGISTRIES = [
    "command-contracts.json",
    "ticket-schema.json",
    "approval-envelope.json",
    "profiles.json",
    "pipeline.json",
    "memory-backends.json",
]
REQUIRED_COMMANDS = {
    "br.ready",
    "br.show",
    "br.create",
    "br.dep.add",
    "br.update.claim",
    "br.update.label",
    "br.comments.add",
    "br.close",
    "br.sync.flush",
    "bv.robot_triage",
    "bv.robot_next",
    "bv.robot_plan",
    "bv.robot_insights",
    "beo.check",
    "beo.memory_write",
    "obsidian.cli.create",
    "qmd.query",
    "qmd.status",
    "qmd.collection.list",
    "qmd.get",
    "qmd.index.update",
    "qmd.collection.add_obsidian_vault",
}
NEW_REFERENCES = [
    "kernel.md",
    "beads-authority.md",
    "decomposition.md",
    "ticket.md",
    "approval.md",
    "mutation-safety.md",
    "lifecycle-events.md",
    "modes.md",
    "memory.md",
]



def load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text())
    except FileNotFoundError:
        errors.append(f"missing registry: {path.name}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {path.name}: {exc}")
        return {}
    if not isinstance(data, dict):
        errors.append(f"registry must be object: {path.name}")
        return {}
    return data


def skill_name(text: str) -> str | None:
    match = re.search(r"(?m)^name:\s*(\S+)\s*$", text)
    return match.group(1) if match else None


def skill_exit_pairs(text: str) -> list[tuple[str, str]]:
    match = re.search(r"(?ms)^## Exits\b(?P<body>.*?)(?=^## |\Z)", text)
    if not match:
        return []
    pairs: list[tuple[str, str]] = []
    for line in match.group("body").splitlines():
        item = re.match(r"- `([^`]+)` -> `([^`]+)`", line.strip())
        if item:
            pairs.append((item.group(1), item.group(2)))
    return pairs


def validate_commands(registry: Path, errors: list[str]) -> None:
    data = load_json(registry / "command-contracts.json", errors)
    commands = data.get("commands")
    if not isinstance(commands, list):
        errors.append("command-contracts.commands must be a list")
        return
    ids = {cmd.get("command_id") for cmd in commands if isinstance(cmd, dict)}
    missing = sorted(REQUIRED_COMMANDS - ids)
    if missing:
        errors.append(f"missing command contract(s): {missing}")
    for cmd in commands:
        if not isinstance(cmd, dict):
            errors.append("command contract entry must be object")
            continue
        for field in ["command_id", "kind", "command", "argv", "owner_allow", "authority", "may_grant_approval"]:
            if field not in cmd:
                errors.append(f"{cmd.get('command_id', '<unknown>')} missing {field}")
        if cmd.get("may_grant_approval") is not False:
            errors.append(f"{cmd.get('command_id')} must not grant approval")
        if cmd.get("command_id", "").startswith("bv.") and "--robot" not in cmd.get("command", ""):
            errors.append(f"{cmd.get('command_id')} must use a bv robot flag")
        if cmd.get("kind") == "write" and cmd.get("command_id") not in {"beo.check", "br.sync.flush"} and cmd.get("command_id", "").startswith("br."):
            if "--actor" not in cmd.get("command", ""):
                errors.append(f"{cmd.get('command_id')} write command must bind --actor")
        if cmd.get("command_id") == "br.sync.flush" and "--actor" in cmd.get("command", ""):
            errors.append("br.sync.flush must not require --actor")
        if cmd.get("command_id", "").startswith("bv.") and "evidence_capture" not in cmd:
            errors.append(f"{cmd.get('command_id')} must name bv metadata evidence_capture fields")
        if cmd.get("command_id") == "beo.check":
            if "--phase" in cmd.get("argv", []):
                errors.append("beo.check base argv must work without --phase")
            if cmd.get("optional_argv") != ["--phase", "{phase}"]:
                errors.append("beo.check must expose optional --phase argv")
        if cmd.get("command_id") == "obsidian.cli.create":
            if "cwd" in cmd:
                errors.append("obsidian.cli.create must not rely on cwd vault targeting")
            argv = cmd.get("argv", [])
            if len(argv) < 3 or argv[1] != "vault={vault_name_or_id}" or argv[2] != "create":
                errors.append("obsidian.cli.create must put vault=<name|id> before create")
            for required_arg in ["path=beo-learnings/{safe_note_slug}.md", "content={markdown}"]:
                if required_arg not in argv:
                    errors.append(f"obsidian.cli.create missing {required_arg}")
        if cmd.get("command_id") == "qmd.query":
            argv = cmd.get("argv", [])
            for token in ["qmd", "query", "{query}", "--json", "-n"]:
                if token not in argv:
                    errors.append(f"qmd.query argv must include {token}")
            if "-c" not in argv and "--collection" not in argv:
                errors.append("qmd.query argv must include -c or --collection")
        if cmd.get("command_id") in {"qmd.status", "qmd.collection.list", "qmd.get"}:
            if cmd.get("kind") != "read":
                errors.append(f"{cmd.get('command_id')} must be read-only")
        if cmd.get("command_id") == "qmd.index.update":
            if cmd.get("kind") != "write_memory_index":
                errors.append("qmd.index.update kind must be write_memory_index")
            if set(cmd.get("owner_allow", [])) != {"beo-setup", "beo-learn"}:
                errors.append("qmd.index.update owner_allow must be beo-setup and beo-learn")
            if cmd.get("operation_class") != "memory_index_maintenance":
                errors.append("qmd.index.update must be memory_index_maintenance")
            if cmd.get("auto_index_allowed_after_learning_write") is not True:
                errors.append("qmd.index.update must allow post-learning-write refresh")
            if cmd.get("delivery_setup_auto_index_allowed") is not False:
                errors.append("qmd.index.update must not auto-index during delivery setup")
            for field in ["may_grant_review_verdict", "may_mutate_product_files"]:
                if cmd.get(field) is not False:
                    errors.append(f"qmd.index.update {field} must be false")
        if cmd.get("command_id") == "qmd.collection.add_obsidian_vault":
            if cmd.get("kind") != "write_memory_index":
                errors.append("qmd.collection.add_obsidian_vault kind must be write_memory_index")
            if cmd.get("operation_class") != "memory_index_maintenance":
                errors.append("qmd.collection.add_obsidian_vault must be memory_index_maintenance")
            if cmd.get("argv", [])[:3] != ["qmd", "collection", "add"]:
                errors.append("qmd.collection.add_obsidian_vault must use qmd collection add")
            for token in ["--name", "--mask", "**/*.md"]:
                if token not in cmd.get("argv", []):
                    errors.append(f"qmd.collection.add_obsidian_vault argv must include {token}")
            for field in ["may_grant_approval", "may_grant_review_verdict", "may_mutate_product_files"]:
                if cmd.get(field) is not False:
                    errors.append(f"qmd.collection.add_obsidian_vault {field} must be false")


def validate_pipeline(registry: Path, errors: list[str]) -> None:
    pipeline = load_json(registry / "pipeline.json", errors)
    vocabulary = load_json(registry / "ticket-schema.json", errors)
    owners = set(vocabulary.get("loadable_owners", []))
    terminals = set(vocabulary.get("terminal_targets", []))
    support_returns = set(vocabulary.get("support_return_targets", []))

    support_subroutines = pipeline.get("support_subroutines", {})
    if not isinstance(support_subroutines, dict):
        errors.append("pipeline.support_subroutines must be an object")
        support_subroutines = {}
    transitions = pipeline.get("transitions")
    if not isinstance(transitions, list):
        errors.append("pipeline.transitions must be a list")
        return
    legal: dict[str, set[tuple[str, str]]] = {}
    for transition in transitions:
        if not isinstance(transition, dict):
            errors.append("pipeline transition must be object")
            continue
        src = transition.get("from")
        cond = transition.get("condition_id")
        dst = transition.get("to")
        target_class = transition.get("target_class")
        if src not in owners and src != "start":
            errors.append(f"pipeline transition has unknown source {src}")
        if dst not in owners and dst not in terminals and dst not in support_returns:
            errors.append(f"pipeline transition has unknown target {dst}")
        if dst in support_returns:
            if src not in support_subroutines:
                errors.append(f"pipeline support return target {dst} is only valid from support subroutines, not {src}")
            if target_class != "support_return":
                errors.append(f"pipeline support return {src} -> {dst} must use target_class support_return")
        if cond == "learning_candidate":
            errors.append("learning_candidate must be a post_verdict_hooks control-plane hook, not a pipeline transition")
        if isinstance(src, str) and isinstance(cond, str) and isinstance(dst, str):
            legal.setdefault(src, set()).add((cond, dst))
    hooks = pipeline.get("post_verdict_hooks", {})
    if not isinstance(hooks, dict):
        errors.append("pipeline.post_verdict_hooks must be an object")
    else:
        if "learning_candidate" not in hooks:
            errors.append("pipeline.post_verdict_hooks.learning_candidate is required")
        for hook_id, hook in hooks.items():
            if not isinstance(hook, dict):
                errors.append(f"pipeline post verdict hook {hook_id} must be object")
                continue
            from_owners = hook.get("from_owners")
            if not isinstance(from_owners, list) or not from_owners:
                errors.append(f"pipeline post verdict hook {hook_id} must list from_owners")
            else:
                for owner in from_owners:
                    if owner not in owners:
                        errors.append(f"pipeline post verdict hook {hook_id} has unknown source owner {owner}")
            dst = hook.get("to")
            if dst not in owners:
                errors.append(f"pipeline post verdict hook {hook_id} has unknown target {dst}")
            if hook.get("authority") != "control_plane_only":
                errors.append(f"pipeline post verdict hook {hook_id} must be control_plane_only")
    for owner in owners:
        skill_path = SKILLS_ROOT / owner.replace("beo-", "") / "SKILL.md"
        if not skill_path.exists():
            continue
        text = skill_path.read_text()
        name = skill_name(text)
        if name != owner:
            errors.append(f"{skill_path} name mismatch: {name} != {owner}")
        for pair in skill_exit_pairs(text):
            if pair not in legal.get(owner, set()):
                errors.append(f"{owner} exit not in pipeline: {pair[0]} -> {pair[1]}")


def validate_refs(errors: list[str]) -> None:
    refs = REFERENCE_ROOT / "references"
    for name in NEW_REFERENCES:
        if not (refs / name).exists():
            errors.append(f"missing reference: {name}")


def validate_ticket_schema(registry: Path, errors: list[str]) -> None:
    schema = load_json(registry / "ticket-schema.json", errors)
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
    minimal = schema.get("minimal_ticket", {}).get("beo.ticket", {}) if isinstance(schema.get("minimal_ticket"), dict) else {}
    forbidden = {"readiness", "approval_ref", "integrity", "execution", "review"}
    present = sorted(forbidden & set(minimal))
    if present:
        errors.append(f"minimal ticket contains future-owned fields: {present}")


def validate_helper_semantics(errors: list[str]) -> None:
    scripts = REFERENCE_ROOT / "scripts"
    sys.path.insert(0, str(scripts))
    try:
        import beo_check  # type: ignore[import-not-found]
    except Exception as exc:
        errors.append(f"cannot import beo_check for semantic smoke: {exc}")
        return
    ticket = {
        "schema_version": "beo-beads/v3",
        "issue_id": "br-1",
        "mode": "quick",
        "request": "x",
        "done": ["y"],
        "human_gates": {"status": "not_applicable", "gates": []},
        "scope": {"files": {"allow": ["README.md"], "forbid": []}, "verify": {"commands": ["rtk git diff --check"]}},
        "acceptance_criteria": ["ok"],
        "atomicity": {"decision": "atomic", "reason": "one bounded repo-only edit", "rejects_multi_task": True},
        "posture_profile": "repo_only_low_risk",
        "readiness": "PASS_EXECUTE",
        "selected_execution_set": "set-1",
        "execution_mode": "normal",
    }
    base_hash = beo_check.plan_input_hash(ticket)
    appended = dict(ticket)
    appended.update(
        {
            "triage_records": [{"owner": "beo-plan", "purpose": "issue_selection", "selected_issue": "br-1"}],
            "execution": {"status": "ready_for_review", "changed_files": ["README.md"]},
            "review": {"verdict": "accept"},
            "debug": {"status": "not_used"},
            "runtime_events": [{"id": "evt-1", "kind": "user_stop", "created_at": "2026-01-01T00:00:00Z", "owner": "beo-execute", "issue_id": "br-1", "condition_id": "user_blocker", "basis_ref": "checks/run.json", "message": "Stop for user."}],
        }
    )
    if beo_check.plan_input_hash(appended) != base_hash:
        errors.append("plan_input_hash must survive triage/execution/review/debug/runtime append")
    issue = {"id": "br-1", "title": "Test", "status": "in_progress", "assignee": "assistant", "labels": ["beo:atomic"]}
    bead_hash = beo_check.sha256_text(beo_check.stable_json(beo_check.bead_snapshot(issue)))
    contracts_hash = "sha256:contracts"
    base_approval = beo_check.approval_hash(ticket, issue, bead_hash, contracts_hash)
    if beo_check.approval_hash(appended, issue, bead_hash, contracts_hash) != base_approval:
        errors.append("approval_projection_hash must exclude triage/execution/review/debug/runtime evidence")
    issue_with_comment = dict(issue, comments=[{"body": "ordinary comment"}], updated_at="2026-01-01T00:03:00Z")
    comment_hash = beo_check.sha256_text(beo_check.stable_json(beo_check.bead_snapshot(issue_with_comment)))
    if comment_hash != bead_hash:
        errors.append("bead_snapshot_hash must exclude ordinary comments and updated_at")
    changed_execution_set = dict(ticket, selected_execution_set="set-2")
    if beo_check.approval_hash(changed_execution_set, issue, bead_hash, contracts_hash) == base_approval:
        errors.append("approval_projection_hash must bind selected_execution_set")
    boundary_errors = beo_check.validate_phase_boundary(dict(ticket, readiness="PASS_EXECUTE"), "beo-plan")
    if not boundary_errors:
        errors.append("owner-boundary checks must reject future-owned fields for explicit phases")
    repair_ticket = dict(
        ticket,
        review={"verdict": "repair_same_scope"},
        runtime_events=[
            {
                "id": "evt-1",
                "kind": "change_request",
                "subtype": "repair_same_scope",
                "created_at": "2026-01-01T00:00:00Z",
                "owner": "beo-review",
                "issue_id": "br-1",
                "condition_id": "repair_same_scope",
                "basis_ref": "review:finding-1",
                "message": "Repair same scope.",
                "requested_by": "beo-review",
                "repair_type": "same_scope",
                "finding_refs": ["finding-1"],
                "prior_approval_ref": "checks/beo-check.json",
                "unchanged_boundaries": {
                    "scope.files.allow": True,
                    "generated_outputs": True,
                    "human_gates": True,
                    "acceptance_criteria": True,
                    "external_side_effects": True,
                    "stateful_external_systems": True,
                    "scope.files.forbid": True,
                    "scope.verify.commands": True,
                },
            }
        ],
    )
    if beo_check.validate_runtime_events(repair_ticket, "br-1"):
        errors.append("runtime event validator must accept complete same-scope repair events")
    bad_debug_return = dict(
        ticket,
        runtime_events=[
            {"id": "evt-1", "kind": "handoff", "subtype": "debug", "created_at": "2026-01-01T00:00:00Z", "owner": "beo-execute", "issue_id": "br-1", "condition_id": "root_cause_diagnosis_needed", "basis_ref": "execution:blocker", "message": "Need debug.", "caller_owner": "beo-execute", "return_to": "beo-execute", "return_condition_id": "debug_return_ready", "question": "Why is execution blocked?"},
            {"id": "evt-2", "kind": "return", "subtype": "debug", "created_at": "2026-01-01T00:01:00Z", "owner": "beo-debug", "issue_id": "br-1", "condition_id": "debug_returned", "basis_ref": "debug:artifact", "message": "Done.", "caller_owner": "beo-review", "return_to": "beo-review", "return_condition_id": "debug_return_ready", "diagnosis_status": "root_cause_proven", "diagnosis_ref": "debug:artifact"},
        ],
    )
    if not beo_check.validate_runtime_events(bad_debug_return, "br-1"):
        errors.append("runtime event validator must reject debug return that mismatches latest debug handoff")
    wrong_owner_debug_return = dict(
        ticket,
        runtime_events=[
            {"id": "evt-1", "kind": "handoff", "subtype": "debug", "created_at": "2026-01-01T00:00:00Z", "owner": "beo-execute", "issue_id": "br-1", "condition_id": "root_cause_diagnosis_needed", "basis_ref": "execution:blocker", "message": "Need debug.", "caller_owner": "beo-execute", "return_to": "beo-execute", "return_condition_id": "debug_return_ready", "question": "Why is execution blocked?"},
            {"id": "evt-2", "kind": "return", "subtype": "debug", "created_at": "2026-01-01T00:01:00Z", "owner": "beo-execute", "issue_id": "br-1", "condition_id": "debug_returned", "basis_ref": "debug:artifact", "message": "Done.", "caller_owner": "beo-execute", "return_to": "beo-execute", "return_condition_id": "debug_return_ready", "diagnosis_status": "root_cause_proven", "diagnosis_ref": "debug:artifact"},
        ],
    )
    if not beo_check.validate_runtime_events(wrong_owner_debug_return, "br-1"):
        errors.append("runtime event validator must reject support returns owned by the caller")
    direct_recall_return = dict(
        ticket,
        runtime_events=[
            {"id": "evt-1", "kind": "return", "subtype": "recall", "created_at": "2026-01-01T00:01:00Z", "owner": "beo-recall", "issue_id": "br-1", "condition_id": "memory_recalled", "basis_ref": "recall:summary", "message": "Done.", "caller_owner": "beo-execute", "return_to": "beo-execute", "result_status": "memory_recalled", "recall_ref": ".beads/artifacts/br-1/recall/RECALL_SUMMARY.md"},
        ],
    )
    if not beo_check.validate_runtime_events(direct_recall_return, "br-1"):
        errors.append("runtime event validator must reject recall return without prior handoff")
    malformed_events = dict(ticket, runtime_events=["bad"])
    if not beo_check.validate_runtime_events(malformed_events, "br-1"):
        errors.append("runtime event validator must reject malformed event entries")
    bad_author_recall = dict(
        ticket,
        runtime_events=[
            {"id": "evt-1", "kind": "handoff", "subtype": "recall", "created_at": "2026-01-01T00:00:00Z", "owner": "beo-recall", "issue_id": "br-1", "condition_id": "memory_recalled", "basis_ref": "author:need", "message": "Recall.", "caller_owner": "beo-author", "return_to": "beo-author", "query": "prior doctrine"},
        ],
    )
    if not beo_check.validate_runtime_events(bad_author_recall, "br-1"):
        errors.append("runtime event validator must reject beo-author as a ticket recall caller")
    bad_recall_ref = dict(
        ticket,
        runtime_events=[
            {"id": "evt-1", "kind": "handoff", "subtype": "recall", "created_at": "2026-01-01T00:00:00Z", "owner": "beo-execute", "issue_id": "br-1", "condition_id": "memory_recalled", "basis_ref": "execute:need", "message": "Recall.", "caller_owner": "beo-execute", "return_to": "beo-execute", "query": "prior failure"},
            {"id": "evt-2", "kind": "return", "subtype": "recall", "created_at": "2026-01-01T00:01:00Z", "owner": "beo-recall", "issue_id": "br-1", "condition_id": "memory_recalled", "basis_ref": "recall:summary", "message": "Done.", "caller_owner": "beo-execute", "return_to": "beo-execute", "result_status": "memory_recalled", "recall_ref": ".beads/artifacts/br-1/recall/WRONG.md"},
        ],
    )
    if not beo_check.validate_runtime_events(bad_recall_ref, "br-1"):
        errors.append("runtime event validator must reject non-canonical recall_ref")
    early_learning = dict(
        ticket,
        runtime_events=[
            {"id": "evt-1", "kind": "learning_candidate", "created_at": "2026-01-01T00:00:00Z", "owner": "beo-debug", "issue_id": "br-1", "condition_id": "learning_candidate", "basis_ref": "debug:none", "message": "Learn.", "case_type": "debug_pattern", "source_phase": "beo-debug"},
        ],
    )
    if not beo_check.validate_runtime_events(early_learning, "br-1"):
        errors.append("runtime event validator must reject learning_candidate before source return/verdict")
    if beo_check.validate_same_scope_repair_request(repair_ticket):
        errors.append("same-scope repair must accept latest relevant change_request")
    superseded = dict(repair_ticket, runtime_events=repair_ticket["runtime_events"] + [{"id": "evt-3", "kind": "change_request", "subtype": "scope_delta", "created_at": "2026-01-01T00:02:00Z", "owner": "beo-review", "issue_id": "br-1", "condition_id": "scope_delta_required", "basis_ref": "review:finding-2", "message": "Scope changed."}])
    if not beo_check.validate_same_scope_repair_request(superseded):
        errors.append("same-scope repair must reject change_request superseded by scope_delta")
    if not beo_check.validate_review_verdict({"verdict": "cannot_deliver"}):
        errors.append("cannot_deliver verdict must require reason_class")
    if beo_check.validate_review_verdict({"verdict": "cannot_deliver", "reason_class": "user_owned"}):
        errors.append("cannot_deliver verdict must accept legal reason_class")
    bad_mode = dict(ticket, mode="typo")
    if not any("mode must be one of" in err for err in beo_check.validate_plan(Path.cwd(), bad_mode, {"id": "br-1", "labels": ["beo:atomic"]})):
        errors.append("validate_plan must reject unknown ticket modes")
    removed_learning_tree = "skills/beo/reference" + "/learnings"
    curated_scope = dict(ticket, scope={"files": {"allow": [f"{removed_learning_tree}/example.md"], "forbid": []}, "verify": {"commands": ["rtk git diff --check"]}})
    if not any("curated learning" in err for err in beo_check.validate_plan(Path.cwd(), curated_scope, {"id": "br-1", "labels": ["beo:atomic"]})):
        errors.append("validate_plan must reject curated learning write paths")
    old_env = {key: os.environ.get(key) for key in ["BR_ACTOR", "BEO_ACTOR", "AGENT_NAME", "BR_AGENT_NAME", "ACTOR"]}
    try:
        for key in old_env:
            os.environ.pop(key, None)
        issue = {"status": "in_progress", "assignee": "assistant"}
        if beo_check.claim_valid(issue):
            errors.append("claim_valid must fail closed without actor identity")
        os.environ["AGENT_NAME"] = "assistant"
        if not beo_check.claim_valid(issue):
            errors.append("claim_valid must accept matching AGENT_NAME")
        os.environ["BR_ACTOR"] = "other"
        if beo_check.claim_valid(issue):
            errors.append("claim_valid must prefer BR_ACTOR and reject mismatch")
        os.environ["BR_ACTOR"] = "assistant"
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "new.txt").write_text("new")
            drift_ticket = dict(ticket, execution={"prestate_refs": {"files": {"new.txt": "missing"}}, "changed_files": []})
            if not any("unexplained prestate drift" in err for err in beo_check.validate_execute(root, drift_ticket, issue, "complete")):
                errors.append("validate_execute must reject files that appear after missing prestate")
            missing_prestate_ticket = dict(ticket, execution={"prestate_refs": {"files": {}}, "changed_files": ["new.txt"]})
            if not any("missing prestate hash" in err for err in beo_check.validate_execute(root, missing_prestate_ticket, issue, "complete")):
                errors.append("validate_execute must require prestate for changed files")
    finally:
        for key, value in old_env.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value


def main(argv: list[str]) -> int:
    registry = Path(argv[0]).resolve() if argv else DEFAULT_REGISTRY
    errors: list[str] = []
    for name in REQUIRED_REGISTRIES:
        load_json(registry / name, errors)
    validate_commands(registry, errors)
    validate_pipeline(registry, errors)
    validate_ticket_schema(registry, errors)
    validate_refs(errors)
    validate_helper_semantics(errors)
    if errors:
        for message in errors:
            print(f"ERROR: {message}", file=sys.stderr)
        return 1
    print("BEO registry check passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
