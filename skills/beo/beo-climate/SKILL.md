---
name: beo-climate
description: "Proactive BEO maintenance cadence. Runs periodic scans for doc-code consistency, tech debt, deprecated contracts, and consolidation opportunities. Advisory only — findings become Beads issues for triage."
---
# beo-climate

## Read

- All BEO skill cards (`beo-*/SKILL.md`) for doc-code consistency checks
- All BEO references (`beo-reference/references/*.md`)
- All BEO registries (`beo-reference/registry/*.json`)
- Update cadence config: `config.json`
- `beo-reference -> references/doctrine-map.md` for rule ownership

## Do

1. Scan skill cards against registries:
   - Every condition in `pipeline.json` transitions must appear in a skill card "Emit" section.
   - Every route class must have at least one condition emitting it.
   - Every skill card "Read" section must reference existing files.
2. Check doc-code consistency:
   - Registry schemas match their corresponding `references/*.md` documentation.
   - No orphaned references (files referenced in doctrine-map but missing).
   - No undocumented registries.
3. Identify consolidation opportunities:
   - Repeated patterns across skill cards that could be extracted.
   - Overlapping permissions in `phase-contracts.json`.
   - Deprecated conditions or routes no longer used.
4. Flag stale or dead contracts:
   - Registries referencing removed pipeline transitions.
   - Schema fields that are no longer written.
5. Report findings (or `climate_self_heal` candidates) to the user via the emit conditions below. beo-climate has no `br.*` write authority; the user (or `beo-author` for items in the auto-heal allowlist) is responsible for opening Beads issues from reported findings.

## Emit

- `climate_scan_complete` -> user (no findings, advisory)
- `climate_issues_found` -> user (findings that need human triage)
- `climate_self_heal` -> user (safe automated fix available; user decides whether to apply via `beo-author`)

## Write

- (read-only advisory; no writes)

## Config

Scan configuration lives in `config.json`:
- `cadence`: default schedule for background runs.
- `scan_scope`: which files to include/exclude.
- `auto_heal_allowlist`: safe fix types that `beo-climate` may auto-route to `beo-author`. Each item is an object with three required fields:
  - `id`: stable identifier for the allowlist entry (e.g., `missing_emit_condition_in_pipeline`).
  - `audit_check_id`: the `beo_audit.py` check_id that surfaces this finding (e.g., `C1`, `C2`, `C4`). This binds the climate scan to the audit's named checks; triage uses the `check_id` to route the finding to the matching fix-up path. `C4` (`stale_schema_field`) additionally covers duplicate `owner_rules` keys and unknown actors.
  - `summary`: human-readable description of what the allowlist entry covers.
  Items whose fix would change a safety invariant, add a skill, alter phase permissions, or modify a `kernel.md` rule must NOT be added — they always require human triage.

## Never

- See `beo-reference -> registry/phase-contracts.json` `must_not[]`; audit C8 enforces drift.
- Do not mutate delivery state or product files.
- Do not grant `PASS_EXECUTE`.
- Do not close delivery issues.
- Do not alter review verdicts.
- Do not modify skill cards or registries directly (route to `beo-author` instead).
- Do not auto-apply fixes outside the `auto_heal_allowlist`.

## C9: stale learning evidence_refs

`beo_audit.py` C9 scans `<BEO_OBSIDIAN_VAULT>/beo-learnings/*.md` (or `~/second-brain` by default) for OKF v0.1 notes whose `evidence_refs` entries no longer resolve. C9 is opt-in: it is a no-op when no vault is configured or `beo-learnings/` is missing.

- **Source:** obsidian vault, not the BEO control plane. The check crosses scope boundaries on purpose: a learning note is durable memory of past work, and its evidence must point at something that still exists.
- **Severity:** always `warning`. Never critical, never auto-healed. A stale evidence_ref is a refresh signal, not a contract violation.
- **Resolution strategy:** try resolving each ref as (1) absolute or `~`-relative, (2) relative to the vault root, (3) relative to the repo root. The first hit wins; if none hit, the ref is stale.
- **Reference implementation:** `/ce-compound-refresh` (EveryInc/compound-engineering-plugin). The plugin reviews stale learnings against current code; C9 surfaces the candidates that need review.
- **Operator action:** route findings to `beo-author` for refresh, supersede, or retire. Do NOT add C9 to `config.json auto_heal_allowlist`; the decision to refresh a learning is content, not mechanics.

Many real-world C9 findings are "evidence moved" or "evidence is a narrative identifier, not a file path" (e.g. subagent ids, commit SHAs, issue titles). Triage accordingly: rename the ref, drop it, or note that it is a text label rather than a path.

## Future metric sources (advisory, not yet wired)

Two external metric sources are not yet wired: `bv --robot-burndown <sprint>` (sprint drift, future C10) and `bv --robot-alerts --severity critical --format json` (stale issues, blocking cascades, priority mismatches). Both are read-only advisory, require `br init` and an active `.beads/` directory, and need phase-contracts.json updates via beo-author before adoption.
