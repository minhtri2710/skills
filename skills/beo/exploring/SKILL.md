---
name: beo-exploring
description: >-
  Use before any non-instant feature work, refactor, behavior change, or
  requirements-shaping conversation where user intent is not yet locked,
  especially when the user knows what they want but has not fully thought
  through edge cases, scope boundaries, or expected behavior.
---

# Beo Exploring

## Overview

Exploring is the decision-extraction phase. Before any research or planning, you must understand what the user actually wants, including the parts they haven't thought about yet.

**Core principle**: Every ambiguity resolved here saves 10x rework downstream.

The output is a `CONTEXT.md` file that becomes the single source of truth for all downstream skills (planning, validating, executing, reviewing).

## Key Terms

- **instant**: single-file or similarly tiny work, well-scoped, typically under 30 minutes, with no meaningful planning ambiguity
- **locked decision**: a behavioral choice the user has explicitly confirmed or accepted as a default
- **gray area**: a requirement that would materially change planning or execution if answered differently

## Default Exploring Loop

1. read any existing context and prior learnings
2. classify the scope and likely gray areas
3. ask one focused behavioral question at a time
4. lock decisions explicitly as they emerge
5. write `CONTEXT.md`
6. self-review for completeness, then hand off to planning

Use the reference docs when you need the exact learnings-read protocol or slug-safe update procedure; the default loop above should cover normal use.

## When NOT to Use

- Request is **instant** (single file, well-scoped, <30 min per router classification): router handles this directly, skip to executing
- Request is purely a bug fix with clear reproduction steps: use debugging workflow
- You're resuming mid-pipeline (router handles this)

## Phase 0: Read Existing Context

Before asking any questions, check what already exists:

```bash
# Check for existing CONTEXT.md
Read .beads/artifacts/<feature_slug>/CONTEXT.md

# Check the epic bead for existing description
br show <EPIC_ID> --json
```

Use `../reference/references/learnings-read-protocol.md` for the canonical prior-learnings read flow.

If CONTEXT.md already exists with locked decisions, skip to Phase 3 (verify, don't re-ask).

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

#### Example: Good vs Bad Exploring Question

**Bad:** "Should we use a queue or a cron job?"
Why bad: this asks the user to choose implementation rather than behavior.

**Good:** "If this job fails overnight, what should the user see the next morning?"
Why good: this locks behavior that planning can later implement in different ways.

For each gray area:
1. State what you currently understand
2. State the specific ambiguity
3. Ask a focused, answerable question
4. If the user says "I don't know" or "whatever you think", propose a concrete default and ask for confirmation

#### Default-Proposal Pattern

When the user does not want to decide directly:
1. state the uncertainty plainly
2. propose one concrete default
3. explain the consequence of that default in behavioral terms
4. ask for confirmation or correction

Example: "You do not seem to care about retry behavior here. I suggest one automatic retry and then a visible failure state so the user is not left guessing. Should I lock that?"

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

<HARD-GATE>
Never copy the user's request verbatim into `CONTEXT.md` or any other artifact.
The `## Request` section must be a sanitized paraphrase in your own words.
Redact or omit secrets, credentials, API keys, tokens, cookies, connection strings, private URLs, and long pasted payloads/logs.
If a sensitive literal matters for implementation, replace it with a stable placeholder such as `[REDACTED_API_KEY]` and note that sensitive material was removed.
</HARD-GATE>

### CONTEXT.md Structure

```markdown
# Feature: <feature-name>

## Request
<Sanitized summary of the user's request in your own words. Redact or omit secrets, credentials, tokens, cookies, connection strings, private URLs, and long pasted payloads/logs. If sensitive values matter, replace them with placeholders such as [REDACTED_API_KEY].>

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
mkdir -p .beads/artifacts/<feature_slug>
```

Write `CONTEXT.md` using your file writing tool.

### Slug Preservation

Load `../reference/references/slug-protocol.md` and follow the safe-update procedure exactly whenever updating the epic description.

Also update the epic bead description with a summary using the canonical slug-first shape.

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
- Feature: <epic-id> (<feature_slug>)
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

If context usage exceeds 65%, use `../reference/references/state-and-handoff-protocol.md` for the canonical base `HANDOFF.json` and `STATE.md` shapes, then add exploring-specific fields such as `decisions_locked` and `open_questions` before pausing.

## Red Flags & Anti-Patterns

See `references/exploring-guardrails.md` for the full red-flags and anti-patterns tables.
