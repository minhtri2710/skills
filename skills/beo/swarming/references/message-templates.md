# Agent Mail Message Templates

> **~350 lines.** Use the Table of Contents below to jump to the template you need. Most common: §3 (Completion Report), §4 (Blocker Alert), §5-6 (File Conflict).

Standard message formats for swarm coordination. All messages use `send_message()` or `reply_message()` from Agent Mail, posting to the epic thread (`thread_id=<EPIC_ID>`) unless noted.
Coordinator identity: `<COORDINATOR_AGENT_NAME>`. Worker identity: `<AGENT_MAIL_NAME>` (from `macro_start_session`).

## Table of Contents

- [1. Spawn Notification](#1-spawn-notification)
- [2. Worker Spawn Acknowledgment](#2-worker-spawn-acknowledgment)
- [3. Completion Report](#3-completion-report)
- [4. Blocker Alert](#4-blocker-alert)
- [5. File Conflict Request](#5-file-conflict-request)
- [6. File Conflict Resolution](#6-file-conflict-resolution)
- [7. Overseer Broadcast](#7-overseer-broadcast)
- [8. Coordinator Context Warning](#8-coordinator-context-warning)
- [9. Swarm Completion Announcement](#9-swarm-completion-announcement)
- [10. Startup Reminder](#10-startup-reminder)
- [11. Silent Worker Reminder](#11-silent-worker-reminder)
- [Handoff JSON Template](#handoff-json-template)

---

## 1. Spawn Notification

> Coordinator → workers | After Agent Mail setup, before spawning

```
Subject: [SWARM START] <feature-name>
Thread: <EPIC_ID>
Importance: NORMAL

Swarm initialized for epic <EPIC_ID>.

Execution model:
- Workers are self-routing via `bv --robot-plan`
- File coordination happens through Agent Mail reservations
- Blockers and course corrections happen in this thread

Workers spawning now:
- <AGENT_NAME_1>
- <AGENT_NAME_2>
- <AGENT_NAME_3>

All workers: join this thread, post startup acknowledgment, then load the beo-executing skill.
```

---

## 2. Worker Spawn Acknowledgment

> Worker → Coordinator | Immediately on startup

```
Subject: [ONLINE] <AGENT_NAME> ready
Thread: <EPIC_ID>
Importance: NORMAL

<AGENT_NAME> online.
Nickname: <NICKNAME> | Agent Mail: <NAME>
Status: Loading beo-executing skill.
Next step: read context, run `bv --robot-plan`, claim the top executable bead.
```

---

## 3. Completion Report

> Worker → Coordinator | After bead close

```
Subject: [DONE] <bead-id>: <bead-title>
Thread: <EPIC_ID>
Importance: NORMAL

Bead closed: <bead-id>
Title: <bead-title>
Worker: <AGENT_NAME>
Commit: <git-commit-hash>

Summary of changes:
<2-3 sentence description of what was implemented>

Files modified:
- <path/to/file1>
- <path/to/file2>

Verification:
- <command/result summary>

Context budget: ~<XX>% used
Next action: return to `bv --robot-plan`
```

---

## 4. Blocker Alert

> Worker → Coordinator | On discovering a blocker

```
Subject: [BLOCKED] <bead-id>: <one-line description>
Thread: <EPIC_ID>
Importance: HIGH

BLOCKED: <AGENT_NAME> cannot proceed on bead <bead-id>.

Blocker type: [MISSING_CONTEXT | DEPENDENCY_NOT_MET | TECHNICAL_FAILURE | AMBIGUITY]

Description:
<Clear description of what is blocking. Include errors, file names, and relevant details.>

What I need to proceed:
<Specific ask: information, release of a file reservation, user decision, etc.>

I am paused on this bead and waiting for a reply on this thread.
```

---

## 5. File Conflict Request

> Worker → Coordinator | File needed that another worker holds

```
Subject: [FILE CONFLICT] <path/to/file>
Thread: <EPIC_ID>
Importance: HIGH

File conflict: <AGENT_NAME> needs a file that is currently reserved.

Requested file: <path/to/file>
Currently reserved by: <AGENT_NAME_holder or "unknown">
Reservation reason: <reason from reservation holder>
Conflict details: <structured conflict payload from `file_reservation_paths(...)`>
My bead: <bead-id>
Reason needed: <Why this file is required for this bead>

Awaiting orchestrator decision:
1. Request holder release at a safe checkpoint
2. Ask me to wait
3. Ask me to defer and create a follow-up bead
```

---

## 6. File Conflict Resolution

> Coordinator → Worker | Reply to file conflict request

```
Subject: Re: [FILE CONFLICT] <path/to/file>
Thread: <EPIC_ID>
Importance: NORMAL

Decision on file conflict for <path/to/file>:

[Choose one:]

OPTION A: Wait:
<AGENT_NAME_requester>: wait for <AGENT_NAME_holder> to release the reservation.

OPTION B: Release requested:
<AGENT_NAME_holder>: please release <path/to/file> when you reach a safe checkpoint.
Call `release_file_reservations(project_key, agent_name, paths=["<path/to/file>"])` when safe.
<AGENT_NAME_requester>: stand by until release is confirmed.
After release, call `file_reservation_paths(project_key, agent_name, paths=["<path/to/file>"], ttl_seconds=3600, exclusive=true, reason="Working bead <BEAD_ID>")` to acquire it.

OPTION C: Defer:
<AGENT_NAME_requester>: defer this change. Create a follow-up bead and continue with the next executable bead.
```

---

## 7. Overseer Broadcast

> Coordinator → all workers | Shared correction or reminder

```
Subject: [OVERSEER] <short instruction>
Thread: <EPIC_ID>
Importance: HIGH

Broadcast to all workers:

<Instruction or correction>

Examples:
- Re-read AGENTS.md before continuing
- Do not touch <file/path> until blocker <id> is resolved
- Decision D7 is now locked; honor it in all remaining work
```

---

## 8. Coordinator Context Warning

> Coordinator → all workers | Context approaching 65%

```
Subject: [CONTEXT WARNING] Coordinator approaching capacity
Thread: <EPIC_ID>
Importance: HIGH

Coordinator context at ~<XX>%. Writing HANDOFF.json now.

Current status:
- Open beads: <count>
- In-progress beads: <count>
- Known blockers: <count>

Workers: continue current bead safely, then report status to this thread.

Resume artifacts:
- .beads/HANDOFF.json
- .beads/STATE.json
- bv --robot-triage --graph-root <EPIC_ID>
```

---

## 9. Swarm Completion Announcement

> Coordinator → all workers | All beads verified closed

```
Subject: [SWARM COMPLETE] <feature-name>: all beads closed
Thread: <EPIC_ID>
Importance: NORMAL

Swarm complete for epic <EPIC_ID>.

Summary:
- Beads implemented: <N>
- Workers used: <K>
- Build status: PASS
- Test status: PASS

All workers: your work is complete.

Next step:
- If this is the final execution scope: invoke beo-reviewing.
- If later phases remain: remove `approved`, then invoke beo-planning for the next phase.
```

---

## 10. Startup Reminder

> Coordinator → worker | Worker not online after 2 cycles

```
Subject: [STARTUP REMINDER] <WORKER_NAME>
Thread: <EPIC_ID>
Importance: HIGH

You were spawned N cycles ago but have not posted `[ONLINE]`.

Please either:
- post `[ONLINE]` with your nickname and Agent Mail identities, or
- report a blocker if you cannot start.
```

---

## 11. Silent Worker Reminder

> Coordinator → worker | No updates for multiple cycles

```
Subject: [STATUS CHECK] <WORKER_NAME>
Thread: <EPIC_ID>
Importance: HIGH

No messages received for N cycles.

Reply with:
- current bead and status
- any blockers
- estimated time to completion
```

---

## Handoff JSON Template

Write to `.beads/HANDOFF.json` when the swarm coordinator context exceeds 65%.

Extends the base HANDOFF schema from `../../reference/references/state-and-handoff-protocol.md` (schema_version, phase, skill, feature, feature_name, next_action, in_flight_beads, timestamp) with swarm-specific fields:

```json
{
  "format": "beo-swarm-handoff",
  "session": {
    "id": "beo-swarm-<YYYYMMDD-HHMMSS>",
    "paused_at": "<ISO-8601 timestamp>",
    "reason_for_pause": "context_critical",
    "agent": "<COORDINATOR_AGENT_NAME>"
  },
  "swarm": {
    "epic_id": "<EPIC_ID>",
    "feature_name": "<feature_slug>",
    "project_key": "<project-root-path>"
  },
  "graph_status": {
    "open_beads": ["<bead-id-1>", "<bead-id-2>"],
    "in_progress_beads": ["<bead-id-3>"],
    "blocked_beads": ["<bead-id-4>"]
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
    "priority_next": "Poll epic thread, then inspect the live graph",
    "read_first": [".beads/STATE.json", ".beads/HANDOFF.json"],
    "check_mail": true,
    "bead_check": "bv --robot-triage --graph-root <EPIC_ID>",
    "restore_confirmation": "Confirm open/in-progress/blocked counts still match before resuming"
  },
  "context_at_pause": {
    "tokens_used_pct": 0.67,
    "agent_mail_thread": "<EPIC_ID>"
  }
}
```
