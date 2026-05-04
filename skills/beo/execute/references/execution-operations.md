# execution-operations

Role: APPENDIX
Allowed content only: claim / execute / verify / complete command sequence and exit evidence shapes for an already-selected execution set; no approval, readiness, or routing decisions

## Claim command forms

Use canonical `br update`, `br comments add`, and `br sync --flush-only` forms from `beo-reference -> cli.md`. This appendix owns when `beo-execute` uses them, not their reusable syntax.

## Preflight checklist

Before mutation, verify:
- loaded owner is `beo-execute`
- readiness is `PASS_EXECUTE`
- `approval_ref` is present and readable
- approval is current
- `CONTEXT.md` hash matches the approval record
- `PLAN.md` hash matches the approval record
- exactly one execution set is selected
- selected beads match `execution_set_beads`
- execution mode is `single`, `ordered_batch`, or `local_parallel`
- intended writes are inside approved declared file scope
- selected beads to be claimed are not already claimed or reserved by another actor, unless the operator confirms a stale self-claim recovery

## Linear steps

| Step | Action |
| --- | --- |
| 1 | Confirm owner has already been selected as `beo-execute`. |
| 2 | Confirm exactly one selected `execution_set` is present in trusted route or state evidence. |
| 3 | Confirm `STATE.json` approval reference matches the live `approval-record.json` AND re-hash current `PLAN.md` and `CONTEXT.md` content against hashes recorded in the approval record; abort and route to `beo-validate` if any hash mismatches. |
| 4 | Confirm every bead in the execution set is inside the approval envelope. |
| 5 | Confirm working tree is clean for in-scope files, or record pre-existing dirty paths before mutation. |
| 6 | Confirm `STATE.json.execution_mode` is `single`, `ordered_batch`, or `local_parallel`. |
| 7 | Re-read and record each selected bead's prior status and labels before claiming. If any selected bead is already `in_progress` or has label `reserved`, stop with bead-conflict evidence unless durable same-worktree evidence proves this is a stale interrupted claim from the same worktree: either `HANDOFF.json` with `created_by_owner=beo-execute` matching this execution set, or a non-final `execution-bundle.json` for that exact execution set with `ready_for_review=false`. Without matching durable evidence, route to `user` for claim resolution rather than assuming ownership. Claim timing depends on `STATE.json.execution_mode`: for `single`, claim the one selected bead; for `ordered_batch`, claim only the first currently executable bead and defer child claims until their predecessors complete; for `local_parallel`, claim every selected bead before concurrent mutation. A claim uses the canonical update form to set `status=in_progress` and the canonical label-add form to apply `reserved`; both command forms live in `beo-reference -> cli.md`. Run the canonical flush command from `beo-reference -> cli.md`, then re-read each claimed bead's current status and labels. A valid claim requires both `status=in_progress` and label `reserved` on every claimed bead. If any claimed bead lacks the reserved marker, abort immediately: remove only the `reserved` labels added during this claim attempt, revert those beads to their recorded prior statuses, flush through the canonical CLI form, and record bead-conflict evidence before routing. Do not mutate any files on a conflict abort. |
| 8 | Write `execution-bundle.json` as a crash-safe pre-mutation checkpoint. (a) Copy known scalar fields from available context: `feature_slug` and `approval_ref` from STATE.json and the approval record; `doctrine_version_ref` from the readiness-record.json or approval record; `execution_set_id` and `execution_set_mode` from the validated execution set. (b) Set boolean flags to their initial values: `partial_progress: true`, `ready_for_review: false`, `scope_respected: null` (not yet evaluated; set to true or false only at finalization). (c) Initialize collection fields to empty arrays or empty objects: `executed_beads: []`, `queued_beads: []`, `blocked_beads: []`, `per_bead_changed_files: {}`, `per_bead_generated_files: {}`, `aggregate_changed_files: []`, `aggregate_generated_files: []`, `dirty_baseline: {in_scope: [], out_of_scope: []}`, `verification: []`, `out_of_scope_changes: []`, `conflict_or_overlap_evidence: []`, `blockers: []`. Zero-cardinality rules (e.g., `aggregate_changed_files` must not be empty) apply only after finalization when `partial_progress=false`. This checkpoint enables safe abort or resumption if the session is interrupted before completion. |
| 9 | For `single`, execute the one selected bead. |
| 10 | For `ordered_batch`, execute beads in the recorded order only; after each predecessor completes and releases its claim, re-read and claim the next bead before mutating it. |
| 11 | For `local_parallel`, re-check disjoint write scopes, disjoint generated outputs, no dependency edge, and clean/recorded dirty state before any concurrent mutation. |
| 12 | Implement only inside each bead's declared file scope and approved generated-output scope. |
| 13 | Run verification commands from each bead description or explicit approved verification commands. |
| 14 | For structural changes, search consuming directories for stale imports, routes, or old patterns before completion. |
| 15 | Record per-bead changed files, generated files, dirty baseline, verification commands, outputs, scope-respected flags, blockers, and approval reference in `execution-bundle.json`; set `partial_progress: false`. Do NOT set `ready_for_review`, `finalized_at`, or `changed_file_hashes` yet — those require the Step 17 flush to succeed first. |
| 16 | Mark each bead done or blocked according to actual evidence. Record failed verification or unrecoverable execution evidence in `execution-bundle.json`; do not invent a non-canonical bead status. Remove the `reserved` label from every bead whose execution claim is ending before the final flush. |
| 17 | Flush bead DB mutations through `beo-reference -> cli.md`. If the flush exits non-zero, stop all work immediately, write `db_flush_failed: true` and current bead progress to `HANDOFF.json`, and route to user. |
| 18 | After a successful flush, re-read each bead to confirm committed status, then set `ready_for_review: true`, `finalized_at`, and `changed_file_hashes` in `execution-bundle.json`. These fields may be set ONLY after the Step 17 flush succeeds and re-read confirms all bead mutations are committed. Pre-final bundles with `ready_for_review=false` or missing `finalized_at` are explicitly non-reviewable and must not be accepted by `beo-review`. |
| 19 | Update `STATE.json` with execution-set status/evidence and next owner evidence. |

