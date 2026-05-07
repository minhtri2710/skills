---
name: beo-debug
description: |
  Use this skill to prove one blocker root cause. Use when root cause is unproven and mutation or verdicting would be unsafe without diagnosis. Do not use when the fix is known and belongs to execute/plan/validate/review.
---

# beo-debug

## Purpose

Prove one blocker root cause.

## Fast predicate

Active when root cause is unproven and mutation or verdicting would be unsafe without diagnosis.

Not active when the fix is known and belongs to execute/plan/validate/review.

## Primary owned decision

Return proven cause and the smallest legal unblock action class.

## Writable surfaces

Diagnostic notes in owner output; STATE.json debug_return fields when the active owner owns that handoff; HANDOFF.json only when pausing/transferring.

## Hard stops

Do not implement the fix. Do not describe the patch. Do not approve readiness. Do not emit review verdict. Do not authorize rollback. Do not change debug_return.return_to unless evidence proves it invalid.

## Allowed next owners

beo-execute, beo-review, beo-plan, beo-validate, beo-explore, user, beo-route

## References

- `beo-reference -> references/pipeline.md`
- `beo-reference -> references/state.md`
- `beo-reference -> references/artifacts.md`
- `beo-reference -> references/approval.md`
- `beo-reference -> references/skill-contract-common.md`
