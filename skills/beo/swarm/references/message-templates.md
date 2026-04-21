# Agent Mail Message Templates

Canonical message shapes for `beo-swarm`. Unless noted, send all messages to the epic thread with `thread_id="<EPIC_ID>"`.

Coordinator identity: `<COORDINATOR_AGENT_NAME>`
Worker identity: `<AGENT_MAIL_NAME>` returned by `macro_start_session(...)`

## 1. Spawn Notification

Coordinator to all workers before assignments:

```text
Subject: [SWARM START] <feature-name>
Thread: <EPIC_ID>
Importance: NORMAL

Swarm initialized for epic <EPIC_ID>.

Execution model:
- one bead per worker
- file coordination via Agent Mail reservations
- blockers and corrections stay in this thread

Workers spawning now:
- <AGENT_NAME_1>
- <AGENT_NAME_2>
- <AGENT_NAME_3>

Post [ONLINE], wait for assignment, then load beo-execute.
```

## 2. Worker Spawn Acknowledgment

Worker to coordinator immediately after startup:

```text
Subject: [ONLINE] <AGENT_NAME> ready
Thread: <EPIC_ID>
Importance: NORMAL

<AGENT_NAME> online.
Nickname: <NICKNAME> | Agent Mail: <AGENT_MAIL_NAME>
Status: Loading beo-execute.
Next: read context, wait for assignment.
```

## 3. Bead Assignment

Coordinator to one worker:

```text
Subject: [ASSIGNMENT] <bead-id>
Thread: <EPIC_ID>
Importance: HIGH

[ASSIGNMENT]
Bead: <bead-id>
Description: <short summary>
File scope: <paths>
Dependencies satisfied: <completed deps>
Verification: <expected command>
Phase: <current phase>
```

## 4. Completion Report

Worker after bead close:

```text
Subject: [DONE] <bead-id>: <bead-title>
Thread: <EPIC_ID>
Importance: NORMAL

Bead closed: <bead-id>
Title: <bead-title>
Worker: <AGENT_NAME>
Commit: <git-commit-hash>

Summary: <2-3 sentences>

Files modified:
- <path/to/file1>
- <path/to/file2>

Verification: <command/result summary>
Context budget: ~<XX>% used
Next: return to coordinator for more work or stop
```

## 5. Blocker Alert

Worker when blocked:

```text
Subject: [BLOCKED] <bead-id>: <one-line description>
Thread: <EPIC_ID>
Importance: HIGH

BLOCKED: <AGENT_NAME> on bead <bead-id>

Type: [MISSING_CONTEXT | DEPENDENCY_NOT_MET | TECHNICAL_FAILURE | AMBIGUITY]
Description: <blocking detail>
Need to proceed: <specific ask>

Paused on this bead, waiting for reply.
```

## 6. File Conflict Request

Worker when reservation conflicts:

```text
Subject: [FILE CONFLICT] <path/to/file>
Thread: <EPIC_ID>
Importance: HIGH

File conflict: <AGENT_NAME> needs a reserved file.

Requested file: <path/to/file>
Reserved by: <holder or "unknown">
Reservation reason: <holder reason>
Conflict details: <payload from file_reservation_paths(...)>
My bead: <bead-id>
Reason needed: <why this file is required>

Awaiting decision:
1. Ask holder to release at a safe checkpoint
2. Ask me to wait
3. Ask me to defer
```

## 7. File Conflict Resolution

Coordinator reply to a conflict request:

```text
Subject: Re: [FILE CONFLICT] <path/to/file>
Thread: <EPIC_ID>
Importance: NORMAL

Decision for <path/to/file>:

OPTION A - Wait:
<REQUESTER>: wait for <HOLDER> to release.

OPTION B - Release requested:
<HOLDER>: release <path/to/file> at a safe checkpoint with `release_file_reservations(...)`.
<REQUESTER>: after confirmation, reacquire with `file_reservation_paths(...)`.

OPTION C - Defer:
<REQUESTER>: defer this change and continue with the next executable bead.
```

## 8. Overseer Broadcast

