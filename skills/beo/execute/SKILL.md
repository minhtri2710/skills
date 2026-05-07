---
name: beo-execute
description: |
  Use this skill to deliver exactly one selected approved execution set. Use when current readiness is PASS_EXECUTE and approval_ref, execution_set_id, execution_set_beads, execution_mode, declared files, and verification contract are present and fresh. Do not use when readiness, approval, or execution set is missing/stale, or review/debug owns the next decision.
---

# beo-execute

## Purpose

Deliver exactly one selected approved execution set.

## Fast predicate

Active when current readiness is PASS_EXECUTE and approval_ref, execution_set_id, execution_set_beads, execution_mode, declared files, and verification contract are present and fresh.

Not active when readiness, approval, or execution set is missing/stale, or review/debug owns the next decision.

## Primary owned decision

Implement the selected approved execution set inside the current approval envelope.

## Writable surfaces

approved declared files for selected beads; declared generated outputs; .beads/artifacts/<feature_slug>/execution-bundle.json; STATE.json fields needed for execution handoff; HANDOFF.json only when pausing/transferring.

## Hard stops

Do not mutate without PASS_EXECUTE, fresh approval_ref, selected execution set, or approved declared file scope. Do not mutate outside scope. Do not continue if approval becomes stale. Do not continue ordered batch after a bead blocks. Do not coordinate external workers. Do not decide review verdict. Do not prove root cause by guessing; route to beo-debug.

## Allowed next owners

beo-review, beo-debug, beo-plan, user, beo-route

## References

- `beo-reference -> references/pipeline.md`
- `beo-reference -> references/state.md`
- `beo-reference -> references/artifacts.md`
- `beo-reference -> references/approval.md`
- `beo-reference -> references/skill-contract-common.md`
