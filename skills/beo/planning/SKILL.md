---
name: beo-planning
description: >-
  Use after exploring completes or whenever a feature already has locked
  requirements and now needs research, synthesis, phase definition, story
  mapping, and executable task beads. Use for prompts like "plan this",
  "break this into tasks", "decompose this work", "map the stories",
  "research and plan", or "turn this into beads" before implementation
  begins.
---

# Beo Planning

## Overview

Planning is the research-and-decompose phase. It takes `CONTEXT.md` from exploring and turns locked decisions into a credible implementation strategy and an execution-ready current phase.

## Key Terms

- **current phase**: the slice being prepared now for validation and execution
- **single-phase**: one closed loop is enough to deliver the feature safely
- **multi-phase**: the feature needs 2-4 intentional slices, and only the current one should be prepared now
- **phase plan**: the whole-feature sequence for multi-phase work; it is not the same thing as the current-phase contract

## Default Planning Loop

Use this happy-path loop before diving into the deeper operations file:

1. confirm `CONTEXT.md` exists and decisions are truly locked
2. retrieve prior learnings and critical patterns
3. run focused discovery
4. write `approach.md`
5. decide `single-phase` vs `multi-phase`
6. write `plan.md`, and `phase-plan.md` if needed
7. define the current phase with `phase-contract.md`
8. map the current phase into stories
9. create only the beads needed for the current phase
10. hand off to validation

Reach for `references/planning-operations.md` when you need the exact artifact order, approval wording, dependency wiring, or high-stakes review procedure.

Outputs:

1. A `discovery.md` document with the implementation landscape
2. An `approach.md` document with the chosen strategy, alternatives, and risk map
3. A `plan.md` summary that explains the plan in human-readable form
4. An optional `phase-plan.md` when the feature should unfold across multiple phases
5. A `phase-contract.md` defining the current phase as a closed loop with entry/exit state
6. A `story-map.md` breaking the current phase into narrative slices
7. Task beads in the bead graph with dependencies wired and story context embedded
8. A risk classification for each task

**Core principle**: Plan once, execute many. Every minute spent shaping the feature and the current phase saves confused implementation later.

## Core Planning Model

Planning operates at these levels:

```text
Whole Feature
  → Discovery
  → Approach
  → Plan Summary
  → Optional Phase Plan
  → Current Phase
  → Stories
  → Beads
```

Do not jump from research straight to beads.

If one believable closed loop is enough, stay single-phase and prepare that phase directly.

If the full feature is too large, too vague, or too sequential to fit one safe loop, create a `phase-plan.md` and prepare only the current phase for execution.

## Planning Modes

Planning supports two modes:

- **single-phase**: one believable closed loop can deliver the feature safely
- **multi-phase**: the feature unfolds across 2-4 meaningful capability slices, and only the current phase should be prepared now

Use the simplest mode that keeps the work understandable and execution-safe.

## When a Phase Plan Is Required

Create `phase-plan.md` when any of these are true:

- a single phase would become a vague work bucket
- the feature naturally unfolds across multiple capability slices
- story count would exceed 4 if forced into one phase
- the work has a clear unlock sequence where one slice must become true before later slices matter
- the team should prepare only the next slice while intentionally deferring later work

Do **not** create `phase-plan.md` just because the feature is moderately sized.
If one clear closed loop can still explain the work, stay single-phase.

## Mini Example

Single-phase example:

Phase:
"A user can submit feedback and the team can review it in the admin panel."

Stories:
1. Capture feedback submissions reliably
2. Display submitted feedback for review

Beads:
- Create the feedback persistence model and write path
- Add submission validation and success/error states
- Build the admin read view for submitted feedback

Multi-phase example:

Whole feature:
"Inbound messages are received safely, normalized, routed, and made operationally visible."

Phase plan:
1. Accept inbound payloads safely
2. Normalize and persist them consistently
3. Route them into the right workflow and add operational visibility

Current phase contract and story map describe only Phase 1 until that phase is complete.

## Prerequisites

Default checks:

```bash
cat .beads/artifacts/<feature-name>/CONTEXT.md 2>/dev/null
br show <EPIC_ID> --json
cat .beads/critical-patterns.md 2>/dev/null
```

Load `references/planning-operations.md` when you need the exact planning-mode selection rules, artifact order, or handoff details.

<HARD-GATE>
If `CONTEXT.md` does not exist, do not invent requirements here. First verify whether the feature was explored under a different slug or path. If no trustworthy context exists, route back to `beo-exploring`.
</HARD-GATE>

## Phase 0: Learnings Retrieval

**Mandatory.** Before any research, check institutional memory.

Default retrieval sequence:

1. query indexed learnings if QMD is available
2. read `.beads/critical-patterns.md` if it exists
3. fall back to flat-file learnings search only when richer retrieval is unavailable or insufficient
4. write down what actually matters for this plan

If relevant patterns exist:
- note them explicitly
- embed them into the approach and plan
- carry them into affected task descriptions
- prevent re-solving known problems

Relevant learnings must influence both the chosen implementation approach and any decision about whether the work stays single-phase or becomes multi-phase.

## Phase 1: Discovery

Goal-oriented research to understand the implementation landscape. Launch 2-4 parallel research subagents (Architecture, Pattern, Constraint, External) when the feature is broad enough to benefit from parallel discovery; otherwise research inline. Synthesize findings into `.beads/artifacts/<feature-name>/discovery.md`.

See `references/discovery-guide.md` for detailed agent descriptions and synthesis format.

