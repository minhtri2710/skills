# Approval

Authority: canonical approval semantics. Machine fields live in `registry/approval-envelope.json`.

## Core rule

Only `beo-validate` can grant `PASS_EXECUTE`. `beo-execute` may mutate product files only inside the exact approved scope and only after fresh `beo_approval_check` output reports `approval_envelope_status: complete`.

## What approval must name

A valid approval binds the registry-defined envelope in `registry/approval-envelope.json`, including:
- readiness: `PASS_EXECUTE`;
- selected execution set;
- execution mode;
- approval ref with `approved_by_owner: beo-validate`;
- approval-bearing projection hash;
- Human Gates status;
- integrity evidence.

Compact approval uses the `beo.ticket` authority block and records `approval_ref.approval_projection_rule: compact_derived`. Full approval uses `CONTEXT.md` plus `PLAN.md` and records `full_plan_explicit`.

## Stale or invalid approval

Approval is stale or invalid when approval-bearing fields, declared files, selected execution set, verification contract, Human Gate status, approval ref, integrity evidence, or artifact hashes no longer match the approved projection. Missing, stale, invalid, contradictory, or unavailable approval stops execution and returns to `beo-validate`.

## Failure readiness

Non-`PASS_EXECUTE` readiness records `readiness` and `readiness_reason`; it does not synthesize approval authority, selected execution set, execution mode, or verified integrity.

## Scope binding

No owner may silently widen approved scope. If execution needs a file, item, generated output, risk, rollback, or verification change outside approval, stop to `beo-plan` or `beo-validate` as required by the active owner contract.

## Helper boundary

`beo_approval_check` verifies integrity; it does not grant approval, refresh approval, select execution sets, or emit a verdict.

## Validate atomicity

`beo-validate` remains one owner. Projection check, Human Gate check, scope binding check, approval ref emission, integrity record, and handoff emission are method labels only; they are not separate owners or independent approval sources.
