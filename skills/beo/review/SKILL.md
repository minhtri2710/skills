---
name: beo-review
description: Judges completed BEO execution and emits exactly one terminal review verdict.
---

# beo-review

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

## Decision

Emit exactly one terminal review verdict.

## Enter

- Ready-for-review execution evidence exists with no active blockers and pre-execution integrity evidence.

## Owns

- Accept/fix/reject verdict.
- Findings and review evidence.
- Closure recommendation.
- Learning candidate signal.

## Writes

- Compact review fields or `REVIEW.md`.
- Accepted-review closure bookkeeping after verdict.
- Legal transition metadata, including temporary-owner return provenance when routing to `beo-debug`.

## Stops

- Execution evidence is incomplete, stale, contradictory, or unavailable.
- Root cause evidence is required but unproven.
- Owner/feature identity is unsafe.

## Exits

- `entry_blocked_execution_evidence_incomplete` -> `beo-execute`
- `verdict_accept` -> `done`
- `verdict_accept_learning_candidate` -> `beo-learn`
- `verdict_fix_unproven_root_cause` -> `beo-debug`
- `verdict_fix_bounded_repair` -> `beo-plan`
- `verdict_reject` -> `beo-plan`
- `repair_budget_exceeded` -> `user`
- `user_abandoned` -> `done`
- `owner_feature_identity_unsafe` -> `beo-route`

## Method

1. Verify review entry evidence is complete and current.
2. Inspect live declared files, changed files, and verification evidence.
3. Emit one verdict with findings and evidence.
4. For accepted work, close runtime or hand off to learning candidate.
5. For unproven root cause, write transition provenance with `return_to_caller` before handing to `beo-debug`.
6. For bounded repair, hand off to plan; never patch directly.
