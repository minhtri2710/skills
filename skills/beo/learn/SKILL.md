---
name: beo-learn
description: |
  Records one accepted feature learning case or consolidates repeated accepted-feature cases. Use only after accepted review evidence or explicit corpus request. Not for runtime approval, execution, review, or doctrine authoring.
---

# beo-learn

## Purpose

Capture accepted learning without runtime authority.

## Decision Card

Decision: record accepted learning cases or consolidate repeated accepted-feature patterns.

Can enter when:
- accepted review verdict evidence or explicit consolidation evidence exists

Can write:
- `beo.learning_case.v1` or `beo.learning_pattern.v1` records

Must stop when:
- selected accepted evidence is missing, stale, contradictory, or insufficient

Exit summary (non-authoritative):
- `case_recorded` -> `done`
- `single_case_authoring_requested_with_evidence` -> `beo-author`
- `pattern_consolidated_authoring_requested_with_evidence` -> `beo-author`
- `insufficient_evidence` -> `done`

Never:
- unlock runtime, approve, execute, review, mutate product files, or edit doctrine directly

Reads:
- learning reference, artifact schemas, learning vocabulary, pipeline, and accepted review evidence

## Contract

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

Acts when:
- accepted review verdict with candidate learning or explicit consolidation request with sufficient evidence

Owns:
- learning case or consolidation record

Local stops:
- owner-specific entry evidence is missing, stale, contradictory, or out of scope

Writes:
- `beo.learning_case.v1` records to `.beads/artifacts/<feature_slug>/learning/case-<feature_slug>-<short-topic>.yaml`
- `beo.learning_pattern.v1` records to `.beads/artifacts/<feature_slug>/learning/pattern-<short-topic>.yaml`, only for repeated-pattern consolidation
- Explicitly user-named corpus destinations for `beo.learning_case.v1` or `beo.learning_pattern.v1` records

Reads:
- `beo-reference -> references/learning.md`, `beo-reference -> registry/artifact-schemas.json`, `beo-reference -> registry/learning-vocabulary.json`, `beo-reference -> registry/pipeline.json`, `TICKET.md#Review` or `REVIEW.md`, finalized learning cases, selected finalized evidence

Local forbids:
- runtime unlocks, approval, product mutation, doctrine edits, reopening execution

Exits:
- `case_recorded` -> `done`
- `single_case_authoring_requested_with_evidence` -> `beo-author`
- `pattern_consolidated_authoring_requested_with_evidence` -> `beo-author`
- `insufficient_evidence` -> `done`

## Learning Candidate Source

Learning candidacy is selected by `beo-review` through the `verdict_accept_learning_candidate` transition and recorded in `TICKET.md#Review` or `REVIEW.md` with the accepted verdict evidence.

This is post-review maintenance work after runtime closure. It may use accepted evidence but cannot keep execution open, reopen execution, or change approval/review verdicts.

Explicit consolidation sources are finalized learning cases and accepted review learning sections. Exclude runtime-active, advisory, generated, or non-authoritative artifacts unless explicitly selected by the user.

A single selected case may produce an authoring recommendation through `single_case_authoring_requested_with_evidence`, but it is not a repeated-pattern consolidation. A `beo.learning_pattern.v1` record requires at least two finalized cases supporting the same recurring issue.

`insufficient_evidence` is only for an explicit corpus/consolidation request that has no new recordable case. If an accepted-review handoff lacks current evidence, stop instead of closing the handoff as learned.
