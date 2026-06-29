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
5. Edit only affected BEO control-plane files.
6. Keep the four-phase loop simple: plan, validate, execute, review.
7. Run only targeted validation for changed registry, schema, script, or skill-card artifacts when such validation exists; do not invent broad delivery checks.

## Write

- BEO doctrine, registry, schema, template, helper script, skill-card, or ADR changes within scope
- `.beads/artifacts/<issue-id>/harness-proposal.json` status updates (applied/declined)
- User-review notes when the requested maintenance is ambiguous or risky

## Emit

- `skill_authored_or_updated` -> caller (resolves to the originating skill or user)
- `reference_or_registry_updated` -> caller
- `no_change_needed` -> caller
- `user_review_needed` -> user

Non-normal `runtime-events.jsonl` events (advisory, optional): `score` (when `beo_score_trace.py` or `beo_score_context.py` is invoked for advisory scoring). beo-author may invoke a scorer and re-emit under its own name (forward-compat slot).

## Never

- See `beo-reference -> registry/phase-contracts.json` `must_not[]`; audit C8 enforces drift.
- Do not mutate product delivery scope.
- Do not grant `PASS_EXECUTE`.
- Do not execute or review product tickets.
- Do not close Beads delivery issues.
