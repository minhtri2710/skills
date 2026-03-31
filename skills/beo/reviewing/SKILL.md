---
name: beo-reviewing
description: >-
  Use after all tasks complete. Runs specialist review subagents, verifies
  artifacts, conducts human UAT, closes the epic, and hands off to
  beo-compounding for learnings. The quality gate before feature completion.
  Trigger phrases: review the feature, verify the work, run UAT, quality check,
  check the implementation.
---

# Beo Reviewing

## Overview

Reviewing is the post-execution quality gate. It verifies that the implementation actually delivers what CONTEXT.md specified, catches issues the workers missed, and formally closes the feature.

**Core principle**: Trust but verify. Workers may have drifted, cut corners, or missed edge cases.

## Prerequisites

```bash
# All tasks under the epic should be closed (canonical enumeration — see pipeline-contracts.md)
br dep list <EPIC_ID> --direction up --type parent-child --json
# Filter for .status != "closed" — should return empty (or only deferred/cancelled tasks)

# CONTEXT.md exists
cat .beads/artifacts/<feature-name>/CONTEXT.md

# phase-contract.md exists (needed for exit-state verification in UAT)
cat .beads/artifacts/<feature-name>/phase-contract.md

# story-map.md exists (needed for story completeness verification)
cat .beads/artifacts/<feature-name>/story-map.md 2>/dev/null

# Build passes
# (Run project-specific build command)

# Tests pass
# (Run project-specific test command)
```

<HARD-GATE>
If tasks are still open or in progress, STOP. Route back to `beo-executing`.
If any tasks have `blocked`, `failed`, or `partial` labels (status `deferred`), STOP. Report these to the user and get explicit approval to proceed, defer, or re-plan before closing the epic.
</HARD-GATE>

## Phase 1: Automated Review

Launch specialist review subagents to examine the implementation from different angles.

Load `references/review-specialist-prompts.md` for the full specialist table, prompt template, dispatch strategy, and P1/P2/P3 bead creation patterns.

**Summary**: 5 specialists (Code Quality, Architecture, Security, Test Coverage, Learnings Synthesis) review changed files. Launch first 4 in parallel, learnings synthesizer last. Each reports findings as P1 (blocks merge), P2 (should fix), or P3 (nice to have).

- **P1 findings** become fix beads under the epic, executed immediately
- **P2 findings** become independent follow-up beads (NOT under epic)
- **P3 findings** recorded but no beads unless user requests
- If P1 fixes fail >2 attempts, route to `beo-debugging`

## Phase 2: Artifact Verification

Verify that all implementation artifacts are real, substantive, and wired.

### 3-Level Verification

For each significant artifact (component, module, endpoint, etc.) promised by the plan:

| Level | Check | FAIL if... |
|-------|-------|------------|
| **L1: EXISTS** | File/component exists at the expected path | File is missing |
| **L2: SUBSTANTIVE** | Not a stub, placeholder, or TODO | Contains `return null`, `TODO`, empty handlers, `throw new Error('not implemented')` |
| **L3: WIRED** | Imported and used by integration code | Component exists but is never imported, endpoint exists but is not registered |

Additionally, check each exit-state line from `phase-contract.md`:
- Is the exit state actually achieved by the implementation?
- Can the demo story from phase-contract.md be walked through successfully?

```bash
# L1: Check file exists
ls <expected-file-path>

# L2: Check for stubs (search for common placeholder patterns)
# Use grep or code search for: TODO, FIXME, return null, not implemented

# L3: Check for usage (search for imports of the new module)
# Use grep or code search for the module's export names
```

### Verification Summary

```
Artifact Verification:
  <component-1>: L1 ✓  L2 ✓  L3 ✓
  <component-2>: L1 ✓  L2 ✓  L3 ✗ (not imported in router)
  <component-3>: L1 ✓  L2 ✗ (contains TODO stub)
```

L2 or L3 failures are P1 findings — create fix beads and resolve before proceeding.

## Phase 3: Human UAT

<HARD-GATE>
Human review is required. Walk through the feature with the user.
</HARD-GATE>

### UAT Protocol

For each locked decision from CONTEXT.md (D1, D2, ...):

1. State the decision
2. Show how the implementation fulfills it
3. Ask: "Does this match your intent?"

Walk through ONE decision at a time. Wait for user confirmation before moving to the next.

Additionally, verify against the phase exit state from `phase-contract.md`:

