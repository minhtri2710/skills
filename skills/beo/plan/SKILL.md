---
name: beo-plan
description: |
  Use this skill to turn locked requirements into executable scope. Use when locked requirements exist and plan, bead graph, file scope, generated outputs, risk proof, rollback boundary, or verification contract is missing, stale, or invalid. Do not use when requirements are unlocked or contradicted.
---

# beo-plan

## Purpose
Turn locked requirements into executable scope.

## Active when
Locked requirements exist and plan, bead graph, file scope, generated outputs, risk proof, rollback boundary, or verification contract is missing, stale, or invalid.

## Owns
Create or repair executable scope and selected execution candidates.

## Reads
- locked requirements
- current plan/tracker if repairing
- artifact and approval references when approval-bearing content changes
- `beo-reference -> references/complexity.md` (read only for tiny reclassification)
- `beo-reference -> references/tool-contracts.md` (read only before using workflow-visible commands)

## Writes
- Tiny: `TICKET.md` Plan section
- Standard: `PLAN.md`; BR task descriptions derived from `PLAN.md`
- Standard: `TRACKER.json` initialization only
- stale approval/readiness mirrors when plan changes stale approval
- owner-owned STATE/HANDOFF fields when pausing/transferring

## Must stop when
- requirements are unlocked or contradicted
- trace coverage is missing for acceptance-critical decisions
- required Human Gate lacks blocking/N/A status (HG-01)
- tiny needs multiple meaningful beads (TINY-02)
- BR descriptions contradict `PLAN.md` (ART-05)
- Enforce shared owner stops from `beo-reference -> references/skill-contract-common.md`.

## Exit map
| Condition | Next owner |
| --- | --- |
| executable scope complete | beo-validate |
| requirements defect | beo-explore |
| required Human Gate unresolved | user |
| unsafe owner/feature identity | beo-route |

## References
- `beo-reference -> references/pipeline.md`
- `beo-reference -> references/artifacts.md`
- `beo-reference -> references/complexity.md` (read only for tiny reclassification)
- `beo-reference -> references/skill-contract-common.md`
- `beo-reference -> references/tool-contracts.md` (read only before using workflow-visible commands)
