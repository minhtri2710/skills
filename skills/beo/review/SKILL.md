---
name: beo-review
description: |
  Emits exactly one phase-terminal review verdict from finalized execution evidence. Use when execution evidence contains ready_for_review, no blockers, and recorded pre-execution integrity check evidence. Not for implementation fixes, readiness refresh, or root-cause proof.
---

# beo-review

## Purpose

Review completed execution and emit one phase-terminal verdict.

## Decision Card

Decision: emit exactly one phase-terminal review verdict.

Can enter when:
- execution evidence is `ready_for_review` with no active blockers and recorded pre-execution integrity evidence

Can write:
- `TICKET.md#Review` or `REVIEW.md`, plus accepted-review closure bookkeeping after the verdict

Must stop when:
- execution evidence is incomplete/stale/contradictory or root-cause evidence is required but unproven

Exit summary (non-authoritative):
- `entry_blocked_execution_evidence_incomplete` -> `beo-execute`
- `verdict_accept` -> `done`
- `verdict_accept_learning_candidate` -> `beo-learn`
- `verdict_fix_unproven_root_cause` -> `beo-debug`
- `verdict_fix_bounded_repair` -> `beo-plan`
- `verdict_reject` -> `beo-plan`
- `repair_budget_exceeded` -> `user`
- `owner_feature_identity_unsafe` -> `beo-route`

Never:
- mutate product files, approve, or directly patch after a fix verdict

Reads:
- current artifacts, live declared files, approval, learning, and pipeline

## Contract

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

Acts when:
- complete `ready_for_review` execution evidence exists with no active blockers, including pre-execution integrity check, ledger status, selected execution set, completed items, and resume point when full density uses `TRACKER.json`

Owns:
- phase-terminal verdict and review findings

Writes:
- `TICKET.md#Review` or `REVIEW.md`
- accepted-review runtime closure bookkeeping: `FEATURE.json.lifecycle_status`, closure metadata, and neutralized active STATE pointers only after writing the final verdict

Reads:
- current artifacts, live declared files, `beo-reference -> references/approval.md`, `beo-reference -> references/learning.md`, `beo-reference -> registry/pipeline.json`

Local stops:
- execution evidence is incomplete, stale, contradictory, or unavailable
- root cause evidence is required but unproven
- owner/feature identity is unsafe

Local forbids:
- product mutation, approval, execution evidence mutation, direct patch after fix

Exits:
- `entry_blocked_execution_evidence_incomplete` -> `beo-execute`
- `verdict_accept` -> `done`
- `verdict_accept_learning_candidate` -> `beo-learn`
- `verdict_fix_unproven_root_cause` -> `beo-debug`
- `verdict_fix_bounded_repair` -> `beo-plan`
- `verdict_reject` -> `beo-plan` with handoff
- `repair_budget_exceeded` -> `user`
- `owner_feature_identity_unsafe` -> `beo-route`

## Repair Loop

A phase-terminal `fix` verdict ends the review phase but does not authorize mutation or end the workflow. `fix` with unproven cause exits to `beo-debug`; proven bounded repair exits to `beo-plan`; repair scope must be represented as an execution set, pass `beo-validate`, and be delivered only by `beo-execute`.

Review never directly patches product files.
