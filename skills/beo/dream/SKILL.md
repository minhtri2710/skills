---
name: beo-dream
description: |
  Consolidate cross-feature learning. Use when at least two accepted features support shared learning or corpus-level consolidation is requested. Do not use when only one feature provides evidence.
---

# beo-dream

## Purpose
Consolidate cross-feature learning.

## Primary owned decision
Consolidate cross-feature learning evidence into a shared conclusion or explicit non-promotion.

## Enter when
- at least two accepted features provide shared learning evidence
- the user explicitly requests corpus-level learning consolidation

## Writable surfaces
- shared learning guidance surfaces explicitly approved by the user or already designated auto-writable by `beo-references -> learning.md`
- consolidation records described by `beo-references -> learning.md`
- shared `STATE/HANDOFF` surfaces under `beo-references -> skill-contract-common.md`

## Decision packet
- shared decision packet under `beo-references -> skill-contract-common.md`
- no local packet extensions beyond consolidation evidence in owned learning surfaces

## Decision rule
- use the consolidation threshold in `beo-references -> learning.md`
- conflicting evidence blocks promotion and records a non-promotion rationale
- actual shared guidance mutation requires explicit user approval unless the surface is designated auto-writable by `beo-references -> learning.md`

## Allowed next owners
- user
- done

## Local hard stops
- Do not promote a single accepted feature into corpus-level consolidation without explicit user request.
- Do not treat feature-local `no-learning` as shared evidence.
- Before routing to `done`, inherit the terminal done rule from `beo-references -> state.md`.

## References
- `beo-references -> operator-card.md`
- `beo-references -> learning.md`
- `beo-references -> pipeline.md`
- `beo-references -> state.md`
