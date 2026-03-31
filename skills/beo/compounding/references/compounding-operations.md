# Compounding Operations

Detailed operational playbook for `beo-compounding`. Load this file when you need exact artifact collection, subagent analysis prompts, learnings-file write steps, critical-promotion mechanics, optional integrations, or checkpoint/handoff details.

## Table of Contents

- [1. Gather Context](#1-gather-context)
- [2. Three-Category Analysis](#2-three-category-analysis)
- [3. Synthesis and Triage](#3-synthesis-and-triage)
- [4. Critical Promotion Workflow](#4-critical-promotion-workflow)
- [5. Optional Integrations](#5-optional-integrations)
- [6. State Update and Checkpointing](#6-state-update-and-checkpointing)

## 1. Gather Context

Collect all available artifacts from the completed feature. Read these if present:

```text
.beads/artifacts/<feature-name>/CONTEXT.md
.beads/artifacts/<feature-name>/discovery.md
.beads/artifacts/<feature-name>/plan.md
.beads/artifacts/<feature-name>/phase-contract.md
.beads/artifacts/<feature-name>/story-map.md
.beads/review-findings.md
.beads/artifacts/<feature-name>/debug-notes.md
.beads/STATE.md or HANDOFF artifacts
.beads/ or `br show` output
```

Missing files are skipped silently; compounding still works with partial context.

Get feature commit history:

```bash
git log --oneline main..feature/<feature-name>
# If already merged, use: git log --oneline --merges --grep="<feature-name>" main
```

If no history files exist, fall back to recent git diff and conversation/session summaries.

## 2. Three-Category Analysis

Launch three subagents in parallel. Each writes to a staging file under `.beads/artifacts/<feature-name>/`.

### Agent 1: Pattern Extractor

Task summary:
- identify reusable code, architecture, process, and integration patterns
- for each pattern, provide name, why it matters, first location, and `applicable-when`
- write to `.beads/artifacts/<feature-name>/compounding-patterns.md`

### Agent 2: Decision Analyst

Task summary:
- identify significant good calls, bad calls, surprises, and trade-offs
- for each decision, describe what was chosen, how it played out, tag it, and recommend future handling
- write to `.beads/artifacts/<feature-name>/compounding-decisions.md`

### Agent 3: Failure Analyst

Task summary:
- identify failures, blockers, wasted effort, wrong assumptions, missing prerequisites, and test gaps
- for each one, describe what went wrong, root cause, cost, and a prevention rule
- write to `.beads/artifacts/<feature-name>/compounding-failures.md`

Do not let subagents write the final learnings file. Only the orchestrator writes durable learnings.

## 3. Synthesis and Triage

### Read the Staging Files

```text
.beads/artifacts/<feature-name>/compounding-patterns.md
.beads/artifacts/<feature-name>/compounding-decisions.md
.beads/artifacts/<feature-name>/compounding-failures.md
```

### Dedup Before Writing

```bash
grep -l "<learning title>" .beads/learnings/ 2>/dev/null
```

Optional semantic search if QMD is available:

```bash
qmd query "<learning title>" --json 2>/dev/null
```

If a similar learning exists, merge instead of creating a new one.

### Triage Tags

For every learning, assign:
- `domain`
- `severity` (`critical` or `standard`)
- `applicable-when`
- `category` (`pattern | decision | failure`)

### Determine the Slug

Use `<primary-topic>-<secondary-topic>`.

### Write the Learnings File

Use `learnings-template.md` and write one learnings file per feature.

Preferred path: write to the Obsidian vault first:

```bash
obsidian create "beo-learnings/YYYYMMDD-<slug>.md" --content "<learnings content>" --silent 2>/dev/null
```

Fallback path: if Obsidian CLI is unavailable or the vault write cannot be completed safely, write to `.beads/learnings/`:

```bash
mkdir -p .beads/learnings
cat > .beads/learnings/YYYYMMDD-<slug>.md << 'EOF'
<learnings content>
EOF
```

If both write surfaces are available and it is useful to keep a local copy, mirror the final content into `.beads/learnings/` as well.

### Refresh QMD Index

```bash
qmd update 2>/dev/null && qmd embed 2>/dev/null
```

## 4. Critical Promotion Workflow

For every `severity: critical` learning, promote only if all are true:
- applies beyond a single feature
- would save meaningful future effort
- generalizes well enough to matter again

### Proposal Rule

Propose the promotion to the user first. Never auto-append to `.beads/critical-patterns.md`.

### After Approval

Use the canonical approval rule from `../../reference/references/approval-gates.md`, then append to `.beads/critical-patterns.md`:

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

If the file does not exist, create it first with the canonical header from the main skill.

Refresh QMD after promotion if available.

## 5. Optional Integrations

These depend on `.beads/config.json` flags.

### CASS

If `cass_enabled`, index the session or learnings path for future semantic retrieval.

### CM

If `cm_enabled`, store each critical learning as a cognitive-memory entry using the learning title as the key.

File-based learnings remain the primary system. CASS/CM are acceleration layers.

## 6. State Update and Checkpointing

### Normal Completion

Update `.beads/STATE.md`:

```markdown
# Beo State
- Phase: compounding → complete
- Feature: <epic-id> (<feature-name>)
- Tasks: N/A (post-execution skill)
- Next: done (feature pipeline complete)

Learnings file: .beads/learnings/YYYYMMDD-<slug>.md
Critical promotions: N (or 0)
```

Then flush bead state:

```bash
br sync --flush-only
```

### Context-Budget Checkpoint

If context usage exceeds 65%, use the canonical shapes from `../../reference/references/state-and-handoff-protocol.md` for `HANDOFF.json` and `STATE.md`, then include:
- current phase
- which analysis agents have completed
- what remains to synthesize or promote
