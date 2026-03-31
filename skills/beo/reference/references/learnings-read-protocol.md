# Learnings Read Protocol

Canonical protocol for reading prior learnings and critical patterns before planning, validation, debugging, dreaming, or other knowledge-sensitive work.

## Why This Exists

Many beo skills need the same behavior:
- query indexed learnings with QMD
- inspect Obsidian-backed learnings when available
- read `.beads/critical-patterns.md`
- fall back to flat-file search only when richer tools are unavailable

This file centralizes that read-side behavior.

## Mandatory Read-Side Workflow

### 1. Query Indexed Learnings With QMD

If QMD is available, start here:

```bash
qmd query "<feature description or learning topic>" --json 2>/dev/null
qmd search "<keyword>" --json 2>/dev/null
```

### 2. Read Critical Patterns

```bash
cat .beads/critical-patterns.md 2>/dev/null
```

If present, treat relevant entries as mandatory context.

### 3. Search Flat-File Learnings As Fallback

If QMD is unavailable or insufficient, use keyword search over `.beads/learnings/`:

```bash
grep -ri "<keyword or domain phrase>" .beads/learnings/ 2>/dev/null
```

### 4. Apply What Matters

If a prior learning is relevant:
- mention it explicitly
- reflect it in the current plan/check/fix/review
- do not re-solve the same known issue from scratch

## Tool Availability

If you need to detect optional tooling first, see `knowledge-store.md`.

## Hard Rules

- Start with QMD and Obsidian-backed learnings when available.
- Critical patterns must always be checked, even when QMD returns results.
- Use flat-file reads as fallback, not as the preferred path.
- If a learning is relevant, incorporate it explicitly rather than silently noting it.
- Do not skip prior learnings for "obvious" work; that is how repeat failures happen.
