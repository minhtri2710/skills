---
name: beo-validate
description: Decides whether the exact BEO plan is ready and approved for execution.
---

# beo-validate

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

## Decision

Atomically decide execution readiness and bind execution authority.

## Enter

- Requirements and plan are ready for approval evaluation.

## Owns

- Readiness/refusal.
- Selected execution set.
- Execution mode.
- Approval ref and integrity object.

## Writes

- Compact validation fields or full Approval section only.
- Legal transition metadata.

## Stops

- Approval inputs are missing, stale, invalid, contradictory, or unavailable.
- Recorded Human Gate status is unresolved, missing, stale, or contradictory.
- Required user input for a Human Gate is absent.
- Owner/feature identity is unsafe.

## Exits

- `PASS_EXECUTE` -> `beo-execute`
- `FAIL_PLAN` -> `beo-plan`
- `FAIL_EXPLORE` -> `beo-explore` for missing, stale, contradictory, or unresolved recorded Human Gate status
- `BLOCK_USER` -> `user` only when required user input is absent
- `user_abandoned` -> `done`
- `FAIL_STATE` -> `beo-route`

## Method

1. Run fresh `beo_approval_check.py --check validate` for the current artifacts.
2. Evaluate the approval projection, Human Gate status, and scope binding from current artifacts and registries.
3. Emit `approval_ref` only for valid `PASS_EXECUTE`.
4. Record integrity.
5. Hand off with exactly one legal condition and transition provenance when applicable.
