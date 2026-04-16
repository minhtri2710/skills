---
name: beo-route
description: |
  Use when a beo pipeline session starts, resumes after interruption, or the correct next skill is ambiguous. Reads STATE.json, optional HANDOFF.json, onboarding readiness, and bead state via br/bv to select exactly one next action: load a skill, return control to the user, or stop. Do not use when the correct skill is already known, for requirements gathering (use beo-explore), solution design (use beo-plan), plan verification (use beo-validate), implementation (use beo-execute/beo-swarm), quality assessment (use beo-review), failure diagnosis (use beo-debug), or learning capture (use beo-compound/beo-dream).
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References**: Protocol rules reference the `beo-reference` corpus via `→ references/<file>` for canonical documents.

# beo-route

## Overview
**Atomic purpose: detect current pipeline state and emit exactly one skill-routing directive.** Select the single correct next action from current pipeline state. **Core principle: route only — never implement, plan, or perform intake scaffolding beyond pure routing.**

## Boundary Rules
- **MUST NOT** gather requirements — owned by `beo-explore`.
- **MUST NOT** decompose work — owned by `beo-plan`.
- **MUST NOT** verify plans — owned by `beo-validate`.
- **MUST NOT** write code — owned by `beo-execute`.
- **MUST NOT** orchestrate workers — owned by `beo-swarm`.
- **MUST NOT** review implementations — owned by `beo-review`.
- **MUST NOT** capture learnings — owned by `beo-compound`.
- **MUST NOT** diagnose failures — owned by `beo-debug`.
- **MUST NOT** consolidate learnings — owned by `beo-dream`.

## Hard Gates
> **HARD-GATE: NO-IMPLEMENTATION** — Route does not write implementation code, create epics, create beads, create feature artifacts, or modify existing feature artifacts. Route selects the next action only. If route starts doing exploration, planning, validation, implementation, or artifact creation, stop and revert to pure routing behavior.

> **HARD-GATE: HANDOFF-PRECEDENCE** — If `HANDOFF.json` exists, its `NextSkill` takes priority over state detection. If violated, routing is invalid and must restart per the STATE.json/HANDOFF.json protocol (`beo-reference` → `references/state-and-handoff-protocol.md`).

## Communication Standard
> Follow the communication standard (`beo-reference` → `references/communication-standard.md`).

## Default Route Loop
1. Read `STATE.json` and `HANDOFF.json`. If `HANDOFF.json` exists with `NextSkill`, use it and clear it after read per the STATE.json/HANDOFF.json protocol (`beo-reference` → `references/state-and-handoff-protocol.md`).
2. If no handoff exists, query `br` and `bv`, then match the observed state against the canonical routing table in the canonical pipeline routing table (`beo-reference` → `references/pipeline-contracts.md`) using first-match-wins semantics.
3. Select the matching next action based on the routing table. Route does not create artifacts; if fresh intake requires scaffolding, route to the appropriate skill.
4. Emit `NextAction` as `LoadSkill(skill_name)`, `ReturnToUser(reason)`, or `Stop`, then update `STATE.json` per the STATE.json/HANDOFF.json protocol (`beo-reference` → `references/state-and-handoff-protocol.md`).

### Reference Files
| File | Purpose |
|------|---------|
| `references/router-operations.md` | Route-specific operational procedure and state detection guidance. |
| `references/go-mode.md` | Defines the go-mode branch used when fresh-start routing detects compressed intake behavior. |

## Inputs and Outputs
- **Inputs** — Current user request or resume signal, `STATE.json`, optional `HANDOFF.json`, onboarding readiness signal (`br`, `bv`, `.beads/`), current bead status snapshot from `br`/`bv`.
- **Outputs** — `NextAction (LoadSkill | ReturnToUser | Stop)`, updated `STATE.json`, consumed/cleared `HANDOFF.json` if present.
- Artifact paths and ownership follow artifact conventions (`beo-reference` → `references/artifact-conventions.md`).

## Pipeline Contract
- Pipeline sequence is fixed: `route → explore → plan → validate → (execute | swarm → execute) → review → compound`.
- Support skills remain on-demand or periodic: `debug`, `dream`, `author`, `onboard`.
- State transitions must follow the bead lifecycle states (`beo-reference` → `references/status-mapping.md`).

## Decision Rubrics
### Resume vs Fresh Start
- If `STATE.json.skill` is set and no `HANDOFF.json` is present, resume that skill.
- If `STATE.json` is missing, treat the request as a fresh start and decide between go-mode handling or `beo-explore`.

### Handoff vs Detection
- If `HANDOFF.json` contains `NextSkill`, always honor it first.
- Only run state detection when no valid handoff is present.

### Ambiguous State
- If multiple routing rows match, use the first canonical match from the canonical pipeline routing table (`beo-reference` → `references/pipeline-contracts.md`).
- If no row matches, return control to the user with a concise state dump and clear recovery direction.

## Failure Recovery
> Any routing failure, missing state, malformed handoff, or unmatched pipeline condition must return a concise recovery action to the user.

## Handoff
> Write `STATE.json` when routing to the next adjacent skill so the selected skill receives current status, gating signals, and artifact pointers. Use `HANDOFF.json` only for emergency checkpoint or low-context resume scenarios.

## Context Budget
> If context exceeds 65% capacity, compress non-essential history before continuing (`beo-reference` → `references/shared-hard-gates.md`).

## Red Flags & Anti-Patterns
- Route spending more than 2 minutes on detection.
- Route modifying any artifact under `.beads/artifacts/<feature_slug>/`.
- Route making planning, validation, or implementation decisions.
- Route skipping `HANDOFF.json` when present.
- Route mutating bead state instead of returning the correct next action.
- Route creating epics, beads, or feature directory stubs (scaffolding belongs to downstream skills).
