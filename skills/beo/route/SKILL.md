---
name: beo-route
description: |
  Use this skill to repair or select the active owner only when owner identity is unsafe. Use when owner identity is missing, stale, contradictory, colliding, or feature collision exists. Do not use when a valid current owner can continue or a normal legal handoff is obvious.
---

# beo-route

## Purpose

Repair or select the active owner only when owner identity is unsafe.

## Fast predicate

Active when owner identity is missing, stale, contradictory, colliding, or feature collision exists.

Not active when a valid current owner can continue or a normal legal handoff is obvious.

## Primary owned decision

Select one next owner or route to user for feature collision.

## Writable surfaces

STATE.json fields needed for owner repair; HANDOFF.json only when pausing/transferring.

## Hard stops

Do not implement product changes. Do not approve readiness. Do not emit PASS_EXECUTE. Do not review or verdict. Do not repair artifacts owned by the selected runtime owner. Do not route merely because an artifact defect exists if a current owner legally owns that repair.

## Allowed next owners

beo-explore, beo-plan, beo-validate, beo-execute, beo-review, beo-debug, beo-compound, beo-dream, user

## References

- `beo-reference -> references/pipeline.md`
- `beo-reference -> references/state.md`
- `beo-reference -> references/artifacts.md`
- `beo-reference -> references/approval.md`
- `beo-reference -> references/skill-contract-common.md`
