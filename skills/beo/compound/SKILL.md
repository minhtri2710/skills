---
name: beo-compound
description: |
  Record one accepted feature learning outcome. Use when verdict=`accept` and acceptance evidence is complete, or when an existing feature learning file lacks a recorded disposition. Do not use when cross-feature consolidation is requested.
metadata:
  dependencies:
    - id: beads-cli
      kind: command
      command: br
      missing_effect: degraded
      reason: Helpful for feature provenance, but accepted artifact bundles can still support the learning write.
---
# beo-compound

## Purpose
Record one accepted feature learning outcome.

## Primary owned decision
Decide whether one accepted feature has durable or unclear learning and record that feature-level outcome. Obvious isolated no-learning cases do not trigger this owner; they complete in `beo-review → done`.

## Ownership predicate
- `REVIEW.md` has verdict=`accept` for one feature.
- Acceptance evidence is complete.
- Feature learning is durable, or disposition is unclear and not an obvious isolated no-learning case.
- Cross-feature consolidation is not the requested work.

## Writable surfaces
- `.beads/learnings/<feature_slug>.md` or the feature-local learning record described by canonical learning doctrine.
- Shared state/handoff fields allowed by `beo-reference -> skill-contract-common.md`.

> Canonical: `beo-reference -> learning.md`
> Locally enforced as:
> - Use durable-learning and no-learning thresholds from the canonical learning rules.
> - Record only one feature outcome here.
> - Route corpus-level consolidation to `beo-dream` only when thresholds or explicit request support it.

## Hard stops
- Do not trigger for obvious isolated no-learning cases; those complete via `beo-review → done`.
- Do not promote one feature directly into shared guidance.
- Do not write feature learning without accepted-review evidence.
- Do not reopen implementation or review findings.
- Do not write to `.beads/critical-patterns.md`; that surface is a shared guidance artifact and requires explicit user confirmation before any mutation. Route shared guidance decisions to `beo-dream` with user approval.

## Feature learning disposition card

```md
Feature:
Accepted evidence checked:
Disposition: no-learning | durable-candidate | unclear
Promotion status: none | candidate-only
Continue via:
Authority note: display-only; canonical authority remains in the referenced state/artifact surface.
```

## Allowed next owners
- `beo-dream`
- `user`
- done

## References
- `beo-reference -> artifacts.md` — read when locating accepted feature artifacts and review evidence.
- `beo-reference -> learning.md` — read when classifying durable, unclear, no-learning, or consolidation outcomes.
- `beo-reference -> pipeline.md` — read when selecting legal closure handoffs.
- `beo-reference -> state.md` — read when updating state or handoff surfaces.
