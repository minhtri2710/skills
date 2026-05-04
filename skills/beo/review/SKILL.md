---
name: beo-review
description: |
  Emit one terminal verdict. Use when execution scope and review evidence bundle are complete. Do not use when fixes must be implemented or root cause must be proven.
metadata:
  dependencies: []
---
# beo-review

## Purpose
Emit one terminal verdict.

## Primary owned decision
Emit exactly one terminal verdict: `accept`, `fix`, or `reject`.

## Ownership predicate
- Execution scope is complete for the current feature or bead set.
- Review evidence includes locked requirements, plan, changed files, verification, and approval reference.
- The requested work is assessment, not implementation or root-cause diagnosis.
- A terminal verdict is needed before closure, learning, or reactive-fix routing.

## Writable surfaces
- `.beads/artifacts/<feature_slug>/REVIEW.md` — verdict, evidence, and (for rejected features) a non-promotable rejection retrospective.
- Reactive-fix bead descriptions only when canonical approval and artifact rules allow them.
- Invalidate current `approval-record.json` and clear approval/readiness mirrors only when reactive-fix bead description changes exceed the retained approval envelope.
- Shared state/handoff fields allowed by `beo-reference -> skill-contract-common.md`.

> Canonical: `beo-reference -> artifacts.md`
> Locally enforced as:
> - Use the canonical `REVIEW.md` minimum template.
> - Keep specialist prompts evidence-only.
> - Create reactive-fix beads only when the canonical approval rule is satisfied.

## Hard stops

### Verdict authority
- Do not implement fixes.
- Do not accept without required verification evidence.
- Do not let specialist evidence emit the terminal verdict.

### Reactive fixes and debug
- Do not create reactive-fix beads unless every condition in the canonical Reactive-fix approval rule (`beo-reference → artifacts.md`) is satisfied; route to `beo-debug` when root cause is unproven, or to `beo-plan` when the fix scope exceeds the current approval envelope.
- A bounded reactive fix still routes to `beo-validate`; bounded scope does not grant direct execution.
- When routing to `beo-debug`, write `debug_return.return_to` to `STATE.json` before handoff.

### Approval and scope coverage
- Do not review an execution bundle unless `ready_for_review=true`, `finalized_at` is present, and `changed_file_hashes` covers every aggregate changed/generated file.
- Independently compute the live execution diff from actual working tree/VCS state and `execution-bundle.json.dirty_baseline`, then compare it to `execution-bundle.json.aggregate_changed_files`; do not limit review to files self-reported by the bundle and do not accept self-reported `scope_respected` flags as the sole confirmation.
- If live file hashes or diff evidence diverge from the finalized bundle, abort review and route to `beo-route` or `user` according to owner-state evidence; do not silently attribute concurrent edits to the execution bundle.
- REVIEW.md Approval/Scope Lens must list every file in the union of live execution diff files and `aggregate_changed_files`; any unlisted file or changed file missing from `aggregate_changed_files` is a P1 finding that blocks `accept`.

## Verdict output card

```md
Verdict: accept | fix | reject
Evidence checked:
Approval/scope result:
Verification result:
Blocking findings:
Learning disposition: no-learning | durable-candidate | unclear | rejection-retrospective
Learning evidence: <source artifacts or pattern refs supporting disposition>
Continue via: beo-compound | beo-validate | beo-plan | beo-explore | done
Authority note: display-only; canonical authority remains in the referenced state/artifact surface.
```

Learning disposition is governed by `beo-reference -> learning.md`; local
review output mechanics and optional metrics live in
`references/review-operations.md`.

## Allowed next owners
- `beo-compound`
- `beo-validate`
- `beo-plan`
- `beo-explore`
- `beo-debug`
- `user`
- done
- `beo-route` — only for exceptional owner-state resolution under canonical route doctrine.

## References
- `beo-reference -> operator-card.md` — read when formatting verdict output.
- `beo-reference -> artifacts.md` — read when writing `REVIEW.md` and reactive-fix bead fields.
- `beo-reference -> approval.md` — read when checking reactive-fix approval retention.
- `beo-reference -> pipeline.md` — read when routing after verdict.
- `beo-reference -> learning.md` — read when splitting accepted-work closure.
- `references/review-operations.md` — read when formatting local review disposition details and optional metrics.
- `references/review-specialist-prompts.md` — read when gathering specialist evidence without verdict authority.
