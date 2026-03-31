---
name: beo-router
description: Use when starting a new session, resuming after a handoff, or needing to determine current feature state and next action. The bootstrap and routing skill for the beo pipeline.
---

# Beo Router

## Overview

The router is the entry point for every beo session. It bootstraps the workspace, detects current state, and routes to the correct pipeline skill.

**Core principle**: Always know where you are before deciding where to go.

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

```bash
# Check if beads workspace exists
ls .beads/ 2>/dev/null

# If missing, initialize
br init

# Verify br is working
br --version

# Check workspace health
br doctor
```

```bash
# Check knowledge search availability (optional: QMD enhances search but is not required)
qmd status 2>/dev/null
```

If `br doctor` reports issues, fix them before proceeding.

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

```bash
br create "<feature-name>" -t epic -p 1 --json
```

Save the returned epic ID for all downstream operations.

Derive the `feature_slug` from the epic title (see `pipeline-contracts.md` → Feature Slug). Store it in the epic description:
```bash
br update <EPIC_ID> --description "slug: <feature_slug>"
```

### Step 2: Classify Request Complexity

| Signal | Classification | Path |
|--------|---------------|------|
| Single file change, well-scoped, <30 min | **instant** | Create task directly, route to `beo-executing` |
| 2-3 files, clear scope, <2 hours | **lightweight** | Route to `beo-exploring` (quick-depth pass, then planning) |
| Multi-file, needs research, >2 hours | **standard** | Route to `beo-exploring` |
| Ambiguous, needs clarification | **unclear** | Route to `beo-exploring` |
| Error, blocker, failure symptoms | **debug** | Route to `beo-debugging` |

### Step 3: Route

- **instant**: Create a single task bead and mark epic approved:
  ```bash
  br create "<task-name>" -t task --parent <EPIC_ID> -p 1 --json
  br update <TASK_ID> --description "<Background + what to do + verify steps>"
  br label add <EPIC_ID> -l approved
  # Create minimal artifacts for downstream skills
  mkdir -p .beads/artifacts/<feature-name>
  # Write minimal CONTEXT.md stub
  # (use file editing tools to write: "# Feature: <name>\n\n## Request\n<user request>\n\n## Locked Decisions\nInstant-path: no exploration needed.\n\n## Scope Classification\n- Complexity: instant\n- Domains: <inferred>\n- Estimated blast radius: 1 file")
   # Write minimal plan.md stub
   # (use file editing tools to write: "# Plan: <name>\n\n## Approach\nSingle-task instant implementation.\n\n## Tasks\n### 1. <task-name>\nSee bead description for spec.")
   # Write minimal phase-contract.md stub
   # (use file editing tools to write: "# Phase Contract: <name>\n\n## 4. Exit State\n- Feature works as described in request.\n\n## 5. Demo Story\nInstant-path: single-task feature, no stories needed.")
   # Write minimal story-map.md stub
   # (use file editing tools to write: "# Story Map: <name>\n\n## 2. Story Table\n\n| Story | Purpose | Done Looks Like |\n|-------|---------|-----------------|\n| Story 1: Implement | Single-task implementation | Task complete and verified |\n\n## 5. Story-To-Bead Mapping\n\n| Story | Beads |\n|-------|-------|\n| Story 1 | <TASK_ID> |")
  ```
  Then route to `beo-executing`.

- **debug**: Route to `beo-debugging` directly.
- **meta-skill**: Route to `beo-writing-skills` directly.
- **lightweight/standard/unclear**: Route to the appropriate skill.

### Promotion Guard

If you classified as **instant** but discover the work is bigger:
- Stop implementation
- Route to `beo-exploring` or `beo-planning`
- The existing task bead becomes input for the plan

## Phase 3: Resume from Handoff

When HANDOFF.json exists:

### Step 1: Read Handoff State

```bash
cat .beads/HANDOFF.json
```

Expected format (see `beo-reference` → `pipeline-contracts.md` for canonical schema):
```json
{
  "schema_version": 1,
  "phase": "executing",
  "skill": "beo-executing",
  "feature": "<epic-id>",
  "feature_name": "<feature-name>",
  "next_action": "Continue executing task <TASK_ID>",
  "in_flight_beads": ["<TASK_ID_1>", "<TASK_ID_2>"],
  "timestamp": "2026-03-29T10:00:00Z"
}
```

### Step 2: Verify State is Still Valid

```bash
# Check that the epic still exists and is open
br show <feature_epic_id> --json

# Check task states haven't changed externally
br list --type task --json
```

### Step 3: Route to Saved Skill

Load the skill indicated by `HANDOFF.json.skill` and follow the `next_action`.

### Step 4: Clean Up

After the resumed skill writes a fresh STATE.md, delete the handoff file:
```bash
rm .beads/HANDOFF.json
```
Do NOT delete HANDOFF.json until the resumed skill has successfully checkpointed.

## Phase 4: Health Check (Doctor Mode)

When asked to check project health or diagnose issues:

```bash
# Full graph analysis
bv --robot-insights --format json

# Check for stale work
br stale --days 7 --json

# Check for cycles
br dep cycles --json

# Check for blocked items
br blocked --json
```

### Diagnostic Table

| Finding | Severity | Action |
|---------|----------|--------|
| Dependency cycles | **HIGH** | Report exact cycle, ask user to break it |
| Tasks blocked >24h | **MEDIUM** | Report blockers, suggest resolution |
| Tasks in_progress >4h with no commits | **MEDIUM** | May be abandoned; check with user |
| Epic with no tasks and no plan | **LOW** | Stale feature; suggest cleanup or activation |
| Closed tasks with open dependencies | **HIGH** | Inconsistent state; investigate |

## Context Budget

If context usage exceeds 65%, write HANDOFF.json (see `pipeline-contracts.md` for schema) before pausing:

```bash
Write `.beads/HANDOFF.json`:
```

```json
{
  "schema_version": 1,
  "phase": "<current phase>",
  "skill": "beo-router",
  "feature": "<epic-id>",
  "feature_name": "<feature-name>",
  "next_action": "<what to do next>",
  "in_flight_beads": ["<bead-ids>"],
  "timestamp": "<iso8601>"
}
```

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
