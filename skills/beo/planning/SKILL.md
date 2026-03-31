---
name: beo-planning
description: >-
  Use after exploring completes or whenever a feature already has locked
  requirements and now needs research, decomposition, phase definition, story
  mapping, and executable task beads. Use for prompts like "plan this", "break
  this into tasks", "decompose this work", "map the stories", "research and
  plan", or "turn this into beads" before implementation begins.
---

# Beo Planning

## Overview

Planning is the research-and-decompose phase. It takes CONTEXT.md from exploring and produces:
1. A `plan.md` document with the high-level approach
2. A `phase-contract.md` defining the phase as a closed loop with entry/exit state
3. A `story-map.md` breaking the phase into narrative slices
4. Task beads in the bead graph with dependencies wired and story context embedded
5. A risk classification for each task

**Core principle**: Plan once, execute many. Every minute spent planning saves 10 minutes of confused implementation.

## Core Planning Model

Planning operates at four levels:

```text
Whole Plan
  → Phase (closed loop with entry/exit state)
    → Stories (narrative slices explaining work order)
      → Beads (executable worker units)
```

Do not jump from `plan.md` straight to beads. If the phase cannot be explained in simple terms with a clear exit state and story sequence, it is not ready for execution.

## Mini Example

Phase:
"A user can submit feedback and the team can review it in the admin panel."

Stories:
1. Capture feedback submissions reliably
2. Display submitted feedback for review

Beads:
- Create the feedback persistence model and write path
- Add submission validation and success/error states
- Build the admin read view for submitted feedback

## Prerequisites

Load `references/planning-operations.md` for the exact prerequisite checks and learnings-retrieval commands.

<HARD-GATE>
If CONTEXT.md does not exist, STOP. Route back to `beo-exploring`.
</HARD-GATE>

## Phase 0: Learnings Retrieval

**Mandatory.** Before any research, check institutional memory.

If relevant patterns exist:
- note them explicitly
- embed them into the plan and affected task descriptions
- prevent re-solving known problems

## Phase 1: Discovery

Goal-oriented research to understand the implementation landscape. Launch 2-4 parallel research subagents (Architecture, Pattern, Constraint, External) to explore the codebase and external dependencies. Synthesize findings into `.beads/artifacts/<feature-name>/discovery.md`.

See `references/discovery-guide.md` for detailed agent descriptions and synthesis format.

## Phase 2: Plan Writing

### Step 1: Draft the Approach

Based on CONTEXT.md decisions and discovery findings, write the implementation approach:

```markdown
# Plan: <feature-name>

## Approach
<High-level implementation strategy in 2-3 paragraphs>

## Discovery Summary
<Key findings from research phase>

## Risk Assessment
<Known risks and mitigations>
```

### Step 2: Decompose into Tasks

Break the approach into discrete, executable tasks. Each task must be:
- **One agent, one context window**: Completable by a single worker in one session
- **30-90 minutes of work**: Not too small (overhead), not too large (context exhaustion)
- **Clear boundaries**: Obvious when it starts and when it's done
- **Independently verifiable**: Has its own test/verification criteria

### Task Format in plan.md

See `references/bead-creation-guide.md` for the full task description template including Story Context Block.

### Bead Acceptance Criteria

Before a task becomes a bead, verify all of the following:
- it names owned files or an explicit file region
- it includes one concrete verification command or observable check
- it has a clear done boundary, not just a topic area
- it belongs to exactly one story
- it unlocks or completes something real in the phase

```markdown
## Tasks

### 1. <Task Name>
**Files**: <list of files to create/modify>
**Dependencies**: none | [task numbers]
**Risk**: LOW | MEDIUM | HIGH
**Description**: <what to implement>
**Verification**: <how to verify it works>
```

### Risk Classification

| Signal | Risk Level |
|--------|-----------|
| Following existing pattern, <3 files | **LOW** |
| New pattern or 3-5 files | **MEDIUM** |
| External dependency, >5 files, architectural change | **HIGH** |

### Step 3: Write plan.md

Load `references/planning-operations.md` for the exact artifact-writing operations, including safe epic description updates with slug preservation.

