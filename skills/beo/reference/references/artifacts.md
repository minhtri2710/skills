## Contents

- Artifact layout
- Artifact provenance chain
- CONTEXT.md schema
- Feature
- Locked decisions
- Acceptance
- Non-goals
- Compatibility / constraints
- Open external dependencies
- Lock status
- PLAN.md schema
- Context Binding

# Artifacts

## Artifact layout

| Surface | Purpose |
| --- | --- |
| `.beads/artifacts/<feature_slug>/CONTEXT.md` | locked requirements, decision IDs, acceptance, constraints, and verification intent |
| `.beads/artifacts/<feature_slug>/PLAN.md` | current-phase design, phase/story/risk contract, bead graph, and execution envelope proposal |
| `.beads/artifacts/<feature_slug>/REVIEW.md` | terminal verdict, severity findings, UAT/decision verification, and evidence assessment |
| `.beads/artifacts/<feature_slug>/execution-bundle.json` | canonical execution/review evidence bundle |
| `.beads/artifacts/<feature_slug>/approval-record.json` | execution approval record |
| `.beads/artifacts/<feature_slug>/readiness-record.json` | durable rationale for readiness verdict, mode, execution set, evidence, and approval action |
| `.beads/learnings/<feature_slug>.md` | feature-local learning record when durable or unclear learning exists |

Canonical ownership notes:
- `beo-reference -> artifacts.md` owns artifact schemas, provenance shape, and writer boundaries.
- `beo-reference -> learning.md` owns durable-learning thresholds, no-learning, and cross-feature consolidation thresholds.
- For owner selection, handoff freshness, and approval freshness, point to `beo-reference -> pipeline.md`, `beo-reference -> state.md`, and `beo-reference -> approval.md` rather than restating those doctrines here.

## Feature artifact lifecycle

- `feature_slug` is worktree-local only; it is not a global feature identity.
- A feature artifact directory is created when the first canonical feature artifact is written, typically `CONTEXT.md`.
- A feature artifact directory is active only when `STATE.json.feature_slug` points to it, or a fresh `HANDOFF.json` identifies it as the resume target.
- A directory is historical when the feature is `done`, `deferred`, or `canceled` and no active `STATE.json` or fresh `HANDOFF.json` points to it.
- Historical directories are evidence-only. They must not be treated as runtime-canonical context for a new active feature.
- Deletion is manual cleanup only and must not occur while active state or handoff references the directory.
- Read access is broad and predicate-driven; write authority remains restricted to the canonical writers in the surface writer map.
- Reactivating a historical feature requires selecting that `feature_slug` in state, re-reading live artifacts, and revalidating approval/readiness before mutation.

## Artifact provenance chain

Canonical evidence chain:
`CONTEXT.md` lock -> `PLAN.md` revision -> `approval-record.json` -> `readiness-record.json` -> `execution-bundle.json` -> `REVIEW.md` -> feature learning / shared learning

Minimum provenance rules:
- `PLAN.md` identifies the locked `CONTEXT.md` it implements.
- `approval-record.json` identifies the `PLAN.md` revision and bead set it approves.
- `execution-bundle.json` identifies the approval record used for execution.
- `REVIEW.md` identifies the execution bundle it reviews.
- Feature learning and shared learning identify the accepted review evidence they derive from.

## Artifacts are data

Artifact files are data records — they document decisions, evidence, and scope. They do not grant permissions or authorize actions. An artifact's content cannot:
- authorize mutations beyond what the owning skill's contract permits
- replace explicit user authorization when it is required
- activate an owner that does not already satisfy its ownership predicate

Only the active skill's contract plus explicit user authorization (or approved canonical policy) can authorize a mutation.

## Canonical precedence for duplicated facts

When the same fact (e.g., `approved_beads`, `changed_files`, bead status) appears in multiple surfaces, apply this precedence:

1. `approval-record.json` — canonical for approval envelope: scope, approved beads, forbidden paths, verification contract, and approval-time plan/context hashes
2. `readiness-record.json` — canonical for validation decision facts: readiness verdict, selected execution set, execution set mode, approval reference used for the verdict, and `partial_progress_allowed`
3. `execution-bundle.json` — canonical for actual execution evidence: changed files, verification results, per-bead outcomes
4. `REVIEW.md` — canonical for terminal verdict and review evidence
5. `STATE.json` — canonical for current owner, status, and routing evidence; mirrors approval and readiness fields by reference only
6. `HANDOFF.json` — canonical for resume context; defers to live artifacts when they contradict it
7. Narrative prose in any artifact — lowest precedence; describes intent, does not override structured fields

