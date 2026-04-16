---
name: beo-compound
description: |
  Use only after review has accepted a completed feature and that single feature’s lessons need to be captured durably. Compound extracts feature-scoped learnings, separates feature-local observations from candidate reusable patterns, and writes one feature learning artifact. Do not use before review acceptance, for multi-feature synthesis, code changes, or promotion of shared patterns into `critical-patterns.md`.
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-compound

## Atomic purpose
Extract and record durable learnings from one accepted feature.

## When to use
- review has accepted a feature and learnings have not yet been captured
- a completed feature needs its lessons preserved before the pipeline closes

## Inputs
**Required**
- accepted feature identifier / slug
- `.beads/artifacts/<feature_slug>/review-findings.md`
- bead history / comments for the feature
- relevant implementation artifacts for that feature

**Optional**
- prior feature learning artifacts for deduplication only

## Outputs
**Allowed writes**
- `.beads/learnings/YYYYMMDD-<feature_slug>.md`
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- `.beads/critical-patterns.md`
- learnings for other features
- planning, implementation, or review artifacts

## Boundary rules
- Compound is single-feature only.
- Compound extracts what one feature taught; it does not consolidate evidence across features.
- Compound must not update `.beads/critical-patterns.md` and may only flag candidate reusable patterns inside the feature learning artifact.

## Minimum hard gates
- **POST-REVIEW-ONLY** — Start only after review acceptance.
- **SINGLE-FEATURE-SCOPE** — Write learnings for exactly one feature.
- **NO-SHARED-PATTERN-WRITES** — Do not write `critical-patterns.md`.
- **GENERALIZE-BEFORE-FLAGGING** — Candidate shared patterns must be framed as evidence-backed candidates, not promoted rules.
- **TERMINATE-ON-HANDOFF** and **FRESH-LOAD-REQUIRED** — Follow the shared session-boundary rules.

## Default loop
1. Read the accepted feature's review findings, bead history, and implementation evidence.
2. Extract what worked, what failed, what surprised the team, and what should be remembered.
3. Separate feature-local observations from candidate reusable patterns.
4. Write `.beads/learnings/YYYYMMDD-<feature_slug>.md` using the local learning template.
5. Hand off to `beo-route` and stop.

## References
| File | Use when |
|------|----------|
| `references/compounding-operations.md` | Running the extraction and writing flow |
| `references/learnings-template.md` | Structuring the feature learning artifact |
| `beo-reference` → `references/knowledge-store.md` | Syncing feature learnings into the knowledge store when available |
| `beo-reference` → `references/learnings-read-protocol.md` | Reading other learnings for deduplication without turning compound into dream |

## Handoff and exit
- Normal completion handoff: `beo-route`
- Compound does not promote shared patterns or branch into dream automatically; route decides any later dream work.

## Context budget
If context exceeds 65%, checkpoint via the shared protocol in `beo-reference` → `references/shared-hard-gates.md`.

## Red flags
- running before review acceptance
- writing shared patterns directly into `critical-patterns.md`
- merging evidence from multiple features inside compound
- producing empty or content-free learnings
- continuing after writing handoff state
