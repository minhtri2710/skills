---
name: beo-plan
description: Mandatory first step for any Beads-anchored development. Locks the smallest safe interpretation of a Beads issue, decomposes broad work, or defines executable scope.
---

# beo-plan

Refs: `beo-reference -> references/kernel.md`, `registry/ticket-schema.json`, `beo-reference -> references/safety.md`, `beo-reference -> references/lifecycle.md`.

## Decision

Lock the smallest safe interpretation of a Beads issue; decompose broad work or define atomic executable scope.

## Enter

- Beads issue selected; `br show <issue-id> --json` succeeds.
- Issue needs intake, decomposition, or atomic scope definition.

## Owns

- Intake: `request`, `done`, Human Gates, assumptions, non-goals, constraints.
- Plan: decomposition, scope, acceptance, atomicity, mode, verification, outputs, risk/rollback.

## Stops

- Requirements missing/contradictory or Human Gate blocks scope selection.
- Selected bead is broad and cannot be safely decomposed.
- Atomic work cannot be stated as one executable unit.

## Exits

- `plan_complete` -> `beo-validate`
- `decomposition_recorded` -> `parent_waits_children`
- `requirements_missing` -> `user`
- `human_gate_blocks` -> `user`
- `abandoned` -> `beo-review`

## Method

1. Recall: Run `beo_recall.py --issue <issue-id>` and read `.beads/artifacts/<issue-id>/RECALL_SUMMARY.md` for advisory lessons.
2. Claim & intake: Use `br show <issue-id> --json`, then claim with `br update --claim` before ticket writes.
3. Triage when needed: Use `bv --robot-triage`, `bv --robot-plan`, or `bv --robot-insights` only for backlog shape, parallel tracks, bottlenecks, or cycles.
4. If non-atomic: Decompose with `br create`, add edges with `br dep add`, comment on the parent, and exit `decomposition_recorded`.
5. If atomic: Draft `TICKET.md` with explicit `allow`/`forbid` files, verification contract, safety mode, assumptions, non-goals, and rollback/repair path.
6. Pre-validate: Run `beo_check.py --check validate --issue <issue-id>` to ensure plan readiness.


