---
name: beo-onboard
description: |
  Use when beo tooling or repository bootstrap state is missing, stale, or must be verified before pipeline skills can operate. Checks and installs required tools (br 0.1.28+, bv 0.15.2+), initializes missing .beads/ structure and bootstrap artifacts, and reports readiness. Idempotent and safe to re-run. Do not use for pipeline routing (use beo-route), feature work (requirements, planning, execution, review), or any destructive rewrite of existing data.
---

> **HARD-GATE: IDEMPOTENT** — Onboard is safe to re-run. It checks existing state and only creates or updates what is missing or stale.

> **Protocol References**: Protocol rules reference the `beo-reference` skill via `→ references/<file>` for canonical documents.

# beo-onboard

## Overview
**Atomic purpose: validate and bootstrap the environment so all beo skills can operate correctly.** Bring a repository into a valid beo operating state without destructive changes. **Core principle: initialize safely, verify explicitly, and never destroy existing project state.**

## Boundary Rules
- **MUST NOT** perform independent state detection or free-form routing — owned by `beo-route`. May emit canonical handoff to the next allowed pipeline skill when exit conditions are met.
- **MUST NOT** gather requirements — owned by `beo-explore`.
- **MUST NOT** decompose work — owned by `beo-plan`.
- **MUST NOT** verify plans — owned by `beo-validate`.
- **MUST NOT** write feature code — owned by `beo-execute`.
- **MUST NOT** review implementations — owned by `beo-review`.
- **MUST NOT** capture learnings — owned by `beo-compound`.
- **MUST NOT** diagnose failures — owned by `beo-debug`.
- **MUST NOT** orchestrate parallel worker execution — owned by `beo-swarm`.
- **MUST NOT** consolidate cross-feature learnings — owned by `beo-dream`.
- **MUST NOT** create skills — owned by `beo-author`.

## Hard Gates
> **HARD-GATE: TOOLING-VERIFICATION** — Node.js 18 or newer, `br` version 0.1.28 or newer, and `bv` version 0.15.2 or newer must be installed and accessible. If any required tool is missing or too old, provide installation guidance from `references/onboarding-flow.md` and stop.

> **HARD-GATE: NO-DESTRUCTIVE-WRITES** — Onboard never overwrites existing artifacts, beads, or user-authored data. If a write would replace existing content, stop and require an explicit update path.

## Communication Standard
> Follow the communication standard (`beo-reference` → `references/communication-standard.md`).

## Default Onboard Loop
1. **Check status** — Determine whether `.beads/` exists, whether onboarding artifacts match artifact conventions (`beo-reference` → `references/artifact-conventions.md`), and whether the repository is already current. If fully current, report status and stop.
2. **Install or verify tooling** — Confirm Node.js 18+, `br`, and `bv` meet minimum versions using `references/onboarding-flow.md`. If required tooling is unavailable, provide instructions and do not continue.
3. **Review planned changes and get approval** — Summarize the onboarding changes you intend to apply and obtain user approval before writing bootstrap files or updating shared repo guidance.
4. **Initialize structure** — Create only missing bootstrap structure, including `.beads/`, `STATE.json`, and required knowledge directories, using the repository's onboarding scripts and asset templates.
5. **Create or update AGENTS.md** — Add beo conventions, tool requirements, and editing guidance without removing existing user content unless an explicit safe merge path exists.
6. **Verify** — Confirm `br` responds, `bv` responds, required directories exist, and state files are valid; route any failure through standard failure recovery (`beo-reference` → `references/failure-recovery.md`).

### Reference Files
| File | Purpose |
|------|---------|
| `references/onboarding-flow.md` | Defines bootstrap checks, version requirements, initialization order, and stop conditions |

## Inputs and Outputs
- **Inputs** — Repository root state, Node/`br`/`bv` version info, existing `.beads/` structure and bootstrap files, existing `AGENTS.md`.
- **Outputs** — Onboarding status report, created missing bootstrap directories/files, safe `AGENTS.md` update/merge, verified tooling readiness.

## Decision Rubrics
### Fresh Install vs Update
- **Fresh install** when `.beads/` and other required beo artifacts do not exist.
- **Update in place** when the repository is partially onboarded or stale and only missing or outdated pieces need attention.

### Stop vs Continue
- **Stop** when `br` or `bv` is missing, below minimum version, or otherwise unavailable.
- **Continue** only after tooling verification passes and safe non-destructive initialization remains possible.

## Special Rules
- Treat file locations and ownership according to artifact conventions (`beo-reference` → `references/artifact-conventions.md`).
- Keep onboarding state and handoff files aligned to the STATE.json/HANDOFF.json protocol (`beo-reference` → `references/state-and-handoff-protocol.md`).
- Respect the shared hard gates (`beo-reference` → `references/shared-hard-gates.md`) and the beo approval gates (`beo-reference` → `references/approval-gates.md`) when onboarding intersects existing managed state.
- Preserve exact pipeline language: `route → explore → plan → validate → (execute | swarm → execute) → review → compound`; support skills remain `debug` on-demand, `dream` periodic, `author` meta, and `onboard` bootstrap.

## Handoff
> Handoff to `beo-route` for next-action detection after onboarding bootstrap or version gating completes. Write `STATE.json` for the normal transition, and reserve `HANDOFF.json` for emergency checkpoint or low-context resume scenarios.

## Context Budget
> If context exceeds 30% capacity (onboard-specific allocation), compress non-essential history before continuing (`beo-reference` → `references/shared-hard-gates.md`).

## Red Flags & Anti-Patterns
- Overwriting existing artifacts or user-authored data
- Proceeding without verified `br` and `bv` tooling
- Running full bootstrap on a repository that is already current instead of reporting status
- Creating beads, plans, or feature artifacts during onboarding
- Ignoring missing-state recovery guidance when verification fails
