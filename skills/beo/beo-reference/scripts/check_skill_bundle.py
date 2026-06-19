#!/usr/bin/env python3
import json
import re
import sys
from pathlib import Path
from typing import Any

# Define paths relative to the script location
SCRIPT_DIR = Path(__file__).resolve().parent
BEO_ROOT = SCRIPT_DIR.parents[1]  # <repo>/skills/beo (resolves dynamically)
REF_DIR = BEO_ROOT / "beo-reference"


def _without_code_fences(text: str) -> str:
    return re.sub(r"```.*?```", "", text, flags=re.DOTALL)


def _path_like_refs(text: str) -> set[str]:
    stripped = _without_code_fences(text)
    refs = set(re.findall(r"`([^`]+)`", stripped))
    refs.update(re.findall(r"\[[^\]]+\]\(([^)]+)\)", stripped))
    return {ref for ref in refs if "/" in ref or ref.endswith(('.md', '.json', '.py'))}


def _is_pseudo_ref(ref: str) -> bool:
    return (
        ref.startswith(("http://", "https://", "br-comment:", "file://"))
        or "<" in ref
        or "pipeline.condition_id" in ref
        or "safe_evidence_ref" in ref
        or ref.startswith(".beads/")
        or ref in {"state.json", "TICKET.json", "harness-proposal.json", "PLAN.md", "runtime-events.jsonl", "AGENTS.md", "README.md", "utils.py", "unrelated.py", ".git/**", "**/.env", "yes/no", "user/operator", "None — no blocking user/operator decisions remain", "skills/beo/", "skills/beo/beo-reference/learnings/"}
    )


def _check_ref_exists(errors: list[str], source: Path, ref: str) -> None:
    if _is_pseudo_ref(ref) or ref.startswith("#"):
        return
    if " -> " in ref:
        skill_name, path_part = ref.split(" -> ", 1)
        if skill_name == "beo-reference":
            if source.is_relative_to(REF_DIR):
                # Source is already inside beo-reference; path_part is already correct.
                ref = path_part
            else:
                ref = f"../beo-reference/{path_part}"
        else:
            errors.append(f"Unknown cross-skill reference format in {source}: {ref}")
            return
    ref_path = ref.split("#", 1)[0]
    if not ref_path:
        return
    if ref_path.startswith("skills/beo/"):
        target = (BEO_ROOT.parents[1] / ref_path).resolve()
    elif source.is_relative_to(REF_DIR) and ref_path.startswith(("references/", "registry/", "scripts/", "templates/", "examples/")):
        target = (REF_DIR / ref_path).resolve()
    elif source.is_relative_to(REF_DIR) and source.parent.name == "references" and ref_path.endswith(".py"):
        target = (REF_DIR / "scripts" / ref_path).resolve()
    elif source.is_relative_to(REF_DIR) and source.parent.name == "references" and ref_path == "AGENTS.template.md":
        target = (REF_DIR / "templates" / ref_path).resolve()
    elif source.is_relative_to(REF_DIR) and re.fullmatch(r"beo-[a-z-]+/.+", ref_path):
        target = (BEO_ROOT / ref_path).resolve()
    else:
        target = (source.parent / ref_path).resolve()
    if not target.exists():
        try:
            display_source = source.relative_to(BEO_ROOT)
        except ValueError:
            display_source = source
        errors.append(f"Unresolved relative reference in {display_source}: {ref}")


def _collect_enums(value: Any) -> set[Any]:
    enums: set[Any] = set()
    if isinstance(value, dict):
        if isinstance(value.get("enum"), list):
            enums.update(value["enum"])
        for child in value.values():
            enums.update(_collect_enums(child))
    elif isinstance(value, list):
        for child in value:
            enums.update(_collect_enums(child))
    return enums


def _build_outcome_index(raw_map: Any) -> dict[str, set[str]]:
    """Map skill -> set of (outcomes + transition condition_ids).

    Accepts either a dict-shaped entry (``{outcomes, transitions}``) or a
    legacy list/string entry, which is normalized to a set.
    """
    index: dict[str, set[str]] = {}
    for key, value in raw_map.items():
        if isinstance(value, dict):
            index[key] = {
                *value.get("outcomes", []),
                *(transition.get("condition_id") for transition in value.get("transitions", [])),
            }
        else:
            index[key] = set(value)
    return index


