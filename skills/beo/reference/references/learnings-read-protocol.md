# Learnings Read Protocol

Read prior learnings only when the calling skill explicitly cites this protocol or the task is clearly knowledge-sensitive.

## Read-Side Workflow

### 1. Read Critical Patterns When Relevant

1. Read `.beads/critical-patterns.md` when the task is likely to repeat prior patterns. Skip if absent.
2. Treat relevant entries as mandatory context.

### 2. Query Indexed Learnings (Preferred Path)

If QMD is available, use it first:

```bash
qmd query "<feature description or learning topic>" --json 2>/dev/null
qmd search "<keyword>" --json 2>/dev/null
```

If the Obsidian vault contains learnings not yet indexed by QMD, supplement with vault search per `knowledge-store.md`.

### 3. Flat-File Fallback

If QMD is unavailable or returns no results, search `.beads/learnings/`.

### 4. Apply What Matters

If a prior learning is relevant:

1. Mention it explicitly.
2. Reflect it in the current plan, check, fix, or review.
3. Do not re-solve the same known issue from scratch.

## Hard Rules

- `.beads/learnings/` and `.beads/critical-patterns.md` remain the authoritative write surfaces.
- QMD and Obsidian are the preferred read path when available; flat-file search is the fallback.
- Skills that explicitly cite this protocol should check critical patterns before concluding that no prior guidance applies.
- If a learning is relevant, incorporate it explicitly rather than silently noting it.
- Do not turn this protocol into a universal preflight for unrelated skills.
