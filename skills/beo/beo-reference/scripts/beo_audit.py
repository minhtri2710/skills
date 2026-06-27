#!/usr/bin/env python3
"""BEO drift audit helper (advisory, read-only).

Checks: C1 transition coverage, C2 reference existence, C3 must_not
violations (Write section), C4 runtime-event kind consistency, C5 manifest
consistency (--check-manifest only), C6 harness proposal target scope, C7
actor consistency, C8 must_not Never-section coverage, C9 stale learning
evidence_refs (advisory, opt-in via BEO_OBSIDIAN_VAULT). Emits markdown or
JSON; never writes.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

HELPER_VERSION = "beo-audit/v1"
SKILL_NAMES = ["beo-plan", "beo-validate", "beo-execute", "beo-review", "beo-debug", "beo-learn", "beo-author", "beo-climate", "beo-setup", "beo-reference"]
# Helper actors that emit runtime-events.jsonl entries but are not BEO skills.
# These are scripts in beo-reference/scripts/ that perform advisory or
# verification work and need a stable actor name in owner_rules. They are
# distinct from SKILL_NAMES: helpers never own a delivery phase, they only
# append events under their own name. C4 uses (SKILL_NAMES | HELPER_ACTORS)
# as the known-actor set.
HELPER_ACTORS = ["beo-verify", "beo-score-trace", "beo-score-context", "beo-audit"]
KNOWN_ACTORS = frozenset(SKILL_NAMES) | frozenset(HELPER_ACTORS)
SEVERITY_CRITICAL, SEVERITY_WARNING, SEVERITY_INFO = "critical", "warning", "info"
SEVERITIES = (SEVERITY_CRITICAL, SEVERITY_WARNING, SEVERITY_INFO)

# Regex to extract check IDs from Finding("CN", ...) calls in this source file.
_CHECK_ID_RE = re.compile(r'Finding\("(C\d+)"')


def get_check_ids() -> frozenset[str]:
    """Return all check IDs used by Finding() calls in this module.

    Scans the source of this file so adding a new check_* function with
    a Finding("CN", ...) call automatically includes its ID without
    manual registration. Returns a frozenset of check ID strings."""
    try:
        path = Path(__file__).resolve()
        source = path.read_text(encoding="utf-8")
    except Exception:
        return frozenset()
    return frozenset(_CHECK_ID_RE.findall(source))


@dataclass(frozen=True)
class Finding:
    check_id: str
    severity: str
    message: str

    def to_row(self) -> str:
        return f"- [{self.check_id}] {self.message}"


def _ref_root(root: Path) -> Path:
    return root / "skills" / "beo" / "beo-reference"


def load_skill_cards(root: Path) -> dict[str, str]:
    """Return mapping of skill_name -> SKILL.md file content."""
    root = Path(root)
    beo_root = root / "skills" / "beo"
    out: dict[str, str] = {}
    for name in SKILL_NAMES:
        path = beo_root / name / "SKILL.md"
        if path.exists():
            out[name] = path.read_text(encoding="utf-8")
    return out


def load_json_registry(root: Path, registry_name: str) -> dict[str, Any]:
    """Load a JSON registry from beo-reference/registry."""
    root = Path(root)
    path = _ref_root(root) / "registry" / registry_name
    return json.loads(path.read_text(encoding="utf-8"))


def _section_body(text: str, header: str) -> str:
    """Return the body of a `## Header` section up to the next `##` or end."""
    pattern = re.escape(header) + r"\s*(.*?)(?=\n## |\Z)"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(1) if match else ""


def extract_emit_identifiers(text: str) -> set[str]:
    """Identifiers (condition_ids) mentioned in a skill card's Emit section."""
    body = _section_body(text, "## Emit")
    found: set[str] = set()
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("-"):
            continue
        payload = stripped.lstrip("-").strip()
        match = re.match(r"`?([a-zA-Z_][a-zA-Z0-9_]*)`?", payload)
        if not match:
            continue
        ident = match.group(1)
        if ident.lower() in {"non-normal", "the", "a", "an"}:
            continue
        found.add(ident)
    return found


