# Mutation Safety, Approval Validity, and Recovery

> [!NOTE]
> This reference is subordinate to `references/kernel.md`. `references/kernel.md` is the canonical owner of BEO rules and invariants.

## Scope precedence

1. protected paths
2. forbid patterns
3. allow paths
4. generated outputs

If a path matches both allow and forbid, forbid wins.

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

Reservation is BEO-local strict-mode path ownership evidence (not an OS/git lock). Active until explicitly released, superseded, or revoked. Prevents BEO from approving overlapping strict path ownership but does not prevent external edits. Validation and review must still inspect dirty/prestate changes.

## Execution start

Execution starts after a durable `state.json` update where `phase = executing`, `execution.actor` and `execution.started_at` are set, and approval validity predicates still hold. No product file mutation before this executing-state entry is written.

## Worktree isolation

> See kernel.md §7 for the canonical worktree isolation policy. This section only documents safety-specific path and recovery details.

**Recovery on re-entry (verify path)**:
- If the worktree is missing but state says `executing`, `beo-verify` emits `skipped` results for verify commands and exits with code 0 (all-skipped is not a failure). It does not refuse on its own. Operators must follow `beo-validate` / `beo-debug` recovery routes; `beo-verify` is read-only and does not gate recovery.

## Interrupted execution recovery

> See kernel.md §13 for canonical interrupted execution recovery rules. This section only documents safety-specific path authority.
