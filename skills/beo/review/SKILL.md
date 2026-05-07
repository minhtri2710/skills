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

.beads/artifacts/<feature_slug>/REVIEW.md; reactive-fix bead descriptions only when allowed by approval/artifact rules; STATE.json verdict/handoff fields; HANDOFF.json only when pausing/transferring.

## Hard stops

Do not implement fixes. Do not accept without required verification evidence. Do not accept if live file-change evidence and bundle disagree. Do not accept if hash coverage is incomplete. Do not accept with P0 or P1 findings. Do not let specialist/lens evidence emit terminal verdict. Do not route to beo-compound merely to ask whether learning exists.

## Allowed next owners

beo-compound, beo-validate, beo-plan, beo-explore, beo-debug, user, done, beo-route

## References

- `beo-reference -> references/pipeline.md`
- `beo-reference -> references/state.md`
- `beo-reference -> references/artifacts.md`
- `beo-reference -> references/approval.md`
- `beo-reference -> references/skill-contract-common.md`
