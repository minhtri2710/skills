# Execution Operations

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

See `beo-reference` → `references/shared-hard-gates.md` § Approval Verification for the canonical approval check and routing rules.

Confirm planning-aware scope when relevant:

1. Read `.beads/STATE.json` if present.
2. Read `phase-plan.md` if present.
3. Treat `phase-contract.md` and `story-map.md` as the **current phase** artifacts.
4. Do not assume current-phase execution implies whole-feature completion when `planning_mode = multi-phase`.

## 2. Epic Claim

On first entry, if the epic is still `open`, transition it to `in_progress`:

```bash
br update <EPIC_ID> --claim
```

See `beo-reference` → `references/pipeline-contracts.md` → Epic Lifecycle.

## 3. Task Selection

Use the scheduling cascade from `beo-reference` → `references/dependency-and-scheduling.md` § Scheduling Cascade.

Pick the top executable bead from the first available track. In swarm-worker mode, execute only the assigned bead, but still verify against the live graph before starting.

For multi-phase work, select only beads that belong to the **current phase**.

Fallback-scoping rule:

1. `bv --robot-plan --graph-root <EPIC_ID>` is authoritative when available.
2. If falling back to `bv --robot-next` or `br ready`, post-filter results to beads that belong to the active epic and current phase before selecting work.

## 4. Pre-Dispatch Checks

### Check the Task and Dependencies

```bash
# Check the task is still open
br show <TASK_ID> --json

# Verify dependencies are satisfied
br dep list <TASK_ID> --direction down --type blocks --json
```

All blocking tasks must be done or otherwise in an allowed terminal dependency state per the canonical graph rules.

### Stale Label Cleanup

Remove only transient stale labels before dispatch. See `pipeline-contracts.md` Label Lifecycle for canonical label definitions.

```bash
br label remove <TASK_ID> -l blocked 2>/dev/null
br label remove <TASK_ID> -l in_progress 2>/dev/null
br label remove <TASK_ID> -l dispatch_prepared 2>/dev/null
```

Do **not** remove `debug_attempted`. It is routing-significant history, not stale execution state. Do **not** auto-remove `failed` or `cancelled`; those are real terminal states and require an explicit routing decision.

### Description Verification

Read `br show <TASK_ID> --json` and verify `.description` is:

1. non-empty and substantive
2. includes file scope
3. includes concrete verification criteria
4. includes story context unless this is a reactive fix bead

If empty or underspecified, do not dispatch. Route back to `beo-plan` or `beo-validate`.

### Decision-ID Cross-Reference

Scan the bead description for D-ID markers (`D1`, `D2`, ...) and verify each one exists in the Locked Decisions table in `.beads/artifacts/<feature_slug>/CONTEXT.md`.

Flag either mismatch:

1. a D-ID is referenced in the bead but missing from `CONTEXT.md`
2. the bead's requested behavior contradicts a locked decision in `CONTEXT.md`

If a mismatch is found, stop execution and route back through the canonical planning back-edge so the conflict is resolved before dispatch. Do not patch the mismatch inside execute.

Fallback for legacy features:

1. If `CONTEXT.md` has no Locked Decisions table, skip D-ID verification.
2. Log `No Locked Decisions table found — D-ID verification skipped.`

### Current-Phase Scope Check

Before execution, confirm the bead belongs to the currently approved phase.

If `phase-plan.md` exists and the bead clearly belongs to a later phase:

1. Do not execute it.
2. Route back to planning-aware flow.
3. Keep later-phase work deferred until the next planning cycle.

## 5. Task Transition Protocol

### File Coordination Rule

If the dispatch contract says `Coordination surface: agent-mail`, use the canonical reservation signatures and identity rules from `beo-reference` → `references/agent-mail-coordination.md`.
If the dispatch contract says `Coordination surface: runtime-only`, skip Agent Mail reservations and stay strictly inside the declared file scope.

### Worker / Agent-Mail mode

When the coordination surface is `agent-mail`, reserve the files the bead will touch using the `file_reservation_paths` API from the canonical reference above.
When the coordination surface is `runtime-only`, do not call reservation APIs; if the file scope is insufficient or uncertain, stop and report `blocked` through the runtime result channel.

If Agent Mail `conflicts` are returned:

1. Do not edit through the conflict.
2. Send a `[FILE CONFLICT]` message to the coordinator using `beo-swarm` → `references/message-templates.md`.
3. Poll inbox until the coordinator resolves the conflict.

After bead close, release held paths using the `release_file_reservations` API from the same reference when the coordination surface is `agent-mail`.

`[FILE CONFLICT]` and `[FILE CONFLICT RESOLUTION]` messages remain the coordination layer above the reservation API.


### Solo mode (no Agent Mail)

If Agent Mail / reservation APIs are unavailable and execution is running in standalone solo mode:

1. Do not attempt reservations.
2. Do not assume any parallel beo workers exist.
3. Execute exactly one bead at a time.
4. Read current local changes before editing. If unrelated concurrent edits are present and the coordination surface is `runtime-only`, stop and return `blocked` through the runtime result channel instead of guessing ownership. Only direct user-facing standalone execution should pause and ask the user.
5. Keep file scope narrow and explicit in the bead report.

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

