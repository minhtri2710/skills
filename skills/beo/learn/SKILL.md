---
name: beo-learn
description: Mandatory learning capture from successes, failures, near misses, or debug patterns. Use this skill whenever a learning candidate is emitted to prevent repeated mistakes and preserve reusable patterns.
---

# beo-learn

Refs: `beo-reference -> references/memory.md`.

## Decision

Record smallest reusable lesson with provenance.

## Enter

- `beo-review` or `beo-debug` marked a learning candidate.
- User consolidated BEO learning evidence.

## Owns

- Case notes, patterns, backend metadata.

## Stops

- Evidence insufficient/non-reusable.
- Reopens delivery or mutates product files.

## Exits

- `case_recorded` -> `done`
- `authoring_requested` -> `beo-author`

## Method

1. Identify `case_type` (e.g., `success_pattern`, `recurring_mistake`).
2. Extract only reusable lesson, trigger, rule, and provenance.
3. Name: `YYYY-MM-DD--<case-type>--<bead-id>--<slug>.md`.
4. Follow backend and secret policy in `beo-reference -> references/memory.md`.
5. Route to `beo-author` only for doctrine changes; write `AUTHORING_RECOMMENDATION.md`.
