---
name: beo-author
description: Edits BEO doctrine, reference files, and skill contracts from explicit authoring requests.
---

# beo-author

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

## Decision

Edit BEO doctrine from explicit request or selected evidence.

## Enter

- Concrete doctrine, skill, registry, or reference change is explicitly requested.
- Selected accepted evidence requires authoring.

## Owns

- Workflow text rewrite.
- Owner contract normalization.
- Doctrine refactor.
- Reference compression.

## Writes

- Requested BEO skill/doctrine files only.
- Requested registries or templates when explicitly in scope.

## Stops

- Entry evidence is missing, stale, contradictory, or out of scope.
- Requested mutation is runtime artifact, product file, approval, execution evidence, review verdict, or execution reopen.

## Exits

- `skill_authored_or_updated` -> `done`
- `user_review_needed` -> `user`

## Method

1. Identify the canonical home from `references/doctrine-map.md`.
2. Move authority to the canonical home and replace duplicates with short pointers.
3. Keep owner files focused on the current contract shape: Decision, Enter, Owns, Writes, Stops, Exits, and Method.
4. Preserve legal `condition_id` -> target pairs.
5. Pressure-read simple compact feature, full multi-item feature, stale approval, unresolved Human Gate, context-loss resume, route contradiction, review fix loop, pipeline consistency, and compact schema alignment.

## Final Response Contract

When exiting `skill_authored_or_updated`, report changed files, canonical home used, duplicate pointers updated or removed, exit condition, and unresolved review items.
