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

## Skillify mapping (advisory)

The OKF v0.1 note shape covers the "what" of a learning (type, basis, evidence). Garry Tan's `Skillify` 10-step checklist (`Clippings/How-to-really-stop-your-agents-from-making-the-same-mistakes.md` `#80a487`) is the broader promotion workflow that turns an ad-hoc failure into a permanent, structurally-unreachable bug. The OKF note participates in steps 1, 2, and 8 of that workflow; the rest live outside the note itself.

| Skillify step | Where it lives | BEO coverage |
| --- | --- | --- |
| 1. `SKILL.md` (the contract) | This skill card, or a BEO skill being authored | OKF frontmatter `type: learning`, `basis_ref` |
| 2. Deterministic code (`scripts/*.mjs`) | The promoted fix in the product repo | OKF `evidence_refs` (when the entry is a script path) |
| 3. Unit tests | Product repo test tree | out of OKF scope; track via `tags: [unittest]` |
| 4. Integration tests | Product repo test tree | out of OKF scope; track via `tags: [integration-test]` |
| 5. LLM evals | Eval suite in the product repo | out of OKF scope; track via `tags: [llm-eval]` |
| 6. Resolver trigger (entry in `AGENTS.md`) | Operator's `AGENTS.md` or `CLAUDE.md` | out of OKF scope; record in body, not frontmatter |
| 7. Resolver eval (verify the trigger routes) | Run by the operator, not by `beo-learn` | out of OKF scope |
| 8. Resolvable + DRY audit | Promotion review before publish | out of OKF scope; track via `case_type: authoring_candidate` |
| 9. E2E smoke test | Product repo CI | out of OKF scope |
| 10. Brain filing rules | Obsidian layout + critical-patterns rollup | OKF `tags`, `case_type`; rolled up in `beo-learnings/critical-patterns.md` |

The 10-step checklist is the promotion bar; the OKF note is the artifact. A note that does not have a path to step 2 (deterministic code) is still valid as an advisory observation, but it has not yet been "skillified" in the structural sense.

### Optional BEO-specific frontmatter

These fields are BEO extensions, not OKF v0.1 fields. They are optional. The parser in `beo_audit.py C9` recognizes them but they do not affect OKF compliance.

- `skillify_state: <incomplete|partial|complete>` — current state of the 10-step promotion. `incomplete` means only the note exists. `partial` means some steps are done. `complete` means all ten steps have evidence.
- `skillify_steps: [1, 2, 3]` — list of step numbers that have evidence. The interpretation is per-step and recorded in the note body, not the frontmatter.
- `refresh_after: 2026-09-01` — optional ISO date after which the note should be reviewed. `beo_audit.py` (C9) does not enforce this date but the operator's `beo-climate` cadence scan can surface it.

A note with no `skillify_*` fields is treated as `incomplete` by default; this is non-blocking. The fields exist so that promotion is tracked, not so that it is gated.
