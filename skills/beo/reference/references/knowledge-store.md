# Knowledge Store Protocol

Shared protocol for reading and writing project learnings. Used by `beo-compounding`, `beo-debugging`, `beo-dream`, `beo-exploring`, `beo-planning`, and `beo-router`.

**Preference order:** `.beads/learnings/` and `.beads/critical-patterns.md` are the canonical durable surfaces. Use Obsidian CLI and QMD as optional indexing and mirroring layers when available.

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

Both tools are optional enhancements. Flat-file operations under `.beads/` are the canonical path. Skills must work fully without Obsidian CLI or QMD.

## Write Protocol

### Canonical: Flat Files

Always write learnings to `.beads/learnings/`:

```bash
mkdir -p .beads/learnings
```

Then use your file writing tool to create `.beads/learnings/YYYYMMDD-<slug>.md` with the learnings content.

### Optional Mirror: Obsidian CLI

When `obsidian` CLI is available and mirroring is desired, copy the learning to the vault for richer linking and graph navigation:

```bash
obsidian create "beo-learnings/YYYYMMDD-<slug>.md" --content "<content>" --silent 2>/dev/null
```

Always use the `--silent` flag to avoid interactive prompts. The vault copy is a convenience mirror; `.beads/learnings/` remains authoritative.

### Critical Patterns

The `.beads/critical-patterns.md` file is the distilled subset of learnings that every planning and exploring Phase 0 reads. Promote patterns here only when they meet severity thresholds (see `beo-compounding`).

```bash
# Canonical: use your file editing tool to append to .beads/critical-patterns.md

# Optional mirror: Obsidian vault append
obsidian append "beo-learnings/critical-patterns.md" --content "<pattern>" --silent 2>/dev/null
```

## Read Protocol

Use `learnings-read-protocol.md` as the canonical read-side workflow: flat-file reads first, with optional QMD/Obsidian enhancement.

### Optional Enhancement: Obsidian Vault Search

If the Obsidian vault contains additional learnings not yet mirrored to `.beads/learnings/`:

```bash
VAULT_PATH=$(obsidian eval code="app.vault.adapter.basePath" 2>/dev/null)
if [ -n "$VAULT_PATH" ] && [ -d "$VAULT_PATH/beo-learnings" ]; then
  # Use your content search tool to search "$VAULT_PATH/beo-learnings/" for "<keyword>"
  :
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

One-time setup to enable semantic search over learnings. Index `.beads/learnings/` first as the canonical source:

```bash
LEARNINGS_PATH=".beads/learnings"
mkdir -p "$LEARNINGS_PATH"
qmd collection add "$LEARNINGS_PATH" --name beo-learnings
qmd embed
```

Optional: index the Obsidian vault mirror for additional coverage:

```bash
VAULT_PATH=$(obsidian eval code="app.vault.adapter.basePath" 2>/dev/null)
if [ -n "$VAULT_PATH" ]; then
  qmd collection add "${VAULT_PATH}/beo-learnings" --name beo-learnings-vault
  qmd embed
fi
```

> **Note**: QMD indexes a single directory per collection. If you use both the Obsidian vault and `.beads/learnings/`, create separate collections for each.

## Index Refresh

After writing new learnings, refresh the QMD index (if QMD is available):

```bash
qmd update 2>/dev/null && qmd embed 2>/dev/null
```

This is safe to call even when QMD is unavailable (the `2>/dev/null` suppresses errors).

## Graceful Degradation Summary

| Capability | Canonical path | Optional enhancement |
|-----------|----------------|----------------------|
| **Write learnings** | Write to `.beads/learnings/` using file writing tool | Mirror to Obsidian vault via `obsidian create/append` |
| **Read learnings** | Read `.beads/learnings/` and `.beads/critical-patterns.md` using file reading and content search tools | `qmd query/search` over indexed learnings, plus vault search |
| **Critical patterns** | Append to `.beads/critical-patterns.md` using file editing tool | Mirror to Obsidian vault, plus QMD-backed retrieval |
| **Dedup check** | Search `.beads/learnings/` for `<title>` using content search tool | `qmd query "<title>"` |
