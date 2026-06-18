# BEO Phase Contracts

> [!NOTE]
> This reference is subordinate to `references/kernel.md`. `references/kernel.md` is the canonical owner of BEO rules and invariants.

The canonical machine-readable contract is `registry/phase-contracts.json`. Per-skill entries record class, `state_write_fields`, `artifact_write_authorities`, `may_emit_*` conditions, `may_emit_runtime_event_kinds`, `must_not`, and (when applicable) `validation_preconditions` content gates or `decomposition_recorded_contract` advisories. This reference summarizes the binding categories; the registry is the source of truth.

## Owner classes

Owner classes are canonical in `registry/phase-contracts.json`.

## Critical boundaries

- Only delivery owners advance delivery state.
- Support subroutines return evidence or advisory output to a delivery owner.
- Maintenance skills mutate only BEO control-plane materials or explicitly authorized setup.
- `beo-reference` is read-only.
- The contract matrix is canonical in `registry/phase-contracts.json`.

## Validation preconditions and decomposition contracts

Two blocks complement the binding per-skill contract and apply during the planning and validation phases:

- `beo-validate.validation_preconditions` — mandatory content-based preconditions that `beo-validate` must apply after ticket-shape validation and before granting `PASS_EXECUTE`. A missing precondition is a hard reject routed `validation_failed -> beo-plan`. Currently scoped to strict-mode destructive schema changes that require a runnable pre-check script in addition to any Human Gate.
- `beo-plan.decomposition_recorded_contract` — advisory conventions for what `beo-plan` writes at the `decomposition_recorded` transition. Currently scoped to pre-writing `TICKET.yaml` for every proposed atomic bead before emitting `decomposition_recorded`, so each child can enter validation directly without a separate planning pass.

Neither block grants new write authority; per-skill `artifact_write_authorities` and `must_not` remain binding. `validation_preconditions` is enforced (a missing precondition rejects); `decomposition_recorded_contract` is advisory guidance.

## Repair boundary

Repair boundary rules are canonical in `references/kernel.md`. In summary:
- `repair_same_scope`: approved file set, generated outputs, done criteria, verification commands, mode, and Human Gates remain unchanged.
- `repair_rescope`: any of the above must change.

## User handoff route comments

`br.final_route_comments` means phase-final route or handoff comments, not review-only comments. For the `user_review_needed` handoff format, subtype selection, and evidence ref rules, see `references/user-handoff.md`.
