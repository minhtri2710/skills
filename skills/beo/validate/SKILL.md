---
name: beo-validate
description: Mandatory technical gate to grant or refuse PASS_EXECUTE for one planned atomic Beads ticket before mutation.
---
# beo-validate
Refs: `references/safety.md`, `references/lifecycle.md`.

## Decision
Grant or refuse `PASS_EXECUTE` token for one atomic bead.

## Enter
- Plan-owned fields exist in `TICKET.md`.
- Selected bead is atomic.

## Owns
- Readiness evaluation, execution mode, approval projection, and prestate hashes.

## Does Not Own
- Scope design, product mutation, review verdicts, issue closure, or learning persistence.

## Stops
- Unresolved Human Gates, non-atomic beads, path collisions, broad unauthorized globs, or stale/missing canonical issue state.

## Exits
- `PASS_EXECUTE` -> `beo-execute`
- `FAIL_PLAN` -> `beo-plan`
- `BLOCK_USER` -> `user`
- `abandoned` -> `beo-review`

## Method
1. Confirm claim and issue identity with `br`; treat `bv` and memory as advisory only.
2. Enforce atomicity, path containment, overlap scans, and execution-mode requirements per `references/safety.md`.
3. Run validation check script using `beo_check.py`.
4. On pass, write `PASS_EXECUTE` and prestate hashes; on fail, route to the owning phase instead of patching scope here.
5. For repairs, enforce registered change bounds before granting a new token.
