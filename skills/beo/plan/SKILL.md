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

1. Run `python3 skills/beo/reference/scripts/beo_recall.py --issue <issue-id>` to semantically retrieve prior learning cases, mistakes, and success patterns before planning.
2. Read `.beads/artifacts/<issue-id>/RECALL_SUMMARY.md` and explicitly design the plan to prevent recurring mistakes.
3. Lock requirements: verify bead with `br show`, claim with `br update --claim`, then lock request/done/gates as the smallest safe interpretation. For low-risk repository edits, use the **6-step Quick Path** (see `beo-reference -> references/lifecycle.md`) and write a minimal `TICKET.md`.
4. Formulate execution tracks dynamically: execute `bv --robot-triage`, `bv --robot-plan`, and `bv --robot-insights` to verify priority scores, parallel execution tracks, and graph health. If cycles are detected, prioritize cycle-break operations. Record these triage insights in the ticket's `triage_records`.
5. If not atomic: create children via `br create`, add dependencies, comment parent, then exit `decomposition_recorded`.
6. If atomic: write ticket with request, done, gates, allow/forbid paths, generated outputs, verification, and acceptance.
7. Select quick, standard, or strict mode per `beo-reference -> references/safety.md`.
8. Run `beo_check.py --check validate --issue <issue-id>` as a readiness check before handoff.

