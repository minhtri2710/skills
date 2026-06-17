# BEO Phase Contracts

> [!NOTE]
> This reference is subordinate to `references/kernel.md`. `references/kernel.md` is the canonical owner of BEO rules and invariants.

This file summarizes phase permissions. The canonical machine-readable permission matrix is `registry/phase-contracts.json`.

## Owner classes

Owner classes are canonical in `registry/phase-contracts.json`.

## Critical boundaries

- Only delivery owners advance delivery state.
- Support subroutines return evidence or advisory output to a delivery owner.
- Maintenance skills mutate only BEO control-plane materials or explicitly authorized setup.
- `beo-reference` is read-only.
- The permission matrix is canonical in `registry/phase-contracts.json`.

## Repair boundary

Repair boundary rules are canonical in `references/kernel.md`. In summary:
- `repair_same_scope`: approved file set, generated outputs, done criteria, verification commands, mode, and Human Gates remain unchanged.
- `repair_rescope`: any of the above must change.

## User handoff route comments

`br.final_route_comments` means phase-final route or handoff comments, not review-only comments. For the `user_review_needed` handoff format, subtype selection, and evidence ref rules, see `references/user-handoff.md`.
