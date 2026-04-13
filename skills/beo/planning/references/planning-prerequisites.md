# Planning Prerequisites

Operational reference for prerequisites, learnings retrieval, and planning mode selection.

## 0. Refactoring Sequencing Rule

When planning structural refactoring, always sequence steps in this order:

1. **Fix** dependency violations (wrong-direction imports, DAG breaks)
2. **Remove** dead artifacts (unused code, stale modules)
3. **Restrict** access control (tighten visibility, lock down APIs)

This is the only rework-free order. Fixing the DAG first means dead-code analysis isn't confused by items kept alive through wrong-direction imports. Removing dead code before visibility tightening means the visibility pass operates on the minimal item set.

## 1. Prerequisites

Before starting, verify:

```bash
# Epic must exist
br show <EPIC_ID> --json
```

Read these artifacts with your file reading tool:

- `.beads/artifacts/<feature_slug>/CONTEXT.md` (required -- if absent, stop and route back to `beo-exploring`)
- `.beads/critical-patterns.md` (optional)

If `CONTEXT.md` does not exist, stop and route back to `beo-exploring`.

Planning assumes decisions are already locked. Do not reopen product-definition questions here unless the planning work proves the decisions are contradictory or incomplete.

## 2. Learnings Retrieval

This step is mandatory before research.

Use `../../reference/references/learnings-read-protocol.md` as the canonical read-side workflow.

If relevant patterns exist:

- note them explicitly in `discovery.md`
- apply them in `approach.md`
- carry them into affected bead descriptions
- let them influence whether the work should stay single-phase or become multi-phase

If no relevant prior learnings exist, record that explicitly rather than implying the step was skipped.

## 3. Decide Planning Mode

Planning supports two modes:

- `single-phase`
- `multi-phase`

Choose `single-phase` when ALL of these are true:

- one believable closed loop can explain the work
- the feature can usually be expressed in 1-4 stories
- there is no obvious capability sequence that should remain deferred
- preparing one current phase does not turn the phase into a vague work bucket

Choose `multi-phase` when ANY of these are true:

- the feature naturally unfolds across 2+ meaningful capability slices
- the current work mainly unlocks later work
- forcing everything into one phase would create a vague or oversized loop
- the full feature only makes sense as a sequence
- story count would likely exceed 4 if kept in one phase
- later work should stay intentionally deferred instead of being loosely implied

Record the planning-mode decision in `approach.md`.

Do not choose `multi-phase` just because the work is moderately large. Use the simplest mode that keeps the work understandable and execution-safe.
