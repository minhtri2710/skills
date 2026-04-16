# Router Operations

Detailed operational playbook for `beo-route`.

Load this file when you need exact bootstrap steps, new-feature creation details, quick-path scaffolding, resume validation, planning-aware routing, or doctor-mode commands.

> **Intake scaffolding authorization:** The quick-path bootstrap steps in this file are a narrow exception to route's NO-IMPLEMENTATION gate. They are authorized only as intake scaffolding for new work: creating the epic/task structure, artifact directory, and minimal draft/stub artifacts that downstream skills will complete or overwrite.

## Intent Short-Circuit Rule

Before doing full feature-state routing, check whether the user's explicit request already selects a meta-path.
Examples:
- creating or editing a beo skill -> `beo-author`
- root-cause analysis of blocked/failing work -> `beo-debug`
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
If it is missing, unreadable, or stale, stop and route to `beo-onboard`.
Only continue deeper workspace interpretation after onboarding is current.

If `.beads/beo_status.mjs` exists, run `node .beads/beo_status.mjs --json` as a read-only quick scout before reading deeper state files individually.

Optional knowledge-search availability check:

```bash
qmd status 2>/dev/null
```

If workspace repair is needed, use the doctor-mode commands in section 7 rather than treating bootstrap repair as normal routing work.

## 2. New Feature Creation

This section covers intake scaffolding for brand-new features, not general artifact creation during normal routing.

### Create the Epic

```bash
br create "<feature-name>" -t epic -p 1 --json
```

Save the returned epic ID for all downstream operations.

### Debug Intake Bootstrap

If the request matches the `new-debug-intake` route from the state table, create a minimal debug epic and one debug task bead before routing to `beo-debug`.

```bash
br create "Debug: <issue summary>" -t epic -p 1 --json
br create "Investigate: <issue summary>" -t task --parent <EPIC_ID> -p 1 --json
```

This gives `beo-debug` the epic/task context it needs for fix beads, debug labels, and comments.

### Store the Immutable Slug

Derive the `feature_slug` from the epic title using `beo-reference` → `references/artifact-conventions.md#slug-lifecycle`. Store it in the epic description with the canonical slug-first shape.

## 3. Quick Path Scaffold

Use for **quick** work only: single file change, well-scoped, <30 minutes.
Quick uses the stricter intake bar here. When work qualifies, the router may use the quick path only at intake. Once an epic already exists or the scope expands beyond that strict quick bar, fall back to the normal Quick-aware pipeline.

> **Ownership exception:** The quick path creates minimal intake scaffolds for artifacts that normally belong to `beo-explore` (CONTEXT.md) and `beo-plan` (approach.md, plan.md, phase-contract.md, story-map.md). This is an intentional shortcut — these files are draft/stub placeholders, not full-depth artifacts, and they exist only to let quick work skip directly to validation. If the work outgrows quick scope, the promotion guard below routes to the normal pipeline owners, which must complete or overwrite these drafts.

### Create the Task

Use the shared Markdown bead templates from `beo-reference` → `references/bead-description-templates.md`.

```bash
br create "<task-name>" -t task --parent <EPIC_ID> -p 1 --json
br update <TASK_ID> --description "<Markdown content that follows the shared bead template>"
```

After scaffolding the minimal draft artifacts, route to `beo-validate`. Do not set the `approved` label here; only `beo-validate` grants approval.

### Create Minimal Draft Artifacts

```bash
mkdir -p .beads/artifacts/<feature_slug>
```

Write these minimal draft/stub files with file editing tools. Each file should remain obviously incomplete so downstream skills can complete or overwrite it as needed.

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

## Existing Code Context

- Reusable assets: <inferred from request>
- Established patterns: <inferred from request>
- Integration points: <inferred from request>

_Sections omitted for quick-path stub: Specific Ideas, Canonical References, Outstanding Questions, Deferred Ideas — all N/A._

## Handoff Note

- `beo-plan` reads: Feature Boundary, Locked Decisions
- `beo-validate` reads: Locked Decisions
- `beo-execute` reads: Locked Decisions, Existing Code Context
- `beo-review` reads: Feature Boundary
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
- route to `beo-explore` or `beo-plan`
- treat the existing quick task bead as planning input

> **Hard gate**: After quick-path promotion, the stub CONTEXT.md and any placeholder artifacts MUST be treated as incomplete drafts. The exploring or planning skill must re-derive them from scratch or overwrite them as needed — never treat promoted stubs as validated artifacts.

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

| Rule | Condition | Route / Action |
|------|-----------|----------------|
| A | CONTEXT.md exists, no approach.md | → beo-plan |
| B | approach.md exists, missing phase-contract.md or story-map.md | → beo-plan |
| C | phase-plan.md exists | Treat as multi-phase unless clearly obsolete; current-phase completion ≠ whole-feature completion |
| D | All current-phase beads closed + phase-plan.md + later phases remain | → beo-plan (prepare next phase) |
| E | Execution complete, no later phases | → beo-review |

```text
if phase_plan exists and current phase complete and later phases remain:
  route = beo-plan
else if no later phases remain and implementation complete:
  route = beo-review
```

## 6. Resume From Handoff

### Read the Handoff

Read `.beads/HANDOFF.json` with your file reading tool.

Use the canonical schema from `beo-reference` → `references/state-and-handoff-protocol.md`.

Before trusting the handoff, confirm `.beads/onboarding.json` still exists and is current.
If onboarding is missing or stale, route to `beo-onboard` before resuming the saved skill.

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

After the resumed skill writes a fresh `STATE.json`, clean up `HANDOFF.json` according to `beo-reference` → `references/state-and-handoff-protocol.md`.

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

After classifying the state and before loading the next skill, write `.beads/STATE.json` using the complete canonical schema from `beo-reference` → `references/state-and-handoff-protocol.md` § Canonical STATE.json Schema.

All 12 required fields must be present: the 7 base fields (`schema_version`, `phase`, `status`, `feature`, `feature_slug`, `tasks`, `next`) plus the 5 planning-aware fields (`planning_mode`, `has_phase_plan`, `current_phase`, `total_phases`, `phase_name`).

This ensures every skill transition has a readable state record, not just handoff-from-checkpoint scenarios.
