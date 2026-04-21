# Agent Mail Coordination

Shared Agent Mail protocol for `beo-execute` and `beo-swarm`.

## Core Runtime Surface

This surface is required for swarming:

- `ensure_project(...)`
- `register_agent(...)`
- `macro_start_session(...)`
- `fetch_inbox(...)`
- `send_message(...)`
- `reply_message(...)`
- `file_reservation_paths(...)`
- `release_file_reservations(...)`

If this surface is not available, do not start `beo-swarm`. Route to solo execution instead.

## Session Setup

Initialize the project before coordinator or worker messaging:

```text
ensure_project(
  human_key="<project-root-path>"
)
```

Register the coordinator when startup is explicit:

```text
register_agent(
  project_key="<project-root-path>",
  name="<COORDINATOR_AGENT_NAME>",
  program="<runtime-program>",
  model="<MODEL>"
)
```

Workers normally bootstrap through:

```text
macro_start_session(
  human_key="<project-root-path>",
  model="<MODEL>",
  program="<runtime-program>",
  task_description="beo worker execution",
  agent_name="<WORKER_NICKNAME>"
)
```

Use `startup.agent.name` from `macro_start_session(...)` as the worker identity for messaging, inbox reads, and reservations.

## Identity Model

Workers may have two names:
- an orchestrator-assigned nickname for human readability
- an Agent Mail identity returned by Agent Mail startup or registration calls

Use the Agent Mail identity for all `sender_name`, inbox, and reservation calls.
If both are shown, format them as:

```text
Nickname: <NICKNAME> | Agent Mail: <AGENT_MAIL_NAME>
```

## Reservation APIs

Reserve files before editing:

```text
file_reservation_paths(
  project_key="<project-root-path>",
  agent_name="<agent-mail-name>",
  paths=["<path-1>", "<path-2>"],
  ttl_seconds=3600,
  exclusive=true,
  reason="Working bead <BEAD_ID>"
)
```

Release files after bead close or after the coordinator resolves a handoff:

```text
release_file_reservations(
  project_key="<project-root-path>",
  agent_name="<agent-mail-name>",
  paths=["<path-1>", "<path-2>"]
)
```

Use specific paths or narrow globs. Do not reserve broad file sets unless required.

## Messaging APIs

Send new thread or thread-targeted messages with:

```text
send_message(
  project_key="<project-root-path>",
  sender_name="<agent-mail-name>",
  to=["<recipient-agent-name>"],
  subject="<subject>",
  body_md="<markdown body>",
  thread_id="<EPIC_ID>"
)
```

Read inbound coordination messages with:

```text
fetch_inbox(
  project_key="<project-root-path>",
  agent_name="<agent-mail-name>"
)
```

Reply inside an existing coordination thread with:

```text
reply_message(
  project_key="<project-root-path>",
  message_id="<message-id>",
  sender_name="<agent-mail-name>",
  body_md="<markdown body>"
)
```

Use:
- `send_message(...)` for `[ONLINE]`, `[DONE]`, `[BLOCKED]`, and coordinator broadcasts
- `reply_message(...)` for direct thread responses such as `[FILE CONFLICT RESOLUTION]`

## Conflict Semantics

If `file_reservation_paths(...)` returns conflicts, treat that as an active coordination event. Expected details include, when available:
- conflicting path or path pattern
- current holder identity
- reservation reason
- any structured reservation metadata returned by the API

The requester must not edit through the conflict.

## Message Boundary

Reservation APIs own file reservations.
Agent Mail messages own conflict resolution, status reporting, and handoff communication.

In practice:
1. use reservation APIs to claim or release paths
2. use `[FILE CONFLICT]` and `[FILE CONFLICT RESOLUTION]` messages to coordinate wait/release/reassign/defer
3. use inbox and message APIs for liveness, completion, blockers, and pause/resume

## Cycle Vocabulary

- `cycle`: one complete coordinator monitor-and-tend pass
- `startup acknowledgment`: the worker's first `[ONLINE]` message after startup
- `silent worker`: a worker that has stopped posting expected updates for multiple cycles
