# Worker Prompt Guide

Template, data gathering, and budget rules for Worker Prompt Assembly in `beo-execute`.

For the canonical worker launch template (identity, Agent Mail, operating model), see `beo-reference` → `references/worker-template.md`. This guide covers the task-level prompt built for each bead.
When `beo-execute` launches a worker directly, this assembled prompt is the worker's full assignment package and must explicitly identify standalone dispatch, the coordination surface, the assigned bead, and the file scope.

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
Implementing a task for feature "<feature-name>" in the currently approved phase.
Multi-phase: later phases remain deferred and out of scope.

## Planning Mode
- Mode: <single-phase | multi-phase>
- Current phase: <number>/<total or unknown> - <phase name>

## Strategy Context
<From approach.md: chosen approach, constraints, risks, why this task exists>

## Phase Exit State
<From phase-contract.md: what the current phase must achieve>

## Story Context
<From bead description: story name, purpose, contributes to, unlocks>

## Plan Summary
<Abbreviated plan.md summary for this task's place in the current phase>

## Your Task
<Full task description from bead>

## CONTEXT.md Decisions
<Relevant decisions affecting this task>

## Previous Task Results
<Summaries from completed dependency tasks>

## Verification
<Verification criteria from the task spec>

## Rules
- Implement ONLY what the task spec describes
- Respect chosen strategy unless task spec explicitly says otherwise
- Do NOT modify files outside listed file scope
- Do NOT pull future-phase work into current task
- Run verification before reporting completion
- If blocked, report the blocker — do not guess or workaround
- If task grows beyond scope, report it — do not scope-creep
```

## Gathering Prompt Data

```bash
br show <TASK_ID> --json                          # Task spec (.description)
br dep list <TASK_ID> --direction down --type blocks --json  # Completed deps
br comments list <DEP_ID> --json --no-daemon      # Dep report artifacts
```

Read and extract from artifacts:

| Artifact | Extract |
|----------|---------|
| `approach.md` (optional) | Recommended approach, planning mode, relevant constraints/risks |
| `plan.md` | Summary relevant to this task's place in current phase |
| `phase-contract.md` | Exit State section |
| `story-map.md` | Story details for this bead's story |
| `CONTEXT.md` | Full content |

## Budget Truncation

If assembled prompt is too large (in priority order):
1. Reduce `approach.md` to relevant strategy, constraints, risks only
2. Reduce `plan.md` to short summary of this task's role
3. Truncate `phase-contract.md` to exit state only
4. Truncate `story-map.md` to relevant story only
5. Include only directly relevant CONTEXT.md decisions
6. Summarize previous task results instead of full reports
7. **Never** truncate the task spec itself — that is the core payload
