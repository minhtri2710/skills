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

See `../../reference/references/shared-hard-gates.md` § Approval Verification for the canonical approval check and routing rules.

Also confirm planning-aware scope when relevant:

- read `.beads/STATE.json` if present
- read `phase-plan.md` if present
- treat `phase-contract.md` and `story-map.md` as the **current phase** artifacts
- do not assume current-phase execution implies whole-feature completion when `planning_mode = multi-phase`

## 2. Epic Claim

On first entry, if the epic is still `open`, transition it to `in_progress`:

```bash
br update <EPIC_ID> --claim
```

See `../../reference/references/pipeline-contracts.md` → Epic Lifecycle.

## 3. Task Selection

Use the scheduling cascade from `../../reference/references/dependency-and-scheduling.md` § Scheduling Cascade.

Pick the top executable bead from the first available track. If dispatched by swarming, respect any startup hint but always verify against the live graph.

For multi-phase work, select only beads that belong to the **current phase**.

Fallback-scoping rule:
- `bv --robot-plan --graph-root <EPIC_ID>` is authoritative when available
- if falling back to `bv --robot-next` or `br ready`, post-filter results to beads that belong to the active epic and current phase before selecting work

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

Remove stale labels before dispatch. See `pipeline-contracts.md` Label Lifecycle for the canonical label definitions.

```bash
br label remove <TASK_ID> -l blocked 2>/dev/null
br label remove <TASK_ID> -l failed 2>/dev/null
br label remove <TASK_ID> -l in_progress 2>/dev/null
br label remove <TASK_ID> -l partial 2>/dev/null
br label remove <TASK_ID> -l cancelled 2>/dev/null
br label remove <TASK_ID> -l dispatch_prepared 2>/dev/null
```

Do **not** remove `debug_attempted`. It is routing-significant history, not stale execution state.

### Description Verification

Read `br show <TASK_ID> --json` and verify `.description` is:
- non-empty and substantive
- includes file scope
- includes concrete verification criteria
- includes story context unless this is a reactive fix bead

If empty or underspecified, do not dispatch. Route back to `beo-planning` or `beo-validating`.

### Decision-ID Cross-Reference

Scan the bead description for D-ID markers (`D1`, `D2`, ...) and verify each one exists in the Locked Decisions table in `.beads/artifacts/<feature_slug>/CONTEXT.md`.

Flag any of these mismatches:
- a D-ID is referenced in the bead but missing from `CONTEXT.md`
- the bead's requested behavior contradicts a locked decision in `CONTEXT.md`

If a mismatch is found, stop execution and route to `beo-exploring` to resolve the decision conflict before dispatch.

Fallback for legacy features:
- if `CONTEXT.md` has no Locked Decisions table, skip D-ID verification and log the warning `No Locked Decisions table found — D-ID verification skipped.`

### Current-Phase Scope Check

Before execution, confirm the bead belongs to the currently approved phase.

If `phase-plan.md` exists and the bead clearly belongs to a later phase:
- do not execute it
- route back to planning-aware flow
- keep later-phase work deferred until the next planning cycle

## 5. Task Transition Protocol

### File Coordination Rule

Use the canonical reservation signatures and identity rules from `../../reference/references/agent-mail-coordination.md`.

### Worker / Agent-Mail mode

Before implementation, reserve the files the bead will touch using the `file_reservation_paths` API from the canonical reference above.

If `conflicts` are returned:
- do not edit through the conflict
- send a `[FILE CONFLICT]` message to the coordinator using `../../swarming/references/message-templates.md`
- poll inbox until the coordinator resolves the conflict

After bead close, release held paths using the `release_file_reservations` API from the same reference.

`[FILE CONFLICT]` and `[FILE CONFLICT RESOLUTION]` messages remain the coordination layer above the reservation API.


### Solo mode (no Agent Mail)

If Agent Mail / reservation APIs are unavailable and execution is running in standalone solo mode:
- do not attempt reservations
- do not assume any parallel beo workers exist
- execute exactly one bead at a time
- read current local changes before editing, and if unrelated concurrent edits are present, pause and ask the user instead of guessing ownership
- still keep file scope narrow and explicit in the bead report

Once file coordination is clear, transition the task:

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

