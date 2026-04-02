---
name: beo-router
description: >-
  Use whenever a beo session is starting, resuming, recovering from interruption,
  checking status, deciding what to do next, or when the correct beo skill is
  not obvious. Use first for prompts like "continue", "resume", "what's
  next?", "status?", "pick this back up", "where are we?", or any new
  feature request where the current phase is unclear.
---

# Beo Router

## Overview

`beo-router` is the entry point for beo sessions.
Its job is simple:

1. determine the real workflow state from artifacts and the live graph
2. explain that state in human terms
3. load exactly one next skill

**Core principle:** always know where you are before deciding where to go.

## Default Router Loop

1. confirm the workspace is initialized and healthy
2. check for `.beads/HANDOFF.json`
3. identify the active epic, if any
4. inspect the active feature's core artifacts and task graph
5. classify the current state using the canonical routing table
6. report the state in human terms
7. load exactly one next skill

Use `references/router-operations.md` when you need the exact bootstrap steps, instant-path scaffold, resume validation procedure, planning-aware routing rules, or doctor-mode commands.
Use `references/state-routing.md` for the canonical state table.

## Hard Gates

<HARD-GATE>
If the current pipeline phase is unclear, use `beo-router` before loading any other beo skill.
Do not guess the phase from memory, partial artifacts, or the last conversational turn alone.
</HARD-GATE>

<HARD-GATE>
If `.beads/HANDOFF.json` exists, read it before normal routing.
Do not skip the handoff path.
</HARD-GATE>

<HARD-GATE>
When resuming from handoff, trust the stored `skill` and `next_action` unless live graph state or current artifacts clearly contradict them.
Do not blindly trust stale checkpoints, but do not recompute from scratch when the handoff is still valid.
</HARD-GATE>

<HARD-GATE>
If `phase-plan.md` exists, treat `phase-contract.md` and `story-map.md` as current-phase artifacts, not whole-feature artifacts.
</HARD-GATE>

<HARD-GATE>
If current-phase work is complete but later phases remain, do not treat the feature as complete. Route back to `beo-planning`.
</HARD-GATE>

<HARD-GATE>
If instant-scoped work expands during inspection, stop treating it as instant work and promote it into the normal pipeline.
</HARD-GATE>

## Routing Notes

Load `references/router-operations.md` when you need exact bootstrap steps, artifact inspection order, instant-path scaffold, resume validation, planning-aware routing, or doctor-mode commands.

### Bootstrap and resume
- If `.beads/` is missing or unhealthy, repair bootstrap before routing.
- If `.beads/HANDOFF.json` exists, read it first, verify it against the live graph and current artifacts, then resume the saved `skill` and `next_action`.
- If planning-aware fields exist in the handoff, trust them unless live state clearly contradicts them.
- Clean up `HANDOFF.json` only after a fresh `STATE.md` or equivalent checkpoint exists.
- If `mode = "go"`, resume inside go-mode rather than normal feature routing.

### Active-feature inspection
Inspect the active epic, task graph, actionable / blocked work, and the current artifact set.
At minimum orient on:
- `CONTEXT.md`
- `approach.md`
- `phase-plan.md`
- `phase-contract.md`
- `story-map.md`

Use the canonical inspection order in `references/router-operations.md`.
Use `references/state-routing.md` for the canonical state names and first-match-wins order.
Do not invent ad-hoc state labels.

## Report State Before Routing

Always report the state in human terms before loading the next skill.
At minimum include:
- feature
- mode (`single-phase`, `multi-phase`, or unknown)
- current phase if known
- canonical state
- progress / blockers
- next action

## Planning-Aware Routing Rules

Keep these rules explicit:
- if `CONTEXT.md` exists but `approach.md` does not, route to `beo-planning`
- if `approach.md` exists but current-phase artifacts are missing, route to `beo-planning`
- if `phase-plan.md` exists, do not assume current-phase completion means feature completion
- if current-phase work is complete and later phases remain, route to `beo-planning`
- if current-phase tasks already advanced but `approved` is now missing, treat approval as invalidated and route to `beo-planning`
- if execution scope is complete and no later phases remain, route to `beo-reviewing`

## New Feature Intake

When no active feature exists, still use the canonical routing model.
The intake-specific states are:
- `new-instant-intake` -> create the epic, preserve the immutable slug using `../reference/references/slug-protocol.md`, scaffold minimal artifacts, then route to `beo-validating`
- `new-debug-intake` -> `beo-debugging`
- `meta-skill` -> `beo-writing-skills`
- otherwise -> create the epic and route to `beo-exploring`

If a request first looks instant but inspection shows it is larger, ambiguous, or phase-shaped, preserve any existing instant task bead as planning input and promote the work into the normal pipeline.
## Doctor Mode

When asked to check project health, inspect graph health, blocked work, stale work, planning shape, artifact presence, and one next corrective action.

## Priority Rules

These override normal routing:

1. P1 review findings block progress.
2. `CONTEXT.md` is the source of truth for locked decisions.
3. Never skip `beo-validating`.
4. Spike failures halt the pipeline and send work back to planning.
5. Current-phase completion is not whole-feature completion when later phases remain.

## Handoff

After classification, report the current state in human terms and load exactly one next skill.
If a checkpoint or resume artifact exists, preserve the planning-aware state while handing off.

## Context Budget

If context usage exceeds 65%, checkpoint using `../reference/references/state-and-handoff-protocol.md`.
Include the current state, selected route, planning-aware fields when known, and any resume detail needed to continue safely.

## Red Flags and Anti-Patterns

See `references/guardrails.md` for the full tables.
