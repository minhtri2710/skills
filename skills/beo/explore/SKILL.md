---
name: beo-explore
description: |
  Locks BEO feature requirements before planning, including Human Gate capture/resolution status. Use for every new BEO feature request, and whenever requirements/gates are missing, unclear, or contradicted. Not for planning, readiness validation, execution, review, or setup.
---

# beo-explore

## Purpose

Lock requirements and Human Gate status.

## Decision Card

Decision: lock requirements and Human Gate status.

Can enter when:
- a new feature request starts or requirements/gates are missing, unclear, or contradicted

Can write:
- `FEATURE.json` plus compact Request/Done/Human Gates seed or full `CONTEXT.md`

Must stop when:
- required human input is unresolved or owner/feature identity is unsafe

Exit summary (non-authoritative):
- `requirements_locked` -> `beo-plan`
- `human_gate_unresolved` -> `user`
- `owner_feature_identity_unsafe` -> `beo-route`

Never:
- plan scope, approve, execute, or review

Reads:
- `beo-reference -> references/decision-boundaries.md` for Human Gate lifecycle
- `beo-reference -> references/artifacts.md`, `beo-reference -> references/state.md`, and `beo-reference -> registry/pipeline.json`

## Contract

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

Acts when:
- a new feature request starts, requirements are missing/ambiguous/contradicted, or scope-affecting gates are unresolved

Owns:
- requirements lock and safe assumption boundary

Local stops:
- owner-specific entry evidence is missing, stale, contradictory, or out of scope

Writes:
- `FEATURE.json` manifest, plus compact Request/Done/Human Gates seed in `TICKET.md` or full `CONTEXT.md`

Reads:
- `beo-reference -> references/decision-boundaries.md`, `beo-reference -> references/artifacts.md`, `beo-reference -> references/state.md`, `beo-reference -> registry/pipeline.json`

Local forbids:
- execution scope, approval, product files, review verdicts

Exits:
- `requirements_locked` -> `beo-plan`
- `human_gate_unresolved` -> `user`
- `owner_feature_identity_unsafe` -> `beo-route`
