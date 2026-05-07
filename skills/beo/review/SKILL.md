---
name: beo-review
description: |
  Use this skill to emit exactly one terminal verdict from finalized execution evidence. Use when the execution bundle is finalized and ready for review. Do not use when implementation fixes, readiness refresh, or root-cause proof is needed.
---

# beo-review

## Purpose

Emit exactly one terminal verdict from finalized execution evidence.

## Fast predicate

Active when the execution bundle is finalized and ready for review.

Not active when implementation fixes, readiness refresh, or root-cause proof is needed.

## Primary owned decision

Decide accept, fix, or reject from evidence, scope, verification, and acceptance requirements.

## Writable surfaces

.beads/artifacts/<feature_slug>/REVIEW.md; STATE.json verdict/handoff fields including closure when status becomes done; HANDOFF.json only when pausing/transferring. No implementation or reactive-fix bead mutation. Review records findings and verdict evidence only.

## Hard stops

Do not accept unless cold review evidence is recorded, trace coverage is complete, verification evidence is specific, required hashes match, and generated outputs are declared or approved verification byproducts. Do not implement fixes. Do not create reactive-fix beads. Any fix routes to beo-plan unless root cause is unproven, in which case route to beo-debug. Do not accept without required verification evidence. Do not accept if live file-change evidence and bundle disagree. Do not accept if hash coverage is incomplete. Do not accept with P0 or P1 findings. Do not let specialist/lens evidence emit terminal verdict. Do not route to beo-compound merely to ask whether learning exists.

## Allowed next owners

beo-compound, beo-plan, beo-explore, beo-debug, user, done, beo-route

## References

- `beo-reference -> references/pipeline.md`
- `beo-reference -> references/state.md`
- `beo-reference -> references/artifacts.md`
- `beo-reference -> references/approval.md`
- `beo-reference -> references/skill-contract-common.md`
