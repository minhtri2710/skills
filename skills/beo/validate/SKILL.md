---
name: beo-validate
description: Mandatory technical gate before execution. Grants or refuses PASS_EXECUTE for one atomic Beads-anchored BEO ticket after verifying scope, safety, and contracts.
---

# beo-validate

Refs: `beo-reference -> references/safety.md`, `beo-reference -> references/lifecycle.md`.

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
- `abandoned` -> `beo-review`

## Method

1. Verify atomicity and ensure no unsafe, undeclared path overlaps exist.
2. Run validation safety gate: `beo_check.py --check validate --issue <issue-id>`.
3. Upon validation success, write `PASS_EXECUTE` token, recording `approval_ref` and prestate hashes.
4. For repairs, enforce change request bounds per lifecycle and safety doctrine.
5. Soft drift (title/labels) triggers warnings; hard drift (scope/criteria changes) invalidates.

