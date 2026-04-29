## Contents

- Bootstrap surfaces
- Feature slug rules
- CONTEXT.md bootstrap
- Go-mode assumption ledger
- Linear steps

# intake-bootstrap

Role: APPENDIX
Allowed content only: bootstrap order, slug creation timing, initial file creation commands, and go-mode assumption recording

## Bootstrap surfaces

Canonical state and handoff semantics remain in `beo-reference -> state.md`; this appendix lists only the bootstrap surfaces `beo-explore` touches.

| Surface | Rule |
| --- | --- |
| `.beads/artifacts/<feature_slug>/CONTEXT.md` | created by `beo-explore` and locked only after required sections are complete |
| feature slug | immutable after first successful artifact write |
| `.beads/STATE.json` | records the selected active feature and exploration evidence |
| `.beads/HANDOFF.json` | written only when clarification blocks progress or owner transfer pauses |

## Feature slug rules

- Regex: `^[a-z0-9]+(?:-[a-z0-9]+)*$`.
- Slug must be unique under `.beads/artifacts/`.
- Slug rename is forbidden after first successful write.
- If the user supplies an unsafe slug, normalize once and record the mapping in evidence.

## CONTEXT.md bootstrap

Use the canonical `CONTEXT.md` schema from `beo-reference -> artifacts.md`. This appendix only covers bootstrap order, slug creation timing, and initial file creation.

Minimal creation stub before filling canonical sections:

```md
# CONTEXT.md

## Feature
- slug: <slug>
- request: <user request or ticket summary>
- owner-visible goal: <what the next owner is trying to make true>
```

## Go-mode assumption ledger

Canonical go-mode semantics remain in `beo-reference -> go-mode.md`. State and handoff persistence remain in `beo-reference -> state.md`.

When `go_mode` is used, record each non-blocking assumption with:
- assumption text
- why it is non-blocking
- affected scope
- authorization source
- persistence condition and invalidation trigger

`go_mode` assumptions must never stand in for missing acceptance, hidden file scope, missing approval, or unresolved security/privacy constraints.

## Linear steps

| Step | Action |
| --- | --- |
| 1 | Confirm owner has already been selected as `beo-explore`. |
| 2 | Select or create a valid immutable feature slug. |
| 3 | Create artifact directory if absent. |
| 4 | Fill the CONTEXT template from user intent and live repo evidence. |
| 5 | Ask only blocking questions whose answers can change acceptance, non-goals, compatibility, constraints, or user-visible scope. |
| 6 | Record non-blocking assumptions only when `go_mode` permits them. |
| 7 | Set `locked=true` and `locked_at` only when required sections are complete and no blocking questions remain. |
| 8 | Update `STATE.json` with feature slug, status, and evidence. |
| 9 | Successor-owner selection remains in `beo-explore`; this appendix only names locked vs blocked outcomes. |

## Exact commands

Create artifact directory:

```sh
mkdir -p .beads/artifacts/<feature_slug>
```

Check slug collision:

```sh
test ! -e .beads/artifacts/<feature_slug>
```
