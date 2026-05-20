---
name: beo-execute
description: Mandatory for mutating only validated scope on one claimed atomic Beads ticket and recording execution evidence.
---
# beo-execute
Refs: `references/safety.md`, `references/lifecycle.md`.

## Decision
Deliver exactly one approved atomic ticket scope.

## Enter
- Valid `PASS_EXECUTE` token exists in `TICKET.md`.
- Bead is claimed per `references/lifecycle.md`.

## Owns
- Product mutation strictly within `scope.files.allow`, declared generated outputs, execution evidence, and runtime events.

## Does Not Own
- Scope expansion, approval renewal, review verdicts, issue closure, or memory persistence.

## Stops
- Stale/missing `PASS_EXECUTE`, prestate drift, unauthorized path change, or uncontracted stateful side effect.

## Exits
- `execution_ready_for_review` -> `beo-review`
- `approval_stale_or_invalid` -> `beo-validate`
- `scope_delta_required` -> `beo-plan`
- `blocker_found` -> `beo-debug`
- `user_blocker` -> `user`
- `abandoned` -> `beo-review`

## Method
1. Validate active approval, claim, and prestate hashes per `references/safety.md`.
2. Apply only the approved mutation; if scope must change, stop and route instead of widening locally.
3. Run the ticket's verification commands and record execution evidence.
4. Pre-check containment before review handoff; leave verdict and closure to `beo-review`.
