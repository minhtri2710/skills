# Artifact Writing Guide

Write planning artifacts in this order and keep each artifact in its own role.

## 1. Write Order

Single-phase:
1. `discovery.md`
2. `approach.md`
3. `plan.md`
4. `phase-contract.md`
5. `story-map.md`
6. current-phase beads

Multi-phase:
1. `discovery.md`
2. `approach.md`
3. `plan.md`
4. `phase-plan.md`
5. multi-phase approval
6. `phase-contract.md` for the current phase
7. `story-map.md` for the current phase
8. current-phase beads

Artifact roles:

| Artifact | Owns |
| --- | --- |
| `discovery.md` | implementation landscape and findings |
| `approach.md` | chosen strategy, alternatives, risks, planning mode |
| `plan.md` | short human-readable plan summary |
| `phase-plan.md` | whole-feature sequencing for multi-phase work |
| `phase-contract.md` | current-phase contract only |
| `story-map.md` | current-phase story sequence only |

Do not use `phase-contract.md` as a whole-feature artifact.

## 2. `approach.md`

Write from `CONTEXT.md`, discovery, learnings, codebase constraints, and external findings.

It must answer:
- what the feature must make true
- what already exists
- what is missing or risky
- what path is recommended
- what alternatives were rejected
- whether the work is single-phase or multi-phase

If `approach.md` is weak, fix it before expanding `plan.md`.

## 3. `plan.md`

Write a short human-readable summary:
- feature goal
- chosen direction
- main risks
- phase shape
- current phase to validate next
- high-level story or bead shape

Do not duplicate `approach.md`. If multi-phase, summarize the sequence briefly and point to `phase-plan.md`.

## 4. `phase-plan.md`

Create only in `multi-phase` mode.

It must answer:
1. what the full feature makes true
2. why one phase is not enough
3. what the 2-4 phases are
4. what becomes true after each phase
5. why the order makes sense
6. which phase to prepare now
7. what later phases intentionally defer

Every phase must be a real capability slice, not a work bucket.

## 5. Multi-Phase Approval

The user must approve:
- the whole phase sequence
- the selected current phase
- the intentional deferral of later phases

This is not the execution approval gate. Use `beo-reference` → `references/approval-gates.md`.

## 6. Current-Phase Artifacts

`phase-contract.md` must define:
- why this phase exists now
- entry state
- exit state
- simplest demo story
- what it unlocks
- out of scope
- pivot signals

`story-map.md` must define:
- why each story exists
- why the order is correct
- what each story unlocks
- how story completion closes the phase

Do not create beads until both current-phase artifacts exist.

Multi-phase rule:
- `phase-contract.md` and `story-map.md` describe the selected current phase only
- create beads for the current phase only
- do not pre-create later-phase beads

## 7. High-Stakes Review

Use only for high-risk work: core architecture changes, auth flows, data model changes, broad blast radius, or major external dependency risk.

Run an isolated review over:
- `approach.md`
- `plan.md`
- `phase-plan.md` when present
- `phase-contract.md`
- `story-map.md`

Delegate only when the runtime allows it; otherwise run the same narrowed pass locally.

Check:
1. does the approach fit codebase reality
2. if multi-phase, does the sequence make practical sense
3. does the current phase close a believable small loop
4. do the stories belong in this order
5. what is missing from the exit state
6. which story or bead is too large, vague, or risky
7. what would be regretted six months later

Iterate 1-2 rounds, then stop when the changes are only incremental.
