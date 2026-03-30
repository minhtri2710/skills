---
name: beo-router
description: Use when starting a new session, resuming after a handoff, or needing to determine current feature state and next action. The bootstrap and routing skill for the beo pipeline.
---

# Beo Router

## Overview

The router is the entry point for every beo session. It bootstraps the workspace, detects current state, and routes to the correct pipeline skill.

**Core principle**: Always know where you are before deciding where to go.

## When to Use

- Starting a new coding session
- User says "build", "add", "change", "implement", "fix", or any feature request
- Resuming after a context handoff (HANDOFF.json exists)
- Checking overall project health
- Unsure which pipeline skill to load next

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
# Check knowledge search availability
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
# List all epics (features)
br list --type epic --json

# Check for in-progress work (search all statuses, not just open)
br list --type epic --json
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

# List tasks under this epic (canonical enumeration — see pipeline-contracts.md)
br dep list <EPIC_ID> --direction up --type parent-child --json

# Check graph health
bv --robot-triage --format json

# Check what's actionable
bv --robot-next --format json
br ready --json
br blocked --json
```

### Step 4: Classify Feature State

Use the canonical state routing table from `beo-reference` → `references/pipeline-contracts.md`. Evaluate **top-to-bottom, first match wins**.

| # | Condition | State | Route To |
|---|-----------|-------|----------|
| 1 | Any tasks have `blocked` or `failed` labels, debugging not yet attempted | **needs-debugging** | `beo-debugging` |
| 2 | Any tasks have `blocked` or `failed` labels, debugging attempted | **blocked** | Report blockers, ask user for decision |
| 3 | Epic exists, tasks exist, `approved` label on epic, all tasks open, ≤2 independent tasks | **ready-to-execute** | `beo-executing` |
| 4 | Epic exists, tasks exist, `approved` label on epic, all tasks open, 3+ independent tasks | **ready-to-swarm** | `beo-swarming` |
| 5 | Epic exists, tasks exist, some in_progress/closed (and no blocked/failed) | **executing** | `beo-executing` |
| 6 | Epic exists, tasks exist, no `approved` label, plan.md exists | **ready-to-validate** | `beo-validating` |
| 7 | Epic exists, tasks exist, no `approved` label, no plan.md | **planning** | `beo-planning` |
| 8 | Epic exists, no tasks, no `approved` label | **exploring** | `beo-exploring` |
| 9 | Epic exists, all tasks closed, epic still open | **ready-to-review** | `beo-reviewing` |
| 10 | Any tasks have `partial` or `cancelled` labels, epic still open | **partial-completion** | Report status, ask user for decision |
| 11 | Epic is closed | **completed** | Report status, ask for next work |
| 12 | All tasks closed, epic closed, no learnings file | **learnings-pending** | `beo-compounding` |
| 13 | Learnings stale, user requests consolidation | **consolidation-due** | `beo-dream` |
| 14 | Skill creation or editing requested | **meta-skill** | `beo-writing-skills` |

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

### Step 2: Classify Request Complexity

| Signal | Classification | Path |
|--------|---------------|------|
| Single file change, well-scoped, <30 min | **instant** | Create task directly, route to `beo-executing` |
| 2-3 files, clear scope, <2 hours | **lightweight** | Route to `beo-planning` (abbreviated) |
| Multi-file, needs research, >2 hours | **standard** | Route to `beo-exploring` |
| Ambiguous, needs clarification | **unclear** | Route to `beo-exploring` |
| Error, blocker, failure symptoms | **debug** | Route to `beo-debugging` |

### Step 3: Route

- **instant**: Create a single task bead and mark epic approved:
  ```bash
  br create "<task-name>" -t task --parent <EPIC_ID> -p 1 --json
  br update <TASK_ID> --description "<Background + what to do + verify steps>"
  br label add <EPIC_ID> -l approved
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

After successfully resuming, delete the handoff file:
```bash
rm .beads/HANDOFF.json
```

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
| Tasks in_progress >4h with no commits | **MEDIUM** | May be abandoned — check with user |
| Epic with no tasks and no plan | **LOW** | Stale feature — suggest cleanup or activation |
| Closed tasks with open dependencies | **HIGH** | Inconsistent state — investigate |

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

## Red Flags

- **Starting implementation without state detection** — Always run Phase 1 first
- **Creating a second epic while one is active** — One feature at a time unless user explicitly requests parallel features
- **Skipping HANDOFF.json on resume** — If the file exists, read it
- **Classifying everything as instant** — If there is any doubt about scope, route to exploring
- **Routing to executing before planning** — Unless the feature has an `approved` label and tasks exist, do not skip planning
- **Routing to swarming without validated plan** — Swarming requires the same `approved` label as executing
- **Skipping compounding after review** — Learnings capture is part of the pipeline, not optional
- **Debugging without checking critical-patterns.md first** — Always check known patterns before investigating

## Anti-Patterns

| Pattern | Why It's Wrong | Instead |
|---------|---------------|---------|
| `br create` without checking existing epics | Creates duplicate features | Always list epics first |
| Routing based on user's words alone | User may not know current state | Always query bead graph |
| Skipping `br doctor` on first session | Silent corruption goes undetected | Run doctor on bootstrap |
| Hardcoding epic IDs | IDs change between sessions | Always query dynamically |
| Routing to executing instead of swarming for parallel work | Executing is single-worker; swarming orchestrates multiple | Check task count and independence before choosing |
| Using dream for one-off fixes | Dream consolidates learnings; debugging fixes issues | Route to `beo-debugging` for errors |
