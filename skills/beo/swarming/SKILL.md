---
name: beo-swarming
description: Orchestrates parallel worker agents for feature execution. Use after the beo-validating skill approves execution. Initializes the overseer/orchestrator context, spawns bounded worker subagents, monitors Agent Mail for completions/blockers/file conflicts, coordinates rescues and course corrections, and hands off to beo-reviewing when all beads are closed. The orchestrator TENDS; it never implements beads directly.
---

# Swarming

## Role Boundary: Read First

You are the **ORCHESTRATOR**. You launch workers, monitor coordination, handle escalations, and keep the swarm moving. You do NOT implement beads. If you find yourself editing source files, stop immediately. That is the `beo-executing` skill's job.

- **beo-swarming** = launches and tends workers (this skill)
- **beo-executing** = each worker's self-routing implementation loop

The orchestrator launches the swarm, then tends it. Workers decide what to do next by using `bv --robot-plan` against the live bead graph.

---

## Phase 1: Confirm Swarm Readiness

### Prerequisites

- Beads are in `open` status and approved for execution
- EPIC_ID is known (from STATE.md or user input)
- Agent Mail server is reachable

If Agent Mail is unavailable, degrade to single-worker mode:
- Route to `beo-executing` instead of swarming
- Log the degradation in STATE.md
- Do not attempt to orchestrate parallel workers without Agent Mail

### Steps

1. Get `EPIC_ID`: read `.beads/STATE.md` or ask the user.
2. Check live bead status:
   ```bash
   bv --robot-triage --graph-root <EPIC_ID> --format json
   ```
3. Verify there is executable work:
   - open beads exist
   - dependencies are acyclic
   - no unresolved validation blockers remain
4. Update `.beads/STATE.md` with current swarm intent and epic ID.
5. Claim the epic if not already in_progress:
   ```bash
   br update <EPIC_ID> --claim
   ```
   See `pipeline-contracts.md` → Epic Lifecycle. This must happen before any workers are spawned.

### Scheduling Strategy (4-Tier Cascade)

Determine which beads to execute first using this cascade:

```bash
# Tier 1: Graph-aware execution plan (best: returns parallel tracks)
bv --robot-plan --graph-root <EPIC_ID> --format json 2>/dev/null

# Tier 2: Single next-task recommendation
|| bv --robot-next --format json 2>/dev/null

# Tier 3: Ready beads from br
|| br ready --json 2>/dev/null

# Tier 4: Manual fallback: list open beads and sort by dependency count
|| br list --status open --json
```

Use the highest-available tier. Workers will re-evaluate scheduling each loop iteration via `bv --robot-plan`.

**Do not** compute runtime tracks, runtime waves, or any separate runtime planning artifact. The bead graph itself is the execution source of truth.

---

## Phase 2: Initialize Agent Mail

```
ensure_project(human_key="<project-root-path>")
register_agent(
  project_key="<project-root-path>",
  name="<COORDINATOR_AGENT_NAME>",  # must be a valid adjective+noun Agent Mail identity
  program="codex-cli",
  model="gpt-5",
  task_description="swarm-coordinator"
)
```

Define an epic topic tag:

```
EPIC_TOPIC="epic-<EPIC_ID>"
```

Bootstrap the epic coordination thread by sending the first message (this is the thread-creation moment in Agent Mail):

```
send_message(
  project_key="<project-root-path>",
  sender_name="<COORDINATOR_AGENT_NAME>",
  to=["<COORDINATOR_AGENT_NAME>"],
  subject="[SWARM START] <feature-name>",
  body_md="Swarm initialized for epic <EPIC_ID> ...",
  thread_id="<EPIC_ID>"
)
```

Template: see `references/message-templates.md` -> **Spawn Notification**.

The epic thread is the coordination surface for:
- worker startup acknowledgments
- completion reports
- blocker alerts
- file conflict requests
- context handoffs
- overseer broadcasts

---

## Phase 3: Spawn Workers

Spawn a pool of worker subagents in parallel:

```
Subagent(
  identity="Worker: <agent-name>",
  context=<scoped worker context from references/worker-template.md>
)
```

`Subagent(...)` is the canonical contract. In an actual runtime, call whatever worker-spawn primitive is available, but preserve the same behavior: the orchestrator stays in control, each worker gets bounded scope by default, and workers report back through Agent Mail plus the live bead graph.

Provide each worker:
- Agent Mail identity (project key, agent name, epic thread)
- Feature name / epic ID
- Instruction to load the `beo-executing` skill immediately
- Optional startup hint if there is an urgent ready bead, clearly labeled as a hint rather than an assignment
- Scoped task-specific context by default; full parent-context inheritance only when explicitly needed

Do **not** assign workers fixed tracks, fixed waves, or fixed bead lists as the normal case. Workers are expected to:
1. register
2. read project context
3. call `bv --robot-plan`
4. reserve files
5. implement and report
6. loop

Mark spawned workers in `.beads/STATE.md` under `## Active Workers`.

---

## Phase 4: Monitor + Tend

This is the "clockwork deity" phase. The swarm is live; now you manage it.

