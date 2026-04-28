---
name: beo-plan
description: |
  Create or repair current-phase design and bead graph. Use when locked requirements exist and planning artifacts need creation or repair. Do not use when requirements are unlocked or contradicted.
metadata:
  dependencies:
    - id: beads-cli
      kind: command
      command: br
      missing_effect: unavailable
      reason: Required to create and update the canonical bead graph.
    - id: beads-viewer
      kind: command
      command: bv
      missing_effect: degraded
      reason: Useful for read-only bead inspection but not required for every planning write.
---

# beo-plan

## Purpose
Create or repair current-phase design and bead graph.

## Primary owned decision
Convert locked requirements into a current executable phase and bead graph.

## Enter when
- locked `CONTEXT.md` exists
- `PLAN.md`, phase shape, bead graph, dependencies, file scopes, verification plan, or any planning-depth-required section from `beo-references -> complexity.md` is missing, contradicted, or invalidated by contract-bearing change

## Writable surfaces
- `.beads/artifacts/<feature_slug>/PLAN.md` while creating or repairing current-phase design and bead graph
- bead descriptions and dependency fields described by `references/bead-ops.md`, only for planned current-phase beads
- approval state surfaces described by `beo-references -> approval.md`, only to invalidate stale approval after contract-bearing plan changes
- shared `STATE/HANDOFF` surfaces under `beo-references -> skill-contract-common.md`

## Decision packet
- shared decision packet under `beo-references -> skill-contract-common.md`
- no local packet extensions beyond plan, bead graph, and approval-invalidation evidence in owned surfaces

## Planning depth rule

When creating or repairing `PLAN.md`, choose the minimum planning depth that is safe:
- `small_change`
- `standard_feature`
- `high_risk_feature`

Depth affects how much discovery, phase mapping, risk proof, and story mapping are required.
It does not alter routing, approval, or execution ownership.
Use `beo-references -> complexity.md` for required sections by depth.

## Phase/story rule

A current phase must define:
- entry state
- exit state
- demo or inspectable result
- rollback expectation when relevant
- pivot signals when relevant
- explicit out-of-scope boundaries

A story must describe a user-visible or system-visible change.
A bead is an executable unit under a story.
Do not substitute a list of implementation chores for a story map.
Small changes may keep the story/phase expression compact, but the executable phase and bead scope must remain explicit.
For `standard_feature` and `high_risk_feature`, keep story map, file scope, verification plan, and risk map explicit.

## Risk proof rule

If a risk can change file scope, verification, acceptance, rollback, security, privacy, migration behavior, or cross-system compatibility, record the proof required before execution.

If the proof changes requirements, route to `beo-explore`.
If the proof changes phase shape, bead graph, scope, or verification, keep ownership in `beo-plan`.
Do not hide a high-risk unknown inside an execution bead.
HIGH risk without proof remains plan-incomplete for execution readiness.

## Prior-learning rule

Consult applicable feature/shared learnings when they match the active feature's domain, risk, failure mode, approval shape, or verification concern.
Record the consultation in `PLAN.md`.
Do not require every planning pass to read the entire learning corpus.

## Local hard stops
- Do not plan from unlocked or contradicted requirements.
- Do not create beads before the current phase contract is coherent.
- Do not mark a bead ready when file scope or verification is missing.
- Do not preserve stale approval assumptions after modifying phase contract, story map, risk map, bead graph, file scope, forbidden paths, or verification.
- Do not create separate history artifacts as canonical BEO state.
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
- `beo-references -> learning.md`
- `beo-references -> pipeline.md`
- `beo-references -> state.md`
- `references/bead-ops.md`
