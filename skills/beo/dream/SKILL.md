---
name: beo-dream
description: >-
  Use when beo learnings need a manual consolidation pass across multiple
  completed features, especially when learnings have gone stale, repeated
  patterns are accumulating, or the user asks to consolidate, clean up, merge,
  or promote existing learnings. Use for prompts like "run dream",
  "consolidate learnings", "merge repeated learnings", or "do a learnings pass".
---

# Beo Dream

## Overview

Load `beo-reference` for knowledge-store protocol (`../reference/references/knowledge-store.md`).

Dream performs one manual consolidation pass across accumulated learnings.
It updates durable learnings in place, keeps the write surface narrow, and promotes only the patterns that still deserve long-term attention.

**Core principle:** consolidate carefully; do not confuse repeated mention with durable signal.

## Hard Gates

<HARD-GATE>
If ownership is ambiguous, ask the user instead of silently choosing a merge target.
</HARD-GATE>

<HARD-GATE>
Do not edit `critical-patterns.md` without explicit approval.
</HARD-GATE>

<HARD-GATE>
Secret/PII redaction is mandatory before summary output and before writing to `.beads/learnings/*.md`.
</HARD-GATE>

The durable write surface is `.beads/learnings/*.md`.
Dream may propose critical promotions, but it must never edit `.beads/critical-patterns.md` without explicit user approval.

## Use Dream vs Compounding

Use `beo-compounding` after one completed feature.
Use `beo-dream` when consolidating, deduplicating, or promoting learnings across multiple completed features over time.
When in doubt: compounding is per-feature, dream is cross-feature.

## Default Dream Loop

1. orient on provenance and choose bootstrap vs recurring mode
2. select the right source window
3. extract and classify candidate learnings
4. apply outcomes: merge, create, skip, or ask the user when ownership is ambiguous
5. finalize the run and update provenance

Load `references/dream-operations.md` for the exact provenance checks, source selection, candidate classification mechanics, apply-outcome behavior, and finalization steps.

## Process Rules

Load `references/dream-operations.md` for process rules and `references/codex-source-policy.md` for source safety constraints.

## Context Budget

If context usage exceeds 65%, use `../reference/references/state-and-handoff-protocol.md` for the canonical `HANDOFF.json` and `STATE.md` shapes, then include the current consolidation phase, which learnings files have been processed, and what candidates remain.

## Red Flags

- Multiple plausible owners exist but you are about to merge anyway
- You are about to summarize or write material that still contains secrets, tokens, or user-identifying details
- A weak signal is being promoted just because a dream pass is already in progress
- The consolidation run is drifting into new planning or implementation work instead of learnings maintenance

See `references/consolidation-rubric.md`, `references/codex-source-policy.md`, and `references/pressure-scenarios.md` when classification or source safety is unclear.

## Handoff

After the consolidation pass:
- persist the updated learnings state
- record `last_dream_consolidated_at` in `dream-run-provenance.md`
- report what was merged, skipped, or proposed for promotion

## References

- `references/dream-operations.md`
- `references/consolidation-rubric.md`
- `references/codex-source-policy.md`
- `references/pressure-scenarios.md`
