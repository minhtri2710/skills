---
name: beo-validating
description: >-
  Use after planning completes and before any implementation begins. Verifies
  that the current phase contract, story map, and bead graph are structurally
  sound, execution-ready, and aligned with locked decisions. Use for prompts
  like "validate the plan", "is this ready to build?", "check the bead graph",
  "verify execution readiness", or whenever there is doubt about whether the
  current phase is safe to execute.
---

# Beo Validating

## Overview

Validating is the critical gate between planning and execution. No code is written until this skill completes successfully.

**Core principle**: Catch plan failures before they become implementation failures.

This skill treats the **current phase** as a small closed loop -- clear entry state, clear exit state, simple demo story, stories that explain the internal order, and beads that implement those stories. The 8-dimension check (Phase 1) verifies this loop is sound.

If `phase-plan.md` exists, validating still focuses on the **current phase only**. Whole-feature sequencing informs the validator, but current-phase approval does not approve later phases.

## Prerequisites

Load `references/validation-operations.md` for the exact prerequisite checks, planning-aware orientation flow, and learnings-retrieval procedure.

<HARD-GATE>
If tasks don't exist in the bead graph, STOP. Route back to `beo-planning`.
If `phase-contract.md` is missing, STOP. Route back to `beo-planning`.
If `story-map.md` is missing, STOP. Route back to `beo-planning`.
</HARD-GATE>

## Phase 0: Learnings Retrieval + Current-Phase Orientation

Before validating structure:

- check institutional memory for relevant failure patterns
- orient yourself to the current phase
- if `phase-plan.md` exists, confirm how the current phase fits the larger whole plan

Load `references/validation-operations.md` for the exact orientation sequence and summary format.

## Phase 1: Structural Verification

Check the current phase across 8 dimensions. For each dimension, assign PASS or FAIL.

### The 8 Dimensions

| # | Dimension | What to Check | FAIL if... |
|---|-----------|--------------|------------|
| 1 | **Phase contract clarity** | `phase-contract.md` has clear entry state, exit state, demo story, unlocks, and scope | Exit state is vague or aspirational, demo does not prove the phase, phase sounds like a work bucket |
| 2 | **Story coverage and ordering** | `story-map.md` stories have purpose, why-now, contributes-to, unlocks, done-looks-like | A story cannot answer "what does this unlock?", order feels arbitrary, a needed story is missing |
| 3 | **Decision coverage** | Every `CONTEXT.md` decision (D1, D2...) maps to at least one story and bead | A locked decision appears nowhere in the story map, or a story mentions it but no bead implements it |
| 4 | **Dependency correctness** | Story order and bead dependencies agree, graph is acyclic | Story order says one thing but bead dependencies say another, cycles exist, implicit undeclared dependencies |
| 5 | **File scope isolation** | Parallel-ready beads don't silently collide | Two ready beads write the same file, config/schema files have no explicit owner |
| 6 | **Context budget** | Each bead fits in one worker context window | A bead spans multiple stories, requires reading too many large files, tries to implement an entire subsystem |
| 7 | **Verification completeness** | Stories and beads both have explicit done/verify criteria | Story "done" is vague, bead verify steps are not runnable, story completion depends on subjective judgment |
| 8 | **Exit-state completeness and risk alignment** | If all beads complete, the current phase reaches its exit state; HIGH-risk items have spike paths | Bead graph could finish while phase is not demoable, exit state depends on missing work, HIGH-risk items lack spikes |

### Running the Check

Load `references/validation-operations.md` for the exact plan-checker invocation, repair routing, and failure-handling loop.

### Repair Routing by Failure Type

| Failure Type | Route Back To |
|---|---|
| Exit state is vague or current-phase meaning is weak | `phase-contract.md` |
| Story order or story coverage is weak | `story-map.md` |
| Locked decisions are not mapped into implementation | `approach.md`, `plan.md`, stories, and bead descriptions |
| Dependency graph is inconsistent or cyclic | bead dependency wiring |
| Parallel beads silently collide on files | bead ownership, bead split, or story decomposition |
| Bead scope exceeds one worker context | bead decomposition |
| Verification is vague or subjective | story and bead verification criteria |
| HIGH-risk work has no proof path | spike design or broader planning revision |
| Current phase no longer fits the larger feature sequence | `phase-plan.md`, `approach.md`, and current-phase artifacts |

## Phase 2: Graph Health

Use `bv` to analyze the bead graph for structural issues.

Load `references/validation-operations.md` for the exact commands, interpretation table, deduplication check, story-to-bead coherence check, and bead-description verification procedure.

<HARD-GATE>
FAIL the plan if any bead has an empty or underspecified description. This is a structural verification failure, not an optional quality note. Route back to `beo-planning` to complete the bead specs.
</HARD-GATE>

## Phase 3: Spike Execution (HIGH-Risk Only)

For each HIGH-risk task, evaluate whether a spike is needed.

A spike is needed when the approach is unproven, depends on external systems, has hard performance requirements, or otherwise relies on hope.

Load `references/validation-operations.md` for the exact create/record/result-handling sequence.

<HARD-GATE>
A spike NO result means the current phase plan is invalid. Do not proceed to approval.
</HARD-GATE>

## Phase 4: Fresh-Eyes Review (Optional)

For **deep** complexity features or features with 5+ tasks, load `references/validation-operations.md` for the exact fresh-eyes review procedure.

## Phase 5: Exit-State Readiness Review

This is the human-readable readiness check before approval.

Ask these questions explicitly:

1. If all stories reach "Done Looks Like", does the current phase exit state hold?
2. If all beads close successfully, will all stories actually be done?
3. Is the current phase demo story now credible?
4. If `phase-plan.md` exists, does this current phase still make sense inside the larger whole plan?

If any answer is "no" or "not sure", do not approve execution. Route back:

| Problem | Route To |
|---------|----------|
| Current-phase meaning / exit state problem | Revise `phase-contract.md` |
| Story decomposition problem | Revise `story-map.md` |
| Implementation granularity problem | Revise bead descriptions |
| Architecture / risk problem | Revise `approach.md`, `plan.md`, and possibly route to `beo-planning` |
| Whole-feature sequencing problem | Revise `phase-plan.md` and current-phase artifacts |

## Phase 6: Approval Gate

<HARD-GATE>
Use the canonical validation approval rule from `../reference/references/approval-gates.md`: user approval is required before any code is written. This is non-negotiable.
</HARD-GATE>

Load `references/validation-operations.md` for the exact approval summary, approval commands, rejection handling, and route-back rules.

## Lightweight Mode

Load `references/validation-operations.md` for the lightweight-validation shortcut, context-budget checkpoint procedure, and canonical handoff flow.

## Context Budget

If context usage exceeds 65%, use the checkpoint procedure from `references/validation-operations.md`.

## Handoff

After user approves, use `references/validation-operations.md` to determine execution mode and write the canonical `STATE.md` handoff.

Announce:
```text
Current phase approved. <N> tasks ready for execution.
Execution mode: <single-worker | parallel (swarming)>
Load <beo-executing | beo-swarming> to begin implementation.
```

If `planning_mode = multi-phase`, current-phase approval does not imply feature completion. Later phases remain deferred until routed back through `beo-planning`.

See `references/validating-guardrails.md` for red flags and anti-patterns.
