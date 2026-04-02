# Router Operations

Detailed operational playbook for `beo-router`.

Load this file when you need exact bootstrap steps, new-feature creation details, instant-path scaffolding, resume validation, planning-aware routing, or doctor-mode commands.

## Table of Contents

- [1. Workspace Bootstrap](#1-workspace-bootstrap)
- [2. New Feature Creation](#2-new-feature-creation)
- [3. Instant Path Scaffold](#3-instant-path-scaffold)
- [4. Artifact Inspection Order](#4-artifact-inspection-order)
- [5. Planning-Aware Routing Rules](#5-planning-aware-routing-rules)
- [6. Resume From Handoff](#6-resume-from-handoff)
- [7. Doctor Mode](#7-doctor-mode)

## 1. Workspace Bootstrap

Run once per session when `.beads/` is missing or unhealthy.

```bash
# Check if beads workspace exists (use your file reading tool to read .beads/ directory)

# If missing, initialize
br init

# Verify br is working
br --version

# Check workspace health
br doctor
```

Optional knowledge-search availability check:

```bash
qmd status 2>/dev/null
```

If `br doctor` reports issues, fix them before proceeding.

## 2. New Feature Creation

### Create the Epic

```bash
br create "<feature-name>" -t epic -p 1 --json
```

Save the returned epic ID for all downstream operations.

### Store the Immutable Slug

Derive the `feature_slug` from the epic title using `../../reference/references/slug-protocol.md`. Store it in the epic description with the canonical slug-first shape.

## 3. Instant Path Scaffold

Use for **instant** work only: single file change, well-scoped, <30 minutes.

### Create the Task

Use the shared Markdown bead templates from `../../reference/references/bead-description-templates.md`.

```bash
br create "<task-name>" -t task --parent <EPIC_ID> -p 1 --json
br update <TASK_ID> --description "<markdown task spec: background + what to do + verify steps>"
```

After scaffolding the minimal artifacts, route to `beo-validating`. Do not set the `approved` label here; only `beo-validating` grants approval.

### Create Minimal Artifacts

```bash
mkdir -p .beads/artifacts/<feature_slug>
```

Write these minimal stubs with file editing tools:

#### CONTEXT.md

```markdown
# Feature: <name>

## Request
<Sanitized summary of the request in your own words. Redact or omit secrets, credentials, tokens, cookies, connection strings, private URLs, and long pasted payloads/logs. Use placeholders such as [REDACTED_SECRET] when needed.>

## Locked Decisions
Instant-path: no exploration needed.

## Scope Classification
- Complexity: instant
- Domains: <inferred>
- Estimated blast radius: 1 file
```

#### approach.md

```markdown
# Approach: <name>

## Problem Shape
Instant-path: single bounded change.

## Recommended Approach
Implement the smallest change that satisfies the request while preserving existing patterns.

## Planning Mode Decision
- Mode: single-phase
```

#### plan.md

```markdown
# Plan: <name>

## Approach
Single-task instant implementation.

## Tasks
### 1. <task-name>
See bead description for spec.
```

#### phase-contract.md

```markdown
# Phase Contract: <name>

## Exit State
- Feature works as described in request.

## Demo Story
Instant-path: single-task feature, no deeper phase structure needed.
```

#### story-map.md

```markdown
# Story Map: <name>

## Story Table

| Story | Purpose | Done Looks Like |
|-------|---------|-----------------|
| Story 1: Implement | Single-task implementation | Task complete and verified |

## Story-To-Bead Mapping

| Story | Beads |
|-------|-------|
| Story 1 | <TASK_ID> |
```

### Promotion Guard

If the work grows beyond instant scope:
- stop implementation
- route to `beo-exploring` or `beo-planning`
- treat the existing instant task bead as planning input

## 4. Artifact Inspection Order

When assessing an active feature, inspect artifacts in this order:

1. `CONTEXT.md`
2. `discovery.md`
3. `approach.md`
4. `phase-plan.md` *(if present)*
5. `phase-contract.md`
6. `story-map.md`

Interpretation rules:

- if `phase-plan.md` exists, the feature is potentially multi-phase
- if `phase-plan.md` does not exist, the feature is usually single-phase unless other evidence contradicts that assumption
- `phase-contract.md` and `story-map.md` always describe the **current phase** only

## 5. Planning-Aware Routing Rules

Use these rules when the planning model is relevant.

### Rule A — Context exists but planning artifacts do not

If `CONTEXT.md` exists but `approach.md` does not:
- route to `beo-planning`

### Rule B — Approach exists but current-phase artifacts are missing

If `approach.md` exists and either `phase-contract.md` or `story-map.md` is missing:
- route to `beo-planning`

### Rule C — Multi-phase sequencing exists

If `phase-plan.md` exists:
- treat the feature as multi-phase unless the file is clearly obsolete or contradicted by current state
- do not assume current-phase completion means whole-feature completion

### Rule D — Current phase complete, later phases remain

If all current-phase beads are closed, `phase-plan.md` exists, and later phases remain:
- route to `beo-planning`
- next action = prepare the next phase

Pseudo-logic:

```text
if phase_plan exists and current phase complete and later phases remain:
  route = beo-planning
else if no later phases remain and implementation complete:
  route = beo-reviewing
```

### Rule E — Final execution scope complete

If execution is complete and no later phases remain:
- route to `beo-reviewing`

## 6. Resume From Handoff

### Read the Handoff

Read `.beads/HANDOFF.json` with your file reading tool.

Use the canonical schema from `../../reference/references/state-and-handoff-protocol.md`.

### Read planning-aware fields when present

If present, read and trust these fields unless live artifacts clearly contradict them:

- `planning_mode`
- `has_phase_plan`
- `current_phase`
- `total_phases`
- `phase_name`
- `artifacts`
- `mode`

### Verify It Is Still Valid

```bash
# Check that the epic still exists and is open
br show <feature_epic_id> --json

# Check task states haven't changed externally
br list --type task --json
```

Also re-check the artifact set in the canonical inspection order.

If `has_phase_plan = true`, verify that `phase-plan.md` still exists.

If `mode = "go"`, resume within go-mode rather than normal routing. Preserve the saved `skill` and `next_action`, and continue using go-mode semantics at the next human gate unless live state clearly invalidates the checkpoint.

### Clean Up Only After Fresh Checkpoint

After the resumed skill writes a fresh `STATE.md`, clean up `HANDOFF.json` according to `../../reference/references/state-and-handoff-protocol.md`.

## 7. Doctor Mode

Use when asked to inspect project health or diagnose workflow issues.

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

In addition to graph health, report planning shape when relevant:

- whether `approach.md` exists
- whether `phase-plan.md` exists
- whether current-phase artifacts exist
- whether the feature appears single-phase or multi-phase

### Diagnostic Table

| Finding | Severity | Action |
|---------|----------|--------|
| Dependency cycles | **HIGH** | Report exact cycle, ask user to break it |
| Tasks blocked >24h | **MEDIUM** | Report blockers, suggest resolution |
| Tasks in_progress >4h with no commits | **MEDIUM** | May be abandoned; check with user |
| Epic with no tasks and no plan | **LOW** | Stale feature; suggest cleanup or activation |
| Closed tasks with open dependencies | **HIGH** | Inconsistent state; investigate |
| `phase-plan.md` exists but no current-phase artifacts | **MEDIUM** | Route back to planning |
| Current phase complete but later phases remain | **MEDIUM** | Route back to planning for next phase prep |
