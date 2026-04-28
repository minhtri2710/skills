---
name: beo-plan
description: |
  Create or repair current-phase design and bead graph. Use when locked requirements exist and planning artifacts need creation or repair. Do not use when requirements are unlocked or contradicted.
---

# beo-plan

## Purpose
Create or repair current-phase design and bead graph.

## Primary owned decision
Convert locked requirements into a current executable phase and bead graph.

## Enter when
- locked `CONTEXT.md` exists
- `PLAN.md`, phase shape, bead graph, dependencies, file scopes, or verification plan is missing, contradicted, or invalidated by contract-bearing change

## Writable surfaces
- `.beads/artifacts/<feature_slug>/PLAN.md` while creating or repairing current-phase design and bead graph
- bead descriptions and dependency fields described by `references/bead-ops.md`, only for planned current-phase beads
- approval state surfaces described by `beo-references -> approval.md`, only to invalidate stale approval after contract-bearing plan changes
- shared `STATE/HANDOFF` surfaces under `beo-references -> skill-contract-common.md`

## Decision packet
- shared decision packet under `beo-references -> skill-contract-common.md`
- no local packet extensions beyond plan, bead graph, and approval-invalidation evidence in owned surfaces

## Local hard stops
- Do not plan from unlocked or contradicted requirements.
- Do not preserve stale approval assumptions after a contract-bearing planning edit.
- Do not hand off to `beo-validate` before all planned beads have been created in the br DB via `br create`.
- Do not omit explicit file scope, forbidden paths when needed, or verification for a ready bead.

## Allowed next owners
- beo-validate
- beo-explore
- user

## References
- `beo-references -> artifacts.md`
- `beo-references -> approval.md`
- `beo-references -> complexity.md`
- `beo-references -> pipeline.md`
- `beo-references -> state.md`
- `references/bead-ops.md`
