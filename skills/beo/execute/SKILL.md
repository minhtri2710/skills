---
name: beo-execute
description: Mutates only the approved scope for one claimed atomic Beads ticket and records execution evidence.
---

# beo-execute

Refs: `beo-reference -> references/safety.md`, `beo-reference -> references/lifecycle.md`.

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
- `scope_delta_required` -> `beo-plan`
- `blocker_found` -> `beo-debug`
- `user_blocker` -> `user`
- `abandoned` -> `beo-review`

## Method

1. Verify approval: Run `beo_check.py --check execute --issue <issue-id>`.
2. Hash pre-state: Capture cryptographic pre-state hashes of all allowed files.
3. Surgical mutation: Modify strictly within approved `allow` files and outputs.
4. Verify changes: Execute declared verification commands and record results.
5. Pre-review: Run `beo_check.py --check review --issue <issue-id>` before review handoff.

