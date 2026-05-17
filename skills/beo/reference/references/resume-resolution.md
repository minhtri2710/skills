# Resume Resolution
<!-- beo:resume-resolution -->

Authority: canonical read-only resume orientation. It writes nothing.

## Rule
<!-- beo:resume-resolution:rule -->

When resuming, read current artifacts before acting. If owner/feature identity is unsafe, use `beo-route` before normal resume.

## Owner orientation
<!-- beo:resume-resolution:owner-orientation -->

Apply the first matching rule:
1. Owner/feature identity is unsafe -> `beo-route`.
2. Artifacts are contradictory and no legal owner can repair safely -> `user`.
3. Accepted verdict has explicit learning candidate (`verdict_accept_learning_candidate`) and no finalized learning case exists -> `beo-learn`.
4. Lifecycle is `closed` or `abandoned`, accepted verdict (`verdict_accept`) has no pending learning handoff, or required learning is already recorded -> `done`.
5. Review verdict `fix` has unproven root cause (`verdict_fix_unproven_root_cause`) -> `beo-debug`.
6. Review verdict `fix` or `reject` has bounded/proven repair need (`verdict_fix_bounded_repair` or `verdict_reject`) -> `beo-plan`.
7. Execution evidence is `ready_for_review` (`execution_ready_for_review`) -> `beo-review`.
8. Current valid `PASS_EXECUTE` exists -> `beo-execute`.
9. Complete executable plan exists without current approval (`plan_complete` already emitted or equivalent artifact evidence) -> `beo-validate`.
10. Locked requirements exist without complete plan (`requirements_locked`) -> `beo-plan`.
11. Request exists but requirements are incomplete or contradicted -> `beo-explore`.

## Output
<!-- beo:resume-resolution:output -->

Report the selected owner/source, artifact evidence used, and whether any Human Gate or approval condition blocks action.

## Route boundary
<!-- beo:resume-resolution:route-boundary -->

Resume orients. Route repairs unsafe identity. Do not use route for normal startup, direct setup/usage requests, or ordinary owner handoff.

## Meta-target boundary

Resume may orient after `return_to_caller` or `restored_owner` only when `beo-reference -> references/transition-provenance.md` has first validated fresh provenance. Resume must not resolve meta-targets from chat memory or STATE alone.
