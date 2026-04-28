---
name: beo-dream
description: |
  Consolidate cross-feature learning. Use when at least two accepted features support shared learning, or when the user explicitly requests corpus-level consolidation. Do not use when only one feature provides evidence and no explicit user request exists.
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
- explicit skill invocation authorizes analysis; concrete shared guidance mutation still requires approval of the proposed change unless the surface is designated auto-writable by `beo-references -> learning.md`

## Consolidation decision matrix

| Evidence | Action |
| --- | --- |
| one accepted feature only, no explicit corpus request | no promotion |
| one accepted feature + explicit user corpus request | analyze, but require override reason |
| two accepted features, same pattern, same future decision impact | consolidation candidate |
| conflicting evidence | non-promotion rationale |
| multiple plausible owner files | ask user with candidate-specific options |
| no existing owner file | create/propose new consolidation record if threshold met |

## Critical shared guidance rule

Concrete shared guidance mutation requires:
- threshold met, or explicit user corpus request with override reason
- conflict check
- owner file identified
- provenance update
- approval if surface is not auto-writable

## Allowed next owners
- user
- done

## Local hard stops
- Do not promote a single accepted feature into corpus-level consolidation without explicit user request.
- Do not treat feature-local `no-learning` as shared evidence.
- Do not write feature-level learning records; that belongs to `beo-compound`.
- Do not mutate shared guidance without the threshold or explicit corpus-request override evidence required by `beo-references -> learning.md`.
- Before routing to `done`, inherit the terminal done rule from `beo-references -> state.md`.

## References
- `beo-references -> operator-card.md`
- `beo-references -> learning.md`
- `beo-references -> pipeline.md`
- `beo-references -> state.md`
