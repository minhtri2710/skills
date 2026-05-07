# Quick reference

## Role

This asset is operator-facing only. It has no routing, approval, readiness, execution, review, closure, or learning authority.

Authority note: display-only; canonical authority remains in the referenced state/artifact surface.

## Happy path

Normal orientation is `beo-route -> beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done`, with optional `beo-review -> beo-compound -> done` when accepted learning needs feature-level disposition. `beo-dream` is explicit corpus-level consolidation only when cross-feature threshold or user request exists.

`beo-route` is exceptional owner-state repair and is not required when exactly one owner is already live.

## beo_tiny golden path

`beo_tiny` uses normal owners with compact artifacts: lock the exact requirement, write one current plan bead with explicit file scope and verification, validate one `single` execution set, execute only that set, run the same accept gate with shorter prose, then close `done` with `no-learning` when isolated.

## Owner-selection symptom table

| Symptom | First owner to consider |
| --- | --- |
| Requirements missing, unlocked, or contradicted | `beo-explore` |
| Locked requirements exist but plan or bead graph is missing/stale | `beo-plan` |
| Plan current but no fresh `PASS_EXECUTE` covers the target set | `beo-validate` |
| Fresh `PASS_EXECUTE` and selected execution set exist | `beo-execute` |
| Finalized execution bundle is ready for verdict | `beo-review` |
| Accepted work has durable or unclear feature learning | `beo-compound` |
| Two accepted features support the same learning pattern | `beo-dream` |
| Owner state is missing, stale, contradictory, colliding, or zero/multiple predicates match | `beo-route` |

If the current owner is valid from live artifacts, do not route just to reconfirm it.

## Execution modes

Supported modes are `single` and `ordered_batch` only. `beo-validate` selects the set and mode; `beo-execute` delivers only that set.

## Verdict routing

`accept` routes to `done` when learning is clearly `no-learning`, or `beo-compound` when durable or unclear learning remains. `fix` routes to `beo-debug` when root cause is unproven, otherwise to `beo-plan`; fixes do not use a direct review-to-validate fast path. `reject` routes to `beo-explore` for invalid requirements or `beo-plan` for design/scope/approach failure with valid requirements.

## Approval freshness summary

Execution needs current `PASS_EXECUTE`, `approval_ref`, selected execution set fields, and matching context/plan approval evidence. Missing/stale readiness, approval, or selected execution set before mutation returns to `beo-validate`; stale approval before mutation returns to validation or plan by stale cause; stale approval after mutation stops execution and follows `approval.md`.

## Execute hard-stop cheat sheet

Stop for missing execution fields, approval mismatch, scope violation, stale approval after mutation begins, persistence/flush failure, unrelated live-file scope ambiguity, or unproven root cause.

## Canonical authority precedence

Loaded owner contract plus canonical references decide authority. Cards, summaries, status output, and chat memory are advisory only.
