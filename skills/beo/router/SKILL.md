---
name: beo/router
description: Use when starting a new session, resuming after a handoff, or needing to determine current feature state and next action. The bootstrap and routing skill for the beo pipeline.
---

# Warcraft Router

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

If `br doctor` reports issues, fix them before proceeding.

## Phase 1: State Detection

Determine the current state of work by querying the bead graph.

### Step 1: Check for HANDOFF.json

```bash
cat .beo/HANDOFF.json 2>/dev/null
```

If HANDOFF.json exists, go to **Phase 3: Resume**.

### Step 2: Detect Active Feature

```bash
# List all epics (features)
br list --type epic --json

# Check for in-progress work
br list --type epic -s open --json
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

# List tasks under this epic
br list --type task --json | jq '[.[] | select(.id | startswith("<EPIC_ID>."))]'

# Check graph health
bv --robot-triage --format json

# Check what's actionable
bv --robot-next --format json
br ready --json
br blocked --json
```

### Step 4: Classify Feature State

Use this decision table:

| Condition | State | Route To |
|-----------|-------|----------|
| Epic exists, no tasks, no `approved` label | **exploring** | `beo/exploring` |
| Epic exists, no tasks, has `approved` label | **ready-to-decompose** | `beo/planning` (Phase 4 only) |
| Epic exists, tasks exist, no `approved` label on epic | **planning** | `beo/planning` |
| Epic exists, tasks exist, `approved` label on epic, all tasks open | **ready-to-execute** | `beo/executing` |
| Epic exists, tasks exist, some in_progress/closed | **executing** | `beo/executing` |
| Epic exists, all tasks closed, epic still open | **ready-to-review** | `beo/reviewing` |
| Epic is closed | **completed** | Report status, ask for next work |
| Any tasks have `blocked` or `failed` labels | **blocked** | Report blockers, ask user for decision |

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
| Single file change, well-scoped, <30 min | **instant** | Create task directly, route to `beo/executing` |
| 2-3 files, clear scope, <2 hours | **lightweight** | Route to `beo/planning` (abbreviated) |
| Multi-file, needs research, >2 hours | **standard** | Route to `beo/exploring` |
| Ambiguous, needs clarification | **unclear** | Route to `beo/exploring` |

### Step 3: Route

- **instant**: Create a single task bead immediately:
  ```bash
  br create "<task-name>" -t task --parent <EPIC_ID> -p 1 --json
  br update <TASK_ID> --description "<Background + what to do + verify steps>"
  ```
  Then route to `beo/executing`.

- **lightweight/standard/unclear**: Route to the appropriate skill.

### Promotion Guard

If you classified as **instant** but discover the work is bigger:
- Stop implementation
- Route to `beo/exploring` or `beo/planning`
- The existing task bead becomes input for the plan

## Phase 3: Resume from Handoff

When HANDOFF.json exists:

### Step 1: Read Handoff State

```bash
cat .beo/HANDOFF.json
```

Expected format:
```json
{
  "schema_version": 1,
  "phase": "executing",
  "skill": "beo/executing",
  "feature": "<epic-id>",
  "context_pct": 72,
  "next_action": "Continue executing task <TASK_ID>",
  "beads_in_flight": ["<TASK_ID_1>", "<TASK_ID_2>"],
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
rm .beo/HANDOFF.json
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

If context usage exceeds 65%, write HANDOFF.json before pausing:

```bash
mkdir -p .beo
```

Write `.beo/HANDOFF.json` with the current state (phase, skill, feature, next action, in-flight beads).

## Skill Routing Quick Reference

| User Says | Route To |
|-----------|----------|
| "build X", "add X", "implement X" | Phase 2 → complexity classification → appropriate skill |
| "what's the status?" | Phase 1 → report state |
| "continue", "resume" | Phase 3 (if HANDOFF.json) or Phase 1 |
| "check health", "doctor" | Phase 4 |
| "plan X" | `beo/planning` directly |
| "review" | `beo/reviewing` directly |
| "what should I work on next?" | Phase 1 → `bv --robot-next` → report recommendation |

## Red Flags

- **Starting implementation without state detection** — Always run Phase 1 first
- **Creating a second epic while one is active** — One feature at a time unless user explicitly requests parallel features
- **Skipping HANDOFF.json on resume** — If the file exists, read it
- **Classifying everything as instant** — If there is any doubt about scope, route to exploring
- **Routing to executing before planning** — Unless the feature has an `approved` label and tasks exist, do not skip planning

## Anti-Patterns

| Pattern | Why It's Wrong | Instead |
|---------|---------------|---------|
| `br create` without checking existing epics | Creates duplicate features | Always list epics first |
| Routing based on user's words alone | User may not know current state | Always query bead graph |
| Skipping `br doctor` on first session | Silent corruption goes undetected | Run doctor on bootstrap |
| Hardcoding epic IDs | IDs change between sessions | Always query dynamically |
