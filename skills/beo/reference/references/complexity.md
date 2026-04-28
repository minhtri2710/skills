# Complexity

## Ceremony modes

Ceremony modes describe presentation compactness. They do not change owner routing, approval, verification, or review obligations.

| Predicate | Mode |
| --- | --- |
| one phase, one bead, one isolated file scope, one verification path, requirements locked, no migration, no security/privacy, no cross-subsystem work | micro-compact |
| single phase, one subsystem, 1-3 beads, no migration, no security/privacy boundary change | compact |
| multi-phase, migration, architecture change, security/privacy risk, cross-subsystem work, uncertain sequencing, or swarm candidate | expanded |

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
- risk map
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
- explicit proof/spike requirements for HIGH risks
- rollback expectation and pivot signals
- deeper review expectations captured through verification and UAT evidence needs

## Hard stops

- Complexity class must not bypass owner routing.
- Complexity class must not bypass `beo-validate`.
- Complexity class only changes required planning depth and review intensity.
- Do not treat `small_change` as permission to omit file scope, forbidden paths when relevant, verification, approval, or review.
- Do not treat `high_risk_feature` as permission to add release gates or new owner skills.

## Decision matrix

| Condition | Ceremony | Planning depth |
| --- | --- | --- |
| 1 file, 1 bead, 1 verification path, no ambiguity, LOW risk | `micro-compact` | `small_change` |
| <= 3 files, bounded file scope, no API/data/security/privacy impact | `compact` | `small_change` |
| 1 subsystem, 1-3 beads, bounded MED risk, no migration/security/privacy | `compact` or `expanded` | `standard_feature` |
| multi-phase, migration, architecture, security/privacy, cross-subsystem, HIGH risk | `expanded` | `high_risk_feature` |
| at least 2 isolated approved beads plus dependency proof | `expanded` if needed | swarm candidate after `beo-validate` |

## Micro-compact default

Default to `micro-compact` when work is low-risk, single-feature, single-bead, single-file or tightly bounded, and has one obvious verification path.

Use `micro-compact` by default when all are true:
- locked requirements exist;
- one current phase is enough;
- one bead is enough;
- one isolated file scope is enough;
- one verification path is enough;
- no migration, security/privacy boundary, architecture change, cross-subsystem risk, or swarm candidacy exists.

`micro-compact` reduces prose, not gates.
It must still preserve:
- locked requirements
- explicit file scope
- forbidden paths when relevant
- verification
- approval
- review verdict

If acceptance, non-goals, compatibility, constraints, or user-visible scope remain ambiguous, do not use `micro-compact` even when implementation size is tiny.
A valid micro-compact plan must still keep one current phase, one bead id, `Goal`, `Scope`, `Acceptance`, `Dependencies`, `File scope`, and `Verification` explicit.

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
| Bead | Goal | Scope | Acceptance | File scope | Dependencies | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| B1 |  |  |  |  | none |  |

## File Scope
- approved candidate write scope:
- forbidden paths:

## Verification Plan
| Command/check | Owner | Required for | Pass signal |
| --- | --- | --- | --- |
| <command> | beo-validate | selected bead | passing output |

## Execution Envelope Proposal
- Selected bead or isolated bead set: B1
- Proposed mode: serial
- Approval subject:
- Approval invalidation triggers:
- forbidden paths:
```

## Tiny-work happy path

For tiny work with locked requirements, one bead, one file scope, and one verification path:

`beo-explore -> beo-plan(micro-compact/small_change) -> beo-validate(PASS_SERIAL) -> beo-execute -> beo-review -> done(no-learning)`

This path reduces prose only. It does not relax approval, scope, forbidden-path, or verification requirements.

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
- mode: `serial`

execution-bundle.json
- executed_beads: [B1]
- changed_files: [`config/app.yaml`]
- verification: [`npm test -- config-defaults`]
- scope_respected: true

REVIEW.md
- verdict: `accept` when verification is complete, approval scope matches, and only P2/P3 findings remain if any.
```
