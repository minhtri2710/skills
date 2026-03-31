---
name: beo-executing
description: >-
  Per-worker implementation loop. Dispatched by beo-swarming or used directly
  for single-worker execution. Implements one task at a time in a claim, build
  prompt, dispatch worker, verify, report, loop cycle. Trigger phrases: implement
  this bead, do the work, execute task, run the worker, start implementing.
---

# Beo Executing

## Overview

Executing is the per-worker implementation loop. It picks the next actionable task, assembles a worker prompt, dispatches a subagent to implement it, and reports results back.

**Two operating modes:**
- **Worker mode** (dispatched by `beo-swarming`): Receives identity and epic ID from the orchestrator. Reports progress via Agent Mail. Implements code directly. Does NOT spawn sub-subagents.
- **Standalone mode** (after `beo-validating` for ≤2 tasks): Acts as both dispatcher and executor. Reports progress via STATE.md. Can dispatch worker subagents via `task()` calls for implementation, or implement directly for single-task features.

In both modes the loop is identical; the difference is how results are reported (Agent Mail vs STATE.md) and whether implementation is direct (worker mode) or delegated via `task()` (standalone mode with multiple tasks).

**Core principle**: One task at a time. Implement, verify, report, loop.

## Prerequisites

```bash
# Epic must be approved
br show <EPIC_ID> --json
# Verify: labels array contains "approved"

# Tasks must exist (canonical enumeration; see pipeline-contracts.md)
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

### Description Verification

```bash
br show <TASK_ID> --json
# Extract .description; must be non-empty and structurally complete
```

Verify the description contains ALL of:

1. Non-empty and substantive (not just a title restatement)
2. File scope (which files to create/modify)
3. Concrete verification criteria (runnable checks, not "make sure it works")
4. Story context block (Story, Purpose, Contributes To, Unlocks) unless this is a reactive fix bead (see Bead Classes below)

<HARD-GATE>
If `.description` is empty, or is missing file scope AND verification criteria, STOP. Do not dispatch this task. Report it as invalid for execution:

"Task <TASK_ID> has an empty or underspecified description. Route back to beo-planning or beo-validating to complete the bead spec."

Do not attempt to reconstruct the spec from plan.md or CONTEXT.md; that produces low-quality worker output.
</HARD-GATE>

### Bead Classes

Two classes of beads may reach execution:

| Class | Created By | Story Context Required | Minimum Description |
|-------|-----------|----------------------|-------------------|
| **Planned execution bead** | beo-planning | Yes (full story context block) | Story context + file scope + steps + verification |
| **Reactive fix bead** | beo-reviewing (P1), beo-debugging, beo-router (instant) | No (exempt) | File scope + what to fix + verification |

Reactive fix beads are exempt from the story context requirement because they are created after planning completes. They still require file scope and verification criteria.

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

Build the complete worker prompt for the subagent. The prompt includes phase exit state, story context, plan summary, task spec, relevant CONTEXT.md decisions, previous task results, and verification criteria.

See `references/worker-prompt-guide.md` for the full prompt template, data gathering commands, and budget truncation rules.

**Key rule**: Never truncate the task spec itself; that is the core payload.

## Phase 4: Worker Dispatch

**Standalone mode only**: in worker mode, implement the task directly (skip to Phase 5 after implementation).

Launch the worker as a subagent:

```
task(
  description: "Implement: <task title>",
  prompt: "<assembled worker prompt>",
  subagent_type: "general"
)
```

The `task()` call is **blocking**; when it returns, the worker is done.

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

When a task reports blocked, follow the classification and resolution protocol in `references/blocker-handling.md`. Key steps: understand the blocker, classify it (missing dependency / external / scope / ambiguous / technical), ask the user for a decision, then resume from Phase 1.

## Completion

When all tasks under the epic are closed:

```bash
# Verify all tasks are closed (canonical enumeration)
br dep list <EPIC_ID> --direction up --type parent-child --json
# Filter for .status != "closed"; should return empty

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

If you detect that context has been compacted (prior conversation is summarized), follow the recovery procedure in `references/execution-guardrails.md` to re-read CONTEXT.md, plan, phase context, and task state before resuming.

## Red Flags & Anti-Patterns

See `references/execution-guardrails.md` for the complete red flags and anti-patterns tables.
