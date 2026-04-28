---
name: beo-review
description: |
  Emit one terminal verdict. Use when execution scope and review evidence bundle are complete. Do not use when fixes must be implemented or root cause must be proven.
---

# beo-review

## Purpose
Emit one terminal verdict.

## Primary owned decision
Emit exactly one verdict: `accept`, `fix`, or `reject`.

## Enter when
- terminal execution scope is complete
- the review evidence bundle contains locked requirements, current plan, changed files, verification evidence, and approval reference

## Writable surfaces
- `.beads/artifacts/<feature_slug>/REVIEW.md` while recording the terminal verdict and evidence assessment
- reactive-fix bead descriptions described by `beo-references -> artifacts.md`, only when verdict=`fix` and the reactive-fix approval rule is satisfied; otherwise route to `beo-plan`
- shared `STATE/HANDOFF` surfaces under `beo-references -> skill-contract-common.md`

## Decision packet
- shared decision packet under `beo-references -> skill-contract-common.md`
- local review fields remain in `REVIEW.md` and reactive-fix records

## Severity rubric

P0:
- catastrophic correctness, security, privacy, data loss, or irreversible damage

P1:
- acceptance blocker
- approval/scope mismatch
- required verification missing or failing
- security/privacy issue that blocks release
- locked `CONTEXT.md` decision violated
- migration/data/integration risk unresolved

P2:
- meaningful quality issue
- maintainability issue
- missing non-critical test
- follow-up needed but acceptance still satisfied

P3:
- polish
- naming
- cleanup
- optional improvement

## Verdict rule

Accept requires all of the following:
- no open P0 or P1 findings
- complete required verification evidence
- approval scope matching executed changes
- acceptance-critical `CONTEXT.md` decisions verified or explicitly marked `N/A`

## Severity-to-verdict mapping

- Any open P0/P1 blocks `accept`.
- P0/P1 with bounded known fix inside approval envelope may produce verdict=`fix` and a reactive-fix bead.
- P0/P1 with unproven root cause routes `beo-debug`.
- P0/P1 requiring requirements change routes `beo-explore`.
- P0/P1 requiring plan/scope/verification change routes `beo-plan`.
- P2/P3 may be accepted if acceptance, approval scope, and verification are complete.

## Decision verification rule

For each user-visible or acceptance-critical `CONTEXT.md` decision:
- verify by `SEE`, `CALL`, `RUN`, `INSPECT`, or explicit `N/A`
- cite evidence
- mark pass/fail/blocked

Do not accept when an acceptance-critical decision is unverified.
Do not treat implementation-agent or worker claims as verification evidence.

If decision verification is `blocked`:
- route to `user` when external evidence, access, or approval is missing
- route to `beo-plan` when a verification command, artifact, or mapping is missing
- route to `beo-debug` when behavior is present but the mismatch root cause is unproven

## Learning closure rule

`review -> done` is the default accepted-work closure when the accepted work is clearly isolated and no durable reusable signal exists.
In that case `beo-review` may record inline `learning_disposition: no-learning` and route to `done`.
`beo-review` must not decide durable learning content.
Route to `beo-compound` only when a durable learning candidate exists or the disposition is not obvious.

## Review fix rule

Reactive fix may route to `beo-execute` only when `beo-references -> artifacts.md` reactive-fix approval rule is fully satisfied.
Otherwise route to `beo-plan` or `beo-debug`.

## Exit routing

| Observation | Next owner |
| --- | --- |
| verdict=`accept` and `learning_disposition=no-learning` is obvious | done |
| verdict=`accept` and durable or unclear learning remains | beo-compound |
| verdict=`fix` and reactive-fix approval rule is fully satisfied | beo-execute |
| verdict=`fix` and requirements must change or be reinterpreted | beo-explore |
| verdict=`fix` and root cause is still unproven | beo-debug |
| verdict=`fix` otherwise | beo-plan |
| verdict=`reject` because requirements are wrong, unlocked, or contradicted | beo-explore |
| external decision or approval is required to resolve findings | user |

## Allowed next owners
- beo-compound
- beo-execute
- beo-plan
- beo-explore
- beo-debug
- user
- done

## Local hard stops
- Do not perform mutation-led diagnosis; route to `beo-debug` when root cause must be proven.
- Do not repair code or planning artifacts while reviewing.
- Do not emit full durable learning; only record obvious `no-learning` inline here.
- Do not convert a review finding into execution work unless the fix is already bounded inside the current approved envelope.
- Do not accept agent or worker completion claims as verification evidence; verify file state directly.
- Do not accept when an acceptance-critical locked decision is unverified.
- Before routing to `done`, inherit the terminal done rule from `beo-references -> state.md`.

## References
- `beo-references -> operator-card.md`
- `beo-references -> artifacts.md`
- `beo-references -> approval.md`
- `beo-references -> pipeline.md`
- `beo-references -> learning.md`
- `references/review-specialist-prompts.md`
