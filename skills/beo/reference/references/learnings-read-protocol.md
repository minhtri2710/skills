# Learnings Read Protocol

Canonical protocol for reading prior learnings and critical patterns before planning, validation, debugging, dreaming, or other knowledge-sensitive work.

## Why This Exists

Many beo skills need the same behavior:
- query indexed learnings with QMD and Obsidian when available
- read `.beads/critical-patterns.md`
- fall back to flat-file search only when richer tools are unavailable

This file centralizes that read-side behavior.

`beo-compounding` is the primary write-side producer for the learnings files and critical patterns this protocol reads.

## Mandatory Read-Side Workflow

### 1. Read Critical Patterns

1. Read `.beads/critical-patterns.md` with your file reading tool. Skip if absent.
2. Treat relevant entries as mandatory context.

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
- Critical patterns must always be checked (Step 1), even when QMD returns results.
- If a learning is relevant, incorporate it explicitly rather than silently noting it.
- Do not skip prior learnings for "obvious" work; that is how repeat failures happen.
