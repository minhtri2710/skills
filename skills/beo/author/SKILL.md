---
name: beo-author
description: |
  Author, audit, or harden beo skill contracts. Use when creating, rewriting, simplifying, deduping, normalizing, reviewing, or pressure-testing beo skill definitions and skill-local writing guidance. Do not use for runtime delivery, checker scripts, fixture suites, release gates, governance validation, topology changes, or product implementation.
metadata:
  dependencies: []
---
# beo-author

## Purpose
Author, audit, or harden beo skill contracts.

## Primary owned decision
Decide the safe wording, placement, dedupe, and pressure-test shape for beo doctrine without taking runtime delivery ownership.

## Ownership predicate
- A beo skill contract or skill-local writing guide needs authoring, audit, simplification, dedupe, or normalization.
- Manual pressure scenarios are requested for beo contracts.
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

## Allowed next owners
- `beo-route`
- `user`
- done

## References
- `beo-reference -> operator-card.md` — read when aligning operator-facing output style.
- `beo-reference -> authoring.md` — read when placing doctrine, applying frontmatter policy, or reviewing anti-goals.
- `beo-reference -> doctrine-map.md` — read when deciding the canonical owner for a rule.
- `references/skill-writing-method.md` — read when authoring or pressure-testing skill wording.
- `references/manual-pressure-scenarios.md` — read when running manual contract pressure scenarios.
