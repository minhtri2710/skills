# Planning Prerequisites

Operational reference for prerequisites, learnings retrieval, and planning mode selection.

## 0. Refactoring Sequencing Rule

When planning structural refactoring, sequence steps in this order:

1. **Fix** dependency violations (wrong-direction imports, DAG breaks)
2. **Remove** dead artifacts (unused code, stale modules)
3. **Restrict** access control (tighten visibility, lock down APIs)

This is the only rework-free order. Fixing the DAG first means dead-code analysis isn't confused by items kept alive through wrong-direction imports. Removing dead code before visibility tightening means the visibility pass operates on the minimal item set.

## 1. Prerequisites

Verify the epic exists:

```bash
br show <EPIC_ID> --json
```

Read these artifacts:

- `.beads/artifacts/<feature_slug>/CONTEXT.md` — **required**; if absent, stop and route back to `beo-explore`
- `.beads/critical-patterns.md` — optional

Planning assumes decisions are already locked. Do not reopen product-definition questions unless planning reveals contradictions or gaps.

## 2. Learnings Retrieval

Run this step before research. Use `beo-reference` → `references/learnings-read-protocol.md` as the canonical workflow.

If relevant patterns exist:
- Note them in `discovery.md`
- Apply them in `approach.md`
- Carry them into affected bead descriptions
- Let them influence single-phase vs. multi-phase selection

If no relevant prior learnings exist, record that explicitly.

## 3. Decide Planning Mode

| Mode | Choose when |
|------|-------------|
| `single-phase` | ALL: one believable closed loop; 1–4 stories; no obvious deferred capability sequence; one phase stays focused |
| `multi-phase` | ANY: 2+ meaningful capability slices; current work mainly unlocks later work; one phase would be vague or oversized; story count likely exceeds 4; later work should stay intentionally deferred |

Record the decision in `approach.md`. Do not choose `multi-phase` just because the work is moderately large — use the simplest mode that keeps the work understandable and execution-safe.
