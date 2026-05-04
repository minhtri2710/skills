# AGENTS.md -- beo

## What This Repo Is

A collection of 12 canonical beo skills and shared references for structured, contract-driven feature development using `br` and `bv`.

## Repository Structure

- `skills/beo/*/SKILL.md` contains skill contracts.
- `skills/beo/reference/references/` contains canonical shared schemas, registries, mappings, protocols, and exact command forms.
- `skills/beo/*/references/` contains skill-local assets or appendices only.
- `skills/beo/author/references/` contains skill-writing guidance only.
- `skills/beo/onboard/` contains managed startup assets and onboarding scripts.

## Core Dependencies

| Tool | Version | Purpose |
| --- | --- | --- |
| `br` | 0.1.28+ | beads_rust CLI |
| `bv` | 0.15.2+ | Beads Viewer |
| `node` | available | managed onboarding script runtime |

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
| first-pass operation | `skills/beo/reference/references/operator-card.md` |
| legal transitions | `skills/beo/reference/references/pipeline.md` |
| approval | `skills/beo/reference/references/approval.md` |
| state/handoff | `skills/beo/reference/references/state.md` |
| commands | `skills/beo/reference/references/cli.md` |
| doctrine ownership | `skills/beo/reference/references/doctrine-map.md` |

## Onboarding Versioning

`skills/beo/onboard/scripts/onboarding-metadata.json` is the source of truth for onboarder and managed startup contract versions used by `skills/beo/onboard/scripts/onboard_beo.mjs`.

<!-- BEO:MANAGED START -->
## Beo Startup

1. Run the live onboarding check before any downstream beo work: `node skills/beo/onboard/scripts/onboard_beo.mjs --repo-root "$(pwd)"`.
2. If the check result is not `up_to_date`, stop and load `beo-onboard`.
3. If `.beads/beo_status.mjs` exists, run `node .beads/beo_status.mjs --json` after the live check passes.
4. Reopen `.beads/STATE.json` and `.beads/HANDOFF.json` when present; verify handoff freshness before routing.
5. Reopen active feature artifacts under `.beads/artifacts/<feature_slug>/` before acting on that feature.
6. Treat status output and cached dependency posture as advisory, display-only context; canonical owners and references remain binding.

## Beo Skill Chain

Startup orientation summary: `beo-route -> beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done`.
Legal transitions remain canonical in `beo-reference -> pipeline.md`.
Optional closure: `beo-review -> beo-compound -> beo-dream/done`.
Support skills: `beo-debug`, `beo-author`. Bootstrap skill: `beo-onboard`. Corpus skill: `beo-dream`. Reference skill: `beo-reference`.
Go mode only reduces unnecessary operator prompts. It does not bypass owner selection, approval, readiness, execution scope, review, or learning gates; see `beo-reference -> go-mode.md`.

Startup pointers: legal transitions (`pipeline.md`), state/handoff freshness (`state.md`), approval refresh (`approval.md`), and go mode (`go-mode.md`).

## Advisory Status Rule

Startup and status surfaces are orientation only. They do not approve execution,
select routes, validate readiness, select execution sets, emit review verdicts,
or promote learning.

## Working Files

- `.beads/onboarding.json`
- `.beads/beo_status.mjs`
- `.beads/STATE.json`
- `.beads/HANDOFF.json`
- `.beads/artifacts/<feature_slug>/`
- `.beads/critical-patterns.md`
- `.beads/learnings/`

## Session End

1. Update or close the active bead only when the current owner owns bead status/evidence mutation.
2. Update `STATE.json` only for fields owned by the current owner.
3. Flush bead DB mutations through `beo-reference -> cli.md`.
4. Write or update `HANDOFF.json` only when pausing or transferring ownership.
5. Record blockers, questions, and the next action.

<!-- BEO:MANAGED END -->

## Skill Loading Rule

A beo skill's `SKILL.md` must be loaded (in scope) before any mutation owned by that skill. Identifying `STATE.json.current_owner` is not sufficient authorization to act. The hard stops and writable surfaces in the loaded skill contract must be in scope. A no-skill mutation is invalid even when the agent can verify the current owner from state. See `beo-reference -> skill-contract-common.md`.

## First 5 Minutes

1. From the repo root, run:
   `node skills/beo/onboard/scripts/onboard_beo.mjs --repo-root "$(pwd)"`

2. If the result is not `up_to_date`, run:
   `node skills/beo/onboard/scripts/onboard_beo.mjs --repo-root "$(pwd)" --apply`
   Then rerun step 1.

3. Read:
   `skills/beo/reference/references/operator-card.md`

4. Read:
   `skills/beo/reference/references/skill-contract-common.md`
   sections `Canonical vocabulary registry` and `Skill must be loaded to act`.

5. Read `.beads/STATE.json` and `.beads/HANDOFF.json` when present.
   - If exactly one current owner is valid, load only `skills/beo/<owner>/SKILL.md`.
   - Otherwise load `skills/beo/route/SKILL.md`.
   - Do not mutate anything before one owner SKILL is loaded.

## Manual Doctrine Review

Shared-reference changes should be read against representative prose pressure scenarios for ambiguity. This review is manual and non-executable; it is not a checker, fixture, eval, benchmark, or release gate.
