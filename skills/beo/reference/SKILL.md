---
name: beo-reference
description: |
  Return canonical references. Use when the request is a read-only lookup of an existing rule, schema, template, mapping, protocol, or command form. Do not use when routing or edits are requested.
---

# beo-reference

## Purpose
Return canonical references.

## Primary owned decision
Return the exact canonical reference surface for a read-only lookup.

## Enter when
- the request is a read-only lookup of an existing canonical rule, schema, template, mapping, protocol, or command form
- no edits, routing, or owner selection are requested

## Writable surfaces
- none

## Allowed next owners
- done

## Local hard stops
- Do not mutate `STATE.json`.
- Do not mutate `HANDOFF.json`.
- Do not turn a read-only lookup into routing or contract editing.
- Before routing to `done`, inherit the terminal done rule from `beo-references -> state.md`.

## References
- `beo-references -> doctrine-map.md`
- `beo-references -> operator-card.md`
- `beo-references -> approval.md`
- `beo-references -> artifacts.md`
- `beo-references -> authoring.md`
- `beo-references -> cli.md`
- `beo-references -> complexity.md`
- `beo-references -> coordination.md`
- `beo-references -> learning.md`
- `beo-references -> pipeline.md`
- `beo-references -> state.md`
- `beo-references -> status-mapping.md`
