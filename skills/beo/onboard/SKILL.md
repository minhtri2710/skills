---
name: beo-onboard
description: |
  Use when beo tooling, bootstrap files, or repository operating state are missing, stale, or must be verified before any other beo skill can run safely. Onboard checks required tooling, creates only missing bootstrap structure, safely updates shared onboarding guidance when necessary, and reports readiness. Do not use for feature delivery, routing logic, or destructive rewrites of existing repo state.
---

> **HARD-GATE: IDEMPOTENT** — Onboard is safe to re-run. It checks existing state first and only creates or updates the minimum missing bootstrap state.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-onboard

## Atomic purpose
Bring the repository into a valid beo operating state with minimal safe changes.

## When to use
- `.beads/` bootstrap state is missing or stale
- required beo tooling is missing, outdated, or unverified
- another beo skill cannot safely start until environment readiness is confirmed

## Inputs
**Required**
- repository root state
- installed tool versions for Node, `br`, and `bv`
- existing `.beads/` structure and onboarding artifacts when present

**Optional**
- existing `AGENTS.md`
- repo-specific bootstrap templates or scripts referenced by local onboarding docs

## Outputs
**Allowed writes**
- missing beo bootstrap directories / files
- safe updates to `AGENTS.md` when onboarding guidance must be merged
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- feature artifacts for active work
- implementation code
- destructive overwrites of user-authored content

## Boundary rules
- Onboard owns environment and bootstrap readiness only.
- Onboard does not perform routing, requirements, planning, validation, execution, review, debugging, learning, or authoring work.
- Onboard should make the smallest safe change that enables the rest of the beo system to function.

## Minimum hard gates
- **TOOLING-VERIFICATION** — Confirm the required toolchain and minimum versions before continuing.
- **NO-DESTRUCTIVE-WRITES** — Never overwrite existing managed or user-authored content without an explicit safe merge path.
- **STRUCTURED-APPROVALS-ONLY** — Use the structured question tool before applying bootstrap changes that affect shared repo guidance.
- **TERMINATE-ON-HANDOFF** and **FRESH-LOAD-REQUIRED** — Follow the shared session-boundary rules.

## Default loop
1. Inspect the repo for beo bootstrap readiness and current onboarding artifacts.
2. Verify Node, `br`, and `bv` against the onboarding requirements.
3. If tooling is missing or too old, report the exact gap and stop.
4. Summarize the minimum bootstrap changes required and obtain any needed approval.
5. Create only the missing beo structure and safely merge shared onboarding guidance when necessary.
6. Verify the resulting setup, write handoff state to `beo-route`, and stop.

## References
| File | Use when |
|------|----------|
| `references/onboarding-flow.md` | Running readiness checks, bootstrap order, and stop conditions |
| `beo-reference` → `references/artifact-conventions.md` | Knowing where beo bootstrap state belongs |
| `beo-reference` → `references/state-and-handoff-protocol.md` | Writing canonical handoff state |
| `beo-reference` → `references/shared-hard-gates.md` | Session boundaries and shared onboarding rules |

## Handoff and exit
- Normal completion handoff: `beo-route`
- Onboard stops after writing handoff state.

## Context budget
If context exceeds 30%, checkpoint via the shared protocol in `beo-reference` → `references/shared-hard-gates.md`.

## Red flags
- overwriting existing user-authored repo content
- proceeding without verified `br` / `bv` readiness
- creating feature artifacts during onboarding
- continuing after writing handoff state
