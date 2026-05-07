# BEO Artifacts v2

## Required runtime artifacts

- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when pausing or transferring
- `.beads/artifacts/<feature_slug>/CONTEXT.md`
- `.beads/artifacts/<feature_slug>/PLAN.md`
- `.beads/artifacts/<feature_slug>/approval-record.json`
- `.beads/artifacts/<feature_slug>/readiness-record.json`
- `.beads/artifacts/<feature_slug>/execution-bundle.json`
- `.beads/artifacts/<feature_slug>/REVIEW.md`
- `.beads/learnings/<feature_slug>.md` only if compound learning is needed

## CONTEXT.md minimum

```md
# CONTEXT

Feature:
Status: locked | unlocked

## User-visible goal

## Acceptance decisions

| ID | Decision | Source | Locked |
| --- | --- | --- | --- |

## Non-goals

## Compatibility constraints

## Human Gates

| Gate | Type | Status | Resolution |
| --- | --- | --- | --- |
```

## PLAN.md minimum

```md
# PLAN

Feature:
Context ref:
Plan status: current | stale

## Execution beads

| Bead | Purpose | Dependencies | Declared files | Forbidden paths | Generated outputs | Verification |
| --- | --- | --- | --- | --- | --- | --- |

## Risks

| Risk | Impact | Proof or mitigation | Status |
| --- | --- | --- | --- |

## Approval-bearing scope

## Rollback boundary
```

Every selected bead must explicitly include requirement refs, dependency order, declared files, forbidden paths, generated outputs, verification, risk proof or valid N/A, rollback boundary, and human blockers if any. Use `[]` or `N/A: <reason>` where appropriate.

## Approval record minimum

```json
{
  "feature_slug": "feature-slug",
  "context_ref": ".beads/artifacts/feature-slug/CONTEXT.md",
  "plan_ref": ".beads/artifacts/feature-slug/PLAN.md",
  "approved_scope": [],
  "approved_execution_mode": "single",
  "approved_execution_set_id": "set-1",
  "approved_execution_set_beads": ["bead-1"],
  "approved_at": "...",
  "approved_by": "user"
}
```

## Readiness record minimum

```json
{
  "feature_slug": "feature-slug",
  "readiness": "PASS_EXECUTE",
  "classification_inputs": {
    "requirements_locked": true,
    "plan_current": true,
    "approval_current": true
  },
  "approval_action": {
    "approval_ref": ".beads/artifacts/feature-slug/approval-record.json"
  },
  "execution_set_selection": {
    "execution_mode": "single",
    "execution_set_id": "set-1",
    "execution_set_beads": ["bead-1"]
  },
  "state_mirror_write_check": {
    "written": true
  },
  "created_at": "..."
}
```

Only `beo-validate` may emit or refresh `PASS_EXECUTE` readiness records.

## Execution bundle minimum

```json
{
  "feature_slug": "feature-slug",
  "execution_set_id": "set-1",
  "execution_mode": "single",
  "selected_beads": ["bead-1"],
  "approval_ref": ".beads/artifacts/feature-slug/approval-record.json",
  "file_change_baseline": {
    "captured_at": "...",
    "files": []
  },
  "aggregate_changed_files": [],
  "aggregate_generated_files": [],
  "changed_file_hashes": {},
  "verification": [],
  "ready_for_review": true,
  "finalized_at": "..."
}
```

Finalized execution bundle must include every changed/generated file and hash coverage for review.

Generated outputs are in scope only when declared by the approved plan or unavoidably produced by an approved verification/build step and recorded in the execution bundle.

## REVIEW.md minimum

```md
# REVIEW

Verdict: accept | fix | reject

## Approval/Scope Lens

| File | Live change | Bundle | Approved scope | Hash match | Finding |
| --- | --- | --- | --- | --- | --- |

## Decision Verification

| Decision | Evidence | Result |
| --- | --- | --- |

## Findings

| Severity | Finding | Blocking | Rationale |
| --- | --- | --- | --- |

## Learning disposition

no-learning | durable-candidate | unclear | rejection-retrospective
```

## Review severity

- P0: critical correctness, security, data loss, or destructive behavior. Blocks accept.
- P1: major acceptance, scope, compatibility, or verification failure. Blocks accept.
- P2: minor issue. May be accepted only with explicit non-blocking rationale.

## Removed legacy artifact concepts

Do not use dirty-baseline naming, worktree-local feature uniqueness, partial-progress records, parallel worker artifacts, or claim records across workers.
