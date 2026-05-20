# Semantic Memory and Mistake Prevention

BEO uses a markdown-first learning loop to prevent repeated mistakes and preserve reusable success patterns without adding delivery authority.

Use one backend role per job; do not duplicate storage or authority:
- [obsidian](https://obsidian.md/cli) CLI writes durable learning case notes inside the configured vault.
- [qmd](https://github.com/tobi/qmd) indexes, embeds, and searches those notes for semantic recall.
- `.beads/artifacts/` stores issue-local fallback evidence only when external memory is unavailable or a claimed issue needs a durable recall summary.

---

## 1. Safety and Advisory Status

- **Advisory Only**: Memory is strictly advisory. It never grants approval, execution permissions (`PASS_EXECUTE`), review verdicts, Beads closure, or Human Gate authorizations.
- **Delivery Isolation**: Memory failures or missing indexes must never block ticket delivery.
- **Privacy & Security**: Learning and recall files store only structural/concept handles, never credential values or secrets.

---

## 2. Recall Protocol
Recall is advisory context for delivery owners (`plan`, `execute`, `review`, `debug`); it never becomes an approval source.

Default helper:
```bash
rtk python3 skills/beo/reference/scripts/beo_recall.py --issue <issue-id>
# after claim, when a durable artifact is needed:
rtk python3 skills/beo/reference/scripts/beo_recall.py --issue <issue-id> --write-summary
```

The helper searches, in order:
1. `qmd` hybrid/vector recall for the configured BEO learning collection.
2. Direct markdown under `$BEO_OBSIDIAN_VAULT/beo-learnings/` if `qmd` is unavailable.
3. Issue-local fallback artifacts under `.beads/artifacts/*/learning/`.

When using `qmd` directly, retrieve full matching notes with `qmd get` or `qmd multi-get` before relying on them; snippets are leads only.
---

## 3. Learning Note Shape

Each note is plain Obsidian markdown with YAML frontmatter and a short body:

```yaml
title: <case title>
created_at: <ISO-8601 timestamp>
case_type: <registered case type>
source_bead_id: <issue-id>
source_phase: <beo-review|beo-debug>
condition_id: <pipeline condition>
basis_ref: <ticket/review/debug evidence ref>
evidence_refs: [<safe refs>]
memory_backend: <obsidian_cli|fallback_local_markdown>
qmd_indexed: <true|false|not_run>
secret_policy: handles_only
tags: [beo/learning, <case_type>]
```

Body headings: Trigger, Lesson, Reuse/Prevention Rule, Evidence refs, Non-authority disclaimer.

---

## 4. Storage Backend: Obsidian CLI

Post-accept learnings are written by `beo-learn` through `beo_memory_write.py`; the helper uses Obsidian CLI when configured and falls back to local markdown.

- **Target Path**: `$BEO_OBSIDIAN_VAULT/beo-learnings/`
- **Dynamic Vault Resolution**: The target vault path and collection name are resolved from:
  - `BEO_OBSIDIAN_VAULT`
  - `BEO_OBSIDIAN_VAULT_NAME`
  - `BEO_OBSIDIAN_VAULT_ID`
  - `BEO_QMD_COLLECTION` (falls back to `second-brain` if none are defined)
- **Command Contract**: `command-contracts.json` owns Obsidian CLI argument shape; setup must verify the installed dialect before Obsidian-backed writes are enabled.
- **Boundary**: Obsidian writes only inside the authorized vault learning directory. It never writes `.git/`, `.beads/`, or product source code.

---

## 5. Vector Engine: `qmd`

`qmd` is the primary search engine for BEO memory. It indexes learnings after save and supports hybrid, lexical, and semantic recall. Index/config writes are allowed only after a `beo-learn` note write or an explicitly authorized setup maintenance command.

- **Setup & Indexing**: `beo_setup.py --configure-memory` and `beo_setup.py --refresh-memory-index` are the only setup-owned memory maintenance entry points; exact command contracts live in `command-contracts.json`.
- **Recall Queries**: Prefer `beo_recall.py`; direct `qmd` use must follow `command-contracts.json` and hydrate matches with `qmd get` or `qmd multi-get` before relying on them.
- **Fallback Persistence**: If Obsidian or `qmd` are unavailable, `beo-learn` writes markdown cases directly to:
  `.beads/artifacts/<issue-id>/learning/YYYY-MM-DD--<case-type>--<bead-id>--<slug>.md`
