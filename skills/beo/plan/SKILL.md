---
name: beo-plan
description: |
  Create or repair current-phase design and bead graph. Use when locked requirements exist and planning artifacts need creation or repair. Do not use when requirements are unlocked or contradicted.
metadata:
  dependencies:
    - id: beads-cli
      kind: command
      command: br
      missing_effect: unavailable
      reason: Required to create and update the canonical bead graph.
    - id: beads-viewer
      kind: command
      command: bv
      missing_effect: degraded
      reason: Useful for read-only bead inspection but not required for every planning write.
---
# beo-plan

## Purpose
Create or repair current-phase design and bead graph.

## Primary owned decision
Turn locked requirements into an executable current-phase plan and bead graph.

## Ownership predicate
- Requirements are locked and planning artifacts are absent, stale, or incomplete.
- The bead graph is missing, stale, or inconsistent with locked requirements.
- Validation found content edits needed in plan or bead descriptions.
- Requirements are not unlocked or contradicted.

## Writable surfaces
- `.beads/artifacts/<feature_slug>/PLAN.md`.
- Current-phase bead descriptions and dependency fields owned by planning procedure.
- Shared `STATE/HANDOFF` surfaces under the common contract baseline.

> Canonical: `beo-reference -> complexity.md`
> Locally enforced as:
> - Select the smallest safe planning depth.
> - Include required sections for that depth.
> - Let `beo-validate` classify readiness after planning writes.
> - Compact planning reduces prose only; it never bypasses validation or approval.

## Hard stops
- Do not execute implementation.
- Do not approve readiness.
- Do not plan from unlocked or contradicted requirements.

## Allowed next owners
- `beo-validate`
- `beo-explore`
- `user`
- `beo-route` — only for exceptional owner-state resolution under canonical route doctrine.

## References
- `beo-reference -> artifacts.md` — read when writing `PLAN.md` and bead schema fields.
- `beo-reference -> complexity.md` — read when selecting planning depth and required sections.
- `beo-reference -> cli.md` — read when using shared `br`/`bv` command forms.
- `beo-reference -> approval.md` — read when invalidating stale approval after plan changes.
- `beo-reference -> pipeline.md` — read when selecting the next owner.
- `references/bead-ops.md` — read when mutating planned current-phase bead descriptions or dependencies.
