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
- Existing shared learning guidance needs consolidation from accepted feature records only when the consolidation threshold is met.
- A single-feature case is in scope only when the user explicitly asks for corpus-level analysis.

## Writable surfaces
- Shared learning guidance surfaces explicitly approved by the user. When approval grants shared-guidance mutation, write to the user-confirmed target file path only. Do not infer a canonical shared guidance location; if no target path has been confirmed, surface the path choice to the user before writing.
- Consolidation records described by canonical learning doctrine.
- Shared state/handoff fields allowed by `beo-reference -> skill-contract-common.md`.

> Canonical: `beo-reference -> learning.md`
> Locally enforced as:
> - Use canonical consolidation thresholds.
> - Do not promote one feature without an explicit corpus-level request.
> - Do not write feature-level learning; use `beo-compound` for that.

## Hard stops
- Do not mutate shared guidance without threshold or explicit corpus-request evidence.
- Do not implement product changes or reopen review.
- Do not infer shared doctrine from isolated evidence.
- Do not write feature-level learning records; that is `beo-compound`'s surface (`beo-compound` owns single-feature, feature-local records; `beo-dream` owns multi-feature cross-feature shared guidance). Route single-feature outcomes to `beo-compound` before consolidation.

## Corpus consolidation card

```md
Candidate:
Source features checked:
Threshold evidence:
Conflict check:
Decision: consolidation-candidate | no-promotion | needs-user
Authority note: display-only; canonical authority remains in the referenced state/artifact surface.
```

## Allowed next owners
- `user`
- done

## References
- `beo-reference -> operator-card.md` — read when formatting operator-facing consolidation results.
- `beo-reference -> learning.md` — read when applying consolidation thresholds and provenance rules.
- `beo-reference -> pipeline.md` — read when choosing legal closure handoffs.
- `beo-reference -> state.md` — read when updating state or handoff surfaces.
