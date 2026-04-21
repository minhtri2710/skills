# Swarming Operations

Operational playbook for `beo-swarm`.

## 1. Confirm Swarm Readiness

Prerequisites:
- beads are open and approved for execution
- `EPIC_ID` is known
- Agent Mail is reachable

If Agent Mail is unavailable, degrade to single-worker mode and route to `beo-execute`.

Also verify planning-aware scope:
- read `.beads/STATE.json` when present
- read `phase-plan.md` when present
- confirm the swarm will execute the current phase only

Readiness steps:
1. get `EPIC_ID`
2. read `.beads/STATE.json` and current-phase artifacts if scope is unclear
3. inspect the live graph:

```bash
bv --robot-triage --graph-root <EPIC_ID> --format json
```

4. verify executable work exists, dependencies are acyclic, and no validation blockers remain
5. update `.beads/STATE.json` with swarm intent and epic ID
6. claim the epic if needed:

```bash
br update <EPIC_ID> --claim
```

7. add the `swarming` label:

```bash
br label add <EPIC_ID> -l swarming
```

Use the scheduling cascade from `dependency-and-scheduling.md`. If graph state and Agent Mail disagree about readiness, pause spawning and reconcile first.

## 2. Initialize Agent Mail

1. register the coordinator and bootstrap the epic thread using `agent-mail-coordination.md`
2. apply file-reservation discipline from `worker-template.md` to every worker contract
3. create the first thread message using `message-templates.md`

### Dual-Identity Contract

Each worker has:
- a coordinator-assigned nickname for humans
- an Agent Mail identity from `macro_start_session`

Workers post both in `[ONLINE]` as `Nickname: <X> | Agent Mail: <Y>`.

### Cycle Definition

A `cycle` is one full monitor-and-tend pass:
- fetch mail for all workers
- run graph oversight
- tend events
- check progress

Measure silence in cycles, not wall-clock time.

## 3. Spawn Workers

Launch workers in parallel using the runtime worker-orchestration mechanism and the canonical worker contract.

If worker spawning is unavailable or unauthorized:
1. remove `swarming`
2. degrade to `beo-execute`

Default max workers: `min(independent ready tasks, 5)`. Override only with explicit user approval.

Each worker must receive:
- Agent Mail identity
- epic ID or feature name
- planning mode and current phase context when known
- instruction to load `beo-execute`
- optional startup hint marked as non-authoritative
- scoped task context by default

Coordinator assignment flow:
1. identify ready beads from the live graph
2. assign exactly one bead per worker via Agent Mail
3. require readiness confirmation against live graph and file scope
4. require the worker to execute that bead only
5. require completion or failure reporting via Agent Mail

### Worker Startup Acknowledgment

A worker startup is valid only after `[ONLINE]` arrives with both nickname and Agent Mail identity. Then send the bead assignment and wait for readiness confirmation.

Recovery ladder:
1. after 2 cycles without `[ONLINE]`, send `[STARTUP REMINDER]`
2. after 3 cycles, send `[STATUS CHECK]`
3. after 5 cycles, escalate to the user and consider respawn

Record active workers in `.beads/STATE.json`.

## 4. Monitor and Tend

Fetch coordinator mail:

```text
fetch_inbox(
  project_key="<project-root-path>",
  agent_name="<COORDINATOR_AGENT_NAME>"
)
```

Run graph oversight:

```bash
bv --robot-triage --graph-root <EPIC_ID> --format json
```

Tend these event types:
- worker startup acknowledgments
- completion reports
- blocker alerts
- file conflict requests
- reservation conflicts
- coordinator broadcasts

For reservation conflicts, choose:
- release
- reassign
- defer

Send the decision with `[FILE CONFLICT RESOLUTION]` via `reply_message`.

### Silence Escalation Protocol

| Quiet cycles | Action |
| --- | --- |
| 2 | `[STARTUP REMINDER]` if `[ONLINE]` never arrived; otherwise `[STATUS CHECK]` |
| 3 | direct status query |
| 5 | escalate to user with worker identity and last known state |

### Progress Check Heuristics

After each completion:

| Condition | Action |
| --- | --- |
| >50% beads still open | continue normally |
| <50% beads still open | consider reducing workers |
| all current-phase beads terminal | evaluate completion readiness |
| no progress for 3+ cycles | diagnose mail, reservations, or worker health |

If coordination overhead exceeds useful progress, stop expanding the swarm, remove `swarming`, and degrade the remainder to `beo-execute`.

## 5. Swarm Completion

When no beads remain `in_progress` and no executable current-phase work remains:
1. verify the graph:

```bash
bv --robot-triage --graph-root <EPIC_ID> --format json
```

2. if orphaned or blocked beads remain, remove `swarming`, report remaining work, and get user direction
3. if all current-phase beads are terminal, apply the pre-completion gate

Pre-completion gate:
- any `failed` bead → remove `swarming`, write `needs-debugging`, hand off to `beo-route`
- any `cancelled` bead without `cancelled_accepted` → remove `swarming`, write `cancelled-needs-decision`, hand off to `beo-route`
- otherwise proceed only when all current-phase beads are `done` or accepted-cancelled

Before final routing, remove `swarming`:

```bash
br label remove <EPIC_ID> -l swarming
```

Then choose the next route:
- remove `approved` and route to `beo-plan` if `planning_mode = multi-phase` and later phases remain
- route to `beo-review` if this was the final execution scope

Update `.beads/STATE.json`, clear active workers, run `br sync --flush-only`, and send the completion message.

## 6. Context-Budget Checkpoint

If context usage exceeds 65%:
1. write `.beads/HANDOFF.json` using the canonical schema
2. include swarming-specific resume detail such as session, active workers, graph status, blockers, resume instructions, and context at pause
3. include planning-aware fields when relevant
4. broadcast a pause notification on the epic thread
5. report to the user how to resume
