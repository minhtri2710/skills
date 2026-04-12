---
name: beo-planning
description: >-
  Use after exploring completes or whenever a feature already has locked
  requirements and needs implementation planning. Use for prompts like "plan
  this", "break this into tasks", "decompose this work", "map the stories",
  or "turn this into beads" before implementation begins. Do not use when
  requirements are still unlocked or ambiguous (use beo-exploring first).
---

<HARD-GATE>
If `.beads/onboarding.json` is missing or stale, stop and load `beo-using-beo` before continuing.
</HARD-GATE>

> **Co-load `beo-reference`** alongside this skill for canonical CLI commands, status mappings, and shared protocol definitions.

# Beo Planning

## Overview

Planning turns locked decisions in `CONTEXT.md` into an execution-ready **current phase**.
It should answer two questions in order:

1. what is the right whole-feature shape?
2. what is the smallest current phase we should validate next?

**Core principle:** do not jump from research straight to beads. First shape the feature, then define the current phase, then decompose that phase only.

## Hard Gates

<HARD-GATE>
If `CONTEXT.md` does not exist, do not invent requirements here. First verify the context was not written under a different slug or path. If no trustworthy context exists, route back to `beo-exploring`.
</HARD-GATE>

<HARD-GATE>
If the work is clearly multi-phase, do not skip `phase-plan.md` and do not prepare the current phase as if it were the whole feature.
</HARD-GATE>

<HARD-GATE>
Do not create beads before both `phase-contract.md` and `story-map.md` exist for the current phase.
</HARD-GATE>

<HARD-GATE>
For multi-phase work, do not hand off to `beo-validating` until the user has explicitly approved the whole-feature phase sequence and the selected current phase.
This approval is about planning shape, not execution readiness.
It does not replace validation approval.
</HARD-GATE>

<HARD-GATE>
Create beads for the current phase only. Do not pre-create execution beads for future phases.
</HARD-GATE>

<HARD-GATE>
If phase structure or execution scope changes during replanning, prior approval is invalidated. Refresh planning-aware state and route back through `beo-validating` before execution resumes.
</HARD-GATE>

## Default Planning Loop

1. confirm `CONTEXT.md` exists and decisions are truly locked
2. retrieve prior learnings and critical patterns
3. run focused discovery and write `discovery.md`
4. write `approach.md`
5. decide `single-phase` vs `multi-phase`
6. write `plan.md`
7. if multi-phase, write `phase-plan.md` and get explicit user approval for the phase sequence and selected current phase
8. define the current phase in `phase-contract.md`
9. map the current phase in `story-map.md`
10. create and verify beads for the current phase only
11. hand off to `beo-validating`

Load `references/planning-operations.md` when you need the exact artifact-writing sequence, approval wording, dependency wiring, bead-creation commands, high-stakes review flow, or replanning cleanup procedure.
Load `references/discovery-guide.md` when running focused discovery (step 3) for guidance on research subagent patterns and codebase investigation.

## Planning Modes

Use the simplest mode that keeps execution safe and understandable.

- **`single-phase`** — one believable closed loop, usually 1-4 stories.
- **`multi-phase`** — feature unfolds across 2+ meaningful capability slices.

See `references/planning-operations.md` § 3 for the full decision criteria.

`phase-plan.md` is the whole-feature sequence for multi-phase work.
`phase-contract.md` and `story-map.md` always describe the **current phase only**.
## Required Artifacts and Their Roles

Artifacts: `discovery.md`, `approach.md`, `plan.md`, `phase-plan.md` (multi-phase only), `phase-contract.md`, `story-map.md`, task beads.

See `references/planning-operations.md` sections 4-7 for write order, artifact roles, and required fields. Use the corresponding templates: `references/discovery-template.md`, `references/approach-template.md`, `references/plan-template.md`, `references/phase-plan-template.md`, `references/phase-contract-template.md`, `references/story-map-template.md`, `references/bead-creation-guide.md`.

