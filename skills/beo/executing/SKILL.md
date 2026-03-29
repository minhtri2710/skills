---
name: beo/executing
description: Use after validating approves the plan. Schedules tasks, assembles worker prompts, dispatches workers, tracks status, handles blockers. The implementation engine.
---

# Warcraft Executing

## Overview

Executing is the implementation engine. It picks the next actionable task from the bead graph, assembles a worker prompt, dispatches a subagent to implement it, and tracks progress until all tasks are complete.

**Core principle**: The orchestrator TENDS — it never implements code directly.

## When to Use

- After `beo/validating` approves the plan (`approved` label on epic)
- Router detected state = **ready-to-execute** or **executing**
- Resuming execution after a context handoff

## Prerequisites

```bash
# Epic must be approved
br show <EPIC_ID> --json
# Verify: labels array contains "approved"

# Tasks must exist
br list --type task --json | jq '[.[] | select(.id | startswith("<EPIC_ID>."))]'
```

<HARD-GATE>
If the epic does not have the `approved` label, STOP. Route to `beo/validating`.
</HARD-GATE>

## The Execution Loop

```
┌─→ Schedule (pick next task)
│        ↓
│   Dispatch (build prompt, launch worker)
│        ↓
│   Monitor (worker runs, returns result)
│        ↓
│   Update (record outcome, update bead)
│        ↓
│   Check (more tasks? blockers? done?)
│        ↓
└── Loop or Complete
```

## Phase 1: Scheduling

### The 4-Tier Scheduling Cascade

Try each tier in order. Use the first that returns a result.

**Tier 1: bv --robot-plan** (authoritative parallel tracks)
```bash
bv --robot-plan --format json
```
Returns parallel execution tracks with task ordering. If available, follow its recommended order.

**Tier 2: bv --robot-next** (single recommendation)
```bash
bv --robot-next --format json
```
Returns the single best next task. Use when robot-plan is unavailable.

**Tier 3: br ready** (unblocked tasks)
```bash
br ready --json
```
Returns all tasks with no unresolved dependencies. Pick the highest-priority one.

**Tier 4: Manual selection** (fallback)
```bash
br list --type task -s open --json
```
Filter to tasks whose dependencies are all closed. Pick highest priority.

### Task Selection Criteria

When multiple tasks are ready:
1. **Priority**: Lower number = higher priority
2. **Critical path**: Tasks on the critical path go first
3. **Risk**: HIGH-risk tasks early (fail fast)
4. **Independence**: Tasks with no downstream dependents can wait

## Phase 2: Pre-Dispatch Checks

Before dispatching a worker, verify:

```bash
# Check the task is still open
br show <TASK_ID> --json

# Verify dependencies are satisfied
br dep list <TASK_ID> --direction down --type blocks --json
# All blocking tasks must be closed
```

### Stale Label Cleanup

Before transitioning a task, clean up any stale labels from previous attempts:

```bash
# Remove stale labels if present
br label remove <TASK_ID> -l blocked 2>/dev/null
br label remove <TASK_ID> -l failed 2>/dev/null
br label remove <TASK_ID> -l partial 2>/dev/null
```

### Transition to In-Progress

```bash
# 1. Mark dispatch_prepared (pending → dispatch_prepared)
br label add <TASK_ID> -l dispatch_prepared

# 2. Claim the task (dispatch_prepared → in_progress)
br update <TASK_ID> --claim

# 3. Swap labels
br label remove <TASK_ID> -l dispatch_prepared
br label add <TASK_ID> -l in_progress

# 4. Record the dispatch
br audit record --kind tool_call --issue-id <TASK_ID> --tool-name "dispatch"
```

## Phase 3: Worker Prompt Assembly

Build the complete worker prompt for the subagent.

### Prompt Structure

```markdown
# Task: <task title>

## Context
You are implementing a task for feature "<feature-name>".

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

### Gathering Prompt Data

```bash
# Get task spec (bead description)
br show <TASK_ID> --json
# Extract: .description field

