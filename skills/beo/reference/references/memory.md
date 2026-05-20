# Semantic Memory and Mistake Prevention

BEO uses a dynamic semantic memory system to prevent repeated mistakes, index past bugs, and preserve reusable success patterns without adding pipeline overhead.

---

## 1. Safety and Advisory Status

- **Advisory Only**: Memory is strictly advisory. It never grants approval, execution permissions (`PASS_EXECUTE`), review verdicts, Beads closure, or Human Gate authorizations.
- **Delivery Isolation**: Memory failures or missing indexes must never block ticket delivery.
- **Privacy & Security**: Learning and recall files store only structural/concept handles, never credential values or secrets.

---

## 2. Querying Memory (Native Recall)

The standalone `beo-recall` owner is deprecated. Instead, all delivery owners (`plan`, `execute`, `review`, `debug`) run native semantic queries using the integrated `beo_recall.py` helper script:
```bash
rtk python3 skills/beo/reference/scripts/beo_recall.py --issue <issue-id>
```

### Retrieval Sequence
The recall helper automatically searches across three layers in order:
1. **`qmd` Vector Engine**: Searches the configured Obsidian/BEO learning collection.
2. **Direct Markdown Walk**: If `qmd` is unavailable, walks files inside `$BEO_OBSIDIAN_VAULT/beo-learnings/` directly.
3. **Local Artifacts Fallback**: Inspects issue-local artifacts under `.beads/artifacts/*/learning/`.

---

## 3. Storage Backend: Obsidian CLI

Post-accept learnings are written by `beo-learn` using the Obsidian CLI when configured.

- **Target Path**: `$BEO_OBSIDIAN_VAULT/beo-learnings/`
- **Dynamic Vault Resolution**: The target vault path and collection name are resolved dynamically from env variables:
  - `BEO_OBSIDIAN_VAULT`
  - `BEO_OBSIDIAN_VAULT_NAME`
  - `BEO_OBSIDIAN_VAULT_ID`
  - `BEO_QMD_COLLECTION` (Falls back to `second-brain` if none are defined)
- **Persistence Command**:
  ```bash
  obsidian vault="$BEO_OBSIDIAN_VAULT" create path="beo-learnings/<note-slug>.md" content="<content>"
  ```
- **Obsidian Sandbox**: The Obsidian CLI may only read/write files within the authorized vault. It never touches `.git/`, `.beads/`, or product source code.

---

## 4. Vector Engine: `qmd`

`qmd` is the primary vector search engine for BEO memory. It indexes and embeds learnings automatically on save to enable instant similarity searches.

- **Initialization & Indexing**:
  ```bash
  rtk qmd collection add "$BEO_OBSIDIAN_VAULT/beo-learnings/" --name "$BEO_QMD_COLLECTION"
  rtk qmd update
  ```
- **Semantic Similarity Query**:
  ```bash
  rtk qmd query "<query-prose>" --collection "$BEO_QMD_COLLECTION"
  ```
- **Fallback Persistence**: If Obsidian or `qmd` are unavailable, `beo-learn` writes markdown cases directly to:
  `.beads/artifacts/<issue-id>/learning/YYYY-MM-DD--<case-type>--<bead-id>--<slug>.md`
