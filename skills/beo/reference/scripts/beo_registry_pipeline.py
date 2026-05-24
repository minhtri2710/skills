#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path
from typing import Any

from beo_utils import load_json

def validate_pipeline(registry: Path, errors: list[str], ticket_schema: dict[str, Any] | None = None) -> None:
    pipeline = load_json(registry / "pipeline.json", {})
    vocabulary = ticket_schema or load_json(registry / "ticket-schema.json", {})
    
    owners = set()
    if "delivery_state_machine" in pipeline:
        dsm = pipeline["delivery_state_machine"]
        for cls_members in dsm.get("owner_classes", {}).values():
            if isinstance(cls_members, list):
                owners.update(cls_members)
        owners.update(pipeline.get("support_subroutines", {}).keys())
        for hook in pipeline.get("post_verdict_hooks", {}).values():
            if isinstance(hook, dict) and "to" in hook:
                owners.add(hook["to"])
        owners.update(pipeline.get("maintenance_skills", {}).keys())
        virtual_sources = set(dsm.get("virtual_sources", []))
    else:
        owner_classes = pipeline.get("owner_classes", {})
        for cls_members in owner_classes.values():
            if isinstance(cls_members, list):
                owners.update(cls_members)
        virtual_sources = set(pipeline.get("virtual_sources", []))

    terminals = set(vocabulary.get("terminal_targets", []))
    support_returns = set(vocabulary.get("support_return_targets", []))

    if "beo-recall" in owners:
        errors.append("beo-recall must not be a loadable owner in pipeline.json")

    # Transitions checking
    transitions = []
    if "delivery_state_machine" in pipeline:
        transitions.extend(pipeline["delivery_state_machine"].get("transitions", []))
    
    for sub in pipeline.get("support_subroutines", {}).values():
        if isinstance(sub, dict) and "transitions" in sub:
            transitions.extend(sub["transitions"])
            
    for hook in pipeline.get("post_verdict_hooks", {}).values():
        if isinstance(hook, dict) and "transitions" in hook:
            transitions.extend(hook["transitions"])
            
    for maint in pipeline.get("maintenance_skills", {}).values():
        if isinstance(maint, dict) and "transitions" in maint:
            transitions.extend(maint["transitions"])

    for trans in transitions:
        if not isinstance(trans, dict):
            continue
        src = trans.get("from")
        dst = trans.get("to")
        cond = trans.get("condition_id")
        t_class = trans.get("target_class")
        
        if src not in owners and src not in virtual_sources:
            errors.append(f"transition source {src} is not a valid owner")
            continue
            
        if dst not in owners and dst not in terminals and dst not in support_returns:
            errors.append(f"transition target {dst} is not valid")
            
        if t_class == "loadable_owner" and dst not in owners:
            errors.append(f"target {dst} has class loadable_owner but is not an owner")
        elif t_class == "terminal" and dst not in terminals:
            errors.append(f"target {dst} has class terminal but is not a terminal")
        elif t_class == "support_runtime" and dst not in owners:
            errors.append(f"target {dst} has class support_runtime but is not an owner")

    # Validate post-verdict hooks
    if "post_verdict_hooks" in pipeline:
        for hook_id, hook in pipeline["post_verdict_hooks"].items():
            if not isinstance(hook, dict):
                continue
            for owner in hook.get("from_owners", []):
                if owner not in owners:
                    errors.append(f"pipeline post verdict hook {hook_id} has unknown source owner {owner}")
            dst = hook.get("to")
            if dst not in owners:
                errors.append(f"pipeline post verdict hook {hook_id} has unknown target {dst}")
            if hook.get("authority") != "control_plane_only":
                errors.append(f"pipeline post verdict hook {hook_id} must be control_plane_only")