Check Agent Mail regularly on the epic thread:

```
fetch_inbox(
  project_key="<project-root-path>",
  agent_name="<COORDINATOR_AGENT_NAME>"
)
```

Use live graph checks for oversight, not assignment:

```bash
bv --robot-triage --graph-root <EPIC_ID> --format json
```

### Worker Startup Acknowledgments

When a worker posts an online message:
1. Confirm it joined the correct epic thread
2. Confirm it is loading `beo-executing`
3. Update `.beads/STATE.md`

### Bead Completion Reports

When a worker posts a completion report:
1. Verify the bead is actually closed: `br show <bead-id> --json` → check `.status` = `closed`
2. Acknowledge receipt on the thread
3. Update `.beads/STATE.md`
4. Re-check the graph if needed to see what newly unblocked

### Progress Check

After each completion, assess overall progress:

```bash
bv --robot-triage --graph-root <EPIC_ID> --format json
```

| Remaining open | Action |
|---|---|
| >50% beads open | Continue monitoring |
| <50% beads open | Evaluate if workers should be reduced |
| All beads closed | Proceed to Phase 5 |
| Stalled (no progress 3+ cycles) | Diagnose: check mail, reservations, worker health |

### Blocker Alerts

When a worker posts a blocker alert:
1. Assess severity:
   - **Resolvable with existing context:** reply on the thread
   - **Needs another worker's status or release:** coordinate via thread
   - **Needs human judgment:** escalate to user quickly
2. Do not let workers spin silently on blockers
3. Record blocker state in `.beads/STATE.md`

### File Conflict Requests

When a worker requests a file another worker holds:
1. Identify holder and requester
2. Coordinate one of:
   - holder releases at a safe checkpoint
   - requester waits
   - requester defers and creates a follow-up bead
3. Log the resolution in `.beads/STATE.md`

### Overseer Broadcasts

Use broadcast messages when the swarm needs a shared correction, for example:
- "re-read AGENTS.md after compaction"
- "do not touch file X until blocker Y is cleared"
- "new user decision: D7 is locked, honor it"

### Context Checkpoint

After each significant event, estimate your own context budget.

**If context >65% used:**
1. Write `.beads/HANDOFF.json` with complete swarm state (see `references/message-templates.md` -> **Handoff JSON template**)
2. Broadcast a pause notification on the epic thread
3. Report to user that the orchestrator paused safely and how to resume
4. Do NOT abandon the swarm without writing `HANDOFF.json`

The swarming HANDOFF.json extends the base schema with additional fields (`session`, `swarm`, `graph_status`, `active_workers`, `open_blockers`, `resume_instructions`, `context_at_pause`). The base fields (`schema_version`, `phase`, `skill`, `feature`, `feature_name`, `next_action`, `in_flight_beads`, `timestamp`) must still be present at the top level for router compatibility. See `references/message-templates.md` → Handoff JSON Template.

---

## Phase 5: Swarm Complete

When no beads remain `in_progress` and the graph shows no remaining executable work:

1. Run final bead verification:
   ```bash
   bv --robot-triage --graph-root <EPIC_ID> --format json
   ```
2. If orphaned or blocked beads remain:
   - report which beads remain and why
   - ask the user whether to defer, create cleanup beads, or continue later
3. If all beads are closed:
   - run final build/test commands appropriate to the project
   - update `.beads/STATE.md`:
      ```markdown
      # Beo State
      - Phase: swarming → complete
      - Feature: <epic-id> (<feature-name>)
      - Tasks: <total> completed
      - Next: beo-reviewing
      ```
   - clear `## Active Workers` from `.beads/STATE.md`

4. Completion announcement via Agent Mail:
   ```
   send_message(
     project_key="<project-root-path>",
     sender_name="<COORDINATOR_AGENT_NAME>",
     to=[<worker-list>],
     thread_id="<EPIC_ID>",
     subject="[SWARM COMPLETE] <feature-name>: all beads closed",
     body_md="Swarm complete for epic <EPIC_ID>. Beads: <N>. Workers: <K>. Build: PASS. Test: PASS."
   )
   ```

5. Handoff message:
   > "Swarm execution complete. All beads closed. Invoke `beo-reviewing` skill."

---

## Red Flags

Stop and diagnose before continuing if you see:

- **Worker implements multiple beads at once**: self-routing does not mean parallelizing within one worker
- **Orchestrator edits source files**: role violation
- **Workers are idle but ready beads exist**: check mail, reservations, or startup drift
- **No Agent Mail activity for >10 poll cycles**: workers may be stuck or context-exhausted
- **The same file conflict repeats**: bead decomposition may be too coarse; escalate
- **Workers stop using `bv --robot-plan` and start freelancing**: re-broadcast the execution contract
- **Build/test failures accumulate without intervention**: create fix beads or stop and escalate

---

## Reference Files

Load when needed:

| File | Load When |
|---|---|
| `references/worker-template.md` | Spawning any worker (Phase 3) |
| `references/message-templates.md` | Posting or parsing Agent Mail messages |
