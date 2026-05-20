---
name: beo-reference
description: Use for read-only lookup of BEO doctrine, registries, templates, and command contracts; not a delivery phase.
---
# beo-reference
Refs: `references/kernel.md`.

## Decision
Resolve a BEO doctrine or registry question without mutation.

## Enter
- A BEO owner or user needs canonical lookup.

## Owns
- Read-only lookup and citation of doctrine files and registries.

## Stops
- Request requires product or lifecycle state mutation.

## Method
1. Load `references/kernel.md` first for core invariants.
2. Select and load the specific reference file needed to resolve the decision.
3. Optimize token usage: avoid loading all reference documents by default.
4. Verify lookups against canonical registries under `registry/`.
