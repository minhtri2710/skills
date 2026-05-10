---
name: beo-compound
description: |
  Use this skill to record one concrete observed workflow-learning case from canonical provenance. Use when a valid learning_source packet exists and runtime safety is not being bypassed. Do not use for vague impressions, runtime repair, consolidation, direct skill edits, or missing provenance.
---

# beo-compound

## Purpose
Record one concrete observed workflow-learning case or agent false case without changing skills, shared doctrine, or implementation.

## Active when
Current evidence includes a concrete workflow-learning case AND a valid canonical `learning_source` packet with `case_status: candidate`.

## Owns
Record exactly one learning case, then close to done unless finalized evidence already requires dream or a user decision.

## Reads
- selected source evidence for one learning case only
- `beo-reference -> references/learning.md`

## Writes
- `.beads/learnings/<case_slug>.md`
- STATE learning/closure fields only when needed for current owner handoff
- HANDOFF only when pausing/transferring

## Must stop when
- canonical `learning_source` is missing
- the case is vague or unsupported
- runtime delivery is still active or a runtime owner still needs repair
- Enforce shared owner stops from `beo-reference -> references/skill-contract-common.md`.

## Exit map
| Condition | Next owner |
| --- | --- |
| learning case recorded | done |
| enough finalized cases for recurring pattern | beo-dream |
| provenance clarification needed | user |

## References
- `beo-reference -> references/learning.md`
- `beo-reference -> references/skill-contract-common.md`
