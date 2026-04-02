# Planning Operations

Detailed operational playbook for `beo-planning`.

Load this file when you need exact prerequisite checks, planning-mode selection, artifact-writing steps, task bead creation flow, dependency wiring, handoff details, or the high-stakes multi-perspective review procedure.

## Table of Contents

- [1. Prerequisites](#1-prerequisites)
- [2. Learnings Retrieval](#2-learnings-retrieval)
- [3. Decide Planning Mode](#3-decide-planning-mode)
- [4. Artifact Write Order](#4-artifact-write-order)
- [5. Writing `approach.md`](#5-writing-approachmd)
- [6. Writing `plan.md`](#6-writing-planmd)
- [7. Writing `phase-plan.md`](#7-writing-phase-planmd)
- [8. Multi-Phase Planning Approval](#8-multi-phase-planning-approval)
- [9. Writing Current-Phase Artifacts](#9-writing-current-phase-artifacts)
- [10. High-Stakes Multi-Perspective Check](#10-high-stakes-multi-perspective-check)
- [11. Task Bead Creation Operations](#11-task-bead-creation-operations)
- [12. Epic Description Update](#12-epic-description-update)
- [13. State Update and Handoff Rules](#13-state-update-and-handoff-rules)
- [14. Phase-Plan Invalidation and Replanning Cleanup](#14-phase-plan-invalidation-and-replanning-cleanup)
- [15. Context-Budget Checkpointing](#15-context-budget-checkpointing)

## 1. Prerequisites

Before starting, verify:

```bash
# Epic must exist
br show <EPIC_ID> --json
```

Read these artifacts with your file reading tool:

- `.beads/artifacts/<feature_slug>/CONTEXT.md` (required -- if absent, stop and route back to `beo-exploring`)
- `.beads/critical-patterns.md` (optional)

If `CONTEXT.md` does not exist, stop and route back to `beo-exploring`.

Planning assumes decisions are already locked. Do not reopen product-definition questions here unless the planning work proves the decisions are contradictory or incomplete.

## 2. Learnings Retrieval

This step is mandatory before research.

Use `../../reference/references/learnings-read-protocol.md` as the canonical read-side workflow.

If relevant patterns exist:

- note them explicitly in `discovery.md`
- apply them in `approach.md`
- carry them into affected bead descriptions
- let them influence whether the work should stay single-phase or become multi-phase

If no relevant prior learnings exist, record that explicitly rather than implying the step was skipped.

## 3. Decide Planning Mode

Planning supports two modes:

- `single-phase`
- `multi-phase`

Choose `single-phase` when ALL of these are true:

- one believable closed loop can explain the work
- the feature can usually be expressed in 1-4 stories
- there is no obvious capability sequence that should remain deferred
- preparing one current phase does not turn the phase into a vague work bucket

Choose `multi-phase` when ANY of these are true:

- the feature naturally unfolds across 2+ meaningful capability slices
- the current work mainly unlocks later work
- forcing everything into one phase would create a vague or oversized loop
- the full feature only makes sense as a sequence
- story count would likely exceed 4 if kept in one phase
- later work should stay intentionally deferred instead of being loosely implied

Record the planning-mode decision in `approach.md`.

Do not choose `multi-phase` just because the work is moderately large. Use the simplest mode that keeps the work understandable and execution-safe.

## 4. Artifact Write Order

Use the correct artifact order for the selected planning mode.

### Single-phase flow

1. `discovery.md`
2. `approach.md`
3. `plan.md`
4. `phase-contract.md`
5. `story-map.md`
6. task beads

### Multi-phase flow

1. `discovery.md`
2. `approach.md`
3. `plan.md`
4. `phase-plan.md`
5. multi-phase planning approval
6. `phase-contract.md` *(current phase only)*
7. `story-map.md` *(current phase only)*
8. task beads for the current phase only

### Artifact roles

- `discovery.md` = implementation landscape and findings
- `approach.md` = chosen strategy, alternatives, and risks
- `plan.md` = human-readable plan summary
- `phase-plan.md` = whole-feature sequencing for multi-phase work
- `phase-contract.md` = current phase only
- `story-map.md` = current phase only

Do not use `phase-contract.md` as a whole-feature artifact when the feature is clearly multi-phase.

## 5. Writing `approach.md`

Write `approach.md` to:

```bash
# .beads/artifacts/<feature_slug>/approach.md
```

Use `approach-template.md`.

Inputs:

- `CONTEXT.md`
- discovery findings
- prior learnings / critical patterns
- codebase constraints
- external dependency findings, if any

`approach.md` must explain:

- what the feature needs to make true
- what the codebase already provides
- what is missing or risky
- the recommended implementation strategy
- alternatives considered
- the risk map
- whether the work stays single-phase or becomes multi-phase

### Self-check for `approach.md`

Before continuing, verify:

- the recommended approach is described in practical language, not only abstract architecture terms
- at least one rejected alternative is named when meaningful alternatives exist
- the risk map is usable by validating and execution
- the planning mode decision is explicit and justified
- relevant learnings are actually applied, not just listed

If `approach.md` is weak, do not compensate by overloading `plan.md`. Fix `approach.md` first.

## 6. Writing `plan.md`

Write `plan.md` to:

```bash
# .beads/artifacts/<feature_slug>/plan.md
```

`plan.md` is the human-readable planning summary.

It should remain readable even when `approach.md` and `phase-plan.md` hold more structured detail.

### `plan.md` should summarize

- the feature goal
- the chosen implementation direction
- the main risks
- the phase shape
- the current phase that will be validated next
- the story/task shape at a high level

### Rules for `plan.md`

- keep it readable by a human scanning the plan quickly
- do not duplicate every detail from `approach.md`
- do not turn it into a second `phase-plan.md`
- if multi-phase, summarize the phase sequence briefly and point to `phase-plan.md` for full detail

## 7. Writing `phase-plan.md`

Only write `phase-plan.md` when planning mode is `multi-phase`.

Write to:

```bash
# .beads/artifacts/<feature_slug>/phase-plan.md
```

Use `phase-plan-template.md`.

`phase-plan.md` must answer:

1. what the full feature makes true
2. why one phase is not enough
3. what the 2-4 meaningful phases are
4. what becomes true after each phase
5. why the order makes sense
6. which phase should be prepared now
7. what later phases are intentionally deferred

### Rules for a good `phase-plan.md`

- every phase must describe a real capability slice, not a work bucket
- Phase 1 should feel obviously first
- later phases must be intentionally deferred, not vaguely implied
- the selected current phase must be a believable first / next slice
- if the phase list grows past 4, reconsider the feature framing

Do not create `phase-plan.md` for a feature that still fits a single clean closed loop.

## 8. Multi-Phase Planning Approval

If planning mode is `multi-phase`, explicit user approval is required before the current phase is handed off for validation.

This approval is for:
- the whole-feature phase sequence
- the selected current phase
- the intentional deferral of later phases

It is **not** the execution approval gate.

Use the canonical rule from `../../reference/references/approval-gates.md`.

### Approval prompt shape

```text
Whole-feature phase plan is ready.

- Total phases: <N>
- Current phase to prepare now: <phase name>
- Why this phase is first / next: <reason>
- Later phases intentionally deferred: <summary>

Approve this phase sequence and current phase selection before validation?
```

### If approved

- proceed to current-phase artifacts or validating handoff, depending on what is already drafted
- keep the approval meaning narrow: planning shape is approved, not execution readiness

### If rejected or withheld

- stop planning handoff
- revise `phase-plan.md`, `approach.md`, or current-phase framing
- do not route to `beo-validating`

## 9. Writing Current-Phase Artifacts

After `approach.md` is complete — and after `phase-plan.md` if multi-phase — prepare the current phase for execution.

### Write `phase-contract.md`

Use `phase-contract-template.md` and write to:

```bash
# .beads/artifacts/<feature_slug>/phase-contract.md
```

`phase-contract.md` always describes the **current phase only**.

It must define:

- why this phase exists now
- the entry state
- the exit state
- the simplest demo story
- what this phase unlocks next
- what is explicitly out of scope
- what signals would force a pivot

### Write `story-map.md`

Use `story-map-template.md` and write to:

```bash
# .beads/artifacts/<feature_slug>/story-map.md
```

`story-map.md` maps the **current phase only**.

It must explain:

- why each story exists
- why the stories appear in this order
- what each story unlocks
- how story completion supports the phase exit state

Do not create beads until both files exist.

### Current-phase rule for multi-phase work

If planning mode is `multi-phase`:

- `phase-contract.md` must describe the selected current phase
- `story-map.md` must map the selected current phase
- task beads must be created for the selected current phase only

Do not pre-create execution beads for later phases in this planning model.

## 10. High-Stakes Multi-Perspective Check

Only for high-stakes features:

- multiple HIGH-risk components
- core architecture changes
- auth flows
- data model changes
- broad blast radius
- external dependency risk that could invalidate the approach

Spawn a fresh subagent with:

- `approach.md`
- `plan.md`
- `phase-plan.md` if it exists
- `phase-contract.md`
- `story-map.md`

Prompt:

> Review this planning package for blind spots:
> 1. Does the chosen approach fit the codebase reality?
> 2. If this is multi-phase, does the phase sequence make practical sense?
> 3. Does the current phase close a believable small loop?
> 4. Do the stories make sense in this order?
> 5. What is missing from the exit state?
> 6. Which story or task is too large, vague, or risky?
> 7. What would the team regret 6 months from now?

Iterate 1-2 rounds. Stop when changes become incremental.

## 11. Task Bead Creation Operations

### Create Task Beads

For each current-phase task in the plan:

```bash
br create "<Task Name>" -t task --parent <EPIC_ID> -p <priority> --json
```

Priority assignment:

- spike / urgent proof task: 0
- critical path: 1
- standard delivery: 2
- cleanup / nice-to-have: 3

### Write Task Descriptions

Use the shared **Planned Task Bead Template** from:

```text
../../reference/references/bead-description-templates.md
```

```bash
br update <TASK_ID> --description "<markdown task spec content>"
```

If no institutional learnings apply, include:

```text
No prior learnings for this domain.
```

### Wire Dependencies

For each dependency:

```bash
# Task B depends on Task A (B is blocked by A)
br dep add <TASK_B_ID> <TASK_A_ID>
```

### Complete Story-to-Bead Mapping

After bead creation, fill the `Story-To-Bead Mapping` section in:

```bash
# .beads/artifacts/<feature_slug>/story-map.md
```

### Validate the Graph

```bash
# Check for dependency cycles
br dep cycles --json

# Verify all tasks are reachable
bv --robot-insights --format json
```

If cycles are detected:

1. identify the cycle
2. determine the weakest edge
3. remove it with `br dep remove <child> <parent>`
4. re-validate

### Bead Completeness Check

After all beads are created, read each one back and verify it passes the checklist from `bead-creation-guide.md`.

### Scope rule for multi-phase work

If planning mode is `multi-phase`, verify that every bead belongs to the selected current phase.

If a bead belongs to a later phase:

- remove it from the current execution set
- keep that work deferred in `phase-plan.md`
- do not smuggle future-phase work into the current phase “just to save time”

## 12. Epic Description Update

Before updating the epic description, use:

```text
../../reference/references/slug-protocol.md
```

Preserve the canonical slug-first shape.

If the epic description includes a planning summary, update it to reflect:

- planning mode (`single-phase` or `multi-phase`)
- whether `phase-plan.md` exists
- current phase number / name, if known
- total phase count, if known

Keep the description concise. Do not paste full artifact contents into the epic bead.

## 13. State Update and Handoff Rules

After planning artifacts are written, tasks are created, and dependencies are wired, write `.beads/STATE.md` using the canonical header from:

```text
../../reference/references/state-and-handoff-protocol.md
```

Then append planning-specific fields.

### Minimum planning state fields

- Phase: `planning → complete`
- Feature: `<epic-id> (<feature_slug>)`
- Planning mode: `single-phase | multi-phase`
- Has phase plan: `true | false`
- Current phase: `<number or 1>`
- Total phases: `<number or unknown>`
- Phase name: `<name or feature summary>`
- Next: `beo-validating`

### Handoff rules

#### Single-phase

- validating checks the current phase, which is also the full execution scope

#### Multi-phase

- validating checks the selected current phase only
- later phases remain deferred in `phase-plan.md`
- when the current phase completes and later phases remain, router should return to `beo-planning`
- do not treat current-phase completion as whole-feature completion
- do not hand off to validating until the user has approved the phase sequence and current-phase selection

### Approval summary templates

#### Single-phase

```text
Plan ready.
Mode: single-phase

- Current phase: full feature scope
- Stories: <count>
- Tasks: <count>
- Risks: <summary>

Ready to validate.
```

#### Multi-phase

```text
Whole-feature phase plan is ready.
Mode: multi-phase

- Total phases: <N>
- Current phase to prepare now: <phase name>
- Why this phase is first / next: <reason>
- Stories in current phase: <count>
- Tasks in current phase: <count>
- Later phases intentionally deferred: <summary>

Approve this phase sequence and current phase selection before validation?
```

## 14. Phase-Plan Invalidation and Replanning Cleanup

When planning re-enters (multi-phase back-edge, scope revision, or user-initiated replan), stale artifacts and state fields must be cleaned up before new planning proceeds.

### Trigger conditions

Replanning cleanup is required when any of these are true:

- the current phase completed and the back-edge returns to planning for the next phase
- the user or reviewer requests a scope revision that changes the phase structure
- the planning mode changes (e.g., multi-phase to single-phase or vice versa)
- the phase sequence changes within multi-phase work

### If replanning results in single-phase work

```bash
# 1. Delete stale phase-plan.md
rm .beads/artifacts/<feature_slug>/phase-plan.md

# 2. Delete stale current-phase artifacts if they reference the old phase identity
rm .beads/artifacts/<feature_slug>/phase-contract.md
rm .beads/artifacts/<feature_slug>/story-map.md
```

Then rewrite planning-aware state fields in `STATE.md` and `HANDOFF.json`:

- `planning_mode: single-phase`
- `has_phase_plan: false`
- `current_phase: 1`
- `total_phases: 1`
- `phase_name:` set to the feature summary (clear the stale value)

Regenerate `phase-contract.md` and `story-map.md` for the new single-phase scope.

### If replanning remains multi-phase but changes sequencing

1. Rewrite `phase-plan.md` to reflect the new sequence
2. Delete stale `phase-contract.md` and `story-map.md` if they reference an old phase identity
3. Refresh all planning-aware fields including `phase_name`
4. Regenerate current-phase artifacts for the newly selected phase
5. Prior approval is invalidated — route back through `beo-validating`

### If the current phase completed and the next phase starts

1. Update `phase-plan.md` to mark the completed phase
2. Delete old `phase-contract.md` and `story-map.md`
3. Increment `current_phase`
4. Update `phase_name` to the new current phase name
5. Create fresh `phase-contract.md` and `story-map.md` for the new current phase
6. Prior approval is invalidated — route back through `beo-validating`

### Hard rules

- **Delete, do not invalidate.** Stale `phase-plan.md` must be deleted, not marked invalid.
- **`phase_name` must be refreshed.** Do not leave a stale phase name from a prior cycle.
- **Prior approval is always invalidated** when the phase structure or execution scope changes.
- **`STATE.md` and `HANDOFF.json` must be refreshed** before any handoff after replanning.

## 15. Context-Budget Checkpointing

If context usage exceeds 65% during planning:

1. write findings so far to `discovery.md`
2. write `approach.md` if approach shaping has started
3. write `plan.md` if a summary exists
4. write `phase-plan.md` if multi-phase sequencing is already clear
5. write `phase-contract.md` if the current phase is drafted
6. write `story-map.md` if the current phase story sequence is drafted
7. create any ready current-phase task beads
8. write `HANDOFF.json`

Use the canonical base schema from:

```text
../../reference/references/state-and-handoff-protocol.md
```

Then add any planning-specific resume detail you need.

### Checkpoint rule

Prefer partial but truthful artifacts over leaving planning state only in conversation history.

A partial `approach.md` or `phase-plan.md` is acceptable if clearly marked as incomplete.
A missing artifact is harder to resume from than an incomplete one with explicit gaps.
