---
name: beo-validate
description: |
  Classifies readiness and selects the next legal execution set. Use when requirements and plan exist but readiness, approval, execution-set selection, recorded Human Gate status evaluation, approval_ref, or integrity evidence is needed. Not for implementation, review verdicting, Human Gate capture/resolution, or requirements/plan authoring.
---

# beo-validate

## Purpose

Own the readiness gate and approval envelope.

## Decision Card

Decision: classify readiness and select the next legal execution set.

Can enter when:
- current requirements and plan are ready for approval evaluation

Can write:
- Approval section fields and allowed STATE/HANDOFF transition metadata

Must stop when:
- approval inputs or recorded Human Gate status are missing, stale, invalid, contradictory, or unavailable

Exit summary (non-authoritative):
- `PASS_EXECUTE` -> `beo-execute`
- `FAIL_PLAN` -> `beo-plan`
- `FAIL_EXPLORE` -> `beo-explore`
- `BLOCK_USER` -> `user`
- `FAIL_STATE` -> `beo-route`

Never:
- mutate product files, resolve Human Gates, write non-Approval sections, or emit verdicts

Reads:
- current artifacts and `beo-reference -> references/decision-boundaries.md` for Human Gate lifecycle
- `beo-reference -> references/approval.md`, `beo-reference -> registry/artifact-schemas.json`, `beo-reference -> registry/approval-envelope.json`, and `beo-reference -> registry/pipeline.json`

## Contract

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

Acts when:
- current artifacts are ready for approval evaluation

Owns:
- `PASS_EXECUTE` or failure readiness, full approval ref, integrity object, selected execution set, and execution mode

Writes:
- compact/full Approval section only and allowed STATE/HANDOFF transition metadata

Reads:
- current artifacts, `beo-reference -> references/approval.md`, `beo-reference -> references/decision-boundaries.md`, `beo-reference -> registry/approval-envelope.json`, `beo-reference -> registry/artifact-schemas.json`, `beo-reference -> registry/pipeline.json`

Local stops:
- readiness inputs are missing, stale, invalid, contradictory, or unavailable
- recorded Human Gate status is unresolved, missing, stale, or contradictory
- required user input for a Human Gate is absent
- owner/feature identity is unsafe

Local forbids:
- product files, execution evidence, terminal verdicts, non-Approval artifact sections
- resolving Human Gates

Exits:
- `PASS_EXECUTE` -> `beo-execute`
- `FAIL_PLAN` -> `beo-plan`
- `FAIL_EXPLORE` -> `beo-explore` for missing, stale, contradictory, or unresolved recorded Human Gate status
- `BLOCK_USER` -> `user` only when required user input is absent
- `FAIL_STATE` -> `beo-route`

## Compact derived projection

Evaluate compact shorthand through the approval-bearing projection defined by `beo-reference -> references/approval.md` and `beo-reference -> registry/approval-envelope.json`.

## Approval fields

Write flat approval fields only:
- `readiness`
- `approval_ref`
- `integrity`
- `selected_execution_set`
- `execution_mode: normal`

`approval_ref.artifact_hashes.approval_bearing_projection` records the approved snapshot. `integrity.status` records helper evidence and must include `evidence_ref` when verified.

Repair and rollback require normal selected execution-set approval.
