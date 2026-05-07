# BEO Artifacts

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

| Gate ID | Type | Required | Status | Resolution ref | N/A reason | Blocks PASS_EXECUTE |
| --- | --- | --- | --- | --- | --- | --- |
```

## PLAN.md minimum

```md
# PLAN

Feature:
Context ref:
Plan status: current | stale

## Execution beads

| Bead | Purpose | Dependencies | Declared files | Forbidden paths | Generated outputs | Verification | Requirement refs | Risk proof/N/A | Rollback boundary | Human blockers |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |

## Risks

| Risk | Impact | Proof or mitigation | Status |
| --- | --- | --- | --- |

## Approval-bearing scope

## Rollback boundary

## Trace matrix

| Decision ID | Bead | Declared files | Verification | Review evidence required |
| --- | --- | --- | --- | --- |
```

Every selected bead must explicitly include requirement refs, dependency order, declared files, forbidden paths, generated outputs, verification, risk proof or valid N/A, rollback boundary, and human blockers if any. Use `[]` or `N/A: <reason>` where appropriate.

Every acceptance-critical decision in `CONTEXT.md` must appear in the `PLAN.md` Trace matrix.

Every selected bead must map back to at least one acceptance decision or to an explicit enabling/non-user-visible reason.

Missing trace coverage is a plan defect owned by `beo-plan`.

## Approval record minimum

```json
{
  "feature_slug": "feature-slug",
  "context_ref": ".beads/artifacts/feature-slug/CONTEXT.md",
  "context_hash": "sha256:...",
  "plan_ref": ".beads/artifacts/feature-slug/PLAN.md",
  "plan_hash": "sha256:...",
  "bead_graph_hash": "sha256:...",
  "verification_hash": "sha256:...",
  "risk_scope_hash": "sha256:...",
  "approved_scope": [],
  "approved_forbidden_paths": [],
  "approved_generated_outputs": [],
  "approved_execution_mode": "single",
  "approved_execution_set_id": "set-1",
  "approved_execution_set_beads": ["bead-1"],
  "approval_kind": "execution_approval",
  "validated_by": "beo-validate",
  "user_authorization_ref": "chat message / ticket / policy ref / N/A: not required",
  "approval_evidence_ref": "validation evidence summary",
  "approved_at": "..."
}
```


## Approval hash and authorization fields

Approval record authorization fields separate user or policy authorization from execution approval:

- `user_authorization_ref` records required user, approval, UAT, access, secret, legal, business, or policy authorization, or `N/A: <reason>` when not applicable.
- `approval_kind=execution_approval` records that the approval is a validate-owned execution envelope decision.
- `validated_by=beo-validate` records the owner that created or refreshed the execution approval record.
- `approval_evidence_ref` records validation evidence summary, not raw secret material.

Hash fields are computed from the canonical artifact content that defines the approved envelope:

- `context_hash`: full locked `CONTEXT.md`
- `plan_hash`: full current `PLAN.md`
- `bead_graph_hash`: `PLAN.md` Execution Beads table
- `verification_hash`: verification cells/section for selected beads
- `risk_scope_hash`: Risks, Approval-bearing scope, Generated outputs, Forbidden paths, and Rollback boundary

When exact hashing is impractical, approval is stale. Fingerprint summaries are diagnostic only and do not authorize `PASS_EXECUTE` or `accept`.

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
    "files": {
      "path/to/file": {
        "status": "clean | modified | untracked | absent",
        "hash": "sha256:..."
      }
    }
  },
  "aggregate_changed_files": [],
  "aggregate_generated_files": [
    {
      "path": "path/to/file",
      "class": "declared_output | verification_byproduct | unexpected_output",
      "source": "selected bead or verification command",
      "hash": "sha256:..."
    }
  ],
  "final_file_hashes": {
    "path/to/file": "sha256:..."
  },
  "verification": [
    {
      "id": "V1",
      "type": "RUN | SEE | CALL | INSPECT | N/A",
      "target": "command, UI state, API call, file, artifact, or decision checked",
      "command": "required only when type=RUN",
      "cwd": "required only when type=RUN",
      "result": "pass | fail | blocked | not_applicable",
      "evidence": "short evidence summary or log/output ref",
      "n_a_reason": "required only when type=N/A"
    }
  ],
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

| Decision ID | Type | Evidence | Result | N/A reason |
| --- | --- | --- | --- | --- |

## Trace review

| Decision ID | Planned evidence | Execution evidence | Review result | Gap |
| --- | --- | --- | --- | --- |

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
- P3: informational note or style/maintainability observation. Does not block accept and does not require follow-up unless reviewer explicitly records one.


## Bead graph authority

`PLAN.md` is the canonical bead graph.

The `PLAN.md` execution bead table is the source of truth for bead ids, dependency order, declared files, forbidden paths, generated outputs, verification, risk proof or N/A, rollback boundary, and human blockers.

External bead databases, CLI views, or project trackers are optional support only. They must not override `PLAN.md`, approval records, readiness records, or owner hard stops.

`beo-plan` owns updates to the `PLAN.md` execution bead table.

`beo-validate` reads the `PLAN.md` execution bead table to select execution sets.

## Decision Verification rules

Every acceptance-critical locked decision must have one row.

Allowed types: `SEE`, `CALL`, `RUN`, `INSPECT`, `N/A`.

`N/A` requires a reason. Missing rows or `N/A` without reason block `accept`.

## Review hash comparison

Review compares baseline hash, finalized bundle hash, and live hash for every changed/generated file.

Generated files must be covered by `final_file_hashes`.

## Security/privacy applicability

Security/privacy lens is applicable when changed scope touches auth, permissions, secrets, PII, billing, migrations, destructive operations, external network calls, irreversible side effects, or legal/compliance behavior.

## Secret Human Gates

For `secret` gates, record only that the secret was provided or access was confirmed. Do not record the secret value.

## Field-name mapping

| Concept | STATE.json | approval-record.json | readiness-record.json | execution-bundle.json |
| --- | --- | --- | --- | --- |
| Execution mode | `execution_mode` | `approved_execution_mode` | `execution_set_selection.execution_mode` | `execution_mode` |
| Execution set id | `execution_set_id` | `approved_execution_set_id` | `execution_set_selection.execution_set_id` | `execution_set_id` |
| Selected beads | `execution_set_beads` | `approved_execution_set_beads` | `execution_set_selection.execution_set_beads` | `selected_beads` |

All matching concepts must agree before `PASS_EXECUTE`.


## Verification evidence rules

Verification evidence must be specific enough for review to distinguish checked behavior from assumed behavior.

For `RUN`, record command, cwd, result, and evidence summary or output ref.

For `SEE`, `CALL`, and `INSPECT`, record target, result, and evidence.

For `N/A`, record a reason. Missing N/A reason blocks accept.

## Trace review rule

Review must not accept if any acceptance-critical decision lacks trace from `CONTEXT.md` to `PLAN.md`, execution evidence, and review evidence.

## Generated output classification

Every generated file in the execution bundle must be classified as one of:

- `declared_output`
- `verification_byproduct`
- `unexpected_output`

`unexpected_output` blocks accept unless repaired through the legal owner path.

`verification_byproduct` is allowed only when produced by an approved verification/build command and recorded in `execution-bundle.json`.

## Human Gate values

Type: `clarification | approval | UAT | external_access | secret | legal_business`

Required: `yes | no`

Status: `unresolved | resolved | not_applicable`

Blocks PASS_EXECUTE: `yes | no`

## Removed legacy artifact concepts

Do not use dirty-baseline naming, worktree-local feature uniqueness, partial-progress records, parallel worker artifacts, or claim records across workers.
