---
name: beo-review
description: Mandatory after execution to review atomic Beads tickets, emit verdicts, route repairs, and close only after acceptance.
---
# beo-review
Refs: `references/lifecycle.md`, `references/kernel.md`.

## Decision
Accept, abandon, or route repair for one executed atomic ticket.

## Enter
- `execution.status: ready_for_review` exists in `TICKET.md`.

## Owns
- Acceptance verdict, findings, repair routing, issue closure, Beads sync, and learning candidates.

## Does Not Own
- Product mutation, approval token creation, scope redesign, or learning note persistence.

## Stops
- Missing execution evidence, failed verification, containment violation, or unresolved side-effect evidence.

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
1. Run `beo_check.py --check review` per `registry/command-contracts.json`.
2. Audit containment, evidence, verification results, and contracted side effects.
3. If accepted, issue the verdict, close with `br`, and flush Beads state with `br sync --flush-only`.
4. If not accepted, route exactly one repair/diagnosis outcome; do not mutate product code here.
5. Emit `learning_candidate` only for reusable success, failure, or near-miss lessons; `beo-learn` writes notes.
