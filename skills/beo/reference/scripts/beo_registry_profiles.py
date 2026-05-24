#!/usr/bin/env python3
from __future__ import annotations

from pathlib import Path

from beo_utils import load_json

def validate_profiles(registry: Path, errors: list[str]) -> None:
    profiles = load_json(registry / "profiles.json", {})
    modes = profiles.get("modes", {})
    if not isinstance(modes, dict):
        errors.append("profiles.json modes must be an object")
        return
        
    for name in ["quick", "standard", "strict"]:
        if name not in modes:
            errors.append(f"profiles.json modes must define {name} posture rules")
            
    budget_policy = profiles.get("repair_budget_policy", {})
    if not isinstance(budget_policy, dict):
        errors.append("profiles.json repair_budget_policy must be an object")
    else:
        for name in ["quick", "standard", "strict"]:
            if name not in budget_policy:
                errors.append(f"repair_budget_policy must define budget rule for {name}")
                continue
            rule = budget_policy[name]
            if not isinstance(rule, dict):
                errors.append(f"repair_budget_policy.{name} must be an object")
                continue
            budget = rule.get("budget")
            if name == "quick" and budget != 1:
                errors.append("quick repair budget must be exactly 1")
            elif name == "standard" and budget != 2:
                errors.append("standard repair budget must be exactly 2")
            elif name == "strict" and budget != "explicit":
                errors.append("strict repair budget must declare 'explicit'")

    protected = profiles.get("protected_path_defaults", [])
    if not isinstance(protected, list) or not protected:
        errors.append("profiles.json protected_path_defaults must be a non-empty list of glob patterns")
        
    side_effects = profiles.get("side_effect_command_patterns", [])
    if not isinstance(side_effects, list) or not side_effects:
        errors.append("profiles.json side_effect_command_patterns must be a non-empty list")
