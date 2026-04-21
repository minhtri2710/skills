# Execution Operations

Operational playbook for `beo-execute`.

## 1. Prerequisites

Verify approval and task existence:

```bash
br show <EPIC_ID> --json
br dep list <EPIC_ID> --direction up --type parent-child --json
```

Use `shared-hard-gates.md` for canonical approval verification.

Confirm planning-aware scope when relevant:
1. read `.beads/STATE.json` if present
2. read `phase-plan.md` if present
3. treat `phase-contract.md` and `story-map.md` as current-phase artifacts
4. do not assume current-phase execution means whole-feature completion in multi-phase work

## 2. Epic Claim

On first entry, if the epic is still `open`, claim it:

```bash
br update <EPIC_ID> --claim
```

## 3. Task Selection

Use the scheduling cascade from `dependency-and-scheduling.md`.

Rules:
- in swarm-worker mode, execute only the assigned bead
- still verify live readiness before starting
- in multi-phase work, select only current-phase beads
- if falling back from `bv --robot-plan`, post-filter to the active epic and current phase

## 4. Pre-Dispatch Checks

Check the task and dependencies:

```bash
br show <TASK_ID> --json
br dep list <TASK_ID> --direction down --type blocks --json
```

All blocking tasks must be in allowed terminal dependency states.

### Stale Label Cleanup

Remove only transient stale labels:

```bash
br label remove <TASK_ID> -l blocked 2>/dev/null
br label remove <TASK_ID> -l in_progress 2>/dev/null
br label remove <TASK_ID> -l dispatch_prepared 2>/dev/null
```

Do not auto-remove `debug_attempted`, `failed`, or `cancelled`.

### Description Verification

Read `br show <TASK_ID> --json` and verify `.description`:
- is non-empty and substantive
- includes file scope
- includes concrete verification criteria
- includes story context unless this is a reactive fix bead

If underspecified, do not dispatch. Route back to planning-aware flow.

### Decision-ID Cross-Reference

If the bead description references decision IDs (`D1`, `D2`, ...), verify each one exists in `CONTEXT.md` and that requested behavior does not contradict locked decisions.

If `CONTEXT.md` has no Locked Decisions table, skip D-ID verification and log that it was skipped.

### Current-Phase Scope Check

If `phase-plan.md` exists and the bead clearly belongs to a later phase:
1. do not execute it
2. route back through planning-aware flow
3. keep later-phase work deferred

## 5. Task Transition Protocol

### File Coordination Rule

If the dispatch contract says `agent-mail`, use reservation APIs and identity rules from `agent-mail-coordination.md`.
If it says `runtime-only`, do not call reservation APIs and stay strictly inside the declared file scope.

### Worker / Agent-Mail Mode

When the coordination surface is `agent-mail`, reserve the files the bead will touch. If reservation conflicts are returned:
1. do not edit through the conflict
2. send `[FILE CONFLICT]` via the swarm message templates
3. poll inbox until resolved

After bead close, release held paths when Agent Mail mode is active.

### Solo Mode

If Agent Mail is unavailable and execution is running in standalone solo mode:
1. do not attempt reservations
2. execute exactly one bead at a time
3. read current local changes before editing
4. if unrelated concurrent edits are present under `runtime-only`, stop and return `blocked` instead of guessing ownership
5. keep file scope narrow and explicit in the bead report

Once coordination is clear, transition the task:

```bash
br label add <TASK_ID> -l dispatch_prepared
br update <TASK_ID> --claim
br label remove <TASK_ID> -l dispatch_prepared
br label add <TASK_ID> -l in_progress
br audit record --kind tool_call --issue-id <TASK_ID> --tool-name "dispatch"
```

## 6. Worker Dispatch and Reporting

Use `worker-prompt-guide.md` for prompt assembly and truncation rules.

Include when relevant:
- planning mode
- current phase name or number
- current-phase exit state
- story context
- a note that later phases remain deferred in multi-phase work

In standalone dispatch, the worker prompt is the assignment package. If no worker-dispatch mechanism is available, implement directly in standalone mode.

Required worker return:
1. status: `done | blocked | failed | cancelled`
2. summary
3. blockers if any
4. learnings

## 7. Post-Worker Updates

### Status Mapping

Use `status-mapping.md` as the source of truth for task and feature status transitions.

### Git Commit Format

Recommended close-time commit format:

```text
<type>(<bead-id>): <one-line summary>
```

Use one logical commit per bead.

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
<tests added or modified, or 'No test changes'>

## Verification
<verification results>

## Learnings
<anything discovered>
---END_ARTIFACT---"
```

Then flush:

```bash
br sync --flush-only
```

### Bead Completion Validation

After every bead close:
1. verify `br show <BEAD_ID> --json` maps to canonical `done`
2. verify the completion report includes bead ID, files changed, tests changed, and verification result
3. release held file reservations when Agent Mail mode is active
4. send `[DONE]` through Agent Mail, or return the completion payload through the runtime result channel in `runtime-only` mode

Re-check the graph with `bv --robot-plan --graph-root <EPIC_ID> --format json`:
- after every 5 beads per worker in swarm mode
- after every bead close in solo mode

## 8. Progress Check and Completion

Run:

```bash
br dep list <EPIC_ID> --direction up --type parent-child --json
bv --robot-next --format json 2>/dev/null || br ready --json
```

| Condition | Action |
| --- | --- |
| more ready current-phase tasks | loop |
| all remaining tasks blocked | report blockers |
| all current-phase tasks `done` or accepted-cancelled | complete current phase |
| any current-phase task `failed` | write `needs-debugging` and hand off to `beo-route` |
| any current-phase task `cancelled` without `cancelled_accepted` | write `cancelled-needs-decision` and hand off to `beo-route` |
| context budget >65% | checkpoint and pause |

### Completion

Before writing completion state:
1. no current-phase tasks may be `failed`
2. no current-phase tasks may be `cancelled` without `cancelled_accepted`

Then run project-specific build and tests.

#### Swarming Mode

Report completion to the orchestrator and stop.

#### Single-Worker Mode

Update `.beads/STATE.json` and route:
- `beo-review` when single-phase execution scope is complete
- `beo-plan` when multi-phase work has later phases remaining; remove `approved` first with `br label remove <EPIC_ID> -l approved`
- `beo-review` when multi-phase work just finished its final phase

## 9. Context-Budget Checkpoint

### Swarming Mode

Write the current report artifact and stop gracefully. The orchestrator will re-dispatch remaining work.

### Single-Worker Mode

1. finish the current task-status update
2. write `HANDOFF.json`
3. flush with `br sync --flush-only`
4. pause

Use the canonical schema from `state-and-handoff-protocol.md`. Include planning-aware fields and whether current-phase execution is complete or still has non-terminal work.
