---
name: beo-validate
description: |
  Decide execution readiness and select the approved execution set. Use when artifacts need readiness verification, not content edits. Do not use when artifact content edits or execution are required.
metadata:
  dependencies:
    - id: beads-cli
      kind: command
      command: br
      missing_effect: unavailable
      reason: Required to prove bead graph readiness and approved execution units.
    - id: beads-viewer
      kind: command
      command: bv
      missing_effect: degraded
      reason: Useful for viewer-backed bead inspection; missing `bv` does not replace live bead graph proof from `br`.
---
# beo-validate

## Purpose
Decide execution readiness and select the approved execution set.

## Primary owned decision
Emit exactly one readiness verdict: `PASS_EXECUTE`, `FAIL_EXPLORE`, `FAIL_PLAN`, or `BLOCK_USER`, from existing artifacts without editing their content.

## Ownership predicate
- Requirements, plan, approval, bead readiness, remediation class, or execution mode needs classification.
- Artifacts need readiness verification, not content edits.
- One or more approved ready beads, or an approved dependency chain whose first bead is ready, need execution-set classification.
- Multiple ready or dependency-chain candidate beads require file-scope, generated-output, and dependency-order classification before execution.
- No artifact content edit or implementation is required.

## Readiness classification order

Classify in this order: requirements, plan/bead graph, user blockers,
approval, then execution-set eligibility.

Do not emit `PASS_EXECUTE` without an explicit selected execution set inside
the current approval envelope. `ordered_batch` may include approved child beads
blocked only by earlier beads in the same selected dependency chain;
`local_parallel` may include only independently ready beads.

For the full procedure, read `references/readiness-classification.md`,
`references/readiness-review-prompt.md`, `beo-reference -> approval.md`, and
`beo-reference -> complexity.md`.

## Execution Set Card

When emitting `PASS_EXECUTE`, present the following display card. It is operator-facing only and does not substitute for `readiness-record.json`.

```md
Execution Set Card:
  execution_set_id:
  mode: single | ordered_batch | local_parallel  # display alias for execution_mode (STATE) / execution_set_mode (readiness-record); do not copy this field name into artifacts or state
  selected_beads: [<bead_ids in execution sequence>]  # display alias for execution_set_beads; do not copy this field name into artifacts or state
  bead_scope: [<declared changed files per bead>]
  approval_ref: <path to approval-record.json>
  blocked_or_queued: [<bead_ids not included in this set>]
  partial_progress_allowed: true | false
Authority note: display-only; canonical authority remains in the referenced state/artifact surface.
```

## Writable surfaces
- Readiness, `approval_ref`, `execution_mode`, `execution_set_id`, `execution_set_beads`, and `partial_progress_allowed` when applicable in shared state surfaces.
- Current `approval-record.json` grant, refresh, or invalidation fields as defined by `beo-reference -> approval.md`.
- Bead readiness/status fields only as allowed by canonical bead/status mapping.
- Shared state/handoff fields allowed by `beo-reference -> skill-contract-common.md`.
- `.beads/artifacts/<feature_slug>/readiness-record.json` — durable rationale for readiness verdict, mode, execution set, evidence summary, and approval action; required for every verdict.

> Canonical: `beo-reference -> artifacts.md`
> Locally enforced as:
> - Check `Forbidden paths`, approved file scope, approved generated outputs, and dependency constraints in the canonical bead schema.
> - Do not redefine bead fields locally.
> - Return content repair to the owning artifact writer.

> Canonical: `beo-reference -> pipeline.md` and `beo-reference -> approval.md`
> Locally enforced as:
> - Route content repair to artifact owners.
> - Write or refresh approval records only as permitted by canonical approval doctrine.
> - Emit `BLOCK_USER` when required external authorization, access, secret, or clarification is missing.
> - Status, onboarding, and Go Mode displays cannot substitute for readiness or mode classification.

## Hard stops
- Do not edit `CONTEXT.md`, `PLAN.md`, or implementation files.
- Do not emit `PASS_EXECUTE` without a selected `execution_set`.
- Do not classify `local_parallel` when write scopes, generated outputs, dependency edges, or approval refs conflict.
- Do not bypass current approval checks.
- When a validation-time blocker requires root-cause diagnosis, route to `beo-route`; do not create a direct `beo-debug` handoff from validate.
- Do not emit `PASS_EXECUTE` unless `approval_ref` points to the exact current approval record used for the selected execution set, including when `approval_action=unchanged`.
- When emitting `PASS_EXECUTE` for `ordered_batch` or `local_parallel`, write `partial_progress_allowed` explicitly to both `STATE.json` and `readiness-record.json`. Default is `false`. Set `partial_progress_allowed=true` only when unaffected beads can continue safely after one selected bead blocks, proven by disjoint file scope, disjoint generated outputs, no dependency edge on the blocked bead, valid shared approval, and independent verification. Missing, null, omitted, or stale values are treated by execute as `false`.
- When validation is entered to repair readiness/state consistency, do not preserve a mismatched `partial_progress_allowed`.
- For `ordered_batch` or `local_parallel`, write the same explicit boolean value to both `STATE.json` and `readiness-record.json`.
- For `single`, omit partial-progress behavior unless canonical state schema requires an explicit default; execution still treats missing or stale values as `false`.

## Allowed next owners
- `beo-execute`
- `beo-plan`
- `beo-explore`
- `user`
- `beo-route` — only for exceptional owner-state resolution under canonical route doctrine.

## References
- `beo-reference -> approval.md` — read when checking approval freshness, invalidation, or execution envelope rules.
- `beo-reference -> artifacts.md` — read when checking artifact/bead schemas, execution-set fields, bead scope, generated outputs, and dependency constraints.
- `beo-reference -> complexity.md` — read when validating required planning-depth sections.
- `beo-reference -> status-mapping.md` — read when mapping readiness to bead labels/statuses.
- `references/readiness-classification.md` — read when classifying readiness verdicts and execution-set modes.
- `references/readiness-review-prompt.md` — read when running a non-normative readiness review.
- `references/bead-readiness-prompt.md` — read when checking bead-level readiness prompts.
