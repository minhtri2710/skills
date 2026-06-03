# Mutation Safety, Approval Validity, and Recovery

> [!NOTE]
> This reference is subordinate to [references/kernel.md](file:///Users/beowulf/Work/personal/beo-skills/skills/beo/beo-reference/references/kernel.md). `references/kernel.md` is the canonical owner of BEO rules and invariants.

## Scope precedence

`scope.files.forbid` is a negative constraint, not alternate scope.

Precedence:

1. protected paths
2. forbid patterns
3. allow paths
4. generated outputs

If a path matches both allow and forbid, it is forbidden.

## Approval validity

Approval validity is canonical in `references/kernel.md` and machine-readable predicates are in `registry/approval-envelope.json`. Agents must not infer invalidity from elapsed time alone.

## Containment failure triage

| Symptom | Cause | Resolution |
| --- | --- | --- |
| `path matches protected pattern: <path>` | A ticket scope path overlaps a protected path from `registry/profiles.json` | Remove the protected path from product scope; use only explicit approved product files |
| `changed path outside approved scope: <path>` | A dirty path is not covered by `scope.files.allow` or `scope.generated_outputs` | Add the exact intended file path to the ticket scope, or clean/revert unrelated dirtiness before rerunning containment |
| Broad wildcard paths overlap protected patterns | A trailing `**` can overlap protected defaults such as `.git/**`, `.beads/**`, or `**/.env` | Prefer exact file paths over broad directory globs |
| Dirty Beads control-plane files appear during containment | `.beads/issues.jsonl`, `state.json`, or related control-plane artifacts changed outside the approved product scope | Commit or otherwise reach a clean control-plane prestate before running containment checks |
| `broad glob requires matching Human Gate authorization: <path>` | Broad scope requires explicit authorization in standard or strict operation | Replace the glob with exact paths, or use a resolved `human_gates` entry of type `broad_scope_authorization`; mode requirements are canonical in `registry/profiles.json` |

## Phase and approval staleness triage

| Symptom | Cause | Resolution |
| --- | --- | --- |
| `review-entry requires executed or reviewing state` | The review check is running against the wrong current phase | Re-read `state.json` and run the check that matches the current phase |
| `approval.<field> is stale` or `PASS_EXECUTE approval is stale for execution entry` | `TICKET.yaml`, git `HEAD`, prestate, or the approval projection changed after validation | Re-run the BEO validation path so helper scripts recompute approval fields; do not hand-edit approval hashes |
| Hash values in `state.json` disagree with current artifacts | Manual ticket edits or new commits invalidated the prior approval envelope | Return to validation and let `compute_approval_fields` update approval evidence synchronously |

## Reservation

Reservation is BEO-local strict-mode path ownership evidence, not an OS/git lock.

It is active until explicitly released, superseded, or revoked. It does not expire by elapsed time.

Reservation prevents BEO from knowingly approving overlapping strict path ownership; it does not prevent external edits. Validation and review must still inspect dirty/prestate changes.

## Execution start

Execution starts only after a durable `state.json` update where:

- `phase` becomes `executing`,
- `execution.actor` is set,
- `execution.started_at` is set,
- approval validity predicates still hold.

No product file mutation may occur before this executing-state entry is written.

## Interrupted execution recovery

If re-entering with `state.phase = executing`:

1. Fresh-read `br`, `TICKET.yaml`, `state.json`, runtime events when present, and approval contracts.
2. Recompute approval validity predicates.
3. Inspect approved files and generated outputs for dirty changes.
4. Compare current dirty paths against `execution.changed_files` and approved scope.
5. If all dirty paths are approved and classifiable, continue execution.
6. If approval predicates fail, emit `approval_stale_or_invalid -> beo-validate`; `beo-execute` may recompute predicates and route, but must not mutate `approval.*`.
7. If dirty paths are outside approved scope and attributable to the interrupted execution, fail closed via `containment_review_needed -> beo-review` if that route exists, or via `root_cause_diagnosis_needed -> beo-debug`; never use normal `executed` for containment.
8. If outside-scope dirtiness is unattributed or appears pre-existing/external, fail closed to `root_cause_diagnosis_needed` rather than treating it as reviewable execution output.
9. If partial mutation cannot be classified, append a handoff event and route to `root_cause_diagnosis_needed`.
