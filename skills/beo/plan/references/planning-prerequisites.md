# Planning Prerequisites

Use before writing any planning artifact.

## 1. Refactoring Order

For structural refactors, plan in this order:
1. fix dependency violations
2. remove dead artifacts
3. tighten visibility or access

This order avoids rework: wrong-direction imports can keep dead code artificially alive, and visibility changes are easiest after the surface is already minimal.

## 2. Required Inputs

Verify the epic:

```bash
br show <EPIC_ID> --json
```

Read:
- `.beads/artifacts/<feature_slug>/CONTEXT.md` — required; if missing, route to `beo-explore`
- `.beads/critical-patterns.md` — optional

Planning assumes requirements are already locked. Reopen product questions only when planning finds a contradiction or an actual gap.

## 3. Learnings Read

Use `beo-reference` → `references/learnings-read-protocol.md`.

If relevant learnings exist:
- record them in `discovery.md`
- apply them in `approach.md`
- carry them into affected bead descriptions
- let them influence single-phase vs. multi-phase choice

If none apply, say so explicitly.

## 4. Planning Mode

| Mode | Choose when |
| --- | --- |
| `single-phase` | one believable closed loop, usually 1-4 stories, with no meaningful deferred capability sequence |
| `multi-phase` | the work naturally splits into 2 or more real capability slices, or one phase would be vague, oversized, or mainly unlock later work |

Record the choice in `approach.md`. Choose the simplest mode that keeps execution clear and safe.
