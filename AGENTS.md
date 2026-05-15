<coding_guidelines>
# AGENTS.md -- beo

## What This Repo Is

A collection of canonical beo skills and shared references for structured, contract-driven feature development using `br` and `bv`.

## Repository Structure

- `skills/beo/*/SKILL.md` contains owner skill contracts.
- `skills/beo/reference/references/` contains canonical shared doctrine and generated/advisory playbook surfaces.
- `skills/beo/reference/registry/` contains machine-readable canonical registries.

## Core Dependencies

| Tool | Version | Purpose |
| --- | --- | --- |
| `br` | 0.1.28+ | beads_rust CLI |
| `bv` | 0.15.2+ | Beads Viewer |

## Canonical Reads

| Need | Read |
| --- | --- |
| skill contract | `skills/beo/<skill>/SKILL.md` |
| reference index | `skills/beo/reference/SKILL.md` |
| operator cockpit | `beo-reference -> references/operator-cockpit.md` |
| runtime playbook | `beo-reference -> references/runtime-playbook.md` |
| runtime kernel | `beo-reference -> references/runtime-kernel.md` |
| artifact model | `beo-reference -> references/artifacts.md` |
| legal transitions | `beo-reference -> registry/pipeline.json` |
| vocabulary registry | `beo-reference -> registry/vocabulary.json` |
| approval | `beo-reference -> references/approval.md` |
| state/handoff | `beo-reference -> references/state.md` |
| doctrine ownership | `beo-reference -> references/doctrine-map.md` |
| skill contract common | `beo-reference -> references/skill-contract-common.md` |

<!-- BEO:MANAGED START -->
Authority: advisory only.

Start here:
<!-- beo:agents:start-cockpit -->
1. Operator cockpit: `beo-reference -> references/operator-cockpit.md`
2. Runtime kernel: `beo-reference -> references/runtime-kernel.md`
3. Current owner contract: active owner `SKILL.md`
4. Canonical transitions: `beo-reference -> registry/pipeline.json`

Startup:
1. Read `.beads/STATE.json` if present.
2. Load `FEATURE.json` and current required artifacts.
3. Resolve current owner from artifacts; STATE/HANDOFF are mirrors only.
4. New feature delivery starts through `beo-explore`.
5. Setup/usage requests use `beo-setup`.

Normal path:
`beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done`.

Runtime authority comes from current artifacts, loaded owner contract, canonical references, and pipeline.
<!-- BEO:MANAGED END -->

## Skill Loading Rule

A beo skill's `SKILL.md` must be loaded before any mutation owned by that skill. Identifying the current owner from state is not sufficient authorization to act. The hard stops and writable surfaces in the loaded skill contract must be in scope. A no-skill mutation is invalid even when the agent can verify the current owner from state.

## First 5 Minutes

1. Read `beo-reference -> references/operator-cockpit.md`.
2. Read `beo-reference -> references/skill-contract-common.md` section `Skill must be loaded to act`.
3. Read `.beads/STATE.json` when present.
4. Load the active owner `SKILL.md` before any mutation.

## Manual Doctrine Review

Shared-reference changes should be read against representative prose pressure scenarios for ambiguity. This review is manual and non-executable; it is not a checker, fixture, eval, benchmark, or release gate.
</coding_guidelines>