def extract_write_bullets(text: str) -> list[str]:
    """Lowercased bullet text from the Write section."""
    body = _section_body(text, "## Write")
    return [
        line.strip().lstrip("-").strip().lower()
        for line in body.splitlines()
        if line.strip().startswith("-")
    ]


def extract_read_refs(text: str) -> list[str]:
    """Reference strings mentioned in the Read section."""
    body = _section_body(text, "## Read")
    refs: list[str] = [
        f"beo-reference -> {m}" for m in re.findall(r"beo-reference\s*->\s*`?([^\s`>]+)", body)
    ]
    for match in re.findall(r"`([^`]+)`", body):
        if "/" in match or match.endswith((".md", ".json", ".py", ".yaml")):
            refs.append(match)
    return refs


def _is_pseudo_ref(ref: str) -> bool:
    """True when a ref is a command, placeholder, glob, or known artifact name."""
    if ref.startswith(("http://", "https://", "br ", "bv ", "file://")):
        return True
    if ref.startswith(("br show", "br ready", "br close", "br update", "br create", "br label")):
        return True
    if "<" in ref or "{" in ref or ref.startswith("`") or ref.endswith("`"):
        return True
    if any(char in ref for char in "*?["):  # glob patterns
        return True
    if ref.startswith(("beo-", "br-", "bv-")):  # skill name prefix
        return True
    artifact_names = {
        "state.json", "TICKET.json", "PLAN.md", "AGENTS.md", "AGENTS.template.md",
        "runtime-events.jsonl", "harness-proposal.json", "beo-reservations.jsonl",
        "CONTEXT_RULES.md", "user-handoff.md", "README.md",
    }
    return ref in artifact_names


def _looks_like_repo_path(ref: str) -> bool:
    """True when a ref looks like a real repo-relative path.

    Requires a path separator or a known subdir prefix. Bare basenames
    are too ambiguous to resolve. Long inline strings (likely code-fence
    content) are excluded.
    """
    if len(ref) > 120 or "\n" in ref:
        return False
    if "/" in ref:
        return True
    for prefix in ("references/", "registry/", "scripts/", "templates/", "examples/", "skills/beo/", ".beads/", "docs/"):
        if ref.startswith(prefix):
            return True
    return False


def resolve_reference(ref: str, source: Path, root: Path) -> Path | None:
    """Resolve a reference string to an absolute Path, or None if it is pseudo.

    source is the markdown file the reference came from (for context).
    """
    if " -> " in ref:
        skill_name, path_part = ref.split(" -> ", 1)
        if skill_name == "beo-reference":
            path_part = path_part.split("#", 1)[0]
            if path_part:
                return _ref_root(root) / path_part
            return None
        return None
    if _is_pseudo_ref(ref):
        return None
    ref = ref.split("#", 1)[0]
    if not ref:
        return None
    if ref.startswith("skills/beo/"):
        return (root / ref).resolve()
    if source.is_relative_to(_ref_root(root)):
        return (_ref_root(root) / ref).resolve()
    return (source.parent / ref).resolve()


def extract_prose_refs(text: str) -> list[str]:
    """Backtick-quoted and markdown-link path refs that look like real paths.

    Bare basenames without a path separator are filtered out — they are
    too ambiguous to resolve against the repo. Inline backticks only;
    code-fence content (multi-line blocks) is not a ref.
    """
    refs: list[str] = []
    refs.extend(m for m in re.findall(r"`([^`\n]+)`", text) if _looks_like_repo_path(m))
    refs.extend(m for m in re.findall(r"\[[^\]\n]+\]\(([^)\n]+)\)", text) if _looks_like_repo_path(m))
    return refs


def _pipeline_transition_iter(pipeline: dict[str, Any]) -> list[tuple[str, str, str]]:
    """[(section, from, condition_id), ...] for every transition in the pipeline."""
    out: list[tuple[str, str, str]] = []
    sections: list[tuple[str, list[dict[str, Any]]]] = [("pipeline", pipeline.get("transitions", []))]
    for name, payload in pipeline.get("support_subroutines", {}).items():
        sections.append((name, payload.get("transitions", [])))
    for name, payload in pipeline.get("maintenance_skills", {}).items():
        if isinstance(payload, dict):
            sections.append((name, payload.get("transitions", [])))
    for section, transitions in sections:
        for transition in transitions:
            out.append((section, transition.get("from", "?"), transition.get("condition_id", "?")))
    return out


