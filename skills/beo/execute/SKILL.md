---
name: beo-execute
description: Mutates only the approved scope for one claimed atomic Beads ticket and records execution evidence.
---

# beo-execute

Refs: `beo-reference -> references/mutation-safety.md`, `beo-reference -> references/lifecycle-events.md`.

## Decision

Deliver exactly one approved atomic ticket scope.

## Enter

- `PASS_EXECUTE` exists; `beo_check.py --check execute` confirms complete approval.
- Bead is claimed by current actor/session.

## Owns

- Product mutation inside approved `scope.files.allow` only.
- `execution` evidence and `runtime_events`.

## Stops

- Stale/invalid approval or unclaimed bead.
- Path is outside approved `allow` or matches `forbidden`/protected.
- Stateful mutation without strict-approved contract.

## Exits

- `execution_ready_for_review` -> `beo-review`
- `approval_stale_or_invalid` -> `beo-validate`
- `blocker_found` -> `beo-debug`

## Method

1. Run `beo_check.py --check execute --issue <issue-id>` to confirm approval.
2. Capture prestate hashes for declared files and outputs.
3. Mutate only approved `allow` paths and declared outputs.
4. Record incremented `execution.iteration` for repairs.
5. Run declared verification commands and record evidence refs.
6. Run `beo_check.py --check review --issue <issue-id>` before review handoff.
