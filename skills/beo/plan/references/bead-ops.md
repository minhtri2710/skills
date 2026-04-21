# Bead Operations

Current-phase bead creation and maintenance rules for `beo-plan`.

## Preconditions

- `CONTEXT.md` is locked
- `approach.md` exists or is being finalized in the same planning cycle
- `phase-contract.md` and `story-map.md` are being written for the current phase
- planning owns planned execution beads; route, validate, execute, and review do not create them

## Description Rule

Every bead description must use the shared templates in `beo-reference` → `references/bead-description-templates.md`.

If no institutional learnings apply, write: `No prior learnings for this domain.`

## Completeness Gate

Before handing off to `beo-validate`, read every bead back and confirm it has:
- a non-empty Markdown description
- clear file scope
- acceptance criteria
- verification steps
- references to the relevant locked decisions or planning artifacts
- enough context for a fresh worker to execute without reopening planning

Fix incomplete beads before handoff.

## Quick-Scoped Planning

Quick scope still must:
1. write `approach.md`
2. write `plan.md`
3. write `phase-contract.md`
4. write `story-map.md`
5. create the current-phase bead set
6. route to `beo-validate`

Quick mode reduces ceremony. It does not skip validation or review.

If quick-scoped work grows:
1. gather existing tasks with `br dep list <EPIC_ID> --direction up --type parent-child --json`
2. write the plan around the existing tasks
3. create only the missing beads
4. wire dependencies for all current-phase work
5. route to `beo-validate`

## Creation Operations

Create task beads:

```bash
br create "<Task Name>" -t task --parent <EPIC_ID> -p <priority> --json
```

After creation:
- write the description using the planned-task template
- include exact file paths when known
- include acceptance criteria and verification
- reference the relevant locked decisions or planning artifacts
- keep the bead independently executable by a fresh worker

Use `beo-reference` → `references/dependency-and-scheduling.md` for dependency rules.

After bead creation, fill `Story-To-Bead Mapping` in `.beads/artifacts/<feature_slug>/story-map.md`.

## Hard Rules

- do not create future-phase executable beads
- do not rely on route to create planned execution beads
- do not create beads during validation
- do not hand off beads that fail the completeness gate
- do not omit acceptance criteria or verification
- do not skip dependency wiring when order matters
