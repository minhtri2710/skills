---
name: beo-review
description: Emits one verdict for an executed atomic Beads ticket and closes or routes the bead accordingly.
---

# beo-review

Refs: `beo-reference -> references/lifecycle.md`, `beo-reference -> references/kernel.md`.

## Decision

Accept, abandon, or route repair for one executed atomic ticket.

## Enter

- `execution.status: ready_for_review` exists.
- `beo_check.py --check review` verifies containment and verification.

## Owns

- Verdict, findings, closure evidence.
- `learning_candidate` events.

## Stops

- Execution evidence missing, stale, or contradictory.
- Changes outside approved scope.
- Blocking findings exist.

## Exits

- `entry_blocked_execution_evidence_incomplete` -> `beo-execute`
- `verdict_accept` -> `done`
- `repair_same_scope` -> `beo-validate`
- `repair_rescope` -> `beo-plan`
- `cannot_deliver` -> `user`
- `root_cause_diagnosis_needed` -> `beo-debug`
- `repair_budget_exceeded` -> `user`
- `abandoned` -> `done`

## Method

1. Run verification checks: `beo_check.py --check review --issue <issue-id>`.
2. Evaluate file containment boundaries, verify test evidence, and check side-effects.
3. If accepted: Write verdict, close issue (`br close <issue-id>`), and flush (`br sync --flush-only`).
4. If abandoned: Record reason, verify cleanup of dirty mutations, and close.
5. If repair: Route to `beo-validate` (same scope) or `beo-plan` (rescope) as appropriate.
6. Emit `learning_candidate` event for reusable patterns or mistakes to trigger learn loop.

