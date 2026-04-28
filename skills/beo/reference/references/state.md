# State

## State surfaces

| Surface | Rule |
| --- | --- |
| `.beads/STATE.json` | live owner, status, evidence, route decision, current phase |
| `.beads/HANDOFF.json` | real checkpoint/resume only |

Execution approval requires both live `approved` and a valid approval record.

## STATE.json shape

Operational state fields:
- `schema_version`
- `current_owner`
- `status`
- `evidence`
- `route_decision`
- `feature_slug`
- `current_phase`
- `readiness`
- `execution_mode`
- `remediation_owner`
- `approval_ref`
- `go_mode`
- `debug_return`
- `debug_result`
- `updated_at`

## Minimal STATE.json schema

The canonical live shape is:

```json
{
  "schema_version": "<version>",
  "current_owner": "<owner>",
  "status": "<status>",
  "feature_slug": "<feature-or-null>",
  "current_phase": "<phase-or-null>",
  "approval_ref": "<approval-record-path-or-null>",
  "readiness": "<readiness-or-null>",
  "execution_mode": "<serial|swarm|null>",
  "route_decision": {},
  "evidence": {},
  "updated_at": "<iso-8601>"
}
```

Required at all times after route normalization:
- `schema_version`
- `current_owner`
- `status`
- `evidence`
- `updated_at`

Required when applicable:
- `feature_slug` when a feature is active
- `current_phase` when phase-scoped planning or execution exists
- `approval_ref` when execution approval exists
- `readiness`, `execution_mode`, and `remediation_owner` only when validation evidence is current
- `route_decision` only when route evidence is relevant to the current owner selection
- `go_mode` only while the authorizing owner still owns the work
- `debug_return` and `debug_result` only while debug state is active or immediately relevant to the return path

## STATUS vocabulary

Use the smallest canonical `status` value that matches live workflow position:
- `idle`
- `needs_onboarding`
- `routing`
- `blocked_user`
- `requirements_locked`
- `plan_ready`
- `approval_ready`
- `executing`
- `swarming`
- `review_ready`
- `accepted`
- `fix_required`
- `rejected`
- `learning_pending`
- `done`

Owners may include additional nuance in `evidence`, but `status` should stay inside this vocabulary unless a shared reference is updated first.

## user_reason enum

Use `user_reason` in owner evidence when routing to `user`:
- `clarification_required`
- `external_access_required`
- `explicit_user_approval_required`
- `owner_selection_required`
- `invalid_state_requires_user`
- `multiple_active_feature_candidates`

## done_reason enum

Use `done_reason` in owner evidence when routing to `done`:
- `workflow_complete`
- `no_active_work`
- `read_only_lookup_complete`
- `authoring_complete`
- `learning_disposition_complete`
- `consolidation_complete`

## Operational write discipline

| Rule | Requirement |
| --- | --- |
| read precedence | owners read the canonical operational fields only |
| timestamp discipline | every state write refreshes `updated_at` from live write time |
| minimality | owners must not keep stale optional fields alive once the owning condition is no longer true |

## STATE field groups

| Group | Fields | Keep when | Clear when |
| --- | --- | --- | --- |
| owner | `current_owner`, `status`, `evidence`, `updated_at` | always live | replaced by newer owner evidence |
| feature | `feature_slug`, `current_phase` | active feature remains the same | feature changes or no active feature |
| route | `route_decision` | it still explains current owner selection | reroute happens or owner no longer depends on it |
| validation | `readiness`, `execution_mode`, `remediation_owner`, `approval_ref` | approval and readiness still match the live execution envelope | plan, scope, verification, mode, or approval changes |
| go | `go_mode` | same owner, same feature scope, and approval still valid | owner changes, scope changes, or approval invalidates |
| debug | `debug_return`, `debug_result` | debug handoff is active or result is not yet consumed | receiving owner consumes result or return path invalidates |

## Owner handoff clearing rule

On owner change, preserve only fields still valid for the next owner's live decision. Clear optional fields that describe a completed, invalidated, or superseded state rather than copying them forward by habit.

## Shared decision packet

Use the smallest packet that preserves routing safety:
- `owner`
- `decision`
- `basis`
- `changed`
- `blocked_by`
- `next_owner`
- `next_owner_reason`
- `evidence_refs`
- `cleared_fields`

Add owner-specific fields only when they materially affect routing, approval, readiness, debug return, review verdict, or blocker handling.
Use `cleared_fields` to name stale optional state fields intentionally removed during this exit; use `[]` when no cleanup was needed.
When `next_owner=user`, include `user_reason`.
When `next_owner=done`, include `done_reason`.
Do not write narrative summaries into `STATE.json`; keep state limited to routing-safe facts and place durable rationale in the owning artifact.

## route_decision schema

| Field | Required |
| --- | --- |
| selected_owner | yes |
| matched_condition | yes |
| collision_rule | required when multiple predicates match |
| disqualified_owners | yes |
| evidence | yes |
| source_state | yes |
| source_artifacts | yes |
| handoff_used | yes |
| handoff_ignored_reason | required when handoff exists but is not used |
| decided_at | yes |

