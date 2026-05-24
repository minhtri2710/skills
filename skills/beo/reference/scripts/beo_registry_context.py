#!/usr/bin/env python3
from __future__ import annotations

import re
from functools import lru_cache
from pathlib import Path
from typing import Any

from beo_utils import load_json

class RegistryContext:
    def __init__(self, root: Path):
        self.root = root

    @lru_cache(maxsize=16)
    def load_registry(self, name: str) -> dict[str, Any]:
        path = self.root / "skills" / "beo" / "reference" / "registry" / f"{name}.json"
        if not path.exists():
            path = Path(__file__).resolve().parents[1] / "registry" / f"{name}.json"
        return load_json(path, {})

    @property
    def schema(self) -> dict[str, Any]:
        return self.load_registry("ticket-schema")

    @property
    def pipeline(self) -> dict[str, Any]:
        return self.load_registry("pipeline")

    @property
    def profiles(self) -> dict[str, Any]:
        return self.load_registry("profiles")

    @property
    def command_contracts(self) -> dict[str, Any]:
        return self.load_registry("command-contracts")

    @property
    def owners(self) -> set[str]:
        pipeline = self.pipeline
        if not pipeline:
            return {"beo-plan", "beo-validate", "beo-execute", "beo-review", "beo-debug", "beo-learn", "beo-author", "beo-setup"}
        dsm = pipeline.get("delivery_state_machine", {})
        classes = {}
        classes["delivery"] = dsm.get("owner_classes", {}).get("delivery", [])
        classes["support_runtime"] = list(pipeline.get("support_subroutines", {}).keys())
        maint = list(pipeline.get("maintenance_skills", {}).keys())
        hooks = pipeline.get("post_verdict_hooks", {})
        for hook in hooks.values():
            if isinstance(hook, dict) and "to" in hook:
                maint.append(hook["to"])
        classes["maintenance"] = list(set(maint))
        all_owners = set()
        for cls_members in classes.values():
            if isinstance(cls_members, list):
                all_owners.update(str(o) for o in cls_members)
        return all_owners or {"beo-plan", "beo-validate", "beo-execute", "beo-review", "beo-debug", "beo-learn", "beo-author", "beo-setup"}

    @property
    def delivery_owners(self) -> set[str]:
        pipeline = self.pipeline
        if not pipeline:
            return {"beo-plan", "beo-validate", "beo-execute", "beo-review"}
        dsm = pipeline.get("delivery_state_machine", {})
        delivery = dsm.get("owner_classes", {}).get("delivery", [])
        return set(str(o) for o in delivery)

    @property
    def runtime_event_owners(self) -> set[str]:
        pipeline = self.pipeline
        if not pipeline:
            return {"beo-plan", "beo-validate", "beo-execute", "beo-review", "beo-debug"}
        support = list(pipeline.get("support_subroutines", {}).keys())
        return self.delivery_owners | set(str(o) for o in support)

    @property
    def modes(self) -> set[str]:
        profiles = self.profiles
        if not profiles:
            return {"quick", "standard", "strict"}
        modes = profiles.get("modes", {})
        return set(str(m) for m in modes)

    @property
    def protected_patterns(self) -> list[str]:
        profiles = self.profiles
        if not profiles:
            return []
        protected = profiles.get("protected_path_defaults", [])
        return [str(pattern) for pattern in protected]

    @property
    def side_effect_patterns(self) -> re.Pattern:
        profiles = self.profiles
        if not profiles:
            return re.compile(r"\b(deploy|migration|publish)\b", re.IGNORECASE)
        side_effects = profiles.get("side_effect_command_patterns")
        if isinstance(side_effects, list) and side_effects:
            escaped = [re.escape(str(pattern)).replace(r"\ ", r"\s+") for pattern in side_effects]
            return re.compile(r"\b(" + "|".join(escaped) + r")\b", re.IGNORECASE)
        return re.compile(r"\b(deploy|migration|publish)\b", re.IGNORECASE)

    @property
    def abandon_reasons(self) -> set[str]:
        event = self.schema.get("runtime_event", {})
        reasons = event.get("abandon_reason", [])
        return set(str(r) for r in reasons)

    @property
    def diagnosis_statuses(self) -> set[str]:
        event = self.schema.get("runtime_event", {})
        statuses = event.get("diagnosis_status", [])
        return set(str(s) for s in statuses)

    @property
    def future_fields(self) -> dict[str, set[str]]:
        future = self.schema.get("future_owned_field_rule", {})
        return {str(k): set(str(v) for v in val) for k, val in future.items() if isinstance(val, list)}
