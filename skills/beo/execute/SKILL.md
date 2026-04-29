---
name: beo-execute
description: |
  Deliver one approved serial bead. Use when exactly one approved ready bead is selected with mode=`serial` and mutation stays in approved scope. Do not use when root cause is unproven or parallel coordination is required.
metadata:
  dependencies:
    - id: beads-cli
      kind: command
      command: br
      missing_effect: unavailable
      reason: Required to claim bead progress and keep canonical bead state in sync.
---
# beo-execute

## Purpose
Deliver one approved serial bead.

## Primary owned decision
Implement exactly one selected ready bead inside the current approval envelope.

## Ownership predicate
- Readiness is `PASS_SERIAL`.
- Exactly one approved ready bead is selected.
- Approval is current and bounds the intended mutation.
- Root cause is proven when the bead is a bug fix.
- Parallel coordination is not required.

## Writable surfaces
- Code and tests required by the selected bead only.
- Selected bead status/evidence surfaces allowed by execution procedure and status mapping.
- Review evidence bundle fields for changed files, verification, and approval reference.
- Shared `STATE/HANDOFF` surfaces under the common contract baseline.

## Hard stops
- Do not broaden scope beyond the selected bead or approval envelope.
- Do not self-approve readiness or swarm fallback.
- Do not continue after unproven root cause blocks safe implementation.

## Allowed next owners
- `beo-review`
- `beo-debug`
- `beo-plan`
- `beo-validate`
- `user`
- `beo-route` — only when owner state is missing, stale, contradictory, or colliding.

## References
- `beo-reference -> approval.md` — read when checking execution envelope or invalidation.
- `beo-reference -> artifacts.md` — read when updating review evidence bundle fields.
- `beo-reference -> cli.md` — read when using shared `br`/`bv` command forms.
- `beo-reference -> pipeline.md` — read when handing off after execution.
- `beo-reference -> status-mapping.md` — read when updating bead status or labels.
- `references/execution-operations.md` — read when following the local execution loop and exit evidence shape.
