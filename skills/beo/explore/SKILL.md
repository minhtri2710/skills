---
name: beo-explore
description: Locks BEO feature requirements and Human Gate status before planning.
---

# beo-explore

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

## Decision

Lock requirements and Human Gate status.

## Enter

- New feature request.
- Stale, missing, unclear, or contradicted requirements.
- Missing, stale, or contradicted Human Gate status.

## Owns

- Request.
- Done target.
- Assumptions, non-goals, and constraints.
- Human Gate discovery and recorded status.

## Writes

- `FEATURE.json` identity seed.
- Compact explore-owned fields in `TICKET.md`.
- Full `CONTEXT.md`.
- Legal transition metadata.

## Stops

- Required user input is unresolved.
- Requirements remain contradictory.
- Owner/feature identity is unsafe.

## Exits

- `requirements_locked` -> `beo-plan`
- `human_gate_unresolved` -> `user`
- `user_abandoned` -> `done`
- `owner_feature_identity_unsafe` -> `beo-route`

## Method

1. Capture the bounded request and success target.
2. Separate blocking Human Gates from safe assumptions.
3. Record gate status and resolution refs without storing secrets.
4. Write only explore-owned fields.
5. Hand off with exactly one legal condition and transition provenance when applicable.
