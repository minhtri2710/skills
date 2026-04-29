# AGENTS.md -- beo

## What This Repo Is

A collection of 13 canonical beo skills and shared references for structured, contract-driven feature development using `br` and `bv`.

## Repository Structure

- `skills/beo/*/SKILL.md` contains skill contracts.
- `skills/beo/reference/references/` contains canonical shared schemas, registries, mappings, protocols, and exact command forms.
- `skills/beo/*/references/` contains skill-local assets or appendices only.
- `skills/beo/author/references/` contains skill-writing guidance only.
- `skills/beo/onboard/` contains managed startup assets and onboarding scripts.

## External Dependencies

| Tool | Version | Purpose |
| --- | --- | --- |
| `br` | 0.1.28+ | beads_rust CLI |
| `bv` | 0.15.2+ | Beads Viewer |
| `obsidian` CLI | optional | external knowledge-store integration |
| `qmd` | optional | external knowledge-store search/query |

## Canonical Pointers

- Skill contracts: `skills/beo/<skill>/SKILL.md`
- Shared reference index: `skills/beo/reference/SKILL.md`
- Operator first-pass view: `skills/beo/reference/references/operator-card.md`
- Authoring method and owner map: `skills/beo/reference/references/authoring.md`
- Exact CLI forms: `skills/beo/reference/references/cli.md`
- Approval doctrine: `skills/beo/reference/references/approval.md`
- Learning thresholds and closure split: `skills/beo/reference/references/learning.md`
- State and handoff schemas: `skills/beo/reference/references/state.md`
- Status mapping: `skills/beo/reference/references/status-mapping.md`
- Pipeline and allowed handoffs: `skills/beo/reference/references/pipeline.md`

## Onboarding Versioning

`skills/beo/onboard/scripts/onboarding-metadata.json` is the source of truth for onboarder and managed startup contract versions used by `skills/beo/onboard/scripts/onboard_beo.mjs`.

<!-- BEO:MANAGED START -->
## Beo Startup

1. Run the live onboarding check before downstream beo work: `node <installed-beo-onboard-root>/scripts/onboard_beo.mjs --repo-root "<absolute-repo-root>"`.
2. If the check result is not `up_to_date`, stop and load `beo-onboard`.
3. If `.beads/beo_status.mjs` exists, run `node .beads/beo_status.mjs --json` after the live check passes.
4. Reopen `.beads/STATE.json` and `.beads/HANDOFF.json` when present; verify handoff freshness before routing.
5. Reopen active feature artifacts under `.beads/artifacts/<feature_slug>/` before acting on that feature.
6. Treat status output and cached dependency posture as advisory/display only; canonical owners and references remain binding.

## Beo Skill Chain

Startup orientation only: `beo-route -> beo-explore -> beo-plan -> beo-validate -> beo-execute/beo-swarm -> beo-review -> done`.
This chain is an orientation summary only; legal transitions remain canonical in `beo-reference -> pipeline.md`.
Optional closure: `beo-review -> beo-compound -> beo-dream/done`.
Support skills: `beo-debug`, `beo-dream`, `beo-author`. Reference skill: `beo-reference`.

Canonical pointers:
- legal transitions: `beo-reference -> pipeline.md`
- approval refresh/invalidation: `beo-reference -> approval.md`
- learning closure split: `beo-reference -> learning.md`
- state and handoff freshness: `beo-reference -> state.md`
- commands: `beo-reference -> cli.md`

## Advisory Status Rule

Startup and status surfaces are orientation only. They do not approve execution,
select routes, validate readiness, emit review verdicts, dispatch swarm work, or
promote learning.

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
3. Run `br sync --flush-only` after bead DB mutations.
4. Write or update `HANDOFF.json` only when pausing or transferring ownership.
5. Record blockers, questions, and next action.

<!-- BEO:MANAGED END -->
