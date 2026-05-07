---
name: beo-compound
description: |
  Use this skill to record one accepted feature learning outcome. Use when review verdict is accept and REVIEW.md records durable-candidate or unclear single-feature learning evidence. Do not use when review has no-learning, review is not accepted, or corpus-level consolidation is requested.
---

# beo-compound

## Purpose

Record one accepted feature learning outcome.

## Fast predicate

Active when review verdict is accept and REVIEW.md records durable-candidate or unclear single-feature learning evidence.

Not active when review has no-learning, review is not accepted, or corpus-level consolidation is requested.

## Primary owned decision

Record a feature-level learning outcome without promoting shared guidance.

## Writable surfaces

.beads/learnings/<feature_slug>.md; STATE.json learning/closure fields; HANDOFF.json only when pausing/transferring.

## Hard stops

Do not reopen review. Do not mutate implementation. Do not promote shared guidance. Do not run corpus consolidation. Do not act without accepted review evidence.

## Allowed next owners

beo-dream, done, user, beo-route

## References

- `beo-reference -> references/pipeline.md`
- `beo-reference -> references/state.md`
- `beo-reference -> references/artifacts.md`
- `beo-reference -> references/approval.md`
- `beo-reference -> references/skill-contract-common.md`