Discovery findings are inputs to `approach.md`; they are not the final plan by themselves.

## Phase 2: Approach Synthesis

Write `.beads/artifacts/<feature-name>/approach.md`.

This artifact explains:

- what the feature needs to make true
- what the codebase already provides
- what is missing or risky
- the recommended implementation strategy
- alternatives considered
- the risk map
- whether the work should stay single-phase or become multi-phase

Use `references/approach-template.md`.

`approach.md` is the strategy artifact.
`plan.md` remains the human-readable planning summary.

## Phase 3: Whole-Feature Phase Planning (Optional but Required for Multi-Phase Work)

If the feature is multi-phase, write `.beads/artifacts/<feature-name>/phase-plan.md`.

The phase plan must explain:

1. the whole-feature goal
2. why one phase is not enough
3. the 2-4 meaningful phases
4. what becomes true after each phase
5. why the order makes sense
6. which phase should be prepared now

Use `references/phase-plan-template.md`.

<HARD-GATE>
If the work is clearly multi-phase, do not skip `phase-plan.md`.
Do not prepare the current phase as if it were the whole feature.
If you are unsure whether it is truly multi-phase, resolve that uncertainty in `approach.md` before creating current-phase beads.
</HARD-GATE>

## Phase 3.5: Multi-Phase Planning Approval

If `planning_mode = multi-phase`, get explicit user approval for the whole-feature phase sequence and the selected current phase **before** handing off to validation.

This approval is about planning shape, not execution readiness.

It confirms:
- the feature should be treated as multi-phase
- the phase order is believable
- the selected current phase is the right first / next slice
- later phases are intentionally deferred

This does **not** replace validation approval.
Validation approval still happens later and applies only to execution readiness for the current phase.

<HARD-GATE>
If the user has not explicitly approved the multi-phase sequence and current-phase selection, do not hand off to `beo-validating`.
If the user is confused or hesitant, tighten the phase framing first: revise `phase-plan.md`, `approach.md`, or current-phase naming before asking again.
</HARD-GATE>

## Phase 4: Current Phase Contract

Before creating beads, define the current phase as a closed loop.

Write to `.beads/artifacts/<feature-name>/phase-contract.md` using `references/phase-contract-template.md`.

`phase-contract.md` always describes the current phase being prepared now, not the whole feature.

The current phase contract must answer, in plain language:

1. Why this phase exists now
2. What the **entry state** is
3. What the **exit state** is
4. What the simplest **demo story** is
5. What this phase unlocks next
6. What is explicitly out of scope
7. What signals would force a pivot

### Rules for a good current phase contract

- The exit state must be observable, not aspirational
- The phase must close a meaningful small loop by itself
- The demo story must prove the phase is real
- If the phase fails, the team should know whether to debug locally or rethink the larger plan

If you cannot explain the current phase in 3-5 simple sentences, the phase is not ready. Revise `approach.md`, `plan.md`, or `phase-plan.md` before moving on.

<HARD-GATE>
If `phase-contract.md` does not exist, do not create beads. Define the current phase first.
If a draft exists but the exit state is vague, fix the contract instead of pushing uncertainty into bead descriptions.
</HARD-GATE>

## Phase 5: Current Phase Story Mapping

Break the current phase into **Stories**, not "plans inside a phase."

Write to `.beads/artifacts/<feature-name>/story-map.md` using `references/story-map-template.md`.

`story-map.md` maps the internal narrative of the current phase only.
If later phases exist, they remain deferred in `phase-plan.md`.

### Story rules

Every story must state:

- **Purpose**
- **Why now**
- **Contributes to** (which exit-state statement)
- **Creates** (code, contract, data, capability)
- **Unlocks** (what later stories can now do)
- **Done looks like** (observable finish line)

### Story quality checks

- Story 1 must have an obvious reason to exist first
- Every story must unlock or de-risk a later story, or directly close part of the exit state
- If all stories complete, the phase exit state should hold
- If a story cannot answer "what does this unlock?" it is probably not a real story

### Story count guidance

- **Typical current phase**: 2-4 stories
- **Small current phase**: 1-2 stories
- **Large current phase**: revise the phase shape instead of creating 5+ stories

Stories are the human-readable narrative. Beads come after.

<HARD-GATE>
If `story-map.md` does not exist, do not create beads. Map the current phase stories first.
If stories exist informally in `plan.md` but not as a real map, promote them into `story-map.md` before decomposition.
</HARD-GATE>

## Phase 6: Multi-Perspective Check (HIGH-Stakes Only)

**Only for HIGH-stakes features**: multiple HIGH-risk components, core architecture, auth flows, data model changes, or anything with a large blast radius. For standard features, skip to Phase 7.

Load `references/planning-operations.md` for the exact multi-perspective review procedure and prompt.

## Phase 7: Task Bead Creation

Convert current-phase plan tasks into bead graph entries.

Load `references/planning-operations.md` for the exact create/write/wire/validate sequence, priority mapping, and handoff-safe checkpointing rules.

<HARD-GATE>
After all beads are created, read every bead back and verify. No bead may be handed off without passing the checklist in `references/bead-creation-guide.md`.
</HARD-GATE>

### Story-to-Bead Decomposition Rules

See `references/bead-creation-guide.md` for decomposition rules. Key points: one story becomes 1-3 beads, no bead spans multiple stories, 4+ beads means the story may be too large.

For multi-phase work, create beads for the current phase only.
Do not pre-create execution beads for future phases in this planning model.
