# Planning Operations

Detailed operational playbook for `beo-planning`. Load this file when you need exact artifact-writing steps, task bead creation flow, dependency wiring, handoff details, or the high-stakes multi-perspective review procedure.

## Table of Contents

- [1. Prerequisites](#1-prerequisites)
- [2. Learnings Retrieval](#2-learnings-retrieval)
- [3. Plan Writing Operations](#3-plan-writing-operations)
- [4. High-Stakes Multi-Perspective Check](#4-high-stakes-multi-perspective-check)
- [5. Task Bead Creation Operations](#5-task-bead-creation-operations)
- [6. Handoff and Progress Checkpointing](#6-handoff-and-progress-checkpointing)

## 1. Prerequisites

Before starting, verify:

```bash
# CONTEXT.md must exist
cat .beads/artifacts/<feature-name>/CONTEXT.md

# Epic must exist
br show <EPIC_ID> --json

# Check for critical-patterns.md
cat .beads/critical-patterns.md 2>/dev/null
```

If `CONTEXT.md` does not exist, stop and route back to `beo-exploring`.

## 2. Learnings Retrieval

This step is mandatory before research. Use `../../reference/references/learnings-read-protocol.md` as the canonical read-side workflow.

If relevant patterns exist:
- note them explicitly
- embed them into the plan
- carry them into affected bead descriptions

## 3. Plan Writing Operations

### Write `plan.md`

Write the complete plan to:

```bash
# Write to .beads/artifacts/<feature-name>/plan.md
```

### Update the Epic Description Safely

Before updating the epic description, use `../../reference/references/slug-protocol.md` and preserve the canonical slug-first shape.

### Write `phase-contract.md`

Use `phase-contract-template.md` and write to:

```bash
# .beads/artifacts/<feature-name>/phase-contract.md
```

### Write `story-map.md`

Use `story-map-template.md` and write to:

```bash
# .beads/artifacts/<feature-name>/story-map.md
```

Do not create beads until both files exist.

## 4. High-Stakes Multi-Perspective Check

Only for high-stakes features: multiple HIGH-risk components, core architecture, auth flows, data model changes, or anything with a large blast radius.

Spawn a fresh subagent with:
- `plan.md`
- `phase-contract.md`
- `story-map.md`

Prompt:

> Review this phase design for blind spots: (1) Does the phase contract close a small loop? (2) Do the stories make sense in this order? (3) What is missing from the exit state? (4) Which story is too large or vague? (5) What would the team regret 6 months from now?

Iterate 1-2 rounds. Stop when changes become incremental.

## 5. Task Bead Creation Operations

### Create Task Beads

For each task in the plan:

```bash
br create "<Task Name>" -t task --parent <EPIC_ID> -p <priority> --json
```

Priority assignment:
- spike/urgent: 0
- critical path: 1
- standard: 2
- cleanup/nice-to-have: 3

### Write Task Descriptions

Use the shared **Planned Task Bead Template** from `../../reference/references/bead-description-templates.md`.

```bash
br update <TASK_ID> --description "<markdown task spec content>"
```

If no institutional learnings apply, include: `No prior learnings for this domain.`

### Wire Dependencies

For each dependency:

```bash
# Task B depends on Task A (B is blocked by A)
br dep add <TASK_B_ID> <TASK_A_ID>
```

### Complete Story-to-Bead Mapping

After bead creation, fill the `Story-To-Bead Mapping` section in `.beads/artifacts/<feature-name>/story-map.md`.

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

## 6. Handoff and Progress Checkpointing

### Context-Budget Checkpoint

If context usage exceeds 65% during planning:
1. write findings so far to `discovery.md`
2. write partial `plan.md` if decomposed
3. write `phase-contract.md` if drafted
4. write `story-map.md` if drafted
5. create any ready task beads
6. write `HANDOFF.json`

Use the canonical base schema from `../../reference/references/state-and-handoff-protocol.md`, then add any planning-specific resume detail you need.

### Normal Handoff

After plan artifacts are written, tasks are created, and dependencies are wired, write `.beads/STATE.md` using the canonical header from `../../reference/references/state-and-handoff-protocol.md`, then append the planning-specific fields.
