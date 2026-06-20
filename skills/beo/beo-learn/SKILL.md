---
name: beo-learn
description: "Save optional advisory BEO learning notes from explicit learning candidates or user requests. Never affects approval, execution, review, closure, or Human Gates."
---
# beo-learn

## Read

- The explicit learning candidate or user request
- Safe evidence refs named by the candidate
- `beo-reference -> references/memory.md` when backend rules are unclear
- `beo-reference -> references/memory.md#note-shape` for OKF frontmatter format

## Do

1. Record a lesson only if it is reusable, non-obvious, safe, and at least two are true: likely to recur in this repo, changes future BEO behavior, identifies a tool-specific trap, captures a user preference about BEO operation, or prevents unsafe approval/execution/review.
2. Skip task trivia, duplicate doctrine, raw secrets/customer data, and generic “be careful” notes.
3. Write the smallest markdown note through `beo-reference -> scripts/beo_memory_write.py`. The note must follow the [Open Knowledge Format (OKF)](https://github.com/GoogleCloudPlatform/knowledge-catalog/tree/main/okf) v0.1 conventions documented in `beo-reference -> references/memory.md#note-shape`: include `type` (`learning`, `decision`, or `reference`), `basis_ref`, `evidence_refs`, `secret_policy: handles_only`, and mode-specific fields. Add `tags` and `timestamp` when they aid future retrieval.
4. Emit `qmd_refresh_recommended` when qmd indexing should be refreshed; refresh/index qmd only through explicit `beo-setup` or authorized maintenance.

## Write

- Advisory learning note only
- `qmd_refresh_recommended` signal only; no qmd index mutation

## Emit

- `learning_recorded`
- `learning_skipped`
- `qmd_refresh_recommended`
- `user_review_needed`

## Never

- Binding: `beo-reference -> registry/phase-contracts.json` `must_not[]` is canonical; prose below mirrors it (audit C8).
- Do not mutate delivery state.
- Do not grant `PASS_EXECUTE`.
- Do not alter review verdicts or close issues.
- Do not store secrets or raw credentials.
- Do not refresh or reindex qmd.
