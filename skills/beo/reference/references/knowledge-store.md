# Knowledge Store Protocol

Shared protocol for reading and writing project learnings. Used by `beo-compounding`, `beo-debugging`, `beo-dream`, `beo-exploring`, `beo-planning`, and `beo-router`.

## Table of Contents

- [Tool Detection](#tool-detection)
- [Write Protocol](#write-protocol)
- [Read Protocol](#read-protocol)
- [YAML Frontmatter Schema](#yaml-frontmatter-schema)
- [QMD Collection Setup](#qmd-collection-setup)
- [Index Refresh](#index-refresh)
- [Graceful Degradation Summary](#graceful-degradation-summary)

## Tool Detection

Run at Phase 0 of any skill that uses the knowledge store:

```bash
obsidian help 2>/dev/null   # Check Obsidian CLI availability
qmd status 2>/dev/null      # Check QMD search availability
```

Both tools are **optional**. All skills degrade gracefully to flat-file operations when either tool is unavailable.

## Write Protocol

### Primary: Flat Files

All learnings writes go to `.beads/learnings/` by default:

```bash
mkdir -p .beads/learnings
cat > .beads/learnings/YYYYMMDD-<slug>.md << 'EOF'
<content>
EOF
```

### Optional Enhancement: Obsidian CLI

When `obsidian` CLI is available, also mirror writes to the vault for richer linking and graph navigation:

```bash
obsidian create "beo-learnings/YYYYMMDD-<slug>.md" --content "<content>" --silent
obsidian append "beo-learnings/YYYYMMDD-<slug>.md" --content "<content>" --silent
```

Always use the `--silent` flag to avoid interactive prompts.

### Critical Patterns

The `.beads/critical-patterns.md` file is the distilled subset of learnings that every planning and exploring Phase 0 reads. Promote patterns here only when they meet severity thresholds (see `beo-compounding`).

```bash
# Primary: flat-file append
echo "<pattern>" >> .beads/critical-patterns.md

# Optional enhancement: also write to Obsidian vault if available
obsidian append "beo-learnings/critical-patterns.md" --content "<pattern>" --silent 2>/dev/null
```

## Read Protocol

### Primary: grep

Read learnings directly from flat files:

```bash
cat .beads/critical-patterns.md 2>/dev/null
grep -ri "<keyword>" .beads/learnings/ 2>/dev/null
```

### Optional Enhancement: QMD Semantic Search

When `qmd` is available, use semantic search for richer results:

```bash
# Semantic query (returns ranked results)
qmd query "<feature domain keywords>" --json 2>/dev/null

# Text search (exact match)
qmd search "<keyword>" --json 2>/dev/null
```

### Optional Enhancement: Obsidian Vault Search

If the Obsidian vault contains additional learnings not yet in `.beads/learnings/`:

```bash
VAULT_PATH=$(obsidian eval code="app.vault.adapter.basePath" 2>/dev/null)
if [ -n "$VAULT_PATH" ] && [ -d "$VAULT_PATH/beo-learnings" ]; then
  grep -ri "<keyword>" "$VAULT_PATH/beo-learnings/" 2>/dev/null
fi
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

One-time setup to enable semantic search over learnings (optional). Point the collection at `.beads/learnings/`:

```bash
LEARNINGS_PATH=".beads/learnings"
mkdir -p "$LEARNINGS_PATH"
qmd collection add "$LEARNINGS_PATH" --name beo-learnings
qmd embed
```

If you also want to index the Obsidian vault's `beo-learnings/` folder:

```bash
VAULT_PATH=$(obsidian eval code="app.vault.adapter.basePath" 2>/dev/null)
if [ -n "$VAULT_PATH" ]; then
  qmd collection add "${VAULT_PATH}/beo-learnings" --name beo-learnings-vault
  qmd embed
fi
```

> **Note**: QMD indexes a single directory per collection. If you write to both `.beads/learnings/` and the Obsidian vault, create separate collections for each.

## Index Refresh

After writing new learnings, refresh the QMD index (if QMD is available):

```bash
qmd update 2>/dev/null && qmd embed 2>/dev/null
```

This is safe to call even when QMD is unavailable (the `2>/dev/null` suppresses errors).

## Graceful Degradation Summary

| Capability | No optional tools | + QMD | + Obsidian CLI | + Both |
|-----------|-------------------|-------|---------------|--------|
| **Write learnings** | `cat >` to `.beads/learnings/` | same | also mirrors to vault | also mirrors to vault |
| **Read learnings** | `grep` over `.beads/learnings/` | `qmd query/search` | also search vault | `qmd query/search` + vault |
| **Critical patterns** | `cat` / `echo >>` `.beads/critical-patterns.md` | + `qmd query` | also writes to vault | all three |
| **Dedup check** | `grep -l "<title>" .beads/learnings/` | `qmd query "<title>"` | same as no tools | `qmd query "<title>"` |
