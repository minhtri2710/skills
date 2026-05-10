---
name: beo-debug
description: |
  Use this skill to prove one blocker root cause. Use when root cause is unproven and mutation or verdicting would be unsafe without diagnosis. Do not use when the fix is known and belongs to execute/plan/validate/review.
---

# beo-debug

## Purpose
Prove one blocker root cause.

## Active when
Root cause is unproven and mutation or verdicting would be unsafe without diagnosis.

## Owns
Return proven cause and smallest legal unblock class.

## Reads
- current debug_return anchor when entered from execution/review
- direct blocker evidence
- current required surfaces needed to prove the blocker
- `debug/references/diagnostic-checklist.md` (required before emitting output)
- `beo-reference -> references/tool-contracts.md` (read only for diagnostic commands)

## Writes
- diagnostic notes in owner output
- debug_return fields when owned by sender handoff
- HANDOFF only when pausing/transferring

## Must stop when
- patch text would be needed
- mutation command would be needed
- approval/readiness/verdict would be emitted
- no debug_return anchor exists when required
- Enforce shared owner stops from `beo-reference -> references/skill-contract-common.md`.

## Return shape
Canonical output shape lives in `debug/references/diagnostic-checklist.md`. Read that file before emitting debug output. Debug output is invalid unless it includes `Patch text: none` and `Mutation command: none`.

## Exit map
| Condition | Next owner |
| --- | --- |
| proven cause, return owner still legal | return owner |
| plan repair class | beo-plan |
| validate refresh class | beo-validate |
| explore clarification class | beo-explore |
| user blocker | user |
| unsafe owner/feature identity | beo-route |
| concrete workflow-learning case, no runtime return | beo-compound |

## References
- `beo-reference -> references/pipeline.md`
- `debug/references/diagnostic-checklist.md`
- `beo-reference -> references/skill-contract-common.md`
- `beo-reference -> references/tool-contracts.md` (read only for diagnostic commands)
