---
name: beo-onboard
description: |
  Use when a repository needs beo onboarding, when onboarding status must be checked, or when another beo skill reports that onboarding is missing or stale. Triggers: "onboard this repo", "set up beo", "check beo status". Bootstraps repository into valid beo operating state and verifies required tool versions (br 0.1.28+, bv 0.15.2+). MUST NOT overwrite existing artifacts, perform pipeline work, or proceed without verified tooling. Do not use when the repository is already fully onboarded and current.
---

> **HARD-GATE: IDEMPOTENT** — Onboard is safe to re-run. It checks existing state and only creates or updates what is missing or stale.

> **Protocol References**: Protocol rules reference the `beo-reference` skill via `→ references/<file>` for canonical documents.

# beo-onboard

## Overview
Bootstrap a repository into a valid beo operating state and verify required tool versions. **Core principle: initialize safely, verify explicitly, and never destroy existing project state.**

## Boundary Rules
- **MUST NOT** route to skills — owned by `beo-route`.
- **MUST NOT** gather requirements — owned by `beo-explore`.
- **MUST NOT** decompose work — owned by `beo-plan`.
- **MUST NOT** verify plans — owned by `beo-validate`.
- **MUST NOT** write feature code — owned by `beo-execute`.
- **MUST NOT** review implementations — owned by `beo-review`.
- **MUST NOT** capture learnings — owned by `beo-compound`.
- **MUST NOT** diagnose failures — owned by `beo-debug`.
- **MUST NOT** create skills — owned by `beo-author`.

## Hard Gates
> **HARD-GATE: TOOLING-VERIFICATION** — `br` version 0.1.28 or newer and `bv` version 0.15.2 or newer must be installed and accessible. If either tool is missing or too old, provide installation guidance from `references/onboarding-flow.md` and stop.

> **HARD-GATE: NO-DESTRUCTIVE-WRITES** — Onboard never overwrites existing artifacts, beads, or user-authored data. If a write would replace existing content, stop and require an explicit update path.

## Communication Standard
> Follow the communication standard (`beo-reference` → `references/communication-standard.md`).

## Default Onboard Loop
1. **Check status** — Determine whether `.beads/` exists, whether onboarding artifacts match artifact conventions (`beo-reference` → `references/artifact-conventions.md`), and whether the repository is already current. If fully current, report status and stop.
2. **Install or verify tooling** — Confirm `br` and `bv` meet minimum versions using `references/onboarding-flow.md`. If required tooling is unavailable, provide instructions and do not continue.
3. **Initialize structure** — Create only missing bootstrap structure, including `.beads/`, `STATE.json`, and required knowledge directories, using the repository's onboarding scripts and asset templates.
4. **Create or update AGENTS.md** — Add beo conventions, tool requirements, and editing guidance without removing existing user content unless an explicit safe merge path exists.
5. **Verify** — Confirm `br` responds, `bv` responds, required directories exist, and state files are valid; route any failure through standard failure recovery (`beo-reference` → `references/failure-recovery.md`).

### Reference Files
| File | Purpose |
|------|---------|
| `references/onboarding-flow.md` | Defines bootstrap checks, version requirements, initialization order, and stop conditions |

## Inputs and Outputs
- **Inputs** — Repository state, `br`/`bv` tool availability, existing `.beads/` structure, current `AGENTS.md`.
- **Outputs** — Initialized `.beads/` directory, `STATE.json`, verified tooling, updated `AGENTS.md`, onboarding status report.

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
> Write `HANDOFF.json` for every skill transition (`beo-reference` → `references/pipeline-contracts.md`). Transitions follow the pipeline: route → explore → plan → validate → (execute | swarm → execute) → review → compound.

## Context Budget
> If context exceeds 30% capacity (onboard-specific allocation), compress non-essential history before continuing (`beo-reference` → `references/shared-hard-gates.md`).

## Red Flags & Anti-Patterns
- Overwriting existing artifacts or user-authored data
- Proceeding without verified `br` and `bv` tooling
- Running full bootstrap on a repository that is already current instead of reporting status
- Creating beads, plans, or feature artifacts during onboarding
- Ignoring missing-state recovery guidance when verification fails
