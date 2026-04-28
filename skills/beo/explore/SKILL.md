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
Lock feature requirements into `CONTEXT.md`.

## Enter when
- feature intake starts
- `CONTEXT.md` is absent
- a required requirement section is missing
- the artifact is unlocked
- newer explicit user clarification contradicts locked requirements

## Writable surfaces
- `.beads/artifacts/<feature_slug>/CONTEXT.md` while locking or repairing requirements
- shared `STATE/HANDOFF` surfaces under `beo-references -> skill-contract-common.md`

## Decision packet
- shared decision packet under `beo-references -> skill-contract-common.md`
- no local packet extensions beyond requirement-lock evidence in `CONTEXT.md`

## Local hard stops
- Do not lock requirements while acceptance, non-goals, compatibility, constraints, or user-visible scope remain materially ambiguous.
- Do not turn design-only choices into requirement churn.
- When `go_mode.active=true`, prefer conservative assumptions for implementation-detail ambiguity that does not change locked requirement meaning.

## Allowed next owners
- beo-plan
- user

## References
- `beo-references -> operator-card.md`
- `beo-references -> artifacts.md`
- `beo-references -> pipeline.md`
- `beo-references -> state.md`
- `references/intake-bootstrap.md`
- `references/gray-area-probes.md`
