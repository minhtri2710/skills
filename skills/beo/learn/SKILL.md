---
name: beo-learn
description: Mandatory after review/debug learning_candidate to record reusable success, failure, near-miss, or debug lessons without reopening delivery.
---
# beo-learn
Refs: `references/memory.md`.

## Decision
Persist the smallest reusable lesson with provenance and non-authority disclaimer.

## Enter
- `learning_candidate` event emitted by `beo-review` or `beo-debug` with sufficient evidence.
- If evidence is insufficient, ask the user instead of inventing a lesson.

## Owns
- Learning note content, metadata, safe slug, Obsidian/local fallback write, and qmd refresh status.

## Does Not Own
- Delivery reopening, review verdicts, approval tokens, issue closure, or doctrine edits.

## Stops
- Evidence is non-reusable, unsafe to persist, secret-bearing, or attempts to reopen delivery.

## Exits
- `case_recorded` -> `done`
- `authoring_requested` -> `beo-author`
- `insufficient_evidence` -> `user`

## Method
1. Extract only the reusable trigger, lesson, prevention rule, and safe evidence refs per `references/memory.md`.
2. Persist through `beo_memory_write.py`; use local markdown fallback if Obsidian is unavailable.
3. Refresh `qmd` only after a successful learning write or explicit setup authorization.
4. If doctrine changes are needed, write `AUTHORING_RECOMMENDATION.md` rather than editing doctrine here.
