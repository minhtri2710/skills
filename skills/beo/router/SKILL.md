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

## Minimal Bootstrap

Run once per session when `.beads/` is missing or health is unclear.

Minimum safe sequence:
1. verify `.beads/` exists or initialize it
2. verify `br` works
3. run workspace health checks

If bootstrap or health recovery gets messy, load `references/router-operations.md`.

## State Detection

### 1. Check for handoff first
If `.beads/HANDOFF.json` exists, go to resume flow before normal classification.

### 2. Find the active feature
Inspect epics and identify the active one, if any.
If multiple open epics exist, ask the user which feature to work on.
If no epic exists, treat the request as new feature intake.

### 3. Inspect the active feature
Inspect, at minimum:
- epic details
- task graph
- actionable / blocked work
- `CONTEXT.md`
- `approach.md`
- `phase-plan.md`
- `phase-contract.md`
- `story-map.md`

Use the canonical artifact inspection order in `references/router-operations.md`.

### 4. Classify with the canonical routing table
Use `references/state-routing.md` for the canonical state names and first-match-wins routing order.
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

## New Feature Intake

When no active feature exists:

1. create the epic
2. preserve the immutable feature slug using `../reference/references/slug-protocol.md`
3. classify the request as one of:
   - `instant`
   - `lightweight`
   - `standard`
   - `unclear`
   - `debug`
   - `meta-skill`
4. route accordingly

### Default routing for new work
- `instant` -> scaffold minimal artifacts, then route to `beo-validating`
- `debug` -> `beo-debugging`
- `meta-skill` -> `beo-writing-skills`
- `lightweight` / `standard` / `unclear` -> usually `beo-exploring`

Use `references/router-operations.md` for the exact instant-path scaffold and slug-storage procedure.

## Instant Promotion Guard

If a request first looks instant but inspection shows it is larger, ambiguous, or phase-shaped:

1. stop treating it as instant work
2. preserve any existing instant task bead as planning input
3. route to `beo-exploring` or `beo-planning`, depending on what is already known

Use `references/router-operations.md` for the exact promotion procedure.

## Resume From Handoff

When `.beads/HANDOFF.json` exists:

1. read it first
2. verify the epic, task graph, and current artifacts still match the saved state
3. if planning-aware fields exist, treat them as the source of truth unless live state clearly contradicts them
4. resume the saved `skill` and `next_action`
5. remove or refresh `HANDOFF.json` only after a fresh `STATE.md` or equivalent checkpoint exists

Use `../reference/references/state-and-handoff-protocol.md` for the canonical schema and cleanup rule.
If `mode = "go"`, resume inside go-mode rather than normal feature routing.

## Planning-Aware Routing Rules

Keep these rules explicit:
- if `CONTEXT.md` exists but `approach.md` does not, route to `beo-planning`
- if `approach.md` exists but current-phase artifacts are missing, route to `beo-planning`
- if `phase-plan.md` exists, do not assume current-phase completion means feature completion
- if current-phase work is complete and later phases remain, route to `beo-planning`
- if execution scope is complete and no later phases remain, route to `beo-reviewing`

Use `references/router-operations.md` and `references/state-routing.md` for the exact routing conditions.

## Doctor Mode

When asked to check project health, inspect:
- graph health
- blocked work
- stale work
- planning shape and artifact presence
- one next corrective action

Use `references/router-operations.md` for the exact commands and interpretation table.

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
