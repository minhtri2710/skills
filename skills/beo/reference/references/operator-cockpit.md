# Operator Cockpit
<!-- beo:operator-cockpit -->

Authority: canonical for operator navigation and read order only. It introduces no owner authority, artifact field, readiness rule, enum, transition, approval mechanic, or writable surface.

Start here, then load `references/runtime-kernel.md`. Before any owner acts, load the active owner `SKILL.md`, `references/skill-contract-common.md`, current required artifacts, and `registry/pipeline.json`.

## Step 1 — Classify the lane
<!-- beo:operator-cockpit:lane -->

| Lane | Use when | Entry |
|---|---|---|
| Delivery | normal feature/change | `beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> done` |
| Support | one blocker needs proof, or owner/feature identity is unsafe | `beo-debug` or `beo-route` |
| Maintenance | lookup, setup, doctrine editing, post-accepted learning | `beo-reference`, `beo-setup`, `beo-author`, `beo-learn` |

Direct setup/usage requests use `beo-setup`, not route. Direct doctrine lookup uses `beo-reference`. Direct doctrine editing uses `beo-author`.

## Step 2 — Resolve current owner
<!-- beo:operator-cockpit:owner -->

For normal runtime resume, use `references/resume-resolution.md`; it writes nothing and only orients the next read from current artifacts.

Use `beo-route` only when owner/feature identity is missing, stale, contradictory, colliding, or unsafe. Route repairs identity metadata only. STATE and HANDOFF are mirrors, never authority.

## Step 3 — Load authority
<!-- beo:operator-cockpit:authority -->

Read in this order before acting:
1. active owner `SKILL.md`;
2. `references/skill-contract-common.md`;
3. `FEATURE.json` and current density artifacts;
4. current structured authority block;
5. `registry/pipeline.json` before checking or emitting a `condition_id`.

Reload current artifacts before approval/refusal, product mutation, terminal verdict, owner identity repair, lifecycle closure, Human Gate resolution, or resume after interruption.

## Step 4 — Mutation checklist
<!-- beo:operator-cockpit:mutation -->

Product mutation is legal only when all are true:
- loaded owner is `beo-execute`;
- current artifacts contain fresh `PASS_EXECUTE`;
- approval envelope is complete and current;
- integrity is verified with evidence;
- fresh pre-mutation `beo_approval_check` output reports `approval_envelope_status: complete`;
- Human Gates are `resolved` or `not_applicable`;
- selected execution set covers the mutation;
- target path is declared and not forbidden;
- no owner/feature identity defect is active.

## Step 5 — Human Gate lifecycle
<!-- beo:operator-cockpit:human-gates -->

Human Gate lifecycle authority lives in `references/decision-boundaries.md`. In short: `beo-explore` records gate status, the user supplies required decisions/secrets/authorization, `beo-plan` stops if missing input blocks scope, `beo-validate` evaluates recorded status without resolving gates, `beo-execute` requires resolved/not-applicable status, and `beo-review` checks execution respected gates.

User chat text alone is not approval-bearing until recorded by the owning artifact owner.

## Step 6 — Compact or full
<!-- beo:operator-cockpit:density -->

Density changes ceremony only, never safety. Use `references/artifacts.md` for compact/full rules. For compact operator drafting, use `assets/operator-forms/compact-ticket.md` as advisory only and copy only fields owned by the current phase.

## Step 7 — Emit one legal condition_id
<!-- beo:operator-cockpit:condition -->

Every stop or handoff emits exactly one legal `condition_id` from the active owner contract and `registry/pipeline.json`. If stuck, do not improvise; use the shared stop shape from `references/skill-contract-common.md`.
