---
name: beo-debug
description: Diagnoses one BEO blocker root cause for a Beads ticket without patching, approving, routing delivery, or issuing verdicts.
---

# beo-debug

Refs: `beo-reference -> references/lifecycle-events.md`.

## Decision

Return one read-only diagnosis for a BEO blocker.

## Enter

- Debug handoff exists or owner requests diagnosis.

## Owns

- Diagnosis artifact, `return` events, `learning_candidate`.

## Stops

- Diagnosis requires product mutation.
- Required evidence unavailable.

## Exits

- `debug_returned` -> `subroutine_done`

## Method

1. Verify handoff issue, return target, and blocker question.
2. Use read-only probes; never patch, approve, or route delivery.
3. Write diagnosis artifact with `diagnosis_status`.
4. Append `return` event with `subtype: debug` and `diagnosis_ref`.
5. Append `learning_candidate` only if the diagnosis pattern is reusable.