def check_transition_coverage(
    pipeline: dict[str, Any],
    emits_by_skill: dict[str, set[str]],
) -> list[Finding]:
    findings: list[Finding] = []
    all_emits: set[str] = set().union(*emits_by_skill.values())
    for section, src, condition_id in _pipeline_transition_iter(pipeline):
        if condition_id == "?":
            findings.append(Finding("C1", SEVERITY_WARNING, f"transition missing condition_id in {section} (from={src})"))
            continue
        if condition_id not in all_emits:
            findings.append(Finding("C1", SEVERITY_CRITICAL, f"pipeline condition '{condition_id}' (from={src}, section={section}) is not mentioned in any skill card Emit section"))
    return findings


# Runtime artifact directories that are created at delivery time, not in
# the source repo. Reporting them as missing in C2 is noise that
# desensitizes operators to real findings. C2 skips any ref whose path
# portion starts with one of these prefixes (e.g., `.beads/...`).
RUNTIME_PATH_PREFIXES = (".beads",)


def _is_runtime_ref(ref: str) -> bool:
    """True if a ref points to a known runtime artifact directory.

    Accepts both bare refs (`.beads/foo`) and the `beo-reference -> .beads/foo`
    form used in skill-card Read sections. Only the path portion after
    `->` (if present) is checked, so a doc that legitimately references
    `.beads/...` as a runtime path is filtered, not the path it describes.
    """
    path = ref.split(" -> ", 1)[-1].strip()
    return any(path.startswith(prefix) for prefix in RUNTIME_PATH_PREFIXES)


def _is_runtime_path(target: Path, root: Path) -> bool:
    """True if a missing path is under a known runtime artifact directory.

    Defense-in-depth for refs that resolve under the repo root via the
    `skills/beo/` prefix (e.g., a future harness that legitimately puts
    a runtime artifact under that tree). Primary filtering happens in
    _is_runtime_ref at the ref-string level.
    """
    try:
        rel = target.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return bool(rel.parts) and rel.parts[0] in RUNTIME_PATH_PREFIXES


def check_reference_existence(root: Path, skill_cards: dict[str, str]) -> list[Finding]:
    findings: list[Finding] = []
    beo_root = root / "skills" / "beo"
    for skill_name, content in skill_cards.items():
        skill_path = beo_root / skill_name / "SKILL.md"
        for ref in extract_read_refs(content):
            if _is_runtime_ref(ref):
                continue
            target = resolve_reference(ref, skill_path, root)
            if not target or target.exists() or _is_runtime_path(target, root):
                continue
            findings.append(Finding("C2", SEVERITY_WARNING, f"{skill_name}/SKILL.md references missing file: {ref}"))
    # Reference prose — skip command-manifest.md since C5 covers it.
    ref_dir = _ref_root(root) / "references"
    if not ref_dir.exists():
        return findings
    for prose_path in sorted(ref_dir.glob("*.md")):
        if prose_path.name == "command-manifest.md":
            continue
        for ref in extract_prose_refs(prose_path.read_text(encoding="utf-8")):
            if _is_runtime_ref(ref):
                continue
            target = resolve_reference(ref, prose_path, root)
            if not target or target.exists() or _is_runtime_path(target, root):
                continue
            findings.append(Finding("C2", SEVERITY_INFO, f"references/{prose_path.name} mentions missing file: {ref}"))
    return findings


