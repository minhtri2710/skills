---
name: beo-author
description: Use for explicit edits to BEO doctrine, registries, templates, and skill contracts.
---
# beo-author
Refs: `references/kernel.md`.

## Decision
Apply doctrine, skill, template, or registry changes.

## Enter
- User requests BEO doctrine/registry edit.
- `beo-learn` recommends authoring with evidence.

## Owns
- BEO control-plane files (doctrine, contracts, registries, templates).

## Stops
- Change weakens kernel invariants.
- Mutation belongs to product delivery scope.

## Exits
- `skill_authored_or_updated` -> `done`
- `reference_or_registry_updated` -> `done`
- `no_change_needed` -> `done`
- `user_review_needed` -> `user`

## Method
1. Identify canonical home for rule per `references/kernel.md`.
2. Consolidate changes: keep one authority, remove duplicates.
3. Update affected owner contracts and registries together.
4. Run `beo_registry_check.py` to validate control-plane integrity.
