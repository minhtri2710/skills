# bead-ops

Role: APPENDIX
Allowed content only: local bead mutation sequence and dependency-field constraints; canonical shared command forms remain in `beo-reference -> cli.md`

## Bead mutation command forms

Use canonical `br create`, `br update`, `br comments add`, `br dep add`, and `br sync --flush-only` forms from `beo-reference -> cli.md`. This appendix owns when `beo-plan` uses them, not their reusable syntax.

## Required bead description block

```md
Goal:
Scope:
Acceptance:
File scope:
Forbidden paths:
Dependencies:
Verification:
Swarm eligibility:
```

## Dependency constraints

- No dependency cycles.
- No child bead is ready before parent completion.
- No concurrent swarm dispatch when a dependency edge exists between beads.
- No overlapping mutable file scopes unless the overlap is explicitly read-only.
- Cross-phase dependencies must name the phase boundary and blocking predecessor.

## File scope constraints

- Every mutable path must be explicit.
- Structural-change beads must include acceptance criteria for auditing all consuming code across the full codebase.
- Directory globs are allowed only when narrower file enumeration is impossible and the reason is recorded.
- Generated files require explicit allowance in file scope or generated outputs.
- Migrations, auth, billing, permissions, data deletion, security, and privacy surfaces require explicit constraint evidence.
- Formatting-only changes outside declared file scope are scope violations unless approved in the bead.

## Linear steps

| Step | Action |
| --- | --- |
| 1 | Confirm owner has already been selected as `beo-plan`. |
| 2 | Read locked `CONTEXT.md` and current `PLAN.md` when present. |
| 3 | Draft current-phase design, dependencies, file scopes, and verification plan. For structural changes (file moves, routing restructure, import-primitive migration), list consuming files across all directories as integration points, not only files being moved. |
| 4 | Create or update beads with the required description block. |
| 5 | Add dependency edges after all bead ids exist. |
| 6 | Record file scope and swarm eligibility evidence on each bead. |
| 7 | Update `PLAN.md` with bead ids, dependency graph summary, file scope summary, and verification plan. |
| 8 | Invalidate approval if any contract-bearing plan content or bead graph changed. |
| 9 | Run `br sync --flush-only` after bead DB mutations. |
| 10 | Record planning exit evidence in `STATE.json`. |

## Planning exit evidence

Use this appendix to describe the evidence `beo-plan` should record; approval invalidation and next-owner doctrine remain canonical in `beo-plan` and `beo-reference -> approval.md`.

| Evidence | Required |
| --- | --- |
| `PLAN.md` path | yes |
| bead ids | yes |
| dependency graph summary | yes |
| file scope summary | yes |
| verification plan | yes |
| approval invalidated | yes/no |

Non-normative scope comment:

```md
File scope:
- src/auth/session.ts
- tests/auth/session.test.ts
Forbidden paths:
- src/billing/**
- migrations/**
Generated outputs:
- none
Swarm eligibility: no; depends on auth-session-parent
```
