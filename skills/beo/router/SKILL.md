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
Its job is simple:

1. determine the real workflow state from artifacts and the live graph
2. explain that state in human terms
3. produce exactly one `NextAction` — `LoadSkill(name)`, `ReturnToUser(reason)`, or `Stop(done)`

**Core principle:** always know where you are before deciding where to go.

## Hard Gates

<HARD-GATE>
If the current pipeline phase is unclear, use `beo-router` before loading any other beo skill.
Do not guess the phase from memory, partial artifacts, or the last conversational turn alone.
</HARD-GATE>

<HARD-GATE>
Conversational phrasing does not bypass the pipeline.
If the user asks to "research", "explore", "discuss", "think through", or "look into" a topic that implies non-trivial work, treat it as a new feature intake or exploration request — not as a freeform conversation outside beo.
Route through the state table normally; do not answer directly just because the prompt sounds casual.
Exception: simple lookup questions about existing code, quick explanations, syntax questions, or single-fact answers are not feature intake — answer those directly.
</HARD-GATE>

<HARD-GATE>
If `.beads/HANDOFF.json` exists, read it before normal routing.
Do not skip the handoff path.
</HARD-GATE>

<HARD-GATE>
When reading HANDOFF.json, validate the canonical schema fields: `skill` (source skill name), `next_action` (target skill or action), `feature` (epic ID), and `timestamp`. These are the authoritative fields defined in `../reference/references/state-and-handoff-protocol.md`. If any required field is missing or malformed, do not route — report the malformed handoff to the user and attempt to reconstruct routing from live graph state and artifacts.
</HARD-GATE>

<HARD-GATE>
When resuming from handoff, trust the stored `skill` and `next_action` unless live graph state or current artifacts clearly contradict them.
Do not blindly trust stale checkpoints, but do not recompute from scratch when the handoff is still valid.
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

1. confirm the repository is onboarded and the workspace is healthy
2. if `.beads/beo_status.mjs` exists, run `node .beads/beo_status.mjs --json` as a quick scout
3. check for `.beads/HANDOFF.json`
4. identify the active epic, if any
5. inspect the active feature's core artifacts and task graph
6. classify the current state using the canonical routing table
7. report the state in human terms
8. emit exactly one `NextAction`: `LoadSkill(name)` to continue the pipeline, `ReturnToUser(reason)` when a decision or clarification is needed, or `Stop(done)` when the session is complete

Use `references/router-operations.md` when you need the exact bootstrap steps, Quick-scope scaffold, resume validation procedure, planning-aware routing rules, or doctor-mode commands.
Use `../reference/references/pipeline-contracts.md` for the canonical state routing table.
Use `references/go-mode.md` when the user says "go", "run the full pipeline", or "go mode" and you need the 3-gate end-to-end sequence.
Use `../reference/references/communication-standard.md` for inter-skill message formatting when writing handoff messages or state reports.

## Report State Before Routing

Always report the state in human terms before loading the next skill.
At minimum include:
- feature
- mode (`single-phase`, `multi-phase`, or `unknown` pre-planning)
- current phase if known
- canonical state
- progress / blockers
- next action

## New Feature Intake

When no active feature exists, still use the canonical routing model.
The intake-specific states are:
- `new-quick-intake` -> create the epic, preserve the immutable slug using `../reference/references/artifact-conventions.md#slug-lifecycle`, scaffold minimal artifacts via `references/router-operations.md` Quick Path Scaffold, then route to `beo-validating`
- `new-debug-intake` -> `beo-debugging`
- `meta-skill` -> `beo-writing-skills`
- otherwise -> create the epic and route to `beo-exploring`

If a request first looks quick but inspection shows it is larger, ambiguous, or phase-shaped, preserve any existing quick task bead as planning input and promote the work into the normal pipeline.
Before creating a new epic, always confirm there is not already an active one for the same feature.

## Doctor Mode

When asked to check project health, inspect graph health, blocked work, stale work, planning shape, artifact presence, and one next corrective action.
On first-session bootstrap or when workspace health is in doubt, include `br doctor` in the health check flow.

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

**Known limitation**: `STATE.json` and `HANDOFF.json` are currently singleton files. When multiple features are in flight simultaneously, verify the `feature` field matches the intended epic before trusting state. Feature-scoped state files are a future improvement.

Do not create duplicate epics, bypass validation because work seems small, route to swarming without a validated parallel plan, or skip compounding after successful review.
