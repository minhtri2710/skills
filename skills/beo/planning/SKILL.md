---
name: beo-planning
description: >-
  Use after exploring completes. Research, synthesize, define the phase contract
  and story map, then decompose into task beads with dependencies via br/bv CLI.
  Writes discovery.md, plan.md, phase-contract.md, story-map.md, and creates
  beads that match the story structure.
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

## When to Use

- After `beo-exploring` completes (CONTEXT.md exists)
- User says "plan this", "create tasks", "decompose"
- Router detected state = **planning** (epic exists, no `approved` label, tasks may or may not exist)

## Prerequisites

Before starting, verify:

```bash
# CONTEXT.md must exist
cat .beads/artifacts/<feature-name>/CONTEXT.md

# Epic must exist
br show <EPIC_ID> --json

# Check for critical-patterns.md
cat .beads/critical-patterns.md 2>/dev/null
```

<HARD-GATE>
If CONTEXT.md does not exist, STOP. Route back to `beo-exploring`.
</HARD-GATE>

## Phase 0: Learnings Retrieval

**Mandatory.** Before any research, check institutional memory.

```bash
# Primary: read flat-file learnings
cat .beads/critical-patterns.md 2>/dev/null
ls .beads/learnings/*.md 2>/dev/null && grep -l "<feature domain keywords>" .beads/learnings/ 2>/dev/null
```

If QMD is available (optional enhancement), also run a semantic search:
```bash
qmd query "<feature description from CONTEXT.md>" --json 2>/dev/null
```

If any patterns are relevant to this feature's domain:
- Note them explicitly
- Embed them into the plan and affected task descriptions
- This prevents re-solving known problems

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

Write the complete plan to the feature artifacts:

```bash
# Write to .beads/artifacts/<feature-name>/plan.md
```

Also write the plan to the epic bead description:

### Slug Preservation

Before updating the epic description, read the current description first (`br show <EPIC_ID> --json`) and preserve the `slug: <feature_slug>` first line. See `beo-exploring` for the full protocol.

```bash
br update <EPIC_ID> --description "slug: <feature_slug>\n<plan content>"
```

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

Spawn a fresh subagent with plan.md, phase-contract.md, and story-map.md. Prompt: "Review this phase design for blind spots: (1) Does the phase contract close a small loop? (2) Do the stories make sense in this order? (3) What is missing from the exit state? (4) Which story is too large or vague? (5) What would the team regret 6 months from now?"

Iterate 1-2 rounds. Stop when changes become incremental.

## Phase 6: Task Bead Creation

Convert plan tasks into bead graph entries.

### Step 1: Create Task Beads

For each task in the plan:

```bash
# Create the task bead
br create "<Task Name>" -t task --parent <EPIC_ID> -p <priority> --json
```

Priority assignment (0-3 scale, see br-cli-reference):
- Spike/urgent: priority 0
- Critical path tasks: priority 1
- Standard tasks: priority 2
- Nice-to-have / cleanup: priority 3

### Step 2: Write Task Descriptions

For each task bead, write a complete description. The description must include Background, Files, Steps, Verification, Rollback (for HIGH risk), and a Story Context Block. See `references/bead-creation-guide.md` for the exact template and story context format.

```bash
br update <TASK_ID> --description "<task spec content>"
```

If no institutional learnings apply, write: "No prior learnings for this domain."

### Step 3: Wire Dependencies

For each task that depends on another:

```bash
# Task B depends on Task A (B is blocked by A)
br dep add <TASK_B_ID> <TASK_A_ID>
```

### Step 3.5: Complete the Story Map

After bead creation, fill the `Story-To-Bead Mapping` section in `.beads/artifacts/<feature-name>/story-map.md`.

The validator must be able to trace: `phase exit state → story → bead`

### Step 4: Validate the Graph

```bash
# Check for dependency cycles
br dep cycles --json

# Verify all tasks are reachable
bv --robot-insights --format json
```

If cycles are detected:
1. Identify the cycle
2. Determine which dependency is weakest (can be broken)
3. Remove it: `br dep remove <child> <parent>`
4. Re-validate

### Step 5: Bead Completeness Check

<HARD-GATE>
After all beads are created, read every bead back and verify. No bead may be handed off without passing this check. See `references/bead-creation-guide.md` for the full checklist.
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

If context usage exceeds 65% during planning:

1. Write all findings so far to discovery.md
2. Write partial plan.md if any tasks are decomposed
3. Write phase-contract.md if phase contract is drafted
4. Write story-map.md if stories are mapped
5. Create any task beads that are ready
6. Write HANDOFF.json:
   ```json
   {
     "schema_version": 1,
     "phase": "planning",
     "skill": "beo-planning",
     "feature": "<epic-id>",
     "feature_name": "<feature-name>",
      "next_action": "Continue from Phase <N>, Step <M>",
      "in_flight_beads": [],
      "timestamp": "<iso8601>"
    }
    ```
7. Report progress and pause

## Handoff

After plan is written, tasks are created, and dependencies are wired:

Write `.beads/STATE.md`:
```markdown
# Beo State
- Phase: planning → complete
- Feature: <epic-id> (<feature-name>)
- Tasks: <count> created
- Stories: <count> mapped
- Phase contract: written
- Next: beo-validating

Dependencies: <count> edges
```

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
