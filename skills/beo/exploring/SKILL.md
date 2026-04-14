---
name: beo-exploring
description: >-
  Use before any non-instant feature work, refactor, behavior change, or
  requirements-shaping conversation where user intent is not yet locked,
  especially when the user knows what they want but has not fully thought
  through edge cases, scope boundaries, or expected behavior. Do not use for
  instant work already routed by beo-router, clear bug-fix root-cause work
  (use beo-debugging), or mid-pipeline resume (use beo-router).
---

<HARD-GATE>
If `.beads/onboarding.json` is missing or stale, stop and load `beo-using-beo` before continuing.
</HARD-GATE>

# Beo Exploring

## Overview

Exploring is the decision-extraction phase.
Use it to turn a partially formed request into a planning-usable `CONTEXT.md`.

> **Shared references** — this skill references specific `beo-reference` docs by path. Do not co-load the full `beo-reference` skill; read individual reference docs as needed.

**Core principle:** ask until planning can proceed without guessing.

`CONTEXT.md` becomes the source of truth for downstream planning, validation, execution, and review.

## Hard Gates

<HARD-GATE>
Ask **one focused question at a time**.
Do not batch multiple exploration questions into one message.
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
If the user has not responded, wait. Do not infer answers from silence or prior context.
</HARD-GATE>

<HARD-GATE>
Do not lock a default proposal without explicit user confirmation.
"I'll assume X unless you object" is not confirmation — the user must actively accept or reject.
</HARD-GATE>

<HARD-GATE>
Never copy the user's raw request or secrets verbatim into `CONTEXT.md`.
Sanitize the request summary, redact or omit secrets, and use stable placeholders such as `[REDACTED_API_KEY]` when sensitive literals matter for implementation.
</HARD-GATE>

## Default Exploring Loop

1. read any existing context and prior learnings
2. classify the scope and likely gray areas
3. classify the feature domain (`SEE`, `CALL`, `RUN`, `READ`, or `ORGANIZE`)
4. run a codebase scout: use that domain classification to identify likely artifacts, protocols, templates, or entry points, then read 2-3 relevant files to ground gray areas in existing repo patterns
5. **repeat until all gray areas are resolved:**
   a. ask one focused behavioral question
   b. **wait for the user's response** — do not continue until the user answers
   c. annotate gray areas with existing context when available
   d. lock decisions explicitly as they emerge
6. write a sanitized `CONTEXT.md`
7. self-check for planning readiness, then hand off to `beo-planning`

Use `../reference/references/learnings-read-protocol.md` when you need the canonical prior-learnings read flow.
Use `../reference/references/slug-protocol.md` when updating the epic description safely.

## Scope Classification

Classify the feature as **Quick**, **Standard**, or **Deep** and record that classification in the exploring output.

- **Quick** uses the canonical definition in `../reference/references/pipeline-contracts.md`.
- **Standard** is the default path for normal feature work.
- **Deep** applies when the work spans multiple systems or needs extra discovery depth.

Quick work still needs gray-area discovery, but it must still satisfy the canonical Quick definition from `../reference/references/pipeline-contracts.md` and it skips self-review.

## Read Existing Context First

Before asking new questions:
- read existing `CONTEXT.md` when present
- inspect the epic description
- determine whether decisions are already locked

If `CONTEXT.md` already contains the needed locked decisions, verify it and continue toward planning.
Do **not** re-ask settled questions just because the feature is being resumed.

## Gray-Area Discovery

Look for uncertainties that would materially change planning or execution, such as:
- failure behavior
- edge cases and empty states
- permissions and visibility
- migration or compatibility behavior
- latency or performance expectations
- out-of-scope boundaries

Keep the exploration concrete and answerable.
A good exploration question should be answerable in 1-2 sentences and should change downstream decisions.

Classify the feature domain (`SEE`, `CALL`, `RUN`, `READ`, or `ORGANIZE`) using the categories in `references/gray-area-probes.md`. Each round, review the candidate probes for the relevant category and **ask exactly one question** — the single most valuable probe for the current state of the conversation. After the user responds, reassess and ask the next most valuable probe if gaps remain. Never batch multiple probes into a single message.

## Default-Proposal Pattern

If the user says "I don't know" or "whatever you think":
1. state the uncertainty plainly
2. propose **one** concrete default
3. explain the consequence in behavioral terms
4. ask for confirmation before locking it

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

The goal is not to preserve the original conversation.
The goal is to preserve the decisions that planning must trust.

## Planning-Readiness Check

Before handoff, confirm all of these are true:
- every material gray area has been resolved or scoped out
- a planner could explain the feature using `CONTEXT.md`
- no unanswered question would change the high-level plan

If any of these fail, keep exploring.

## Self-Review

For **Standard** and **Deep** work, run one fresh-eyes self-review pass on the `CONTEXT.md` draft before handoff.

The reviewer checks:
- all material gray areas are resolved or explicitly scoped out
- no locked decisions contradict each other
- D-IDs are assigned consistently
- outstanding questions are split correctly between "Resolve Before Planning" and "Deferred to Planning"

Allow at most one retry iteration. If the draft still fails after that retry, flag the unresolved gray areas to the user and ask whether to proceed or keep exploring. Do not auto-proceed.

**Quick** work is exempt from this self-review step.

## Handoff

When exploring is complete:
1. write `CONTEXT.md`
2. update `.beads/STATE.json`
3. report how many decisions were locked and what remains out of scope
4. hand off to `beo-planning`

Exploring STATE.json uses the canonical 12-field schema from `../reference/references/state-and-handoff-protocol.md` (see Example F). Exploring-specific field values:

- `phase`: `"exploring"`
- `status`: `"planning-needs-approach"` (on completion)
- `tasks`: `"none — exploring does not create beads"`
- `next`: `"beo-planning"`
- `planning_mode`: `"unknown"` (pre-planning)
- `phase_name`: human-readable feature summary (e.g., `"Onboarding wizard"`)

Exploring does not create execution beads.
Its deliverable is decision clarity.

## Context Budget

If context usage exceeds 65%, use `../reference/references/state-and-handoff-protocol.md` for canonical `STATE.json` and `HANDOFF.json`, then include exploring-specific fields such as locked decisions and open questions before pausing.

## Red Flags & Anti-Patterns

Red flags to catch early:
- if you find fewer than 2 meaningful gray areas for non-trivial work, verify that you have not skipped edge cases or scope boundaries
- do not spend excessive time circling a single unresolved question; lock what is known and mark the rest for planning only when the remaining uncertainty is truly planning-shaped
- do not skip exploring for non-instant feature work just because the request sounds simple; only work classified as `instant-path` by `beo-router` may bypass exploring

Read `references/context-template.md` when creating or updating `CONTEXT.md` to ensure correct structure and required fields.
Read `references/gray-area-probes.md` when a user's answer is ambiguous or incomplete and you need targeted follow-up questions.
