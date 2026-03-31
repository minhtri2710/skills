---
name: beo-compounding
description: >-
  Capture learnings from completed feature work to make future work easier.
  Invoke after reviewing completes and the feature is merged. Runs three parallel
  analysis subagents (patterns/decisions/failures), synthesizes into
  .beads/learnings/YYYYMMDD-slug.md, promotes critical items to
  critical-patterns.md. Trigger phrases: what did we learn, capture learnings,
  compound, lessons learned, document what we found.
  Key output: critical-patterns.md is read by every planning and exploring
  Phase 0 -- this is the flywheel that makes the ecosystem smarter over time.
---

# Compounding Skill

Load `beo-reference` for knowledge-store protocol (`references/knowledge-store.md`).

---

## Process

Complete these phases in order. The three-agent analysis (Phase 2) runs in parallel.

---

### Phase 1: Gather Context

Collect all artifacts from the completed feature. Read:

```
.beads/artifacts/<feature-name>/CONTEXT.md      <- locked decisions (what we committed to)
.beads/artifacts/<feature-name>/discovery.md   <- research findings (what we learned before coding)
.beads/artifacts/<feature-name>/plan.md        <- high-level approach summary (compatibility artifact)
.beads/artifacts/<feature-name>/phase-contract.md <- phase definition (entry/exit state, demo, scope)
.beads/artifacts/<feature-name>/story-map.md     <- story structure (sequence, closure, bead mapping)
.beads/review-findings.md                      <- P1/P2/P3 findings from beo-reviewing
.beads/artifacts/<feature-name>/debug-notes.md <- failure patterns from beo-debugging (if any)
.beads/STATE.md or HANDOFF artifacts           <- runtime coordination state, if retained
.beads/ or `br show` output                    <- the executable work graph we actually ran
```

All paths above are checked; missing files are silently skipped. Compounding works with partial context.

Run this git command to get the feature's commit history:

```bash
git log --oneline main..feature/<feature-name>  # commits in feature branch not yet in main
# If already merged, use: git log --oneline --merges --grep="<feature-name>" main
```

Build an internal summary: what was built, what risks were flagged, what surprises emerged.

**If no history files exist:** fall back to reading the conversation/session summary and
recent git diff. Compounding is still valuable even with partial context.

---

### Phase 2: Three-Category Analysis (3 Parallel Subagents)

Launch three subagents simultaneously using the canonical `Subagent(...)` contract. Each writes findings to a staging file under `.beads/artifacts/<feature-name>/`.
Do NOT have subagents write the final learnings file; only the orchestrator writes that.

---

#### Agent 1: Pattern Extractor

**Task for Agent 1:**

```
Read the feature artifacts provided. Identify all REUSABLE PATTERNS that emerged:

- Code patterns: new functions, utilities, abstractions worth standardizing
- Architecture patterns: structural decisions that worked and should be repeated
- Process patterns: workflow approaches that saved time or prevented errors
- Integration patterns: how this feature connected to other systems

For each pattern:
1. Name it concisely
2. Describe what it does and why it's valuable
3. Note the specific file/location where it was first used (if applicable)
4. State "applicable-when": under what conditions should future agents use this?

Write findings to: .beads/artifacts/<feature-name>/compounding-patterns.md
```

---

#### Agent 2: Decision Analyst

**Task for Agent 2:**

```
Read the feature artifacts provided. Identify all significant DECISIONS made during this work:

- Good calls: decisions that proved correct, saved time, or prevented problems
- Bad calls: decisions that were wrong, required rework, or added unnecessary complexity
- Surprises: things that turned out differently than expected (either direction)
- Trade-offs accepted: conscious choices where alternatives were considered

For each decision:
1. State the decision clearly (what was chosen vs what was rejected)
2. Describe how it played out in practice
3. Tag as: GOOD_CALL | BAD_CALL | SURPRISE | TRADEOFF
4. State the recommendation for future work

Write findings to: .beads/artifacts/<feature-name>/compounding-decisions.md
```

---

#### Agent 3: Failure Analyst

**Task for Agent 3:**

```
Read the feature artifacts provided. Identify all FAILURES, BLOCKERS, and WASTED EFFORT:

- Bugs introduced and their root causes
- Wrong assumptions that required backtracking
- Blockers encountered and how they were resolved (or not)
- Wasted effort: work done that turned out unnecessary
- Missing prerequisites discovered mid-execution
- Test gaps that allowed regressions

For each failure:
1. Describe what went wrong
2. Identify the root cause (not just the symptom)
3. State how long it blocked progress (estimate)
4. Write the prevention rule: what should future agents do differently?

Write findings to: .beads/artifacts/<feature-name>/compounding-failures.md
```

---

### Phase 3: Synthesis & Triage

After all three agents complete, the orchestrator:

**Step 3.1: Read all three staging files:**
```
.beads/artifacts/<feature-name>/compounding-patterns.md
.beads/artifacts/<feature-name>/compounding-decisions.md
.beads/artifacts/<feature-name>/compounding-failures.md
```

**Step 3.2: Dedup check before writing:**

Search for existing similar learnings before creating new entries:

```bash
grep -l "<learning title>" .beads/learnings/ 2>/dev/null
```

If QMD is available (optional enhancement), also run a semantic search:

