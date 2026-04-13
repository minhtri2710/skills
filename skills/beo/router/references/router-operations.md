# Router Operations

Detailed operational playbook for `beo-router`.

Load this file when you need exact bootstrap steps, new-feature creation details, quick-path scaffolding, resume validation, planning-aware routing, or doctor-mode commands.

## Intent Short-Circuit Rule

Before doing full feature-state routing, check whether the user's explicit request already selects a meta-path.
Examples:
- creating or editing a beo skill -> `beo-writing-skills`
- root-cause analysis of blocked/failing work -> `beo-debugging`
- explicit learnings consolidation request -> `beo-dream`

If explicit user intent clearly selects one of these paths, honor it unless live state proves the request is impossible, stale, or aimed at the wrong feature.

Conversational phrasing is **not** a valid short-circuit. Requests like "research X with me", "let's explore X", or "help me think through X" imply non-trivial work and must route through the state table normally — they are feature intake, not freeform chat. Only simple lookups, quick explanations, and single-fact questions may be answered directly.

## Table of Contents

- [1. Workspace Bootstrap](#1-workspace-bootstrap)
- [2. New Feature Creation](#2-new-feature-creation)
- [3. Quick Path Scaffold](#3-quick-path-scaffold)
- [4. Artifact Inspection Order](#4-artifact-inspection-order)
- [5. Planning-Aware Routing Rules](#5-planning-aware-routing-rules)
- [6. Resume From Handoff](#6-resume-from-handoff)
- [7. Doctor Mode](#7-doctor-mode)
- [8. STATE.json on Handoff](#8-statejson-on-handoff)

## 1. Workspace Bootstrap

Run once per session when onboarding is missing or stale, or when `.beads/` is missing or unhealthy.

Before normal bootstrap, check `.beads/onboarding.json`.
If it is missing, unreadable, or stale, stop and route to `beo-using-beo`.
Only continue deeper workspace interpretation after onboarding is current.

If `.beads/beo_status.mjs` exists, run `node .beads/beo_status.mjs --json` as a read-only quick scout before reading deeper state files individually.

Optional knowledge-search availability check:

```bash
qmd status 2>/dev/null
```

If workspace repair is needed, use the doctor-mode commands in section 7 rather than treating bootstrap repair as normal routing work.

## 2. New Feature Creation

### Create the Epic

```bash
br create "<feature-name>" -t epic -p 1 --json
```

Save the returned epic ID for all downstream operations.

### Debug Intake Bootstrap

If the request matches the `new-debug-intake` route from the state table, create a minimal debug epic and one debug task bead before routing to `beo-debugging`.

```bash
br create "Debug: <issue summary>" -t epic -p 1 --json
br create "Investigate: <issue summary>" -t task --parent <EPIC_ID> -p 1 --json
```

This gives `beo-debugging` the epic/task context it needs for fix beads, debug labels, and comments.

### Store the Immutable Slug

Derive the `feature_slug` from the epic title using `../../reference/references/slug-protocol.md`. Store it in the epic description with the canonical slug-first shape.

## 3. Quick Path Scaffold

Use for **quick** work only: single file change, well-scoped, <30 minutes.
Quick uses the stricter intake bar here. When work qualifies, the router may use the quick path only at intake. Once an epic already exists or the scope expands beyond that strict quick bar, fall back to the normal Quick-aware pipeline.

> **Ownership exception:** The quick path creates minimal stubs for artifacts that normally belong to `beo-exploring` (CONTEXT.md) and `beo-planning` (approach.md, plan.md, phase-contract.md, story-map.md). This is an intentional shortcut — these stubs are not full-depth artifacts but placeholder scaffolds that let quick work skip directly to validation. If the work outgrows quick scope, the promotion guard below routes to the normal pipeline owners.

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
# CONTEXT Template: <name>

## Feature Boundary

- Scope: <one-sentence statement of what this feature changes>
- Domain Type: <SEE | CALL | RUN | READ | ORGANIZE>

## Locked Decisions

| D-ID | Decision | Rationale | Source |
|------|----------|-----------|--------|
| D1 | Quick-path: no exploration needed | Single bounded change, ≤1 file | agent default |

### Agent's Discretion

- Implementation details follow existing codebase patterns

## Specific Ideas & References

- N/A

## Existing Code Context

- Reusable assets: <inferred from request>
- Established patterns: <inferred from request>
- Integration points: <inferred from request>

## Canonical References

- N/A

## Outstanding Questions

### Resolve Before Planning

- N/A

### Deferred to Planning

- N/A

## Deferred Ideas

- N/A

## Handoff Note

- `beo-planning` reads: Feature Boundary, Locked Decisions
- `beo-validating` reads: Locked Decisions
- `beo-executing` reads: Locked Decisions, Existing Code Context
- `beo-reviewing` reads: Feature Boundary
```

#### approach.md

```markdown
# Approach: <name>

## Problem Shape
Quick-path: single bounded change.

## Recommended Approach
Implement the smallest change that satisfies the request while preserving existing patterns.

## Planning Mode Decision
- Mode: single-phase
```

#### plan.md

```markdown
# Plan: <name>

## Approach
Single-task quick implementation.

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
Quick-path: single-task feature, no deeper phase structure needed.
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

If the work grows beyond quick scope:
- stop implementation
- route to `beo-exploring` or `beo-planning`
- treat the existing quick task bead as planning input

> **Hard gate**: After quick-path promotion, the stub CONTEXT.md and any placeholder artifacts MUST be treated as incomplete drafts. The exploring or planning skill must re-derive them from scratch — never treat promoted stubs as validated artifacts.

## 4. Artifact Inspection Order

When assessing an active feature, inspect artifacts in this order:

1. `CONTEXT.md`
2. `discovery.md`
3. `approach.md`
4. `plan.md`
5. `phase-plan.md` *(if present)*
6. `phase-contract.md`
7. `story-map.md`

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

Before trusting the handoff, confirm `.beads/onboarding.json` still exists and is current.
If onboarding is missing or stale, route to `beo-using-beo` before resuming the saved skill.

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
br dep list <feature_epic_id> --direction up --type parent-child --json
```

Also re-check the artifact set in the canonical inspection order.

If `has_phase_plan = true`, verify that `phase-plan.md` still exists.

If `mode = "go"`, resume within go-mode rather than normal routing. Preserve the saved `skill` and `next_action`, and continue using go-mode semantics at the next human gate unless live state clearly invalidates the checkpoint.

### Clean Up Only After Fresh Checkpoint

After the resumed skill writes a fresh `STATE.json`, clean up `HANDOFF.json` according to `../../reference/references/state-and-handoff-protocol.md`.

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

## 8. STATE.json on Handoff

After classifying the state and before loading the next skill, write `.beads/STATE.json` using the canonical format from `../../reference/references/state-and-handoff-protocol.md`.

Include all 12 canonical fields:
- `schema_version`: always `1`
- `feature`: epic ID
- `feature_slug`: the immutable feature slug
- `phase`: skill that wrote this state (bare name, no `beo-` prefix)
- `status`: canonical state from the routing table
- `tasks`: summary of current task status
- `next`: the next skill to load
- `planning_mode`: `single-phase`, `multi-phase`, or `unknown` (pre-planning only)
- `has_phase_plan`: `true` if `phase-plan.md` exists, otherwise `false`
- `current_phase`: current phase number (use `1` for single-phase)
- `total_phases`: total phase count (use `1` for single-phase)
- `phase_name`: human-readable current phase name

This ensures every skill transition has a readable state record, not just handoff-from-checkpoint scenarios.