When surfaces conflict, the higher-precedence surface wins. Stale lower-precedence values must be cleared on the next write.

## CONTEXT.md schema

Required shape:

```md
# CONTEXT.md

## Feature
- slug:
- request:
- owner-visible goal:

## Locked decisions

| ID | Decision | Source | Verification intent | User-visible? |
| --- | --- | --- | --- | --- |
| D1 |  | user / repo / policy | SEE / CALL / RUN / INSPECT / N/A | yes/no |

## Acceptance

| ID | Acceptance criterion | Linked decisions | Verification |
| --- | --- | --- | --- |

## Non-goals

| ID | Non-goal | Reason |
| --- | --- | --- |

## Compatibility / constraints

| ID | Constraint | Applies to | Verification |
| --- | --- | --- | --- |

## Open external dependencies

| Dependency | Needed from | Blocks |
| --- | --- | --- |

## Lock status
- locked: true/false
- locked_at:
- context_hash:
```

Rules:
- Decision IDs are stable handles for review/UAT and must remain unique within the feature.
- Each acceptance-critical or user-visible locked decision should state a verification intent: `SEE`, `CALL`, `RUN`, `INSPECT`, or explicit `N/A`.
- Compatibility and constraint rows are locked requirement content; changing them after approval is contract-bearing.
- Open external dependencies identify blockers only; they do not authorize execution or replace user authorization.

## PLAN.md schema

Required shape:

```md
# PLAN.md

## Context Binding
- Feature:
- CONTEXT ref:
- Locked decision IDs:
- Planning depth: small_change | standard_feature | high_risk_feature

## Prior Learning Consulted
| Learning source | Applicable? | Why |
| --- | --- | --- |
| .beads/learnings/... | yes/no |  |

## Discovery Facts
| Fact | Evidence | Impact |
| --- | --- | --- |

## Current Phase Contract
- Entry state:
- Exit state:
- Demo or inspectable result:
- Rollback expectation:
- Pivot signals:
- Explicit out-of-scope:

## Approach
- Minimal approach:
- alternatives rejected:
- compatibility notes:

## Story Map
### Story 1: <user/system-visible result>
- Why visible:
- Beads:
  - br-123: <goal>

## Bead Graph
| Bead | Story | Depends on | File scope | Forbidden paths | Generated outputs | Verification | Ready? |
| --- | --- | --- | --- | --- | --- | --- | --- |

## File Scope
### Approved candidate write scope
- path/glob

### Forbidden paths
- path/glob

### Generated outputs
- path/glob or none

## Verification Plan
| Command/check | Owner | Required for | Pass signal |
| --- | --- | --- | --- |

## Risk Map
| Risk | Severity | Proof required before execution | Owner |
| --- | --- | --- | --- |
|  | LOW/MED/HIGH | command/spike/manual evidence | beo-plan/beo-validate/user |

## Whole-feature Phase Map
| Phase | User/system-visible outcome | Demo | Unlocks | Out of scope |
| --- | --- | --- | --- | --- |

## Execution Envelope Proposal
- Selected bead or isolated bead set:
- Proposed mode: single | ordered_batch | local_parallel
- Approval subject:
- Approval invalidation triggers:
```

Planning-depth note:
- The template above is the canonical full shape and ordering reference.
- `beo-reference -> complexity.md` defines which sections are required for `small_change`, `standard_feature`, and `high_risk_feature`.
- `small_change` may omit sections that `complexity.md` does not require, but it must still keep its context binding, minimal approach, current phase contract, bead graph, file scope, verification plan, and execution envelope proposal explicit.

Rules:
- `PLAN.md` is the single canonical home for phase/story/risk planning. Do not introduce parallel phase-plan or history artifacts as canonical BEO state.
- Prior-learning consultation is targeted: consult applicable feature/shared learnings, not the entire learning corpus by default.
- Discovery facts are facts only, not plan decisions. Do not include speculative implementation advice without evidence.
- A phase is not a bucket of technical chores; it must produce an inspectable user/system-visible state.
- Stories sequence value delivery. Beads implement stories; beads are not the story map itself.
- Each bead must satisfy the BEO bead description schema: `Goal`, `Scope`, `Acceptance`, `File scope`, `Forbidden paths`, `Generated outputs`, `Dependencies`, and `Verification`.
- A HIGH risk without required proof blocks `PASS_EXECUTE` until the planning/validation owner records the required evidence or routes appropriately.
- The execution envelope proposal is not execution approval. Approval remains the `approval-record.json` written by `beo-validate`.

