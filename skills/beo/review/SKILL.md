---
name: beo-review
description: |
  Use this skill to emit exactly one terminal verdict from finalized execution evidence. Use when tiny TICKET.md execution evidence or standard TRACKER.json execution evidence is finalized and ready for review. Do not use when implementation fixes, readiness refresh, or root-cause proof is needed.
---

# beo-review

## Purpose
Emit one terminal verdict from finalized execution evidence.

## Active when
Execution evidence is finalized and ready for cold review.

## Owns
Decide accept, fix, or reject from current evidence, scope, verification, and acceptance requirements.

## Reads
- current required requirement/plan/tracker surfaces
- finalized execution evidence
- live declared files
- integrity evidence when needed
- review surface if already created
- `beo-reference -> references/approval.md` (read only for stale approval check)
- `review/references/review-operations.md` (read only for verdict routing and bounded repair packet)
- `beo-reference -> references/tool-contracts.md` (read only before using workflow-visible commands)

## Writes
- Tiny: `TICKET.md` Review/Closure
- Standard: `REVIEW.md` and `TRACKER.json.review_pointer`
- STATE verdict/closure fields
- No implementation or review-created fix bead mutation

## Must stop when
- execution evidence is missing/vague
- approval/integrity is stale/invalid/unavailable
- generated outputs are undeclared (ART-06)
- review would rely on memory/chat (REV-01)
- fix implementation is needed
- Enforce shared owner stops from `beo-reference -> references/skill-contract-common.md`.

## Exit map
| Condition | Next owner |
| --- | --- |
| accept, no learning case | done |
| accept, concrete learning_source | beo-compound |
| known bounded repair | beo-plan |
| fix/reject with unproven root cause | beo-debug |
| requirements contradiction | beo-explore |
| approval/integrity refresh needed | beo-validate |
| unsafe owner/feature identity | beo-route |

## Verdict routing
Learning routing is exceptional; enforce `beo-reference -> references/learning.md`. Route to `beo-compound` only with canonical `learning_source` provenance after the runtime verdict is complete.

## References
- `beo-reference -> references/approval.md` (read only for stale approval check)
- `beo-reference -> references/pipeline.md`
- `beo-reference -> references/learning.md` (read only for learning routing)
- `review/references/review-operations.md` (read only for verdict routing and bounded repair packet)
- `beo-reference -> references/skill-contract-common.md`
- `beo-reference -> references/tool-contracts.md` (read only before using workflow-visible commands)