# Approximate must_not -> Write-section-keyword mapping. If any of the
# pipe-separated keywords appears in a skill's Write bullets, report
# a violation.
_MUST_NOT_KEYWORDS: dict[str, str] = {
    "mutate_product_files": "product files|mutate product",
    "mutate_product_delivery_scope": "mutate product delivery scope|product delivery scope",
    "mutate_outside_approved_scope": "outside approved scope|outside of approved scope",
    "mutate_delivery_state": "state.json|delivery state",
    "grant_PASS_EXECUTE": "pass_execute",
    "close": "br close|close in br",
    "close_non_accepted_work": "close non-accepted",
    "close_delivery_issue": "close the issue|close in br",
    "review": "perform manual review|do not review|do not perform review",
    "approve": "do not approve|approval.status",
    "validate": "do not validate",
    "execute_product_ticket": "do not execute",
    "review_product_ticket": "do not review",
    "act_as_delivery_phase_owner": "delivery phase owner",
    "alter_review_verdict": "review.verdict|alter review verdict",
    "modify_skill_cards_or_registries_directly": "skill cards or registries|modify skill cards",
    "make_qmd_or_obsidian_authoritative": "qmd or obsidian|obsidian authoritative",
    "refresh_or_reindex_qmd": "reindex qmd|refresh qmd",
    "mutate_registries": "registries",
    "mutate_Beads_state": "beads state|beads lifecycle",
    "issue_review_verdicts": "issue review verdicts|verdict_accept",
    "claim_issues": "claim the issue|claim issues",
    "mutate_qmd_indexes": "qmd index|qmd indexes",
    "mutate_BEO_artifacts": "beo artifacts|beo control plane",
    "mutate_memory": "memory note|obsidian|qmd index",
    "store_secrets": "secrets|credentials",
    "repair_code": "repair code|fix the bug",
    "patch_ticket_plan": "patch_ticket_plan|ticket plan",
    "emit_learning_candidate": "emit learning_candidate",
    "emit_multiple_review_routes": "emit more than one review route",
}


def check_must_not_violations(
    phase_contracts: dict[str, Any],
    skill_cards: dict[str, str],
) -> list[Finding]:
    findings: list[Finding] = []
    for skill_name, contract in phase_contracts.get("skills", {}).items():
        must_not_list = contract.get("must_not", []) or []
        write_blob = "\n".join(extract_write_bullets(skill_cards.get(skill_name, "")))
        for ban in must_not_list:
            keywords = _MUST_NOT_KEYWORDS.get(ban, ban.replace("_", " ").lower())
            for keyword in keywords.split("|"):
                if keyword and keyword in write_blob:
                    findings.append(Finding(
                        "C3",
                        SEVERITY_CRITICAL,
                        f"skill card {skill_name}/SKILL.md Write section mentions banned authority '{ban}' (matched '{keyword}')",
                    ))
                    break
    return findings


def check_must_not_coverage(
    phase_contracts: dict[str, Any],
    skill_cards: dict[str, str],
) -> list[Finding]:
    """C8: every registry must_not token must be mirrored in the skill Never section.

    Catches drift where phase-contracts.json adds a must_not constraint
    that the skill card's Never prose does not reflect. Complements C3,
    which checks the Write section for banned authorities. Direction:
    each registry token -> at least one of its significant words appears
    in the skill's ## Never body (prose only; the "- Binding:" cite line
    is excluded so its vocabulary can't mask drift). Words of 3 chars or
    fewer (connectives like 'and', 'not', 'the') are dropped to avoid
    loose matches; a token with no significant words (e.g. all-≤3-char)
    cannot be verified by stem matching and is flagged as unverifiable.
    Matching is word-boundary anchored so 'store' in 'restore' does not
    cover 'store_secrets'. Missing coverage is a drift warning.
    """
    findings: list[Finding] = []
    for skill_name, contract in phase_contracts.get("skills", {}).items():
        must_not_list = contract.get("must_not", []) or []
        never_body = _section_body(skill_cards.get(skill_name, ""), "## Never").lower()
        # Drop the canonical-source cite line ("- Binding: ...") so its own
        # vocabulary (canonical, phase, audit, prose, ...) cannot falsely
        # satisfy a token's stem coverage and mask real drift.
        never_body = "\n".join(
            ln for ln in never_body.splitlines()
            if not ln.strip().startswith("- binding:")
        )
        for ban in must_not_list:
            stems = [w for w in ban.lower().split("_") if len(w) > 3]
            # Word-boundary anchored so 'store' in 'restore' or 'approve' in
            # 'approved' does not falsely cover an unrelated token.
            covered = bool(stems) and any(
                re.search(r"\b" + re.escape(stem) + r"\b", never_body)
                for stem in stems
            )
            if not covered:
                note = (
                    "(no significant stem words; unverifiable)" if not stems
                    else "(phase-contracts.json drift risk)"
                )
                findings.append(Finding(
                    "C8",
                    SEVERITY_WARNING,
                    f"skill card {skill_name}/SKILL.md Never section does not mirror "
                    f"registry must_not token '{ban}' {note}",
                ))
    return findings


