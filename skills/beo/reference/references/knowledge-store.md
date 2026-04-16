# Knowledge Store Protocol

Shared protocol for reading and writing project learnings. Used by `beo-compound`, `beo-debug`, `beo-dream`, `beo-explore`, `beo-plan`, and `beo-route`.

**Preference order:** `.beads/learnings/` and `.beads/critical-patterns.md` are the canonical durable write surfaces. For reads, **prefer Obsidian CLI and QMD when available**; fall back to flat-file search only when they are unavailable.

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

Both tools are optional on writes. On reads, prefer them and fall back to flat-file operations under `.beads/` when neither is available.

## Write Protocol

Learnings write governance:
- redact or generalize PII, secrets, customer data, internal URLs, and credentials before any write
- never append to `.beads/critical-patterns.md` without explicit user approval per `approval-gates.md`
- refresh QMD after writes when available so later reads see the latest state

### Canonical: Flat Files

Write learnings to `.beads/learnings/`:

```bash
mkdir -p .beads/learnings
```

Then use your file writing tool to create `.beads/learnings/YYYYMMDD-<slug>.md`.

### Optional Mirror: Obsidian CLI

When `obsidian` CLI is available and mirroring is desired, copy the learning to the vault:

```bash
obsidian create path="beo-learnings/YYYYMMDD-<slug>.md" content="<content>" silent 2>/dev/null
```

Use the `silent` flag to avoid interactive prompts. The vault copy is a convenience mirror; `.beads/learnings/` remains canonical.

### Critical Patterns

`.beads/critical-patterns.md` is the distilled subset of learnings that every planning and exploring Phase 0 reads. Promote patterns here only when they are supported by multi-feature evidence and explicit approval (see `beo-dream` and `approval-gates.md`).

```bash
# Canonical: use your file editing tool to append to .beads/critical-patterns.md

# Optional mirror: Obsidian vault append
obsidian append "beo-learnings/critical-patterns.md" --content "<pattern>" --silent 2>/dev/null  # Vault mirror only; canonical repo path remains .beads/critical-patterns.md
```

## Read Protocol

Use `learnings-read-protocol.md` as the canonical read-side workflow: **QMD and Obsidian first, flat-file fallback only when unavailable.**

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
severity: routine | useful | critical
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

> QMD indexes a single directory per collection. If you use both the Obsidian vault and `.beads/learnings/`, create separate collections for each.

## Index Refresh

After writing new learnings, refresh the QMD index if QMD is available:

```bash
qmd update 2>/dev/null && qmd embed 2>/dev/null
```

This is safe even when QMD is unavailable because `2>/dev/null` suppresses errors.

## Graceful Degradation Summary

| Capability | Canonical write path | Preferred read path | Fallback read path |
|-----------|---------------------|--------------------|--------------------|
| **Write learnings** | Write to `.beads/learnings/` using file writing tool | N/A (always write to canonical) | N/A |
| **Mirror learnings** | N/A | N/A | Mirror to Obsidian vault via `obsidian create/append` |
| **Read learnings** | N/A | `qmd query/search` + Obsidian vault search | Read `.beads/learnings/` using file reading and content search tools |
| **Critical patterns** | Append to `.beads/critical-patterns.md` | Same file (always read directly) | Same file |
| **Dedup check** | N/A | `qmd query "<title>"` | Search `.beads/learnings/` for `<title>` using content search tool |