# Get plan summary
cat .beads/artifacts/<feature-name>/plan.md

# Get CONTEXT.md
cat .beads/artifacts/<feature-name>/CONTEXT.md

# Get completed dependency task summaries
br dep list <TASK_ID> --direction down --type blocks --json
# For each completed dependency:
br comments list <DEP_ID> --json
# Extract the latest report artifact (see artifact protocol in beo/reference)
```

### Budget Truncation

If the assembled prompt is too large:
1. Truncate plan.md to approach section only (skip task list)
2. Include only directly relevant CONTEXT.md decisions
3. Summarize previous task results instead of including full reports
4. Never truncate the task spec itself — that's the core payload

## Phase 4: Worker Dispatch

Launch the worker as a subagent:

```
task(
  description: "Implement: <task title>",
  prompt: "<assembled worker prompt>",
  subagent_type: "general"
)
```

The `task()` call is **blocking** — when it returns, the worker is done.

### Worker Behavior

The worker follows this flow:
1. **Understand**: Read the task spec and relevant code
2. **Orient**: Identify the implementation approach
3. **Implement**: Write the code changes
4. **Verify**: Run the verification criteria
5. **Report**: Update the task with results

### What the Worker Updates

The worker should report back via its final message with:
- **Status**: done / blocked / failed / partial
- **Summary**: What was accomplished
- **Blockers**: If blocked, what's blocking
- **Learnings**: Anything discovered during implementation

## Phase 5: Post-Worker Update

After the worker returns, update the bead graph.

### Status Mapping

See `beo/reference` for the complete status mapping table. Quick reference:

| Worker Reports | br Commands |
|---------------|-------------|
| **done** | `br label remove <ID> -l in_progress && br close <ID>` |
| **blocked** | `br label remove <ID> -l in_progress && br update <ID> -s deferred && br label add <ID> -l blocked` |
| **failed** | `br label remove <ID> -l in_progress && br update <ID> -s deferred && br label add <ID> -l failed` |
| **partial** | `br label remove <ID> -l in_progress && br update <ID> -s deferred && br label add <ID> -l partial` |

### Write the Report Artifact

Write the worker's report as a comment-backed artifact:

```bash
# Write report artifact
br comments add <TASK_ID> --no-daemon --message "---ARTIFACT:report:v1---
## Summary
<worker summary>

## Changes Made
<list of files modified>

## Verification
<verification results>

## Learnings
<anything discovered>
---END_ARTIFACT---"
```

### Flush

```bash
br sync --flush-only
```

## Phase 6: Progress Check

After each worker completes:

```bash
# Check overall progress
br list --type task --json | jq '[.[] | select(.id | startswith("<EPIC_ID>."))]'

# Count by status
# open: not started
# in_progress: being worked on (shouldn't be any after worker returns)
# closed: done
# deferred: blocked or failed

# Check what's next
bv --robot-next --format json 2>/dev/null || br ready --json
```

### Decision Table

| Condition | Action |
|-----------|--------|
| More ready tasks exist | Loop back to Phase 1 |
| All remaining tasks are blocked | Report blockers to user (see Blocker Handling) |
| All tasks are closed | Proceed to completion |
| A task failed | Report failure, ask user for decision |
| Context budget >65% | Write HANDOFF.json and pause |

## Blocker Handling

When a task reports blocked:

### Step 1: Understand the Blocker

```bash
# Read the task's blocker info
br show <TASK_ID> --json
br comments list <TASK_ID> --json
# Look for the blocker description in the latest report
```

### Step 2: Classify the Blocker

| Blocker Type | Action |
|-------------|--------|
| **Missing dependency output** | Check if the dependency task actually completed; if so, the worker may need clearer input |
| **External service unavailable** | Report to user, cannot resolve automatically |
| **Scope exceeds task boundary** | The task needs re-planning — route to `beo/planning` |
| **Ambiguous requirement** | Route to user for clarification |
| **Technical issue** (build failure, test failure) | Attempt to fix or create a fix-task |

### Step 3: Ask User for Decision

Present the blocker to the user with options:
1. Provide the missing information/decision
2. Skip the task (mark as cancelled)
3. Re-plan the task
4. Unblock manually

### Step 4: Resume

After the user provides a decision:

```bash
# Remove blocked label
br label remove <TASK_ID> -l blocked

