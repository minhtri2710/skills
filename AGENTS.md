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

`skills/beo/onboard/assets/onboarding-metadata.json` is the source of truth for onboarder and managed startup contract versions used by `skills/beo/onboard/scripts/onboard_beo.mjs`.

<!-- BEO:MANAGED START -->
- beo canonical runtime doctrine lives under `skills/beo/*/SKILL.md` and `skills/beo/reference/references/*.md`.
- Use `skills/beo/reference/references/operator-card.md` as the first-pass operator view.
- This block is pointer-only; exact CLI, approval, learning, state, status, routing, and handoff rules are not canonical here.
<!-- BEO:MANAGED END -->