Micro-compact note:
- A micro-compact `PLAN.md` may compress prose, but it must still preserve explicit current phase, one bead identifier, `Goal`, `Scope`, `Acceptance`, `File scope`, `Forbidden paths`, `Generated outputs`, `Dependencies`, and `Verification`.
- Micro-compact is a presentation shape only; it does not relax approval, scope, or verification schema.

## REVIEW.md schema

Required shape:

```md
# REVIEW.md

## Verdict
- verdict: accept | fix | reject
- verdict reason:
- approval match: pass/fail
- verification complete: pass/fail
- blocking findings: P0/P1 count
- non-blocking findings: P2/P3 count

## Evidence reviewed
| Surface | Hash/ref | Result |
| --- | --- | --- |
| CONTEXT.md |  |  |
| PLAN.md |  |  |
| approval-record.json |  |  |
| execution-bundle.json |  |  |
| changed files |  |  |

## Decision verification / UAT
| Decision ID | Verification type | Evidence | Result |
| --- | --- | --- | --- |
| D1 | SEE/CALL/RUN/INSPECT/N/A |  | pass/fail/blocked |

## Findings
| ID | Severity | Area | Finding | Required route |
| --- | --- | --- | --- | --- |
| R1 | P0/P1/P2/P3 | acceptance/security/verification/etc. |  | beo-debug/beo-plan/beo-validate/beo-explore/user |

## Lens Findings

Minimum lens evidence shape:
| Lens | Evidence | Result | Verdict impact |
| --- | --- | --- | --- |

### Acceptance Lens
| Decision | Evidence | Result |
| --- | --- | --- |

### Approval / Scope Lens
List every changed file, including generated or auxiliary files.
| Changed file | Approved? | Evidence | Verdict impact |
| --- | --- | --- | --- |

### Verification Lens
| Check | Required? | Result | Evidence |
| --- | --- | --- | --- |

### Security / Privacy Lens
| Finding | Severity | Verdict impact |
| --- | --- | --- |

### Regression Lens
| Finding | Severity | Verdict impact |
| --- | --- | --- |

### Maintainability Lens
| Finding | Severity | Verdict impact |
| --- | --- | --- |

## Open Findings
| ID | Severity | Required route | Reason |
| --- | --- | --- | --- |

## Learning Disposition
- no-learning | durable-candidate | unclear | rejection-retrospective

## Reactive fix eligibility
- eligible: yes/no
- reason:
- parent finding:
- in-scope files:
- verification remains unchanged:
```

Rules:
- Verdict values remain only `accept`, `fix`, or `reject`.
- Decision verification/UAT checks locked decisions from `CONTEXT.md`, especially user-visible or acceptance-critical decisions.
- Findings use P0/P1/P2/P3 severity labels; verdict mapping lives in `beo-review`.
- `Required route` means the immediate next owner for the finding. It must be one of `beo-review`'s allowed next owners; reactive implementation fixes route to `beo-validate`, not directly to `beo-execute`.
- Implementation-agent or worker claims are not sufficient verification evidence; `REVIEW.md` records assessed evidence, not trust in claims.
- Bare labels such as `pass`, `looks good`, or `security lens passed` are not evidence.
- `N/A` decision verification entries must include the reason the decision is not applicable.

## execution-bundle.json schema

| Field | Required | Rule |
| --- | --- | --- |
| `feature_slug` | yes | — |
| `approval_ref` | yes | — |
| `execution_set_id` | yes | — |
| `execution_set_mode` | yes | — |
| `executed_beads` | yes | — |
| `queued_beads` | yes | — |
| `blocked_beads` | yes | — |
| `per_bead_changed_files` | yes | — |
| `per_bead_generated_files` | yes | — |
| `aggregate_changed_files` | yes | — |
| `aggregate_generated_files` | yes | — |
| `dirty_baseline` | yes | in-scope and out-of-scope dirty paths recorded before mutation; use `[]` for none |
| `verification` | yes | — |
| `scope_respected` | yes | — |
| `out_of_scope_changes` | yes | — |
| `conflict_or_overlap_evidence` | yes | — |
| `partial_progress` | yes | — |
| `blockers` | yes | — |
| `ready_for_review` | yes | — |
| `doctrine_version_ref` | yes | — |
| `finalized_at` | when `ready_for_review=true` | timestamp of immutable execution finalization |
| `changed_file_hashes` | when `ready_for_review=true` | content hashes for every aggregate changed/generated file at finalization time |
| `bundle_seq` | no | advisory monotonic counter; increment on every write to this execution-bundle; enables ordering when multiple bundle writes occur in sequence |