# Reset to open
br update <TASK_ID> -s open

# Update description with the new information
br update <TASK_ID> --description "<updated spec with user's decision>"
```

Then loop back to Phase 1 to re-schedule.

## Parallel Execution (Optional)

When multiple independent tasks are ready simultaneously:

### Check Independence

Two tasks can run in parallel if:
- They have no dependency relationship (neither blocks the other)
- They modify different files (no file scope overlap)
- They don't depend on the same in-progress task

### Dispatch Multiple Workers

```
# Launch multiple task() calls in the same message
task(description: "Implement: <task A>", prompt: "<prompt A>", subagent_type: "general")
task(description: "Implement: <task B>", prompt: "<prompt B>", subagent_type: "general")
```

Wait for all to return, then update each task's status.

## Completion

When all tasks under the epic are closed:

```bash
# Verify all tasks are closed
br list --type task --json | jq '[.[] | select((.id | startswith("<EPIC_ID>.")) and .status != "closed")]'
# Should return empty array

# Verify build/tests pass
# (Run project-specific build and test commands)
```

Update state:
```markdown
# Warcraft State
- Phase: executing → complete
- Feature: <epic-id> (<feature-name>)
- Tasks: <total> completed, <blocked> blocked, <failed> failed
- Next: beo/reviewing
```

Announce:
```
Execution complete.
- <N>/<total> tasks completed successfully
- Build: <pass/fail>
- Tests: <pass/fail>

Load beo/reviewing for quality verification and feature completion.
```

## Context Budget

If context usage exceeds 65%:

1. Finish updating the current task's status
2. Write HANDOFF.json:
   ```json
   {
     "schema_version": 1,
     "phase": "executing",
     "skill": "beo/executing",
     "feature": "<epic-id>",
     "next_action": "Task <TASK_ID> completed. Resume scheduling from Phase 1.",
     "beads_in_flight": [],
     "timestamp": "<iso8601>"
   }
   ```
3. Flush: `br sync --flush-only`
4. Pause

## Post-Compaction Recovery

If you detect that context has been compacted (prior conversation is summarized):

1. Re-read CONTEXT.md:
   ```bash
   cat .beads/artifacts/<feature-name>/CONTEXT.md
   ```
2. Re-read the plan:
   ```bash
   cat .beads/artifacts/<feature-name>/plan.md
   ```
3. Re-read current task state:
   ```bash
   br list --type task --json | jq '[.[] | select(.id | startswith("<EPIC_ID>."))]'
   ```
4. Check for HANDOFF.json:
   ```bash
   cat .beo/HANDOFF.json 2>/dev/null
   ```
5. Resume from the last known good state

## Red Flags

| Flag | Description |
|------|-------------|
| **Implementing code directly** | The orchestrator dispatches workers; it never writes implementation code |
| **Dispatching without checking dependencies** | Always verify deps are satisfied before dispatch |
| **Ignoring worker blockers** | Every blocker needs classification and resolution |
| **Dispatching the same task twice** | Check task status before dispatching |
| **Skipping the report artifact** | Every completed task needs a report for downstream tasks |
| **Not flushing after updates** | Run `br sync --flush-only` after status changes |

## Anti-Patterns

| Pattern | Why It's Wrong | Instead |
|---------|---------------|---------|
| Sequential execution of independent tasks | Wastes time | Dispatch in parallel when safe |
| Re-dispatching a failed task without investigation | Same failure will recur | Understand the failure first |
| Modifying task specs during execution | Plan integrity violation | If specs need changing, route to planning |
| Dispatching all tasks at once | Overwhelms context, loses control | Dispatch 1-3 at a time, track progress |
| Skipping verification in the worker prompt | Workers will skip verification | Always include verification criteria |
