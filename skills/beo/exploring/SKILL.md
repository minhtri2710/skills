---
name: beo-exploring
description: Use before any feature work, refactor, or behavior modification. Extracts locked decisions from the user through Socratic dialogue before research or planning begins. Output is CONTEXT.md.
---

# Beo Exploring

## Overview

Exploring is the decision-extraction phase. Before any research or planning, you must understand what the user actually wants, including the parts they haven't thought about yet.

**Core principle**: Every ambiguity resolved here saves 10x rework downstream.

The output is a `CONTEXT.md` file that becomes the single source of truth for all downstream skills (planning, validating, executing, reviewing).

## When NOT to Use

- Request is **instant** (single file, well-scoped, <30 min per router classification): router handles this directly, skip to executing
- Request is purely a bug fix with clear reproduction steps: use debugging workflow
- You're resuming mid-pipeline (router handles this)

## Phase 0: Read Existing Context

Before asking any questions, check what already exists:

```bash
# Check for existing CONTEXT.md
cat .beads/artifacts/<feature-name>/CONTEXT.md 2>/dev/null

# Check for any prior learnings
cat .beads/critical-patterns.md 2>/dev/null

# Check the epic bead for existing description
br show <EPIC_ID> --json
```

If CONTEXT.md already exists with locked decisions, skip to Phase 3 (verify, don't re-ask).

If `critical-patterns.md` exists, scan it for patterns relevant to this feature's domain. Mention any relevant patterns to the user.

## Phase 1: Scope Assessment

Classify the request before diving into questions.

| Signal | Classification | Depth |
|--------|---------------|-------|
| Trivial rename, config change | **Quick** | Skip to Phase 3, 1-2 questions max |
| Clear feature with known boundaries | **Standard** | Full Phase 2, 3-5 questions |
| Ambiguous, multi-system, architectural | **Deep** | Full Phase 2, 5-8 questions + gray areas |

## Phase 2: Decision Extraction

### Step 1: Domain Classification

Classify the feature into one or more domains:

| Domain | Signal | Key Questions |
|--------|--------|---------------|
| **SEE** (UI/Visual) | User mentions display, page, component | What does the user see? What triggers it? |
| **CALL** (API/Integration) | External services, endpoints, protocols | What's the contract? Auth? Error handling? |
| **RUN** (Processing/Logic) | Algorithms, transformations, business rules | What are the inputs/outputs? Edge cases? |
| **READ** (Data/Storage) | Database, files, caching | What's the schema? Migration needed? |
| **ORGANIZE** (Refactor/Structure) | Code organization, patterns, architecture | What's the target structure? What moves? |

### Step 2: Identify Gray Areas

For each domain, identify 2-4 areas where the user probably hasn't thought through the details. These are your exploration targets.

Common gray areas:
- Error handling behavior (what happens when X fails?)
- Edge cases (empty state, max limits, concurrent access)
- Migration path (existing data, backward compatibility)
- Performance requirements (latency, throughput, caching)
- Security implications (auth, validation, sanitization)

### Step 3: Socratic Exploration

<HARD-GATE>
Ask ONE question at a time. Wait for the user's answer before asking the next question.
Do NOT batch multiple questions in a single message.
</HARD-GATE>

For each gray area:
1. State what you currently understand
2. State the specific ambiguity
3. Ask a focused, answerable question
4. If the user says "I don't know" or "whatever you think", propose a concrete default and ask for confirmation

**Question quality checklist** (apply to every question before asking):
- Is this answerable in 1-2 sentences?
- Does this affect implementation decisions?
- Am I asking about BEHAVIOR, not IMPLEMENTATION? (users decide what, not how)
- Have I already asked this or can I infer it?

### Step 4: Lock Decisions

As the user answers, assign stable IDs to each decision:

```
D1: Authentication uses JWT tokens with 1-hour expiry
D2: Error responses follow RFC 7807 Problem Details format
D3: Database migration runs as a separate step, not on startup
D4: Rate limiting is 100 req/min per API key
```

Confirm each decision explicitly: "Locking D3: Database migration runs as a separate step. Correct?"

### Completion Criteria

Stop asking questions when ALL of these are true:
- [ ] Every identified gray area has a locked decision or explicit "out of scope"
- [ ] You could explain the feature to another developer and they could start planning
- [ ] No remaining questions would change the high-level approach

<HARD-GATE>
If you cannot check all three boxes, keep asking. Do not proceed to Phase 3.
</HARD-GATE>

## Phase 3: Context Assembly

Write the CONTEXT.md file with all locked decisions.

### CONTEXT.md Structure

```markdown
# Feature: <feature-name>

## Request
<Original user request, quoted verbatim>

## Scope Classification
- Complexity: <quick/standard/deep>
- Domains: <SEE, CALL, RUN, READ, ORGANIZE>
- Estimated blast radius: <number of files/modules affected>

## Locked Decisions

### D1: <decision title>
<Full decision description>
- Rationale: <why this choice>
- Alternatives considered: <what was rejected and why>

### D2: <decision title>
...

## Out of Scope
- <Thing explicitly excluded and why>

## Open Questions (for planning)
- <Questions that need research, not user input>

## Relevant Patterns
- <Patterns from critical-patterns.md that apply>
```

### Write the File

```bash
# Create the artifacts directory
mkdir -p .beads/artifacts/<feature-name>

# Write CONTEXT.md (use your file editing tools)
```

### Slug Preservation

When updating the epic description, always preserve the immutable `slug:` line:

1. Read the current epic description: `br show <EPIC_ID> --json`
2. Extract the first line (should be `slug: <feature_slug>`)
3. Prepend the slug line to the new description content
4. Write via `br update <EPIC_ID> --description "slug: <feature_slug>\n<rest of description>"`

<HARD-GATE>
Never overwrite an epic description without checking for and preserving the `slug:` first line. If the slug line is missing and the epic already has tasks, STOP; the slug was lost. Check `.beads/artifacts/` for the correct feature directory name and restore the slug.
</HARD-GATE>

Also update the epic bead description with a summary:

```bash
br update <EPIC_ID> --description "slug: <feature_slug>\nFeature: <name>\n\nScope: <summary>\nDecisions: <count> locked\nDomains: <list>"
```

## Phase 4: Self-Review

Before handing off, verify the CONTEXT.md quality:

**Completeness check**: for each locked decision, ask:
1. Would a developer reading only this file understand the decision?
2. Is the rationale clear enough to prevent someone from re-opening the discussion?
3. Are there implicit assumptions that should be explicit?

**90% confidence test**: "Could a competent developer plan this feature using only CONTEXT.md?"
- If yes → proceed to handoff
- If no → identify what's missing and go back to Phase 2

## Phase 5: Handoff

### Update State

Write `.beads/STATE.md`:
```markdown
# Beo State
- Phase: exploring → complete
- Feature: <epic-id> (<feature-name>)
- Tasks: 0 (exploring does not create tasks)
- Next: beo-planning

Decisions: <count> locked
```

### Announce

Report to user:
```
Exploring complete.
- <N> decisions locked (D1-D<N>)
- <M> items marked out of scope
- <K> open questions for planning phase

Ready to plan. Load beo-planning to begin research and decomposition.
```

## Context Budget

If context usage exceeds 65%, write HANDOFF.json before pausing:

```bash
Write `.beads/HANDOFF.json`:
```

```json
{
  "schema_version": 1,
  "phase": "exploring",
  "skill": "beo-exploring",
  "feature": "<epic-id>",
  "feature_name": "<feature-name>",
  "next_action": "Continue decision extraction from D<N+1>",
  "in_flight_beads": [],
  "decisions_locked": ["D1", "D2", "..."],
  "open_questions": ["..."],
  "timestamp": "<iso8601>"
}
```

## Red Flags

| Flag | Description |
|------|-------------|
| **Asking implementation questions** | "Should we use a Map or an Object?" is planning, not exploring |
| **Batching 3+ questions** | One question at a time. Period. |
| **Accepting "I don't care"** | Propose a concrete default instead |
| **Skipping gray areas** | Every feature has at least 2 gray areas |
| **Writing CONTEXT.md before decisions are locked** | Decisions first, document second |
| **Spending >15 min on one question** | If it's that complex, lock what you can and mark the rest as an open question for planning |

## Anti-Patterns

| Pattern | Why It's Wrong | Instead |
|---------|---------------|---------|
| Starting to plan during exploring | Premature commitment | Lock decisions only; planning comes next |
| Asking about tech stack choices | That's a planning decision | Ask about behavior and requirements |
| Copying the user's words verbatim as decisions | Users speak loosely | Restate precisely and confirm |
| Creating tasks during exploring | No tasks until planning | Only the epic bead should exist |
| Skipping exploring for non-instant features | Even "simple" features (lightweight and above) still have gray areas | At minimum, do a Quick-depth pass. Only **instant** requests (single file, <30 min) skip exploring. |