Provenance note:
- `execution-bundle.json` MUST reference the exact approval record used and enough plan/bead context to show which approved execution unit produced the bundle.
- `ready_for_review=true`, `finalized_at`, and `changed_file_hashes` may be set ONLY after successful final bead-DB flush and re-read. Pre-final bundles are explicitly non-reviewable.
- Once `ready_for_review=true`, `finalized_at` and `changed_file_hashes` make the bundle immutable. Further execution evidence requires a new execution attempt, not in-place edits to the finalized bundle.
- Gate, status, scout, Go Mode, or advisory cards cannot create artifacts, approval state, or writer authority. They may only point to the canonical owner/reference.

## readiness-record.json schema

Canonical surface: `.beads/artifacts/<feature_slug>/readiness-record.json`
Writer: `beo-validate`. Required for every `PASS_EXECUTE`, `FAIL_EXPLORE`, `FAIL_PLAN`, or `BLOCK_USER` verdict.

| Field | Required | Rule |
| --- | --- | --- |
| `"verdict"` | yes | `PASS_EXECUTE` \| `FAIL_EXPLORE` \| `FAIL_PLAN` \| `BLOCK_USER` |
| `"execution_set_id"` | when PASS_EXECUTE | selected execution set id |
| `"execution_set_mode"` | when PASS_EXECUTE | `single` \| `ordered_batch` \| `local_parallel` |
| `"execution_set_beads"` | when PASS_EXECUTE | ordered or unordered array of approved bead ids |
| `"partial_progress_allowed"` | when verdict=`PASS_EXECUTE` and `execution_set_mode` is `ordered_batch` or `local_parallel` | boolean; `true` only when `beo-validate` proves unaffected beads may continue independently if one bead blocks |
| `"rationale"` | yes | narrative explaining the verdict and mode choice |
| `"evidence_refs"` | yes | list of artifact paths or sections inspected during readiness classification |
| `"approval_action"` | yes | one of: `created`, `refreshed`, `unchanged`, `blocked` |
| `"approval_ref"` | when verdict=`PASS_EXECUTE` | path to the current `approval-record.json` used for this verdict, whether `approval_action` is `created`, `refreshed`, or `unchanged` |
| `"doctrine_version_ref"` | yes | beo doctrine version or git commit ref at assessment time |
| `"validated_at"` | yes | timestamp of verdict |

When `approval_action=unchanged`, `approval_ref` MUST point to the existing current valid approval record that was revalidated for this `PASS_EXECUTE` verdict. An unchanged approval is still an approval dependency and must remain auditable by `beo-execute`, `beo-review`, and resume flows.

`partial_progress_allowed` is validation-owned authority. It is not inferred from the display card and is not created by `beo-execute`. For `single` execution sets, omit the field or treat it as `false`; single-bead execution has no unaffected bead to continue.

Authority for mirrored fields is mapped in `beo-reference -> state.md`. Artifact schemas define required fields; display cards and self-reported summary flags are not canonical authority.

## Partial-progress authority

`partial_progress_allowed=true` is legal only when all selected unaffected beads can continue safely after another bead blocks.

Required proof:
- the remaining beads are inside the same current approval envelope;
- file scopes are disjoint from the blocked bead;
- generated outputs are disjoint from the blocked bead;
- no dependency edge requires the blocked bead to complete first;
- verification can still produce meaningful evidence for the continued beads;
- continuing does not hide, overwrite, or complicate blocker evidence.

Default: `false`.

`beo-execute` may continue unaffected beads after a blocker only when both canonical `STATE.json` and `readiness-record.json` have `partial_progress_allowed=true`, and the live execution facts still match the validation proof.

## Zero-cardinality legality

Artifacts with zero entries in required arrays are not automatically valid. Explicit legality rules:

| Case | Legal? | Rule |
| --- | --- | --- |
| `CONTEXT.md` with no decision IDs | Legal | Only when no external decision was required for scope, constraints, or acceptance; use `decisions: []` with an explicit note that none apply |
| `REVIEW.md` with no verification rows | Illegal | When `verification_commands` is non-empty in the approval record; omit or use explicit `N/A` entries only when no commands apply |
| `execution-bundle.json` with `aggregate_changed_files=[]` when finalized (`partial_progress=false`) | Illegal | Execution always produces at least one file change; if none, the bead was not executed — abort and treat as a TOCTOU or scope failure. Pre-mutation checkpoints and rollback bundles that remain in `partial_progress=true` state may legitimately have `aggregate_changed_files=[]`. |
| `execution_set_beads=[]` | Illegal | An execution set must name at least one bead |
| `approved_beads=[]` in approval record | Illegal | Approval must name at least one bead |
| `forbidden_paths=[]` | Legal | Explicitly empty is valid; use `[]`, not omission |
| `approved_generated_outputs=[]` | Legal | Explicitly empty is valid; use `[]`, not omission |

