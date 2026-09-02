---
name: beo-author
description: "Maintain BEO control-plane files: skill cards, references, registries, templates, scripts, and ADRs. Use when modifying BEO workflow rules or contracts. No product delivery authority."
---
# beo-author

## Rule ownership

Before changing any BEO rule, identify its canonical owner via `beo-reference -> references/doctrine-map.md`.

Do not duplicate a rule into multiple references. Non-owner files should cite the canonical owner.

When a repeated behavior becomes durable workflow doctrine, update the canonical reference, registry, script, skill card, or AGENTS template. Do not add ad-hoc rules elsewhere.

## Read

- The BEO maintenance request (or harness change proposal) and the affected BEO file(s)
- `.beads/artifacts/<issue-id>/harness-proposal.json` (when responding to `harness_change_needed`) and `beo-reference -> registry/harness-proposal.schema.json` (before validating)
- Narrow `beo-reference` docs/registries that own the affected rule; start with `beo-reference -> references/doctrine-map.md` when authority is unclear

## Do

1. Confirm the request is BEO control-plane maintenance, not product delivery.
2. Identify the canonical artifact that owns the rule.
3. For harness change proposals from delivery agents:
   - Read `.beads/artifacts/<issue-id>/harness-proposal.json` and validate against `beo-reference -> registry/harness-proposal.schema.json`.
   - Review the `proposed_diff` and `safety_note`. Confirm the change is safe, scoped to `skills/beo/`, and does not weaken safety invariants.
   - If approved: apply the change to the target file(s), update `harness-proposal.json` status to `applied`, emit `skill_authored_or_updated` or `reference_or_registry_updated` -> caller.
   - If declined: update status to `declined`, include rationale, emit `no_change_needed` -> caller.
   - If ambiguous or risky: route `user_review_needed` -> user.
4. For direct BEO maintenance requests, follow the normal procedure.
5. For maintenance scans, run `beo_audit.py --check-manifest --json` and triage each finding by `check_id`:
   - Apply mechanical fixes directly for C2 orphaned references and C4 stale schema fields.
   - Route every other finding, including C9 stale learning evidence_refs, to the user via `user_review_needed`.
   - A scan with no findings emits `no_change_needed`; a direct fix emits `reference_or_registry_updated`.
6. Edit only affected BEO control-plane files.
7. Keep the four-phase loop simple: plan, validate, execute, review.
8. Run only targeted validation for changed registry, schema, script, or skill-card artifacts when such validation exists; do not invent broad delivery checks.

## Write

- BEO doctrine, registry, schema, template, helper script, skill-card, or ADR changes within scope
- `.beads/artifacts/<issue-id>/harness-proposal.json` status updates (applied/declined)
- User-review notes when the requested maintenance is ambiguous or risky

## Emit

- `skill_authored_or_updated` -> caller (resolves to the originating skill or user)
- `reference_or_registry_updated` -> caller
- `no_change_needed` -> caller
- `user_review_needed` -> user

Non-normal `runtime-events.jsonl` events (advisory, optional): `score` (when `beo_score_trace.py` or `beo_score_context.py` is invoked for advisory scoring). beo-author may invoke a scorer and re-emit under its own name.

## C9: stale learning evidence_refs

`beo_audit.py` C9 scans `<BEO_OBSIDIAN_VAULT>/beo-learnings/*.md` (or `~/second-brain` by default) for OKF v0.1 notes whose `evidence_refs` entries no longer resolve. C9 is opt-in: it is a no-op when no vault is configured or `beo-learnings/` is missing.

- **Dual-root note:** evidence_refs often span two roots — the skills repo (`skills/...`) and a product repo (`.beads/...`, `src/...`). Run the audit with both: `beo_audit.py --root <skills-repo> --learning-repo <product-repo>` (the flag is repeatable). With only `--root`, product-rooted refs surface as false positives.

- **Source:** obsidian vault, not the BEO control plane. The check crosses scope boundaries on purpose: a learning note is durable memory of past work, and its evidence must point at something that still exists.
- **Severity:** always `warning`. Never critical, never auto-healed. A stale evidence_ref is a refresh signal, not a contract violation.
- **Resolution strategy:** try resolving each ref as (1) absolute or `~`-relative, (2) relative to the vault root, (3) relative to the repo root (`--root`), (4) relative to any extra root passed via `--learning-repo` (repeatable). The first hit wins; if none hit, the ref is stale.
- **Reference implementation:** `/ce-compound-refresh` (EveryInc/compound-engineering-plugin). The plugin reviews stale learnings against current code; C9 surfaces the candidates that need review.
- **Operator action:** route findings to the user via `user_review_needed` for refresh, supersede, or retire. Do NOT add C9 to any auto-heal allowlist; the decision to refresh a learning is content, not mechanics.

Many real-world C9 findings are "evidence moved" or "evidence is a narrative identifier, not a file path" (e.g. subagent ids, commit SHAs, issue titles). Triage accordingly: rename the ref, drop it, or note that it is a text label rather than a path.

## Never

- See `beo-reference -> registry/phase-contracts.json` `must_not[]`; audit C8 enforces drift.
- Do not mutate product delivery scope.
- Do not grant `PASS_EXECUTE`.
- Do not execute or review product tickets.
- Do not close Beads delivery issues.
