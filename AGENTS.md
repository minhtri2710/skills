# AGENTS.md -- beo

## What This Repo Is

A collection of 11 canonical beo skills and shared references for structured, contract-driven feature development using `br` and `bv`.

## Repository Structure

- `skills/beo/*/SKILL.md` contains skill contracts.
- `beo-reference -> references/` contains canonical shared schemas, registries, mappings, protocols, and exact command forms.
- `skills/beo/*/references/` contains skill-local assets or appendices only.
- `skills/beo/author/references/` contains skill-writing guidance only.

## Core Dependencies

| Tool | Version | Purpose |
| --- | --- | --- |
| `br` | 0.1.28+ | beads_rust CLI |
| `bv` | 0.15.2+ | Beads Viewer |

## Optional Integrations

Optional only; not required for core beo runtime.

| Tool | Purpose |
| --- | --- |
| `obsidian` CLI | external knowledge-store integration |
| `qmd` | external knowledge-store search/query |

## Canonical Reads

| Need | Read |
| --- | --- |
| skill contract | `skills/beo/<skill>/SKILL.md` |
| reference index | `skills/beo/reference/SKILL.md` |
| first-pass operation | `beo-reference -> references/operator-card.md` |
| legal transitions | `beo-reference -> references/pipeline.md` |
| approval | `beo-reference -> references/approval.md` |
| state/handoff | `beo-reference -> references/state.md` |
| commands | `beo-reference -> references/cli.md` |
| doctrine ownership | `beo-reference -> references/doctrine-map.md` |

<!-- BEO:MANAGED START -->
## Beo Startup

1. Read `.beads/STATE.json` if present.
2. Read `.beads/HANDOFF.json` only if resuming paused or transferred work.
3. Read active feature artifacts only for the active `feature_slug`.
4. If no active feature exists and the user request names a feature goal, start through `beo-explore`.
5. Use `beo-route` only when owner identity or active feature identity is unsafe. If multiple active feature candidates exist, stop and ask the user which feature is active.
6. Treat startup output as advisory only; it cannot approve execution, select execution sets, emit review verdicts, or promote learning.

## Beo Skill Chain

Startup orientation summary: read `beo-reference -> references/operator-card.md` first for the workflow quick map; normal path is `beo-route -> beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done`.
Legal transitions remain canonical in `beo-reference -> references/pipeline.md`.
Optional learning closure: `beo-review -> beo-compound -> done` only when REVIEW records durable-candidate or unclear single-feature learning. `beo-dream` only when cross-feature threshold or explicit corpus request exists.
Support skills: `beo-debug`, `beo-author`. Corpus skill: `beo-dream`. Reference skill: `beo-reference`.
Go mode only changes assumption posture. It does not bypass owner selection, Human approval gates, UAT gates, validation, approval freshness, `PASS_EXECUTE`, execution scope, review, or learning thresholds; see `beo-reference -> references/go-mode.md`.

Startup pointers: workflow quick map (`beo-reference -> references/operator-card.md`), legal transitions (`beo-reference -> references/pipeline.md`), state/handoff freshness (`beo-reference -> references/state.md`), approval refresh (`beo-reference -> references/approval.md`), and go mode (`beo-reference -> references/go-mode.md`).

## Working Files

- `.beads/STATE.json`
- `.beads/HANDOFF.json`
- `.beads/artifacts/<feature_slug>/`
- `.beads/learnings/`

## Session End

1. Update or close the active bead only when the current owner owns bead status/evidence mutation.
2. Update `STATE.json` only for fields owned by the current owner.
3. Flush any owner-owned artifact or optional bead metadata mutation before handoff or session end.
4. Write or update `HANDOFF.json` only when pausing or transferring ownership.
5. Record blockers, questions, and the next action.

<!-- BEO:MANAGED END -->

## Skill Loading Rule

A beo skill's `SKILL.md` must be loaded before any mutation owned by that skill. Identifying `STATE.json.current_owner` is not sufficient authorization to act. The hard stops and writable surfaces in the loaded skill contract must be in scope. A no-skill mutation is invalid even when the agent can verify the current owner from state. See `beo-reference -> references/skill-contract-common.md`.

## First 5 Minutes

1. Read `beo-reference -> references/operator-card.md`.
2. Read `beo-reference -> references/skill-contract-common.md` sections `Canonical vocabulary registry` and `Skill must be loaded to act`.
3. Read `.beads/STATE.json` when present.
4. Read `.beads/HANDOFF.json` only when resuming paused or transferred work.
5. Read active feature artifacts only for the active `feature_slug`.
6. If exactly one current owner is valid, load only `skills/beo/<owner>/SKILL.md`; if no active feature exists and the user request names a feature goal, load `skills/beo/explore/SKILL.md`; otherwise load `skills/beo/route/SKILL.md`.
7. Do not mutate anything before one owner SKILL is loaded.

## Manual Doctrine Review

Shared-reference changes should be read against representative prose pressure scenarios for ambiguity. This review is manual and non-executable; it is not a checker, fixture, eval, benchmark, or release gate.
