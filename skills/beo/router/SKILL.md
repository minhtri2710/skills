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

The router is the entry point for every beo session. It bootstraps the workspace, detects current state, and routes to the correct pipeline skill.

**Core principle**: Always know where you are before deciding where to go.

## Key Terms

- **instant**: single-file or similarly tiny work, well-scoped, typically under 30 minutes, with no meaningful planning ambiguity
- **current phase**: the slice being prepared or executed now; in multi-phase work this is narrower than the whole feature
- **single-phase**: one closed loop can safely deliver the feature
- **multi-phase**: the feature needs 2-4 intentional slices, and only one slice should be prepared now
- **feature complete**: no later phases remain and the final execution scope has passed review

## Default Router Loop

Use this happy-path loop before loading deeper reference material:

1. confirm the workspace is initialized and healthy
2. check for `HANDOFF.json`
3. identify the active epic, if any
4. inspect the core artifacts for that feature
5. classify the current state
6. report the state in human terms
7. load exactly one next skill

Reach for `references/router-operations.md` when you need the exact command sequence, instant-path scaffolding details, or doctor-mode mechanics.

## Router Default Rule

<HARD-GATE>
If the current pipeline phase is unclear, use `beo-router` before loading any other beo skill.
Do not guess the phase from memory, partial artifacts, or the last conversational turn alone.
</HARD-GATE>

## Minimal Bootstrap Fallback

If router reference files are unavailable, do the minimum safe sequence manually:
1. Check `.beads/HANDOFF.json`
2. List open epics
3. Inspect the active epic and its task graph
4. Check whether `CONTEXT.md`, `approach.md`, `phase-contract.md`, and `story-map.md` exist
5. Report the current state, then route to the next matching skill

## Skill Catalog

| # | Skill | One-line description | Load when... |
|---|-------|----------------------|--------------|
| 1 | `beo-router` | This file. Bootstrap, state detection, routing. | Starting any session |
| 2 | `beo-exploring` | Socratic dialogue → lock decisions → CONTEXT.md | Feature request is vague or new |
| 3 | `beo-planning` | Research + synthesis → `discovery.md` + `approach.md` + `plan.md` + optional `phase-plan.md` + current-phase contract/story/beads | Decisions are locked (CONTEXT.md exists) |
| 4 | `beo-validating` | Verify current phase contract, story map, and bead graph (8 dimensions) | Stories and beads exist; prove execution-readiness |
| 5 | `beo-swarming` | Launch + tend worker pool via Agent Mail + bv | Beads validated; execute at scale (3+ independent tasks) |
| 6 | `beo-executing` | Single worker loop: claim → build prompt → implement → verify → report | Spawned by swarming, or direct for ≤2 tasks |
| 7 | `beo-reviewing` | 5 parallel review agents (P1/P2/P3) + artifact verification + UAT | Final execution scope complete; quality gate before close |
| 8 | `beo-compounding` | Capture learnings → critical-patterns.md | Feature shipped; extract patterns/decisions/failures |
| 9 | `beo-debugging` | Root-cause analysis for blocked beads and execution failures | Agent stuck, bead blocked, unexpected error |
| 10 | `beo-dream` | Periodic consolidation of learnings across features | Learnings stale (>30 days or 3+ since last) |
| 11 | `beo-writing-skills` | TDD-for-skills: create and pressure-test beo skills | Improving or creating beo skills |
| 12 | `beo-reference` | Shared CLI reference, status mapping, approval gates, artifact protocol | Any skill needs canonical lookup tables |

## Phase 0: Workspace Bootstrap

Run once per session. Skip if `.beads/` already exists and is healthy.

Default bootstrap sequence:

```bash
# Check if beads workspace exists (use your file reading tool to read .beads/ directory)

# Initialize only when missing
br init

# Verify the CLI and workspace health
br --version
br doctor
```

If `.beads/` exists and `br doctor` is clean, continue. If health is unclear or bootstrap behaves unexpectedly, then load `references/router-operations.md` for the full recovery and doctor-mode playbook.

## Phase 1: State Detection

