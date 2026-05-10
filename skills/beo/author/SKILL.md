---
name: beo-author
description: |
  Use this skill to update existing BEO skills, harden BEO skill contracts, or create a new BEO skill from explicit user request or selected learning-case/pattern evidence. Use when the user asks to modify BEO skills/doctrine, or when a finalized compound case or dream pattern is selected for authoring. Do not use for runtime delivery, product implementation, approval, execution, review verdicting, debugging, or automatic self-modification.
---

# beo-author

## Purpose
Update existing BEO skills or create a new BEO skill from explicit user request or selected observed learning evidence.

## Active when
User explicitly requests BEO skill creation/update/hardening, or when a selected finalized learning case or dream pattern has been explicitly chosen for authoring.

## Owns
Produce the smallest skill/doctrine change that blocks the selected false case or implements the requested BEO skill improvement while preserving owner boundaries and canonical homes.

## Reads
- selected learning case/pattern or files needed for the explicit user-requested skill edit
- `beo-reference -> references/doctrine-map.md`
- `author/references/skill-writing-method.md`

## Writes
- `<skill_name>/SKILL.md` when explicitly updating that skill
- `<skill_name>/references/*` skill-local writing assets when needed
- `beo-reference -> references/*` only when explicitly editing shared doctrine and canonical home is identified
- HANDOFF only when pausing/transferring

## Must stop when
- no explicit request or selected evidence exists
- canonical home for shared doctrine is not identified
- the change duplicates multi-step logic across owner files
- a new skill is created when an existing skill can be hardened
- Enforce shared owner stops from `beo-reference -> references/skill-contract-common.md`.

## Required author output
```md
Decision:
Source request or case:
Canonical home:
Surfaces changed:
Why this blocks the false case or satisfies the request:
Doctrine duplicated? no
Runtime ceremony added? no/yes with reason
Next owner:
```

## Exit map
| Condition | Next owner |
| --- | --- |
| skill update complete | done |
| user confirmation needed | user |

## References
- `beo-reference -> references/doctrine-map.md`
- `beo-reference -> references/skill-contract-common.md`
- `author/references/skill-writing-method.md`
