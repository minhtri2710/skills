---
name: beo-plan
description: |
  Use this skill to turn locked requirements into executable scope. Use when locked requirements exist and plan, bead graph, file scope, generated outputs, risk proof, rollback boundary, or verification contract is missing, stale, or invalid. Do not use when requirements are unlocked or contradicted.
---

# beo-plan

## Purpose

Turn locked requirements into executable scope.

## Fast predicate

Active when locked requirements exist and plan, bead graph, file scope, generated outputs, risk proof, rollback boundary, or verification contract is missing, stale, or invalid.

Not active when requirements are unlocked or contradicted.

## Primary owned decision

Create or repair the current executable plan.

## Writable surfaces

.beads/artifacts/<feature_slug>/PLAN.md; current-phase bead graph descriptions and dependencies; STATE.json stale readiness/approval mirror clearing when approval-bearing content changes; HANDOFF.json only when pausing/transferring.

## Hard stops

Do not plan from unlocked or contradicted requirements. Do not implement. Do not approve readiness. Do not emit PASS_EXECUTE. Do not route for a plan defect that beo-plan owns. If plan changes approval-bearing content, clear stale readiness and approval mirrors in the same handoff.

## Allowed next owners

beo-validate, beo-explore, user, beo-route

## References

- `beo-reference -> references/pipeline.md`
- `beo-reference -> references/state.md`
- `beo-reference -> references/artifacts.md`
- `beo-reference -> references/approval.md`
- `beo-reference -> references/skill-contract-common.md`
