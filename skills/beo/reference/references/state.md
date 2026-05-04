## Contents

- Single-feature invariant
- Worktree and branch-switch rule
- State surfaces
- STATE.json shape
- Minimal STATE.json schema
- Operator view
- STATUS vocabulary
- user_reason enum
- done_reason enum
- Operational write discipline
- STATE write precedence matrix
- STATE field groups
- Owner handoff clearing rule
- Shared decision packet
- route_decision schema

# State

## Single-feature invariant

BEO operates on one active feature per worktree.
`.beads/STATE.json` and `.beads/HANDOFF.json` are global surfaces — they bind to exactly one `feature_slug` at a time.
Working on multiple features simultaneously in the same worktree produces undefined state.
When a new feature is started, the prior feature's state must be closed or explicitly deferred before setting a new `feature_slug`.

## Worktree and branch-switch rule

`.beads/` is not version-controlled. Its contents are worktree-local and branch-unaware:
- Switching git branches does not switch state; the same `.beads/STATE.json` persists.
- After any branch switch, run the startup check (`beo-onboard`) and re-read canonical artifacts before any beo action.
- If `PLAN.md`, `CONTEXT.md`, or `approval-record.json` do not match the current branch checkout, treat `.beads/STATE.json` as stale and route to `beo-route`.
- Never assume the `.beads/` state reflects the artifact state of the current branch.

## State surfaces

| Surface | Rule |
| --- | --- |
| `.beads/STATE.json` | live owner, status, evidence, route decision, current phase |
| `.beads/HANDOFF.json` | real checkpoint/resume only |

Execution approval requires a valid approval record and matching `STATE.json.approval_ref`; the `approved` label is an advisory bead marker.

## STATE.json shape

Operational state fields:
- `schema_version`
- `operator_view`
- `current_owner`
- `status`
- `evidence`
- `route_decision`
- `feature_slug`
- `current_phase`
- `readiness`
- `execution_mode`
- `execution_set_id`
- `execution_set_beads`
- `partial_progress_allowed`
- `remediation_owner`
- `approval_ref`
- `go_mode`
- `debug_return`
- `debug_result`
- `updated_at`
- `state_seq` — advisory monotonic write counter; increment on every STATE.json write; enables ordering of concurrent writes and crash-recovery detection; omit on first write if not yet initialized
- `last_git_ref` — advisory string capturing `<branch>@<short-sha>` at the time of the last STATE.json write; used by the worktree and branch-switch rule to detect state invalidation on branch switch

## Minimal STATE.json schema

The canonical live shape is:

```json
{
  "schema_version": "<version>",
  "operator_view": {
    "feature": "<feature-or-null>",
    "current_owner": "<owner>",
    "why_here": "<human-readable reason>",
    "next_expected_owner": "<owner-or-null>",
    "blocked": false,
    "human_action_needed": null,
    "last_decision": "<latest owner decision>"
  },
  "current_owner": "<owner>",
  "status": "<status>",
  "feature_slug": "<feature-or-null>",
  "current_phase": "<phase-or-null>",
  "approval_ref": "<approval-record-path-or-null>",
  "readiness": "<readiness-or-null>",
  "execution_mode": "<single|ordered_batch|local_parallel|null>",
  "execution_set_id": "<set-id-or-null>",
  "execution_set_beads": ["<bead-id>"],
  "partial_progress_allowed": false,
  "route_decision": {},
  "evidence": {},
  "updated_at": "<iso-8601>"
}
```

Required at all times after route normalization:
- `schema_version`
- `operator_view` — optional when `status=done` and no active feature remains; required otherwise
- `current_owner`
- `status`
- `evidence`
- `updated_at`