def check_runtime_event_kinds(events_schema: dict[str, Any], root: Path) -> list[Finding]:
    findings: list[Finding] = []
    metadata = events_schema.get("beo_contract_metadata", {})
    payload_contracts = metadata.get("payload_contracts", {}) or {}
    owner_rules = metadata.get("owner_rules", {}) or {}
    contract_kinds = set(payload_contracts.keys())
    emitted_kinds: set[str] = set().union(*(r.get("may_emit", []) for r in owner_rules.values()))
    findings.extend(
        Finding("C4", SEVERITY_CRITICAL, f"runtime-event kind '{k}' is defined in payload_contracts but no owner_rules.may_emit list claims it")
        for k in sorted(contract_kinds - emitted_kinds)
    )
    findings.extend(
        Finding("C4", SEVERITY_WARNING, f"runtime-event kind '{k}' appears in some owner_rules.may_emit but has no payload_contract entry")
        for k in sorted(emitted_kinds - contract_kinds)
    )
    # Python's json silently overwrites the first occurrence with the last.
    findings.extend(_find_duplicate_owner_rules(root))
    findings.extend(
        Finding("C4", SEVERITY_WARNING, f"owner_rules actor '{a}' is not a known BEO actor (skill or helper)")
        for a in sorted(set(owner_rules) - KNOWN_ACTORS)
    )
    return findings


def _find_duplicate_owner_rules(root: Path) -> list[Finding]:
    """Scan runtime-event.schema.json owner_rules for repeated keys.

    Uses a two-pass approach: first parse with a duplicate-detecting
    object_pairs_hook to find the owner_rules block, then count key
    occurrences. This is reliable across JSON formatting variations.
    """
    schema_path = _ref_root(root) / "registry" / "runtime-event.schema.json"
    if not schema_path.exists():
        return []

    duplicates: list[str] = []

    def _hook(pairs: list) -> Any:
        counts: dict[str, int] = {}
        keys_in_order: list[str] = []
        for key, _ in pairs:
            if isinstance(key, str):
                counts[key] = counts.get(key, 0) + 1
                if key not in keys_in_order:
                    keys_in_order.append(key)
        for key in keys_in_order:
            if counts[key] > 1 and key not in duplicates:
                duplicates.append(key)
        return dict(pairs)

    try:
        json.loads(schema_path.read_text(encoding="utf-8"), object_pairs_hook=_hook)
    except json.JSONDecodeError:
        return []
    return [
        Finding("C4", SEVERITY_WARNING, f"runtime-event.schema.json has duplicate key '{key}' (last entry wins)")
        for key in sorted(set(duplicates))
    ]


def _manifest_script_names(manifest_text: str) -> tuple[set[str], set[str]]:
    """Return (unplanned, planned) script basenames from the manifest tables.

    Accepts bare script names (beo_foo.py), scripts/ prefixed names
    (scripts/beo_foo.py), and full-path names (skills/beo/.../scripts/beo_foo.py).
    The scripts/ prefix is stripped before storing, so the stored name is
    always the bare basename for comparison with on-disk scripts.

    Planned entries are tracked separately so C5 can honour the
    documented contract: planned entries do not fail drift when the
    file is absent, but if a planned file later lands on disk, C5
    should flag that the manifest still labels it as planned.
    """
    unplanned: set[str] = set()
    planned: set[str] = set()
    for line in manifest_text.splitlines():
        if not line.startswith("|"):
            continue
        first = line.split("|", 2)[1].strip() if line.count("|") >= 2 else ""
        match = re.match(
            r"`?(?:skills/beo/[\w./-]+/scripts/|scripts/)?([A-Za-z0-9_]+\.py)`?(\s*\[planned\])?",
            first,
        )
        if not match:
            continue
        (planned if match.group(2) else unplanned).add(match.group(1))
    return unplanned, planned


