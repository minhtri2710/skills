# Swarming Operations

Detailed operational playbook for `beo-swarming`. Load this file when you need exact swarm readiness checks, Agent Mail setup, worker spawning flow, monitoring heuristics, or completion/checkpoint mechanics.

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

1. get `EPIC_ID` from `.beads/STATE.json` or user input
2. read `.beads/STATE.json` and current-phase artifacts if scope is unclear
3. inspect the live graph:

```bash
bv --robot-triage --graph-root <EPIC_ID> --format json
```

4. verify executable work exists, dependencies are acyclic, and no unresolved validation blockers remain
5. update `.beads/STATE.json` with current swarm intent and epic ID
6. claim the epic if not already in progress:

```bash
br update <EPIC_ID> --claim
```

### Scheduling Cascade

```bash
bv --robot-plan --graph-root <EPIC_ID> --format json 2>/dev/null || bv --robot-next --format json 2>/dev/null || br ready --json
```

Use the highest-available tier. Do not invent separate runtime planning artifacts.
If the graph and Agent Mail disagree about what is ready, pause spawning and reconcile before adding more workers.

## 2. Initialize Agent Mail

Register the coordinator and bootstrap the epic thread.

Canonical setup shape:

```text
ensure_project(human_key="<project-root-path>")
register_agent(
  project_key="<project-root-path>",
  name="<COORDINATOR_AGENT_NAME>",
  program="<runtime-program>",
  model="<MODEL>",
  task_description="swarm-coordinator"
)
```

Use `../../reference/references/agent-mail-coordination.md` as the canonical source for reservation signatures and identity rules.

Each worker contract inherits file-reservation discipline from `../../reference/references/worker-template.md`.

Then create the first thread message using the templates in `message-templates.md`.

### Dual-Identity Contract

Each worker has a coordinator-assigned nickname and an Agent Mail name from `macro_start_session`. Workers post both in their `[ONLINE]` message as `Nickname: <X> | Agent Mail: <Y>`. After first message, `sender_name` carries the Agent Mail identity. See `../../reference/references/worker-template.md` for the full worker startup sequence.

### Cycle Definition

A `cycle` is one complete iteration of the coordinator's monitor-and-tend loop:
- fetch mail for all workers
- run graph oversight
- tend events
- check progress

Silence thresholds in this document and in `message-templates.md` are measured in cycles, not wall-clock time.

## 3. Spawn Workers

Spawn a pool of worker subagents in parallel using the canonical worker contract.

Default max workers = `min(independent ready tasks, 5)`. Override this bound only with explicit user approval.

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
- after 2 cycles without `[ONLINE]`, send `[STARTUP REMINDER]`
- after 3 cycles, send `[STATUS CHECK]`
- after 5 cycles, escalate to the user and consider respawn

Mark active workers in `.beads/STATE.json`.

## 4. Monitor and Tend

Check Agent Mail regularly on the epic thread and use live graph checks for oversight.

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

For reservation conflicts, read the returned `file_reservation_paths(...)` conflict data using `../../reference/references/agent-mail-coordination.md` and decide whether to:
- ask the current holder to release at the next safe checkpoint
- reassign the bead
- defer the work into a follow-up bead

Send the decision with `[FILE CONFLICT RESOLUTION]` via `reply_message`.

### Silence Escalation Protocol

Treat silence deterministically:
- 2 quiet cycles from a worker -> send `[STARTUP REMINDER]` if `[ONLINE]` was never received, otherwise send `[STATUS CHECK]`
- 3 quiet cycles -> send a direct status query
- 5 quiet cycles -> escalate to the user with the worker identity and last known state

### Progress Check Heuristics

After each completion:
- >50% beads open → continue normally
- <50% beads open → consider reducing workers
- all current-phase beads closed → complete swarm
- no progress for 3+ cycles → diagnose mail, reservations, or worker health

If coordination overhead starts exceeding useful progress, stop expanding the swarm and degrade the remainder to `beo-executing`.

## 5. Swarm Completion

When no beads remain `in_progress` and no executable current-phase work remains:

1. verify the graph:

```bash
bv --robot-triage --graph-root <EPIC_ID> --format json
```

2. if orphaned/blocked beads remain, report them and get user direction
3. if all current-phase beads are closed:
   - run final build/test commands
   - choose the next route:
     - `beo-reviewing` if this was the final execution scope
     - remove `approved` label first (`br label remove <EPIC_ID> -l approved`), then `beo-planning` if `planning_mode = multi-phase` and later phases remain
   - update `.beads/STATE.json`: set `"status"` to `"phase-complete-needs-replan"` when later phases remain, or `"ready-to-review"` when this was the final scope; set `"next"` to the chosen route
   - clear active workers
4. run `br sync --flush-only` to export mutations to JSONL before committing to git
5. send the completion message on Agent Mail using `message-templates.md`

## 6. Context-Budget Checkpoint

If context usage exceeds 65%:
- write `.beads/HANDOFF.json` using the canonical base fields from `../../reference/references/state-and-handoff-protocol.md`
- include swarming-specific extension fields (`session`, `swarm`, `graph_status`, `active_workers`, `open_blockers`, `resume_instructions`, `context_at_pause`)
- include planning-aware fields when relevant (`planning_mode`, `has_phase_plan`, `current_phase`, `total_phases`, `phase_name`)
- broadcast a pause notification on the epic thread
- report to the user how to resume
