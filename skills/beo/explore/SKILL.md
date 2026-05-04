---
name: beo-explore
description: |
  Lock feature requirements. Use when a missing answer can change acceptance, non-goals, compatibility, constraints, or user-visible scope. Do not use when work is design-only choices.
metadata:
  dependencies: []
---
# beo-explore

## Purpose
Lock feature requirements.

## Primary owned decision
Produce or repair locked `CONTEXT.md` requirements before design or implementation.

## Ownership predicate
- Feature intake starts and `CONTEXT.md` is absent.
- Required requirements, constraints, compatibility, non-goals, or acceptance criteria are missing.
- New explicit user clarification contradicts locked requirements.
- A missing answer can materially change user-visible scope, acceptance criteria, non-goals, or constraints.
- The work is not merely a design-style choice or an implementation detail inside locked requirements; those belong to `beo-plan`.

## Writable surfaces
- `.beads/artifacts/<feature_slug>/CONTEXT.md` while locking or repairing requirements.
- Invalidate current `approval-record.json` and clear approval/readiness mirrors when requirement edits make approval stale.
- Shared state/handoff fields allowed by `beo-reference -> skill-contract-common.md`.

## Hard stops
- Do not plan or implement while requirements are unlocked or contradicted.
- Do not ask for clarification when the answer cannot affect acceptance or scope.
- Do not duplicate artifact schemas locally.

## Allowed next owners
- `beo-plan`
- `user`

## References
- `beo-reference -> operator-card.md` — read when presenting requirement questions or locked scope.
- `beo-reference -> artifacts.md` — read when writing `CONTEXT.md` shape and provenance.
- `beo-reference -> pipeline.md` — read when handing off after requirements lock.
- `beo-reference -> state.md` — read when updating feature state and handoff freshness.
- `references/intake-bootstrap.md` — read when creating a feature slug or first `CONTEXT.md`.
- `references/gray-area-probes.md` — read when choosing non-normative clarification prompts.
