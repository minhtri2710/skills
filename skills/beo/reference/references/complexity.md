## Contents

- Ceremony modes
- Planning depth classes
- Hard stops
- Decision matrix
- Mode selection table
- Micro-compact default
- Context Binding
- Approach
- Current Phase Contract
- Bead Graph
- File Scope
- Verification Plan
- Execution Envelope Proposal

# Complexity

## Ceremony modes

Ceremony modes describe presentation compactness. They do not change owner routing, approval, verification, or review obligations.

| Predicate | Mode |
| --- | --- |
| one phase, one bead, one isolated file scope, one verification path, requirements locked, no migration, no security/privacy, no cross-subsystem work | micro-compact |
| single phase, one subsystem, 1-3 beads, no migration, no security/privacy boundary change | compact |
| multi-phase, migration, architecture change, security/privacy risk, cross-subsystem work, uncertain sequencing, or local_parallel execution set candidate | expanded |

## Planning depth classes

Planning depth classes describe how much discovery, phase mapping, risk proof, and story mapping the plan must carry. They are not route modes and must not bypass `beo-validate`.

### small_change

Use when all are true:
- <= 3 files expected
- no new API or data model
- no migration, security, or privacy surface
- LOW risk
- no gray-area requirement
- one current phase is enough

Required `PLAN.md` sections:
- context binding
- minimal approach
- current phase contract
- bead graph
- file scope
- verification plan
- execution envelope proposal

Rules:
- still requires `beo-validate`
- never skips approval/readiness classification
- may use `micro-compact` or `compact` ceremony when the required sections remain explicit

### standard_feature

Use when any are true:
- normal feature or refactor
- moderate scope
- multiple stories or files
- bounded MED risk exists

Required `PLAN.md` sections:
- context binding
- applicable prior learning consulted
- discovery facts when needed
- approach
- risk map with proof required for each MED risk that can affect acceptance, scope, verification, rollback, security, privacy, migration behavior, or compatibility
- current phase contract
- story map
- bead graph
- file scope
- verification plan
- execution envelope proposal

### high_risk_feature

Use when any are true:
- cross-cutting architecture
- migration, data, security, or privacy impact
- high blast radius
- uncertain integration
- multi-phase delivery likely
- HIGH risk remains after initial exploration

Required `PLAN.md` sections:
- all standard sections
- whole-feature phase map when feature cannot safely ship in one phase
- explicit proof/spike/manual-decision requirements for every HIGH risk before execution
- rollback expectation and pivot signals
- deeper review expectations captured through verification and UAT evidence needs

## Hard stops

- Ceremony modes affect presentation compactness only.
- Planning depth classes affect required `PLAN.md` content only.
- Neither ceremony mode nor planning depth may bypass `beo-validate`, execution approval, verification, or `beo-review`.
- Complexity class must not bypass owner routing.
- Complexity class must not bypass `beo-validate`.
- Complexity class only changes required planning depth and review intensity.
- Do not treat `small_change` as permission to omit file scope, forbidden paths (use `[]` when none apply), verification, approval, or review.
- Do not treat `high_risk_feature` as permission to add release gates or new owner skills.
- Do not introduce `TINY_SAFE`, `tiny_safe`, or any equivalent formal shortcut that skips locked requirements, plan, validation, approval, verification, execution evidence, or review.
- One-line auth, permission, security, privacy, migration, data, or irreversible-action changes are not shortcut-eligible.

## Decision matrix

| Condition | Ceremony | Planning depth |
| --- | --- | --- |
| 1 file, 1 bead, 1 verification path, no ambiguity, LOW risk | `micro-compact` | `small_change` |
| <= 3 files, bounded file scope, no API/data/security/privacy impact | `compact` | `small_change` |
| 1 subsystem, 1-3 beads, bounded MED risk, no migration/security/privacy | `compact` or `expanded` | `standard_feature` |
| multi-phase, migration, architecture, security/privacy, cross-subsystem, HIGH risk | `expanded` | `high_risk_feature` |
| at least 2 isolated approved beads plus dependency proof | `expanded` if needed | `standard_feature` or `high_risk_feature` as applicable; `local_parallel` execution mode is determined by `beo-validate`, not by planning depth |

## Compact mode decision table

Compact mode reduces wording, not authority checks.

| Condition | Mode | Still required |
| --- | --- | --- |
| One isolated copy/config/test change, one file, no ambiguity | `micro-compact` | requirements lock, plan, validate, execute, review |
| One small bugfix with known defect location | `small_change` | scope, approval, verification, review |
| Unknown root cause | not compact yet | `beo-debug` before fix path |
| Cross-file behavior change | `standard_feature` | full planning depth |
| Acceptance, non-goals, compatibility, or constraints unclear | explore first | no planning or execution |
| Approval stale or scope changed | validate first | no execution |

## Mode selection table

The execution mode is determined by `beo-validate` from the bead graph. Use this table as a planning guide only; `beo-validate` owns the final mode classification.

