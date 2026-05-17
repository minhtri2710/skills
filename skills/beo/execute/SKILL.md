---
name: beo-execute
description: Executes an approved BEO plan by mutating only approved files and recording evidence.
---

# beo-execute

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

## Decision

Deliver exactly one approved execution set.

## Enter

- `PASS_EXECUTE`, fresh complete approval envelope, and selected execution set exist.

## Owns

- Mutation inside the selected approved execution set.
- Execution evidence.

## Writes

- Declared product files and generated outputs in the selected set.
- Compact execution fields or full `TRACKER.json`.
- Legal transition metadata, including temporary-owner return provenance when routing to `beo-debug`.

## Stops

- Fresh approval check is missing, incomplete, stale, invalid, contradictory, or unavailable.
- Mutation is outside the selected approved set.
- Blocker root cause is unproven.
- Repair requires scope change.
- Owner/feature identity is unsafe.

## Exits

- `execution_ready_for_review` -> `beo-review`
- `blocker_found` -> `beo-debug`
- `approval_stale_or_invalid` -> `beo-validate`
- `bounded_plan_repair_needed` -> `beo-plan`
- `scope_delta_required` -> `beo-plan`
- `user_blocker` -> `user`
- `user_abandoned` -> `done`
- `owner_feature_identity_unsafe` -> `beo-route`

## Method

1. Read the approval block and selected execution set.
2. Run fresh `beo_approval_check` for the current execution attempt.
3. Confirm live helper output reports `approval_envelope_status: complete`.
4. Apply only selected approved changes inside declared, non-forbidden paths.
5. Record pre-execution integrity, changed files, verification evidence, blocker status, and review-ready handoff.
6. When routing to `beo-debug`, write transition provenance with `return_to_caller`.
7. Hand off with exactly one legal condition and transition provenance when applicable.
