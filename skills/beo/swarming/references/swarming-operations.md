# Swarming Operations

Operational playbook for `beo-swarming`.

## Table of Contents

- [1. Confirm Swarm Readiness](#1-confirm-swarm-readiness)
- [2. Initialize Agent Mail](#2-initialize-agent-mail)
- [3. Spawn Workers](#3-spawn-workers)
- [4. Monitor and Tend](#4-monitor-and-tend)
- [5. Swarm Completion](#5-swarm-completion)
- [6. Context-Budget Checkpoint](#6-context-budget-checkpoint)

## 1. Confirm Swarm Readiness

Prerequisites:
- beads are `open` and approved for execution
- `EPIC_ID` is known
- Agent Mail server is reachable

If Agent Mail is unavailable, degrade to single-worker mode and route to `beo-executing`.

Also verify planning-aware scope:
- read `.beads/STATE.json` when present
- read `phase-plan.md` when present
- confirm the swarm will execute the **current phase** only

### Readiness Steps

1. Get `EPIC_ID` from `.beads/STATE.json` or user input.
2. Read `.beads/STATE.json` and current-phase artifacts if scope is unclear.
3. Inspect the live graph:

```bash
bv --robot-triage --graph-root <EPIC_ID> --format json
```

4. Verify executable work exists, dependencies are acyclic, and no unresolved validation blockers remain.
5. Update `.beads/STATE.json` with current swarm intent and epic ID.
6. Claim the epic if not already in progress:

```bash
br update <EPIC_ID> --claim
```

### Scheduling Cascade

Use `../../reference/references/dependency-and-scheduling.md` § Scheduling Cascade. Use the highest-available tier. Do not invent separate runtime planning artifacts. If the graph and Agent Mail disagree about readiness, pause spawning and reconcile before adding workers.

## 2. Initialize Agent Mail

1. Register the coordinator and bootstrap the epic thread using `ensure_project` and `register_agent` from `../../reference/references/agent-mail-coordination.md`.
2. Apply file-reservation discipline from `../../reference/references/worker-template.md` to every worker contract.
3. Create the first thread message using `message-templates.md`.

### Dual-Identity Contract

Each worker has:

| Identity | Source | Use |
| --- | --- | --- |
| Nickname | coordinator-assigned | Human-readable worker label |
| Agent Mail | `macro_start_session` | `sender_name` after first message |

Workers post both in `[ONLINE]` as `Nickname: <X> | Agent Mail: <Y>`. See `../../reference/references/worker-template.md` for the full startup sequence.

### Cycle Definition

A `cycle` is one complete monitor-and-tend iteration:
- fetch mail for all workers
- run graph oversight
- tend events
- check progress

Measure silence thresholds here and in `message-templates.md` in cycles, not wall-clock time.

## 3. Spawn Workers

Spawn worker subagents in parallel using the canonical worker contract. Default max workers = `min(independent ready tasks, 5)`. Override only with explicit user approval.

Each worker must receive:
- Agent Mail identity
- epic ID / feature name
- planning mode and current phase context when known
- instruction to load `beo-executing`
- optional startup hint (clearly marked as a hint)
- scoped task context by default

Do not assign fixed tracks or fixed bead lists in the normal case. Workers should self-route from the live graph.

### Worker startup acknowledgment

A worker startup is valid when `[ONLINE]` arrives with both nickname and Agent Mail identity. See `../../reference/references/worker-template.md` for the full startup sequence.

Recovery ladder:
1. After 2 cycles without `[ONLINE]`, send `[STARTUP REMINDER]`.
2. After 3 cycles, send `[STATUS CHECK]`.
3. After 5 cycles, escalate to the user and consider respawn.

Mark active workers in `.beads/STATE.json`.

## 4. Monitor and Tend

Check Agent Mail on the epic thread and use live graph checks for oversight.

### Fetch Mail

```text
fetch_inbox(
  project_key="<project-root-path>",
  agent_name="<COORDINATOR_AGENT_NAME>"
)
```

### Graph Oversight

```bash
bv --robot-triage --graph-root <EPIC_ID> --format json
```

### Tend These Event Types

- worker startup acknowledgments
- bead completion reports
- blocker alerts
- file conflict requests
- reservation conflict detections
- overseer broadcasts

For reservation conflicts, read returned `file_reservation_paths(...)` conflict data using `../../reference/references/agent-mail-coordination.md`, then choose:

| Option | Action |
| --- | --- |
| Release | Ask the current holder to release at the next safe checkpoint |
| Reassign | Reassign the bead |
| Defer | Defer the work into a follow-up bead |

Send the decision with `[FILE CONFLICT RESOLUTION]` via `reply_message`.

### Silence Escalation Protocol

Treat silence deterministically:

| Quiet cycles | Action |
| --- | --- |
| 2 | Send `[STARTUP REMINDER]` if `[ONLINE]` was never received; otherwise send `[STATUS CHECK]` |
| 3 | Send a direct status query |
| 5 | Escalate to the user with worker identity and last known state |

### Progress Check Heuristics

After each completion:

| Condition | Action |
| --- | --- |
| >50% beads open | Continue normally |
| <50% beads open | Consider reducing workers |
| All current-phase beads closed | Complete swarm |
| No progress for 3+ cycles | Diagnose mail, reservations, or worker health |

If coordination overhead starts exceeding useful progress, stop expanding the swarm and degrade the remainder to `beo-executing`.

## 5. Swarm Completion

When no beads remain `in_progress` and no executable current-phase work remains:

1. Verify the graph:

```bash
bv --robot-triage --graph-root <EPIC_ID> --format json
```

2. If orphaned or blocked beads remain, report them and get user direction.
3. If all current-phase beads are closed, run final build/test commands.
4. Choose the next route:
   - `beo-reviewing` if this was the final execution scope
   - remove `approved` first (`br label remove <EPIC_ID> -l approved`), then `beo-planning` if `planning_mode = multi-phase` and later phases remain
5. Update `.beads/STATE.json`, clear active workers, run `br sync --flush-only`, and send the completion message using `message-templates.md`:
   - set `"status"` to `"phase-complete-needs-replan"` when later phases remain, or `"ready-to-review"` when this was the final scope
   - set `"next"` to the chosen route

## 6. Context-Budget Checkpoint

If context usage exceeds 65%:
1. Write `.beads/HANDOFF.json` using the canonical base fields from `../../reference/references/state-and-handoff-protocol.md`.
2. Include swarming-specific extension fields (`session`, `swarm`, `graph_status`, `active_workers`, `open_blockers`, `resume_instructions`, `context_at_pause`).
3. Include planning-aware fields per `../../reference/references/state-and-handoff-protocol.md` § Planning-Aware HANDOFF.json Extension Fields when relevant.
4. Broadcast a pause notification on the epic thread.
5. Report to the user how to resume.
