---
name: beo-reference
description: |
  Use this skill to return canonical references without mutating runtime artifacts. Use when the request is a read-only lookup of an existing rule, schema, template, mapping, protocol, or command form. Do not use when routing, artifact edits, implementation, validation, execution, review, or doctrine authoring is requested.
---

# beo-reference

## Purpose
Return canonical references without mutating runtime artifacts.

## Active when
The request is a read-only lookup of an existing rule, schema, template, mapping, protocol, or command form.

## Owns
Identify and quote the canonical reference that exactly matches the user's requested rule, schema, template, mapping, protocol, or command form.

## Reads
- `references/pipeline.md` (topology, vocabulary, legal transitions)
- `references/approval.md` (approval envelope and staleness)
- `references/approval-integrity.md` (helper contract and integrity status)
- `references/artifacts.md` (schemas, precedence, field ownership)
- `references/state.md` (STATE/HANDOFF authority)
- `references/learning.md` (learning loop)
- `references/operator-card.md` (human orientation)
- `references/skill-contract-common.md` (owner mechanics)
- `references/tool-contracts.md` (workflow-visible command contracts)

## Writes
None.

## Must stop when
- mutation of files or runtime artifacts is requested
- owner selection, readiness approval, review verdicts, or implementation is needed
- Enforce shared owner stops from `beo-reference -> references/skill-contract-common.md`.

## Exit map
| Condition | Next owner |
| --- | --- |
| lookup complete | done |
| clarification needed | user |

## References
- All canonical references under `references/` as listed in Reads.
