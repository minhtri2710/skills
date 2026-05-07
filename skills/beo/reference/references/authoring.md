# BEO Authoring

## Owner SKILL.md rewrite standard

Every owner SKILL uses this structure:

```md
---
name: beo-<owner>
description: |
  Use this skill to <one owned decision>. Use when <trigger>. Do not use when <neighboring owner owns it>.
---

# beo-<owner>

## Purpose
One sentence.

## Fast predicate
Active when...
Not active when...

## Primary owned decision
Exactly one decision.

## Writable surfaces
Explicit list.

## Hard stops
Local hard stops only.

## Allowed next owners
Explicit list.

## References
Canonical pointers only.
```

## Rules

- Keep `SKILL.md` lean.
- Do not duplicate multi-step canonical doctrine.
- Keep local hard stops near the owner.
- Use canonical references for approval, artifacts, state, route, learning, and Human Gate rules.
- Do not hide writable surfaces in reference files.
- Use manual prose pressure review for ambiguity; do not add checker, fixture, eval, benchmark, or release-gate requirements.
