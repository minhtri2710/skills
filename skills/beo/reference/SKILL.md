---
name: beo-reference
description: |
  Return canonical references. Use when the request is a read-only lookup of an existing rule, schema, template, mapping, protocol, or command form. Do not use when routing or edits are requested.
metadata:
  dependencies: []
---
# beo-reference

## Purpose
Return canonical references.

## Primary owned decision
Return the exact canonical reference surface for a read-only lookup.

## Ownership predicate
- The request is a read-only lookup of an existing canonical rule, schema, template, mapping, protocol, or command form.
- No edits, routing, owner selection, or runtime delivery are requested.

## Writable surfaces
- none

## Hard stops
- Do not edit doctrine or artifacts.
- Do not route or execute feature work.
- Do not synthesize new canonical law.

## Allowed next owners
- done

## References
- `beo-reference -> approval.md` — read when checking approval freshness, invalidation, or execution envelope rules.
- `beo-reference -> artifacts.md` — read when locating artifact layout, schemas, writer boundaries, decision mapping, bead schema, or `REVIEW.md` template.
- `beo-reference -> authoring.md` — read when placing doctrine, applying BEO frontmatter policy, or checking anti-goals.
- `beo-reference -> cli.md` — read when exact shared `br`/`bv` command forms are needed.
- `beo-reference -> complexity.md` — read when selecting ceremony mode or planning depth.
- `beo-reference -> coordination.md` — read when checking worker authority, Agent Mail posture, or reservation semantics.
- `beo-reference -> doctrine-map.md` — read when finding the canonical owner for a concept or deletion rule.
- `beo-reference -> go-mode.md` — read when applying go-mode macro behavior or operator assumption discipline.
- `beo-reference -> learning.md` — read when applying durable-learning, no-learning, or consolidation thresholds.
- `beo-reference -> operator-card.md` — read for first-pass operator workflow and output order.
- `beo-reference -> pipeline.md` — read when checking legal transitions and allowed handoffs.
- `beo-reference -> skill-contract-common.md` — read when applying shared contract boilerplate, terminal-done rule, decision-packet template, or dependency schema.
- `beo-reference -> state.md` — read when applying `STATE.json`, `HANDOFF.json`, freshness, or resume lifecycle rules.
- `beo-reference -> status-mapping.md` — read when mapping bead states and labels.
