---
name: beo-route
description: |
  Repairs or selects the active owner only when runtime owner identity is unsafe. Use when owner identity is missing, stale, contradictory, colliding, or feature collision exists during runtime resume or handoff. Not for direct setup/usage/meta requests, or normal startup when a valid current owner can continue.
---

# beo-route

## Purpose

Restore one safe current owner identity.

## Decision Card

Decision: repair unsafe owner/feature identity metadata only.

Can enter when:
- owner or active feature identity is missing, stale, contradictory, colliding, or unsafe

Can write:
- STATE/HANDOFF identity metadata only as allowed by `references/state.md`

Must stop when:
- no identity defect exists or artifacts cannot prove a safe repair

Exit summary (non-authoritative):
- `identity_repaired` -> `restored_owner`
- `user_decision_needed` -> `user`

Never:
- handle normal startup, select setup, repair runtime artifacts, approve, execute, review, or mutate product files

Reads:
- state, route resolution, resume resolution, current artifacts, and pipeline

## Contract

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

Acts when:
- owner or active feature identity is unsafe

Owns:
- owner identity repair only

Local stops:
- no owner/feature identity defect is present
- the request is a direct non-runtime setup, usage, meta, product, approval, execution, review, or learning request

Writes:
- STATE/HANDOFF identity metadata only when allowed by `beo-reference -> references/state.md`

Reads:
- `beo-reference -> references/state.md`, `beo-reference -> references/route-resolution.md`, `beo-reference -> references/resume-resolution.md`, current artifacts, `beo-reference -> registry/pipeline.json`

Local forbids:
- normal runtime work, approval, execution, review, product mutation

Exits:
- `identity_repaired` -> `restored_owner`
- `user_decision_needed` -> `user`

## Route Defects

Route only for missing, stale, contradictory, colliding, or unsafe owner/feature identity. Route is rare and is not normal startup or handoff.

## Route Rule

Use route only after owner/feature identity is unsafe; otherwise stay with the current legal owner or stop under the common contract.

Artifacts beat STATE/HANDOFF. Repair identity metadata only. Never repair requirements, plan, approval, execution evidence, review, or product files. If no artifact-derived owner is safe, stop for user.

Use `beo-reference -> references/route-resolution.md` for `return_to_caller` legality, symbolic `restored_owner` semantics, and operator output shape. After identity repair, use `beo-reference -> references/resume-resolution.md` for concrete target orientation.
