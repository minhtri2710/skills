---
name: beo-validate
description: |
  Use this skill to classify readiness and select the next legal execution or repair path. Use when requirements and plan exist, but readiness, approval, execution set selection, remediation classification, or user-blocker classification is needed. Do not use when implementation, review verdicting, or requirements/plan authoring is needed.
---

# beo-validate

## Purpose

Classify readiness and select the next legal execution or repair path.

## Fast predicate

Active when requirements and plan exist, but readiness, approval, execution set selection, remediation classification, or user-blocker classification is needed.

Not active when implementation, review verdicting, or requirements/plan authoring is needed.

## Primary owned decision

Emit exactly one readiness classification: PASS_EXECUTE, FAIL_PLAN, FAIL_EXPLORE, BLOCK_USER, or FAIL_STATE.

## Writable surfaces

.beads/artifacts/<feature_slug>/readiness-record.json; .beads/artifacts/<feature_slug>/approval-record.json only if validate owns approval recording in this implementation; STATE.json readiness mirrors; HANDOFF.json only when pausing/transferring.

## Hard stops

Do not implement. Do not review. Do not emit PASS_EXECUTE without approval_ref. Do not emit PASS_EXECUTE with stale approval. Do not select unsupported execution modes. Do not allow continuation after a blocked ordered-batch bead. Do not ask user questions unless the blocker is a true Human Gate.

## Allowed next owners

beo-execute, beo-plan, beo-explore, user, beo-route

## References

- `beo-reference -> references/pipeline.md`
- `beo-reference -> references/state.md`
- `beo-reference -> references/artifacts.md`
- `beo-reference -> references/approval.md`
- `beo-reference -> references/skill-contract-common.md`
