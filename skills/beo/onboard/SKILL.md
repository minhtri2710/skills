---
name: beo-onboard
description: |
  Verify and minimally repair beo operating readiness when required tooling, bootstrap files, directories, or managed startup contract state is missing, stale, or invalid. Use only for environment and bootstrap readiness, not for product delivery, routing decisions, or general project setup beyond beo readiness.

---

> **HARD-GATE: IDEMPOTENT** — Onboard is safe to re-run. It checks existing state first and only creates or updates the minimum missing bootstrap state.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-onboard

## Atomic purpose
Establish and refresh safe beo readiness.

## When to use
- required beo bootstrap files or directories are missing or stale
- required beo tooling or runtime prerequisites are missing, outdated, or unverified
- the managed startup contract in `AGENTS.md` is stale or mismatched with onboarding metadata
- another beo skill cannot safely start until environment readiness is confirmed

## Inputs
**Required**
- repository root state
- required tool availability and versions
- existing `.beads/` structure and onboarding artifacts when present
- onboarding freshness metadata, including managed startup contract state

**Optional**
- existing `AGENTS.md`
- repo-specific bootstrap templates or scripts referenced by onboarding docs

## Outputs
**Allowed writes**
- readiness result
- missing bootstrap files or directories created only as needed
- safe managed startup contract updates to `AGENTS.md`
- `.beads/onboarding.json`
- `.beads/beo_status.mjs`
- `.beads/STATE.json`
- `.beads/critical-patterns.md` when missing
- `.beads/artifacts/` when missing
- `.beads/learnings/` when missing
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- feature artifacts for active work
- implementation code
- destructive overwrites of user-authored content

## Boundary rules
- Onboard owns environment and bootstrap validation only.
- Onboard must not act as general project setup, perform routing or feature delivery work, create feature artifacts, implement code, review work, debug blockers, extract learnings, or author skills.
- Onboard should make only the smallest safe changes needed for beo readiness.
- Onboard must not overwrite user-authored content destructively.
- Onboard must treat managed startup contract freshness as explicit state, not as an implied side effect of plugin version alone.

## Minimum hard gates
- **TOOLING-VERIFICATION** — Confirm the required toolchain and minimum versions before continuing.
- **NO-DESTRUCTIVE-WRITES** — Never overwrite existing managed or user-authored content without an explicit safe merge path.
- **CANONICAL-APPROVAL-PROTOCOL** — Use the runtime's canonical user-interaction mechanism before applying bootstrap changes that affect shared repo guidance.
- **TERMINATE-ON-HANDOFF** and **FRESH-LOAD-REQUIRED** — Follow the shared session-boundary rules.

## Default loop
1. Inspect the repo for beo bootstrap readiness and current onboarding artifacts.
2. Verify the runtime and tooling prerequisites required by onboarding, including Node for the local onboarding scripts plus `br` and `bv`.
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
