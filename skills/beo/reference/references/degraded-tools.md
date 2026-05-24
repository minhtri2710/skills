# Degraded Tool Guidance

BEO is designed to degrade gracefully when optional tooling is missing. This reference defines degraded-mode behavior for each tool and guides operators on what remains available.

---

## Tool Authority Matrix

| Tool | Required | Authority | Degraded Fallback |
|------|----------|-----------|-------------------|
| `br` | Yes | Issue lifecycle, claims, dependency edges, closure | None; BEO cannot operate without br |
| `bv` | No | Read-only triage and graph orientation | Manual issue selection via br show/ready |
| `qmd` | No | Advisory semantic memory recall | Direct markdown fallback or issue-local artifacts |
| Obsidian CLI | No | Durable learning note persistence | Local markdown fallback under .beads/artifacts/*/learning/ |

---

## Per-Tool Degradation Scenarios

### `br` (Required)

**Authority**: Issue lifecycle, claim/unclaim, comment, dependency edges, status transitions, closure.

**Detection**: Run `br capabilities --format json` to verify availability and supported commands.

**Degraded Behavior**: BEO cannot operate without `br`. All delivery phases require canonical issue state from `br show` and lifecycle mutations via `br update`, `br create`, `br close`.

**Operator Guidance**:
- If `br` is missing, install Beads CLI (>= 0.1.28) before attempting BEO workflow.
- If `br capabilities` fails or returns empty, verify `.beads/` repo initialization.
- Setup skill will report `br_missing` or `br_degraded` and block delivery workflow activation.

---

### `bv` (Optional, Triage)

**Authority**: Read-only graph orientation, dependency visualization, robot triage (`bv --robot-triage`, `bv --robot-next`).

**Detection**: Check for `bv` executable or `br capabilities` reporting `bv` availability.

**Degraded Behavior**: When `bv` is missing:
- Plan phase loses automated triage and robot-next orientation.
- Operators must select ready issues manually via `br ready --json`.
- Review phase loses graph-aware routing suggestions.
- Dependency visualization is unavailable; use `br show <issue-id> --json` blocked_by/blocking fields.

**Operator Guidance**:
- BEO delivery workflow remains fully functional; `bv` is convenience only.
- Plan and review phases should use `br ready` and `br show` for issue selection.
- Automated triage and next-issue suggestions are unavailable but not required.
- Setup skill will report `bv_missing` or `bv_available` but will not block delivery.

**Fallback Commands**:
- `br ready --json` → discover unblocked ready issues
- `br show <issue-id> --json` → inspect dependencies and status

---

### `qmd` (Optional, Memory Recall)

**Authority**: Advisory semantic memory recall via hybrid/vector search over BEO learning notes.

**Detection**: Check for `qmd` executable and valid collection configuration (`BEO_QMD_COLLECTION`).

**Degraded Behavior**: When `qmd` is missing:
- Recall helper (`beo_recall.py`) falls back to direct markdown search under `$BEO_OBSIDIAN_VAULT/beo-learnings/`.
- If Obsidian vault is also unavailable, recall falls back to issue-local artifacts under `.beads/artifacts/*/learning/`.
- Semantic/vector recall is unavailable; only exact keyword or glob matching remains.
- Memory queries degrade to file system search; recall precision and relevance drops.

**Operator Guidance**:
- BEO delivery workflow remains fully functional; memory is strictly advisory.
- Recall will attempt vault markdown fallback first, then issue-local artifacts.
- Missing recall context may reduce mistake-prevention coverage but never blocks delivery.
- Setup skill will report `qmd_missing` or `qmd_available`.

**Fallback Recall**:
- Direct markdown search: `grep -r <pattern> $BEO_OBSIDIAN_VAULT/beo-learnings/`
- Issue-local fallback: `.beads/artifacts/*/learning/*.md`
- Recall summaries will note degraded search backend in frontmatter: `qmd_indexed: false`

---

### Obsidian CLI (Optional, Learning Persistence)

**Authority**: Durable learning note writes to configured vault after review verdict or debug return.

**Detection**: Check for `obsidian` executable and valid vault configuration (`BEO_OBSIDIAN_VAULT`, `BEO_OBSIDIAN_VAULT_NAME`, or `BEO_OBSIDIAN_VAULT_ID`).

**Degraded Behavior**: When Obsidian CLI is missing:
- Learning write helper (`beo_memory_write.py`) falls back to local markdown under `.beads/artifacts/<issue-id>/learning/`.
- Learning notes are written as plain markdown files with YAML frontmatter.
- Notes remain queryable but lose Obsidian vault features (wikilinks, graph view, plugins).
- `qmd` indexing may still work if configured to watch `.beads/artifacts/` instead of vault.

**Operator Guidance**:
- BEO delivery workflow remains fully functional; learning is post-accept only.
- Learning notes persist locally and remain searchable via filesystem or qmd (if configured).
- Vault-based workflows (wikilink navigation, graph exploration) are unavailable.
- Setup skill will report `obsidian_cli_missing` or `obsidian_cli_available`.

**Fallback Learning Paths**:
- Local markdown: `.beads/artifacts/<issue-id>/learning/YYYY-MM-DD--<case-type>--<bead-id>--<slug>.md`
- Notes include frontmatter: `memory_backend: fallback_local_markdown`, `qmd_indexed: false|true`
- Setup can configure qmd to index local fallback directory if desired.

---

## Compatibility Reporting

Setup skill (`beo-setup`) provides structured compatibility reporting via `beo_setup_compat.py` helper.

**Report Shape**:
```json
{
  "tools": {
    "br": {"status": "available", "version": "0.1.28"},
    "bv": {"status": "missing", "reason": "executable not found"},
    "qmd": {"status": "available", "version": "0.3.1"},
    "obsidian": {"status": "degraded", "reason": "vault not configured"}
  },
  "workflow_readiness": "ready|degraded|blocked",
  "degraded_capabilities": ["bv_triage", "obsidian_persistence"],
  "operator_guidance": "BEO workflow is ready. Triage and vault persistence are degraded but not required."
}
```

**Workflow Readiness States**:
- `blocked`: `br` is missing; BEO cannot operate.
- `degraded`: `br` is available but optional tools are missing; workflow runs with reduced convenience/memory.
- `ready`: All tools available and configured.

---

## Design Principles

1. **Advisory Memory**: Missing qmd/Obsidian degrades recall and learning persistence but never blocks delivery.
2. **Required Lifecycle**: `br` is mandatory; missing `br` blocks all BEO workflow.
3. **Optional Convenience**: `bv` is orientation/triage only; missing `bv` requires manual issue selection.
4. **Graceful Fallback**: Each optional tool has a documented fallback path that preserves core workflow.
5. **No Authority Drift**: Degraded mode never bypasses approval, containment, review, or closure gates.
6. **Operator Transparency**: Setup reports exact degradation status and remaining capabilities.


## Emergency Bypass & BEO Off Switch Policy

### Manual Suspension Mechanism
To work directly with Beads/Git without breaking BEO safety states in critical production hotfixes or environment failures, an operator can manually create an explicit suspension flag/file: `.beads/bypass.json` declaring `reason`, `operator`, `timestamp`, and `affected_issues`. This marks BEO delivery as suspended. 

> [!WARNING]
> While active, the BEO bypass does NOT relax validation checks, bypass safety gates, or grant `PASS_EXECUTE`. It strictly halts and blocks normal BEO delivery pipelines, signaling to tools and agents that manual out-of-band operations are in progress.

### Audit Trail Requirements
All emergency out-of-band updates executed during suspension must be manually annotated by the operator via a Beads comment or a Git commit message clearly explaining the emergency justification and listing all affected paths.

### Post-Suspension Convergence Protocol
Before normal BEO delivery can resume, the out-of-band changes must be reconciled. The operator must run `beo_reconcile_state.py` (accessible under the `beo-setup` maintenance skill) to parse the out-of-band Git diffs/Beads mutations, regenerate the prestate hashes for modified files, align the state records, and cleanly archive the bypass flag file. Normal BEO delivery pipelines remain blocked until reconciliation converges successfully.

---

## Cross-References

- Canonical tool authority: `command-contracts.json`
- Memory fallback protocol: `memory.md`
- Setup skill: `skills/beo/setup/SKILL.md`
- Compatibility helper: `scripts/beo_setup_compat.py`
