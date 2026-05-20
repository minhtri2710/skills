---
name: beo-recall
description: Read-only retrieval of prior BEO learning cases, mistakes, and playbooks before planning, execution, review, debug, or authoring.
---

# beo-recall

Refs: `beo-reference -> references/memory.md`, `beo-reference -> references/lifecycle-events.md`.

## Decision

Return relevant prior lessons without mutating files.

## Enter

- BEO owner requests prior-case research.
- Work resembles a known failure-prone area.

## Owns

- Read-only memory search and inline summaries.

## Stops

- Query exposes secrets rather than safe handles.

## Exits

- `memory_recalled` -> `caller`
- `no_relevant_memory` -> `caller`

## Method

1. Avoid recall for routine quick tasks.
2. Build narrow query from issue request, scope, files, and errors.
3. Follow backend order and secret policy in `beo-reference -> references/memory.md`.
4. Summarize only relevant lessons, trigger signs, and prevention rules.
5. Write `RECALL_SUMMARY.md` only for strict or high-risk work.
6. Append `return` event only if entered through a runtime handoff.
