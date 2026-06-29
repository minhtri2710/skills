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

- See `beo-reference -> registry/phase-contracts.json` `must_not[]`; audit C8 enforces drift.
- Do not mutate delivery state.
- Do not grant `PASS_EXECUTE`.
- Do not alter review verdicts or close issues.
- Do not store secrets or raw credentials.
- Do not refresh or reindex qmd.

## Skillify mapping (advisory)

The 10-step Skillify promotion workflow is broader than BEO. Of the 10 steps, BEO scope covers 1 (skill card), 2 (deterministic code), and 10 (brain filing); the other 7 steps (3-9: tests, evals, resolver trigger, DRY audit, E2E smoke) live in the operator's product repo and the broader `writing-great-skills` skill.

| Scope | Steps | BEO coverage |
| --- | --- | --- |
| BEO scope | 1, 2, 10 | OKF `type: learning` frontmatter, `evidence_refs` for script paths, `tags`/`case_type` for brain filing |
| Operator scope | 3-9 | Tests, evals, resolver trigger, DRY audit, E2E smoke — track via `tags` and `case_type: authoring_candidate` |

The 10-step checklist is the promotion bar; the OKF note is the artifact. A note without a path to step 2 (deterministic code) is still valid as an advisory observation, but is not yet "skillified" in the structural sense.

### Optional BEO-specific frontmatter

- `skillify_state: <incomplete|partial|complete>` — current state of the 10-step promotion. Default: `incomplete` if the field is missing; non-blocking.
- `skillify_steps: [1, 2, 3]` — list of step numbers that have evidence. Per-step interpretation lives in the note body.
- `refresh_after: 2026-09-01` — optional ISO date; surfaced by `beo-climate` cadence scan, not enforced by `beo_audit.py` C9.
