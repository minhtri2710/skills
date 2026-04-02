# Learnings Read Protocol

Canonical protocol for reading prior learnings and critical patterns before planning, validation, debugging, dreaming, or other knowledge-sensitive work.

## Why This Exists

Many beo skills need the same behavior:
- query indexed learnings with QMD
- inspect Obsidian-backed learnings when available
- read `.beads/critical-patterns.md`
- fall back to flat-file search only when richer tools are unavailable

This file centralizes that read-side behavior.

`beo-compounding` is the primary write-side producer for the learnings files and critical patterns this protocol reads.

## Mandatory Read-Side Workflow

### 1. Read Critical Patterns

Read `.beads/critical-patterns.md` with your file reading tool (skip if absent).

If present, treat relevant entries as mandatory context.

### 2. Search Flat-File Learnings

Use your content search tool to search `.beads/learnings/` for `<keyword or domain phrase>`.

### 3. Optional Enhancement: Query Indexed Learnings With QMD

If QMD is available, supplement flat-file results with semantic search:

```bash
qmd query "<feature description or learning topic>" --json 2>/dev/null
qmd search "<keyword>" --json 2>/dev/null
```

### 4. Apply What Matters

If a prior learning is relevant:
- mention it explicitly
- reflect it in the current plan/check/fix/review
- do not re-solve the same known issue from scratch

## Tool Availability

If you need to detect optional tooling first, see `knowledge-store.md`.

## Hard Rules

- `.beads/learnings/` and `.beads/critical-patterns.md` are the authoritative read surfaces.
- QMD and Obsidian-backed learnings are optional enhancements, not requirements.
- Critical patterns must always be checked, even when QMD returns results.
- Use QMD/Obsidian reads as supplementary context, not as the primary path.
- If a learning is relevant, incorporate it explicitly rather than silently noting it.
- Do not skip prior learnings for "obvious" work; that is how repeat failures happen.
