---
name: beo-review
description: |
  Emit one terminal verdict. Use when execution scope and review evidence bundle are complete. Do not use when fixes must be implemented or root cause must be proven.
metadata:
  dependencies: []
---
# beo-review

## Purpose
Emit one terminal verdict.

## Primary owned decision
Emit exactly one terminal verdict: `accept`, `fix`, or `reject`.

## Ownership predicate
- Execution scope is complete for the current feature or bead set.
- Review evidence includes locked requirements, plan, changed files, verification, and approval reference.
- The requested work is assessment, not implementation or root-cause diagnosis.
- A terminal verdict is needed before closure, learning, or reactive-fix routing.

## Writable surfaces
- `.beads/artifacts/<feature_slug>/REVIEW.md`.
- Reactive-fix bead descriptions only when canonical approval and artifact rules allow them.
- Shared `STATE/HANDOFF` surfaces under the common contract baseline.

> Canonical: `beo-reference -> artifacts.md`
> Locally enforced as:
> - Use the canonical `REVIEW.md` minimum template.
> - Keep specialist prompts evidence-only.
> - Create reactive-fix beads only when the canonical approval rule is satisfied.

## Hard stops
- Do not implement fixes.
- Do not accept without required verification evidence.
- Do not let specialist evidence emit the terminal verdict.

## Allowed next owners
- `beo-compound`
- `beo-execute`
- `beo-plan`
- `beo-explore`
- `beo-debug`
- `user`
- done
- `beo-route` — only when owner state is missing, stale, contradictory, or colliding.

## References
- `beo-reference -> operator-card.md` — read when formatting verdict output.
- `beo-reference -> artifacts.md` — read when writing `REVIEW.md` and reactive-fix bead fields.
- `beo-reference -> approval.md` — read when checking reactive-fix approval retention.
- `beo-reference -> pipeline.md` — read when routing after verdict.
- `beo-reference -> learning.md` — read when splitting accepted-work closure.
- `references/review-specialist-prompts.md` — read when gathering specialist evidence without verdict authority.
