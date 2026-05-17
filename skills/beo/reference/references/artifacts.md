# Artifacts

Authority: canonical prose rules for Compact Ticket and full runtime artifact shape. Machine field authority lives in `registry/artifact-schemas.json`; approval envelope fields live in `registry/approval-envelope.json`; density selection lives in `references/density.md`.

## Compact Ticket

Compact mode presents one visible operator artifact: `TICKET.md`. Its approval-bearing and owner-bearing authority is one structured `beo.ticket` block. Markdown headings may orient humans, but helpers must not derive approval from headings. Use `references/density.md` for compact/full selection.

Future-owned fields are absent until the owning phase acts. Templates may show them as comments/placeholders only.

## Compact field ownership

- `beo-explore` owns identity seed fields, `request`, `done`, `human_gates`, `assumptions`, `non_goals`, and `constraints`.
- `beo-plan` owns `scope`, plan-owned approval-bearing `acceptance_criteria`, `generated_outputs`, `risk_scope`, `rollback_boundary`, verification contract, and plan handoff metadata.
- `beo-validate` owns `readiness`, `readiness_reason`, `selected_execution_set`, `execution_mode`, `approval_ref`, `integrity`, and validation handoff metadata.
- `beo-execute` owns `execution_status`, `pre_execution_integrity_check`, `changed_files`, `verification_evidence`, `review_status`, `blocker`, and `execution_notes`.
- `beo-review` owns `verdict`, `findings`, `review_evidence`, `closure`, and `learning_candidate`; accepted review may set `lifecycle_status: closed`.
- The owner emitting `user_abandoned` may write only abandonment lifecycle bookkeeping; this does not grant review closure or verdict authority.
- Each phase owner may update `phase_status`, `current_owner`, and optional `owner` mirror only while making a legal handoff with transition provenance. `beo-route` may update them only when resolving unsafe identity.

Compact `current_owner` is owner-bearing authority and may name any registered runtime owner. Optional compact `owner` is a display mirror and must match `current_owner` when present. `FEATURE.json.current_owner`, STATE, and HANDOFF are advisory mirrors handled by `references/state.md`; stale mirrors require `beo-route` repair but do not override compact authority.

## Full feature artifacts

Full density uses `FEATURE.json`, `CONTEXT.md`, `PLAN.md`, `TRACKER.json`, `REVIEW.md`, and `HANDOFF.json`.

- `beo-explore` owns `CONTEXT.md` requirements and Human Gates.
- `beo-plan` owns non-Approval sections of `PLAN.md`.
- `beo-validate` owns the Approval section of `PLAN.md`.
- `beo-execute` owns `TRACKER.json` execution evidence.
- `beo-review` owns `REVIEW.md` verdict, findings, review evidence, closure, and learning candidate fields.

## Human Gates

Human Gates use the shared shape in `registry/artifact-schemas.json`. Gate answers that contain secrets must store handles only, such as `env:PROVIDER_API_TOKEN`.

## Lifecycle mirror

`lifecycle_status` is feature lifecycle: `active | closed | reopened | abandoned`. Compact phase progress uses `phase_status` separately: `draft | planned | approved | executing | ready_for_review | blocked`.

## Alignment rule

Artifact prose, registries, templates, and contracted helper behavior must remain consistent. Documentation changes do not require adding new tests, evals, or checks.
