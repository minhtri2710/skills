---
name: beo-plan
description: |
  Turns locked requirements into executable scope. Use when locked requirements exist and plan, file scope, risk scope, rollback boundary, generated outputs, execution sets, or verification contract is missing/stale/invalid. Not for requirements authoring, approval, execution, or review verdicts.
---

# beo-plan

## Purpose

Convert locked requirements into executable scope.

## Decision Card

Decision: convert locked requirements into executable scope.

Can enter when:
- locked requirements need scope, files, risk, rollback, execution sets, or verification

Can write:
- compact `TICKET.md#Scope` or full `PLAN.md` non-Approval sections

Must stop when:
- requirements are missing/contradicted or a Human Gate answer has not been recorded by `beo-explore`

Exit summary (non-authoritative):
- `plan_complete` -> `beo-validate`
- `requirements_missing_or_contradicted` -> `beo-explore`
- `human_gate_blocks_planning` -> `user`
- `owner_feature_identity_unsafe` -> `beo-route`

Never:
- write approval fields, product files, execution evidence, or terminal verdicts

Reads:
- locked requirements and `beo-reference -> references/decision-boundaries.md` for Human Gate lifecycle
- `beo-reference -> references/artifacts.md`, `beo-reference -> references/approval.md`, `beo-reference -> references/state.md`, and `beo-reference -> registry/pipeline.json`

## Contract

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

Acts when:
- requirements are locked and executable scope is missing, stale, invalid, or contradicted
- a proven bounded repair or rollback needs an execution set

Owns:
- declared files, forbidden paths, generated outputs, risk scope, rollback boundary, execution sets, acceptance criteria, and verification contract

Writes:
- compact `TICKET.md#Scope`
- full `PLAN.md` non-Approval sections

Reads:
- locked requirements, `beo-reference -> references/artifacts.md`, `beo-reference -> references/approval.md`, `beo-reference -> references/decision-boundaries.md`, `beo-reference -> references/state.md`, `beo-reference -> registry/pipeline.json`

Local stops:
- requirements are missing or contradicted
- a Human Gate blocks executable scope selection because required user input is absent
- user has answered a Human Gate but `beo-explore` has not recorded current gate status
- owner/feature identity is unsafe

Local forbids:
- approval fields, product files, execution evidence, terminal verdicts

Exits:
- `plan_complete` -> `beo-validate`
- `requirements_missing_or_contradicted` -> `beo-explore`
- `human_gate_blocks_planning` -> `user` when required input is absent, then `beo-explore` records the answer before planning resumes
- `owner_feature_identity_unsafe` -> `beo-route`

## Compact shorthand

Write compact shorthand only as defined by `beo-reference -> references/artifacts.md` and `beo-reference -> registry/artifact-schemas.json`.

Compact scope uses `scope.item` as one string. Do not author expanded projection fields in compact artifacts.

## Repair and rollback planning

Represent repair and rollback as execution sets in full density:
- `kind: repair` for bounded repair inside declared files;
- `kind: rollback` for rollback mutation, with `rollback_from_execution_set`.

Do not add separate repair surfaces or intent-only relationship fields. File-scope validation enforces repair containment.
