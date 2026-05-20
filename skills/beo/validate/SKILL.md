---
name: beo-validate
description: Mandatory technical gate before execution. Grants or refuses PASS_EXECUTE for one atomic Beads-anchored BEO ticket after verifying scope, safety, and contracts.
---

# beo-validate

Refs: `beo-reference -> references/approval.md`, `beo-reference -> references/modes.md`.

## Decision

Grant or refuse `PASS_EXECUTE` for one atomic bead.

## Enter

- Plan-owned fields exist in `TICKET.md`.
- Selected bead is atomic.

## Owns

- `readiness`, `selected_execution_set`, `execution_mode`, `approval_ref`, `integrity`.

## Stops

- Unresolved Human Gates or non-atomic beads.
- Unsafe undeclared path overlap with other active tickets.
- Missing strict command contracts for stateful systems.

## Exits

- `PASS_EXECUTE` -> `beo-execute`
- `FAIL_PLAN` -> `beo-plan`
- `BLOCK_USER` -> `user`

## Method

1. Confirm `atomicity.decision: atomic`.
2. Check for unsafe overlap; safe overlap must be per-path in `scope.scope_overlap.overlaps`.
3. Run `beo_check.py --check validate --issue <issue-id>`.
4. Record `approval_ref`, mode, and hashes only if checks pass.
5. For `repair_same_scope`, require valid `change_request` per `beo-reference -> references/lifecycle-events.md`.
6. Apply drift rules: Soft Drift (title/labels) notes only; Hard Invalidators (scope/criteria) refuse.
