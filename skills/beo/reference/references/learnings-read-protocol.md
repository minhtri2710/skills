# Learnings Read Protocol

Canonical protocol for reading prior learnings and critical patterns before planning, debugging, dreaming, or other explicitly knowledge-sensitive work that cites this reference.

## Why This Exists

Some beo skills need the same behavior:
- query indexed learnings with QMD and Obsidian when available
- read `.beads/critical-patterns.md`
- fall back to flat-file search only when richer tools are unavailable

This file centralizes that read-side behavior.

`beo-compound` is the primary write-side producer for feature learnings and initial critical-pattern entries, while `beo-dream` consolidates that shared guidance over time.

## Read-Side Workflow

### 1. Read Critical Patterns When Relevant

1. Read `.beads/critical-patterns.md` with your file reading tool when the current skill explicitly cites this protocol or the request is likely to repeat prior patterns. Skip if absent.
2. Treat relevant entries as mandatory context once loaded.

### 2. Query Indexed Learnings (Preferred Path)

If QMD is available, use semantic search as the primary retrieval method:

```bash
qmd query "<feature description or learning topic>" --json 2>/dev/null
qmd search "<keyword>" --json 2>/dev/null
```

If the Obsidian vault contains additional learnings not yet indexed by QMD, supplement with vault search. See `knowledge-store.md` § Optional Enhancement: Obsidian Vault Search.

### 3. Flat-File Fallback

If QMD is unavailable or returns no results, use your content search tool to search `.beads/learnings/` for `<keyword or domain phrase>`.

### 4. Apply What Matters

If a prior learning is relevant:

1. Mention it explicitly.
2. Reflect it in the current plan, check, fix, or review.
3. Do not re-solve the same known issue from scratch.

## Tool Availability

To detect optional tooling first, see `knowledge-store.md` § Tool Detection.

## Hard Rules

- `.beads/learnings/` and `.beads/critical-patterns.md` remain the authoritative write surfaces.
- **QMD and Obsidian are the preferred read path** when available; flat-file search is the fallback.
- Skills that explicitly cite this protocol should check critical patterns before concluding that no prior guidance applies.
- If a learning is relevant, incorporate it explicitly rather than silently noting it.
- Do not turn this protocol into a universal preflight for unrelated skills.
