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

1. Run semantic memory recall via `beo_recall.py --issue <issue-id>` (powered by `qmd` vector search) to retrieve prior learnings.
2. Read `.beads/artifacts/<issue-id>/RECALL_SUMMARY.md` to prevent recurring mistakes in plan design.
3. Claims & Intake: Claim issue atomically (`br update --claim`) and lock requirements. For low-risk edits, follow the 6-Step Compact Protocol.
4. Triage & Graph Insights: Run `bv` robot tools (`--robot-triage`, `--robot-plan`, `--robot-insights`) to map parallel tracks and resolve cycle bottlenecks.
5. If non-atomic: Decompose via `br create`, add dependency edges (`br dep add`), and exit `decomposition_recorded`.
6. If atomic: Draft `TICKET.md` specifying explicit file boundaries (`allow`/`forbid`), verification contracts, and safety mode (quick/standard/strict).
7. Pre-validate: Run `beo_check.py --check validate --issue <issue-id>` to ensure plan readiness.


