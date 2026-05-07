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

Emit exactly one readiness classification and select execution sets from the canonical `PLAN.md` bead graph: PASS_EXECUTE, FAIL_PLAN, FAIL_EXPLORE, BLOCK_USER, or FAIL_STATE.

## Writable surfaces

- `.beads/artifacts/<feature_slug>/readiness-record.json`
- `.beads/artifacts/<feature_slug>/approval-record.json`
- `STATE.json` readiness mirrors
- `HANDOFF.json` only when pausing/transferring

## Hard stops

Do not emit PASS_EXECUTE with missing trace coverage, unresolved required Human Gates, ambiguous hashes, fingerprint-only approval evidence, or mismatched selected execution-set fields. Do not implement. Do not review. Do not emit PASS_EXECUTE without approval_ref. Do not emit PASS_EXECUTE with stale approval. Do not emit PASS_EXECUTE unless the approval record is created or refreshed by beo-validate and its approval hashes match live artifacts. Do not select unsupported execution modes. Do not allow continuation after a blocked ordered-batch bead. Do not use FAIL_STATE for ordinary plan or explore defects. Do not ask user questions unless the blocker is a true Human Gate.

## Allowed next owners

beo-execute, beo-plan, beo-explore, user, beo-route

## References

- `beo-reference -> references/pipeline.md`
- `beo-reference -> references/state.md`
- `beo-reference -> references/artifacts.md`
- `beo-reference -> references/approval.md`
- `beo-reference -> references/skill-contract-common.md`
