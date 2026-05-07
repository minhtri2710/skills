---
name: beo-dream
description: |
  Use this skill to consolidate cross-feature learning only when threshold evidence or explicit request exists. Use when at least two accepted/finalized feature outcomes support the same shared pattern, or the user explicitly requests corpus-level consolidation. Do not use when only one feature provides evidence and there is no explicit corpus request.
---

# beo-dream

## Purpose

Consolidate cross-feature learning only when threshold evidence or explicit request exists.

## Fast predicate

Active when at least two accepted/finalized feature outcomes support the same shared pattern, or the user explicitly requests corpus-level consolidation.

Not active when only one feature provides evidence and there is no explicit corpus request.

## Primary owned decision

Choose and apply a user-confirmed corpus-level consolidation target.

## Writable surfaces

User-confirmed shared guidance target path; STATE.json closure fields; HANDOFF.json only when pausing/transferring.

## Hard stops

Do not mutate shared guidance without current user-confirmed target path. Do not promote one-feature learning. Do not reopen runtime delivery. Do not implement product changes.

## Allowed next owners

done, user, beo-route

## References

- `beo-reference -> references/pipeline.md`
- `beo-reference -> references/state.md`
- `beo-reference -> references/artifacts.md`
- `beo-reference -> references/approval.md`
- `beo-reference -> references/skill-contract-common.md`
