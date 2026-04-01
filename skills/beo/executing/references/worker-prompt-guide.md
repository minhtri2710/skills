# Worker Prompt Guide

Template, data gathering, and budget rules for Phase 3 (Worker Prompt Assembly) of `beo-executing`.

## Prompt Template

```markdown
# Task: <task title>

## Context
You are implementing a task for feature "<feature-name>".
This task belongs to the currently approved phase.
If the feature is multi-phase, later phases remain deferred and are out of scope.

## Planning Mode
- Mode: <single-phase | multi-phase>
- Current phase: <number>/<total or unknown> - <phase name>

## Strategy Context
<Relevant summary from approach.md: chosen approach, important constraints, major risks, and why this task exists in that strategy>

## Phase Exit State
<Exit state from phase-contract.md: what the current phase must achieve>

## Story Context
<Story context block from this bead's description: story name, purpose, contributes to, unlocks>

## Plan Summary
<Abbreviated plan.md summary for this task's place in the current phase>

## Your Task
<Full task description from bead: the spec>

## CONTEXT.md Decisions
<Relevant decisions from CONTEXT.md that affect this task>

## Previous Task Results
<Summaries from already-completed tasks that this task depends on>

## Verification
<Verification criteria from the task spec>

## Rules
- Implement ONLY what is described in the task spec
- Respect the chosen strategy unless the task spec explicitly says otherwise
- Do NOT modify files outside the listed file scope
- Do NOT pull future-phase work into the current task
- Run verification before reporting completion
- If blocked, report the blocker. Do not guess or workaround
- If the task grows beyond scope, report it. Do not scope-creep
```

## Gathering Prompt Data

```bash
# Get task spec (bead description)
br show <TASK_ID> --json
# Extract: .description field

# Get strategy context
cat .beads/artifacts/<feature_slug>/approach.md 2>/dev/null
# Extract: recommended approach, planning mode, relevant constraints/risks

# Get plan summary
cat .beads/artifacts/<feature_slug>/plan.md
# Extract: only the summary relevant to this task's place in the current phase

# Get phase exit state
cat .beads/artifacts/<feature_slug>/phase-contract.md
# Extract: Exit State section

# Get story context
cat .beads/artifacts/<feature_slug>/story-map.md
# Extract: story details for the story this bead belongs to

# Get CONTEXT.md
cat .beads/artifacts/<feature_slug>/CONTEXT.md

# Get completed dependency task summaries
br dep list <TASK_ID> --direction down --type blocks --json
# For each completed dependency:
br comments list <DEP_ID> --json
# Extract the latest report artifact (see artifact protocol in beo-reference)
```

## Budget Truncation

If the assembled prompt is too large:
1. Reduce `approach.md` to the relevant strategy choice, constraints, and risks only
2. Reduce `plan.md` to the short summary that explains this task's role in the current phase
3. Truncate `phase-contract.md` to exit state only (skip diagram, scope, signals)
4. Truncate `story-map.md` to the relevant story only (skip other stories)
5. Include only directly relevant `CONTEXT.md` decisions
6. Summarize previous task results instead of including full reports
7. Never truncate the task spec itself. That is the core payload
