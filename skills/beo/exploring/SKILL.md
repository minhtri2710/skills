---
name: beo-exploring
description: >-
  Use before any non-Quick feature work, refactor, behavior change, or
  requirements-shaping conversation where user intent is not yet locked,
  especially when the user knows what they want but has not fully thought
  through edge cases, scope boundaries, or expected behavior. Do not use for
  instant work already routed by beo-router, clear bug-fix root-cause work
  (use beo-debugging), or mid-pipeline resume (use beo-router).
---

<HARD-GATE>
Onboarding — see `../reference/references/shared-hard-gates.md` § Onboarding Check.
</HARD-GATE>

# Beo Exploring

## Overview

Extract decisions.
Turn a partial request into a planning-ready `CONTEXT.md`.

> See `../reference/references/shared-hard-gates.md` § Shared References Convention.

**Core principle:** ask until planning can proceed without guessing.

`CONTEXT.md` is the source of truth for planning, validation, execution, and review.

## Hard Gates

<HARD-GATE>
Ask **one focused question at a time**.
</HARD-GATE>

<GUIDELINE>
Ask about **behavior**, not implementation.
Users decide what should happen; planning decides how to build it.
</GUIDELINE>

<HARD-GATE>
Do not proceed to planning until every material gray area has either:
- a locked decision, or
- an explicit out-of-scope ruling.
</HARD-GATE>

<HARD-GATE>
Do not continue exploration until the user answers the current question.
</HARD-GATE>

<HARD-GATE>
Do not lock a default proposal without explicit user confirmation.
</HARD-GATE>

<HARD-GATE>
Never copy the user's raw request or secrets verbatim into `CONTEXT.md`.
</HARD-GATE>

## Default Exploring Loop

1. read any existing context and prior learnings
2. classify the scope and likely gray areas
3. classify the feature domain (`SEE`, `CALL`, `RUN`, `READ`, or `ORGANIZE`)
4. run a codebase scout: identify likely artifacts, protocols, templates, or entry points, then read 2-3 relevant files to ground gray areas in repo patterns
5. **repeat until all gray areas are resolved:**
   a. ask one focused behavioral question
   b. **wait for the user's response**
   c. annotate gray areas with existing context
   d. lock decisions explicitly as they emerge
6. write a sanitized `CONTEXT.md`
7. self-check planning readiness, then hand off to `beo-planning`

## References (load on demand)

| File | Use for |
| --- | --- |
| `../reference/references/learnings-read-protocol.md` | canonical prior-learnings read flow |
| `../reference/references/artifact-conventions.md#slug-lifecycle` | updating the epic description safely |
| `../reference/references/failure-recovery.md` | state-file, artifact-write, or `br`/`bv` failures during exploration |

## Scope Classification

Classify the feature as **Quick**, **Standard**, or **Deep** and record that classification in the exploring output.

- **Quick** uses the canonical definition in `../reference/references/pipeline-contracts.md`.
- **Standard** is the default path for normal feature work.
- **Deep** applies when the work spans multiple systems or needs extra discovery depth.

Quick work still requires gray-area discovery, must satisfy that canonical definition, and skips self-review.

## Read Existing Context First

Before asking new questions:
- read existing `CONTEXT.md` when present
- inspect the epic description
- determine whether decisions are already locked

If `CONTEXT.md` already contains the needed locked decisions, verify it and continue toward planning.
Do **not** re-ask settled questions on resume.

## Gray-Area Discovery

Find uncertainties that would materially change planning or execution, such as:
- failure behavior
- edge cases and empty states
- permissions and visibility
- migration or compatibility behavior
- latency or performance expectations
- out-of-scope boundaries

Keep questions concrete and answerable.
Each question should be answerable in 1-2 sentences and should change downstream decisions.

Classify the feature domain (`SEE`, `CALL`, `RUN`, `READ`, or `ORGANIZE`) with `references/gray-area-probes.md`. Each round, review the relevant probes and **ask exactly one question**: the highest-value probe for the current state. After the user responds, reassess and ask the next highest-value probe if gaps remain. Never batch probes in one message.

## Default-Proposal Pattern

If the user says "I don't know" or "whatever you think":
1. state the uncertainty plainly
2. propose **one** concrete default
3. explain the behavioral consequence
4. ask for confirmation before locking it

## Decision Rubrics

### What to ask next

- Ask the question whose answer would most change planning shape, execution risk, or user-visible behavior.
- If tied, ask the one that narrows scope before implementation detail.

### When exploring is done

- Stop only when a planner could produce `approach.md` without inventing behavior.
- If only implementation preference remains uncertain, hand off to planning.

## Lock Decisions Explicitly

As answers emerge, assign stable IDs and confirm them.

Example shape:
- `D1`: retry behavior after overnight failure
- `D2`: empty-state behavior for first-time users
- `D3`: permission rule for non-admin access

Do not treat an answer as locked until it has been explicitly confirmed or accepted as the default.

## `CONTEXT.md` Requirements

Write `CONTEXT.md` using `references/context-template.md`.
All 8 sections are required. If a section is empty, write `N/A`.

Preserve the decisions planning must trust, not the original conversation.

## Planning-Readiness Check

Before handoff, confirm:
- every planning-shaping gray area has been resolved or scoped out
- a planner could explain the feature using `CONTEXT.md`
- no unanswered question would change the high-level plan

If any of these fail, keep exploring.

## Self-Review

For **Standard** and **Deep** work, run one fresh-eyes self-review on the `CONTEXT.md` draft before handoff.

Check that:
- all planning-shaping gray areas are resolved or explicitly scoped out
- no locked decisions contradict each other
- D-IDs are assigned consistently
- outstanding questions are split correctly between "Resolve Before Planning" and "Deferred to Planning"

Allow at most one retry. If the draft still fails, flag the unresolved planning-shaping gray areas to the user and ask them to resolve each item or mark it out of scope. Do not offer a "proceed anyway" option.

**Quick** work is exempt from this self-review step.

## Handoff

When complete:
1. write `CONTEXT.md`
2. update `.beads/STATE.json`
3. report how many decisions were locked and what remains out of scope
4. hand off to `beo-planning`

Exploring STATE.json uses the canonical 12-field schema from `../reference/references/state-and-handoff-protocol.md` (see Example F). Set `phase: "exploring"`, `status: "planning-needs-approach"`, `tasks: "none"`, `next: "beo-planning"`, `planning_mode: "unknown"`, and `phase_name` to a human-readable feature summary. Do not create execution beads.

## Context Budget

Follow `../reference/references/shared-hard-gates.md` § Context Budget Protocol. Skill-specific checkpoint items: locked decisions and open questions.

## Red Flags & Anti-Patterns

- if you find fewer than 2 meaningful gray areas for non-trivial work, verify that you have not skipped edge cases or scope boundaries
- do not spend excessive time circling a single unresolved question; lock what is known and mark the rest for planning only when the remaining uncertainty is truly planning-shaped
- do not resume by re-asking already locked decisions; continue from the real gaps in `CONTEXT.md`

Use `references/context-template.md` when creating or updating `CONTEXT.md`.
Use `references/gray-area-probes.md` when an answer is ambiguous or incomplete and you need a targeted follow-up.
