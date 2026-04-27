# Artifacts

## Artifact layout

| Surface | Purpose |
| --- | --- |
| `.beads/artifacts/<feature_slug>/CONTEXT.md` | locked requirements |
| `.beads/artifacts/<feature_slug>/PLAN.md` | current-phase design and bead graph |
| `.beads/artifacts/<feature_slug>/REVIEW.md` | terminal verdict and evidence |
| `.beads/artifacts/<feature_slug>/execution-bundle.json` | canonical execution/review evidence bundle |
| `approval-record.json` | execution approval record |

Canonical ownership notes:
- `beo-references -> artifacts.md` owns artifact schemas and writer boundaries.
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

| Section | Required |
| --- | --- |
| acceptance | yes |
| non-goals | yes |
| compatibility | yes |
| constraints | yes |
| locked marker | yes |

## PLAN.md schema

| Section | Required |
| --- | --- |
| current phase | yes |
| design | yes |
| bead graph | yes |
| dependencies | yes |
| file scopes | yes |
| verification plan | yes |

Micro-compact note:
- A micro-compact `PLAN.md` may compress prose, but it must still preserve explicit current phase, one bead identifier, `Goal`, `Scope`, `Acceptance`, `Dependencies`, `File scope`, and `Verification`.
- Micro-compact is a presentation shape only; it does not relax approval, scope, or verification schema.

## REVIEW.md schema

| Field | Required |
| --- | --- |
| verdict=`accept`/`fix`/`reject` | yes |
| evidence bundle reference | yes |
| UAT / acceptance evidence when required | yes |
| finding minimums when findings exist | yes |

Finding minimum shape:
- `Severity`
- `Evidence`
- `Acceptance impact`
- `Required owner`

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
| locked CONTEXT.md | yes | execute/swarm writes bundle flag only |
| current PLAN.md | yes | execute/swarm writes bundle flag only |
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
| in-scope file list | yes |
| verification evidence | yes |

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
