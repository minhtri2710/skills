---
name: beo-review
description: Audit containment, verification, and side effects for a completed BEO ticket, and issue a final verdict. Always use this skill after code changes are done, when verification passes, or when an issue needs to be closed or sent back for repair. Trigger this when the user says "review this", "submit my bead", "close the ticket", or "are we done?"
requires: br>=0.1.28
---
# beo-review

## Use when

Execution is ready for independent audit, or an abandoned delivery needs a final BEO route.

## Read

- Claimed issue state from `br show <issue-id> --json`.
- Plan-owned `TICKET.md`, validate-owned approval state, execute-owned evidence, and relevant runtime events.
- Changed paths, verification output, containment checks, and strict side-effect evidence when applicable.
- `beo-reference` canonical contracts: `references/kernel.md`, `references/safety.md`, `registry/pipeline.json`, `registry/ticket-schema.json`, `registry/approval-envelope.json`, and `registry/command-contracts.json`.

## Do

1. Run review entry checks through `beo-reference` scripts as commands.
2. Audit containment, approved-scope adherence, verification results, side-effect evidence, and acceptance criteria.

### Quick Mode Review Fast-Path
For Quick Mode tickets, review audits simple execution evidence, unchanged boundaries, and verification results without requiring strict attachments, independence reviews, or side-effect evidence. Repair budgets (quick=1) remain fully active.
3. Emit exactly one verdict or repair route.
4. Close the Beads issue only after an accepted verdict.
5. Release active path reservation on final verdict when one exists.
6. Emit a learning candidate only after the delivery route is recorded and only for reusable, safe evidence.

## Repair Loop Policy

Enforce repair budgets from `profiles.json repair_budget_policy` and transition
rules from `pipeline.json repair_loop_policy`. Same-scope repair delta boundaries
are defined in `pipeline.json repair_loop_policy.same_scope_repair_delta`.
Quick=1, standard=2, strict=explicit. Counter resets only on new PASS_EXECUTE
after user-driven plan restart.

### Terminal Routes
- `repair_budget_exceeded`: Routes to user when mode budget exhausted; user decides continuation or `cannot_deliver`
- `cannot_deliver`: Terminal blocker requiring registered reason (`user_owned`, `unsafe_environment`, `unavailable_dependency`, `scope_invalid`, `tool_missing`); routes to user with reason, never auto-abandons

## Write

- Review-owned `state.json` fields: verdict, findings, repair route, cannot-deliver reason, or abandon result.
- Runtime events for repair, diagnosis handoff, abandon, or learning candidate when needed.
- `br close` and `br sync --flush-only` only after accepted review or registered abandon closure.

## Emit

- `entry_blocked_execution_evidence_incomplete` -> stop and load `beo-execute`.
- `verdict_accept` -> close through `br`, then stop.
- `repair_same_scope` -> stop and load `beo-validate`.
- `repair_rescope` -> stop and load `beo-plan`.
- `cannot_deliver` or `repair_budget_exceeded` -> stop for user.
- `root_cause_diagnosis_needed` -> stop and load `beo-debug`.
- `abandoned` -> stop after recording final route.
- `learning_candidate` -> after the verdict route, stop and load `beo-learn` only for the learning hook.

## Never

- Do not mutate product files (review is an independent audit; changing code during review violates the separation of concerns).
- Do not grant approval tokens (only validate can issue PASS_EXECUTE).
- Do not redesign scope or acceptance locally (route to repair_rescope if the current scope/acceptance is invalid).
- Do not choose next unrelated work while reviewing the current issue.
- Do not load another BEO delivery owner in the same turn for the same issue after emitting; stop first.
