# Artifacts

Authority: canonical for artifact density, ownership, and human artifact shape.

## Density

BEO uses one workflow with `artifact_density: compact | full`. Density changes ceremony and artifact shape only. It never weakens approval, execution scope, review, owner authority, or fail-closed behavior.

| Density | Artifact set | Use when |
|---|---|---|
| compact | `FEATURE.json` + `HANDOFF.json` + `TICKET.md` | one bounded normal execution set with one bounded item, explicit files, direct verification, low declared risk |
| full | `FEATURE.json` + `CONTEXT.md` + `PLAN.md` + `TRACKER.json` + `REVIEW.md` + `HANDOFF.json` | multiple items, multiple execution sets, repair/rollback set, broad risk, indirect verification, complex generated outputs, multi-phase work |

Compact is allowed only when all are true: exactly one normal execution set with exactly one bounded item, explicit narrow declared files, direct verification, absent or bounded risk, absent/simple/declared generated outputs, and Human Gates are resolved or not applicable. Use full when any compact condition is false.

Density escalation is mechanical:

| Trigger | Density |
|---|---|
| One bounded change, one execution item, simple scope | compact |
| Multiple execution items | full |
| Multiple execution sets | full |
| Repair or rollback set needed | full |
| Item-level execution state tracking needed | full |
| Complex generated outputs | full |
| Multi-owner or high-risk feature | full |
| Human Gate matrix beyond simple status | full |

## FEATURE manifest

`FEATURE.json` identifies one runtime feature artifact root. It records the feature slug, density, lifecycle status, current owner mirror, contract version, timestamps, and artifact list. It is required in both compact and full density and is the anchor used by helpers to find the current artifact set.

`FEATURE.json.current_owner` is identity metadata only. It orients resume/repair, but it does not authorize action without loading the owner `SKILL.md` and reading current required artifacts.

## Ownership

| Surface/section | Owner |
|---|---|
| `TICKET.md#Request`, `#Done`, `#Human Gates` | beo-explore |
| `TICKET.md#Scope` | beo-plan |
| `TICKET.md#Approval` | beo-validate |
| `TICKET.md#Execution` | beo-execute |
| `TICKET.md#Review` | beo-review |
| `CONTEXT.md` | beo-explore |
| `PLAN.md` non-Approval sections | beo-plan |
| `PLAN.md#Approval` | beo-validate |
| `TRACKER.json` | beo-execute |
| `REVIEW.md` | beo-review |

## Compact phase-gated shape

Compact mode presents one visible operator artifact: `TICKET.md`. Its approval-bearing authority is one structured `beo.ticket.v1` block inside that artifact. Markdown headings may orient humans, but the helper treats markdown-only tickets as draft-only diagnostics and derives no approval fields from headings.

A compact `TICKET.md` grows by owner phase. Future fields are not required until the owning phase begins.

Canonical compact sections:

```md
# TICKET.md

## Request
## Done
## Human Gates
## Scope
## Approval
## Execution
## Review
```

### Explore-owned seed

Required after `beo-explore`: `artifact_density`, `owner`, `request`, `done`, `human_gates`. Optional: `assumptions`, `non_goals`, `constraints`.

Human Gate location: `TICKET.md#Human Gates`. Shape and approval-bearing semantics: `beo-reference -> references/decision-boundaries.md`.

### Plan-owned scope

Compact operators author shorthand only. For compact operator drafting, use `assets/operator-forms/compact-ticket.md` as advisory only. Canonical compact field authority remains `registry/artifact-schemas.json` and `registry/approval-envelope.json`.

Required shorthand after `beo-plan`:
- `scope.files.allow`
- `scope.files.forbid`
- `scope.item`
- `scope.verify`

The helper derives the approval-bearing projection:
- `declared_files` from `scope.files.allow`
- `forbidden_paths` from `scope.files.forbid`
- one execution set `set-1` with `kind: normal`
- execution set `files` from `scope.files.allow`
- one item `item-1` with `description` from `scope.item`
- `acceptance_criteria` from `done`
- `verification_contract` from `scope.verify`
- `generated_outputs`, `risk_scope`, and `rollback_boundary` as explicit `not_applicable` unless specified
- `non_goal_constraints` from `non_goals` or `[]` when absent

Operator-authored compact projection fields such as `declared_files`, `execution_sets`, `acceptance_criteria`, or `verification_contract` are not the target compact form. Use full density when explicit projection authoring is required.

### Validate-owned approval

Required for `PASS_EXECUTE`: `readiness`, `approval_ref`, `integrity`, `selected_execution_set`, `execution_mode`.

Approval fields are flat under the authority block. Do not nest them under `approval:`.

### Execute-owned evidence

Required for review: `pre_execution_integrity_check`, `changed_files`, `verification_evidence`, `review_status: ready_for_review`, and `blocker` showing no active blockers.

`pre_execution_integrity_check.approval_envelope_status` must reflect the helper output from the current execution attempt.

### Review-owned verdict

Required after terminal review: `verdict`, `evidence`, `findings`, `closure`. Optional: `learning`.

## Full phase-gated shape

Full artifacts are also phase-gated. Future-owned files or fields are not required until the owning phase begins.

### Explore-owned context

`CONTEXT.md` is required after `beo-explore` and contains `artifact_density`, `owner`, `request`, `done`, and `human_gates`. Optional: `assumptions`, `non_goals`, `constraints`.

In full density, `CONTEXT.md#human_gates` is canonical. A duplicated `human_gates` block in `PLAN.md` is non-authoritative and must not be used for approval.

### Plan-owned plan

`PLAN.md` non-Approval sections are required after `beo-plan` and contain `declared_files`, `forbidden_paths`, `generated_outputs`, `non_goal_constraints`, `risk_scope`, `rollback_boundary`, `execution_sets`, `acceptance_criteria`, and `verification_contract`.

Execution sets use `kind: normal | repair | rollback`. Repair and rollback are execution sets, not execution modes. Repair files must be inside `declared_files`. Rollback sets require `rollback_from_execution_set`.

### Validate-owned approval

`PLAN.md#Approval` is required for `PASS_EXECUTE` and contains flat `readiness`, `approval_ref`, `integrity`, `selected_execution_set`, and `execution_mode`.

### Execute-owned tracker

`TRACKER.json` is the Execution Ledger (`beo.execution_ledger.v1`) required for review. It records selected execution set, execution mode, pre-execution integrity check, ledger status, item statuses, changed files, observations, blockers, resume point, repair budget, scope delta requests, and rollback status. See `beo-reference -> references/execution-ledger.md`.

### Review-owned review

`REVIEW.md` is required after terminal review and contains `verdict`, `evidence`, `findings`, and `closure`. Optional: `learning`.

## Placeholder policy

Use absence for future-owned fields. Use explicit `not_applicable` only for approval-bearing fields where absence would be ambiguous: `generated_outputs`, `risk_scope`, `rollback_boundary`, and `human_gates`.
