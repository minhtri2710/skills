---
name: beo-validate
description: |
  Use this skill to classify readiness and grant or refuse execution approval. Use when locked requirements and plan exist, but readiness, approval, integrity, execution-set selection, remediation classification, or user-blocker classification is needed. Do not use for requirements authoring, plan authoring, implementation, terminal review verdicts, or root-cause proof.
---

# beo-validate

## Purpose
Classify readiness and grant or refuse execution approval.

## Active when
Locked requirements and plan exist, but readiness, approval, integrity, execution-set selection, remediation classification, or user-blocker classification is needed.

## Owns
Emit exactly one readiness classification and record approval/integrity when eligible.

## Reads
- locked requirements
- plan / execution sets
- current approval and integrity evidence
- helper output as evidence only
- `beo-reference -> references/approval.md`
- `beo-reference -> references/approval-integrity.md` (read only for helper output contract)
- `beo-reference -> references/tool-contracts.md` (read only before using workflow-visible commands)

## Writes
- Tiny: `TICKET.md` Approval section
- Standard: `TRACKER.json` readiness/approval/integrity sections
- STATE readiness mirrors
- owner-owned STATE/HANDOFF fields when pausing/transferring

## Must stop when
- trace coverage is missing
- Human Gates are unresolved (HG-01)
- integrity is stale/invalid/unavailable (INT-04)
- selected execution set is missing/contradictory
- generated outputs are undeclared (ART-06)
- `approval_ref` is missing (APP-01)
- Enforce shared owner stops from `beo-reference -> references/skill-contract-common.md`.

## Exit map
| Condition | Next owner |
| --- | --- |
| PASS_EXECUTE | beo-execute |
| plan defect | beo-plan |
| requirement/Human Gate defect | beo-explore or user |
| state/owner identity defect | beo-route |
| concrete learning after classification | beo-compound |

## References
- `beo-reference -> references/approval.md`
- `beo-reference -> references/approval-integrity.md` (read only for helper output contract)
- `beo-reference -> references/pipeline.md`
- `beo-reference -> references/skill-contract-common.md`
- `beo-reference -> references/tool-contracts.md` (read only before using workflow-visible commands)
