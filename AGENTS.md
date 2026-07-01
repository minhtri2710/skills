<coding_guidelines>
# AGENTS.md -- beo

## What This Repo Is

A collection of canonical beo skills and shared references for structured, contract-driven feature development using `br` and `bv`.

## Repository Structure

- `skills/beo/*/SKILL.md` contains owner skill contracts.
- `beo-reference` -> `references/` contains canonical shared doctrine.
- `beo-reference` -> `registry/` contains machine-readable canonical registries.

## Core Dependencies

| Tool | Version | Purpose |
| --- | --- | --- |
| `br` | 0.1.28+ | beads_rust CLI |
| `bv` | 0.15.2+ | Beads Viewer |
| `qmd` | latest | Vector search for learning recall |
| `obsidian` | latest | Learning note persistence |
| `beo_verify.py` | v1 | Runs TICKET.json scope verify commands and appends `verification_run` runtime events |
| `beo_score_trace.py` | v1 | Advisory trace-quality scoring (minimal/standard/detailed tier) |
| `beo_score_context.py` | v1 | Advisory context-coverage scoring against per-phase read list |
| `beo_audit.py` | v1 | Drift checks: skill-card ↔ registry transitions, references, must_not, manifest |
| `beo_propose.py` | v1 | Generate BEO change proposals from runtime events + learnings (never apply) |
| `beo-climate` | skill + config.json | cadence-scanned drift/preventive maintenance |

## Canonical Reads

| Need | Read |
| --- | --- |
| skill contract | `beo-<skill>` |
| reference index | `beo-reference` |
| kernel invariants | `beo-reference` -> `references/kernel.md` |
| lifecycle, triage, decomposition | `references/lifecycle.md`, `registry/pipeline.json` |
| safety & path rules | `references/safety.md` |
| execution modes & profiles | `registry/profiles.json` |
| approval binding | `registry/approval-envelope.json` |
| ticket schema | `registry/ticket.schema.json` |
| semantic memory | `references/memory.md` |
| command authority | `references/lifecycle.md` |
| helper index | `references/command-manifest.md` |
| per-phase context budget | `references/context-budget.md` |
| user handoff format | `references/user-handoff.md` |
| artifact placement rules | `references/artifact-boundaries.md` |

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

## Skill Loading Rule

A beo skill's `SKILL.md` must be loaded before any mutation owned by that skill. Identifying the current owner from state is not sufficient authorization to act. The hard stops and writable surfaces in the loaded skill contract must be in scope. A no-skill mutation is invalid even when the agent can verify the current owner from state.

## First 5 Minutes

1. Load the active owner `SKILL.md` before any mutation.
2. Read `.beads/artifacts/<issue-id>/TICKET.json` and `state.json` when acting on a delivery bead.
3. Read `beo-reference` docs only when the active skill or ambiguity requires the owning rule.

## Manual Doctrine Review

Shared-reference changes should be read against representative prose pressure scenarios for ambiguity. This review is manual and non-executable; it is not a checker, fixture, eval, benchmark, or release gate.
</coding_guidelines>
