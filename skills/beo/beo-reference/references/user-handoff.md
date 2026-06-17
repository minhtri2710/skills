# User Handoff Format

> [!NOTE]
> This reference is subordinate to `references/kernel.md`. `references/kernel.md` is the canonical owner of BEO rules and invariants.
>
> This file owns the `user_review_needed` handoff format. Other files should cite this file instead of restating this content.

## Handoff Requirements

When emitting `user_review_needed`, every handoff must include all of the following in the Beads comment or handoff text:

1. **Handoff subtype** — one of the subtype values below.
2. **Blocking question** — the specific decision the user must make.
3. **Recommended option** — BEO's recommended choice with reasoning.
4. **Fallback (optional)** — what happens if the user does not act.
5. **Evidence refs** — durable repo-relative refs supporting the handoff.

Do not emit a vague user handoff.

## Subtype Selection

Use the following table to select the correct handoff subtype:

| Condition | Subtype |
|---|---|
| Claim mismatch, closed issue, or blocked issue | `user_claim_or_lifecycle_decision_needed` |
| Dirty approved/generated paths | `user_dirty_tree_action_needed` |
| User-authorizable scope question or unauthorized broad glob | `user_scope_decision_needed` |
| Unresolved Human Gate | `user_human_gate_needed` |
| External side effect or irreversible behavior | `user_external_side_effect_authorization_needed` or `user_irreversible_behavior_decision_needed` |
| Missing strict reservation | `user_strict_reservation_action_needed` |
| Parent decomposition blocker | `user_decomposition_boundary_decision_needed` |
| Review cannot choose an allowed route without user authority | `user_review_verdict_decision_needed` |
| Path/scope decisions marked user-authorizable by registry | `user_path_safety_decision_needed` |

Protected or unsafe paths route to plan repair unless a registry entry explicitly makes the path decision user-authorizable.

## Evidence Refs

Evidence refs must be durable and repo-relative.

Allowed:
- `.beads/artifacts/<issue-id>/checks/<file>`
- `.beads/artifacts/<issue-id>/logs/<file>`
- `br-comment:<id>`

Disallowed:
- Raw secrets
- Absolute local paths
- Unredacted customer data
- Temporary terminal scrollback without a durable file
