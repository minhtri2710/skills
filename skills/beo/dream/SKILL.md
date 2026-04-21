---
name: beo-dream
description: |
  Consolidate multiple accepted-feature learnings into stable corpus-level guidance when repeated patterns, duplication, conflicts, or stale guidance require long-term maintenance. Use only for corpus maintenance, not for single-feature learning capture, immediate post-review promotion, implementation, or operational delivery.

---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References** — Shared protocol rules live in `beo-reference` → `references/<file>`.

# beo-dream

## Atomic purpose
Maintain and consolidate the shared learning corpus.

## When to use
- accumulated learnings or promoted patterns need deduplication, retirement, or restructuring
- `critical-patterns.md` needs an evidence-backed refresh, merge, or retirement pass
- the user explicitly requests long-term pattern consolidation

## Inputs
**Required**
- current `.beads/critical-patterns.md`
- relevant feature learning artifacts from `.beads/learnings/`

**Optional**
- archive or staleness metadata
- historical attribution context allowed by policy

## Outputs
**Allowed writes**
- updated `.beads/critical-patterns.md` only with explicit approval
- archived or consolidated learning records defined by protocol
- consolidation summary
- `.beads/STATE.json`
- `.beads/HANDOFF.json` only when checkpoint or resume protocol requires it

**Must not write**
- feature-specific learning artifacts that belong to `beo-compound`
- code or planning artifacts
- invented patterns lacking source evidence

## Boundary rules
- Dream owns long-term consolidation only.
- Dream must not handle a single accepted feature in isolation or perform immediate post-review promotion that belongs to `beo-compound`.
- Dream must not create or rewrite a single feature learning artifact except for archive bookkeeping, modify code, plans, or pipeline behavior, or invent patterns without traceable source evidence.
- Dream operates on the accumulated corpus, not one accepted feature in isolation.

## Minimum hard gates
- **CORPUS-LEVEL-ONLY** — Operate on the accumulated learnings and pattern corpus, never a single accepted feature in isolation.
- **NO-INVENTION** — Every promoted pattern must trace back to source learnings.
- **EXPLICIT-PROMOTION-APPROVAL** — Any update to `critical-patterns.md` requires explicit approval via the runtime's canonical user-interaction mechanism.
- **ARCHIVE-INSTEAD-OF-DELETE** — Retire stale guidance by archiving per the local dream references.
- **TERMINATE-ON-HANDOFF** and **FRESH-LOAD-REQUIRED** — Follow the shared session-boundary rules.

## Default loop
1. Read the current `critical-patterns.md` and the relevant supporting learnings corpus.
2. Group recurring guidance, trace it back to source learnings, and identify duplicates, conflicts, or stale entries.
3. Prepare evidence-backed consolidation, retirement, or restructuring updates using the consolidation rubric.
4. Request explicit approval for the proposed `critical-patterns.md` changes.
5. Apply approved changes, archive superseded guidance as needed, write handoff state to `beo-route`, and stop.

## References
| File | Use when |
|------|----------|
| `references/dream-operations.md` | Running consolidation and long-horizon maintenance work |
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
- running dream on a single accepted feature that belongs in compound
- promoting a pattern without traceable source learnings
- updating `critical-patterns.md` without explicit approval
- deleting stale guidance instead of archiving it
- continuing after writing handoff state
