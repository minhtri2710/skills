---
name: beo-validate
description: Validate a planned atomic BEO ticket's scope, overlap safety, and prestate before code is changed. Always use this skill after TICKET.md is created, when a ticket is ready for approval, or when deciding if it is safe to begin coding. Trigger this whenever the user asks "can we execute?", "is this approved?", or "check my plan."
requires: br>=0.1.28
---
# beo-validate

## Use when

A plan-owned `TICKET.md` is ready and the next decision is whether execution may proceed.

## Read

- Claimed issue state from `br show <issue-id> --json`.
- `.beads/artifacts/<issue-id>/TICKET.md`.
- Existing `.beads/artifacts/<issue-id>/state.json` when present.
- `beo-reference` canonical contracts: `references/kernel.md`, `references/safety.md`, `registry/profiles.json`, `registry/ticket-schema.json`, `registry/approval-envelope.json`, `registry/pipeline.json`, and `registry/command-contracts.json`.
- Path reservation state only when the selected profile or overlap risk requires it.

## Do

1. Confirm issue identity, claim, atomicity, mode/profile requirements, and Human Gate status.
2. Check explicit file scope, protected paths, broad globs, generated outputs, overlap safety, and strict side-effect contracts.

### Quick Mode Validation Fast-Path
For Quick Mode tickets, validation skips reservation checks and side-effect contracts, but **must never skip active overlap analysis** which protects against parallel concurrency collisions.
3. Derive reservation requirements from canonical profile/risk policy; do not rely on caller intent alone.
4. Build approval projection and prestate evidence for the approved execution scope.
5. Run validation helpers as commands through `beo-reference` scripts.

## Write

- Validation-owned `state.json` fields: readiness, selected execution set, execution mode, approval reference, integrity evidence, approval projection, and prestate hashes.
- `PASS_EXECUTE` only when all validation checks pass and approval evidence records the repo HEAD freshness sentinel.
- Validation failure evidence when approval is refused, including `FAIL_PLAN` subreasons: `fail_atomicity`, `fail_scope`, `fail_profile`, `fail_human_gate`, and `fail_schema`.

## Emit

- `PASS_EXECUTE` -> stop and load `beo-execute` before mutation.
- `FAIL_PLAN` -> stop and load `beo-plan` for scope or ticket repair.
- `BLOCK_USER` -> stop for user-owned gate resolution.
- `abandoned` -> stop and load `beo-review`.

## Never

- Do not mutate product files or generated outputs (validation is a pure control-plane check; changing code now breaks prestate hashSentinels).
- Do not widen scope, rewrite acceptance, or patch the plan locally (if the plan is broken, refuse approval and route to FAIL_PLAN).
- Do not create review verdicts or close issues (review owns final closure verdicts).
- Do not treat `br`, `bv`, qmd, or memory output as approval.
- Do not load another BEO delivery owner in the same turn for the same issue after emitting; stop first.
