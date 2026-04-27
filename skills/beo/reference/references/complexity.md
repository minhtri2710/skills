# Complexity

## Mode selection

| Predicate | Mode |
| --- | --- |
| one phase, one bead, one isolated file scope, one verification path, requirements locked, no migration, no security/privacy, no cross-subsystem work | micro-compact |
| single phase, one subsystem, 1-3 beads, no migration, no security/privacy boundary change | compact |
| multi-phase, migration, architecture change, security/privacy risk, cross-subsystem work, uncertain sequencing, or swarm candidate | expanded |

## Decision matrix

| Condition | Mode |
| --- | --- |
| 1 file, 1 bead, 1 verification path, no ambiguity, low risk | `micro-compact` |
| 1 subsystem, 1-3 beads, no migration/security | `compact` |
| multi-phase, migration, architecture, security/privacy, cross-subsystem | `expanded` |
| at least 2 isolated approved beads plus dependency proof | swarm candidate after `beo-validate` |

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
## Current phase
- Ship one tiny approved change.

## Bead B1
- Goal:
- Scope:
- Acceptance:
- Dependencies: none
- File scope:
- Forbidden paths:
- Verification:
```

## Tiny-work happy path

For tiny work with locked requirements, one bead, one file scope, and one verification path:

`beo-explore -> beo-plan(micro-compact) -> beo-validate(PASS_SERIAL) -> beo-execute -> beo-review -> done(no-learning)`

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
- current phase: ship one isolated config fix
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
