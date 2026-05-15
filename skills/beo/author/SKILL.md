---
name: beo-author
description: |
  Authors or hardens BEO skill contracts and doctrine text. Use when editing or proposing concrete BEO doctrine/skill contract changes, including creating, rewriting, simplifying, deduplicating, or normalizing BEO skill definitions or skill-local writing guidance. Not for generic read-only review, runtime delivery, approval, execution, review verdicting, debugging, learning promotion, or product implementation.
---

# beo-author

## Purpose

Edit doctrine from explicit request, selected consolidated evidence, or selected single-case evidence.

## Decision Card

Decision: edit doctrine from explicit request or selected evidence.

Can enter when:
- concrete BEO doctrine/skill contract changes are explicitly requested or selected evidence requires authoring

Can write:
- BEO skill/doctrine files named by the request

Must stop when:
- owner-specific entry evidence is missing, stale, contradictory, or out of scope

Exit summary (non-authoritative):
- `skill_authored_or_updated` -> `done`
- `user_review_needed` -> `user`

Never:
- mutate runtime artifacts, product files, approvals, execution evidence, review verdicts, or reopen execution

Reads:
- doctrine map, common contract, pipeline, affected owner skill, and selected evidence

## Contract

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

Acts when:
- explicit request to edit or propose concrete BEO doctrine/skill contract changes, selected consolidated evidence requiring authoring, or selected single-case evidence requiring authoring

Owns:
- smallest doctrine/skill change that implements the request while preserving canonical homes

Local stops:
- owner-specific entry evidence is missing, stale, contradictory, or out of scope

Writes:
- BEO skill/doctrine files named by the request

Reads:
- `beo-reference -> references/doctrine-map.md`, `beo-reference -> references/skill-contract-common.md`, `beo-reference -> registry/pipeline.json`, affected owner `SKILL.md`, and current selected evidence

Local forbids:
- runtime artifacts, product files, approvals, execution evidence, review verdicts, reopening execution

Exits:
- `skill_authored_or_updated` -> `done`
- `user_review_needed` -> `user`

## Authoring Method

Keep changes small, preserve one canonical home per decision, remove duplicate/pointer surfaces after references are updated, remove stale terminology, and pressure-read representative scenarios for ambiguity.

## Final Response Contract

When exiting `skill_authored_or_updated`, report:
- changed files;
- canonical home used;
- duplicate pointers updated or removed;
- exit condition;
- unresolved review items, if any.

## Doctrine Refactor Method

When simplifying or deduplicating BEO doctrine:

1. Identify the canonical home from `beo-reference -> references/doctrine-map.md`.
2. Move authority to the canonical home, not to owner files or generated playbooks.
3. Replace duplicates with short pointers unless local trigger clarity requires a summary.
4. Keep owner `SKILL.md` files focused on local entry, ownership, writes, reads, local stops, and exits.
5. Preserve explicit exit `condition_id` -> target pairs.
6. If a rule becomes machine-enforced, keep prose as mental model only and point to the registry/helper.
7. Pressure-read:
   - simple compact feature
   - full multi-item feature
   - stale approval
   - unresolved Human Gate
   - context-loss resume
   - route identity contradiction
   - review fix loop
   - decision card vs. contract and pipeline exit consistency
   - compact template field alignment with artifact-schemas.json
