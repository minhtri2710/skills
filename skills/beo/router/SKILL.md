---
name: beo-router
description: >-
  Use whenever a beo session is starting, resuming, recovering from interruption,
  checking status, deciding what to do next, or when the correct beo skill is
  not obvious. This is the default bootstrap and routing entry point for the beo
  pipeline. Use first for prompts like "continue", "resume", "what's next?",
  "status?", "pick this back up", "where are we?", or any new feature request
  where the current phase is unclear.
---

# Beo Router

## Overview

The router is the entry point for every beo session. It bootstraps the workspace, detects current state, and routes to the correct pipeline skill.

**Core principle**: Always know where you are before deciding where to go.

## Router Default Rule

If the current pipeline phase is unclear, use `beo-router` before loading any other beo skill.
Do not guess the phase from memory, partial artifacts, or the last conversational turn alone.

## Minimal Bootstrap Fallback

If router reference files are unavailable, do the minimum safe sequence manually:
1. Check `.beads/HANDOFF.json`
2. List open epics
3. Inspect the active epic and its task graph
4. Check whether `CONTEXT.md`, `phase-contract.md`, and `story-map.md` exist
5. Report the current state, then route to the next matching skill

## Skill Catalog

| # | Skill | One-line description | Load when... |
|---|-------|----------------------|--------------|
| 1 | `beo-router` | This file. Bootstrap, state detection, routing. | Starting any session |
| 2 | `beo-exploring` | Socratic dialogue → lock decisions → CONTEXT.md | Feature request is vague or new |
| 3 | `beo-planning` | Research + synthesis → phase-contract.md + story-map.md + beads | Decisions are locked (CONTEXT.md exists) |
| 4 | `beo-validating` | Verify phase contract, story map, bead graph (8 dimensions) | Stories and beads exist; prove execution-readiness |
| 5 | `beo-swarming` | Launch + tend worker pool via Agent Mail + bv | Beads validated; execute at scale (3+ independent tasks) |
| 6 | `beo-executing` | Single worker loop: claim → build prompt → implement → verify → report | Spawned by swarming, or direct for ≤2 tasks |
| 7 | `beo-reviewing` | 5 parallel review agents (P1/P2/P3) + artifact verification + UAT | Execution complete; quality gate before close |
| 8 | `beo-compounding` | Capture learnings → critical-patterns.md | Feature shipped; extract patterns/decisions/failures |
| 9 | `beo-debugging` | Root-cause analysis for blocked beads and execution failures | Agent stuck, bead blocked, unexpected error |
| 10 | `beo-dream` | Periodic consolidation of learnings across features | Learnings stale (>30 days or 3+ since last) |
| 11 | `beo-writing-skills` | TDD-for-skills: create and pressure-test beo skills | Improving or creating beo skills |

## Phase 0: Workspace Bootstrap

Run once per session. Skip if `.beads/` already exists and is healthy.

Load `references/router-operations.md` when you need the exact bootstrap commands or doctor-mode commands.

## Phase 1: State Detection

Determine the current state of work by querying the bead graph.

### Step 1: Check for HANDOFF.json

```bash
cat .beads/HANDOFF.json 2>/dev/null
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
cat .beads/artifacts/<feature-name>/phase-contract.md 2>/dev/null
cat .beads/artifacts/<feature-name>/story-map.md 2>/dev/null
```

### Step 4: Classify Feature State

See `references/state-routing.md` for the full state routing table (14 conditions, first-match-wins evaluation).

### Step 5: Report State

Before routing, always report the current state to the user:

```
Feature: <epic title>
State: <state from table>
Progress: <closed>/<total> tasks (<in_progress> in progress)
Blockers: <count> (<details if any>)
Next action: Loading <skill name>...
```

## Phase 2: New Feature

When no active feature exists and the user has a request:

### Step 1: Create the Epic

Load `references/router-operations.md` for the exact epic-creation and slug-storage commands.

Save the returned epic ID for all downstream operations.

### Step 2: Classify Request Complexity

| Signal | Classification | Path |
|--------|---------------|------|
| Single file change, well-scoped, <30 min | **instant** | Create task directly, route to `beo-executing` |
| 2-3 files, clear scope, <2 hours | **lightweight** | Route to `beo-exploring` (quick-depth pass, then planning) |
| Multi-file, needs research, >2 hours | **standard** | Route to `beo-exploring` |
| Ambiguous, needs clarification | **unclear** | Route to `beo-exploring` |
| Error, blocker, failure symptoms | **debug** | Route to `beo-debugging` |

### Step 3: Route

- **instant**: Load `references/router-operations.md` and follow the **Instant Path Scaffold** exactly. Create one task bead, write a Markdown description using the shared bead templates, scaffold minimal artifacts, mark the epic approved, then route to `beo-executing`.

- **debug**: Route to `beo-debugging` directly.
- **meta-skill**: Route to `beo-writing-skills` directly.
- **lightweight/standard/unclear**: Route to the appropriate skill.

### Promotion Guard

If you classified as **instant** but discover the work is bigger, load `references/router-operations.md` and follow the promotion guard exactly.

## Phase 3: Resume from Handoff

When HANDOFF.json exists:

Load `references/router-operations.md` for the exact resume-from-handoff procedure, validation checks, and cleanup rule. Then load the skill indicated by `HANDOFF.json.skill` and follow `next_action`.

## Phase 4: Health Check (Doctor Mode)

When asked to check project health or diagnose issues, load `references/router-operations.md` and follow the doctor-mode commands and diagnostic table.

## Context Budget

If context usage exceeds 65%, use `../reference/references/state-and-handoff-protocol.md` for the canonical `HANDOFF.json` shape, then add any router-specific resume detail you need before pausing.

## Skill Routing Quick Reference

| User Says | Route To |
|-----------|----------|
| "build X", "add X", "implement X" | Phase 2 → complexity classification → appropriate skill |
| "what's the status?" | Phase 1 → report state |
| "continue", "resume" | Phase 3 (if HANDOFF.json) or Phase 1 |
| "check health", "doctor" | Phase 4 |
| "plan X" | `beo-planning` directly |
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
6. **Never skip validating.** Not for small features. Not for "obvious" plans. Skipping validating is the #1 cause of wasted execution work.
7. **critical-patterns.md is mandatory context.** If it exists, read it before planning or executing. Ignoring past critical patterns is the #1 source of repeat failures.

## Red Flags and Anti-Patterns

See `references/guardrails.md` for red flags (8 items) and anti-patterns (6 items).