The worker prompt should include, when relevant:
- planning mode
- current phase name / number
- current-phase exit state
- current story context
- a note that later phases remain deferred if the feature is multi-phase

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

> Task and feature status values follow `status-mapping.md`. See `beo-reference` for the authoritative state machines and the `br` command sequences for each worker report.

### Git Commit Format

Recommended commit format:

```text
<type>(<bead-id>): <one-line summary>
```

Use the type that best matches the bead work:
- `feat` for new functionality
- `fix` for bug fixes
- `refactor` for restructuring
- `docs` for documentation
- `test` for test-only changes
- `chore` for config or tooling work

Use one logical commit per bead at close time. Multi-file beads should still produce a single atomic commit.

Example:

```text
feat(pe-jju.3): add retry logic to webhook handler
```

This format is a strong recommendation, not a hard gate.

### Write the Report Artifact

```bash
br comments add <TASK_ID> --no-daemon --message "---ARTIFACT:report:v1---
## Bead
<TASK_ID>

## Summary
<worker summary>

## Changes Made
<list of files modified>

## Tests
<tests added or modified, or 'No test changes' if none>

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

### Bead Completion Validation

After every bead close, run this validation sequence:

1. Verify `br show <BEAD_ID> --json` reports status `closed`.
2. Verify the completion report includes bead ID, files changed, tests added or modified, and verification result.
3. Release all held file reservations with `release_file_reservations(project_key, agent_name, paths=[...])` when Agent Mail mode is active.
4. Send the `[DONE]` Agent Mail report with the full completion summary.
5. Re-check the graph with `bv --robot-plan --graph-root <EPIC_ID> --format json` to confirm no orphaned dependencies.

Frequency rules:
- Steps 1-4 run after every bead close.
- Step 5 runs after every 5 beads per worker in swarm mode.
- In solo mode, step 5 runs after every bead close.

## 8. Progress Check and Completion

### Progress Check

```bash
br dep list <EPIC_ID> --direction up --type parent-child --json
bv --robot-next --format json 2>/dev/null || br ready --json
```

Decision table:
- more ready current-phase tasks → loop
- all remaining tasks blocked → report blockers
- all current-phase tasks closed → complete current phase
- a task failed → report and ask user
- context budget >65% → checkpoint and pause

### Completion

When all current-phase tasks under the epic are in canonical terminal states (`done`, `cancelled`, or `failed`):

```bash
br dep list <EPIC_ID> --direction up --type parent-child --json
# Filter for any current-phase task not in a canonical terminal state; should return empty for the current-phase execution scope
```

Then run project-specific build/tests.

#### Swarming Mode

Report completion to the orchestrator via Agent Mail and stop.

#### Single-Worker Mode

Update `.beads/STATE.json`:

```json
{
  "schema_version": 1,
  "phase": "executing",
  "status": "<ready-to-review | phase-complete-needs-replan>",
  "feature": "<epic-id>",
  "feature_slug": "<feature_slug>",
  "tasks": "<total> completed, <blocked> blocked, <failed> failed",
  "next": "<beo-reviewing | beo-planning>",
  "planning_mode": "<single-phase | multi-phase>",
  "has_phase_plan": false,
  "current_phase": 1,
  "total_phases": 1,
  "phase_name": "<name>"
}
```

Routing rule:
- if `planning_mode = single-phase` and execution scope is complete → `beo-reviewing`
- if `planning_mode = multi-phase` and later phases remain → remove `approved` label first (`br label remove <EPIC_ID> -l approved`), then route to `beo-planning`
- if `planning_mode = multi-phase` and this was the final phase → `beo-reviewing`

## 9. Context-Budget Checkpoint

### Swarming Mode

Write a final report artifact for the current task and stop gracefully. The orchestrator will re-dispatch remaining work.

### Single-Worker Mode

1. finish updating the current task status
2. write `HANDOFF.json`
3. flush with `br sync --flush-only`
4. pause

Use the canonical base schema from `../../reference/references/state-and-handoff-protocol.md`, then add any executing-specific resume detail you need.

When relevant, include the planning-aware fields from `../../reference/references/state-and-handoff-protocol.md` § Planning-Aware HANDOFF.json Extension Fields.
- whether current-phase execution is complete or partially complete
