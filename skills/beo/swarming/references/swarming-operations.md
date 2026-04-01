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
- read `.beads/STATE.md` when present
- read `phase-plan.md` when present
- confirm the swarm will execute the **current phase** only

Default readiness loop:
1. confirm current-phase execution is approved
2. confirm 3+ independent ready tracks exist
3. confirm Agent Mail is healthy enough to coordinate
4. claim the epic if needed
5. only then spawn workers

### Readiness Steps

1. get `EPIC_ID` from `.beads/STATE.md` or user input
2. read `.beads/STATE.md` and current-phase artifacts if scope is unclear
3. inspect the live graph:

```bash
bv --robot-triage --graph-root <EPIC_ID> --format json
```

3. verify executable work exists, dependencies are acyclic, and no unresolved validation blockers remain
4. update `.beads/STATE.md` with current swarm intent and epic ID
5. claim the epic if not already in progress:

```bash
br update <EPIC_ID> --claim
```

### Scheduling Cascade

```bash
bv --robot-plan --graph-root <EPIC_ID> --format json 2>/dev/null
|| bv --robot-next --format json 2>/dev/null
|| br ready --json 2>/dev/null
|| br list --status open --json
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
  program="codex-cli",
  model="gpt-5",
  task_description="swarm-coordinator"
)
```

Set:

```text
EPIC_TOPIC="epic-<EPIC_ID>"
```

Then create the first thread message using the templates in `message-templates.md`.

## 3. Spawn Workers

Spawn a pool of worker subagents in parallel using the canonical worker contract.

Each worker must receive:
- Agent Mail identity
- epic ID / feature name
- planning mode and current phase context when known
- instruction to load `beo-executing`
- optional startup hint (clearly marked as a hint)
- scoped task context by default

Do not assign fixed tracks or fixed bead lists in the normal case. Workers should self-route from the live graph.

### Worker startup acknowledgment

A worker startup acknowledgment should confirm:
- the worker is online
- it joined the correct epic thread
- it loaded `beo-executing`
- it understands the current execution scope is the current phase only

Mark active workers in `.beads/STATE.md`.

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
- overseer broadcasts

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
     - `beo-planning` if `planning_mode = multi-phase` and later phases remain
   - update `.beads/STATE.md` with phase complete and next skill
   - clear active workers
4. send the completion message on Agent Mail using `message-templates.md`

## 6. Context-Budget Checkpoint

If context usage exceeds 65%:
- write `.beads/HANDOFF.json` using the canonical base fields from `../../reference/references/state-and-handoff-protocol.md`
- include swarming-specific extension fields (`session`, `swarm`, `graph_status`, `active_workers`, `open_blockers`, `resume_instructions`, `context_at_pause`)
- include planning-aware fields when relevant (`planning_mode`, `has_phase_plan`, `current_phase`, `total_phases`, `phase_name`)
- broadcast a pause notification on the epic thread
- report to the user how to resume
