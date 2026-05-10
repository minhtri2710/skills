---
name: beo-execute
description: |
  Use this skill to deliver exactly one selected approved execution set. Use when current readiness is PASS_EXECUTE and approval_ref, execution_set_id, execution_set_beads, execution_mode, declared files, and verification contract are present and fresh. Do not use when readiness, approval, or execution set is missing/stale, or review/debug owns the next decision.
---

# beo-execute

## Purpose
Deliver exactly one selected approved execution set.

## Active when
Current required surfaces prove `PASS_EXECUTE`, fresh approval, verified integrity, selected execution set, supported execution mode, declared files, forbidden paths, generated outputs, and verification contract.

## Owns
Implement the selected approved execution set inside the approval envelope.

## Reads
- approval envelope
- integrity status
- selected execution set
- declared files / forbidden paths / generated outputs / verification contract
- approved implementation files
- `beo-reference -> references/approval.md`
- `beo-reference -> references/approval-integrity.md` (read only before mutation)
- `execute/references/execution-operations.md` (read only for ordered batch, generated outputs, or verification byproducts)
- `beo-reference -> references/tool-contracts.md` (read only before using workflow-visible commands)

## Writes
- approved declared implementation files
- approved generated outputs
- approved verification byproducts
- execution evidence surfaces
- owner-owned STATE/HANDOFF fields

## Must stop when
- approval/integrity is missing, stale, invalid, unavailable, or contradictory (APP-01)
- intended mutation is outside approved declared files
- ordered batch bead blocks (APP-06)
- root cause is unproven
- Enforce shared owner stops from `beo-reference -> references/skill-contract-common.md`.

## Exit map
| Condition | Next owner |
| --- | --- |
| execution evidence finalized | beo-review |
| root cause unproven | beo-debug |
| approval/integrity stale before mutation | beo-validate or beo-plan |
| known bounded plan/scope repair needed | beo-plan |
| user blocker | user |
| unsafe owner/feature identity | beo-route |
| concrete learning after safe runtime stop | beo-compound |

## References
- `beo-reference -> references/approval.md`
- `beo-reference -> references/approval-integrity.md` (read only before mutation)
- `beo-reference -> references/pipeline.md`
- `beo-reference -> references/skill-contract-common.md`
- `execute/references/execution-operations.md` (read only for ordered batch, generated outputs, or verification byproducts)
- `beo-reference -> references/tool-contracts.md` (read only before using workflow-visible commands)