For each exit-state line:
1. State the exit-state claim
2. Show how the implementation satisfies it
3. Ask: "Is this exit state now true?"

### UAT Outcomes

| User Says | Action |
|-----------|--------|
| "Yes, looks good" | Mark decision as verified, continue |
| "No, this isn't right" | Create P1 fix bead, route to executing |
| "Close enough, fix later" | Create P2 follow-up bead, continue |
| "I changed my mind about this" | Update CONTEXT.md, assess impact on implementation |

### Scope Change During UAT

If the user changes a decision:
1. Update CONTEXT.md with the new decision
2. Assess which tasks are affected
3. If minor (1-2 files) → create fix bead, execute
4. If major (architectural change) → STOP reviewing, strip `approved` label (`br label remove <EPIC_ID> -l approved`), route to `beo-planning`

## Phase 4: Finishing

After all P1 issues are resolved, artifacts are verified, and UAT is complete.

### Step 1: Final Build/Test/Lint

```bash
# Run full build
# Run full test suite
# Run linter
```

All must pass before proceeding.

### Step 2: Close the Epic

```bash
# Close the epic bead
br close <EPIC_ID>
br comments add <EPIC_ID> --no-daemon --message "Feature complete. All tasks closed. UAT passed."

# Flush
br sync --flush-only
```

### Step 3: Hand Off to Compounding

The learnings synthesizer (Specialist #5) findings are input for `beo-compounding`.
Do NOT write learnings directly -- the compounding skill handles synthesis, deduplication,
and critical-pattern promotion with proper knowledge store integration.

Save the synthesizer's raw findings for compounding to consume:

```bash
mkdir -p .beads
```

Write `.beads/review-findings.md` with the raw learnings synthesizer output.

Note: `beo-compounding` will be invoked after reviewing completes.

### Step 4: AGENTS.md Sync (Optional)

If the feature introduced new patterns, tools, or conventions that should be in the project's AGENTS.md:

1. Read the current AGENTS.md
2. Propose additions based on the new feature
3. Ask user for approval
4. Write the updates

### Step 5: Clean Up State

```bash
rm -f .beads/HANDOFF.json
# Do NOT delete .beads/STATE.md -- beo-compounding needs it
```

## Completion

Announce:
```
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

For features meeting ALL of these criteria:
- ≤2 tasks, all LOW risk
- No external dependencies
- No schema changes
- No auth/security impact

1. Skip Phase 1 specialist subagents — do a quick manual review instead
2. Skip Phase 2 formal artifact verification — check the obvious stuff
3. Phase 3 UAT: Quick confirmation ("Does this look right?")
4. Phase 4: Build/test/lint + close epic

Should take <5 minutes.

## Context Budget

If context usage exceeds 65%:

1. Save review findings gathered so far
2. Save UAT progress
3. Write HANDOFF.json:
   ```json
   {
     "schema_version": 1,
     "phase": "reviewing",
     "skill": "beo-reviewing",
     "feature": "<epic-id>",
     "feature_name": "<feature-name>",
     "next_action": "Resume from Phase <N>. Specialists complete, UAT at D<N>.",
     "in_flight_beads": ["<fix-task-ids-if-any>"],
     "timestamp": "<iso8601>"
   }
   ```
4. Pause

## Red Flags

| Flag | Description |
|------|-------------|
| **Skipping specialist reviews** | "The code looks fine" is not a review |
| **Auto-passing UAT** | User must confirm each decision |
| **Ignoring P1 findings** | P1 blocks merge — no exceptions |
| **Closing epic with open P1 fixes** | All P1 beads must be closed first |
| **Promoting learnings without approval** | critical-patterns.md is shared — ask first |
| **Skipping build/test/lint** | Phase 4 Step 1 is mandatory |

## Anti-Patterns

| Pattern | Why It's Wrong | Instead |
|---------|---------------|---------|
| Reviewing your own code (same agent that implemented) | Blind spots | Use fresh subagents with isolated context |
| Creating P1 beads under a different epic | Breaks the dependency chain | P1 beads go under the current epic |
| Creating P2/P3 beads under the current epic | Blocks feature completion | P2/P3 are independent follow-up beads |
| Closing the epic before UAT | User hasn't confirmed | Always complete Phase 3 first |
| Skipping learnings capture | Wastes institutional memory | At minimum, run the learnings synthesizer |
| Writing novel code during review | That's execution, not review | Create beads for any needed changes |
