# router-operations

Role: APPENDIX
Allowed content only: live onboarding gate command, feature detection command, route evidence capture steps, and local operational mechanics.

This appendix is operational only. Owner selection and collision doctrine are canonical in `beo-route`, legal transitions are canonical in `beo-reference -> pipeline.md`, and route evidence shape is canonical in `beo-reference -> state.md`.

## Live onboarding gate

Run before downstream owner selection when the installed onboarding skill path is known:

```sh
node <installed-beo-onboard-root>/scripts/onboard_beo.mjs --repo-root "<absolute-repo-root>"
```

If the result is not `up_to_date`, record onboarding freshness evidence and continue through canonical owner selection. This appendix does not choose between `beo-onboard`, `beo-reference`, `beo-author`, or another legal owner.

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

Enumerate directories under `.beads/artifacts/` with repo-supported file listing, or inspect known artifact paths from `STATE.json`.

If more than one active feature can satisfy the request and no explicit feature is selected, record the candidate feature slugs and ambiguity evidence. Canonical owner selection decides whether the next owner is `user` or another legal owner.

## Operational checklist

| Step | Action |
| --- | --- |
| 1 | Run the live onboarding gate and record status evidence. |
| 2 | Inspect `STATE.json` and ignore stale or contradictory state against live artifacts. |
| 3 | Inspect `HANDOFF.json` when present, evaluate freshness in `beo-reference -> state.md`, and record `handoff_used=false` plus `handoff_ignored_reason` when the handoff is stale or invalid. |
| 4 | Detect active feature candidates and record ambiguity evidence when explicit feature selection may be required. |
| 5 | Apply the owner decision ladder and collision rules in `beo-route`. |
| 6 | Write `route_decision` with selected owner, disqualified owners, evidence, and timestamp. |
| 7 | Update `current_owner`, `status`, and `evidence` in `STATE.json`. |

For route evidence shape, use `beo-reference -> state.md`; this appendix records evidence only and does not own routing decisions.
