# Router Operations

Role: APPENDIX
Allowed content only: route defect classification, evidence capture steps, owner identity decision ladder, output card
Forbidden content: approval authority, review verdict authority, writable-surface expansion beyond STATE/HANDOFF

## Legal route defects (ROUTE-01)

A route decision is legal only for:

- `missing_owner`
- `stale_owner`
- `contradictory_owner`
- `colliding_predicates`
- `feature_collision`

## Route is not a repair owner (ROUTE-02)

Do not use `beo-route` for ordinary artifact defects. If the active owner can legally repair the defect, that owner continues. If the next legal owner is obvious from the current owner contract, hand off directly.

Examples: missing `approval_ref` belongs to `beo-validate`; missing plan verification belongs to `beo-plan`; vague review evidence stays in the review fix/debug path; contradicted requirements belong to `beo-explore`.

## Startup evidence

At session start, read `.beads/STATE.json` if present. Read `.beads/HANDOFF.json` only if resuming paused or transferred work. Read current required surfaces only for the active `feature_slug`.

Startup output is advisory only and cannot approve execution, select execution sets, emit review verdicts, record learning, consolidate learning, or author skill changes.

Learning is not a route defect. Route may identify a learning case only after the owner/feature identity decision is complete.

## Evidence capture steps

| Step | Action |
| --- | --- |
| 1 | Read canonical state if present (STATE-01). |
| 2 | Identify active feature from `STATE.json.feature_slug` and current required surfaces. |
| 3 | Inspect `HANDOFF.json` only when resuming paused/transferred work. |
| 4 | Compare owner predicate evidence against loaded owner contracts. |
| 5 | If multiple active feature candidates exist and canonical evidence cannot select one, route to `user` (STATE-02). |
| 6 | If exactly one defect proves unsafe owner identity, select the legal next owner. |

## Owner identity decision ladder

Use this ordering whenever owner identity is unclear:

1. If multiple active feature candidates cannot be resolved by canonical evidence, route to `user`.
2. If finalized execution evidence is ready for terminal verdict, route to `beo-review`. This must be checked before current-owner continuation. If `PASS_EXECUTE` still exists but execution evidence is finalized, do not route back to execute.
3. If a current valid owner can legally continue or repair its own artifact defect, keep that owner.
4. If requirements are missing, contradicted, or a Human Gate can affect acceptance/scope/constraints, route to `beo-explore`.
5. If locked requirements exist but executable scope is missing/stale/invalid, route to `beo-plan`.
6. If locked requirements and plan exist but readiness/approval/classification is needed, route to `beo-validate`.
7. If `PASS_EXECUTE`, approval reference, selected execution set, declared files, forbidden paths, verification contract, and verified integrity are fresh, route to `beo-execute`.
8. If mutation or verdicting would be unsafe because root cause is unproven, route to `beo-debug`.
9. If runtime decision is complete and a concrete observed learning case is tagged with source evidence, route to `beo-compound`.
10. If a concrete learning case is present but provenance is missing, return to the last runtime owner that produced the evidence. Do not route to compound until the tag exists.
11. If only a setup/check/usage question is active and no runtime owner is active, route to `beo-setup`.
12. If the user asks for read-only canonical rule lookup, route to `beo-reference`.
13. If no safe owner can be selected, route to `user`.

## Route and learning

If route observes a concrete owner-identity false case:

1. Repair/select/block the correct owner first.
2. Only after owner identity is safe, route to compound if a learning case is concrete and tagged with `learning_source`.
3. Do not use compound instead of owner repair.

## Output card

```md
Decision:
Evidence:
Changed surfaces:
Blocked by:
Next owner:
Next owner reason:
```

Put route defect, active feature, disqualified owners, and selected-owner evidence under `Evidence`.