## Phase 3: Phase Contract

Before creating beads, define the phase as a closed loop.

Write to `.beads/artifacts/<feature-name>/phase-contract.md` using `references/phase-contract-template.md`.

The phase contract must answer, in plain language:

1. Why this phase exists now
2. What the **entry state** is
3. What the **exit state** is
4. What the simplest **demo story** is
5. What this phase unlocks next
6. What is explicitly out of scope
7. What signals would force a pivot

### Rules for a good phase contract

- The exit state must be observable, not aspirational
- The phase must close a meaningful small loop by itself
- The demo story must prove the phase is real
- If the phase fails, the team should know whether to debug locally or rethink the larger plan

If you cannot explain the phase in 3-5 simple sentences, the phase is not ready. Revise plan.md before moving on.

<HARD-GATE>
If phase-contract.md does not exist, do not create beads. Define the phase first.
</HARD-GATE>

## Phase 4: Story Mapping

Break the phase into **Stories**, not "plans inside a phase."

Write to `.beads/artifacts/<feature-name>/story-map.md` using `references/story-map-template.md`.

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

- **Typical phase**: 2-4 stories
- **Small phase**: 1-2 stories
- **Large phase**: split into multiple phases instead of creating 5+ stories

Stories are the human-readable narrative. Beads come after.

<HARD-GATE>
If story-map.md does not exist, do not create beads. Map the stories first.
</HARD-GATE>

## Phase 5: Multi-Perspective Check (HIGH-Stakes Only)

**Only for HIGH-stakes features**: multiple HIGH-risk components, core architecture, auth flows, data model changes, or anything with a large blast radius. For standard features, skip to Phase 6.

Load `references/planning-operations.md` for the exact multi-perspective review procedure and prompt.

## Phase 6: Task Bead Creation

Convert plan tasks into bead graph entries.

Load `references/planning-operations.md` for the exact create/write/wire/validate sequence, priority mapping, and handoff-safe checkpointing rules.

<HARD-GATE>
After all beads are created, read every bead back and verify. No bead may be handed off without passing the checklist in `references/bead-creation-guide.md`.
</HARD-GATE>

### Story-to-Bead Decomposition Rules

See `references/bead-creation-guide.md` for decomposition rules. Key points: one story becomes 1-3 beads, no bead spans multiple stories, 4+ beads means the story may be too large.

## Phase 7: Plan Review

Before marking the plan as approved, run the self-review checklists in `references/bead-creation-guide.md` (Completeness Check, Decomposition Quality Check, Story Completeness Check).

### Present to User

Show the plan summary:
```
Plan: <feature-name>
Tasks: <count> (<HIGH risk>, <MEDIUM risk>, <LOW risk>)
Dependencies: <count> edges
Estimated parallel tracks: <count based on dependency structure>

[Task list with names, risk levels, and dependency chains]

Ready to validate? Load beo-validating for phase closure, story coherence, and bead quality verification.
```

## Lightweight Mode

For lightweight features (2-3 files, clear scope), see `references/bead-creation-guide.md` for the abbreviated workflow.

## Promotion Flow

When direct/instant tasks grow beyond their envelope, see `references/bead-creation-guide.md` for the promotion procedure.

## Context Budget

If context usage exceeds 65% during planning, load `references/planning-operations.md` and follow the checkpoint procedure exactly.

## Handoff

After plan artifacts are written, tasks are created, and dependencies are wired, load `references/planning-operations.md` for the canonical `STATE.md` handoff shape.

Announce:
```
Planning complete.
- Phase contract: .beads/artifacts/<feature-name>/phase-contract.md
- Story map: .beads/artifacts/<feature-name>/story-map.md (<S> stories)
- <N> tasks created with descriptions, story context, and verification criteria
- <M> dependency edges wired
- <K> HIGH-risk tasks identified
- All beads passed completeness check (non-empty descriptions verified)

Ready for validation. Load beo-validating to verify phase closure, story coherence, and bead quality.
```

## Red Flags & Anti-Patterns

See `references/planning-guardrails.md` for the complete red flags and anti-patterns tables.
