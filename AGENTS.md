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
BEO always-on rules (kernel is canonical):
1. Work on one verified Beads issue at a time; load the active
   `skills/beo/*/SKILL.md` before any mutation.
2. `br` owns lifecycle/claims/comments/closure; `bv` is orientation only.
3. Only a claimed atomic bead with current `PASS_EXECUTE` may mutate approved
   scope; strict mode is required for external/stateful/high-risk work.
4. Human Gates are user-owned, memory is advisory, only `beo-review` closes
   delivery (strictly via verdict_accept for completed delivery, leaving non-normal terminal routes open on br for manual user closure), and learning never reopens delivery.
5. Use `bv` robot flags only; never open bare `bv` TUI in agent workflow.
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
