---
name: beo-planning
description: >-
  Use after exploring completes or whenever a feature already has locked
  requirements and needs implementation planning. Use for prompts like "plan
  this", "break this into tasks", "decompose this work", "map the stories",
  "research and plan", or "turn this into beads" before implementation
  begins.
---

# Beo Planning

## Overview

Planning turns locked decisions in `CONTEXT.md` into an execution-ready **current phase**.
It should answer two questions in order:

1. what is the right whole-feature shape?
2. what is the smallest current phase we should validate next?

**Core principle:** do not jump from research straight to beads. First shape the feature, then define the current phase, then decompose that phase only.

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

## Planning Modes

Use the simplest mode that keeps execution safe and understandable.

### `single-phase`
Use when one believable closed loop can deliver the feature safely, usually in 1-4 stories, with no important capability slice that should stay deferred.

### `multi-phase`
Use when the feature naturally unfolds across 2-4 meaningful capability slices, the current work mainly unlocks later work, or forcing everything into one phase would create a vague bucket or >4 stories.

`phase-plan.md` is the whole-feature sequence for multi-phase work.
`phase-contract.md` and `story-map.md` always describe the **current phase only**.

## Required Artifacts and Their Roles

Write artifacts in this order:

1. `discovery.md` — implementation landscape and findings
2. `approach.md` — chosen strategy, alternatives, risks, planning-mode decision
3. `plan.md` — short human-readable plan summary
4. `phase-plan.md` — whole-feature sequencing, only when work is truly multi-phase
5. `phase-contract.md` — current phase entry state, exit state, demo story, unlocks, out of scope, pivot signals
6. `story-map.md` — current phase stories, order, closure, and story-to-bead logic
7. task beads — executable tasks for the current phase only

Use these templates and guides when writing artifacts:
- `references/approach-template.md`
- `references/phase-plan-template.md`
- `references/phase-contract-template.md`
- `references/story-map-template.md`
- `references/bead-creation-guide.md`

## Learnings Retrieval

This step is mandatory before discovery.

Use `../reference/references/learnings-read-protocol.md` for the canonical read flow.
If relevant patterns exist, they must influence:

- the chosen approach
- the planning-mode decision
- the current-phase shape
- any affected bead descriptions

If no relevant learnings exist, record that explicitly rather than implying the step was skipped.

## Discovery and Approach

`discovery.md` gathers evidence.
`approach.md` turns that evidence into a decision.

`approach.md` must make these things explicit:
- what the feature needs to make true
- what the codebase already provides
- what is missing or risky
- the recommended implementation strategy
- meaningful alternatives considered
- the risk map
- the planning-mode decision and why it is justified

If `approach.md` is weak, do not compensate by stuffing extra detail into `plan.md`. Fix `approach.md` first.

## Multi-Phase Approval

If planning mode is `multi-phase`, get explicit user approval before validation handoff.
That approval confirms:

- the feature should be treated as multi-phase
- the phase order is believable
- the selected current phase is the right first / next slice
- later phases are intentionally deferred

Use the canonical approval rule from `../reference/references/approval-gates.md` and the exact prompt shape in `references/planning-operations.md`.

## Current-Phase Definition

Before bead creation, define the current phase as a closed loop.

### `phase-contract.md`
This file must explain:
- why this phase exists now
- the entry state
- the exit state
- the simplest demo story
- what this phase unlocks next
- what is explicitly out of scope
- what signals would force a pivot

If the exit state is vague, fix the contract instead of pushing uncertainty into bead descriptions.

### `story-map.md`
This file must explain the internal narrative of the current phase only.
Each story should make clear:
- why it exists
- why it is now
- what it creates
- what it unlocks
- what done looks like

If stories do not clearly support the phase exit state, fix the story map before creating beads.

## Bead Creation Rules

Only create beads after `phase-contract.md` and `story-map.md` are real and coherent.

Use `references/planning-operations.md` for the exact create / write / wire / validate sequence.
Use `references/bead-creation-guide.md` as the bead quality checklist.

Key rules:
- one story typically becomes 1-3 beads
- no bead should span unrelated stories
- 4+ beads for one story usually means the story is too large or poorly shaped
- for multi-phase work, every bead must belong to the selected current phase

After creation, read every bead back and verify it is specific enough for a fresh worker.

## High-Stakes Review

For HIGH-stakes work — core architecture, auth, data model changes, large blast radius, or multiple HIGH-risk components — use `references/planning-operations.md` for the multi-perspective review before handoff.

## Handoff to Validation

After current-phase artifacts are written and beads are verified:

1. write `.beads/STATE.md` using `../reference/references/state-and-handoff-protocol.md`
2. include planning-aware fields (`planning_mode`, `has_phase_plan`, `current_phase`, `total_phases`, `phase_name`) when known
3. announce handoff to `beo-validating`

Validation always approves execution readiness for the **current phase only**.
If later phases remain, current-phase completion is not whole-feature completion.

Write `.beads/HANDOFF.json` only when the context budget requires a checkpoint or the session must pause.

## Replanning and Phase Advancement

When planning re-enters after a scope change or completed phase:

- delete or replace stale `phase-plan.md`, `phase-contract.md`, and `story-map.md` as needed
- refresh `planning_mode`, `has_phase_plan`, `current_phase`, `total_phases`, and `phase_name` in `STATE.md` / `HANDOFF.json`
- regenerate current-phase artifacts for the newly selected phase
- treat prior approval as invalid
- route back through `beo-validating` before execution resumes

Use `references/planning-operations.md` section 14 for the exact cleanup sequence.

## Context Budget

If context usage exceeds 65%, use `../reference/references/state-and-handoff-protocol.md` for the canonical `STATE.md` / `HANDOFF.json` shapes, then checkpoint:
- planning mode
- current-phase selection
- artifact completeness
- any ready beads already created

## Red Flags & Anti-Patterns

See `references/planning-guardrails.md` for the full tables.