def check_manifest_consistency(root: Path) -> list[Finding]:
    findings: list[Finding] = []
    manifest_path = _ref_root(root) / "references" / "command-manifest.md"
    if not manifest_path.exists():
        return [Finding("C5", SEVERITY_INFO, "command-manifest.md not found; skipping manifest check")]
    scripts_dir = _ref_root(root) / "scripts"
    if not scripts_dir.exists():
        return [Finding("C5", SEVERITY_WARNING, f"scripts directory missing: {scripts_dir}")]
    on_disk = {p.name for p in scripts_dir.glob("*.py")}
    unplanned, planned = _manifest_script_names(manifest_path.read_text(encoding="utf-8"))
    for script in sorted(on_disk - unplanned):
        label = "still marked [planned]" if script in planned else "missing from command-manifest.md"
        findings.append(Finding("C5", SEVERITY_WARNING, f"script '{script}' exists in scripts/ but is {label}"))
    for script in sorted((unplanned | planned) - on_disk):
        findings.append(Finding("C5", SEVERITY_INFO, f"command-manifest.md references '{script}' but no such script exists"))
    return findings


# C9: stale learning evidence_refs. Operates on the BEO Obsidian vault
# (BEO_OBSIDIAN_VAULT, default ~/second-brain). For each OKF v0.1 note
# in <vault>/beo-learnings/, parse frontmatter and verify that each
# evidence_refs entry still resolves. A stale ref points at a file that
# has moved, been renamed, or been deleted, and indicates the learning
# note needs to be refreshed (per /ce-compound-refresh semantics).
#
# C9 is opt-in: if no vault is configured or the beo-learnings directory
# is missing, the check returns no findings (silent no-op). C9 findings
# are always SEVERITY_WARNING and never auto-healed; refreshed learnings
# are a content decision, not a mechanical fix.
_FRONT_KV_RE = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*):\s*(.*)$")


def _parse_okf_frontmatter(content: str) -> dict[str, Any]:
    """Parse minimal YAML frontmatter (one level, OKF v0.1 shape).

    Deliberately narrow: only flat key:value and a single list-of-strings
    shape. evidence_refs and tags are common list fields; everything
    else is treated as a scalar string. Returns {} when no frontmatter
    is present or it cannot be parsed.
    """
    if not content.startswith("---\n"):
        return {}
    end = content.find("\n---\n", 4)
    if end < 0:
        return {}
    block = content[4:end]
    out: dict[str, Any] = {}
    pending_list: str | None = None
    for line in block.splitlines():
        if line.startswith("  - "):
            if pending_list:
                val = line[4:].strip().strip('"').strip("'")
                bucket = out.get(pending_list)
                if isinstance(bucket, list):
                    bucket.append(val)
            continue
        m = _FRONT_KV_RE.match(line)
        if not m:
            pending_list = None
            continue
        key, raw = m.group(1), m.group(2).strip()
        if raw == "" or raw == "|" or raw == ">":
            pending_list = key
            out[key] = []
        elif raw.startswith("[") and raw.endswith("]"):
            inner = raw[1:-1]
            items = [s.strip().strip('"').strip("'") for s in inner.split(",") if s.strip()]
            out[key] = items
            pending_list = None
        else:
            out[key] = raw.strip('"').strip("'")
            pending_list = None
    return out


def _resolve_learning_ref(ref: str, vault: Path, repo: Path) -> Path | None:
    """Resolve a learning evidence_ref to an existing path, or None.

    Strategies, in order:
      1. Absolute or ~-relative: expand and check.
      2. Relative: try vault-rooted first, then repo-rooted.
    """
    if ref.startswith("/") or ref.startswith("~"):
        try:
            p = Path(ref).expanduser().resolve()
        except OSError:
            return None
        return p if p.exists() else None
    for base in (vault, repo):
        try:
            candidate = (base / ref).resolve()
        except OSError:
            continue
        try:
            if candidate.exists():
                return candidate
        except OSError:
            continue
    return None