def run_checks() -> int:
    errors = []

    # 1. Verify all 10 BEO SKILL.md files exist
    skills = [
        "beo-plan", "beo-validate", "beo-execute", "beo-review",
        "beo-debug", "beo-learn", "beo-author", "beo-climate",
        "beo-setup", "beo-reference"
    ]
    for skill in skills:
        skill_path = BEO_ROOT / skill / "SKILL.md"
        if not skill_path.exists():
            errors.append(f"Missing skill card: {skill_path.relative_to(BEO_ROOT)}")
        else:
            # Check length limit (500 non-frontmatter lines)
            content = skill_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            non_frontmatter_lines = []
            in_frontmatter = False
            frontmatter_count = 0
            for line in lines:
                if line.strip() == "---":
                    frontmatter_count += 1
                    in_frontmatter = (frontmatter_count == 1)
                    continue
                if not in_frontmatter:
                    non_frontmatter_lines.append(line)
            if len(non_frontmatter_lines) > 500:
                errors.append(f"Skill card exceeds 500 non-frontmatter lines: {skill_path.relative_to(BEO_ROOT)} ({len(non_frontmatter_lines)} lines)")

            # Check format: Read, Do, Write, Emit, Never
            headers = ["## Read", "## Do", "## Write", "## Emit", "## Never"]
            for header in headers:
                if header not in content:
                    errors.append(f"Skill card {skill}/SKILL.md is missing expected header: {header}")

            # Check no ticket-plan.schema.json references
            if "ticket-plan.schema.json" in content:
                errors.append(f"Skill card {skill}/SKILL.md references legacy ticket-plan.schema.json")
            for ref in _path_like_refs(content):
                if ref.startswith("../beo-reference/") or ref.startswith("beo-reference -> "):
                    _check_ref_exists(errors, skill_path, ref)

    # 2. Check shared directory structures
    if not REF_DIR.exists():
        errors.append("Missing beo-reference directory")
        return 1

    required_references = [
        "kernel.md", "doctrine-map.md", "artifact-boundaries.md",
        "lifecycle.md", "phase-contracts.md", "safety.md", "memory.md", "degraded-tools.md"
    ]
    for ref in required_references:
        p = REF_DIR / "references" / ref
        if not p.exists():
            errors.append(f"Missing reference: {p.relative_to(BEO_ROOT)}")

    required_registries = [
        "pipeline.json", "profiles.json", "ticket.schema.json",
        "state.schema.json", "runtime-event.schema.json", "approval-envelope.json",
        "reservation-schema.json", "phase-contracts.json"
    ]
    for reg in required_registries:
        p = REF_DIR / "registry" / reg
        if not p.exists():
            errors.append(f"Missing registry: {p.relative_to(BEO_ROOT)}")

    required_examples = [
        "quick-mode-golden-trace.md", "negative-dirty-approved-path.md",
        "negative-approval-predicate-failed.md", "negative-repair-rescope-required.md",
        "negative-containment-review-needed.md"
    ]
    for ex in required_examples:
        p = REF_DIR / "examples" / ex
        if not p.exists():
            errors.append(f"Missing example: {p.relative_to(BEO_ROOT)}")

    required_templates = ["AGENTS.template.md", "PLAN.template.md"]
    for t in required_templates:
        p = REF_DIR / "templates" / t
        if not p.exists():
            errors.append(f"Missing template: {p.relative_to(BEO_ROOT)}")

    # 3. Check phase-contracts.json internal consistency
    contracts_path = REF_DIR / "registry" / "phase-contracts.json"
    pipeline_path = REF_DIR / "registry" / "pipeline.json"
    events_path = REF_DIR / "registry" / "runtime-event.schema.json"
    state_schema_path = REF_DIR / "registry" / "state.schema.json"

    if contracts_path.exists() and pipeline_path.exists() and events_path.exists() and state_schema_path.exists():
        try:
            contracts = json.loads(contracts_path.read_text(encoding="utf-8"))
            pipeline = json.loads(pipeline_path.read_text(encoding="utf-8"))
            events = json.loads(events_path.read_text(encoding="utf-8"))
            state_schema = json.loads(state_schema_path.read_text(encoding="utf-8"))

            classes = contracts.get("classes", {})
            skills_config = contracts.get("skills", {})

            # Each skill appears in exactly one class and has exactly one config.
            all_classified = []
            for c_name, skill_list in classes.items():
                all_classified.extend(skill_list)
            for skill in skills:
                count = all_classified.count(skill)
                if count != 1:
                    errors.append(f"Skill {skill} is classified {count} times (must be exactly 1)")
            configured_skills = set(skills_config)
            required_skills = set(skills)
            missing_configs = sorted(required_skills - configured_skills)
            unknown_configs = sorted(configured_skills - required_skills)
            if missing_configs:
                errors.append(f"phase-contracts.json missing skill config(s): {missing_configs}")
            if unknown_configs:
                errors.append(f"phase-contracts.json contains unknown skill config(s): {unknown_configs}")

            # Check transitions and typed outcome registries
            pipeline_conditions = {t["condition_id"] for t in pipeline.get("transitions", [])}
            runtime_event_kinds = set(events.get("properties", {}).get("kind", {}).get("enum", []))
            support_by_skill = _build_outcome_index(pipeline.get("support_subroutines", {}))
            maintenance_by_skill = _build_outcome_index(pipeline.get("maintenance_skills", {}))
            lookup_by_skill = _build_outcome_index(pipeline.get("lookup_skills", {}))
            delivery_by_skill = {}
            for transition in pipeline.get("transitions", []):
                delivery_by_skill.setdefault(transition["from"], set()).add(transition["condition_id"])
            handoff_subtypes = set(pipeline.get("delivery_user_handoff_subtypes", []))
            route_conditions = {t["condition_id"] for t in pipeline.get("transitions", [])}
            if "user_review_needed" not in pipeline.get("route_classes", {}).get("user_handoff", []):
                errors.append("pipeline.json must classify user_review_needed under route_classes.user_handoff")
            if "user_review_needed" in pipeline.get("route_classes", {}).get("planning", []):
                errors.append("pipeline.json must not classify user_review_needed under route_classes.planning")
            mirrored_subtypes = sorted(handoff_subtypes & route_conditions)
            if mirrored_subtypes:
                errors.append(f"delivery_user_handoff_subtypes must remain metadata, not route IDs: {mirrored_subtypes}")
            event_kind_enums = set(events.get("properties", {}).get("kind", {}).get("enum", []))
            mirrored_event_subtypes = sorted(handoff_subtypes & event_kind_enums)
            if mirrored_event_subtypes:
                errors.append(f"delivery_user_handoff_subtypes must not be runtime-event kinds: {mirrored_event_subtypes}")
            state_enums = {item for item in _collect_enums(state_schema) if isinstance(item, str)}
            mirrored_state_subtypes = sorted(handoff_subtypes & state_enums)
            if mirrored_state_subtypes:
                errors.append(f"delivery_user_handoff_subtypes must not be state schema enum values: {mirrored_state_subtypes}")

            outcome_fields_by_class = {
                "delivery_owner": "may_emit_delivery_conditions",
                "support_subroutine": "may_emit_support_outcomes",
                "maintenance": "may_emit_maintenance_outcomes",
                "read_only_lookup": "may_emit_lookup_outcomes",
            }
            expected_outcomes_by_class = {
                "delivery_owner": delivery_by_skill,
                "support_subroutine": support_by_skill,
                "maintenance": maintenance_by_skill,
                "read_only_lookup": lookup_by_skill,
            }
            class_by_skill = {skill_name: class_name for class_name, skill_list in classes.items() for skill_name in skill_list}
            owner_rules = events.get("beo_contract_metadata", {}).get("owner_rules", {})
            state_write_policy = {
                "beo-plan": {"initialize"},
                "beo-validate": {"phase", "approval"},
                "beo-execute": {"phase", "execution", "review"},
                "beo-review": {"phase", "review"},
                "beo-debug": set(),
                "beo-learn": set(),
                "beo-author": set(),
                "beo-climate": set(),
                "beo-setup": set(),
                "beo-reference": set(),
            }
            artifact_authorities = {
                "plan_artifact",
                "ticket",
                "br.child_beads",
                "br.dependency_edges",
                "br.decomposition_comments",
                "br.labels.beo_blocked_user",
                "br.final_route_comments",
                "strict_reservation",
                "validation_evidence",
                "approved_product_files",
                "declared_generated_outputs",
                "harness_proposal",
                "br.close_on_verdict_accept",
                "reservation_release",
                "advisory_learning_note",
                "BEO_control_plane_files",
                "setup_status_output",
                "explicitly_authorized_memory_setup",
            }

            for s_name, s_conf in skills_config.items():
                class_name = class_by_skill.get(s_name)
                if s_conf.get("class") != class_name:
                    errors.append(f"Skill {s_name} class mismatch: {s_conf.get('class')} != {class_name}")
                allowed_outcome_field = outcome_fields_by_class.get(class_name)
                for field in outcome_fields_by_class.values():
                    if field in s_conf and field != allowed_outcome_field:
                        errors.append(f"Skill {s_name} uses outcome field {field} but class {class_name} requires {allowed_outcome_field}")
                declared_state_fields = set(s_conf.get("state_write_fields", []))
                expected_state_fields = state_write_policy.get(s_name, set())
                if declared_state_fields != expected_state_fields:
                    errors.append(f"Skill {s_name} state_write_fields mismatch: declared {sorted(declared_state_fields)} expected {sorted(expected_state_fields)}")
                unknown_authorities = sorted(set(s_conf.get("artifact_write_authorities", [])) - artifact_authorities)
                if unknown_authorities:
                    errors.append(f"Skill {s_name} uses unknown artifact write authorit(y/ies): {unknown_authorities}")
                expected_outcomes = expected_outcomes_by_class.get(class_name, {}).get(s_name, set())
                declared_outcomes = set(s_conf.get(allowed_outcome_field, [])) if allowed_outcome_field else set()
                if declared_outcomes != expected_outcomes:
                    errors.append(f"Skill {s_name} outcomes mismatch: declared {sorted(declared_outcomes)} expected {sorted(expected_outcomes)}")
                for cond in s_conf.get("may_emit_delivery_conditions", []):
                    if cond not in pipeline_conditions:
                        errors.append(f"Skill {s_name} emits unregistered pipeline condition: {cond}")
                for kind in s_conf.get("may_emit_runtime_event_kinds", []):
                    if kind not in runtime_event_kinds:
                        errors.append(f"Skill {s_name} emits unregistered runtime event kind: {kind}")
                declared_kinds = set(s_conf.get("may_emit_runtime_event_kinds", []))
                if declared_kinds and s_name not in owner_rules:
                    errors.append(f"Skill {s_name} declares runtime event kind(s) but has no runtime-event owner rule")
                if s_name in owner_rules:
                    expected_kinds = set(owner_rules[s_name].get("may_emit", []))
                    forbidden_kinds = set(owner_rules[s_name].get("must_not_emit", []))
                    if declared_kinds != expected_kinds:
                        errors.append(f"Skill {s_name} runtime event kind mismatch: declared {sorted(declared_kinds)} expected {sorted(expected_kinds)}")
                    if declared_kinds & forbidden_kinds:
                        errors.append(f"Skill {s_name} declares forbidden runtime event kind(s): {sorted(declared_kinds & forbidden_kinds)}")
                # Verify SKILL.md Emit subset of phase-contracts.json outcomes
                skill_md_path = BEO_ROOT / s_name / "SKILL.md"
                if skill_md_path.exists():
                    skill_md_content = skill_md_path.read_text(encoding="utf-8")
                    emit_section = re.search(r"## Emit\s*(.*?)(?=\n##|$)", skill_md_content, re.DOTALL)
                    if emit_section:
                        emitted_from_card = set()
                        for line in emit_section.group(1).splitlines():
                            stripped = line.strip()
                            if not stripped.startswith("-"):
                                continue
                            match = re.match(r"-\s+`?([a-zA-Z_][a-zA-Z0-9_]*)`?(?:\s|$|->)", stripped)
                            if match:
                                emitted_from_card.add(match.group(1))
                        allowed_emits = set(s_conf.get(allowed_outcome_field, [])) if allowed_outcome_field else set()
                        extra_card_emits = emitted_from_card - allowed_emits
                        if extra_card_emits:
                            errors.append(f"Skill card {s_name}/SKILL.md emits unregistered condition(s) not allowed in phase-contracts.json: {sorted(extra_card_emits)}")

        except Exception as exc:
            errors.append(f"Failed to perform consistency validation on JSON registries: {exc}")


    # 4. Check legacy references and local Markdown links
    forbidden_tokens = [
        "ticket-plan" + ".schema.json",
        "forbidden_state_fields",
        "_forbidden_ticket_fields",
        "expires_at",
        "status == \"expired\"",
        "release_reason\": \"expired\"",
        '"abandon"',
    ]
    for p in BEO_ROOT.rglob("*"):
        if p.is_file() and p.suffix in [".md", ".json", ".py"]:
            if p.name == "check_skill_bundle.py":
                continue
            try:
                text = p.read_text(encoding="utf-8")
            except Exception:
                continue
            for token in forbidden_tokens:
                if token in text:
                    errors.append(f"Legacy token {token!r} found in file: {p.relative_to(BEO_ROOT)}")
            if p.suffix == ".md" and p.is_relative_to(REF_DIR):
                for ref in _path_like_refs(text):
                    _check_ref_exists(errors, p, ref)

    # Print results
    if errors:
        print("BEO Skill Bundle Integrity Verification: FAILED")
        for err in errors:
            print(f"- {err}")
        return 1
    else:
        print("BEO Skill Bundle Integrity Verification: SUCCESS")
        return 0


if __name__ == "__main__":
    sys.exit(run_checks())
