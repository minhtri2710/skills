---
name: beo-dream
description: |
  Use when learnings from two or more accepted features need consolidation into shared canonical knowledge. Dream merges recurring patterns from existing feature learnings, retires stale guidance, and updates `critical-patterns.md` only with explicit user approval. Do not use for single-feature learning capture, product implementation, or speculative doctrine that lacks source evidence.
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-dream

## Atomic purpose
Consolidate multi-feature evidence into shared patterns and critical guidance.

## When to use
- 2 or more accepted features have learnings that should be merged or promoted
- `critical-patterns.md` needs evidence-backed refresh, merge, or retirement work
- the user explicitly requests pattern consolidation or dream work

## Inputs
**Required**
- at least two feature learning artifacts from `.beads/learnings/`
- current `.beads/critical-patterns.md`

**Optional**
- archive or staleness metadata
- historical attribution context allowed by local dream references

## Outputs
**Allowed writes**
- updated `.beads/critical-patterns.md` with explicit user approval
- archived or consolidated learning records as defined by the local dream references
- consolidation summary
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- feature-specific learning artifacts that belong to `beo-compound`
- code or planning artifacts
- invented patterns lacking source evidence

## Boundary rules
- Dream owns cross-feature synthesis and promotion.
- Dream does not create single-feature learnings, modify code, plans, or pipeline behavior.
- Dream generalizes only from existing evidence; it does not invent patterns without traceable source evidence.

## Minimum hard gates
- **MULTI-FEATURE-ONLY** — Require evidence from at least 2 completed features.
- **NO-INVENTION** — Every promoted pattern must trace back to source learnings.
- **EXPLICIT-PROMOTION-APPROVAL** — Any update to `critical-patterns.md` requires explicit approval via the structured question tool.
- **ARCHIVE-INSTEAD-OF-DELETE** — Retire stale guidance by archiving per the local dream references.
- **TERMINATE-ON-HANDOFF** and **FRESH-LOAD-REQUIRED** — Follow the shared session-boundary rules.

## Default loop
1. Read feature learning artifacts and the current `critical-patterns.md`.
2. Group recurring patterns and score them with the consolidation rubric.
3. Merge duplicates, separate genuinely distinct patterns, and identify stale guidance.
4. Prepare evidence-backed updates to `critical-patterns.md` and request explicit approval.
5. Apply approved changes, archive superseded guidance as needed, write handoff state to `beo-route`, and stop.

## References
| File | Use when |
|------|----------|
| `references/dream-operations.md` | Running consolidation and promotion work |
| `references/consolidation-rubric.md` | Deciding promote / retain / merge / archive |
| `references/agent-history-source-policy.md` | Constraining acceptable synthesis inputs |
| `references/pressure-scenarios.md` | Testing edge cases for dream decisions |
| `beo-reference` → `references/learnings-read-protocol.md` | Reading learnings and critical patterns consistently |
| `beo-reference` → `references/approval-gates.md` | User approval requirements for promotion |

## Handoff and exit
- Normal completion handoff: `beo-route`
- Dream is a support skill, not a mainline phase; route decides the next operational step.

## Context budget
If context exceeds 65%, checkpoint via the shared protocol in `beo-reference` → `references/shared-hard-gates.md`.

## Red flags
- running dream with evidence from only one feature
- promoting a pattern without traceable source learnings
- updating `critical-patterns.md` without explicit approval
- deleting stale guidance instead of archiving it
- continuing after writing handoff state
