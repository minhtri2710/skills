---
name: beo-reviewing
description: >-
  Use after the final approved execution scope is complete, or when the user
  asks whether a feature is done, ready to ship, safe to merge, or needs a
  quality check. Use for prompts like "review this feature", "is this done?",
  "can we ship this?", "double-check the implementation", or "run UAT". Do
  not use for plan review (use beo-validating), mid-execution quality checks,
  or when later phases remain unplanned.
---

<HARD-GATE>
Onboarding — see `../reference/references/shared-hard-gates.md` § Onboarding Check.
</HARD-GATE>

<HARD-GATE>
If no active epic with terminal-state tasks exists, do not attempt review. Route to `beo-router` for state detection and proper intake.
</HARD-GATE>

> See `../reference/references/shared-hard-gates.md` § Shared References Convention.

# Beo Reviewing

## Overview

Reviewing is the final quality gate after execution.
Verify the implemented final execution scope is safe, aligned with locked decisions, and acceptable to the user before the feature passes quality criteria.

**Core principle:** review finds truth, not excuses.

## Communication Standard

All review outputs (specialist findings, P1/P2/P3 classifications) must follow `../reference/references/communication-standard.md`: plain language first, evidence with quotes or path:line, concrete failure scenario, and smallest fix.

## Hard Gates

<HARD-GATE>
Multi-phase completion — see `../reference/references/shared-hard-gates.md` § Multi-Phase Completion Routing.
</HARD-GATE>

<HARD-GATE>
Do not finish the feature while any P1 issue remains unresolved.
</HARD-GATE>

<HARD-GATE>
Human UAT is required.
Walk through locked decisions and exit-state claims one at a time, waiting for explicit user confirmation.
</HARD-GATE>

<HARD-GATE>
If the user changes intent in a way that meets the planning-level intent-change rule below, stop review.
Update `CONTEXT.md`, strip `approved` if needed, and route back to `beo-planning`.
</HARD-GATE>

<HARD-GATE>
Do not write novel implementation code inside review.
Create fix beads and send execution work back through the proper path.
</HARD-GATE>

<HARD-GATE>
Every task in the approved final execution scope must be in a terminal state (`done`, `cancelled`, or `failed`) before review begins. If any are still open, route back to `beo-executing`. Only `done` (`closed` in br) is a successful terminal. For `cancelled`/`failed` tasks, pause and ask the user for direction — continue only if the user confirms they were intentionally descoped and the phase exit state is still achievable. Otherwise route to `beo-planning` or `beo-executing`.
</HARD-GATE>

## Default Review Loop

1. confirm review is allowed for the final execution scope
2. run automated specialist review
3. classify findings and create follow-up work as needed
4. run human UAT against locked decisions and exit-state claims
5. announce pass or fail; hand off, loop reactive fixes, or route back as needed
6. hand off to compounding only when review is complete

| File | Use for |
| --- | --- |
| `references/reviewing-operations.md` | exact prerequisite checks, artifact verification, UAT handling, finishing sequence |
| `references/review-specialist-prompts.md` | five-specialist review structure and severity rules |

**Quick Mode:** For Quick-scope features (see `../reference/references/pipeline-contracts.md`), skip specialist subagents, do a quick manual artifact check, get explicit per-claim user confirmation, then run build/test/lint and close. Do not skip UAT. See `references/reviewing-operations.md` Section 6.

## Review Prerequisites

Confirm the final execution scope is complete and all required artifacts are available before starting review.
See `references/reviewing-operations.md` Section 1 for the exact prerequisite checks.

## Scope Rule

Review the executed scope only.
For multi-phase work, review the final approved scope for the feature **only when no later phases remain**.
If later phases still exist, do not finish the feature in review; route back to planning-aware flow.

## Automated Specialist Review

Run the canonical five-specialist review defined in `references/review-specialist-prompts.md`.

