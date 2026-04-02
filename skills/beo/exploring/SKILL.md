---
name: beo-exploring
description: >-
  Use before any non-instant feature work, refactor, behavior change, or
  requirements-shaping conversation where user intent is not yet locked,
  especially when the user knows what they want but has not fully thought
  through edge cases, scope boundaries, or expected behavior.
---

# Beo Exploring

## Overview

Exploring is the decision-extraction phase.
Use it to turn a partially formed request into a planning-usable `CONTEXT.md`.

**Core principle:** ask until planning can proceed without guessing.

`CONTEXT.md` becomes the source of truth for downstream planning, validation, execution, and review.

## Hard Gates

<HARD-GATE>
Ask **one focused question at a time**.
Do not batch multiple exploration questions into one message.
</HARD-GATE>

<HARD-GATE>
Ask about **behavior**, not implementation.
Users decide what should happen; planning decides how to build it.
</HARD-GATE>

<HARD-GATE>
Do not proceed to planning until every material gray area has either:
- a locked decision, or
- an explicit out-of-scope ruling.
</HARD-GATE>

<HARD-GATE>
Never copy the user's raw request or secrets verbatim into `CONTEXT.md`.
Sanitize the request summary, redact or omit secrets, and use stable placeholders such as `[REDACTED_API_KEY]` when sensitive literals matter for implementation.
</HARD-GATE>

## Default Exploring Loop

1. read any existing context and prior learnings
2. classify the scope and likely gray areas
3. ask one focused behavioral question at a time
4. lock decisions explicitly as they emerge
5. write a sanitized `CONTEXT.md`
6. self-check for planning readiness, then hand off to `beo-planning`

Use `../reference/references/learnings-read-protocol.md` when you need the canonical prior-learnings read flow.
Use `../reference/references/slug-protocol.md` when updating the epic description safely.

## When Not to Use

- truly instant work already routed by `beo-router`
- clear bug-fix root-cause work -> `beo-debugging`
- mid-pipeline resume -> `beo-router`

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

`CONTEXT.md` must be planning-usable.
At minimum it should contain:
- a sanitized request summary
- scope classification
- locked decisions
- out-of-scope items
- open questions that need research rather than more user decisions
- relevant patterns when they materially affect planning

The goal is not to preserve the original conversation.
The goal is to preserve the decisions that planning must trust.

## Planning-Readiness Check

Before handoff, confirm all of these are true:
- every material gray area has been resolved or scoped out
- a planner could explain the feature using `CONTEXT.md`
- no unanswered question would change the high-level plan

If any of these fail, keep exploring.

## Handoff

When exploring is complete:
1. write `CONTEXT.md`
2. update `.beads/STATE.md`
3. report how many decisions were locked and what remains out of scope
4. hand off to `beo-planning`

Exploring does not create execution beads.
Its deliverable is decision clarity.

## Context Budget

If context usage exceeds 65%, use `../reference/references/state-and-handoff-protocol.md` for canonical `STATE.md` and `HANDOFF.json`, then include exploring-specific fields such as locked decisions and open questions before pausing.

## Red Flags & Anti-Patterns

See `references/exploring-guardrails.md` for the full tables.
