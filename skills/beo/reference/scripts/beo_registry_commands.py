#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from beo_utils import load_json

def validate_commands(registry: Path, errors: list[str]) -> None:
    data = load_json(registry / "command-contracts.json", {})
    commands = data.get("commands")
    if not isinstance(commands, list):
        errors.append("command-contracts.commands must be a list")
        return
        
    by_id = {}
    for cmd in commands:
        if not isinstance(cmd, dict):
            continue
        cmd_id = cmd.get("command_id")
        if cmd_id in by_id:
            errors.append(f"duplicate command_id: {cmd_id}")
        else:
            by_id[cmd_id] = cmd
    helpers = data.get("internal_helpers", {})
    
    recall_helper = helpers.get("beo-recall") if isinstance(helpers, dict) else None
    if not isinstance(recall_helper, dict):
        errors.append("command-contracts.internal_helpers.beo-recall is required")
    else:
        if recall_helper.get("loadable_owner") is not False:
            errors.append("beo-recall internal helper must not be a loadable owner")
        if set(recall_helper.get("entry_commands", [])) != {"beo.recall", "beo.recall.write_summary"}:
            errors.append("beo-recall entry_commands must be beo.recall and beo.recall.write_summary")
        if set(recall_helper.get("may_use_commands", [])) != {"qmd.query", "qmd.get"}:
            errors.append("beo-recall may_use_commands must be limited to qmd.query and qmd.get")
        for field in ["may_grant_approval", "may_grant_review_verdict", "may_grant_execution_permission", "may_close_issues", "may_resolve_human_gates"]:
            if recall_helper.get(field) is not False:
                errors.append(f"beo-recall {field} must be false")
        if recall_helper.get("writes") != []:
            errors.append("beo-recall internal helper must not declare writes")
            
    if isinstance(helpers, dict):
        for helper_id, helper in helpers.items():
            if not isinstance(helper, dict):
                continue
            for command_id in helper.get("may_use_commands", []):
                command = by_id.get(command_id)
                if command is None:
                    errors.append(f"helper {helper_id} uses undeclared command {command_id}")
                else:
                    if command.get("operation_class") == "learning" and helper_id not in {"beo-learn", "beo-debug"}:
                        errors.append(f"{helper_id} must not use learning command {command_id}")
                    if command.get("operation_class") == "memory_index_maintenance" and helper_id != "beo-setup":
                        errors.append(f"{helper_id} must not use memory index maintenance command {command_id}")
                    if command.get("mutation_scope") == "product_files" and helper_id != "beo-execute":
                        errors.append(f"{helper_id} must not use product-mutating command {command_id}")
                    if command.get("mutation_scope") == "lifecycle_only" and helper_id not in {"beo-plan", "beo-review"}:
                        errors.append(f"{helper_id} must not use lifecycle-mutating command {command_id}")
                    if command.get("mutation_scope") == "reservation_log_only" and helper_id not in {"beo-plan", "beo-validate", "beo-execute", "beo-review"}:
                        errors.append(f"{helper_id} must not use reservation-mutating command {command_id}")

    for cmd in commands:
        if not isinstance(cmd, dict):
            continue
        cmd_id = cmd.get("command_id")
        if not cmd_id:
            errors.append("command contract must have command_id")
            continue
        if cmd.get("kind") == "read_gc_expired":
            if cmd.get("mutation_scope") not in {"reservation_log_only", "evidence_only"}:
                errors.append(f"{cmd_id} has kind read_gc_expired but mutation_scope is not reservation_log_only or evidence_only")
