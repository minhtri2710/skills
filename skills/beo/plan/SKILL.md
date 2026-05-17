---
name: beo-plan
description: Converts locked BEO requirements into executable scope and verification.
---

# beo-plan

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

## Decision

Convert locked requirements into an executable contract.

## Enter

- Requirements are locked and plan/scope/verification is missing, stale, invalid, or contradicted.
- Proven bounded repair needs scoped work.

## Owns

- Declared files and forbidden paths.
- Generated outputs, execution sets, risk, and rollback.
- Acceptance criteria and verification contract.

## Writes

- Plan-owned compact fields in `TICKET.md`.
- Full `PLAN.md` non-Approval sections.
- Legal transition metadata.

## Stops

- Requirements are missing or contradicted.
- Required Human Gate input is absent.
- A Human Gate answer exists but `beo-explore` has not recorded current gate status.
- Owner/feature identity is unsafe.

## Exits

- `plan_complete` -> `beo-validate`
- `requirements_missing_or_contradicted` -> `beo-explore`
- `human_gate_blocks_planning` -> `user` when required input is absent, then `beo-explore` records the answer before planning resumes
- `user_abandoned` -> `done`
- `owner_feature_identity_unsafe` -> `beo-route`

## Method

1. Read locked requirements and Human Gate status.
2. Define the smallest executable scope and forbidden paths.
3. Define acceptance criteria and verification commands.
4. Use `beo-reference -> references/density.md` to select compact or full.
5. Hand off with exactly one legal condition and transition provenance when applicable.
