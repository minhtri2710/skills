# Agent Mail Coordination

Shared canonical reference for Agent Mail coordination used by `beo-executing` and `beo-swarming`.

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

## Cycle Vocabulary

- `cycle`: one complete coordinator monitor-and-tend pass
- `startup acknowledgment`: the worker's first `[ONLINE]` message after startup
- `silent worker`: a worker that has stopped posting expected updates for multiple cycles
