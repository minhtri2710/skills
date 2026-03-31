# Execution Operations

Detailed operational playbook for `beo-executing`. Load this file when you need exact prereq checks, task transitions, reporting commands, completion verification, or checkpoint/handoff details.

## Table of Contents

- [1. Prerequisites](#1-prerequisites)
- [2. Epic Claim](#2-epic-claim)
- [3. Task Selection](#3-task-selection)
- [4. Pre-Dispatch Checks](#4-pre-dispatch-checks)
- [5. Task Transition Protocol](#5-task-transition-protocol)
- [6. Worker Dispatch and Reporting](#6-worker-dispatch-and-reporting)
- [7. Post-Worker Updates](#7-post-worker-updates)
- [8. Progress Check and Completion](#8-progress-check-and-completion)
- [9. Context-Budget Checkpoint](#9-context-budget-checkpoint)

## 1. Prerequisites

```bash
# Epic must be approved
br show <EPIC_ID> --json
# Verify: labels array contains "approved"

# Tasks must exist (canonical enumeration; see pipeline-contracts.md)
br dep list <EPIC_ID> --direction up --type parent-child --json
```

If the epic does not have the `approved` label, stop and route to `beo-validating`.

## 2. Epic Claim

On first entry, if the epic is still `open`, transition it to `in_progress`:

```bash
br update <EPIC_ID> --claim
```

See `pipeline-contracts.md` → Epic Lifecycle.

## 3. Task Selection

Use the scheduling cascade:

```bash
bv --robot-plan --graph-root <EPIC_ID> --format json 2>/dev/null || bv --robot-next --format json 2>/dev/null || br ready --json
```

Pick the top executable bead from the first available track. If dispatched by swarming, respect any startup hint but always verify against the live graph.

## 4. Pre-Dispatch Checks

### Check the Task and Dependencies

```bash
# Check the task is still open
br show <TASK_ID> --json

# Verify dependencies are satisfied
br dep list <TASK_ID> --direction down --type blocks --json
```

All blocking tasks must be closed.

### Stale Label Cleanup

```bash
br label remove <TASK_ID> -l blocked 2>/dev/null
br label remove <TASK_ID> -l failed 2>/dev/null
br label remove <TASK_ID> -l partial 2>/dev/null
```

### Description Verification

Read `br show <TASK_ID> --json` and verify `.description` is:
- non-empty and substantive
- includes file scope
- includes concrete verification criteria
- includes story context unless this is a reactive fix bead

If empty or underspecified, do not dispatch. Route back to `beo-planning` or `beo-validating`.

## 5. Task Transition Protocol

Reserve files before editing. Then transition:

```bash
# 1. Mark dispatch_prepared
br label add <TASK_ID> -l dispatch_prepared

# 2. Claim the task
br update <TASK_ID> --claim

# 3. Swap labels
br label remove <TASK_ID> -l dispatch_prepared
br label add <TASK_ID> -l in_progress

# 4. Record the dispatch
br audit record --kind tool_call --issue-id <TASK_ID> --tool-name "dispatch"
```

## 6. Worker Dispatch and Reporting

### Worker Prompt Assembly

Use `worker-prompt-guide.md` for the full prompt template and budget-truncation rules.

### Standalone Dispatch

Use the session's standard subagent or task-execution tool. The exact tool name may vary by environment; the required payload does not:

- implementation-focused task title or description
- assembled worker prompt
- worker/subagent type capable of implementation
- blocking wait for the result before post-worker updates

Abstract contract:

```text
dispatch_worker(
  description: "Implement: <task title>",
  prompt: "<assembled worker prompt>",
  worker_type: "implementation-capable"
)
```

If no worker-dispatch mechanism is available, skip delegated dispatch and implement directly in standalone mode.

### Worker Report Expectations

The worker should return:
- status: `done | blocked | failed | partial`
- summary
- blockers (if any)
- learnings

## 7. Post-Worker Updates

### Status Mapping

| Worker Reports | br Commands |
|---------------|-------------|
| `done` | `br label remove <ID> -l in_progress && br close <ID>` |
| `blocked` | `br label remove <ID> -l in_progress && br update <ID> -s deferred && br label add <ID> -l blocked` |
| `failed` | `br label remove <ID> -l in_progress && br update <ID> -s deferred && br label add <ID> -l failed` |
| `partial` | `br label remove <ID> -l in_progress && br update <ID> -s deferred && br label add <ID> -l partial` |

### Write the Report Artifact

```bash
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

## 8. Progress Check and Completion

### Progress Check

```bash
br dep list <EPIC_ID> --direction up --type parent-child --json
bv --robot-next --format json 2>/dev/null || br ready --json
```

Decision table:
- more ready tasks → loop
- all remaining tasks blocked → report blockers
- all tasks closed → complete
- a task failed → report and ask user
- context budget >65% → checkpoint and pause

### Completion

When all tasks under the epic are closed:

```bash
br dep list <EPIC_ID> --direction up --type parent-child --json
# Filter for .status != "closed"; should return empty
```

Then run project-specific build/tests.

#### Swarming Mode

Report completion to the orchestrator via Agent Mail and stop.

#### Single-Worker Mode

Update `.beads/STATE.md`:

```markdown
# Beo State
- Phase: executing → complete
- Feature: <epic-id> (<feature-name>)
- Tasks: <total> completed, <blocked> blocked, <failed> failed
- Next: beo-reviewing
```

## 9. Context-Budget Checkpoint

### Swarming Mode

Write a final report artifact for the current task and stop gracefully. The orchestrator will re-dispatch remaining work.

### Single-Worker Mode

1. finish updating the current task status
2. write `HANDOFF.json`
3. flush with `br sync --flush-only`
4. pause

Use the canonical base schema from `../../reference/references/state-and-handoff-protocol.md`, then add any executing-specific resume detail you need.
