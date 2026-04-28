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
Author or harden beo contract wording without taking ownership of runtime delivery or topology.

## Enter when
- the user requests a new beo skill contract
- the user requests rewriting, simplifying, deduping, or normalizing an existing beo contract
- the user requests manual pressure scenarios or contract hardening
- the user requests audit or review of beo skill wording

## Writable surfaces
- `skills/beo/<skill>/SKILL.md` when the request explicitly targets that skill
- `skills/beo/<skill>/references/*.md` only for skill-local writing guidance
- `references/skill-writing-method.md`
- shared `STATE/HANDOFF` surfaces under `beo-references -> skill-contract-common.md`

## Manual pressure default
For beo workflow improvement requests, prefer dedupe, simplification, canonical-source cleanup, and manual pressure review.
For audits or hardening requests, prefer manual pressure scenarios over checker scripts or eval fixtures.
Unless the user requests otherwise, pressure-test at least:
- one happy path
- one owner collision
- one stale approval or stale handoff case
- one forbidden-surface temptation
- one debug return or rollback case
- one user-clarification vs go-mode case

## Allowed next owners
- beo-route
- done
- user

## Local hard stops
- Do not add checker scripts.
- Do not add fixture suites.
- Do not add release gates.
- Do not change runtime topology.
- Do not take over product delivery files.
- Before routing to `done`, inherit the terminal done rule from `beo-references -> state.md`.

## References
- `beo-references -> operator-card.md`
- `beo-references -> authoring.md`
- `beo-references -> anti-goals.md`
- `references/skill-writing-method.md`
- `references/manual-pressure-scenarios.md`
