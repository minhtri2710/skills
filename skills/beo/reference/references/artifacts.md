# Artifacts

## Artifact layout

| Surface | Purpose |
| --- | --- |
| `.beads/artifacts/<feature_slug>/CONTEXT.md` | locked requirements, decision IDs, acceptance, constraints, and verification intent |
| `.beads/artifacts/<feature_slug>/PLAN.md` | current-phase design, phase/story/risk contract, bead graph, and execution envelope proposal |
| `.beads/artifacts/<feature_slug>/REVIEW.md` | terminal verdict, severity findings, UAT/decision verification, and evidence assessment |
| `.beads/artifacts/<feature_slug>/execution-bundle.json` | canonical execution/review evidence bundle |
| `.beads/artifacts/<feature_slug>/approval-record.json` | execution approval record |
| `.beads/learnings/<feature_slug>.md` | feature-local learning record when durable or unclear learning exists |

Canonical ownership notes:
- `beo-references -> artifacts.md` owns artifact schemas, provenance shape, and writer boundaries.
- `beo-references -> learning.md` owns durable-learning thresholds, no-learning, and cross-feature consolidation thresholds.
- For owner selection, handoff freshness, and approval freshness, point to `beo-references -> pipeline.md`, `beo-references -> state.md`, and `beo-references -> approval.md` rather than restating those doctrines here.

## Artifact provenance chain

Canonical evidence chain:
`CONTEXT.md` lock -> `PLAN.md` revision -> `approval-record.json` -> `execution-bundle.json` -> `REVIEW.md` -> feature learning / shared learning

Minimum provenance rules:
- `PLAN.md` identifies the locked `CONTEXT.md` it implements.
- `approval-record.json` identifies the `PLAN.md` revision and bead set it approves.
- `execution-bundle.json` identifies the approval record used for execution.
- `REVIEW.md` identifies the execution bundle it reviews.
- Feature learning and shared learning identify the accepted review evidence they derive from.

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

## 0. Context binding
- context_hash:
- locked decision IDs covered:
- requirement contradictions checked: yes/no
- planning depth class: small_change / standard_feature / high_risk_feature

## 1. Prior learning consulted
| Learning source | Applicable? | Why |
| --- | --- | --- |
| .beads/learnings/... | yes/no |  |

## 2. Discovery facts
| Fact | Evidence | Impact |
| --- | --- | --- |

## 3. Approach
- chosen approach:
- alternatives rejected:
- reason for rejection:
- compatibility notes:

## 4. Risk map
| Risk | Severity | Proof required before execution | Owner |
| --- | --- | --- | --- |
|  | LOW/MED/HIGH | command/spike/manual evidence | beo-plan/beo-validate/user |

## 5. Whole-feature phase map
| Phase | User/system-visible outcome | Demo | Unlocks | Out of scope |
| --- | --- | --- | --- | --- |

## 6. Current phase contract
- phase id:
- entry state:
- exit state:
- demo:
- rollback expectation:
- pivot signals:
- explicit out of scope:

## 7. Current phase story map
| Story | User/system-visible change | Acceptance | Beads |
| --- | --- | --- | --- |

## 8. Bead graph
| Bead | Goal | Scope | Acceptance | File scope | Dependencies | Verification |
| --- | --- | --- | --- | --- | --- | --- |

