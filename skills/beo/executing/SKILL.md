---
name: beo-executing
description: Per-worker implementation loop. Dispatched by beo-swarming or used directly for single-worker execution. Implements one task at a time: claim, build prompt, dispatch worker, verify, report, loop.
---

# Beo Executing

## Overview

Executing is the per-worker implementation loop. It picks the next actionable task, assembles a worker prompt, dispatches a subagent to implement it, and reports results back.

**Two operating modes:**
- **Worker mode** (dispatched by `beo-swarming`): Receives identity and epic ID from the orchestrator. Reports progress via Agent Mail. Implements code directly. Does NOT spawn sub-subagents.
- **Standalone mode** (after `beo-validating` for ≤2 tasks): Acts as both dispatcher and executor. Reports progress via STATE.md. Can dispatch worker subagents via `task()` calls for implementation, or implement directly for single-task features.

In both modes the loop is identical — the difference is how results are reported (Agent Mail vs STATE.md) and whether implementation is direct (worker mode) or delegated via `task()` (standalone mode with multiple tasks).

**Core principle**: One task at a time. Implement, verify, report, loop.

## When to Use

- Dispatched by `beo-swarming` as a worker
- Single-worker mode: after `beo-validating` approves the plan (`approved` label on epic)
- Router detected state = **ready-to-execute** or **executing**
- Resuming execution after a context handoff

## Prerequisites

```bash
# Epic must be approved
br show <EPIC_ID> --json
# Verify: labels array contains "approved"

# Tasks must exist (canonical enumeration — see pipeline-contracts.md)
br dep list <EPIC_ID> --direction up --type parent-child --json
```

<HARD-GATE>
If the epic does not have the `approved` label, STOP. Route to `beo-validating`.
</HARD-GATE>

### Epic Claim

On first entry (epic status is still `open`), transition the epic to `in_progress`:

```bash
br update <EPIC_ID> --claim
```

See `pipeline-contracts.md` → Epic Lifecycle.

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

## Phase 1: Select Next Task

```bash
bv --robot-plan --graph-root <EPIC_ID> --format json 2>/dev/null || bv --robot-next --format json 2>/dev/null || br ready --json
```

Pick the top executable bead from the first available track. If dispatched by swarming, follow any startup hint but always verify against the live graph.

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

Reserve files before editing (required in worker mode, recommended in standalone mode). Use Agent Mail `file_reservation_paths` or coordinate via the file convention your project uses. Do not edit files without reserving them first.

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
# Extract the latest report artifact (see artifact protocol in beo-reference)
```

### Budget Truncation

If the assembled prompt is too large:
1. Truncate plan.md to approach section only (skip task list)
2. Include only directly relevant CONTEXT.md decisions
3. Summarize previous task results instead of including full reports
4. Never truncate the task spec itself — that's the core payload

## Phase 4: Worker Dispatch

**Standalone mode only** — in worker mode, implement the task directly (skip to Phase 5 after implementation).

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

See `beo-reference` for the complete status mapping table. Quick reference:

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
# Check overall progress (canonical enumeration)
br dep list <EPIC_ID> --direction up --type parent-child --json

# Count by status
# open: not started
# in_progress: being worked on (shouldn't be any after worker returns)
# closed: done
# deferred: blocked or failed

# Check what's next
bv --robot-next --format json 2>/dev/null || br ready --json
# Filter results to tasks under this epic (cross-reference with br dep list <EPIC_ID>)
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
| **Scope exceeds task boundary** | The task needs re-planning — strip `approved` label (`br label remove <EPIC_ID> -l approved`) and route to `beo-planning` |
| **Ambiguous requirement** | Route to user for clarification |
| **Technical issue** (build failure, test failure) | Route to `beo-debugging` if not resolvable in-context |

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

## Completion

When all tasks under the epic are closed:

```bash
# Verify all tasks are closed (canonical enumeration)
br dep list <EPIC_ID> --direction up --type parent-child --json
# Filter for .status != "closed" — should return empty

# Verify build/tests pass
# (Run project-specific build and test commands)
```

Update state:

**In swarming mode** (dispatched by `beo-swarming`):
Report completion to the orchestrator via Agent Mail and stop.

**In single-worker mode**:
```markdown
# Beo State
- Phase: executing → complete
- Feature: <epic-id> (<feature-name>)
- Tasks: <total> completed, <blocked> blocked, <failed> failed
- Next: beo-reviewing
```

Announce:
```
Execution complete.
- <N>/<total> tasks completed successfully
- Build: <pass/fail>
- Tests: <pass/fail>

Load beo-reviewing for quality verification and feature completion.
```

## Context Budget

If context usage exceeds 65%:

**In swarming mode**: Write a final report artifact for the current task and stop gracefully. The orchestrator will re-dispatch remaining work.

**In single-worker mode**:
1. Finish updating the current task's status
2. Write HANDOFF.json:
   ```json
   {
     "schema_version": 1,
     "phase": "executing",
     "skill": "beo-executing",
     "feature": "<epic-id>",
     "feature_name": "<feature-name>",
     "next_action": "Task <TASK_ID> completed. Resume scheduling from Phase 1.",
     "in_flight_beads": [],
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
   br dep list <EPIC_ID> --direction up --type parent-child --json
   ```
4. Check for HANDOFF.json:
   ```bash
   cat .beads/HANDOFF.json 2>/dev/null
   ```
5. Resume from the last known good state

## Red Flags

| Flag | Description |
|------|-------------|
| **Implementing code directly in standalone mode** | In standalone mode with multiple tasks, dispatch subagents via `task()` — do not write implementation code directly. In worker mode or standalone with a single task, direct implementation is expected. |
| **Dispatching without checking dependencies** | Always verify deps are satisfied before dispatch |
| **Ignoring worker blockers** | Every blocker needs classification and resolution |
| **Dispatching the same task twice** | Check task status before dispatching |
| **Skipping the report artifact** | Every completed task needs a report for downstream tasks |
| **Not flushing after updates** | Run `br sync --flush-only` after status changes |

## Anti-Patterns

| Pattern | Why It's Wrong | Instead |
|---------|---------------|---------|
| Sequential execution of independent tasks | Wastes time; use `beo-swarming` for parallel work | Route to swarming when multiple independent tasks are ready |
| Re-dispatching a failed task without investigation | Same failure will recur | Understand the failure first |
| Modifying task specs during execution | Plan integrity violation | If specs need changing, strip `approved` label (`br label remove <EPIC_ID> -l approved`) and route to planning |
| Dispatching all tasks at once | Overwhelms context, loses control | Dispatch 1-3 at a time, track progress |
| Skipping verification in the worker prompt | Workers will skip verification | Always include verification criteria |
