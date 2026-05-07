---
name: beo-reference
description: |
  Use this skill to return canonical references without mutating runtime artifacts. Use when the request is a read-only lookup of an existing rule, schema, template, mapping, protocol, or command form. Do not use when routing, artifact edits, implementation, validation, execution, review, or doctrine authoring is requested.
---

# beo-reference

## Purpose

Return canonical references without mutating runtime artifacts.

## Fast predicate

Active when the request is a read-only lookup of an existing rule, schema, template, mapping, protocol, or command form.

Not active when routing, artifact edits, implementation, validation, execution, review, or doctrine authoring is requested.

## Primary owned decision

Identify and quote the canonical reference surface.

## Writable surfaces

None for read-only lookup.

## Hard stops

Do not mutate files or runtime artifacts. Do not select owners. Do not approve readiness. Do not emit review verdicts. Do not implement.

## Allowed next owners

done, user

## References

- `references/pipeline.md`
- `references/state.md`
- `references/artifacts.md`
- `references/approval.md`
- `references/skill-contract-common.md`
