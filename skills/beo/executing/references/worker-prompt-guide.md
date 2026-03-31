# Worker Prompt Guide

Template, data gathering, and budget rules for Phase 3 (Worker Prompt Assembly) of `beo-executing`.

## Prompt Template

```markdown
# Task: <task title>

## Context
You are implementing a task for feature "<feature-name>".

## Phase Exit State
<Exit state from phase-contract.md — what the whole phase must achieve>

## Story Context
<Story context block from this bead's description — story name, purpose, contributes to, unlocks>

## Plan Summary
<Abbreviated plan.md — approach section only, not full plan>

## Your Task
<Full task description from bead — the spec>

## CONTEXT.md Decisions
<Relevant decisions from CONTEXT.md that affect this task>

## Previous Task Results
<Summaries from already-completed tasks that this task depends on>

## Verification
<Verification criteria from the task spec>

## Rules
- Implement ONLY what is described in the task spec
- Do NOT modify files outside the listed file scope
- Run verification before reporting completion
- If blocked, report the blocker — do not guess or workaround
- If the task grows beyond scope, report it — do not scope-creep
```

## Gathering Prompt Data

```bash
# Get task spec (bead description)
br show <TASK_ID> --json
# Extract: .description field

# Get plan summary
cat .beads/artifacts/<feature-name>/plan.md

# Get phase exit state
cat .beads/artifacts/<feature-name>/phase-contract.md
# Extract: Exit State section

# Get story context
cat .beads/artifacts/<feature-name>/story-map.md
# Extract: story details for the story this bead belongs to

# Get CONTEXT.md
cat .beads/artifacts/<feature-name>/CONTEXT.md

# Get completed dependency task summaries
br dep list <TASK_ID> --direction down --type blocks --json
# For each completed dependency:
br comments list <DEP_ID> --json
# Extract the latest report artifact (see artifact protocol in beo-reference)
```

## Budget Truncation

If the assembled prompt is too large:
1. Truncate plan.md to approach section only (skip task list)
2. Truncate phase-contract.md to exit state only (skip diagram, scope, signals)
3. Truncate story-map.md to the relevant story only (skip other stories)
4. Include only directly relevant CONTEXT.md decisions
5. Summarize previous task results instead of including full reports
6. Never truncate the task spec itself — that's the core payload
