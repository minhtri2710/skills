---
name: beo-compound
description: |
  Extract durable learnings from one accepted feature and optionally promote a reusable pattern with explicit approval. Use only for single-feature learning extraction after acceptance, not for corpus-wide consolidation, implementation, or review.

---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-compound

## Atomic purpose
Extract and store learnings for one accepted feature.

## When to use
- review has accepted a feature and its lessons have not yet been captured
- a completed feature needs its durable learnings preserved before the pipeline closes

## Inputs
**Required**
- accepted feature slug or identifier
- `.beads/artifacts/<feature_slug>/review-findings.md`
- feature bead history and comments
- relevant implementation artifacts for that feature

**Optional**
- prior feature learning artifacts for deduplication only
- existing `.beads/critical-patterns.md` only for deduplication or promotion checks

## Outputs
**Allowed writes**
- `.beads/learnings/YYYYMMDD-<feature_slug>.md`
- updates to `.beads/critical-patterns.md` only with explicit approval
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- learnings for other features
- planning, implementation, or review artifacts

## Boundary rules
- Compound owns learning extraction for one accepted feature only.
- Compound must not run before review acceptance, merge evidence across multiple features, modify code or plans, or perform corpus-wide consolidation, retirement, or restructuring.
- Any promoted pattern must be traceable to that accepted feature.
- Compound must not create or rewrite review artifacts.

## Minimum hard gates
- **POST-REVIEW-ONLY** — Start only after review acceptance.
- **SINGLE-FEATURE-SCOPE** — Write learnings for exactly one feature.
- **EXPLICIT-PROMOTION-APPROVAL** — Any write to `critical-patterns.md` requires explicit approval via the runtime's canonical user-interaction mechanism.
- **GENERALIZE-BEFORE-PROMOTION** — Promoted patterns must be evidence-backed and traceable to the accepted feature.
- **TERMINATE-ON-HANDOFF** and **FRESH-LOAD-REQUIRED** — Follow the shared session-boundary rules.

## Default loop
1. Read the accepted feature's review findings, bead history, and implementation evidence.
2. Extract what worked, what failed, what surprised the team, and what should be remembered.
3. Separate feature-local observations from reusable patterns supported by that feature.
4. Write `.beads/learnings/YYYYMMDD-<feature_slug>.md` using the local learning template.
5. If reusable patterns are warranted, present the proposed `critical-patterns.md` updates, obtain explicit approval, apply the approved promotions, and stop after writing handoff state to `beo-route`.

## References
| File | Use when |
|------|----------|
| `references/compounding-operations.md` | Running the extraction and writing flow |
| `references/learnings-template.md` | Structuring the feature learning artifact |
| `beo-reference` → `references/knowledge-store.md` | Syncing feature learnings into the knowledge store when available |
| `beo-reference` → `references/learnings-read-protocol.md` | Reading other learnings for deduplication without turning compound into dream |

## Handoff and exit
- Normal completion handoff: `beo-route`
- Compound does not branch into dream automatically; route decides any later long-horizon consolidation work.

## Context budget
If context exceeds 65%, checkpoint via the shared protocol in `beo-reference` → `references/shared-hard-gates.md`.

## Red flags
- running before review acceptance
- merging evidence from multiple features inside compound
- promoting a pattern that is not traceable to the accepted feature
- producing empty or content-free learnings
- continuing after writing handoff state
