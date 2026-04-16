---
name: beo-dream
description: |
  Use when learnings from 2+ accepted features need consolidation into shared canonical knowledge. Synthesizes cross-feature patterns from existing evidence, merges duplicates, retires stale entries, and updates critical-patterns.md with user approval. Sole owner of shared-pattern promotion. Do not use for single-feature extraction (use beo-compound), to invent patterns without source evidence, or to modify code or pipeline flow.
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References**: Protocol rules reference the `beo-reference` skill via `→ references/<file>` for canonical documents.

# beo-dream

## Overview
**Atomic purpose: consolidate learnings across multiple features into durable system-wide patterns.** Consolidate multi-feature learnings into shared canonical knowledge. **Core principle: synthesize only from existing evidence, never invent net-new patterns.**

## Boundary Rules
- **MUST NOT** perform independent state detection or free-form routing — owned by `beo-route`. May emit canonical handoff to the next allowed pipeline skill when exit conditions are met.
- **MUST NOT** gather requirements — owned by `beo-explore`.
- **MUST NOT** decompose work — owned by `beo-plan`.
- **MUST NOT** write code — owned by `beo-execute`.
- **MUST NOT** review implementations — owned by `beo-review`.
- **MUST NOT** capture single-feature learnings — owned by `beo-compound`.
- **MUST NOT** diagnose failures — owned by `beo-debug`.
- **MUST NOT** create or test skills — owned by `beo-author`.

## Hard Gates
> **HARD-GATE: MULTI-FEATURE-ONLY** — Dream requires learnings from at least 2 completed features. If only 1 feature exists, stop and use `beo-compound`.

> **HARD-GATE: AMBIGUOUS-PROMOTION-APPROVAL** — All appends to `critical-patterns.md` require explicit user approval per the beo approval gates (`beo-reference` → `references/approval-gates.md`). If approval is missing, stop promotion and surface the decision.

> **HARD-GATE: NO-INVENTION** — Dream only consolidates, merges, and promotes learnings already present in source artifacts. If a pattern does not appear in feature learnings, it cannot be created here.

## Communication Standard
> Follow the communication standard (`beo-reference` → `references/communication-standard.md`).

## Default Dream Loop
1. **Read** — Load `.beads/learnings/` and `.beads/critical-patterns.md` using artifact conventions (`beo-reference` → `references/artifact-conventions.md`). Follow `references/dream-operations.md` and `references/agent-history-source-policy.md` while collecting source material.
2. **Identify patterns** — Find learnings repeated across at least 2 completed features, group them by theme, and score them with `references/consolidation-rubric.md`.
3. **Consolidate** — Merge duplicate or overlapping learnings into canonical entries while preserving feature attribution and keeping state handling aligned with the bead lifecycle states (`beo-reference` → `references/status-mapping.md`).
4. **Promote** — For entries that meet the promotion rubric, prepare updates to `.beads/critical-patterns.md`; require explicit user approval for all appends per the beo approval gates (`beo-reference` → `references/approval-gates.md`).
5. **Archive** — Archive stale or superseded learnings instead of deleting them, following standard failure recovery (`beo-reference` → `references/failure-recovery.md`).

### Reference Files
| File | Purpose |
|------|---------|
| `references/dream-operations.md` | Defines dream execution flow, consolidation mechanics, and output expectations |
| `references/consolidation-rubric.md` | Scores recurring learnings for promotion, retention, merge, or archive decisions |
| `references/agent-history-source-policy.md` | Constrains what historical material dream may use as synthesis input |
| `references/pressure-scenarios.md` | Provides edge cases and validation scenarios for dream behavior |

## Operations
### dream-consolidate
- Read all feature learnings.
- Identify cross-feature patterns.
- Merge duplicates.
- Promote recurring patterns.
- Archive stale entries.
- Update `critical-patterns.md`.

### dream-pressure-test
- Validate current `critical-patterns.md` entries against the current repository state.
- Remove or archive patterns that no longer apply.
- Flag patterns that have drifted and require review.

## Inputs and Outputs
- **Inputs** — At least two feature learnings files from `.beads/learnings/`, current `.beads/critical-patterns.md`, optional archive/staleness metadata.
- **Outputs** — Consolidated learning updates, archived/superseded entries, approved updates to `.beads/critical-patterns.md`, consolidation summary.

## Decision Rubrics
### Promote vs Keep Local
- **Promote** when the pattern appears in at least 2 completed features, has high impact, and is actionable.
- **Keep local** when the learning is single-feature, weakly evidenced, or too situational for shared promotion.

### Archive vs Retain
- **Archive** when the learning is older than 6 months, is not supported by active code or current practice, and has been superseded.
- **Retain** when it is still applicable, still referenced, or lacks a clear replacement.

### Merge vs Separate
- **Merge** when multiple entries express the same practical insight with only wording differences.
- **Separate** when the entries produce different guidance, different risks, or different operational decisions.

## Special Rules
- Treat input and output paths according to artifact conventions (`beo-reference` → `references/artifact-conventions.md`).
- Use the learnings read protocol (`beo-reference` → `references/learnings-read-protocol.md`) for reading learnings and critical patterns.
- Route any blocked or invalid state through standard failure recovery (`beo-reference` → `references/failure-recovery.md`).
- Preserve canonical pipeline contracts (`beo-reference` → `references/pipeline-contracts.md`) while treating `dream` as a periodic support skill rather than a main pipeline stage.

## Handoff
> Handoff to `beo-route` for next-action detection after consolidation completes. Write `STATE.json` for the normal transition, and reserve `HANDOFF.json` for emergency checkpoint or low-context resume scenarios.

## Context Budget
> If context exceeds 65% capacity, compress non-essential history before continuing (`beo-reference` → `references/shared-hard-gates.md`).

## Red Flags & Anti-Patterns
- Running dream with learnings from only 1 feature
- Promoting a pattern that cannot be traced to source feature learnings
- Updating `critical-patterns.md` without explicit user approval for every append
- Deleting stale learnings instead of archiving them
- Modifying feature-specific learnings that belong to `beo-compound`