```bash
qmd query "<learning title>" --json 2>/dev/null
```

If a similar learning exists, merge instead of creating new.

**Step 3.3: Triage each finding:**

Tag every learning with:
- `domain`: which technical or process domain (e.g., `auth`, `database`, `testing`, `bead-decomposition`, `agent-coordination`)
- `severity`: `critical` (affects multiple features, prevents serious waste, or reveals systemic risk) vs `standard` (valuable but feature-specific)
- `applicable-when`: concise condition for when future agents should apply this learning
- `category`: `pattern` | `decision` | `failure`

**Step 3.4: Determine slug:**

Create a short, descriptive slug: `<primary-topic>-<secondary-topic>` (e.g., `auth-token-refresh`, `bead-scope-isolation`, `db-migration-ordering`).

**Step 3.5: Write the learnings file:**

```bash
mkdir -p .beads/learnings
cat > .beads/learnings/YYYYMMDD-<slug>.md << 'EOF'
<learnings content>
EOF
```

If Obsidian CLI is available (optional enhancement), also write to the vault:
```bash
obsidian create "beo-learnings/YYYYMMDD-<slug>.md" --content "<learnings content>" --silent 2>/dev/null
```

Use the format from `references/learnings-template.md`. Include YAML frontmatter.

One learnings file per feature. Group related findings within that file; do NOT create
separate files per finding.

**Step 3.6: Refresh QMD index (if available):**

```bash
qmd update 2>/dev/null && qmd embed 2>/dev/null
```

---

### Phase 4: Promote Critical Learnings

For every finding tagged `severity: critical`:

**Promotion criteria (only promote if ALL are true):**
- Affects more than one potential future feature (not just this specific codebase area)
- Would cause meaningful wasted effort if future agents didn't know it
- Is generalizable: not so implementation-specific it's useless elsewhere

**If criteria met, propose the promotion to the user:**

Present the proposed entry and request explicit approval before writing. Never auto-append to `critical-patterns.md`; see `pipeline-contracts.md` → Shared Artifact Write Rules.

**After user approves, append to `.beads/critical-patterns.md`:**

```bash
cat >> .beads/critical-patterns.md << 'EOF'
## [YYYYMMDD] <Learning Title>
**Category:** pattern | decision | failure
**Feature:** <feature-name>
**Tags:** [tag1, tag2]

<2-4 sentence summary of the learning and what to do differently>

**Full entry:** .beads/learnings/YYYYMMDD-<slug>.md
EOF
```

**If `.beads/critical-patterns.md` does not exist yet, create it with this header:**

```markdown
# Critical Patterns

Promoted learnings from completed features. Read this file at the start of every
planning Phase 0 and every exploring Phase 0. These are the lessons that cost the
most to learn and save the most by knowing.

---
```

**Refresh QMD index after promotion (if available):**

```bash
qmd update 2>/dev/null && qmd embed 2>/dev/null
```

---

### Phase 5: Optional CASS / CM Integration

These steps are optional. Check `.beads/config.json` for `cass_enabled` and `cm_enabled` flags.
If the config file is absent, skip both.

**If CASS is available:**
```
Index the session: provide the learnings file path to CASS for future semantic search.
This enables future agents to retrieve relevant learnings by description, not just by tag.
```

**If CM (Cognitive Memory) is available:**
```
Store each critical-severity learning as a cognitive memory entry.
Use the learning title as the memory key.
```

The file-based learnings are the primary system. CASS/CM are acceleration layers.

---

### Phase 6: Update STATE.md

Update `.beads/STATE.md` to record that compounding ran:

```markdown
# Beo State
- Phase: compounding → complete
- Feature: <epic-id> (<feature-name>)
- Tasks: N/A (post-execution skill)
- Next: done (feature pipeline complete)

Learnings file: .beads/learnings/YYYYMMDD-<slug>.md
Critical promotions: N (or 0)
```

Flush bead state to git:

```bash
br sync --flush-only
```

---

## Handoff

```
Compounding complete.
- Learnings: .beads/learnings/YYYYMMDD-<slug>.md
- Critical promotions: N findings added to critical-patterns.md
- The ecosystem now has [N total] accumulated learnings.

Next feature starts with this knowledge available.
```

---

## Red Flags

**Do NOT skip compounding because "we're in a hurry."**
The compound loop only works if it runs every cycle. One skip is fine;
a habit of skipping means the ecosystem never gets smarter.

**Do NOT promote everything as critical.**
critical-patterns.md is read at the start of every session. If it grows
past 20-30 entries it becomes noise. Only promote learnings that would
have saved >= 30 minutes if known in advance.

**Do NOT write generic learnings.**
"Test more carefully" is worthless. "When migrating database columns with
a non-null constraint, always provide a default in the migration or it
will fail in production with zero rows affected" is valuable.

**Do NOT fabricate findings.**
If the feature ran smoothly with no surprises, write that. A short learnings
file with 2 genuine entries is better than a long file with invented ones.

---

## Context Budget

If context usage exceeds 65%, write HANDOFF.json (see `pipeline-contracts.md` for schema) and STATE.md before pausing. Include the current phase, which analysis agents have completed, and what remains.

---

## References

- `references/learnings-template.md`: full template for learnings files with YAML frontmatter
