<coding_guidelines>
# AGENTS.md -- beo

## What This Repo Is

A collection of canonical beo skills and shared references for structured, contract-driven feature development using `br` and `bv`.

## Repository Structure

- `skills/beo/*/SKILL.md` contains owner skill contracts.
- `skills/beo/reference/references/` contains canonical shared doctrine.
- `skills/beo/reference/registry/` contains machine-readable canonical registries.

## Core Dependencies

| Tool | Version | Purpose |
| --- | --- | --- |
| `br` | 0.1.28+ | beads_rust CLI |
| `bv` | 0.15.2+ | Beads Viewer |
| `qmd` | latest | Vector search for learning recall |
| `obsidian` | latest | Learning note persistence |

## Canonical Reads

| Need | Read |
| --- | --- |
| skill contract | `beo-<skill>` |
| reference index | `beo-reference` |
| kernel invariants | `references/kernel.md` |
| lifecycle, triage, decomposition | `references/lifecycle.md`, `registry/pipeline.json` |
| safety & path rules | `references/safety.md` |
| execution modes & profiles | `registry/profiles.json` |
| approval binding | `registry/approval-envelope.json` |
| ticket schema | `registry/ticket-schema.json` |
| semantic memory | `references/memory.md`, `registry/memory-backends.json` |
| commands | `registry/command-contracts.json` |

<!-- BEO:MANAGED START -->
BEO always-on rules (kernel is canonical):
1. Work on one verified Beads issue at a time; load the active
   `skills/beo/*/SKILL.md` before any mutation.
2. `br` owns lifecycle/claims/comments/closure; `bv` is orientation only.
3. Only a claimed atomic bead with current `PASS_EXECUTE` may mutate approved
   scope; strict mode is required for external/stateful/high-risk work.
4. Human Gates are user-owned, memory is advisory, only `beo-review` closes
   delivery, and learning never reopens delivery.
<!-- BEO:MANAGED END -->

## Skill Loading Rule

A beo skill's `SKILL.md` must be loaded before any mutation owned by that skill. Identifying the current owner from state is not sufficient authorization to act. The hard stops and writable surfaces in the loaded skill contract must be in scope. A no-skill mutation is invalid even when the agent can verify the current owner from state.

## First 5 Minutes

1. Read `beo-reference -> references/kernel.md`.
2. Read `.beads/artifacts/<issue-id>/TICKET.md` when acting on a bead.
3. Load the active owner `SKILL.md` before any mutation.

## Manual Doctrine Review

Shared-reference changes should be read against representative prose pressure scenarios for ambiguity. This review is manual and non-executable; it is not a checker, fixture, eval, benchmark, or release gate.
</coding_guidelines>
