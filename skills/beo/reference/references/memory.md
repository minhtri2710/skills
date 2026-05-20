# BEO Memory

## Purpose

BEO memory prevents repeated agent mistakes and preserves reusable success patterns without changing delivery authority.

## Authority

Memory is advisory. It never grants approval, execution permission, review verdicts, Beads closure, product mutation authority, or Human Gate authorization.

## Preferred Write Backend

`beo-learn` writes learning notes through Obsidian CLI when available.

Target directory: `$BEO_OBSIDIAN_VAULT/beo-learnings/`.

### Obsidian CLI Implementation
- **Vault Targeting**: Use `vault=<name|id>` as required by the Obsidian CLI for the target vault.
- **Note Management**: Use `obsidian vault=<v> create path=beo-learnings/<note>.md content=<markdown>` for learning persistence.
- **Boundary**: Obsidian CLI may read/write only within the authorized vault. It never touches `.git/`, `.beads/`, or product source code unless explicitly authorized for a separate task.

## Search Backend: qmd

qmd is the primary semantic and full-text search engine for BEO memory.

### qmd CLI Implementation
- **Initialize**: `qmd collection add $BEO_OBSIDIAN_VAULT/beo-learnings/ --name beo`
- **Maintenance**: `qmd update`
- **Health Check**: `qmd status` to verify indexing status.
- **Query**: `qmd query "<query>"` for retrieval during `beo-recall`.

## Fallback Backend

`beo-learn` must record the learning case even when Obsidian CLI or qmd is unavailable.
Fallback path: `.beads/artifacts/<issue-id>/learning/YYYY-MM-DD--<case-type>--<bead-id>--<slug>.md`

## Recall Rule

`beo-recall` searches:
1. qmd configured BEO/Obsidian learning collection.
2. Obsidian learning notes directly if qmd is unavailable.
3. Issue-local learning artifacts under `.beads/artifacts/*/learning/`.

## Delivery Isolation

Memory failures must not block delivery. Learning and recall store secret handles only, never secret values. Reusable behavior belongs in BEO skills, doctrine, or registries authored by `beo-author`, not memory.

