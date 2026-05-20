---
name: beo-plan
description: Mandatory first step for any Beads-anchored development. Locks the smallest safe interpretation of a Beads issue, decomposes broad work, or defines executable scope.
---

# beo-plan

Refs: `beo-reference -> references/kernel.md`, `beo-reference -> references/ticket.md`, `beo-reference -> references/modes.md`.

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
- `abandoned` -> `beo-review`

## Method

1. Lock smallest safe interpretation. For low-risk repository edits, use the **6-step Quick Path** (see `beo-reference -> references/lifecycle-events.md`) and write a minimal `TICKET.md`.
2. Use `bv` only for orientation. Append `triage_records[]` only if `bv` materially affects selection or decomposition.
3. If not atomic: create children via `br create`, add dependencies, comment parent, then exit `decomposition_recorded`.
4. If atomic: write ticket with request, done, gates, allow/forbid paths, generated outputs, verification, and acceptance.
5. Select quick, standard, or strict mode per `beo-reference -> references/modes.md`.
6. Run `beo_check.py --check validate --issue <issue-id>` as a readiness check before handoff.

