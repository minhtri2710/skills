# BEO Phase Contracts

> [!NOTE]
> This reference is subordinate to [references/kernel.md](file:///Users/beowulf/Work/personal/beo-skills/skills/beo/beo-reference/references/kernel.md). `references/kernel.md` is the canonical owner of BEO rules and invariants.

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

Use `repair_same_scope` only when all are true:

- approved file set remains valid,
- generated outputs remain valid,
- done criteria unchanged,
- verification commands unchanged or only need rerun,
- no new Human Gate is required,
- mode does not change.

Use `repair_rescope` when any are true:

- allowed files change,
- generated outputs change,
- done criteria change,
- verification contract changes,
- mode changes,
- new risk/human gate/strict contract is required.

## User handoff route comments

`br.final_route_comments` means phase-final route or handoff comments, not review-only comments. Delivery-owner `user_review_needed` comments must include subtype, blocking question, recommended option, optional fallback, and evidence refs.

Subtype selection:

- claim mismatch, closed issue, or blocked issue -> `user_claim_or_lifecycle_decision_needed`
- dirty approved/generated paths -> `user_dirty_tree_action_needed`
- user-authorizable scope question or unauthorized broad glob -> `user_scope_decision_needed`
- unresolved Human Gate -> `user_human_gate_needed`
- external side effect or irreversible behavior -> `user_external_side_effect_authorization_needed` or `user_irreversible_behavior_decision_needed`
- missing strict reservation -> `user_strict_reservation_action_needed`
- parent decomposition blocker -> `user_decomposition_boundary_decision_needed`
- review cannot choose an allowed route without user authority -> `user_review_verdict_decision_needed`
- path/scope decisions marked user-authorizable by registry -> `user_path_safety_decision_needed`

Protected or unsafe paths route to plan repair unless a registry explicitly makes the path decision user-authorizable.

## Evidence refs

Evidence refs must be durable and repo-relative.

Allowed:

- `.beads/artifacts/<issue-id>/checks/<file>`
- `.beads/artifacts/<issue-id>/logs/<file>`
- `br-comment:<id>`

Disallowed:

- raw secrets,
- absolute local paths,
- unredacted customer data,
- temporary terminal scrollback without durable file.
