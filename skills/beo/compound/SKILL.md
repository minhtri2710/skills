---
name: beo-compound
description: |
  Record one accepted feature learning outcome. Use when verdict=`accept` and acceptance evidence is complete, or when an existing feature learning file lacks a finalized disposition. Do not use when cross-feature consolidation is requested.
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
- an existing feature learning file lacks a finalized disposition

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

## Feature learning taxonomy rule

When a feature learning record is warranted, classify evidence into the BEO learning schema:
- `Patterns`
- `Decisions`
- `Failures / blockers`
- `Applicability`
- `Provenance`
- `Promotion status`

A single feature may mark a learning as a promotion candidate, but it must also record whether second-feature evidence is still needed.
Do not auto-promote feature learning into shared guidance.

## Allowed next owners
- beo-dream
- user
- done

## Local hard stops
- Do not create a standalone learning file for isolated accepted work with no durable reusable signal.
- Do not perform cross-feature consolidation here.
- Do not write to shared consolidation surfaces; that belongs to `beo-dream`.
- Do not auto-promote a single feature into `.beads/critical-patterns.md` or other shared guidance.
- Before routing to `done`, inherit the terminal done rule from `beo-references -> state.md`.

## References
- `beo-references -> artifacts.md`
- `beo-references -> learning.md`
- `beo-references -> pipeline.md`
- `beo-references -> state.md`
