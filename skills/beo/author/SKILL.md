---
name: beo-author
description: |
  Author, review, or harden beo skill contracts. Use when creating, rewriting, simplifying, deduping, normalizing, reviewing, or performing manual prose pressure review of beo skill definitions and skill-local writing guidance. Do not use for runtime delivery, checker scripts, fixture suites, release gates, governance validation, topology changes, automated evals, benchmarks, or product implementation.
metadata:
  dependencies: []
---
# beo-author

## Purpose
Author, review, or harden beo skill contracts.

## Primary owned decision
Decide the safe wording, placement, dedupe, and manual prose pressure review shape for beo doctrine without taking runtime delivery ownership.

## Ownership predicate
- A beo skill contract or skill-local writing guide needs authoring, review, simplification, dedupe, or normalization.
- Manual prose pressure review is requested for beo contracts.
- A proposed doctrine edit needs owner-boundary or anti-goal review.
- The request is not runtime delivery, checker implementation, topology change, or product work.

## Writable surfaces
- `skills/beo/<skill>/SKILL.md` when the request explicitly targets that skill.
- `skills/beo/<skill>/references/*.md` only for skill-local writing guidance.
- Shared canonical references only when explicitly authoring or repairing doctrine ownership.

## Hard stops
- Do not create release gates, checker scripts, fixture suites, or runtime owners.
- Do not edit runtime artifacts for a feature mission.
- Do not duplicate canonical law into appendices.
- Do not edit own SKILL.md (`beo-author/SKILL.md`) without explicit per-file user request — treat it as a self-modifying governance surface requiring out-of-band confirmation.
- Do not edit any file under `skills/beo/reference/` (SKILL.md or references/*.md) without explicit per-file user request, even under general "repair doctrine ownership" authorization — shared references require targeted user confirmation.

## Allowed next owners
- `beo-route`
- `user`
- done

## References
- `beo-reference -> operator-card.md` — read when aligning operator-facing output style.
- `beo-reference -> authoring.md` — read when placing doctrine, applying frontmatter policy, or reviewing anti-goals.
- `beo-reference -> doctrine-map.md` — read when deciding the canonical owner for a rule.
- `references/skill-writing-method.md` — read when authoring or manually reviewing skill wording.
- `references/manual-pressure-scenarios.md` — read when performing manual prose review of contract pressure scenarios.
