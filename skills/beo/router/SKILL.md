---
name: beo-router
description: >-
  Use whenever a beo session is starting, resuming, recovering from interruption,
  checking status, deciding what to do next, or when the correct beo skill is
  not obvious. Use first for prompts like "continue", "resume", "what's
  next?", "status?", "pick this back up", "where are we?", or any new
  feature request where the current phase is unclear. Also use when the user
  asks to research, explore, discuss, or think through a topic that could
  become a feature — phrases like "can you research X with me", "let's
  explore X", "I want to build X", "help me think through X", or any
  request implying non-trivial work, even if phrased conversationally.
---

> **Onboarding gate:** If `.beads/onboarding.json` is missing or stale, stop and load `beo-using-beo` before continuing.

# Beo Router

## Overview

`beo-router` is the entry point for beo sessions.
Its job is simple:

1. determine the real workflow state from artifacts and the live graph
2. explain that state in human terms
3. load exactly one next skill

**Core principle:** always know where you are before deciding where to go.

## Default Router Loop

1. confirm the repository is onboarded and the workspace is healthy
2. if `.beads/beo_status.mjs` exists, run `node .beads/beo_status.mjs --json` as a quick scout
3. check for `.beads/HANDOFF.json`
4. identify the active epic, if any
5. inspect the active feature's core artifacts and task graph
6. classify the current state using the canonical routing table
7. report the state in human terms
8. load exactly one next skill

Use `references/router-operations.md` when you need the exact bootstrap steps, instant-path scaffold, resume validation procedure, planning-aware routing rules, or doctor-mode commands.
Use `references/state-routing.md` for the canonical state table.
Use `references/go-mode.md` when the user says "go", "run the full pipeline", or "go mode" and you need the 3-gate end-to-end sequence.

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
