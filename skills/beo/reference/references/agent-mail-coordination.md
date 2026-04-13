# Agent Mail Coordination

Shared canonical reference for Agent Mail coordination used by `beo-executing` and `beo-swarming`.

## Core Runtime Surface

The beo workflow assumes this Agent Mail surface exists when swarming is enabled:

- `ensure_project(...)`
- `register_agent(...)`
- `macro_start_session(...)`
- `fetch_inbox(...)`
- `send_message(...)`
- `reply_message(...)`
- `file_reservation_paths(...)`
- `release_file_reservations(...)`

If this surface is not available, `beo-swarming` must not start. Route to solo execution instead.

## Project / Session Initialization

Initialize a project before coordinator or worker messaging:

```text
ensure_project(
  human_key="<project-root-path>"
)
```

Register the coordinator when using explicit coordinator startup:

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

`macro_start_session(...)` returns the canonical Agent Mail identity at `startup.agent.name`. Use that value for all worker `sender_name` and inbox calls.

## Identity Model

Workers often have two names:
- an orchestrator-assigned nickname for human readability
- an Agent Mail identity returned by Agent Mail startup or registration calls

The Agent Mail identity is canonical for all `sender_name`, inbox, and reservation calls.
If both names are shown, format them as:

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

Use specific paths or narrow globs. Do not reserve broad file sets unless the work truly requires them.

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

Use `send_message(...)` for `[ONLINE]`, `[DONE]`, `[BLOCKED]`, and coordinator broadcasts.
Use `reply_message(...)` for direct responses such as `[FILE CONFLICT RESOLUTION]`.

## Conflict Semantics

If `file_reservation_paths(...)` returns conflicts, treat that as an active coordination event.
Expected conflict details include, when available:
- conflicting path or path pattern
- current holder identity
- reservation reason
- any structured reservation metadata returned by the API

The requester must not edit through the conflict.

## Message Boundary

Reservation APIs own file reservations.
Agent Mail messages own conflict resolution, status reporting, and handoff communication.

In practice:
- use reservation APIs to claim or release paths
- use `[FILE CONFLICT]` and `[FILE CONFLICT RESOLUTION]` messages to coordinate who should wait, release, reassign, or defer
- use inbox/message APIs for worker liveness, completion reports, blocker escalation, and pause/resume coordination

## Cycle Vocabulary

- `cycle`: one complete coordinator monitor-and-tend pass
- `startup acknowledgment`: the worker's first `[ONLINE]` message after startup
- `silent worker`: a worker that has stopped posting expected updates for multiple cycles
