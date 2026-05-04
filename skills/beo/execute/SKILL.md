---
name: beo-execute
description: |
  Deliver one approved execution set. Use when readiness is `PASS_EXECUTE`, a selected execution set is present, and mutation stays in approved scope. Do not use when root cause is unproven, execution-set scope is ambiguous, or external worker coordination is required.
metadata:
  dependencies:
    - id: beads-cli
      kind: command
      command: br
      missing_effect: unavailable
      reason: Required to claim bead progress and keep canonical bead state in sync.
---
# beo-execute

## Purpose
Deliver one approved execution set.

## Primary owned decision
Implement the selected approved execution set inside the current approval envelope.

## Ownership predicate
- Readiness is `PASS_EXECUTE`.
- Exactly one approved execution set is selected.
- Approval is current and bounds every bead in the execution set.
- Root cause is proven for every bug-fix bead in the set, or each bug-fix bead's scope is bounded to a confirmed defect location requiring no diagnostic decision.
- Execution-set mode is `single`, `ordered_batch`, or `local_parallel`.
- Local parallel execution has disjoint write scopes, disjoint generated outputs, and no dependency edge.
- For `ordered_batch` or `local_parallel`, partial-progress behavior is governed by canonical `partial_progress_allowed` in `STATE.json` and `readiness-record.json`.
- Absent, null, missing, or stale `partial_progress_allowed` in either surface is treated as `false`.

## Execution Set Card

When claiming an execution set, confirm and record the following. This card is operator-facing only; canonical fields are in `STATE.json` and `execution-bundle.json`.

```md
Execution Set Card:
  execution_set_id: <from STATE.json>
  mode: single | ordered_batch | local_parallel
  claimed_beads: [<bead_ids in execution sequence>]
  approval_ref: <path to approval-record.json>
  changed_files_target: [<approved declared files per bead>]
  blocked_or_queued: [<bead_ids not in this set>]
  partial_progress_allowed: <from STATE.json/readiness-record.json>
Authority note: display-only; canonical authority remains in the referenced state/artifact surface.
```

## Writable surfaces
- Code and tests required by the selected execution-set beads only.
- Selected bead status/evidence surfaces for every bead in the execution set, as allowed by execution procedure and status mapping.
- Review evidence bundle fields for changed files, verification, and approval reference.
- Shared state/handoff fields allowed by `beo-reference -> skill-contract-common.md`.

## Local parallel

`local_parallel` is local-only parallelism inside one loaded `beo-execute` owner; see `beo-reference -> pipeline.md` and `references/execution-operations.md`.

## Preflight before mutation

Detailed claim, flush, re-read, checkpoint, verification, and completion steps live in `references/execution-operations.md`. This skill owns the execution contract boundary; the appendix owns the local operation sequence after `beo-execute` has already been selected.

Before mutation, verify the execution envelope from:
- `beo-reference -> approval.md`
- `beo-reference -> state.md`
- `references/execution-operations.md`

Local hard stops:
- do not mutate without current `PASS_EXECUTE`
- do not mutate outside approved declared file scope
- do not coordinate workers or external agents
- do not continue after stale approval or unproven root cause

## Hard stops

### Scope and approval
- Do not broaden scope beyond the selected execution set or approval envelope.
- Do not self-approve readiness, execution-set membership, ordering, or local-parallel safety.
- If approval becomes stale before mutation, stop and return to the canonical validate/approval flow before any pass or implementation continues.
- If approval becomes stale after mutation begins, stop immediately and hand off through the stale-after-mutation decision tree in `beo-reference -> approval.md`; do not keep implementing to finish first and do not re-enter execute directly.
- Do not begin mutation without re-verifying `PLAN.md` and `CONTEXT.md` content hashes against the approval record; a hash mismatch aborts execution and routes to `beo-validate`.

### Execution-set integrity
- Do not claim unrelated ready beads merely because they are convenient.
- If any bead to be claimed now is already claimed or reserved, abort and record bead-conflict evidence unless durable same-worktree evidence proves this is a stale interrupted claim: `HANDOFF.json` with `created_by_owner=beo-execute` for this execution set, or a non-final `execution-bundle.json` for that exact execution set with `ready_for_review=false`. Without matching durable evidence, route to `user`.
- After claiming, if claim + flush + re-read does not show both `status=in_progress` and label `reserved` for every bead claimed in this claim step, abort immediately, release only claims created by this attempt, and record bead-conflict evidence.

### Parallel and partial progress
- Do not execute two beads concurrently when write scopes, generated outputs, dependency edges, approval refs, or dirty-worktree evidence conflict.
- Do not use external worker dispatch, reservations, heartbeat protocols, or routing.
- If any bead in a multi-bead execution set blocks, do not continue unaffected beads unless canonical `readiness-record.json` and `STATE.json` both explicitly have `partial_progress_allowed=true`, and live execution evidence still proves disjoint scope, disjoint generated outputs, no dependency on the blocked bead, and current approval. If either surface is absent, null, missing, stale, or otherwise not explicitly `true`, stop the set and route blocker evidence through the legal owner.
- If `STATE.json.partial_progress_allowed` and `readiness-record.json.partial_progress_allowed` disagree, treat partial progress as `false`.
- Stop the execution set on a partial-progress mismatch. Route to:
  - `beo-debug` when a live blocker has unproven root cause.
  - `beo-validate` when the mismatch is a readiness/state consistency problem and no diagnostic proof is needed.
  - `beo-route` only when owner state is also stale, contradictory, or colliding.

### Debug and rollback
- Do not continue an affected bead after unproven root cause blocks safe implementation; return blocker evidence through `beo-debug`.
- When rollback of the current bead's mutation is needed before re-routing, limit rollback to that bead's declared changed files only; do not rollback prior beads or files outside declared scope without explicit plan authorization.
- When routing to `beo-debug`, write `debug_return.return_to` to `STATE.json` before handoff so beo-debug can return to the correct owner.

Do not emit ambiguous `review or plan` routing after stale approval is detected
post-mutation.

Return deterministic evidence:
- route to `beo-review` when scope impact must be assessed from the execution bundle/live diff
- route to `beo-plan` only when plan/file-scope/verification repair is already proven necessary
- otherwise route to `beo-route` for owner-state resolution

## Allowed next owners
- `beo-review`
- `beo-debug`
- `beo-plan`
- `beo-validate`
- `user`
- `beo-route` — only for exceptional owner-state resolution under canonical route doctrine.

## References
- `beo-reference -> approval.md` — read when checking execution envelope or invalidation.
- `beo-reference -> artifacts.md` — read when updating review evidence bundle fields.
- `beo-reference -> cli.md` — read when using shared `br`/`bv` command forms.
- `beo-reference -> pipeline.md` — read when handing off after execution.
- `beo-reference -> status-mapping.md` — read when updating bead status or labels.
- `references/execution-operations.md` — read when following the local execution loop and exit evidence shape.
