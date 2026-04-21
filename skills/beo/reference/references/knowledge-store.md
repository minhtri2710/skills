# Knowledge Store Protocol

Read and write learnings only from skills that explicitly need the knowledge store.

Canonical write surfaces:
- `.beads/learnings/`
- `.beads/critical-patterns.md`

Preferred read path:
- `qmd`
- Obsidian vault search
- flat-file fallback

## Tool Detection

Run only when the active skill needs learnings lookup or learnings writes:

```bash
obsidian help 2>/dev/null   # Check Obsidian CLI availability
qmd status 2>/dev/null      # Check QMD search availability
```

Both tools are optional on writes. On reads, prefer them before flat-file fallback.

## Write Protocol

- redact or generalize PII, secrets, customer data, internal URLs, and credentials before any write
- never write to `.beads/critical-patterns.md` without explicit user approval per `approval-gates.md`
- refresh QMD after writes when available so later reads see the latest state

### Canonical write

Write learnings to `.beads/learnings/`:

```bash
mkdir -p .beads/learnings
```

Then use your file writing tool to create `.beads/learnings/YYYYMMDD-<slug>.md`.

### Optional Obsidian mirror

When `obsidian` is available and mirroring is desired, copy the learning to the vault:

```bash
obsidian create path="beo-learnings/YYYYMMDD-<slug>.md" content="<content>" 2>/dev/null
```

The vault copy is a mirror only; `.beads/learnings/` remains canonical.

### Critical Patterns

`.beads/critical-patterns.md` holds distilled reusable guidance. `beo-compound` promotes single-feature patterns there after review acceptance and explicit approval. `beo-dream` later consolidates or retires them.

```bash
# Canonical: use your file editing tool to update .beads/critical-patterns.md

# Optional vault mirror
obsidian append path="beo-learnings/critical-patterns.md" content="<pattern>" 2>/dev/null
```

## Read Protocol

Use `learnings-read-protocol.md` for read-side behavior.

### Optional Obsidian vault search

If the Obsidian vault contains additional learnings not yet mirrored to `.beads/learnings/`:

```bash
VAULT_PATH=$(obsidian eval code="app.vault.adapter.basePath" 2>/dev/null)
if [ -n "$VAULT_PATH" ] && [ -d "$VAULT_PATH/beo-learnings" ]; then
  # Use your content search tool to search "$VAULT_PATH/beo-learnings/" for "<keyword>"
  :
fi
```

## YAML Frontmatter Schema

All learnings files should include:

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

Index `.beads/learnings/` first:

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

QMD indexes one directory per collection. If you index both repo and vault paths, use separate collections.

## Index Refresh

After writing new learnings, refresh the QMD index if QMD is available:

```bash
qmd update 2>/dev/null && qmd embed 2>/dev/null
```

## Degradation Summary

| Capability | Canonical write | Preferred read | Fallback |
|-----------|-----------------|----------------|----------|
| Learnings | `.beads/learnings/` | `qmd` + vault search | flat-file search |
| Critical patterns | `.beads/critical-patterns.md` | direct file read | same |
| Vault mirror | optional | N/A | omit |
