<!-- BEO:MANAGED START -->
BEO is active in this repo.
- Kernel invariants are canonical: `beo-reference -> references/kernel.md`.
- Normal delivery path: `beo-plan -> beo-validate -> beo-execute -> beo-review`.
- Extended flows live outside the normal path: `beo-climate` (cadence maintenance), fast-track (quick-mode flag, §12), strict-mode worktree isolation (§7), and harness proposals (§10) for evolving the control plane. See `beo-reference -> references/kernel.md`.
- Supporting skills: `beo-debug` (when blocked), `beo-learn` (capture notes), `beo-reference` (read-only lookup), `beo-author` (maintain BEO itself). Load via `skills/beo/<name>/SKILL.md`.
- Use one claimed Beads issue and one BEO owner at a time.
- `br` owns lifecycle; `bv`, qmd, and Obsidian never grant authority.
- Use the `br`/`bv` CLI for all `.beads/` reads and mutations (`br ready --json`, `br show <id> --json`, `br close`); never parse `issues.jsonl`/`beads.db` directly (kernel §2.11; detail in `beo-reference -> references/lifecycle.md`). Orient with `br robot-docs guide`; per-project command help via `br agents --add`.
- Do not execute without validation-owned `PASS_EXECUTE`; review owns accepted closure.
- `strict`-mode `verdict_accept` requires a recorded second-reviewer cross-check (`state.json.review.cross_check`); see kernel §15.
- Do not scatter BEO workflow rules outside this managed block; update `skills/beo/` canonical references instead.
<!-- BEO:MANAGED END -->