## Feature slug schema

| Rule | Value |
| --- | --- |
| regex | `^[a-z0-9]+(?:-[a-z0-9]+)*$` |
| uniqueness | worktree-local; do not create a second active feature with the same slug |
| immutability | slug rename forbidden after first successful write |

## Artifact lock predicate

| Predicate | Required fields | Writer |
| --- | --- | --- |
| locked | required sections present; `locked=true`; `locked_at >= last content mutation`; locking skill owns artifact | owning skill |

## Review bundle predicate

Canonical surface: `.beads/artifacts/<feature_slug>/execution-bundle.json`

| Field | Required | Writer |
| --- | --- | --- |
| locked `CONTEXT.md` | yes | execute writes bundle flag only |
| current `PLAN.md` | yes | execute writes bundle flag only |
| terminal scope list | yes | execute |
| changed-files list | yes | execute |
| verification evidence | yes | execute |
| approval record reference | yes | execute |

## Bead description schema

| Field | Required |
| --- | --- |
| Goal | yes |
| Scope | yes |
| Acceptance | yes |
| File scope | yes |
| Forbidden paths | yes |
| Dependencies | yes |
| Verification | yes |
| Generated outputs | yes |

## Reactive-fix bead schema

| Field | Required |
| --- | --- |
| parent review finding | yes |
| exact bounded fix objective | yes |
| affected approved bead or reactive-fix bead id | yes |
| in-scope file list | yes |
| verification evidence or verification command reference | yes |

## Reactive-fix approval rule

A review-created reactive-fix bead must route to `beo-validate` for a fresh `PASS_EXECUTE` before `beo-execute`. All of the following conditions must hold for this route to be legal:
- verdict is `fix`
- root cause is proven
- fix is bounded to current approved file scope
- verification command/check remains unchanged or already approved
- acceptance and requirements do not change
- approval envelope remains current for the bounded fix
- reactive-fix record names changed files, acceptance target, and verification evidence required
- source finding is named
- exact bounded fix objective is named
- affected approved bead or bounded reactive-fix bead id is named
- fix file scope stays fully inside the current explicit approved scope
- forbidden paths remain unchanged
- verification remains inside the currently approved verification contract
- dependency shape does not change beyond linking the fix to the parent finding
- execution mode remains unchanged
- no new generated outputs, forbidden-path exceptions, or migration/security/privacy surfaces are introduced

If any of the above is false, route to `beo-plan` and treat approval as requiring repair before execution.
If root cause is not proven enough to classify the fix, route to `beo-debug`.

## Feature learning record artifact shape

Feature learning records are feature-local artifacts. Durable-learning thresholds and consolidation thresholds live in `beo-reference -> learning.md`.

Minimum feature-learning sections when a record is created:
- `Disposition`
- `Accepted evidence`
- `Patterns`
- `Decisions`
- `Failures / blockers`
- `Applicability`
- `Provenance`
- `Promotion status`

Do not create a feature learning record for obvious isolated accepted work with `no-learning`; record the inline disposition shape from `beo-reference -> learning.md` instead.

## Surface writer map

The writer map is canonical for artifact ownership. Per-file writer-map evidence used during a specific hardening upgrade is implementation evidence only and must not become future runtime ceremony for unrelated edits.

| Surface | Create | Modify | Invalidate approval? |
| --- | --- | --- | --- |
| `CONTEXT.md` | beo-explore | beo-explore | yes |
| `PLAN.md` | beo-plan | beo-plan | yes |
| bead graph / descriptions | beo-plan | beo-plan, beo-review for reactive-fix beads | yes when current approved graph changes or reactive-fix exceeds in-scope approval rule |
| `approval-record.json` | beo-validate | beo-validate or authorized invalidator | n/a |
| `readiness-record.json` | beo-validate | beo-validate | no |
| `execution-bundle.json` | beo-execute | beo-execute | no |
| `REVIEW.md` | beo-review | beo-review | no |
| product files | beo-execute | beo-execute | no unless scope violation |
| review evidence bundle | beo-execute | beo-execute | no |
| feature learning record | beo-compound | beo-compound | no |
| shared learning guidance | beo-dream with approval | beo-dream with approval | no |
| managed onboarding surfaces | beo-onboard | beo-onboard | no |
