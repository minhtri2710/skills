---
name: beo-reference
description: |
  Returns canonical references without mutating runtime artifacts. Use for read-only lookup of existing rules, schemas, mappings, protocols, and exact command forms. Not for routing, artifact edits, implementation, validation, execution, review, or doctrine authoring.
---

# beo-reference

## Purpose

Return targeted canonical references.

## Decision Card

Decision: return canonical references.

Can enter when:
- the request is a read-only lookup of BEO doctrine, registry, schema, or command authority

Can write:
- nothing

Must stop when:
- the request requires runtime mutation or owner decision

Returns:
- reference result to requester or caller

Never:
- route, approve, execute, review, debug, author doctrine, or mutate runtime artifacts

Reads:
- requested canonical references and registries

## Contract

Common owner rules:
- Load and obey `beo-reference -> references/skill-contract-common.md`.
- Transition topology may be read from `beo-reference -> registry/pipeline.json` for lookup/citation only.

Acts when:
- the request is a read-only lookup of BEO doctrine, registry, schema, or command authority.

Owns:
- reference selection and citation only.

Local stops:
- the request requires runtime mutation or owner decision.

Stop reporting:
- Use the next-action shape in `beo-reference -> references/skill-contract-common.md`.

Writes:
- nothing.

Reads:
- `references/README.md`, `references/operator-cockpit.md`, `references/resume-resolution.md`, `references/route-resolution.md`, `references/glossary.md`, `references/doctrine-map.md`, `references/runtime-kernel.md`, canonical references, assets, and registries requested by the user.

Local forbids:
- routing, approving, executing, reviewing, debugging, or authoring doctrine.

Exits:
- return reference result to requester or caller; no runtime pipeline transition is emitted.