## HANDOFF freshness predicate

| Predicate | Rule |
| --- | --- |
| `handoff_fresh` | required fields present AND `updated_at >= last owning mutation` AND `from_owner` matches prior owner AND to_owner allowed by pipeline AND reason/status consistent with artifacts |

Handoff hygiene:
- stale or invalid handoff data is ignored and recorded in `route_decision.handoff_ignored_reason` when it affects owner selection
- a fresh valid handoff may surface resume context before mutation
- handoff data never overrides fresher live artifacts, approval records, or locked contract surfaces
- do not introduce duplicate state or handoff trees; `.beads/STATE.json` and `.beads/HANDOFF.json` remain canonical

## HANDOFF.json schema

| Field | Required | Rule |
| --- | --- | --- |
| `schema_version` | yes | current handoff schema version |
| `from_owner` | yes | owner writing the handoff |
| `to_owner` | yes | target owner allowed by `beo-references -> pipeline.md` |
| `feature_slug` | yes when a feature is active | current feature slug |
| `status` | yes | state summary at handoff time |
| `reason` | yes | why the handoff is required |
| `artifact_refs` | yes | relevant artifact paths or refs |
| `last_owning_mutation` | yes | timestamp of the last mutation by `from_owner` |
| `updated_at` | yes | handoff write timestamp |
| `resume_instructions` | yes | minimal next-step instructions |

## Transition types

Use exactly one of these models when ownership changes:
- `inline transition`: owner changes inside the same live session or reasoning chain; update `STATE.json` only
- `persisted handoff`: progress must survive a pause, checkpoint, external wait, or transfer; write `HANDOFF.json`
- `handoff forbidden`: do not write `HANDOFF.json` for routine next-owner routing that can continue immediately from live artifacts in the same session

## HANDOFF write criteria

| Situation | Write HANDOFF? | Required evidence | Next owner |
| --- | --- | --- | --- |
| user clarification blocks the current owner | yes | blocking question, current artifact path, last safe state | user |
| owner transfer cannot continue in the same session | yes | from_owner, to_owner, reason, completed evidence, expected return condition | target owner |
| external blocker prevents safe progress | yes | blocker, attempted command or artifact, last safe state | user or beo-debug |
| local completion can continue immediately to next owner | no | update `STATE.json` route/status evidence instead | next owner |
| routine same-session owner transition | no | inline transition only; `HANDOFF.json` is forbidden | next owner |
| terminal done with no resume need | no | terminal evidence in `STATE.json` or owning artifact | done |

## State freshness and stale-field rule

`STATE.json` is a live coordination surface, not an archive.
- A field is stale when its governing artifact, approval, owner decision, or blocker basis is no longer current.
- Owners must not rely on stale optional fields when fresher live artifacts disagree.
- When a stale optional field could mislead the next owner, clear it in the same write that records the superseding evidence.
- If a field is preserved across owner changes, the current owner is responsible for confirming it still matches live artifacts rather than copying it forward on trust.
- If a field no longer affects the current owner or the immediate next owner, clear it.

## Stale field cleanup quick rule

When writing STATE:
1. keep only fields still live for the current owner decision
2. clear validation fields when the execution envelope changes
3. clear `approval_ref` when approval invalidates
4. clear `debug_return` and `debug_result` after the return is consumed
5. clear `route_decision` after fresher evidence selects owner
6. record cleared fields in `evidence.cleared_fields`

## Go-mode ownership

- Only explicit user authorization in the current task or fresh handoff may create `go_mode`.
- No skill may infer `go_mode` from silence, approval, prior successful execution, or route confidence.
- `go_mode` must include `authorized_by`, `authorized_at`, `scope`, and `expires_on_owner_exit=true`.
- `go_mode` applies only to non-blocking clarification.
- `go_mode` expires when owner changes, feature scope changes, or approval is invalidated.
- `go_mode` never bypasses approval, file scope, P0/P1 review findings, or security/privacy constraints.

## Debug return metadata

`debug_return` is a single object stored in `STATE.json`.

| Field | Rule |
| --- | --- |
| `origin_skill` | written once by skill handing to debug; immutable during debug |
| `return_to` | written once by skill handing to debug; immutable during debug unless override evidence proves it invalid |
| `return_reason` | required summary of why debug should return there |
| `blocker_id` | required blocker identifier when available |
| `override` | boolean; true only when debug changes `return_to` |
| `override_evidence` | required when `override=true` |
| `approval_stale` | boolean when approval freshness is relevant |

## Terminal done rule

Use `done` only when all are true:
- no owner action remains legally required
- no unresolved blocker remains
- no stale handoff is being trusted
- no pending readiness, approval, execution, review, or learning disposition remains
- latest evidence packet explains why the workflow is terminal

`done` is not a substitute for `user` when external clarification, access, approval, or owner selection is required.
