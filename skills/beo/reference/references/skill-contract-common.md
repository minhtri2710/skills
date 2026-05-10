# BEO Skill Contract Common

## Canonical vocabulary

Owners:
`beo-explore`, `beo-plan`, `beo-validate`, `beo-execute`, `beo-review`, `beo-debug`, `beo-route`, `beo-compound`, `beo-dream`, `beo-author`, `beo-reference`, `beo-setup`, `user`, `done`

Lanes:
`beo_tiny`, `standard`. Do not use `tiny`, `small`, `normal`, or `beo_standard`.

Readiness:
`PASS_EXECUTE`, `FAIL_PLAN`, `FAIL_EXPLORE`, `BLOCK_USER`, `FAIL_STATE`

Integrity:
`verified | stale | invalid | unavailable`. Do not use `valid`, `ok`, `clean`, `matched`, `pass`, `fail`, or `N/A`.

Field-level status:
`complete | missing | invalid | unavailable`. Scoped to helper sub-fields only. Must not be used for global integrity.

Execution modes:
`single`, `ordered_batch`

Review verdicts:
`accept | fix | reject`

Learning case status:
`candidate | finalized | consolidated | closed`. Do not use `draft`, `pending`, `accepted`, `archived`, or `done`.

Learning case types:
`wrong-owner-selection | unsafe-mutation-temptation | approval-scope-confusion | review-debug-confusion | human-gate-confusion | tiny-standard-confusion | route-identity-confusion | durable-workflow-learning | unclear-learning`

Owner contracts must use these canonical values only. Do not invent new statuses, lanes, modes, or case types outside this registry. Any value not listed here is invalid unless its canonical owner file is changed in the same edit.

## Shared owner stops

All owners must enforce:

- Do not write outside listed writable surfaces.
- Do not perform another owner's primary decision.
- Do not treat STATE/HANDOFF, chat, memory, display cards, or summaries as authority over current required surfaces.
- Do not use workflow-visible command output as authority unless `tool-contracts.md` defines that exact command/subcommand authority.
- Do not route to learning to bypass runtime safety.
- Do not use go-mode to bypass approval, Human Gates, owner selection, execution scope, review, or learning provenance.

Owner files reference these shared stops with:

```md
- Enforce shared owner stops from `beo-reference -> references/skill-contract-common.md`.
```

## Authority verb glossary

| Verb | Meaning |
| --- | --- |
| `grant` | Create official authority. Only owners that truly own that right may grant. |
| `record` | Write evidence or state. Does not create authority. |
| `select` | Choose an execution set or next owner when the owner holds selection rights. |
| `route` | Legal handoff. Not synonymous with artifact mutation. |
| `approve` | Only associated with `beo-validate` approval authority. |
| `verdict` | Only associated with `beo-review` terminal decision. |
| `advisory` | Reference material; no workflow authority. |
| `mirror` | Display copy; loses to canonical surface. |
| `canonical` | Source of truth with precedence. |
| `hard stop` | Mandatory stop condition. |

Avoid ambiguous phrasing:
- `safe to execute` unless clearly labeled as helper evidence only.
- `ready` unless attached to the readiness owner.
- `approval evidence` unless the reader cannot mistake it for approval authority.
- `route to X to fix` unless X owns that surface.
- `learning suggests` unless learning cannot be mistaken for doctrine.

## Owner handoff vocabulary

`Exit map` lists legal successors for an owner contract. It does not select a successor by itself.

`Next owner` is the selected successor recorded in owner output or handoff.

`Return owner` is used by debug to return a diagnostic result to the runtime owner that requested proof.

## Skill must be loaded to act

A beo skill's `SKILL.md` must be loaded before any mutation owned by that skill. Identifying `STATE.json.current_owner` is not sufficient authorization to act. The loaded skill contract's writable surfaces and hard stops must be in scope.

## Owner SKILL.md skeleton

```md
---
name: beo-<owner>
description: |
  Use this skill to <owned decision>. Use when <specific trigger state>.
  Do not use when <nearest neighbor owns this>.
---

# beo-<owner>

## Purpose
## Active when
## Owns
## Reads
## Writes
## Must stop when
## Exit map
## References
```

Target body lengths:

| Skill | Target body length |
| --- | ---:|
| `beo-route` | 45-70 lines |
| `beo-explore` | 45-70 lines |
| `beo-plan` | 55-80 lines |
| `beo-validate` | 55-85 lines |
| `beo-execute` | 55-85 lines |
| `beo-review` | 65-95 lines |
| `beo-debug` | 60-90 lines |
| `beo-compound` | 35-60 lines |
| `beo-dream` | 35-60 lines |
| `beo-reference` | 30-50 lines |
| `beo-author` | 45-70 lines |
| `beo-setup` | 70-110 lines |

## Shared exit packet

```md
Decision:
Evidence:
Changed surfaces:
Blocked by:
Next owner:
Next owner reason:
```

Rules:
- `Changed surfaces` must be `none` if no files were changed.
- `Blocked by` must be `none` if not blocked.
- `Next owner` must be allowed by the active owner contract or be `done` for terminal closure.
- Do not invent owner-specific packet fields when the shared packet is sufficient.

## Read-budget principle

Owners read only their active `SKILL.md`, current required surfaces for the active stage, and the minimum referenced procedure needed for the current owned decision.

Owner files list only read-budget exceptions beyond this principle. Do not expand read rights beyond current required surfaces.

If an owner lists more than three references, each reference must include a parenthetical trigger such as `(read only for generated outputs)`. A reference list without conditional triggers is invalid.

## Output compactness

Prefer concise operator output. Use long cards only when the active owner requires one.

## Neutral note

Owner contracts should be small. Shared rules belong in canonical references. Learning cases belong in `.beads/learnings/` and do not authorize runtime action.
