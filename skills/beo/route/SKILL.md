---
name: beo-route
description: |
  Use whenever a beo session is starting, resuming, or when the correct beo skill is unclear. Triggers: "continue", "resume", "status?", "what's next?", new feature requests, or conversational prompts like "let's explore X" or "help me think through X" that imply non-trivial work. Detects current pipeline state via br/bv and routes to the correct skill. MUST NOT execute pipeline work, modify delivery artifacts, or route to execute/swarm without a validated plan. Do not use for simple direct questions, quick one-off tasks, or when the correct beo skill is already obvious.
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References**: Protocol rules reference the `beo-reference` skill via `→ references/<file>` for canonical documents.

# beo-route

## Overview
Detect the current pipeline state and choose the next action using canonical routing rules, handoff precedence, and repo state signals. **Core principle: route only; never implement, plan, or mutate delivery artifacts.**

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
> **HARD-GATE: NO-IMPLEMENTATION** — Route never writes code, creates artifacts, or modifies beads. If violated, stop and revert to pure routing behavior.

> **HARD-GATE: HANDOFF-PRECEDENCE** — If `HANDOFF.json` exists, its `NextSkill` takes priority over state detection. If violated, routing is invalid and must restart per the STATE.json/HANDOFF.json protocol (`beo-reference` → `references/state-and-handoff-protocol.md`).

## Communication Standard
> Follow the communication standard (`beo-reference` → `references/communication-standard.md`).

## Default Route Loop
1. Read `STATE.json` and `HANDOFF.json`. If `HANDOFF.json` exists with `NextSkill`, use it and clear it after read per the STATE.json/HANDOFF.json protocol (`beo-reference` → `references/state-and-handoff-protocol.md`).
2. If no handoff exists, query `br` and `bv`, then match the observed state against the canonical routing table in the canonical pipeline routing table (`beo-reference` → `references/pipeline-contracts.md`) using first-match-wins semantics.
3. Emit `NextAction` as `LoadSkill(skill_name)`, `ReturnToUser(reason)`, or `Stop`, then update `STATE.json` per the STATE.json/HANDOFF.json protocol (`beo-reference` → `references/state-and-handoff-protocol.md`).

### Reference Files
| File | Purpose |
|------|---------|
| `references/router-operations.md` | Route-specific operational procedure and state detection guidance. |
| `references/go-mode.md` | Defines the go-mode branch used when fresh-start routing detects compressed intake behavior. |

## Inputs and Outputs
- **Inputs** — `STATE.json`, `HANDOFF.json`, `br`/`bv` state queries.
- **Outputs** — `NextAction (LoadSkill | ReturnToUser | Stop)`, updated `STATE.json`.
- Artifact paths and ownership follow artifact conventions (`beo-reference` → `references/artifact-conventions.md`).

## Pipeline Contract
- Pipeline sequence is fixed: `route → explore → plan → validate → (execute | swarm → execute) → review → compound`.
- Support skills remain on-demand or periodic: `debug`, `dream`, `author`, `onboard`.
- State transitions must follow the bead lifecycle states (`beo-reference` → `references/status-mapping.md`).

## Decision Rubrics
### Resume vs Fresh Start
- If `STATE.json.current_skill` is set and no `HANDOFF.json` is present, resume that skill.
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
> Write `HANDOFF.json` for every skill transition (`beo-reference` → `references/pipeline-contracts.md`). Transitions follow the pipeline: route → explore → plan → validate → (execute | swarm → execute) → review → compound.

## Context Budget
> If context exceeds 65% capacity, compress non-essential history before continuing (`beo-reference` → `references/shared-hard-gates.md`).

## Red Flags & Anti-Patterns
- Route spending more than 2 minutes on detection.
- Route modifying any artifact under `.beads/artifacts/<feature_slug>/`.
- Route making planning, validation, or implementation decisions.
- Route skipping `HANDOFF.json` when present.
- Route mutating bead state instead of returning the correct next action.