Determine the current state of work by querying the bead graph.

### Step 1: Check for HANDOFF.json

```bash
Read .beads/HANDOFF.json
```

If HANDOFF.json exists, go to **Phase 3: Resume**.

### Step 2: Detect Active Feature

```bash
# List all epics including in_progress and closed (filter in application logic)
br list --type epic -a --json
```

Parse the output:
- **No epics** → New feature request → go to Phase 2
- **One open epic** → Active feature → go to Step 3
- **Multiple open epics** → Ask user which feature to work on

### Step 3: Assess Feature Progress

For the active epic, gather full state:

```bash
# Get epic details
br show <EPIC_ID> --json
```

Extract the immutable `slug: <feature_slug>` line from the epic description. Use that slug for all artifact existence checks below.

```bash
# List tasks under this epic (canonical enumeration; see pipeline-contracts.md)
br dep list <EPIC_ID> --direction up --type parent-child --json

# Check graph health (scoped to active epic)
bv --robot-triage --graph-root <EPIC_ID> --format json

# Check what's actionable
bv --robot-next --format json
br ready --json
br blocked --json

# Check planning artifacts exist
Read .beads/artifacts/<feature_slug>/CONTEXT.md
Read .beads/artifacts/<feature_slug>/discovery.md
Read .beads/artifacts/<feature_slug>/approach.md
Read .beads/artifacts/<feature_slug>/phase-plan.md
Read .beads/artifacts/<feature_slug>/phase-contract.md
Read .beads/artifacts/<feature_slug>/story-map.md
```

### Step 4: Classify Feature State

See `references/state-routing.md` for the canonical routing table sourced from `../reference/references/pipeline-contracts.md`. Use those canonical state names when reporting or checkpointing state; do not invent ad-hoc labels.

In normal feature flow, the most common canonical states are:

- `meta-skill`
- `needs-debugging`
- `blocked`
- `exploring`
- `planning-needs-approach`
- `planning-current-phase`
- `ready-to-validate`
- `ready-to-execute`
- `ready-to-swarm`
- `executing`
- `ready-to-review`
- `partial-completion`
- `learnings-pending`
- `completed`
- `consolidation-due`

If `phase-plan.md` exists, treat `phase-contract.md` and `story-map.md` as **current-phase** artifacts, not whole-feature artifacts.

### Step 5: Report State

Before routing, always report the current state to the user:

```text
Feature: <epic title>
Mode: <single-phase | multi-phase | unknown>
Current phase: <n>/<total or unknown> - <phase name if known>
State: <state from table>
Progress: <closed>/<total> tasks (<in_progress> in progress)
Blockers: <count> (<details if any>)
Next action: Loading <skill name>...
```

## Phase 2: New Feature

When no active feature exists and the user has a request:

### Step 1: Create the Epic

Default sequence:

```bash
br create "<feature-name>" -t epic -p 1 --json
```

Save the returned epic ID for all downstream operations, then preserve the immutable slug using `../reference/references/slug-protocol.md`.

Load `references/router-operations.md` when you need the exact slug-storage procedure or instant-path scaffolding details.

### Step 2: Classify Request Complexity

| Signal | Classification | Path |
|--------|---------------|------|
| Single file change, well-scoped, <30 min | **instant** | Create task directly, scaffold minimal artifacts, route to `beo-validating` |
| 2-3 files, clear scope, <2 hours | **lightweight** | Route to `beo-exploring` (quick-depth pass, then planning) |
| Multi-file, needs research, >2 hours | **standard** | Route to `beo-exploring` |
| Ambiguous, needs clarification | **unclear** | Route to `beo-exploring` |
| Error, blocker, failure symptoms | **debug** | Route to `beo-debugging` |

### Step 3: Route

- **instant**: create one task bead, write a concise Markdown description using the shared bead templates, scaffold the minimal artifacts, then route to `beo-validating`. Load `references/router-operations.md` for the exact instant-path scaffold.

- **debug**: Route to `beo-debugging` directly.
- **meta-skill**: Route to `beo-writing-skills` directly.
- **lightweight/standard/unclear**: Route to the appropriate skill.