def check_stale_learning_evidence_refs(root: Path) -> list[Finding]:
    """C9: scan BEO learning notes for evidence_refs that no longer resolve.

    Source: <BEO_OBSIDIAN_VAULT>/beo-learnings/*.md (or ~/second-brain
    by default). For each note, parse OKF v0.1 frontmatter; for each
    evidence_refs entry, attempt to resolve. Findings are advisory;
    operators (or `beo-author` after triage) decide whether to refresh,
    supersede, or retire the note.
    """
    findings: list[Finding] = []
    raw_vault = os.environ.get("BEO_OBSIDIAN_VAULT")
    vault = Path(raw_vault).expanduser().resolve() if raw_vault else (Path.home() / "second-brain").resolve()
    learnings_dir = vault / "beo-learnings"
    if not learnings_dir.is_dir():
        return findings
    repo = Path(root).resolve()
    for note_path in sorted(learnings_dir.glob("*.md")):
        try:
            content = note_path.read_text(encoding="utf-8")
        except OSError:
            continue
        frontmatter = _parse_okf_frontmatter(content)
        evidence_refs = frontmatter.get("evidence_refs", [])
        if not isinstance(evidence_refs, list):
            continue
        for ref in evidence_refs:
            if not isinstance(ref, str) or not ref.strip():
                continue
            if _resolve_learning_ref(ref, vault, repo) is None:
                findings.append(Finding(
                    "C9",
                    SEVERITY_WARNING,
                    f"learning '{note_path.name}' has unresolvable evidence_ref: {ref}",
                ))
    return findings


def check_harness_proposal_targets(root: Path) -> list[Finding]:
    """Scan .beads/artifacts/*/harness-proposal.json for target scope violations.

    Per kernel §10, proposals must target paths under skills/beo/. This check
    (C6) scans all harness-proposal.json files found at delivery time and
    reports any whose target does not start with 'skills/beo/'.
    """
    findings: list[Finding] = []
    artifacts_dir = root / ".beads" / "artifacts"
    if not artifacts_dir.is_dir():
        return findings
    for proposal_path in sorted(artifacts_dir.rglob("harness-proposal.json")):
        try:
            data = json.loads(proposal_path.read_text(encoding="utf-8"))
        except Exception as exc:
            findings.append(Finding(
                "C6", SEVERITY_WARNING,
                f"{proposal_path.relative_to(root)}: unreadable or invalid JSON: {exc}",
            ))
            continue
        if not isinstance(data, dict):
            findings.append(Finding(
                "C6", SEVERITY_WARNING,
                f"{proposal_path.relative_to(root)}: not a mapping",
            ))
            continue
        target = data.get("target", "")
        if not isinstance(target, str) or not target.startswith("skills/beo/"):
            findings.append(Finding(
                "C6", SEVERITY_CRITICAL,
                f"{proposal_path.relative_to(root)}: target '{target}' does not start with "
                f"'skills/beo/' (kernel §10 violation)",
            ))
    return findings


def check_actor_consistency(events_schema: dict[str, Any], root: Path) -> list[Finding]:
    """C7: every script that calls append_event must use an actor in owner_rules.

    Scans scripts/ for patterns like `"actor": "beo-..."` that are passed to
    append_event. Confirms each actor exists in runtime-event.schema.json
    owner_rules.
    """
    findings: list[Finding] = []
    metadata = events_schema.get("beo_contract_metadata", {})
    owner_rules = metadata.get("owner_rules", {}) or {}
    known_actors = set(owner_rules.keys())

    scripts_dir = _ref_root(root) / "scripts"
    if not scripts_dir.is_dir():
        return findings

    for script_path in sorted(scripts_dir.glob("*.py")):
        if script_path.name == "beo_audit.py":
            continue  # self-check would match docstring examples
        text = script_path.read_text(encoding="utf-8")
        if "append_event" not in text:
            continue
        # Look for literal actor strings in the form "actor": "beo-..."
        for match in re.finditer(r'"actor"\s*:\s*"(beo-[^"]+)"', text):
            actor = match.group(1)
            if actor not in known_actors:
                findings.append(Finding(
                    "C7", SEVERITY_WARNING,
                    f"{script_path.name} uses append_event with actor '{actor}' "
                    f"which is not in runtime-event.schema.json owner_rules",
                ))
    return findings


