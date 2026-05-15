---
name: beo-execute
description: |
  Delivers exactly one selected approved execution set. Use when PASS_EXECUTE exists with current approval, integrity evidence, resolved/not-applicable Human Gates, selected execution set, execution_mode normal, declared files, and verification contract. Must call beo_approval_check fresh before any mutation. Not for planning, approving, review verdicts, or unscoped mutation.
---

# beo-execute

## Purpose

Perform the approved mutation and record execution evidence.

## Decision Card

Decision: deliver exactly one selected approved execution set.

Can enter when:
- `PASS_EXECUTE`, current approval/integrity, resolved/not_applicable Human Gates, and selected execution set exist

Can write:
- declared product files/generated outputs and execution evidence

Must stop when:
- fresh `beo_approval_check` is missing or not complete, or mutation is outside the selected approved set

Exit summary (non-authoritative):
- `execution_ready_for_review` -> `beo-review`
- `blocker_found` -> `beo-debug`
- `approval_stale_or_invalid` -> `beo-validate`
- `bounded_plan_repair_needed` -> `beo-plan`
- `scope_delta_required` -> `beo-plan`
- `user_blocker` -> `user`
- `owner_feature_identity_unsafe` -> `beo-route`

Never:
- change approval, emit terminal verdicts, or mutate undeclared/forbidden paths

Reads:
- current artifacts, approval, artifacts, state, and pipeline

## Contract

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

Acts when:
- `PASS_EXECUTE`, current approval, integrity evidence, resolved/not-applicable Human Gates, and selected execution set exist

Owns:
- approved execution-set delivery inside declared scope

Writes:
- declared product files/generated outputs and execution evidence (`TICKET.md#Execution` or `TRACKER.json`)

Reads:
- current artifacts, `beo-reference -> references/approval.md`, `beo-reference -> references/artifacts.md`, `beo-reference -> references/state.md`, `beo-reference -> registry/pipeline.json`

Local stops:
- approval is missing, stale, invalid, contradictory, or unavailable
- fresh `beo_approval_check` output is missing or does not report `approval_envelope_status: complete`
- selected execution set does not cover the mutation
- blocker root cause is unproven
- repair requires scope change
- owner/feature identity is unsafe

Local forbids:
- approval changes
- terminal verdicts
- undeclared/forbidden path mutation
- unproven blocker fixes
- mutation outside the selected approved execution set
- relying only on artifact-recorded `integrity.status` as live authority

Exits:
- `execution_ready_for_review` -> `beo-review`
- `blocker_found` -> `beo-debug`
- `approval_stale_or_invalid` -> `beo-validate`
- `bounded_plan_repair_needed` -> `beo-plan`
- `scope_delta_required` -> `beo-plan`
- `user_blocker` -> `user`
- `owner_feature_identity_unsafe` -> `beo-route`

## Execution Loop

Before any mutation, run `beo_approval_check` for the current execution attempt. Only live helper output with `approval_envelope_status: complete` permits mutation.

Update only the selected approved execution set. If approval-bearing content changes, stop to `beo-validate`. If blocker root cause is unproven, stop to `beo-debug`. If repair requires scope change, stop to `beo-plan`.

Record `pre_execution_integrity_check` in execution evidence with helper name, evidence ref, and approval envelope status.

Repair and rollback execution are normal approved execution-set delivery with `kind: repair` or `kind: rollback`.
