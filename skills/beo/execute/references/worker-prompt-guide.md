# Worker Prompt Guide

Task-level prompt assembly for `beo-execute`.

For runtime identity, Agent Mail setup, and the canonical worker shell, use `beo-reference` → `references/worker-template.md`. This file defines the bead-specific payload.

## Prompt Template

```markdown
# Task: <task title>

## Dispatch Contract
- Dispatch mode: <standalone-beo-execute | beo-swarm>
- Coordination surface: <agent-mail | runtime-only>
- Assigned bead: <TASK_ID>
- File scope:
  - <path-or-glob-1>
  - <path-or-glob-2>

## Context
Implementing feature "<feature-name>" in the current approved phase only. Later phases are out of scope.

## Planning Mode
- Mode: <single-phase | multi-phase>
- Current phase: <number>/<total or unknown> - <phase name>

## Strategy Context
<chosen approach, constraints, risks, and why this bead exists>

## Phase Exit State
<exit state from phase-contract.md>

## Story Context
<story name, purpose, contributes to, unlocks>

## Plan Summary
<short task-local summary from plan.md>

## Your Task
<full bead description>

## CONTEXT.md Decisions
<only decisions that constrain this bead>

## Previous Task Results
<summaries from completed dependency beads>

## Verification
<verification from the bead>

## Rules
- Implement only the assigned bead
- Respect the chosen strategy unless the bead explicitly overrides it
- Do not edit outside the declared file scope
- Do not pull future-phase work into the bead
- Run verification before reporting completion
- If blocked, report the blocker; do not guess
- If scope expands, report it; do not scope-creep
```

## Data Gathering

```bash
br show <TASK_ID> --json
br dep list <TASK_ID> --direction down --type blocks --json
br comments list <DEP_ID> --json --no-daemon
```

Read and extract:

| Source | Include |
| --- | --- |
| `approach.md` | chosen approach, relevant constraints, relevant risks, planning mode |
| `plan.md` | short summary of this bead's place in the current phase |
| `phase-contract.md` | exit state |
| `story-map.md` | only the story that owns this bead |
| `CONTEXT.md` | only decisions that constrain this bead |
| dependency reports | only results that change implementation or verification |

## Truncation Order

If the assembled prompt is too large, cut in this order:
1. reduce `approach.md` to task-relevant strategy, constraints, and risks
2. reduce `plan.md` to a short task-local summary
3. truncate `phase-contract.md` to exit state only
4. truncate `story-map.md` to the owning story only
5. include only directly relevant `CONTEXT.md` decisions
6. summarize previous task results instead of pasting full reports
7. never truncate the task spec itself
