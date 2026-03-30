# Knowledge Store Protocol

Shared protocol for reading and writing project learnings. Used by `beo-compounding`, `beo-debugging`, `beo-dream`, `beo-planning`, and `beo-router`.

## Tool Detection

Run at Phase 0 of any skill that uses the knowledge store:

```bash
obsidian help 2>/dev/null   # Check Obsidian CLI availability
qmd status 2>/dev/null      # Check QMD search availability
```

Both tools are **optional**. All skills degrade gracefully to flat-file operations when either tool is unavailable.

## Write Protocol

### Primary: Obsidian CLI

When `obsidian` CLI is available, use it for all learnings writes:

```bash
# Create a new learnings note
obsidian create "beo-learnings/YYYYMMDD-<slug>.md" --content "<content>" --silent

# Append to an existing note
obsidian append "beo-learnings/YYYYMMDD-<slug>.md" --content "<content>" --silent
```

Always use the `--silent` flag to avoid interactive prompts.

### Fallback: Flat Files

When Obsidian CLI is unavailable, write directly to `.beads/learnings/`:

```bash
mkdir -p .beads/learnings
cat > .beads/learnings/YYYYMMDD-<slug>.md << 'EOF'
<content>
EOF
```

### Critical Patterns

The `.beads/critical-patterns.md` file is the distilled subset of learnings that every planning and exploring Phase 0 reads. Promote patterns here only when they meet severity thresholds (see `beo-compounding`).

```bash
# Obsidian CLI (preferred)
obsidian append "beo-learnings/critical-patterns.md" --content "<pattern>" --silent

# Flat-file fallback
echo "<pattern>" >> .beads/critical-patterns.md
```

## Read Protocol

### Primary: QMD Semantic Search

When `qmd` is available, use semantic search to find relevant learnings:

```bash
# Semantic query (returns ranked results)
qmd query "<feature domain keywords>" --json 2>/dev/null

# Text search (exact match)
qmd search "<keyword>" --json 2>/dev/null
```

### Fallback: grep

When QMD is unavailable, fall back to flat-file search:

```bash
cat .beads/critical-patterns.md 2>/dev/null
grep -ri "<keyword>" .beads/learnings/ 2>/dev/null
```

## YAML Frontmatter Schema

All learnings files should include this frontmatter for Obsidian and QMD indexing:

```yaml
---
date: YYYY-MM-DD
feature: <feature-name>
categories:
  - pattern | decision | failure | anti-pattern
severity: low | medium | high | critical
tags:
  - <domain-tag>
  - <technology-tag>
---
```

## QMD Collection Setup

One-time setup to enable semantic search over learnings:

```bash
qmd collection add .beads/learnings --name beo-learnings
qmd embed
```

## Index Refresh

After writing new learnings, refresh the QMD index:

```bash
qmd update 2>/dev/null && qmd embed 2>/dev/null
```

This is safe to call even when QMD is unavailable (the `2>/dev/null` suppresses errors).

## Graceful Degradation Summary

| Capability | Obsidian CLI available | QMD available | Neither |
|-----------|----------------------|---------------|---------|
| **Write learnings** | `obsidian create/append` | N/A | `cat >` / `echo >>` to `.beads/learnings/` |
| **Read learnings** | N/A | `qmd query/search` | `grep` over `.beads/learnings/` |
| **Critical patterns** | `obsidian append` | `qmd query` | `cat` / `echo >>` `.beads/critical-patterns.md` |
| **Dedup check** | N/A | `qmd query "<title>"` | `grep -l "<title>" .beads/learnings/` |