| Bead count | Dependency shape | File/output scope overlap | Recommended execution mode | Notes |
| --- | --- | --- | --- | --- |
| 1 | any | any | `single` | Always safe; default for any single bead |
| 2+ | ordered chain (B depends on A) | none | `ordered_batch` | Beads have sequential dependencies; each bead starts only after the prior completes |
| 2+ | none (all independent) | none | `local_parallel` | No shared files or outputs; one shared current approval envelope covers all beads; all beads may proceed simultaneously |
| 2+ | ordered chain (B depends on A) | overlap exists | `ordered_batch` | Sequential execution makes overlap safe; each bead completes before the next writes to shared scope |
| 2+ | independent (no explicit order) | any overlap exists | route to `beo-plan` — split or add explicit ordering | Independent beads with overlapping scope cannot be classified as a valid execution mode; establish a dependency chain or split beads to eliminate overlap, then re-validate |

Rules:
- `local_parallel` requires zero file-scope or generated-output overlap across all beads in the set.
- `ordered_batch` requires explicit dependency edges in the bead graph; do not infer dependency from proximity.
- `single` requires exactly one bead; do not use `single` as a fallback for multiple overlapping beads.
- When in doubt, split until overlap is eliminated, then classify mode.
- Mode selection does not bypass `beo-validate`; this table informs planning, not approval.

## Micro-compact default

Default to `micro-compact` when work is low-risk, single-feature, single-bead, single-file or tightly bounded, and has one obvious verification path.

Use `micro-compact` by default when all are true:
- locked requirements exist;
- one current phase is enough;
- one bead is enough;
- one file scope with no cross-file dependencies, shared state, or cross-subsystem boundary is enough;
- one verification path is enough;
- no migration, security/privacy boundary, architecture change, cross-subsystem risk, or local_parallel multi-bead selection required.

`micro-compact` reduces prose, not gates.
It must still preserve:
- locked requirements
- explicit file scope
- forbidden paths when relevant
- verification
- approval
- review verdict

If acceptance, non-goals, compatibility, constraints, or user-visible scope remain ambiguous, do not use `micro-compact` even when implementation size is tiny.
A valid micro-compact plan must still keep one current phase, one bead id, `Goal`, `Scope`, `Acceptance`, `File scope`, `Forbidden paths`, `Generated outputs`, `Dependencies`, and `Verification` explicit.

### Canonical micro-compact template

```md
## Context Binding
- Feature:
- CONTEXT ref:
- Locked decision IDs:
- Planning depth: small_change

## Approach
- Minimal approach:

## Current Phase Contract
- entry state:
- exit state:
- demo or inspectable result:
- explicit out-of-scope:

## Bead Graph
| Bead | Goal | Scope | Acceptance | File scope | Generated outputs | Dependencies | Verification |
| --- | --- | --- | --- | --- | --- | --- | --- |
| B1 |  |  |  |  | none | none |  |

## File Scope
- approved candidate write scope:
- generated outputs:
- forbidden paths:

## Verification Plan
| Command/check | Owner | Required for | Pass signal |
| --- | --- | --- | --- |
| <command> | beo-validate | selected bead | passing output |

## Execution Envelope Proposal
- Selected bead or isolated bead set: B1
- Proposed mode: single
- Approval subject:
- Approval invalidation triggers:
- forbidden paths:
```

## Tiny-work happy path

For tiny work with locked requirements, one bead, one file scope, and one verification path:

`beo-explore -> beo-plan(micro-compact/small_change) -> beo-validate(PASS_EXECUTE) -> beo-execute -> beo-review -> done(no-learning)`

This path reduces prose only. It does not relax approval, scope, forbidden-path, or verification requirements.

## Small-change compact examples

These examples illustrate compact expression only. Each still requires locked
context, explicit file scope, verification, validation, execution, and review.

| Case | Compact shape |
| --- | --- |
| tiny UI copy change | one locked copy decision, one UI file, visual/text inspection plus focused test when available |
| one-file bugfix | one failure statement, one implementation file, regression test or exact repro command |
| one-test-only verification change | acceptance is test coverage only, test file scope only, target test command must fail before/pass after when applicable |
| low-risk config tweak | one config key/value decision, config file scope only, config/defaults validation command |

## Compact end-to-end example

Use this shape when one isolated change can move through the workflow without hidden scope:

```md
beo-explore -> beo-plan -> beo-validate -> beo-execute -> beo-review -> beo-compound/done

CONTEXT.md
- acceptance: config default is corrected
- non-goals: no runtime behavior redesign
- compatibility: existing config keys unchanged
- constraints: only `config/app.yaml`

PLAN.md
- Planning depth: small_change
- current phase contract: ship one isolated config fix
- bead B1
  - Goal: correct the default value
  - Scope: one config edit only
  - File scope: `config/app.yaml`
  - Verification: `npm test -- config-defaults`

approval-record.json
- approved_beads: [B1]
- approved_file_scope: [`config/app.yaml`]
- forbidden_paths: [`src/**`]
- verification_commands: [`npm test -- config-defaults`]
- execution_mode: `single`

execution-bundle.json
- executed_beads: [B1]
- per_bead_changed_files: {B1: [`config/app.yaml`]}
- aggregate_changed_files: [`config/app.yaml`]
- per_bead_generated_files: {B1: []}
- aggregate_generated_files: []
- verification: [`npm test -- config-defaults`]
- scope_respected: true

REVIEW.md
- verdict: `accept` when verification is complete, approval scope matches, and only P2/P3 findings remain if any.
```
