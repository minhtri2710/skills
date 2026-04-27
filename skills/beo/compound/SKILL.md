---
name: beo-compound
description: |
  Record one accepted feature learning outcome. Use when verdict=`accept`, acceptance evidence is complete, and learning disposition is missing. Do not use when cross-feature consolidation is requested.
---

# beo-compound

## Purpose
Record one accepted feature learning outcome.

## Primary owned decision
Record durable or unclear accepted-work learning for one feature.

## Enter when
- one feature has `REVIEW.md` verdict=`accept`
- acceptance evidence is complete
- durable learning exists or the learning disposition is still unclear

## Writable surfaces
- `.beads/learnings/<feature_slug>.md` or equivalent feature learning record described by `beo-references -> learning.md`
- learning disposition marker for the accepted feature
- shared `STATE/HANDOFF` surfaces under `beo-references -> skill-contract-common.md`

## Decision packet
- shared decision packet under `beo-references -> skill-contract-common.md`
- local learning details belong in the feature learning record or inline disposition marker

## Learning rule

Use the durable-learning and consolidation thresholds in `beo-references -> learning.md`.
Default to inline `no-learning` when no durable reusable decision impact exists.
Do not revisit a review-recorded obvious `no-learning` unless new accepted-work evidence contradicts it.

## Allowed next owners
- beo-dream
- user
- done

## Local hard stops
- Do not create a standalone learning file for isolated accepted work with no durable reusable signal.
- Do not perform cross-feature consolidation here.
- Before routing to `done`, inherit the terminal done rule from `beo-references -> state.md`.

## References
- `beo-references -> learning.md`
- `beo-references -> pipeline.md`
- `beo-references -> state.md`