Required when applicable:
- `feature_slug` when a feature is active
- `current_phase` when phase-scoped planning or execution exists — derives from the active `PLAN.md` `## Current Phase Contract` section; if no such section exists, `current_phase` is absent; update together with PLAN.md when the phase changes
- `approval_ref` when execution approval exists
  - `readiness`, `execution_mode` (mirrors the selected `execution_set`'s mode), `execution_set_id`, `execution_set_beads`, and `remediation_owner` only when validation evidence is current
  - `partial_progress_allowed` when `readiness=PASS_EXECUTE` and `execution_mode` is `ordered_batch` or `local_parallel`; default `false` otherwise; absent, null, missing, or stale values are treated as `false`; authorizes whether `beo-execute` may continue unaffected beads after one bead blocks
  - `execution_set_id` is assigned by `beo-validate` at `PASS_EXECUTE`; use a stable slug (e.g., joined bead ids or a reviewer-assigned label); no derivation after the fact
  - `remediation_owner` is written by `beo-validate` on `FAIL_PLAN` or `FAIL_EXPLORE` to name the required remediation owner; consumed by `beo-route` when selecting the remediation path
- `route_decision` only when route evidence is relevant to the current owner selection
- `go_mode` only while the authorized feature scope, approval/assumption constraints, and handoff-persistence conditions remain valid
- `debug_return` and `debug_result` only while debug state is active or immediately relevant to the return path

## Operator view

`operator_view` is a human-readable mirror inside `.beads/STATE.json`.
It is not a separate source of truth. If `operator_view` conflicts with canonical
fields, canonical fields win.

Required fields:
- `feature`
- `current_owner`
- `why_here`
- `next_expected_owner`
- `blocked`
- `human_action_needed`
- `last_decision`

Do not create or manually maintain `.beads/STATE.md`.
A markdown narrative may be generated by tooling, but `.beads/STATE.json`
remains canonical.

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
- `review_ready`
- `accepted`
- `fix_required`
- `rejected`
- `learning_pending`
- `done`

Owners may include additional nuance in `evidence`, but `status` MUST stay inside this vocabulary unless a shared reference is updated first.

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
- `deferred_by_user` — operator intentionally paused active work and may reactivate later
- `canceled_by_user` — operator explicitly canceled active work before completion

## Operational write discipline

| Rule | Requirement |
| --- | --- |
| read precedence | owners read canonical operational fields first; `operator_view` is for orientation only |
| timestamp discipline | every state write refreshes `updated_at` from live write time |
| minimality | owners must not keep stale optional fields or stale `operator_view` claims alive once the owning condition is no longer true |
| monotonic sequence discipline | `state_seq` increments on every `STATE.json` write; `handoff_seq` increments on every `HANDOFF.json` write; `approval_seq` increments on every `approval-record.json` write; `bundle_seq` increments on every `execution-bundle.json` write; the highest seq for a given surface is the most recent; lower-seq versions are superseded |

## STATE write precedence matrix

When multiple writes to `STATE.json` or related surfaces exist or conflict, resolve using this order:

| Priority | Source | Rule |
| --- | --- | --- |
| 1st | Live canonical artifacts (`CONTEXT.md`, `PLAN.md`, `approval-record.json`, `readiness-record.json`, `execution-bundle.json`) | Ground truth; override any `STATE.json` or `HANDOFF.json` claim that contradicts them. `readiness-record.json` is canonical for validation decision facts including readiness verdict, selected execution set, execution mode, approval reference used for the verdict, and `partial_progress_allowed`. |
| 2nd | `STATE.json` canonical operational fields (`current_owner`, `status`, `feature_slug`, `approval_ref`, `readiness`, `execution_mode`, `execution_set_id`, `execution_set_beads`, `partial_progress_allowed`) | Take precedence over `operator_view` and `HANDOFF.json`; mirrored approval/readiness fields defer to the live approval and readiness records when they conflict |
| 3rd | `HANDOFF.json` when fresh | Advisory resume context; may not override fresher live artifacts |
| 4th | `operator_view` | Display surface; advisory only; never canonical |
| 5th | Scout/status output | Advisory/display; cannot authorize execution, routing, or approval |

When two `STATE.json` writes appear concurrent or their ordering is ambiguous, the write with the higher `state_seq` is the authoritative one. The write with the lower `state_seq` is superseded and its fields must not be used for routing or mutation decisions.

For duplicated readiness mirrors, disagreement is not resolved by choosing the
more permissive value. Consumers must use the safer interpretation and route to
the owning classifier/writer for repair.

## Authority map

| Field / concept | Canonical writer | Canonical reader | Co-surface requirement | Not authoritative |
| --- | --- | --- | --- | --- |
| `current_owner` | `beo-route` or current owner per state doctrine | all owners | must match live artifact evidence | `operator_view`, scout/status output |
| `approval_ref` | `beo-validate` | `beo-execute`, `beo-review`, resume flows | required for every `PASS_EXECUTE`, including unchanged approval | display card |
| `execution_set_id` | `beo-validate` | `beo-execute` | must match `STATE.json` and `readiness-record.json` | ad-hoc bead choice |
| `execution_set_beads` | `beo-validate` | `beo-execute` | selected set only; must match readiness record | convenient ready beads |
| `execution_set_mode` / `execution_mode` | `beo-validate` | `beo-execute`, `beo-review` | readiness record and state mirror must agree for `PASS_EXECUTE` | display alias `mode` |
| `partial_progress_allowed` | `beo-validate` | `beo-execute` | explicit `true` required in both `STATE.json` and `readiness-record.json`; otherwise false | Execution Set Card only |
| `aggregate_changed_files` | `beo-execute` | `beo-review` | review must compare with live diff and recorded pre-existing dirty paths | self-reported `scope_respected` alone |
| `dirty_baseline` | `beo-execute` | `beo-review` | stored in `execution-bundle.json` before mutation | `HANDOFF.json.dirty_state` alone |
| `finalized_at` / `changed_file_hashes` | `beo-execute` | `beo-review` | required when `ready_for_review=true`; finalized bundle is immutable | later worktree state alone |
| `operator_view` | current state-writing owner | human operator only | should mirror canonical fields or be replaced/omitted | routing, approval, readiness, verdict authority |
| `debug_return.return_to` | owner routing to `beo-debug` | `beo-debug`, receiving owner | must name one legal return owner and remain consistent with live artifacts | origin-owner habit |
| feature lifecycle state | owner closing, deferring, canceling, or reactivating the feature | route, onboard, all runtime owners | active only when `STATE.json.feature_slug` or fresh `HANDOFF.json` points to the directory | historical artifact directory alone |
| `STATE.json.status=needs_onboarding` | `beo-onboard` only | startup flow, `beo-route` | allowed only when managed startup freshness is false, missing, or stale | onboarding script-local `status` field |
| `readiness` / `PASS_EXECUTE` | `beo-validate` | `beo-execute`, `beo-review` | must be backed by readiness record and current approval envelope | status card |
| terminal verdict | `beo-review` | closure owners, `done` | must be recorded in `REVIEW.md` | specialist evidence or verdict card alone |

## STATE field groups

| Group | Fields | Keep when | Clear when |
| --- | --- | --- | --- |
| owner | `current_owner`, `status`, `evidence`, `updated_at` | always live | replaced by newer owner evidence |
| operator | `operator_view` | always present after route normalization | repair when owner changes, feature changes, or last decision/next owner narrative becomes stale |
| feature | `feature_slug`, `current_phase` | active feature remains the same | feature changes or no active feature |
| route | `route_decision` | it still explains current owner selection | reroute happens or owner no longer depends on it |
| validation | `readiness`, `execution_mode`, `execution_set_id`, `execution_set_beads`, `partial_progress_allowed`, `remediation_owner`, `approval_ref` | approval and readiness still match the live execution envelope | plan, scope, verification, mode, or approval changes |
| go | `go_mode` | same authorized feature scope still applies and approval/assumption constraints remain valid | feature changes, scope changes, approval invalidates, or explicit go-mode revocation occurs |
| debug | `debug_return`, `debug_result` | debug handoff is active or result is not yet consumed | receiving owner consumes result or return path invalidates |

## Owner handoff clearing rule

On owner change, preserve only fields still valid for the next owner's live decision. Clear optional fields that describe a completed, invalidated, or superseded state rather than copying them forward by habit. When `operator_view` is preserved, the current owner is responsible for keeping it aligned with canonical owner, feature, and next-owner facts.

## Feature abandonment and reactivation

To defer, cancel, or close a feature:
1. set `status=done` and write `done_reason=deferred_by_user`, `canceled_by_user`, or the applicable terminal reason;
2. clear approval/readiness mirrors (`approval_ref`, `readiness`, `execution_mode`, `execution_set_id`, `execution_set_beads`, `partial_progress_allowed`);
3. clear or replace `current_owner` so no runtime owner remains active for that feature;
4. leave the artifact directory historical and evidence-only.

Reactivation requires setting `STATE.json.feature_slug` back to the historical slug, re-reading current artifacts, and routing through the normal owner/approval/readiness gates. Historical artifacts alone do not authorize mutation.

## Shared decision packet

See `beo-reference -> skill-contract-common.md` for the canonical base packet field list and usage rules.

State-specific additions:
- When `next_owner=user`, include `user_reason` (see user_reason enum above).
- When `next_owner=done`, include `done_reason` (see done_reason enum above).
- Do not write long narrative summaries into `STATE.json`; keep state limited to routing-safe facts plus the short human-readable `operator_view`, and place durable rationale in the owning artifact. Narrative audit data (e.g., `skills_upgraded`, `files_written`, `beo_dream_changes`) belongs in feature artifact evidence, not in `STATE.json.evidence`.

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
| `handoff_fresh` | required fields present AND `updated_at >= last owning mutation` AND `created_by_owner` matches prior owner AND `intended_resume_owner` is allowed by pipeline AND resume evidence is consistent with artifacts |

Definition: "last owning mutation" means the `updated_at` of `STATE.json` as recorded by the creating owner immediately before writing this handoff. Include this value as `freshness_checks.state_updated_at` in the handoff's `freshness_checks` object so the freshness comparison is deterministic.

Handoff hygiene:
- stale or invalid handoff data is ignored and recorded in `route_decision.handoff_ignored_reason` when it affects owner selection
- a fresh valid handoff may surface resume context before mutation
- handoff data never overrides fresher live artifacts, approval records, or locked contract surfaces
- do not introduce duplicate state or handoff trees; `.beads/STATE.json` and `.beads/HANDOFF.json` remain canonical
- stale or invalid handoff data never authorizes auto-resume, approval, or owner selection when live artifacts disagree

## HANDOFF.json schema

| Field | Required | Rule |
| --- | --- | --- |
| `schema_version` | yes | current handoff schema version |
| `created_by_owner` | yes | owner writing the handoff |
| `intended_resume_owner` | yes | target owner allowed by `beo-reference -> pipeline.md` |
| `feature_slug` | yes when a feature is active | current feature slug |
| `approval_ref` | yes when approval is current | approval surface tied to the paused execution/review state |
| `execution_set_id` | yes when execution selection exists | id of the selected execution set |
| `execution_set_beads` | yes when execution selection exists | ordered bead ids of the selected execution set (order is execution sequence for `ordered_batch`) |
| `changed_files` | yes | changed files already observed at checkpoint time |
| `verification` | yes | verification status/evidence already collected |
| `blockers` | yes | active blockers at checkpoint time |
| `dirty_state` | yes | in-scope vs out-of-scope dirty paths at checkpoint time |
| `freshness_checks` | yes | state/artifact hashes or refs used to decide resume freshness |
| `updated_at` | yes | handoff write timestamp |
| `handoff_seq` | no | advisory monotonic write counter for `HANDOFF.json`; increment on every write; enables ordering when multiple handoffs are written in sequence |
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
| owner transfer cannot continue in the same session | yes | `created_by_owner`, `intended_resume_owner`, reason, completed evidence, expected return condition | target owner |
| external blocker prevents safe progress | yes | blocker, attempted command or artifact, last safe state | user or beo-debug |
| context budget is high before mutation, owner transfer, or terminal review | yes | current owner, feature, approval, selected bead(s), changed files, verification, blockers, next legal owner | target owner or user |
| local completion can continue immediately to next owner | no | update `STATE.json` route/status evidence instead | next owner |
| routine same-session owner transition | no | inline transition only; `HANDOFF.json` is forbidden | next owner |
| terminal done with no resume need | no | terminal evidence in `STATE.json` or owning artifact | done |

## State freshness and stale-field rule

`STATE.json` is a live coordination surface, not an archive.
- A field is stale when its governing artifact, approval, owner decision, or blocker basis is no longer current.
- Owners must not rely on stale optional fields when fresher live artifacts disagree.
- When a stale optional field could mislead the next owner, clear it in the same write that records the superseding evidence.
- When `operator_view` could mislead the next owner, repair or clear it in the same write that records the superseding evidence.
- If a field is preserved across owner changes, the current owner is responsible for confirming it still matches live artifacts rather than copying it forward on trust.
- If a field no longer affects the current owner or the immediate next owner, clear it.

## Stale field cleanup quick rule

When writing STATE:
1. keep only fields still live for the current owner decision
2. clear validation fields when the execution envelope changes
3. clear `approval_ref` when approval invalidates
4. clear `debug_return` and `debug_result` after the return is consumed
5. clear `route_decision` after fresher evidence selects owner
6. repair or clear stale `operator_view` claims in the same write
7. record cleared fields in `evidence.cleared_fields`

## Go-mode ownership

- Only explicit user authorization in the current task or fresh handoff may create `go_mode`.
- No skill may infer `go_mode` from silence, approval, prior successful execution, or route confidence.
- `go_mode` must include `active`, `authorized_by`, `authorized_at`, `feature_slug`, `operator_assumption`, `last_gate_passed`, `next_gate`, `human_action_needed`, `scope`, and `persists_across_owner_handoffs=true`.
- `go_mode` applies only to non-blocking clarification and conservative implementation-detail assumptions.
- `go_mode` may persist across legal owner handoffs within the same authorized feature scope.
- Clear `go_mode` when feature slug changes, user authorization changes, CONTEXT contradiction appears, approval envelope changes, handoff is stale or invalid, external access/secret/legal decision is needed, or the recorded operator assumption is no longer safe.
- `go_mode` never bypasses approval, file scope, P0/P1 review findings, or security/privacy constraints.
- `go_mode` is an operator macro, not an owner.

## Context budget handoff

Context pressure means the live session may no longer reliably preserve the
current owner decision, approval envelope, blockers, or next legal action through
continued work or compaction.

## Context pressure and resume rule

When context pressure threatens reliable continuation, or a compaction/resume
boundary is expected, preserve only the state needed to resume safely.

Write `HANDOFF.json` only when one of these is true:
- pause/resume must survive beyond the live session
- external wait is required
- owner transfer must survive beyond live context
- compaction would otherwise lose blocker, approval, or next-action evidence

Do not write `HANDOFF.json` for routine same-session owner transitions.

## HANDOFF minimum fields

When writing a persisted handoff, use all required fields in the HANDOFF.json schema above. The schema table is the authoritative field list; the former bullet-list summary is superseded by it. Pay particular attention to `freshness_checks.state_updated_at` (required for deterministic freshness evaluation) and `execution_set_id`/`execution_set_beads` (required when execution selection exists).

## Post-compaction / resume recovery

Before mutating after compaction or resumed handoff:
1. Run onboarding/scout when available.
2. Re-open canonical `STATE.json`.
3. Re-open `HANDOFF.json` when present.
4. Re-open active `CONTEXT.md`.
5. Re-open active `PLAN.md` when planning or later.
6. Re-check approval reference before execution.
7. Route from live artifacts if handoff is stale, contradictory, or incomplete.

If context budget is high before mutation, owner transfer, external wait, or
terminal review:
- write `.beads/HANDOFF.json`
- include current owner, feature slug, approval ref, selected bead(s), changed files,
  verification status, blockers, and next legal owner
- update `.beads/STATE.json.operator_view`
- stop before unsafe continuation

After compaction or resume:
1. run live onboarding check or scout as allowed by shared hard gates
2. read `.beads/STATE.json`
3. inspect `.beads/HANDOFF.json` if present
4. verify handoff freshness against live artifacts
5. route through `beo-route` when owner is stale, missing, or contradictory

Do not write `.beads/HANDOFF.json` merely because routine same-session routing
continues from fresh canonical artifacts.

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

## Canonical JSON atomic write and corruption recovery

To avoid partial-write corruption of canonical JSON surfaces (`STATE.json`, `HANDOFF.json`, `approval-record.json`, `readiness-record.json`, and `execution-bundle.json`):
- Write changes to a sibling temporary file first (for example, `<name>.tmp`), then atomically rename to the canonical path.
- Every `STATE.json` write must refresh `updated_at` from the live write timestamp.
- If both a canonical file and its temp file exist, use the readable canonical file when its sequence/timestamp is at least as recent; otherwise route to `user` with tmp-collision evidence before trusting either surface.
- If only a temp file exists, treat the canonical write as interrupted and route by the last readable canonical surface plus tmp evidence; do not promote the temp file silently.

Corruption recovery path:
- If a canonical JSON surface is unreadable or contains invalid JSON, treat it as corrupt.
- Read `HANDOFF.json` as the recovery source; record corruption evidence in STATE evidence on recovery.
- If both `STATE.json` and `HANDOFF.json` are unreadable, route to `beo-onboard`.
- Do not use partial, temp, or corrupt JSON fields as canonical routing evidence.
