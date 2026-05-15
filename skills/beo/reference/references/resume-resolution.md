# Resume Resolution
<!-- beo:resume-resolution -->

Authority: canonical for read-only normal resume owner orientation. It writes nothing, grants no owner authority, emits no `condition_id`, and never selects setup or usage utilities from runtime artifacts.

## Rule
<!-- beo:resume-resolution:rule -->

Use resume resolution after context loss or interruption when current artifacts are present and owner/feature identity is not unsafe. Read artifacts first; use STATE and HANDOFF only as mirrors to locate and compare artifact evidence.

Resume resolution is not `HANDOFF.json`, STATE repair, approval, a transition, or permission to skip owner entry checks. The oriented owner must still load its `SKILL.md`, load `beo-reference -> references/skill-contract-common.md`, read current required artifacts, and verify entry conditions before acting.

If owner/feature identity is missing, stale, contradictory, colliding, or unsafe, stop normal resume and use `beo-route` for identity repair.

## Owner orientation
<!-- beo:resume-resolution:owner-orientation -->

Evaluate current artifacts in order. First matching non-contradictory artifact state orients the next read. If no artifact-derived owner is safe, stop for user decision.

| Priority | Artifact evidence | Oriented owner/source |
|---:|---|---|
| 1 | artifacts contradictory and no legal owner can repair safely | user |
| 2 | accepted verdict with explicit learning candidate and no finalized learning case has been recorded | beo-learn |
| 3 | terminal accepted, closed, abandoned, or learning already recorded lifecycle | done |
| 4 | review verdict `fix` with unproven root cause | beo-debug |
| 5 | review verdict `fix`/`reject` with bounded or proven repair need | beo-plan |
| 6 | execution evidence `ready_for_review` | beo-review |
| 7 | current valid `PASS_EXECUTE` | beo-execute |
| 8 | complete executable plan without current approval | beo-validate |
| 9 | locked requirements without complete plan | beo-plan |
| 10 | request exists but requirements are incomplete or contradicted | beo-explore |
| 11 | no safe artifact-derived owner | user |

This table orients runtime owners and terminal/user results only. Direct setup/usage requests use `beo-setup`; direct reference lookup uses `beo-reference`; direct doctrine editing uses `beo-author`.

## Orientation output
<!-- beo:resume-resolution:output -->

When reporting resume orientation, use this shape:

```yaml
resume_resolution_report:
  authority: orientation_only_not_handoff
  status: oriented | unsafe | user_decision_needed
  oriented_owner: <runtime_owner | done | user>
  evidence_refs:
    - <artifact/path/section>
  required_next_read:
    - active owner SKILL.md
    - beo-reference -> references/skill-contract-common.md
    - current required artifacts
  notes: <bounded note>
```

The report is advisory orientation only. It does not authorize mutation, grant approval, repair STATE/HANDOFF, emit a pipeline condition, or replace owner entry checks.

## Route boundary
<!-- beo:resume-resolution:route-boundary -->

Normal resume uses current artifacts to orient the next legal read. Route is only for unsafe owner/feature identity repair: missing, stale, contradictory, colliding, or unsafe identity metadata. After route repairs identity metadata, concrete target orientation comes back through this reference; `restored_owner` is symbolic and not a concrete owner by itself.
