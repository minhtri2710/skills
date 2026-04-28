# router-operations

Role: APPENDIX
Allowed content only: live onboarding gate command, feature detection command, route evidence capture steps, and local operational mechanics.

This appendix is operational only. Routing precedence, the owner decision ladder, and collision doctrine are canonical in `beo-route`.

## Live onboarding gate

Run before downstream owner selection when the installed onboarding skill path is known:

```sh
node <installed-beo-onboard-root>/scripts/onboard_beo.mjs --repo-root "<absolute-repo-root>"
```

If the result is not `up_to_date`, route to `beo-onboard` unless the user explicitly requested `beo-reference` read-only lookup or `beo-author` contract-only work that does not depend on repo runtime state.

## Minimum inspection set

| Surface | Use |
| --- | --- |
| `.beads/STATE.json` | current owner, status, route decision, phase |
| `.beads/HANDOFF.json` | resume checkpoint when fresh; stale/invalid handoff evidence and ignored-reason input when not fresh |
| `.beads/artifacts/<feature_slug>/CONTEXT.md` | requirement lock and contradictions |
| `.beads/artifacts/<feature_slug>/PLAN.md` | current phase, bead graph, file scopes |
| `.beads/artifacts/<feature_slug>/approval-record.json` | approval freshness and scope |
| `.beads/artifacts/<feature_slug>/execution-bundle.json` | execution completion evidence |
| `.beads/artifacts/<feature_slug>/REVIEW.md` | verdict and learning disposition |

## Feature candidate detection

```sh
tilth ".beads/artifacts/*" --scope .beads
```

If more than one active feature can satisfy the request and no explicit feature is selected, route to `user` with the candidate feature slugs.

## Operational checklist

| Step | Action |
| --- | --- |
| 1 | Run the live onboarding gate and record status evidence. |
| 2 | Inspect `STATE.json` and ignore stale or contradictory state against live artifacts. |
| 3 | Inspect `HANDOFF.json` when present, evaluate freshness in `beo-references -> state.md`, and record `handoff_used=false` plus `handoff_ignored_reason` when the handoff is stale or invalid. |
| 4 | Detect active feature candidates and require user selection when ambiguous. |
| 5 | Apply the owner decision ladder and collision rules in `beo-route`. |
| 6 | Write `route_decision` with selected owner, disqualified owners, evidence, and timestamp. |
| 7 | Update `current_owner`, `status`, and `evidence` in `STATE.json`. |

For route decision shape, use `beo-references -> state.md` and local route evidence extensions in `beo-route`.
