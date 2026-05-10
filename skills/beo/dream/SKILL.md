---
name: beo-dream
description: |
  Use this skill to consolidate multiple finalized BEO learning cases into one recurring pattern or skill-improvement candidate. Use when at least two finalized learning cases support the same workflow pattern, or the user explicitly asks to consolidate learning. Do not use for one isolated case, runtime delivery, product implementation, direct skill edits, or speculative doctrine.
---

# beo-dream

## Purpose
Consolidate multiple finalized learning cases into one recurring pattern or skill-improvement candidate without editing skills, shared doctrine, or product files.

## Active when
At least two finalized learning cases support the same recurring BEO workflow pattern, or the user explicitly requests learning consolidation.

## Owns
Decide whether multiple finalized cases justify one consolidated pattern, then write only the consolidation output or no-consolidation decision.

## Reads
- finalized learning cases needed for the pattern
- `beo-reference -> references/learning.md`

## Writes
- `.beads/learnings/<pattern_slug>.md` as a consolidated learning pattern
- STATE closure fields only when needed
- HANDOFF only when pausing/transferring

## Must stop when
- only one case exists without explicit user consolidation request
- runtime delivery is still open
- skill edits or doctrine changes would be made directly
- Enforce shared owner stops from `beo-reference -> references/skill-contract-common.md`.

## Exit map
| Condition | Next owner |
| --- | --- |
| consolidation complete | done |
| pattern recommends skill update, user confirms | beo-author |
| user decision needed | user |

## References
- `beo-reference -> references/learning.md`
- `beo-reference -> references/skill-contract-common.md`
