---
name: beo-reviewing
description: >-
  Use after the final approved execution scope is complete, or when the user asks
  whether a feature is done, ready to ship, safe to merge, or needs a quality
  check. Runs the post-execution quality gate: specialist review, artifact
  verification, and human UAT against locked decisions and the final exit state.
  Use for prompts like "review this feature", "is this done?", "can we ship
  this?", "double-check the implementation", or "run UAT".
---

# Beo Reviewing

## Overview

Reviewing is the post-execution quality gate. It verifies that the implementation actually delivers what `CONTEXT.md` specified, catches issues the workers missed, and formally closes the feature.

**Core principle**: Trust but verify. Workers may have drifted, cut corners, or missed edge cases.

Reviewing is for the **final execution scope**. If planning mode is `multi-phase` and later phases remain, route back to planning rather than reviewing the feature as if it were complete.

## Prerequisites

Load `references/reviewing-operations.md` for the exact prerequisite checks, isolated review inputs, and finishing prerequisites.

<HARD-GATE>
If tasks from the final execution scope are still open or in progress, STOP. Route back to `beo-executing`.
If any tasks have `blocked`, `failed`, or `partial` labels (status `deferred`), STOP. Report these to the user and get explicit approval to proceed, defer, or re-plan before closing the epic.
If `planning_mode = multi-phase` and later phases remain, STOP. Route back to `beo-planning` instead of reviewing the feature as complete.
</HARD-GATE>

## Phase 1: Automated Review

Launch specialist review subagents to examine the implementation from different angles.

Load `references/review-specialist-prompts.md` for the full specialist table, prompt template, dispatch strategy, and P1/P2/P3 bead creation patterns.

**Summary**: 5 specialists (Code Quality, Architecture, Security, Test Coverage, Learnings Synthesis) review changed files. Launch first 4 in parallel, learnings synthesizer last. Each reports findings as P1 (blocks merge), P2 (should fix), or P3 (nice to have).

- **P1 findings** become fix beads under the epic, executed immediately, using the shared **Reactive Fix Bead Template**
- **P2 findings** become independent follow-up beads (NOT under epic), using the shared **Follow-Up Bead Template**
- **P3 findings** recorded but no beads unless user requests
- If P1 fixes fail >2 attempts, route to `beo-debugging`

Use isolated review context whenever possible: changed files / diff, `CONTEXT.md`, `approach.md`, and final current-phase artifacts.

### Severity Examples

- **P1**: security hole, broken acceptance path, data-loss risk, or a locked decision from `CONTEXT.md` is not actually met
- **P2**: maintainability problem, weak edge-case handling, incomplete tests, or a risky design choice that should be corrected soon
- **P3**: polish, naming, cleanup, readability, or a non-blocking improvement suggestion

When unsure between P1 and P2, ask: "Would I block merge if this remained unfixed?" If yes, it is P1.

## Phase 2: Artifact Verification

Verify that all implementation artifacts promised by the final execution scope are real, substantive, and wired.

Load `references/reviewing-operations.md` for the 3-level verification procedure, command shapes, and finishing flow.

## Phase 3: Human UAT

<HARD-GATE>
Human review is required. Use the canonical rule from `../reference/references/approval-gates.md` and walk through the feature with the user.
</HARD-GATE>

### UAT Protocol

For each locked decision from `CONTEXT.md` (D1, D2, ...):

1. State the decision
2. Show how the implementation fulfills it
3. Ask: "Does this match your intent?"

Walk through ONE decision at a time. Wait for user confirmation before moving to the next.

Additionally, verify against the relevant exit state from `phase-contract.md`:

For each exit-state line:
1. State the exit-state claim
2. Show how the implementation satisfies it
3. Ask: "Is this exit state now true?"

### UAT Outcomes

Load `references/reviewing-operations.md` for the canonical UAT outcome handling.

### Scope Change During UAT

If the user changes a decision:
1. Update `CONTEXT.md` with the new decision
2. Assess which tasks are affected
3. If minor (1-2 files) → create fix bead, execute
4. If major (architectural change or changes to feature sequencing) → STOP reviewing, strip `approved` label (`br label remove <EPIC_ID> -l approved`), route to `beo-planning`

## Phase 4: Finishing

After all P1 issues are resolved, artifacts are verified, and UAT is complete, load `references/reviewing-operations.md` for the exact finishing sequence, review-findings handoff, merge-path presentation, optional AGENTS.md sync, and cleanup rule.

## Completion

Announce:
```text
Feature "<feature-name>" is complete.

Review Summary:
- Specialist reviews: <N> findings (<P1 count> P1, <P2 count> P2, <P3 count> P3)
- P1 fixes: <N> resolved
- P2 follow-ups: <N> beads created
- Artifact verification: <N>/<total> L3 verified
- UAT: <N>/<total> decisions confirmed

Epic <EPIC_ID> is closed.
Review findings saved for compounding.

Next: Load beo-compounding to capture learnings and promote critical patterns.
```

## Lightweight Mode

Load `references/reviewing-operations.md` for the lightweight-review shortcut.

## Context Budget

If context usage exceeds 65%, use `references/reviewing-operations.md` together with `../reference/references/state-and-handoff-protocol.md` for the canonical checkpoint behavior.

## Red Flags

| Flag | Description |
|------|-------------|
| **Skipping specialist reviews** | "The code looks fine" is not a review |
| **Auto-passing UAT** | User must confirm each decision |
| **Ignoring P1 findings** | P1 blocks merge; no exceptions |
| **Closing epic with open P1 fixes** | All P1 beads must be closed first |
| **Promoting learnings without approval** | critical-patterns.md is shared; ask first |
| **Skipping build/test/lint** | Full build/test/lint verification is mandatory before closing the epic |
| **Reviewing before later phases are planned/executed** | Multi-phase feature is not done just because the current phase is done |

## Anti-Patterns

| Pattern | Why It's Wrong | Instead |
|---------|---------------|---------|
| Reviewing your own code (same agent that implemented) | Blind spots | Use fresh subagents with isolated context |
| Creating P1 beads under a different epic | Breaks the dependency chain | P1 beads go under the current epic |
| Creating P2/P3 beads under the current epic | Blocks feature completion | P2/P3 are independent follow-up beads |
| Closing the epic before UAT | User hasn't confirmed | Always complete Phase 3 first |
| Skipping learnings capture | Wastes institutional memory | At minimum, run the learnings synthesizer |
| Writing novel code during review | That's execution, not review | Create beads for any needed changes |
