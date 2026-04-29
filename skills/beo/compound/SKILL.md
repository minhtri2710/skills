---
name: beo-compound
description: |
  Record one accepted feature learning outcome. Use when verdict=`accept` and acceptance evidence is complete, or when an existing feature learning file lacks a finalized disposition. Do not use when cross-feature consolidation is requested.
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
Decide whether one accepted feature has durable learning, unclear learning, or explicit no-learning, and record that feature-level outcome.

## Ownership predicate
- `REVIEW.md` has verdict=`accept` for one feature.
- Acceptance evidence is complete.
- Feature learning is durable, unclear, or not yet finalized.
- Cross-feature consolidation is not the requested work.

## Writable surfaces
- `.beads/learnings/<feature_slug>.md` or the feature-local learning record described by canonical learning doctrine.
- Shared `STATE/HANDOFF` surfaces under the common contract baseline.

> Canonical: `beo-reference -> learning.md`
> Locally enforced as:
> - Use durable-learning and no-learning thresholds from the canonical learning rules.
> - Record only one feature outcome here.
> - Route corpus-level consolidation to `beo-dream` only when thresholds or explicit request support it.

## Hard stops
- Do not promote one feature directly into shared guidance.
- Do not write feature learning without accepted-review evidence.
- Do not reopen implementation or review findings.

## Feature learning disposition card

```md
Feature:
Accepted evidence checked:
Disposition: no-learning | durable-candidate | unclear
Promotion status: none | candidate-only
Continue via:
Authority note: This output is valid only when emitted by `beo-compound`. It records one feature-level outcome only and does not promote shared guidance.
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
