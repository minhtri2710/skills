---
name: beo-dream
description: >-
  Use when beo learnings need a manual consolidation pass across multiple
  completed features, especially when learnings have gone stale, repeated
  patterns are accumulating, or the user asks to consolidate, clean up, merge,
  or promote existing learnings. Use for prompts like "run dream",
  "consolidate learnings", "merge repeated learnings", or "do a learnings pass".
  Do not use for single-feature learnings capture (use beo-compounding
  instead).
---

<HARD-GATE>
Onboarding — see `../reference/references/shared-hard-gates.md` § Onboarding Check.
</HARD-GATE>

# Beo Dream

## Overview

Run one manual consolidation pass across accumulated learnings.
Update durable learnings in place, keep the write surface narrow, and promote only patterns that still deserve long-term attention.
> See `../reference/references/shared-hard-gates.md` § Shared References Convention.


**Core principle:** consolidate carefully; do not confuse repeated mention with durable signal.

## Hard Gates

<HARD-GATE>
If ownership is ambiguous, ask the user instead of silently choosing a merge target.
</HARD-GATE>

<HARD-GATE>
Follow the learnings write-governance rules in `../reference/references/knowledge-store.md`, including PII redaction and approval before any `critical-patterns.md` promotion.
</HARD-GATE>

<HARD-GATE>
Dream must never create new beads, epics, or feature artifacts. It only reads and consolidates existing learnings.
</HARD-GATE>

<HARD-GATE>
Every consolidated learning must include the source feature slug and original capture date.
</HARD-GATE>

<HARD-GATE>
If recurring mode yields zero actionable candidates after a full source scan, escalate to bootstrap mode before finalizing. Do not finalize an empty recurring pass without attempting the broader bootstrap window.
</HARD-GATE>

<HARD-GATE>
Every dream run must write an updated provenance record to `.beads/learnings/dream-run-provenance.md` before finalizing, regardless of whether any learnings were merged, created, or skipped.
</HARD-GATE>

The durable write surface is `.beads/learnings/*.md`.

## Use Dream vs Compounding

| Use | Skill |
| --- | --- |
| Consolidate learnings from one completed feature | `beo-compounding` |
| Consolidate, deduplicate, or promote learnings across multiple completed features over time | `beo-dream` |

When in doubt: compounding is per-feature; dream is cross-feature.

## Default Dream Loop

1. orient on provenance; choose bootstrap or recurring mode
2. select the source window
3. extract and classify candidates
4. apply outcomes: merge, create, skip, or ask when ownership is ambiguous
5. finalize and update provenance

Load `references/dream-operations.md` for exact provenance checks, source selection, candidate classification, apply-outcome behavior, and finalization.
Use `../reference/references/failure-recovery.md` when provenance/state files are malformed or learnings writes fail during consolidation.

## Process Rules

Load `references/dream-operations.md` for process rules and `references/agent-history-source-policy.md` for source safety constraints.

## Handoff

After the consolidation pass:
- persist the updated learnings state
- record `last_dream_consolidated_at` in `.beads/learnings/dream-run-provenance.md`
- report what was merged, skipped, or proposed for promotion
- return control to `beo-router` (or the calling beo skill) after the consolidation report

## Context Budget

Follow `../reference/references/shared-hard-gates.md` § Context Budget Protocol. Skill-specific checkpoint items: current consolidation phase, which learnings files have been processed, and what candidates remain.

## Red Flags & Anti-Patterns

- Multiple plausible owners exist but you are about to merge anyway
- You are about to summarize or write material that still contains secrets, tokens, or user-identifying details
- A weak signal is being promoted just because a dream pass is already in progress
- The consolidation run is drifting into new planning or implementation work instead of learnings maintenance

See `references/consolidation-rubric.md`, `references/agent-history-source-policy.md`, and `references/pressure-scenarios.md` when classification or source safety is unclear.

## References

| File | Use for |
| --- | --- |
| `references/dream-operations.md` | Provenance checks, mode selection, source selection, classification flow, finalization |
| `references/consolidation-rubric.md` | Candidate matching criteria and outcome rules |
| `references/agent-history-source-policy.md` | Source priority, run windows, provenance persistence, redaction rules |
| `references/pressure-scenarios.md` | RED-phase failure cases and guardrail checks |
