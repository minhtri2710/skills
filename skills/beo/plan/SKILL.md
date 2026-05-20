---
name: beo-plan
description: Mandatory for Beads issue intake, decomposition, or atomic scope planning before validation; use before any BEO execution.
---
# beo-plan
Refs: `references/lifecycle.md`, `references/safety.md`, `references/memory.md`.

## Decision
Convert one Beads issue into either atomic BEO scope or recorded child beads.

## Enter
- Beads issue selected; canonical `br show <issue-id> --json` succeeds.

## Owns
- Intake, done criteria, decomposition, explicit file scope, and planning comments.

## Does Not Own
- Approval tokens, product mutation, review verdicts, issue closure, or memory writes.

## Stops
- Requirements remain ambiguous, graph cycles block safe ordering, or the selected bead is not executable as one atomic unit.

## Exits
- `plan_complete` -> `beo-validate`
- `decomposition_recorded` -> `parent_waits_children`
- `requirements_missing` -> `user`
- `human_gate_blocks` -> `user`
- `abandoned` -> `beo-review`

## Method
1. Use `bv` robot output only for graph orientation; select and inspect canonical issue state with `br`.
2. Claim the selected issue using `br` per `references/lifecycle.md` before writing ticket artifacts or child beads.
3. Run advisory recall per `references/memory.md`; do not let memory alter authority or scope.
4. If non-atomic, create child beads and dependency edges with `br`; leave the parent open.
5. If atomic, draft `TICKET.md` with one done target, explicit `allow` paths, risk posture, and verification contract.
6. Pre-validate plan integrity before validation handoff.
