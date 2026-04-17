# Bead Operations

Canonical operational guide for creating and maintaining current-phase beads during planning.

## Preconditions

- `CONTEXT.md` is locked.
- `approach.md` exists or is being finalized in the same planning cycle.
- `phase-contract.md` and `story-map.md` are being written for the current phase.
- Planning owns bead creation; execution, validation, review, and route do not create planned execution beads.

## Description Template Rule

Every bead description must use Markdown format with the shared templates from `beo-reference` → `references/bead-description-templates.md`. If no institutional learnings apply, write: "No prior learnings for this domain."

## Bead Completeness Gate

After creating or updating current-phase beads, read each bead back before handoff and verify it includes:
- a non-empty Markdown description using the planned task template
- clear file scope
- acceptance criteria
- verification steps
- references to the relevant locked decisions or planning artifacts
- enough context for a fresh worker to execute it without reopening planning

Fix incomplete beads immediately before routing to `beo-validate`.

## Quick-Scoped Planning

For quick-scoped work, planning may keep artifacts smaller and the current phase narrower, but it still must:

1. write `approach.md`
2. write `plan.md`
3. write `phase-contract.md`
4. write `story-map.md`
5. create the current-phase bead set
6. route to `beo-validate`

Quick mode reduces ceremony with smaller artifacts and faster cycles, but it does not skip validation or review.

---

## Promotion Flow

When quick-scoped work grows beyond its initial envelope:

1. **Gather existing tasks:** `br dep list <EPIC_ID> --direction up --type parent-child --json`
2. **Write plan around them:** Create `plan.md` incorporating existing tasks plus any new tasks needed
3. **Create missing beads:** Only for tasks that do not already exist. Wire dependencies for all current-phase work
4. **Proceed to validation:** Route to `beo-validate`. Expanded plans need the same rigor as fresh plans

---

## Task Bead Creation Operations

### Create task beads

```bash
br create "<Task Name>" -t task --parent <EPIC_ID> -p <priority> --json
```

### Write bead descriptions

Use the **Planned Task Bead Template** from `beo-reference` → `references/bead-description-templates.md`.

Checklist:
- include exact file paths when known
- include acceptance criteria
- include verification steps
- reference the relevant locked decisions or planning artifacts
- keep the bead independently executable by a fresh worker

### Dependency wiring

Use `beo-reference` → `references/dependency-and-scheduling.md` for canonical dependency rules.

### Story-map sync

After bead creation, fill `Story-To-Bead Mapping` in `.beads/artifacts/<feature_slug>/story-map.md`.

## Hard Rules

- Do not create future-phase executable beads.
- Do not rely on route to create planned execution beads.
- Do not create beads during validation.
- Do not hand off beads that fail the bead completeness gate.
- Do not leave bead descriptions without acceptance criteria or verification.
- Do not skip dependency wiring when ordering matters.