| Specialist | Focus |
| --- | --- |
| implementation correctness | implementation correctness |
| contract / interface safety | contract and interface safety |
| test and verification adequacy | test and verification adequacy |
| architecture / maintainability risk | architecture and maintainability risk |
| user-facing or workflow regression risk | user-facing and workflow regression risk |

Use the reference file for the exact prompts and dispatch structure.
Do not treat code inspection alone as sufficient evidence; review findings about tests, build, lint, runtime behavior, or generated artifacts must be backed by concrete verification evidence.

## Severity Semantics

Do not collapse the P1/P2/P3 categories. Their placement and blocking behavior matter.
See `references/review-specialist-prompts.md` for the severity table and rules.

## Specialist Conflict Resolution

Use a conservative evidence-first policy when specialists disagree:

| Case | Rule |
| --- | --- |
| substantiated P1 | block completion until re-verified or fixed |
| substantiated P2/P3 | keep all; disagreement does not erase them |
| evidence-free claim | discard or downgrade |
| contradictory blocking findings | run targeted re-verification or escalate to the user |

## Reactive Fix Loop

Reactive fixes are part of finishing the current feature. P2 and P3 work are not.
See `references/reviewing-operations.md` and `references/review-specialist-prompts.md` for the exact P1 fix-and-re-review cycle.
Do not patch implementation directly inside review. Route fixes back through execution with proper bookkeeping.

## Human UAT

Human UAT is not optional.
Review automated findings first, then walk the user through the implemented outcome against locked decisions and exit-state claims.

Use the canonical review/UAT approval rules from `../reference/references/approval-gates.md` (items 3 and 6).
Use `references/reviewing-operations.md` Section 4 for the exact UAT loop and outcome handling.

### UAT Walkthrough Order

Derive the walkthrough list in this order:
1. locked decisions from `CONTEXT.md`
2. promised exit-state lines from `phase-contract.md`
3. any user-facing workflow claims added during execution or reactive fixes

Walk each item one at a time. If an item cannot be traced to implementation or verification evidence, treat it as a review defect.

## Intent Changes During UAT

If the user says the implementation is wrong because the desired behavior changed:
- update `CONTEXT.md` to reflect the new decision
- if the change is minor, create follow-up work using the proper severity path
- if the change is major, stop review, strip `approved`, and route back to `beo-planning`

Treat the change as **minor** only when all of these are true:

| Test | Must be true |
| --- | --- |
| locked decisions | no locked decision in `CONTEXT.md` changes |
| ordering | no story ordering or phase sequencing changes |
| scope boundary | no new artifact, contract, or architectural boundary is required |

If any of those conditions fail, treat the change as **major**.

Do not patch over a changed feature definition inside review.
Do not misclassify changed user intent as a normal defect; treat it as a planning/context change and route accordingly.

## Finishing Rules

Use `references/reviewing-operations.md` Section 5 for the exact conditions, finish sequence, artifact verification, and final reporting.
When review passes with non-blocking follow-up work, keep P2/P3 items outside the current epic unless the user explicitly wants them folded into the same feature closure path.

## Handoff

Only after review genuinely passes:
1. close the epic in br: `br close <EPIC_ID>`
2. write fresh state using `../reference/references/state-and-handoff-protocol.md`
3. set the state to `status: "learnings-pending"` and `next: "beo-compounding"`
4. announce that the review gate has passed and hand off to `beo-compounding`

Do not hand off to compounding while P1 fixes, unresolved UAT, or planning-level intent changes remain.

## Context Budget

Follow `../reference/references/shared-hard-gates.md` § Context Budget Protocol. Skill-specific checkpoint items: review progress, open findings by severity, UAT status, and whether review is waiting on execution, planning, or user confirmation.

## Red Flags & Anti-Patterns

Do not skip artifact verification because the implementation "looks fine," invent a walkthrough list without grounding it in `CONTEXT.md` and `phase-contract.md`, or downgrade a planning-level intent change into a cosmetic follow-up.