### Promotion Guard

If you classified as **instant** but discover the work is bigger:
1. stop treating it as instant work
2. preserve the existing task bead as planning input
3. route to `beo-exploring` or `beo-planning`
4. use `references/router-operations.md` for the exact promotion guard details

## Phase 3: Resume from Handoff

When HANDOFF.json exists:

1. read `.beads/HANDOFF.json`
2. verify the epic, task graph, and current artifacts still match the handoff
3. trust the stored `skill` and `next_action` unless live state clearly contradicts them
4. resume the named skill
5. remove or refresh `HANDOFF.json` only after a fresh `STATE.md` checkpoint exists

Load `references/router-operations.md` when you need the exact resume validation procedure or cleanup rule.

## Phase 4: Health Check (Doctor Mode)

When asked to check project health or diagnose issues, do this minimum sequence first:

1. inspect graph health
2. inspect blocked work
3. inspect stale work
4. report the planning shape (single-phase vs multi-phase, current-phase artifacts present or missing)
5. recommend one next corrective action

Load `references/router-operations.md` for the exact doctor-mode commands and diagnostic table.

## Context Budget

<HARD-GATE>
If context usage exceeds 65%, use `../reference/references/state-and-handoff-protocol.md` for the canonical `HANDOFF.json` shape, then add any router-specific resume detail you need before pausing.
Do not continue burning context once the checkpoint threshold is crossed.
</HARD-GATE>

## Skill Routing Quick Reference

| User Says | Route To |
|-----------|----------|
| "build X", "add X", "implement X" | Phase 2 → complexity classification → appropriate skill |
| "what's the status?" | Phase 1 → report state |
| "continue", "resume" | Phase 3 (if HANDOFF.json) or Phase 1 |
| "check health", "doctor" | Phase 4 |
| "plan X" | `beo-planning` directly **only if** `CONTEXT.md` exists for the feature; otherwise route through Phase 2 state detection (which will route to `beo-exploring` first) |
| "review" | `beo-reviewing` directly |
| "what should I work on next?" | Phase 1 → `bv --robot-next` → report recommendation |
| "debug this", "why is X failing", "fix error" | `beo-debugging` |
| "what did we learn", "capture learnings" | `beo-compounding` |
| "swarm", "parallel workers", "launch workers" | `beo-swarming` |
| "dream", "consolidate learnings" | `beo-dream` |
| "write a skill", "create a skill", "edit skill" | `beo-writing-skills` |
| "go", "run the full pipeline", "go mode" | Go Mode (below) |

## Go Mode (Full Pipeline)

See `references/go-mode.md` for the full Go Mode workflow (3 human gates, sequence, context budget).

## Priority Rules

These override all other routing and execution decisions:

1. **P1 review findings always block.** Never merge, never close epic, never proceed to compounding while P1 findings are open.
2. **Context budget always applies.** If context usage exceeds 65%, write `.beads/HANDOFF.json` and pause. Do not continue burning context.
3. **CONTEXT.md is the source of truth.** If implementation diverges from a locked decision in CONTEXT.md, stop and surface the conflict before proceeding.
4. **Gate 2 (post-validating) is the most critical gate.** Execution is irreversible at scale. If there is any doubt about the plan's soundness, do not approve; loop back to validating.
5. **Spike failures halt the pipeline.** A failed spike means the approach is broken. Do not proceed to swarming; return to planning.
<HARD-GATE>
6. **Never skip validating.** Not for small features. Not for "obvious" plans. Skipping validating is the #1 cause of wasted execution work.
</HARD-GATE>
7. **critical-patterns.md is mandatory context.** If it exists, read it before planning or executing. Ignoring past critical patterns is the #1 source of repeat failures.
8. **Current-phase completion is not whole-feature completion for multi-phase work.** If `phase-plan.md` exists and later phases remain, route back to `beo-planning` instead of jumping to final review.

## Red Flags and Anti-Patterns

See `references/guardrails.md` for red flags (8 items) and anti-patterns (6 items).
