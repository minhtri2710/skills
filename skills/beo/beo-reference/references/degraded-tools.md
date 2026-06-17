# Degraded Tool Guidance

> [!NOTE]
> This reference is subordinate to `references/kernel.md`. `references/kernel.md` is the canonical owner of BEO rules and invariants.

This file guidance focuses on setup checks. Authority invariants are canonical in `references/kernel.md`.

## Tool requirements

| Tool | Status | Purpose | If missing |
| --- | --- | --- | --- |
| `br` | Required | Issue lifecycle, claims, comments, closure | Block BEO delivery readiness. |
| PyYAML | Required | Parse BEO YAML/JSON artifacts | Block helper execution. |
| `bv` | Optional | Read-only graph orientation | Use `br ready --json` and `br show --json`. |
| `qmd` | Optional | Advisory semantic recall | Disable semantic search. |
| Obsidian | Optional | Reusable learning note vault | Fall back to `.beads/learnings/`. |
| `beo_verify.py` | Optional | Queryable verification runner | Skip verification_run events; `beo-execute` still records its own verify_results. |
| `beo_score_trace.py` / `beo_score_context.py` | Optional | Advisory scoring helpers | Skip score events; no functional impact. |
| `beo_audit.py` / `beo_propose.py` | Optional | Drift detection and proposal generation | Skip audit findings; `check_skill_bundle.py` still validates schema integrity. |

## Minimum viable BEO

BEO delivery can run when:

- `br` works,
- BEO artifacts can be read/written,
- YAML/JSON helper dependencies work,
- repo working tree can be inspected.

BEO delivery does not require:

- `bv`,
- qmd,
- Obsidian CLI,
- semantic memory,
- repo `AGENTS.md`.

## AGENTS.md bootstrap

A missing repo `AGENTS.md` is setup guidance, not a required-tool blocker. Authorized setup may create `AGENTS.md` from `templates/AGENTS.template.md` when missing, always replace the current `BEO:MANAGED` block from the template when valid markers already exist, or append the managed block only when no managed block exists without overwriting unmanaged content. Malformed managed markers require manual repair; setup must not edit them.

## Reporting

`beo_setup.py` reports:

- control-plane readiness: `ready|blocked`
- advisory memory status: `ok|degraded|missing`
- `AGENTS.md` bootstrap status: `missing|installed|managed_current|managed_stale|managed_refreshed|unmanaged_exists|managed_appended|malformed_markers`
- operator guidance for the narrow missing dependency or degraded capability

Keep degraded reports short, concrete, and separated by authority class.
