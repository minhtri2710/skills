# Pressure Scenarios

Use these RED/GREEN scenarios for swarm coordination failures.

## Scenario 1: Worker Skips [ONLINE]

Setup: Worker starts, calls `macro_start_session`, but never posts `[ONLINE]`.

- RED: Coordinator waits indefinitely or ignores the missing acknowledgment.
- GREEN: Coordinator sends `[STARTUP REMINDER]` after 2 cycles, `[STATUS CHECK]` after 3 cycles, and escalates to the user after 5 cycles.

## Scenario 2: Worker Skips Completion Report

Setup: Worker closes a bead with `br close` but never sends `[DONE]`.

- RED: Coordinator sees the closed bead in the graph but has no completion report.
- GREEN: Coordinator detects the graph-versus-mail mismatch, sends `[STATUS CHECK]`, and requests a retroactive report.

## Scenario 3: Worker Waits Silently on File Conflict

Setup: `file_reservation_paths(...)` returns conflicts, but the worker does not report them.

- RED: Worker stalls and the coordinator does not know why.
- GREEN: Worker immediately sends `[FILE CONFLICT]` with the conflict details and polls inbox until a resolution arrives.

## Scenario 4: Coordinator Idles on Quiet Thread

Setup: Workers are active but no messages arrive for several cycles.

- RED: Coordinator stops polling and misses a later blocker.
- GREEN: Coordinator continues polling, keeps graph oversight active, and treats an active swarm as a tending phase even when mail is quiet.

## Scenario 5: Combined Maximum Pressure

Setup: Worker A skips `[ONLINE]`, Worker B sends `[BLOCKED]`, Worker C hits a file conflict with Worker B's reserved files, and the coordinator is at 60% context budget.

- RED: Any single failure mode from the earlier scenarios causes the swarm to drift.
- GREEN: Coordinator handles the issues in priority order: startup escalation for A, blocker handling for B, conflict resolution for C, then a context-budget checkpoint.

## Scenario 6: Worker Timeout with Reserved Files

Setup: A worker reserves files, starts implementation, then times out or disappears before releasing reservations.

- RED: Reservations remain stale, other workers block indefinitely, and the coordinator does not reconcile ownership.
- GREEN: Coordinator detects the silent worker timeout, confirms no fresh progress arrived, releases or reassigns stale reservations using the canonical recovery path, and notifies affected workers.

## Scenario 7: Mixed Success Across Dependent Beads

Setup: Worker A finishes an upstream bead, Worker B fails a dependent bead, and Worker C is waiting on the same dependency chain.

- RED: Coordinator marks the swarm as broadly successful or keeps dispatching downstream work without reconciling the failed dependency.
- GREEN: Coordinator records the mixed outcome explicitly, halts newly unblocked dependent work, routes the failed path to the right recovery flow, and preserves the completed upstream result.

## Scenario 8: Stale Reservation Reconciliation After Resume

Setup: The coordinator resumes after interruption and finds reservation records that may belong to workers that no longer exist.

- RED: Coordinator trusts stale reservations forever or wipes them without checking for real in-flight work.
- GREEN: Coordinator reconciles reservations against current mail, process state, and graph progress, then clears only stale claims and reports the reconciliation result.
