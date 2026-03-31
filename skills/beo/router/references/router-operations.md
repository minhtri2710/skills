# Router Operations

Detailed operational playbook for `beo-router`. Load this file when you need exact bootstrap steps, new-feature creation details, instant-path scaffolding, resume validation, or doctor-mode commands.

## Table of Contents

- [1. Workspace Bootstrap](#1-workspace-bootstrap)
- [2. New Feature Creation](#2-new-feature-creation)
- [3. Instant Path Scaffold](#3-instant-path-scaffold)
- [4. Resume From Handoff](#4-resume-from-handoff)
- [5. Doctor Mode](#5-doctor-mode)

## 1. Workspace Bootstrap

Run once per session when `.beads/` is missing or unhealthy.

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
br label add <EPIC_ID> -l approved
```

### Create Minimal Artifacts

```bash
mkdir -p .beads/artifacts/<feature-name>
```

Write these minimal stubs with file editing tools:

#### CONTEXT.md

```markdown
# Feature: <name>

## Request
<user request>

## Locked Decisions
Instant-path: no exploration needed.

## Scope Classification
- Complexity: instant
- Domains: <inferred>
- Estimated blast radius: 1 file
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

## 4. Exit State
- Feature works as described in request.

## 5. Demo Story
Instant-path: single-task feature, no stories needed.
```

#### story-map.md

```markdown
# Story Map: <name>

## 2. Story Table

| Story | Purpose | Done Looks Like |
|-------|---------|-----------------|
| Story 1: Implement | Single-task implementation | Task complete and verified |

## 5. Story-To-Bead Mapping

| Story | Beads |
|-------|-------|
| Story 1 | <TASK_ID> |
```

### Promotion Guard

If the work grows beyond instant scope:
- stop implementation
- route to `beo-exploring` or `beo-planning`
- treat the existing instant task bead as planning input

## 4. Resume From Handoff

### Read the Handoff

```bash
cat .beads/HANDOFF.json
```

Use the canonical schema from `../../reference/references/state-and-handoff-protocol.md`.

### Verify It Is Still Valid

```bash
# Check that the epic still exists and is open
br show <feature_epic_id> --json

# Check task states haven't changed externally
br list --type task --json
```

### Clean Up Only After Fresh Checkpoint

After the resumed skill writes a fresh `STATE.md`, clean up `HANDOFF.json` according to `../../reference/references/state-and-handoff-protocol.md`.

## 5. Doctor Mode

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

### Diagnostic Table

| Finding | Severity | Action |
|---------|----------|--------|
| Dependency cycles | **HIGH** | Report exact cycle, ask user to break it |
| Tasks blocked >24h | **MEDIUM** | Report blockers, suggest resolution |
| Tasks in_progress >4h with no commits | **MEDIUM** | May be abandoned; check with user |
| Epic with no tasks and no plan | **LOW** | Stale feature; suggest cleanup or activation |
| Closed tasks with open dependencies | **HIGH** | Inconsistent state; investigate |
