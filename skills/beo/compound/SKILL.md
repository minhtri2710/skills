---
name: beo-compound
description: |
  Use after review accepts a feature to extract learnings from that single completed feature into durable knowledge. Identifies what worked, what failed, and unexpected discoveries; categorizes as feature-specific or generalizable; optionally proposes critical-pattern promotions requiring explicit user approval. MUST NOT run on incomplete or unaccepted features, consolidate across multiple features, or promote patterns without user approval. Do not use for cross-feature learnings consolidation (use beo-dream) or while the feature is still in progress or under review.
---

> **HARD-GATE: ONBOARDING** — Before any work, verify `br` and `bv` are accessible and `.beads/` is initialized (`beo-reference` → `references/shared-hard-gates.md`). If stale or missing, load `beo-onboard` and stop.

> **Protocol References**: Protocol rules reference the `beo-reference` skill via `→ references/<file>` for canonical documents.

# beo-compound

## Overview
Capture what a single completed feature taught the system and store it in the knowledge corpus. **Core principle: turn finished work into reusable knowledge without expanding scope beyond the one feature.**

## Boundary Rules
- **MUST NOT** perform independent state detection or free-form routing — owned by `beo-route`. May emit canonical handoff to the next allowed pipeline skill when exit conditions are met.
- **MUST NOT** gather requirements — owned by `beo-explore`.
- **MUST NOT** decompose work — owned by `beo-plan`.
- **MUST NOT** verify plans — owned by `beo-validate`.
- **MUST NOT** write code — owned by `beo-execute`.
- **MUST NOT** orchestrate workers — owned by `beo-swarm`.
- **MUST NOT** review implementations — owned by `beo-review`.
- **MUST NOT** consolidate cross-feature learnings — owned by `beo-dream`.
- **MUST NOT** diagnose failures — owned by `beo-debug`.

## Hard Gates
> **HARD-GATE: POST-REVIEW-ONLY** — Compound only runs after review accepts. If review has not accepted, compound does not start.

> **HARD-GATE: SINGLE-FEATURE-SCOPE** — Compound extracts learnings from exactly one feature. Writes only current feature learnings and approved critical-pattern appends. May read prior learnings for deduplication only, using the shared critical-patterns destination defined by `artifact conventions (`beo-reference` → `references/artifact-conventions.md`)`.

> **HARD-GATE: CRITICAL-PATTERN-APPROVAL** — Promoting a pattern to `critical-patterns.md` requires explicit user approval per `the beo approval gates` (`beo-reference` → `references/approval-gates.md`). Compound proposes; user decides.

## Communication Standard
> Follow the communication standard (`beo-reference` → `references/communication-standard.md`).

## Default Compound Loop
1. **Verify completion**: Confirm review accepted and the feature is eligible for post-review knowledge capture. Read review findings, bead history, and implementation artifacts from `.beads/artifacts/<feature_slug>/` using `artifact conventions (`beo-reference` → `references/artifact-conventions.md`)`.
2. **Extract learnings**: Identify what worked, what failed, unexpected discoveries, debugging insights, and performance observations from the completed feature.
3. **Categorize**: Group learnings by type such as technique, pitfall, tool-usage, architecture, and process.
4. **Generalize patterns**: Decide whether each learning is feature-specific or generalizable. Use `references/learnings-template.md` to normalize format before any promotion consideration.
5. **Promote critical patterns**: When a generalized pattern is recurring, high-impact, and actionable, propose promotion for user approval per `the beo approval gates` (`beo-reference` → `references/approval-gates.md`).
6. **Write artifacts**: Write `.beads/learnings/YYYYMMDD-<feature_slug>.md` and optionally update `.beads/critical-patterns.md` if approved. If the knowledge store is available, update it per `the knowledge store (`beo-reference` → `references/knowledge-store.md`)`.

### Reference Files
| File | Purpose |
|------|---------|
| `references/compounding-operations.md` | Operational sequence for extracting, categorizing, and writing feature learnings. |
| `references/learnings-template.md` | Canonical structure and formatting rules for feature learnings and generalized patterns. |

## Inputs and Outputs
- **Inputs** — Completed feature after review acceptance, review findings, implementation artifacts, bead history, and feature-scoped knowledge inputs resolved via `artifact conventions (`beo-reference` → `references/artifact-conventions.md`)`.
- **Outputs** — `.beads/learnings/YYYYMMDD-<feature_slug>.md`, optional `.beads/critical-patterns.md` updates when approved, and any state/handoff records required by the STATE.json/HANDOFF.json protocol (`beo-reference` → `references/state-and-handoff-protocol.md`).

## Decision Rubrics
- **Feature-Specific vs General** — If a learning depends on this feature’s exact tech stack, domain, or constraints, keep it feature-specific. If it applies across future features, generalize it.
- **Promote vs Keep Local** — Generalizable + recurring across 2 or more beads + high impact on quality or delivery → propose for promotion. Otherwise keep it in `feature-learnings.md` only.
- **Knowledge Store** — If Obsidian CLI is available, write or sync per `the knowledge store (`beo-reference` → `references/knowledge-store.md`)`. If it is unavailable, `feature-learnings.md` is sufficient.
- **Failure Recovery** — If artifact writing, approval flow, or knowledge updates fail, recover via `standard failure recovery (`beo-reference` → `references/failure-recovery.md`)`.

## Special Rules
- Compound is single-feature only; cross-feature synthesis belongs to `beo-dream`.
- Shared concerns, state transitions, and handoffs must reference canonical docs instead of being restated.
- State transitions must align with `the bead lifecycle states` (`beo-reference` → `references/status-mapping.md`).
- Approval ownership must follow `the beo approval gates` (`beo-reference` → `references/approval-gates.md`).
- Learnings should never be empty; if no meaningful learning exists, explicitly record that outcome and why.

## Handoff
> Write `STATE.json` for the normal adjacent-skill handoff with completion status, promoted learnings, and any deferred follow-up. Use `HANDOFF.json` only for emergency checkpoint or low-context resume scenarios.

## Context Budget
> If context exceeds 65% capacity, compress non-essential history before continuing (`beo-reference` → `references/shared-hard-gates.md`).

## Red Flags & Anti-Patterns
- Compound runs before review acceptance.
- Compound modifies another feature’s learnings.
- Compound promotes patterns without explicit user approval.
- Compound skips generalization and promotes raw feature-specific notes.
- Compound writes an empty or content-free learnings artifact.
- Compound duplicates shared-reference rules instead of citing canonical documents.