Include, when relevant:

1. planning mode
2. current phase name / number
3. current-phase exit state
4. current story context
5. a note that later phases remain deferred if the feature is multi-phase

### Standalone Dispatch

Use the session's standard worker-launch or task-execution mechanism. Required payload:

1. implementation-focused task title or description
2. assembled worker prompt
3. worker type capable of implementation
4. blocking wait for the result before post-worker updates

In standalone dispatch, the worker prompt itself is the assignment package. Use the `Dispatch Contract` section from `worker-prompt-guide.md` so the prompt explicitly declares standalone dispatch, the coordination surface, the target bead, and the file scope. If the coordination surface is `runtime-only`, do not make the worker wait for Agent Mail setup or a later Agent Mail assignment.

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

1. status: `done | blocked | failed | cancelled`
2. summary
3. blockers (if any)
4. learnings

## 7. Post-Worker Updates

### Status Mapping

Task and feature status values follow `status-mapping.md`. See `beo-reference` for the authoritative state machines and the `br` command sequences for each worker report.

### Git Commit Format

Recommended commit format:

```text
<type>(<bead-id>): <one-line summary>
```

Use the type that best matches the bead work:

| Type | Use |
| --- | --- |
| `feat` | new functionality |
| `fix` | bug fixes |
| `refactor` | restructuring |
| `docs` | documentation |
| `test` | test-only changes |
| `chore` | config or tooling work |


This format is a strong recommendation, not a hard gate.
Use one logical commit per bead at close time. Multi-file beads should still produce a single atomic commit.

Example:

```text
feat(pe-jju.3): add retry logic to webhook handler
```

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

1. Verify `br show <BEAD_ID> --json` maps to canonical status `done` (backed by `br` status `closed`).
2. Verify the completion report includes bead ID, files changed, tests added or modified, and verification result.
3. Release all held file reservations with `release_file_reservations(project_key, resolved_agent_mail_name, paths=[...])` when Agent Mail mode is active.
4. If the coordination surface is `agent-mail`, send the `[DONE]` Agent Mail report with the full completion summary. If the coordination surface is `runtime-only`, return the completion payload through the runtime result channel instead.
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

| Condition | Action |
| --- | --- |
| more ready current-phase tasks | loop |
| all remaining tasks blocked | report blockers |
| all current-phase tasks `done` (or `done` + `cancelled` with `cancelled_accepted` label) | complete current phase |
| any current-phase task `failed` | **stop** — write `"needs-debugging"` to STATE.json `status` field, hand off to `beo-route` |
| any current-phase task `cancelled` without `cancelled_accepted` label | **stop** — write `"cancelled-needs-decision"` to STATE.json `status` field, hand off to `beo-route` |
| context budget >65% | checkpoint and pause |

### Completion

When all current-phase tasks under the epic are in terminal states, evaluate completion readiness:

```bash
br dep list <EPIC_ID> --direction up --type parent-child --json
# Filter for any current-phase task not in a canonical terminal state; should return empty for the current-phase execution scope
```

**Pre-completion gate.** Before writing the completion STATE.json, verify:
1. No current-phase tasks are `failed`. If any are, write `status: "needs-debugging"` and hand off to `beo-route` instead of completing.
2. No current-phase tasks are `cancelled` without the `cancelled_accepted` label. If any are, write `status: "cancelled-needs-decision"` and hand off to `beo-route` instead of completing.

Only proceed to completion when all current-phase tasks are `done`, or a mix of `done` and `cancelled` where every cancelled task has the `cancelled_accepted` label.

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
  "next": "<beo-review | beo-plan>",
  "planning_mode": "<single-phase | multi-phase>",
  "has_phase_plan": false,
  "current_phase": 1,
  "total_phases": 1,
  "phase_name": "<phase name from phase-contract.md>"
}
```

Routing rule:

| Condition | Route |
| --- | --- |
| `planning_mode = single-phase` and execution scope is complete | `beo-review` |
| `planning_mode = multi-phase` and later phases remain | remove `approved` label first (`br label remove <EPIC_ID> -l approved`), then route to `beo-plan` |
| `planning_mode = multi-phase` and this was the final phase | `beo-review` |

## 9. Context-Budget Checkpoint

### Swarming Mode

Write a final report artifact for the current task and stop gracefully. The orchestrator will re-dispatch remaining work.

### Single-Worker Mode

1. Finish updating the current task status.
2. Write `HANDOFF.json`.
3. Flush with `br sync --flush-only`.
4. Pause.

Use the canonical base schema from `beo-reference` → `references/state-and-handoff-protocol.md`, then add any executing-specific resume detail you need.

When relevant, include the planning-aware fields from `beo-reference` → `references/state-and-handoff-protocol.md` § Planning-Aware HANDOFF.json Extension Fields.
1. whether current-phase execution is complete or still has non-terminal work
