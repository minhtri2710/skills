# BEO Skills

BEO is a repo-local Agent Skills package for safe Beads-backed delivery.

Install/copy/validate the whole `skills/beo/` sibling set together because delivery skills share `skills/beo/beo-reference/{references,registry,scripts}`.

## Agent loading rule

Do not eagerly load all BEO references. Load:

1. the selected skill card,
2. `beo-reference/references/doctrine-map.md`,
3. then only the narrow reference or registry required for the current decision.

## Skill classes

### Delivery owners

- `beo-plan`
- `beo-validate`
- `beo-execute`
- `beo-review`

### Support subroutines

- `beo-debug`
- `beo-learn`

### Maintenance

- `beo-author`
- `beo-climate`
- `beo-setup`

### Read-only lookup

- `beo-reference`

## Normal delivery path

`beo-plan -> beo-validate -> beo-execute -> beo-review`

Support skills do not advance delivery state unless a delivery owner routes to them and then consumes their result.

## Minimal agent path

1. Pick or inspect exactly one bead with `br`; use `bv` only for read-only graph orientation.
2. Use `beo-plan` to claim the bead. For epics/features, brainstorm the request with recommended questions, write `.beads/artifacts/<issue-id>/PLAN.md`, validate it, then decompose into atomic child beads. For epics/features, `PLAN.md` is the only parent planning artifact; child beads are created only after `beo-validate` emits `plan_validated`. For atomic beads, author `TICKET.yaml`.
3. Use `beo-validate` to validate epic/feature plan readiness or grant/deny `PASS_EXECUTE` for an atomic ticket.
4. Use `beo-execute` to select one ready approved atomic bead, mutate approved scope, and record evidence.
5. Use `beo-review` to review the atomic bead/task evidence, accept, repair, diagnose, or route to user.

## Canonical lookup

Start with `beo-reference/references/doctrine-map.md`.

Hard invariants live in `beo-reference/references/kernel.md`.
Artifact boundaries live in `beo-reference/references/artifact-boundaries.md`.
Machine-readable contracts live in `beo-reference/registry/`.
Helper index lives in `beo-reference/references/command-manifest.md`.
Per-phase context budget lives in `beo-reference/references/context-budget.md`.

## Verification, scoring, and audit

BEO ships advisory helpers in `beo-reference/scripts/` for queryable verification, quality-tiered scoring, and control-plane drift detection. These are owned by the delivery skills that invoke them and never grant authority.

- `beo_verify.py` (Verification): runs `TICKET.yaml.scope.verify.commands` and appends `verification_run` events. Added to `approval_bearing_contracts` because it is machine-enforced.
- `beo_score_trace.py`, `beo_score_context.py` (Scoring): advisory scoring against tier requirements (minimal/standard/detailed). Output score 0-3 plus a diff of missing fields.
- `beo_audit.py` (Audit): drift checks across skill cards, registries, references, must_not lists, and the command manifest. `--check-manifest` enables manifest drift detection.
- `beo_propose.py` (Audit): generates `beo-climate/proposals/pending/prop-*.md` from friction/learning-candidate events. Never applies changes.

`beo_reference` (lookup) routes operators to the right helper via `references/command-manifest.md`. See `references/command-manifest.md` for the full helper index, output shape, and exit code contract.
