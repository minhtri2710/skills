---
name: beo-reviewing
description: >-
  Use after the final approved execution scope is complete, or when the user
  asks whether a feature is done, ready to ship, safe to merge, or needs a
  quality check. Use for prompts like "review this feature", "is this done?",
  "can we ship this?", "double-check the implementation", or "run UAT".
---

> **Onboarding gate:** If `.beads/onboarding.json` is missing or stale, stop and load `beo-using-beo` before continuing.

# Beo Reviewing

## Overview

Reviewing is the final quality gate after execution.
Its job is to verify that the implemented final execution scope is safe, aligned with locked decisions, and actually acceptable to the user before the feature is finished.

**Core principle:** review finds truth, not excuses.

## Communication Standard

Review outputs must follow `../reference/references/communication-standard.md`.

## Default Review Loop

1. confirm review is allowed for the final execution scope
2. run automated specialist review
3. classify findings by severity and create follow-up work when needed
4. run human UAT against locked decisions and exit-state claims
5. decide whether to finish, loop through reactive fixes, or route back
6. hand off to compounding only when review is truly complete

Use `references/reviewing-operations.md` for the exact prerequisite checks, artifact verification, UAT handling, and finishing sequence.
Use `references/review-specialist-prompts.md` for the five-specialist review structure and severity rules.

## Hard Gates

<HARD-GATE>
If `planning_mode = multi-phase` and later phases remain, do not treat the feature as complete.
Remove `approved` if needed and route back to `beo-planning`.
</HARD-GATE>

<HARD-GATE>
Do not finish the feature while any P1 issue remains unresolved.
P1 findings become reactive fix beads under the current epic and must be executed before review can finish.
</HARD-GATE>

<HARD-GATE>
Human UAT is required.
Do not auto-pass UAT from automated review, tone, or silence.
Walk through locked decisions and exit-state claims one at a time, waiting for explicit user confirmation.
</HARD-GATE>

<HARD-GATE>
If the user changes intent in a way that affects architecture, sequencing, or other locked decisions, stop review.
Update `CONTEXT.md`, strip `approved` if needed, and route back to `beo-planning`.
</HARD-GATE>

<HARD-GATE>
Do not write novel implementation code inside review.
Create fix beads and send execution work back through the proper path.
</HARD-GATE>

## Review Prerequisites

Confirm the final execution scope is actually complete and all required artifacts are available before starting review.
See `references/reviewing-operations.md` Section 1 for the exact prerequisite checks.

## Scope Rule

Review the executed scope only.
For multi-phase work, that means the final approved scope for the feature **only when no later phases remain**.
If later phases still exist, do not finish the feature in review; route back to planning-aware flow instead.

## Automated Specialist Review

Run the canonical five-specialist review defined in `references/review-specialist-prompts.md`.
The review must cover, at minimum:
- implementation correctness
- contract / interface safety
- test and verification adequacy
- architecture / maintainability risk
- user-facing or workflow regression risk

Use the reference file for the exact prompts and dispatch structure.

## Severity Semantics

Do not collapse the P1/P2/P3 categories. Their placement and blocking behavior matter.
See `references/review-specialist-prompts.md` for the severity table and rules.

## Reactive Fix Loop

Reactive fixes are part of finishing the current feature. P2 and P3 work are not.
See `references/reviewing-operations.md` and `references/review-specialist-prompts.md` for the exact P1 fix-and-re-review cycle.

## Human UAT

Human UAT is not optional.
Review automated findings first, then walk the user through the implemented outcome against locked decisions and exit-state claims.

Use `references/reviewing-operations.md` Section 4 for the exact UAT loop and outcome handling.

## Intent Changes During UAT

If the user says the implementation is wrong because the desired behavior changed:
- update `CONTEXT.md` to reflect the new decision
- if the change is minor and does not alter architecture or sequencing, create follow-up work using the proper severity path
- if the change is major, stop review, strip `approved`, and route back to `beo-planning`

Do not patch over a changed feature definition inside review.

## Finishing Rules

Use `references/reviewing-operations.md` Section 5 for the exact conditions, finish sequence, artifact verification, and final reporting.

## Handoff to Compounding

Only after review genuinely passes:
1. write fresh state using `../reference/references/state-and-handoff-protocol.md`
2. announce the feature is ready to finish
3. load `beo-compounding`

Do not hand off to compounding while P1 fixes, unresolved UAT, or planning-level intent changes remain.

## Context Budget

If context usage exceeds 65%, write `.beads/HANDOFF.json` using `../reference/references/state-and-handoff-protocol.md` and include:
- review progress
- open findings by severity
- UAT status
- whether review is waiting on execution, planning, or user confirmation

## Red Flags & Anti-Patterns

See `references/reviewing-guardrails.md` for the full tables.
