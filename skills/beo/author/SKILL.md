---
name: beo-author
description: Edits BEO doctrine, references, registries, templates, and skill contracts from explicit authoring requests or selected reusable learning evidence.
---

# beo-author

Refs: `beo-reference -> references/kernel.md`.

## Decision

Apply doctrine, skill, template, or registry changes.

## Enter

- User requests BEO doctrine, skill, template, or registry edit.
- `beo-learn` recommends authoring with selected evidence.

## Owns

- Doctrine text, owner contracts, registries, templates, and skill updates.

## Stops

- Evidence is missing or change weakens kernel invariants.
- Mutation belongs to product delivery, not control-plane.

## Exits

- `skill_authored_or_updated` -> `done`
- `reference_or_registry_updated` -> `done`

## Method

1. Identify canonical home for the rule.
2. Remove duplicate wording; keep one authority and short pointers.
3. Preserve `br` lifecycle, BEO safety split, and review separation.
4. Update affected owner contracts and registries together.
5. Tighten existing owner skills or canonical references before creating new skills.
6. Run validators (e.g. `beo_registry_check.py`) after any change.
