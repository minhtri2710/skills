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
- Invalidate current `approval-record.json` and clear approval/readiness mirrors when plan, bead graph, scope, or verification edits make approval stale.
- Shared state/handoff fields allowed by `beo-reference -> skill-contract-common.md`.

> Canonical: `beo-reference -> complexity.md`
> Locally enforced as:
> - Select the smallest safe planning depth.
> - Include required sections for that depth.
> - Let `beo-validate` classify readiness after planning writes.
> - Compact planning reduces prose only; it never bypasses validation or approval.

## Validation-facing completeness checklist

Before routing to `beo-validate`, planning content should make these facts
explicit when applicable:

- locked requirement source implemented by this plan
- current-phase bead list and dependency order
- declared file scope per bead
- forbidden paths per bead, including explicit `[]` when none apply
- generated outputs per bead, including explicit `[]` when none apply
- verification command or manual verification contract per bead
- risk proof or accepted mitigation for risks that affect acceptance, scope, verification, rollback, security, privacy, migration behavior, or compatibility
- blocker/user-decision fields when a required answer is still missing

This checklist supports planning completeness only. It does not grant
readiness, approval, or execution authority.

## Hard stops
- Do not execute implementation.
- Do not approve readiness.
- Do not plan from unlocked or contradicted requirements.
- When a planning blocker requires root-cause diagnosis, route to `beo-route`; do not create a direct `beo-debug` handoff from plan.
- When writing contract-bearing PLAN.md content where a valid execution approval exists, clear `readiness`, `execution_mode`, `execution_set_id`, `execution_set_beads`, `partial_progress_allowed`, and `approval_ref` from STATE.json in the same write.

## Bead-graph source of truth
`br` is the canonical bead graph. `PLAN.md` bead graph is the mirror. When they diverge, re-read live checked-out artifacts before repairing. If `STATE.json.last_git_ref` does not match the current HEAD, treat the divergence as stale branch state and route to `beo-route` rather than overwriting `PLAN.md`. When branch state is confirmed current, repair `PLAN.md` to match `br` before routing to `beo-validate`.

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
