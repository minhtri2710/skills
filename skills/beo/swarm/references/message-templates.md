# Agent Mail Message Templates

> Use the Table of Contents to jump to the template needed. Most common: §3 (Bead Assignment), §4 (Completion Report), §5-7 (Blocker/File Conflict).

Standard message formats for swarm coordination. All messages use `send_message()` or `reply_message()` from Agent Mail, posting to the epic thread (`thread_id=<EPIC_ID>`) unless noted.
Coordinator identity: `<COORDINATOR_AGENT_NAME>`. Worker identity: `<AGENT_MAIL_NAME>` (from `macro_start_session`).

## Table of Contents

- [1. Spawn Notification](#1-spawn-notification)
- [2. Worker Spawn Acknowledgment](#2-worker-spawn-acknowledgment)
- [3. Bead Assignment](#3-bead-assignment)
- [4. Completion Report](#4-completion-report)
- [5. Blocker Alert](#5-blocker-alert)
- [6. File Conflict Request](#6-file-conflict-request)
- [7. File Conflict Resolution](#7-file-conflict-resolution)
- [8. Overseer Broadcast](#8-overseer-broadcast)
- [9. Coordinator Context Warning](#9-coordinator-context-warning)
- [10. Swarm Completion Announcement](#10-swarm-completion-announcement)
- [11. Startup Reminder](#11-startup-reminder)
- [12. Silent Worker Reminder](#12-silent-worker-reminder)
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
- Coordinator assigns one bead per worker
- File coordination via Agent Mail reservations
- Blockers and corrections in this thread

Workers spawning now:
- <AGENT_NAME_1>
- <AGENT_NAME_2>
- <AGENT_NAME_3>

All workers: join thread, post startup acknowledgment, wait for assignment, then load beo-execute.
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
Status: Loading beo-execute skill.
Next: read context, wait for assignment from coordinator.
```

---

## 3. Bead Assignment

> Coordinator → worker | After `[ONLINE]`, before execution begins

```
Subject: [ASSIGNMENT] <bead-id>
Thread: <EPIC_ID>
Importance: HIGH

[ASSIGNMENT]
Bead: <bead-id>
Description: <bead description summary>
File scope: <expected files>
Dependencies satisfied: <list of completed dep beads>
Verification: <expected verification command>
Phase: <current phase>
```

---

## 4. Completion Report

> Worker → Coordinator | After bead close

```
Subject: [DONE] <bead-id>: <bead-title>
Thread: <EPIC_ID>
Importance: NORMAL

Bead closed: <bead-id>
Title: <bead-title>
Worker: <AGENT_NAME>
Commit: <git-commit-hash>

Summary: <2-3 sentence description>

Files modified:
- <path/to/file1>
- <path/to/file2>

Verification: <command/result summary>

Context budget: ~<XX>% used
Next: return to `bv --robot-plan`
```

---

## 5. Blocker Alert

> Worker → Coordinator | On discovering a blocker

```
Subject: [BLOCKED] <bead-id>: <one-line description>
Thread: <EPIC_ID>
Importance: HIGH

BLOCKED: <AGENT_NAME> on bead <bead-id>.

Type: [MISSING_CONTEXT | DEPENDENCY_NOT_MET | TECHNICAL_FAILURE | AMBIGUITY]

Description:
<What is blocking. Include errors, file names, relevant details.>

Need to proceed:
<Specific ask: information, file reservation release, user decision, etc.>

Paused on this bead, waiting for reply.
```

---

## 6. File Conflict Request

> Worker → Coordinator | File needed that another worker holds

```
Subject: [FILE CONFLICT] <path/to/file>
Thread: <EPIC_ID>
Importance: HIGH

File conflict: <AGENT_NAME> needs a reserved file.

Requested file: <path/to/file>
Reserved by: <AGENT_NAME_holder or "unknown">
Reservation reason: <reason from reservation holder>
Conflict details: <payload from `file_reservation_paths(...)`>
My bead: <bead-id>
Reason needed: <Why this file is required>

Awaiting decision:
1. Request holder release at safe checkpoint
2. Ask me to wait
3. Ask me to defer and create follow-up bead
```

---

## 7. File Conflict Resolution

> Coordinator → Worker | Reply to file conflict request

```
Subject: Re: [FILE CONFLICT] <path/to/file>
Thread: <EPIC_ID>
Importance: NORMAL

Decision for <path/to/file>:

[Choose one:]

OPTION A - Wait:
<AGENT_NAME_requester>: wait for <AGENT_NAME_holder> to release.

OPTION B - Release requested:
<AGENT_NAME_holder>: release <path/to/file> at safe checkpoint.
Call `release_file_reservations(project_key, agent_name, paths=["<path/to/file>"])`.
<AGENT_NAME_requester>: stand by until confirmed, then acquire with
`file_reservation_paths(project_key, agent_name, paths=["<path/to/file>"], ttl_seconds=3600, exclusive=true, reason="Working bead <BEAD_ID>")`.

OPTION C - Defer:
<AGENT_NAME_requester>: defer change, create follow-up bead, continue with next executable bead.
```

---

## 8. Overseer Broadcast

> Coordinator → all workers | Shared correction or reminder

```
Subject: [OVERSEER] <short instruction>
Thread: <EPIC_ID>
Importance: HIGH

Broadcast to all workers:
<Instruction or correction>
```

---

## 9. Coordinator Context Warning

> Coordinator → all workers | Context approaching 65%

```
Subject: [CONTEXT WARNING] Coordinator approaching capacity
Thread: <EPIC_ID>
Importance: HIGH

Coordinator context at ~<XX>%. Writing HANDOFF.json now.

Status: Open: <N> | In-progress: <N> | Blocked: <N>

Workers: complete current bead safely, then report status.

Resume: .beads/HANDOFF.json, .beads/STATE.json, `bv --robot-triage --graph-root <EPIC_ID>`
```

---

## 10. Swarm Completion Announcement

> Coordinator → all workers | All beads verified closed

```
Subject: [SWARM COMPLETE] <feature-name>: all beads closed
Thread: <EPIC_ID>
Importance: NORMAL

Swarm complete for epic <EPIC_ID>.

Beads: <N> | Workers: <K> | Build: PASS | Tests: PASS

All workers: work complete.

Next: final scope → beo-review. Later phases remain → remove `approved`, invoke beo-plan.
```

---

## 11. Startup Reminder

> Coordinator → worker | Worker not online after 2 cycles

```
Subject: [STARTUP REMINDER] <WORKER_NAME>
Thread: <EPIC_ID>
Importance: HIGH

Spawned N cycles ago, no [ONLINE] posted.
Post [ONLINE] with identities, or report a blocker.
```

---

## 12. Silent Worker Reminder

> Coordinator → worker | No updates for multiple cycles

```
Subject: [STATUS CHECK] <WORKER_NAME>
Thread: <EPIC_ID>
Importance: HIGH

No messages for N cycles.
Reply with: current bead/status, blockers, estimated completion.
```

---

## Handoff JSON Template

Write to `.beads/HANDOFF.json` when coordinator context exceeds 65%.
Extends the base HANDOFF schema from `beo-reference` → `references/state-and-handoff-protocol.md` with swarm-specific fields:

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