## Execution-set safety policy

- `single` requires exactly one bead.
- `ordered_batch` requires explicit order and dependency rationale.
- `local_parallel` requires disjoint write scopes, disjoint generated outputs, no dependency edge, and one current approval envelope covering every bead.
- If local-parallel safety becomes false after execution starts, stop affected work and record scope/conflict evidence.
- Missing ordering, missing generated-output proof, or unresolved overlap belongs to `beo-plan`.
- Approval refresh belongs to canonical approval doctrine; this appendix does not approve or refresh work.
- If the canonical bead DB flush exits non-zero at any point, stop all work immediately, write `db_flush_failed: true` with current bead progress to `HANDOFF.json`, and route to user.

Routing, approval law, and scope law remain canonical in `beo-execute`, `beo-reference -> approval.md`, and `beo-reference -> artifacts.md`.

## Dirty worktree and concurrent work policy

- If an in-scope file is already dirty before execution and the current owner did not create that diff, stop and record evidence for canonical owner selection; do not merge unowned work by assumption.
- If an out-of-scope file is dirty, do not touch it; record it as pre-existing state only.
- Pre-existing dirty generated files must not be claimed as outputs of the current bead.
- When execution proceeds with recorded pre-existing dirty paths, execution evidence must distinguish pre-existing diffs from current-bead changes.

## Generated side-effect policy

- Generated files may change only when explicitly listed in bead file scope, listed under approved generated outputs, or deterministically updated by a verification command with recorded evidence.
- Unexpected generated changes outside scope require stopping and recording scope-drift evidence; successor owner remains canonical in `beo-execute` / `pipeline.md`.
- Lockfile changes require explicit dependency-change approval.
- Snapshot changes require acceptance evidence that the UI or output change is intended.
- Formatting changes outside approved file scope are scope violations unless the bead explicitly allows them.

## Execution bundle minimum fields

Write the canonical execution bundle to `.beads/artifacts/<feature_slug>/execution-bundle.json` with at least:

- `feature_slug`
- `approval_ref`
- `execution_set_id`
- `execution_set_mode`
- `executed_beads`
- `queued_beads`
- `blocked_beads`
- `per_bead_changed_files`
- `per_bead_generated_files`
- `aggregate_changed_files`
- `aggregate_generated_files`
- `verification`
- `scope_respected`
- `out_of_scope_changes`
- `conflict_or_overlap_evidence`
- `partial_progress`
- `blockers`
- `ready_for_review`
- `doctrine_version_ref`

## Multi-bead blocker handling

When any bead in a multi-bead execution set hits a blocker during mutation:

1. **Pause the affected bead immediately.** Do not attempt to guess a fix or skip silently.
2. **Record blocker evidence** in `execution-bundle.json`: affected bead id, failing command, smallest repro, why root cause is unproven. Set the `blocked_beads` entry.
3. **Re-read both `STATE.json` and `.beads/artifacts/<feature_slug>/readiness-record.json`.**
4. **Continue only when both surfaces have `partial_progress_allowed=true`.**
5. **If either surface is missing, false, stale, or contradictory, treat `partial_progress_allowed=false`:** stop the entire execution set; route to `beo-debug` per the debug-return protocol (write `debug_return.return_to` to `STATE.json` before routing).
6. **If all conditions hold:** re-verify that live execution facts still match the validation proof — disjoint file scope, disjoint generated outputs, no dependency on the blocked bead, and current approval still bounds unaffected beads. If any condition is no longer true, treat as `partial_progress_allowed=false` per step 5. Continue unaffected beads; record continued-bead ids, changed files, verification evidence, and `partial_progress=true` in `execution-bundle.json`. Keep the blocked bead in `blocked_beads` with full blocker evidence. After unaffected work is safely recorded, route the blocker through the legal owner, usually `beo-debug` when root cause is unproven. Route to `beo-review` only when the selected execution scope is terminally complete or canonical pipeline doctrine explicitly permits partial-scope review.

## Exit evidence shapes, not routing decisions

Use this appendix to name the evidence that `beo-execute` should emit; successor-owner selection remains canonical in `beo-execute` and `beo-reference -> pipeline.md`.

| Exit shape | Required evidence |
| --- | --- |
| review-ready | execution set id, completed bead ids, changed files, generated files, verification evidence, approval reference, execution bundle ref |
| debug-needed | affected bead id, failing command, smallest repro, why root cause is unproven |
| plan-needed | contract, ordering, dependency, file-scope, generated-output, or bead-graph mismatch that cannot be fixed inside approved scope |
| validate-needed | approval became stale before mutation and no product mutation occurred, or execution-set evidence is stale |
| user-needed | external blocker, missing access, missing secret, or required clarification |

Non-normative completion comment:

```text
Execution complete for execution-set <execset-id>. Beads: <bead-ids>. Changed files: <paths>. Verification: <commands and result>. Approval: <approval_ref>.
```