## 9. Execution envelope proposal
- candidate mode: serial/swarm
- candidate approved beads:
- approved file scope proposal:
- approved generated outputs:
- forbidden paths:
- verification commands:
- scope source refs:
```

Planning-depth note:
- The template above is the canonical full shape and ordering reference.
- `beo-references -> complexity.md` defines which sections are required for `small_change`, `standard_feature`, and `high_risk_feature`.
- `small_change` may omit sections that `complexity.md` does not require, but it must still keep its minimal approach, current phase contract, bead graph, and execution envelope proposal explicit.

Rules:
- `PLAN.md` is the single canonical home for phase/story/risk planning. Do not introduce parallel phase-plan or history artifacts as canonical BEO state.
- Prior-learning consultation is targeted: consult applicable feature/shared learnings, not the entire learning corpus by default.
- Discovery facts are facts only, not plan decisions. Do not include speculative implementation advice without evidence.
- A phase is not a bucket of technical chores; it must produce an inspectable user/system-visible state.
- Stories sequence value delivery. Beads implement stories; beads are not the story map itself.
- Each bead must satisfy the BEO bead description schema: `Goal`, `Scope`, `Acceptance`, `File scope`, `Dependencies`, and `Verification`.
- A HIGH risk without required proof blocks `PASS_SERIAL` and `PASS_SWARM` until the planning/validation owner records the required evidence or routes appropriately.
- The execution envelope proposal is not execution approval. Approval remains the `approval-record.json` written by `beo-validate`.

Micro-compact note:
- A micro-compact `PLAN.md` may compress prose, but it must still preserve explicit current phase, one bead identifier, `Goal`, `Scope`, `Acceptance`, `Dependencies`, `File scope`, and `Verification`.
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
| R1 | P0/P1/P2/P3 | acceptance/security/verification/etc. |  | beo-debug/beo-plan/beo-execute/user |

## Specialist review sections
### Code quality
### Architecture
### Security / privacy
### Test coverage
### Product / UAT
### Learning candidates

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
- Implementation-agent or worker claims are not sufficient verification evidence; `REVIEW.md` records assessed evidence, not trust in claims.

## execution-bundle.json schema

| Field | Required |
| --- | --- |
| `feature_slug` | yes |
| `approval_ref` | yes |
| `executed_beads` | yes |
| `changed_files` | yes |
| `generated_files` | yes |
| `verification` | yes |
| `scope_respected` | yes |
| `out_of_scope_changes` | yes |
| `blockers` | yes |
| `ready_for_review` | yes |

Provenance note:
- `execution-bundle.json` should reference the exact approval record used and enough plan/bead context to show which approved execution unit produced the bundle.

## Feature slug schema

| Rule | Value |
| --- | --- |
| regex | `^[a-z0-9]+(?:-[a-z0-9]+)*$` |
| uniqueness | no existing `.beads/artifacts/<feature_slug>/` |
| immutability | slug rename forbidden after first successful write |

## Artifact lock predicate

| Predicate | Required fields | Writer |
| --- | --- | --- |
| locked | required sections present; `locked=true`; `locked_at >= last content mutation`; locking skill owns artifact | owning skill |

## Review bundle predicate

Canonical surface: `.beads/artifacts/<feature_slug>/execution-bundle.json`

| Field | Required | Writer |
| --- | --- | --- |
| locked `CONTEXT.md` | yes | execute/swarm writes bundle flag only |
| current `PLAN.md` | yes | execute/swarm writes bundle flag only |
| terminal scope list | yes | execute/swarm |
| changed-files list | yes | execute/swarm |
| verification evidence | yes | execute/swarm |
| approval record reference | yes | execute/swarm |

## Bead description schema

| Field | Required |
| --- | --- |
| Goal | yes |
| Scope | yes |
| Acceptance | yes |
| File scope | yes |
| Dependencies | yes |
| Verification | yes |

## Reactive-fix bead schema

| Field | Required |
| --- | --- |
| parent review finding | yes |
| exact bounded fix objective | yes |
| affected approved bead or reactive-fix bead id | yes |
| in-scope file list | yes |
| verification evidence or verification command reference | yes |

## Reactive-fix approval rule

A reactive-fix bead written by `beo-review` does not stale approval only when all of the following remain true:
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

Feature learning records are feature-local artifacts. Durable-learning thresholds and consolidation thresholds live in `beo-references -> learning.md`.

Minimum feature-learning sections when a record is created:
- `Disposition`
- `Accepted evidence`
- `Patterns`
- `Decisions`
- `Failures / blockers`
- `Applicability`
- `Provenance`
- `Promotion status`

Do not create a feature learning record for obvious isolated accepted work with `no-learning`; record the inline disposition shape from `beo-references -> learning.md` instead.

## Surface writer map

| Surface | Create | Modify | Invalidate approval? |
| --- | --- | --- | --- |
| `CONTEXT.md` | beo-explore | beo-explore | yes |
| `PLAN.md` | beo-plan | beo-plan | yes |
| bead graph / descriptions | beo-plan | beo-plan, beo-review for reactive-fix beads | yes when current approved graph changes or reactive-fix exceeds in-scope approval rule |
| `approval-record.json` | beo-validate | beo-validate or authorized invalidator | n/a |
| `execution-bundle.json` | beo-execute, beo-swarm | beo-execute, beo-swarm | no |
| `REVIEW.md` | beo-review | beo-review | no |
| product files | beo-execute or worker | beo-execute or worker | no unless scope violation |
| review evidence bundle | beo-execute, beo-swarm | beo-execute, beo-swarm | no |
| feature learning record | beo-compound | beo-compound | no |
| shared learning guidance | beo-dream with approval | beo-dream with approval | no |
| managed onboarding surfaces | beo-onboard | beo-onboard | no |

## Swarm worker note

- A swarm worker is an execution delegate, not a route owner.
- A worker may mutate only the already-approved bead files for its assigned isolated scope.
- A worker inherits the same approved file-scope, forbidden-path, verification, and evidence obligations as equivalent serial execution.
- Worker output must aggregate into `execution-bundle.json` without inventing a separate approval or review protocol.
