---
name: beo-reference
description: Returns canonical BEO references without mutating runtime artifacts.
---

# beo-reference

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

## Decision

Return canonical references without mutation.

## Enter

- Read-only lookup of BEO doctrine, registry, schema, or command authority.

## Owns

- Reference selection.
- Citation.
- Explanation.

## Writes

- Nothing.

## Stops

- Request requires runtime mutation, owner decision, approval, execution, review, route repair, or doctrine editing.

## Returns

- Explanatory answer or reference summary in the agent response only.
- No runtime pipeline transition is emitted.

## Method

1. Identify the canonical home from `references/doctrine-map.md` or the request.
2. Read the smallest relevant source.
3. Answer with source paths and no mutation.
4. If the request is not lookup, report the legal next owner/source.