## Learnings Retrieval

This step is mandatory before discovery.

Use `../reference/references/learnings-read-protocol.md` for the canonical read flow. See `references/planning-operations.md` section 2 for how learnings must influence planning artifacts.

If no relevant learnings exist, record that explicitly rather than implying the step was skipped.

## Discovery and Approach

`discovery.md` gathers evidence.
`approach.md` turns that evidence into a decision.

`approach.md` must exist before any current-phase artifacts are written. See `references/planning-operations.md` section 5 for the required fields and self-check.

If `approach.md` is weak, do not compensate by stuffing extra detail into `plan.md`. Fix `approach.md` first.

## Multi-Phase Approval

If planning mode is `multi-phase`, the user must explicitly approve the phase sequence and current-phase selection before validation handoff.

Use the canonical approval rule from `../reference/references/approval-gates.md` and the exact prompt shape and approval/rejection flow in `references/planning-operations.md` section 8.

## Current-Phase Definition

Before bead creation, define the current phase as a closed loop. Both `phase-contract.md` and `story-map.md` are required, and both describe the **current phase only**.

See `references/planning-operations.md` section 9 for required fields, and use `references/phase-contract-template.md` and `references/story-map-template.md` for structure.

If the exit state in `phase-contract.md` is vague, fix the contract instead of pushing uncertainty into bead descriptions. If stories in `story-map.md` do not clearly support the phase exit state, fix the story map before creating beads.

## Bead Creation Rules

Only create beads after `phase-contract.md` and `story-map.md` are real and coherent.

Use `references/planning-operations.md` section 11 for the exact create / write / wire / validate sequence.
Use `references/bead-creation-guide.md` for decomposition rules and the bead quality checklist.

After creation, read every bead back and verify it is specific enough for a fresh worker.

## High-Stakes Review

For HIGH-stakes work — core architecture, auth, data model changes, large blast radius, or multiple HIGH-risk components — use `references/planning-operations.md` for the multi-perspective review before handoff.

## Handoff

After current-phase artifacts are written and beads are verified:

1. write `.beads/STATE.json` using `../reference/references/state-and-handoff-protocol.md`
2. include planning-aware fields (`planning_mode`, `has_phase_plan`, `current_phase`, `total_phases`, `phase_name`) when known
3. announce handoff to `beo-validating`

Validation always approves execution readiness for the **current phase only**.
If later phases remain, current-phase completion is not whole-feature completion.

Write `.beads/HANDOFF.json` only when the context budget requires a checkpoint or the session must pause.


## Quick Mode

When `CONTEXT.md` classifies the feature as **Quick** (see `../reference/references/pipeline-contracts.md` § Quick-Scope Definition), planning uses an abbreviated flow:

- Skip parallel discovery; do a quick single-pass review of affected files
- Write abbreviated artifacts (approach + tasks in `plan.md`, single-story `story-map.md`, minimal `phase-contract.md`)
- The hard gate requiring `phase-contract.md` and `story-map.md` still applies — Quick mode writes abbreviated versions, it does not skip them
- Skip the formal multi-perspective review

See `references/bead-creation-guide.md` § Quick Mode for the exact abbreviated sequence.

## Replanning and Phase Advancement

When planning re-enters after a scope change or completed phase, stale artifacts and state fields must be cleaned up before new planning proceeds. Prior approval is always invalidated when the phase structure or execution scope changes.

Use `references/planning-operations.md` section 14 for the exact cleanup sequence, trigger conditions, and hard rules.

## Context Budget

If context usage exceeds 65%, use `../reference/references/state-and-handoff-protocol.md` for the canonical `STATE.json` / `HANDOFF.json` shapes, then checkpoint:
- planning mode
- current-phase selection
- artifact completeness
- any ready beads already created

## Red Flags & Anti-Patterns

See `references/planning-guardrails.md` for the full tables.