def render_markdown_report(timestamp: str, findings: list[Finding], checks_run: list[str]) -> str:
    grouped: dict[str, list[Finding]] = {s: [] for s in SEVERITIES}
    for finding in findings:
        grouped.setdefault(finding.severity, []).append(finding)
    headings = {SEVERITY_CRITICAL: "Critical", SEVERITY_WARNING: "Warnings", SEVERITY_INFO: "Info"}
    lines: list[str] = [
        f"# BEO Audit Report — {timestamp}", "",
        f"helper: {HELPER_VERSION}", f"checks run: {', '.join(checks_run)}", "",
        "## Summary",
        f"- critical: {len(grouped[SEVERITY_CRITICAL])}",
        f"- warnings: {len(grouped[SEVERITY_WARNING])}",
        f"- info: {len(grouped[SEVERITY_INFO])}", "",
        "## Drift Findings",
    ]
    for severity in SEVERITIES:
        bucket = grouped[severity]
        if not bucket:
            continue
        lines.append(f"### {headings[severity]}")
        lines.extend(f.to_row() for f in sorted(bucket, key=lambda f: (f.check_id, f.message)))
        lines.append("")
    if not any(grouped.values()):
        lines.append("_No drift findings. BEO control plane is consistent._")
    return "\n".join(lines)


def render_json_report(timestamp: str, findings: list[Finding], checks_run: list[str]) -> str:
    summary = {s: sum(1 for f in findings if f.severity == s) for s in SEVERITIES}
    return json.dumps({
        "helper_version": HELPER_VERSION,
        "generated_at": timestamp,
        "checks_run": checks_run,
        "summary": {"critical": summary[SEVERITY_CRITICAL], "warnings": summary[SEVERITY_WARNING], "info": summary[SEVERITY_INFO]},
        "findings": [{"check_id": f.check_id, "severity": f.severity, "message": f.message} for f in findings],
    }, indent=2, sort_keys=True)


def run_audit(root: Path, *, check_manifest: bool) -> tuple[list[Finding], list[str]]:
    root = Path(root)
    findings: list[Finding] = []
    checks_run: list[str] = []
    registries: dict[str, Any] = {}
    for name in ("pipeline.json", "phase-contracts.json", "runtime-event.schema.json"):
        try:
            registries[name] = load_json_registry(root, name)
        except Exception as exc:
            return [Finding("C0", SEVERITY_CRITICAL, f"failed to load {name}: {exc}")], ["C0"]
    skill_cards = load_skill_cards(root)
    emits_by_skill = {n: extract_emit_identifiers(c) for n, c in skill_cards.items()}
    plan = (
        ("C1: transition coverage", check_transition_coverage(registries["pipeline.json"], emits_by_skill)),
        ("C2: reference existence", check_reference_existence(root, skill_cards)),
        ("C3: must_not violations", check_must_not_violations(registries["phase-contracts.json"], skill_cards)),
        ("C4: runtime-event kind consistency", check_runtime_event_kinds(registries["runtime-event.schema.json"], root)),
        ("C6: harness proposal target scope", check_harness_proposal_targets(root)),
        ("C7: actor consistency", check_actor_consistency(registries["runtime-event.schema.json"], root)),
        ("C8: must_not coverage", check_must_not_coverage(registries["phase-contracts.json"], skill_cards)),
        ("C9: stale learning evidence_refs", check_stale_learning_evidence_refs(root)),
    )
    for label, result in plan:
        checks_run.append(label)
        findings.extend(result)
    if check_manifest:
        checks_run.append("C5: manifest consistency")
        findings.extend(check_manifest_consistency(root))
    return findings, checks_run


def main() -> int:
    parser = argparse.ArgumentParser(description="BEO control-plane drift audit (advisory, read-only)")
    parser.add_argument("--root", default=".", help="Repository root (default: cwd)")
    parser.add_argument("--check-manifest", action="store_true", help="Enable command-manifest consistency check")
    parser.add_argument("--json", action="store_true", help="Emit machine-readable JSON instead of markdown")
    args = parser.parse_args()
    from beo_io import now as _now
    findings, checks_run = run_audit(Path(args.root).resolve(), check_manifest=args.check_manifest)
    timestamp = _now()
    if args.json:
        sys.stdout.write(render_json_report(timestamp, findings, checks_run) + "\n")
    else:
        sys.stdout.write(render_markdown_report(timestamp, findings, checks_run))
    return 1 if any(f.severity == SEVERITY_CRITICAL for f in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
