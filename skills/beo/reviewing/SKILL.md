---
name: beo/reviewing
description: Use after all tasks complete. Runs specialist review subagents, verifies artifacts, conducts human UAT, closes the epic, and captures learnings. The quality gate before feature completion.
---

# Warcraft Reviewing

## Overview

Reviewing is the post-execution quality gate. It verifies that the implementation actually delivers what CONTEXT.md specified, catches issues the workers missed, and formally closes the feature.

**Core principle**: Trust but verify. Workers may have drifted, cut corners, or missed edge cases.

## When to Use

- After `beo/executing` completes (all tasks closed)
- Router detected state = **ready-to-review**
- User says "review", "verify", "check the work"

## Prerequisites

```bash
# All tasks under the epic should be closed
br list --type task --json | jq '[.[] | select((.id | startswith("<EPIC_ID>.")) and .status != "closed")]'
# Should return empty array (or only deferred/cancelled tasks)

# CONTEXT.md exists
cat .beads/artifacts/<feature-name>/CONTEXT.md

# Build passes
# (Run project-specific build command)

# Tests pass
# (Run project-specific test command)
```

<HARD-GATE>
If tasks are still open or in progress, STOP. Route back to `beo/executing`.
</HARD-GATE>

## Phase 1: Automated Review

Launch specialist review subagents to examine the implementation from different angles.

### 5 Review Specialists

| # | Specialist | Focus | Key Questions |
|---|-----------|-------|---------------|
| 1 | **Code Quality** | Clean code, patterns, naming, complexity | Does the code follow project conventions? Any dead code? Unnecessary complexity? |
| 2 | **Architecture** | Module boundaries, coupling, separation of concerns | Does the implementation respect existing architecture? Any new coupling introduced? |
| 3 | **Security** | Input validation, auth, injection, data exposure | Any security vulnerabilities? Unsanitized inputs? Exposed secrets? |
| 4 | **Test Coverage** | Tests exist, meaningful assertions, edge cases | Are the verification criteria actually tested? Any missing edge cases? |
| 5 | **Learnings Synthesis** | Cross-cutting patterns, institutional memory | What patterns emerged? What should be remembered for future work? |

### Dispatch Strategy

- **4 or fewer specialists needed**: Launch all in parallel via `task()` calls
- **All 5**: Launch first 4 in parallel, then learnings synthesizer last (it cross-references the other findings)

### Specialist Prompt Template

Each specialist receives:
```markdown
# Review: <specialist-type> for <feature-name>

## Your Role
You are reviewing the implementation of "<feature-name>" from a <specialist-type> perspective.

## Scope
Review ONLY the changes made for this feature. Do NOT review pre-existing code unless it was modified.

## Files Changed
<list of files modified by all tasks — gathered from task reports>

## CONTEXT.md Decisions
<relevant decisions that should be reflected in the implementation>

## Instructions
1. Read each changed file
2. Evaluate against your specialist criteria
3. Report findings with severity:
   - P1 (BLOCKS MERGE): Must fix before the feature can ship
   - P2 (SHOULD FIX): Important but can be a follow-up task
   - P3 (NICE TO HAVE): Minor improvements, style nits

## Output Format
For each finding:
- File: <path>
- Line: <number or range>
- Severity: P1 | P2 | P3
- Finding: <description>
- Suggestion: <how to fix>
```

### Processing Review Results

Collect all findings from all specialists. Categorize:

| Severity | Action |
|----------|--------|
| **P1** (blocks merge) | Create a fix task bead, wire to epic, execute immediately |
| **P2** (should fix) | Create a follow-up bead NOT under the current epic |
| **P3** (nice to have) | Record but do not create beads unless user requests |

### Creating P1 Fix Beads

```bash
# P1 finding becomes a blocking task
br create "Fix: <P1 finding summary>" -t task --parent <EPIC_ID> -p 1 --json
br update <FIX_TASK_ID> --description "<finding details + fix suggestion>"

# Execute the fix immediately
# Route back to Phase 2 of beo/executing for this task
```

After all P1 fixes are resolved, return to reviewing.

### Creating P2/P3 Follow-Up Beads

```bash
# P2 findings become independent follow-up beads (NOT under the epic)
br create "Follow-up: <P2 finding summary>" -t task -p 3 --json
br label add <FOLLOWUP_ID> -l review
br label add <FOLLOWUP_ID> -l review-p2
br update <FOLLOWUP_ID> --description "External ref: <EPIC_ID>\n\n<finding details>"
```

P2/P3 beads are intentionally NOT children of the current epic so they don't block feature completion.

## Phase 2: Artifact Verification

Verify that all implementation artifacts are real, substantive, and wired.

### 3-Level Verification

For each significant artifact (component, module, endpoint, etc.) promised by the plan:

| Level | Check | FAIL if... |
|-------|-------|------------|
| **L1: EXISTS** | File/component exists at the expected path | File is missing |
| **L2: SUBSTANTIVE** | Not a stub, placeholder, or TODO | Contains `return null`, `TODO`, empty handlers, `throw new Error('not implemented')` |
| **L3: WIRED** | Imported and used by integration code | Component exists but is never imported, endpoint exists but is not registered |

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
4. If major (architectural change) → STOP reviewing, route to `beo/planning`

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

### Step 3: Capture Learnings

If the learnings synthesizer (Specialist #5) produced findings:

```bash
mkdir -p .beo
```

Write learnings to `.beo/learnings/<date>-<feature-slug>.md`:

```markdown
# Learnings: <feature-name>

## Date
<ISO date>

## Patterns Discovered
- <pattern 1>
- <pattern 2>

## Decisions That Worked Well
- <decision and why>

## Things That Went Wrong
- <issue and root cause>

## Recommendations for Future Work
- <recommendation>
```

If any learnings are critical (would cause significant waste if forgotten), promote to `.beo/critical-patterns.md`:

```markdown
## <Pattern Name>
- **Domain**: <affected area>
- **Pattern**: <what to do>
- **Rationale**: <why>
- **Discovered**: <date>, <feature-name>
```

<HARD-GATE>
Promotion to critical-patterns.md requires user approval. Ask before writing.
</HARD-GATE>

### Step 4: AGENTS.md Sync (Optional)

If the feature introduced new patterns, tools, or conventions that should be in the project's AGENTS.md:

1. Read the current AGENTS.md
2. Propose additions based on the new feature
3. Ask user for approval
4. Write the updates

### Step 5: Clean Up State

```bash
rm -f .beo/HANDOFF.json
rm -f .beo/STATE.md
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
<Learnings captured / no learnings>
```

## Lightweight Mode

For instant/tiny features (1-2 tasks, LOW risk):

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
     "skill": "beo/reviewing",
     "feature": "<epic-id>",
     "next_action": "Resume from Phase <N>. Specialists complete, UAT at D<N>.",
     "beads_in_flight": ["<fix-task-ids-if-any>"],
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