Coordinator to all workers:

```text
Subject: [OVERSEER] <short instruction>
Thread: <EPIC_ID>
Importance: HIGH

Broadcast to all workers:
<instruction or correction>
```

## 9. Coordinator Context Warning

Coordinator when context nears the checkpoint threshold:

```text
Subject: [CONTEXT WARNING] Coordinator approaching capacity
Thread: <EPIC_ID>
Importance: HIGH

Coordinator context at ~<XX>%. Writing HANDOFF.json now.

Status: Open: <N> | In-progress: <N> | Blocked: <N>

Workers: finish the current bead safely, then report status.

Resume with: .beads/HANDOFF.json, .beads/STATE.json, `bv --robot-triage --graph-root <EPIC_ID>`
```

## 10. Swarm Completion Announcement

Coordinator when all verified beads are closed:

```text
Subject: [SWARM COMPLETE] <feature-name>: all beads closed
Thread: <EPIC_ID>
Importance: NORMAL

Swarm complete for epic <EPIC_ID>.

Beads: <N> | Workers: <K> | Build: PASS | Tests: PASS

All workers: work complete.

Next: final scope -> beo-review. Later phases -> remove `approved`, route to beo-plan.
```

## 11. Startup Reminder

Coordinator to a worker with no `[ONLINE]` after two cycles:

```text
Subject: [STARTUP REMINDER] <WORKER_NAME>
Thread: <EPIC_ID>
Importance: HIGH

Spawned N cycles ago, no [ONLINE] posted.
Post [ONLINE] with identities, or report a blocker.
```

## 12. Silent Worker Reminder

Coordinator to a worker with no updates for multiple cycles:

```text
Subject: [STATUS CHECK] <WORKER_NAME>
Thread: <EPIC_ID>
Importance: HIGH

No messages for N cycles.
Reply with current bead, status, blockers, and estimated completion.
```

## Handoff JSON Template

When coordinator context exceeds the checkpoint threshold, write:

```json
{
  "schema_version": 1,
  "phase": "swarming",
  "skill": "beo-swarm",
  "feature": "<EPIC_ID>",
  "feature_name": "<feature_slug>",
  "next": "beo-swarm",
  "reason": "swarm-checkpoint",
  "content": "Coordinator paused near context limit; poll Agent Mail thread and re-check live graph before resuming.",
  "in_flight_beads": ["<bead-id-3>"],
  "timestamp": "<ISO-8601 timestamp>",
  "planning_mode": "single-phase",
  "has_phase_plan": false,
  "current_phase": 1,
  "total_phases": 1,
  "phase_name": "<current phase name>",
  "swarm": {
    "session_id": "beo-swarm-<YYYYMMDD-HHMMSS>",
    "coordinator_agent": "<COORDINATOR_AGENT_NAME>",
    "epic_id": "<EPIC_ID>",
    "project_key": "<project-root-path>",
    "graph_status": {
      "open_beads": ["<bead-id-1>", "<bead-id-2>"],
      "in_progress_beads": ["<bead-id-3>"],
      "blocked_beads": ["<bead-id-4>"]
    }
  },
  "active_workers": [
    {
      "agent_nickname": "<NICKNAME>",
      "agent_mail_name": "<NAME>",
      "current_bead": "<bead-id-3>",
      "status": "in_progress"
    }
  ],
  "open_blockers": [
    {
      "bead_id": "<bead-id>",
      "worker": "<AGENT_NAME>",
      "description": "<blocker description>",
      "thread_message_id": "<mail-id>"
    }
  ],
  "resume_instructions": {
    "priority_next": "Poll epic thread, then inspect live graph",
    "read_first": [".beads/STATE.json", ".beads/HANDOFF.json"],
    "check_mail": true,
    "bead_check": "bv --robot-triage --graph-root <EPIC_ID>",
    "restore_confirmation": "Confirm open/in-progress/blocked counts match before resuming"
  },
  "context_at_pause": {
    "tokens_used_pct": 0.67,
    "agent_mail_thread": "<EPIC_ID>"
  }
}
```
