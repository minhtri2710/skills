---
name: beo-learn
description: Mandatory learning capture from successes, failures, near misses, or debug patterns. Use this skill whenever a learning candidate is emitted to prevent repeated mistakes and preserve reusable patterns.
---

# beo-learn

Refs: `beo-reference -> references/memory.md`.

## Decision

Record smallest reusable lesson with provenance.

## Enter

- `beo-review` or `beo-debug` marked a learning candidate.
- User consolidated BEO learning evidence.

## Owns

- Case notes, patterns, backend metadata.

## Stops

- Evidence insufficient/non-reusable.
- Reopens delivery or mutates product files.

## Exits

- `case_recorded` -> `done`
- `authoring_requested` -> `beo-author`
- `insufficient_evidence` -> `user`

## Method

1. Identify case type (e.g., `success_pattern`, `recurring_mistake`) and extract the reusable lesson and trigger.
2. Structure note: Use filename `YYYY-MM-DD--<case-type>--<bead-id>--<slug>.md` with safe alphanumeric-hyphen slug.
3. Persist and index: Run `beo_memory_write.py --issue <issue-id> --case-type <case-type> --slug <slug> --markdown-file <file-path>` and report which backend path was used.
   - Obsidian CLI owns durable markdown note creation in the learnings collection.
   - `qmd update` and `qmd embed` own search/index freshness.
   - If either backend is unavailable, keep the fallback artifact and do not reopen delivery.
4. State the memory boundary in the learning note: recall is advisory only and never grants approval, verdicts, closure, or Human Gate authorization.
5. Doctrine loop: Route to `beo-author` via `AUTHORING_RECOMMENDATION.md` only for BEO doctrine/registry updates.

