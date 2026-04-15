---
name: beo-router
description: >-
  Use whenever a beo session is starting, resuming, or when the correct beo
  skill is unclear. Triggers: "continue", "resume", "status?", "what's
  next?", new feature requests, or conversational prompts like "let's explore
  X" or "help me think through X" that imply non-trivial work. Do not use for
  simple direct questions that need no project state, quick one-off tasks that fit the Quick scope definition,
  or when the correct beo skill is already obvious.
---

<HARD-GATE>
Onboarding — see `../reference/references/shared-hard-gates.md` § Onboarding Check.
</HARD-GATE>

# Beo Router

## Overview

`beo-router` is the entry point for beo sessions.
Its job:

1. determine the real workflow state from artifacts and the live graph
2. explain the state in human terms
3. produce exactly one `NextAction` — `LoadSkill(name)`, `ReturnToUser(reason)`, or `Stop(done)`

**Core principle:** always know where you are before deciding where to go.

## Hard Gates

<HARD-GATE>
If the current pipeline phase is unclear, use `beo-router` before loading any other beo skill.
</HARD-GATE>

<HARD-GATE>
Conversational phrasing does not bypass the pipeline.
Treat requests to "research", "explore", "discuss", "think through", or "look into" non-trivial work as new feature intake or exploration.
Answer directly only for simple lookups, quick explanations, syntax questions, or single-fact answers.
</HARD-GATE>

<HARD-GATE>
If `.beads/HANDOFF.json` exists, read it before normal routing.
Do not skip the handoff path.
</HARD-GATE>

<HARD-GATE>
When reading HANDOFF.json, validate all canonical base-schema fields from `../reference/references/state-and-handoff-protocol.md`: `schema_version`, `phase`, `skill`, `feature`, `feature_name`, `next_action`, `in_flight_beads`, and `timestamp`. If any required field is missing or malformed, do not route from the handoff — report the malformed handoff to the user and reconstruct routing from live graph state and artifacts.
</HARD-GATE>

<HARD-GATE>
When resuming from handoff, trust the stored `skill` and `next_action` unless live graph state or current artifacts prove the checkpoint stale or invalid.
</HARD-GATE>

<HARD-GATE>
Beo runs one active feature per workspace thread. If multiple active epics exist, do not silently choose one from `STATE.json`, `HANDOFF.json`, or conversational memory alone. Report the ambiguity, identify the candidate epics, and ask the user which feature to continue before routing deeper.
</HARD-GATE>

<HARD-GATE>
If `phase-plan.md` exists, treat `phase-contract.md` and `story-map.md` as current-phase artifacts, not whole-feature artifacts.
</HARD-GATE>

<HARD-GATE>
Multi-phase completion — see `../reference/references/shared-hard-gates.md` § Multi-Phase Completion Routing.
</HARD-GATE>

<HARD-GATE>
If quick-scoped work expands during inspection, stop treating it as quick work and promote it into the normal pipeline.
</HARD-GATE>

> See `../reference/references/shared-hard-gates.md` § Shared References Convention.

## Default Router Loop

1. confirm onboarding and workspace health
2. if `.beads/beo_status.mjs` exists, run `node .beads/beo_status.mjs --json`
3. check for `.beads/HANDOFF.json`
4. identify the active epic, if any
5. inspect core artifacts and task graph
6. classify state with the canonical routing table
7. report the state in human terms
8. emit exactly one `NextAction`: `LoadSkill(name)`, `ReturnToUser(reason)`, or `Stop(done)`

## References (load on demand)

| File | Use for |
| --- | --- |
| `references/router-operations.md` | exact bootstrap steps, Quick Path Scaffold, resume validation, planning-aware routing, doctor-mode commands |
| `../reference/references/pipeline-contracts.md` | canonical state routing table |
| `../reference/references/failure-recovery.md` | malformed `br`, `bv`, state files, or resume recovery |
| `references/go-mode.md` | "go", "run the full pipeline", or "go mode" 3-gate sequence |
| `../reference/references/communication-standard.md` | handoff and state-report formatting |

## Report State Before Routing

Report the state in human terms before loading the next skill.
Include: feature; mode (`single-phase`, `multi-phase`, or `unknown` pre-planning); current phase if known; canonical state; progress/blockers; next action.

## Core Routing Decision

Use `../reference/references/pipeline-contracts.md` as the canonical table, but apply these inline tie-breaks before leaving the skill:
- choose `Stop(done)` only when the epic is truly complete and no compounding handoff remains
- choose `ReturnToUser(...)` when the next safe step requires a human decision (for example: planning approval, blocker triage, or multi-epic ambiguity)
- otherwise choose exactly one `LoadSkill(...)` based on the highest-priority matching routing state

Treat live state as contradictory only when artifacts or the graph prove the handoff is stale — for example: the stored skill requires artifacts that are now missing, the cited epic is closed, or the next action conflicts with current labels/status.

For new work:
- quick-scoped request -> `new-quick-intake`
- clear debugging request -> `new-debug-intake`
- skill-authoring request -> `meta-skill`
- otherwise -> normal feature intake through exploring

## New Feature Intake

When no active feature exists, use the canonical routing model:
- `new-quick-intake` -> create the epic; preserve the immutable slug using `../reference/references/artifact-conventions.md#slug-lifecycle`; scaffold minimal artifacts via `references/router-operations.md` Quick Path Scaffold; route to `beo-validating`
- `new-debug-intake` -> `beo-debugging`
- `meta-skill` -> `beo-writing-skills`
- otherwise -> create the epic; route to `beo-exploring`

If a request first looks quick but inspection shows it is larger, ambiguous, or phase-shaped, preserve any existing quick task bead as planning input and promote the work into the normal pipeline.
Before creating a new epic, always confirm there is not already an active one for the same feature.

## Doctor Mode

When asked to check project health, inspect graph health, blocked work, stale work, planning shape, artifact presence, and the next corrective action.
On first-session bootstrap or when workspace health is doubtful, include `br doctor`.

## Priority Rules

These override normal routing:

1. P1 review findings block progress.
2. `CONTEXT.md` is the source of truth for locked decisions.
3. Never skip `beo-validating`.
4. Spike failures halt the pipeline and send work back to planning.
5. Current-phase completion is not whole-feature completion when later phases remain.
6. Quick-scope work still routes through validation before execution.
7. Choose `beo-swarming` only when validated parallel-ready tasks exist; otherwise route to `beo-executing`.

## Handoff

After classification, report the current state in human terms and emit exactly one `NextAction`: `LoadSkill(name)`, `ReturnToUser(reason)`, or `Stop(done)`.
If a checkpoint or resume artifact exists, preserve the planning-aware state while handing off.

## Context Budget

Follow `../reference/references/shared-hard-gates.md` § Context Budget Protocol. Skill-specific checkpoint items: current STATE.json, selected route, planning-aware fields when known, and any resume detail needed to continue safely.

## Red Flags & Anti-Patterns

**Single-feature workspace rule**: `STATE.json` and `HANDOFF.json` are singleton checkpoint files. Treat the workspace as one active feature thread at a time; if multiple active epics exist, stop and ask the user which one this workspace should continue.

Do not create duplicate epics, allow routing loops, or skip compounding after successful review.
