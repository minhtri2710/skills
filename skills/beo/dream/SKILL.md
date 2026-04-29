---
name: beo-dream
description: |
  Consolidate cross-feature learning. Use when at least two accepted features support shared learning, or when the user explicitly requests corpus-level consolidation. Do not use when only one feature provides evidence and no explicit user request exists.
metadata:
  dependencies: []
---
# beo-dream

## Purpose
Consolidate cross-feature learning.

## Primary owned decision
Decide whether accepted feature evidence supports a shared learning update or an explicit non-promotion.

## Ownership predicate
- At least two accepted features support the same shared learning candidate.
- The user explicitly requests corpus-level consolidation.
- Existing shared learning guidance needs consolidation from accepted feature records.
- Only one feature is available only when the user explicitly asks for corpus-level analysis.

## Writable surfaces
- Shared learning guidance surfaces explicitly approved by the user or designated auto-writable by canonical learning doctrine.
- Consolidation records described by canonical learning doctrine.
- Shared `STATE/HANDOFF` surfaces under the common contract baseline.

> Canonical: `beo-reference -> learning.md`
> Locally enforced as:
> - Use canonical consolidation thresholds.
> - Do not promote one feature without an explicit corpus-level request.
> - Do not write feature-level learning; use `beo-compound` for that.

## Hard stops
- Do not mutate shared guidance without threshold or explicit corpus-request evidence.
- Do not implement product changes or reopen review.
- Do not infer shared doctrine from isolated evidence.

## Corpus consolidation card

```md
Candidate:
Source features checked:
Threshold evidence:
Conflict check:
Decision: consolidate | do-not-promote | needs-user
Authority note: This output is valid only when emitted by `beo-dream`. Consolidation requires threshold evidence or an explicit corpus-level user request.
```

## Allowed next owners
- `user`
- done

## References
- `beo-reference -> operator-card.md` — read when formatting operator-facing consolidation results.
- `beo-reference -> learning.md` — read when applying consolidation thresholds and provenance rules.
- `beo-reference -> pipeline.md` — read when choosing legal closure handoffs.
- `beo-reference -> state.md` — read when updating state or handoff surfaces.
