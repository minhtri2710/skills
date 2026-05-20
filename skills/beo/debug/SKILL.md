---
name: beo-debug
description: Use for read-only root-cause diagnosis of BEO blockers without patching or verdicts.
---
# beo-debug
Refs: `references/lifecycle.md`.

## Decision
Return one read-only diagnosis for a BEO blocker.

## Enter
- Debug handoff event exists or owner requests diagnosis.

## Owns
- Read-only diagnosis artifact, return event, and learning candidate.

## Does Not Own
- Product mutation, repair implementation, approval tokens, review verdicts, issue closure, or learning note persistence.

## Stops
- Diagnosis would require mutation, uncontracted stateful side effects, or unsupported access beyond the handoff scope.

## Exits
- `debug_returned` -> `subroutine_done`
- `debug_abandoned` -> `subroutine_done`

## Method
1. Verify handoff issue, blocker question, target scope, and active claim per `references/lifecycle.md`.
2. Use read-only probes only; `bv` may orient graph risk and `qmd` may recall prior lessons, but neither grants authority.
3. Write one diagnosis artifact and append a `return` event to the ticket.
4. If the pattern is reusable, emit `learning_candidate`; leave persistence to `beo-learn`.
