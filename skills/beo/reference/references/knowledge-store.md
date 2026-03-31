# Knowledge Store Protocol

Shared protocol for reading and writing project learnings. Used by `beo-compounding`, `beo-debugging`, `beo-dream`, `beo-exploring`, `beo-planning`, and `beo-router`.

**Preference order:** use Obsidian CLI and QMD first when available; fall back to flat files only when either tool is unavailable or the richer path cannot satisfy the task safely.

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

Both tools are preferred when available. All skills must degrade gracefully to flat-file operations only when Obsidian CLI or QMD is unavailable.

## Write Protocol

### Preferred: Obsidian CLI

When `obsidian` CLI is available, write learnings to the vault first for richer linking, graph navigation, and durable knowledge-store continuity:

```bash
obsidian create "beo-learnings/YYYYMMDD-<slug>.md" --content "<content>" --silent
obsidian append "beo-learnings/YYYYMMDD-<slug>.md" --content "<content>" --silent
```

Always use the `--silent` flag to avoid interactive prompts.

### Fallback: Flat Files

If Obsidian CLI is unavailable or the vault write cannot be completed safely, write to `.beads/learnings/`.

If both surfaces are available, keeping a mirrored flat-file copy is allowed, but the vault write remains the preferred path:

```bash
mkdir -p .beads/learnings
cat > .beads/learnings/YYYYMMDD-<slug>.md << 'EOF'
<content>
EOF
```

### Critical Patterns

The `.beads/critical-patterns.md` file is the distilled subset of learnings that every planning and exploring Phase 0 reads. Promote patterns here only when they meet severity thresholds (see `beo-compounding`).

```bash
# Preferred: Obsidian vault append
obsidian append "beo-learnings/critical-patterns.md" --content "<pattern>" --silent 2>/dev/null

# Fallback: flat-file append
echo "<pattern>" >> .beads/critical-patterns.md
```

## Read Protocol

Use `learnings-read-protocol.md` as the canonical read-side workflow for Obsidian/QMD-first retrieval with flat-file fallback.

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

One-time setup to enable semantic search over learnings. Prefer indexing the Obsidian vault's `beo-learnings/` folder first:

```bash
VAULT_PATH=$(obsidian eval code="app.vault.adapter.basePath" 2>/dev/null)
if [ -n "$VAULT_PATH" ]; then
  qmd collection add "${VAULT_PATH}/beo-learnings" --name beo-learnings-vault
  qmd embed
fi
```

Fallback collection for flat files:

```bash
LEARNINGS_PATH=".beads/learnings"
mkdir -p "$LEARNINGS_PATH"
qmd collection add "$LEARNINGS_PATH" --name beo-learnings
qmd embed
```

> **Note**: QMD indexes a single directory per collection. If you use both the Obsidian vault and `.beads/learnings/`, create separate collections for each.

## Index Refresh

After writing new learnings, refresh the QMD index (if QMD is available):

```bash
qmd update 2>/dev/null && qmd embed 2>/dev/null
```

This is safe to call even when QMD is unavailable (the `2>/dev/null` suppresses errors).

## Graceful Degradation Summary

| Capability | Preferred path | Fallback path |
|-----------|----------------|---------------|
| **Write learnings** | `obsidian create/append` to `beo-learnings/` | `cat >` to `.beads/learnings/` |
| **Read learnings** | `qmd query/search` over indexed learnings, plus vault search if needed | `grep` over `.beads/learnings/` and `.beads/critical-patterns.md` |
| **Critical patterns** | `obsidian append` to vault copy, plus QMD-backed retrieval | `echo >> .beads/critical-patterns.md` |
| **Dedup check** | `qmd query "<title>"` | `grep -l "<title>" .beads/learnings/` |
