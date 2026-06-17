# Context Budget

> [!NOTE]
> This reference is subordinate to `references/kernel.md`. `references/kernel.md` is the canonical owner of BEO rules and invariants.

This file documents per-lane token budgets and per-phase read lists so a delivery skill can decide what to load without exceeding its working context window. It does not enforce — `beo_score_context.py` is the read-side check that flags drift.

## Lane budgets

| Lane | TICKET.yaml mode | Token budget |
| --- | --- | --- |
| tiny | `quick` | ~4K |
| normal | `standard` | ~8K |
| high-risk | `strict` | ~15K |

Numbers are agent working context after system prompt and BEO skill cards already loaded. They are advisory ceilings, not hard limits.

## Per-phase read lists

The five delivery phases are intake, planning, implementation, validation, and trace. Each phase has a minimum read set per lane. "Required" means the file MUST be loaded; "optional" means load only if the ticket references it.

### Phase: intake (TICKET.yaml mode determines lane)

| Lane | Required reads | Optional reads |
| --- | --- | --- |
| tiny | `beo-plan/SKILL.md` (or the active skill) | `references/degraded-tools.md` |
| normal | tiny + `beo-reference/SKILL.md`, `references/doctrine-map.md` | `references/safety.md`, `beo-setup/SKILL.md` |
| high-risk | normal + `references/kernel.md`, `registry/phase-contracts.json` | `beo-climate/SKILL.md`, `beo-climate/config.yaml` |

### Phase: planning

| Lane | Required reads | Optional reads |
| --- | --- | --- |
| tiny | `beo-plan/SKILL.md`, `references/lifecycle.md` | — |
| normal | tiny + `references/safety.md`, `registry/ticket.schema.json` | `examples/quick-mode-golden-trace.md` |
| high-risk | normal + `references/kernel.md`, `registry/reservation-schema.json` | `references/user-handoff.md` |

### Phase: implementation

| Lane | Required reads | Optional reads |
| --- | --- | --- |
| tiny | `beo-execute/SKILL.md` | `beo_run.py` (for verify command pattern) |
| normal | tiny + `beo-validate/SKILL.md`, `registry/approval-envelope.json` | `beo_state.py` operations |
| high-risk | normal + `references/kernel.md`, `registry/reservation-schema.json`, `beo_worktree.py` | `references/safety.md` |

### Phase: validation

| Lane | Required reads | Optional reads |
| --- | --- | --- |
| tiny | `beo-validate/SKILL.md` | `beo_check.py --help` |
| normal | tiny + `references/lifecycle.md`, `registry/approval-envelope.json` | `beo_check_approval.py` |
| high-risk | normal + `references/kernel.md`, `references/safety.md`, `registry/phase-contracts.json` | `beo_reservation.py` |

### Phase: trace

| Lane | Required reads | Optional reads |
| --- | --- | --- |
| tiny | `beo-reference/SKILL.md` (lookup) | — |
| normal | tiny + `examples/quick-mode-golden-trace.md` | — |
| high-risk | normal + `beo-review/SKILL.md`, `references/artifact-boundaries.md` | — |

## Out of budget (do NOT load)

- Full `beo-reference/scripts/` source (use `--help` or summary instead).
- All 10 skill cards at once (load only the active owner + adjacent phases).
- Full `runtime-events.jsonl` if it exceeds 1K lines (sample last 50 events).
- Obsidian vault content (use `qmd` semantic search for targeted recall).

## Drift detection

`beo_score_context.py` (advisory helper, see `scripts/beo_score_context.py`) checks actual files read against this table. The score is 0-3:
- 0: missing required files for the active phase+lane
- 1: all required files present
- 2: required + half of optional
- 3: required + most/all optional

A score of 0 is not a hard failure — it is advisory for the operator to widen context.

## Source

Inspired by the `repository-harness` plan's context-rules reference (draft, 2026-06-16). BEO numbers reflect the larger skill-card footprint (10 cards × 4-5K each) — harness used 2K/5K/10K which is too tight for BEO.
