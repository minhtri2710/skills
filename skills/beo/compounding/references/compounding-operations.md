# Compounding Operations

Detailed operational playbook for `beo-compounding`. Load this file when you need exact artifact collection, subagent analysis prompts, learnings-file write steps, critical-promotion mechanics, optional integrations, or checkpoint/handoff details.

## Table of Contents

- [1. Gather Context](#1-gather-context)
- [2. Three-Category Analysis](#2-three-category-analysis)
- [3. Synthesis and Triage](#3-synthesis-and-triage)
- [4. Critical Promotion Workflow](#4-critical-promotion-workflow)
- [5. State Update and Checkpointing](#5-state-update-and-checkpointing)

## 1. Gather Context

### Read Prior Learnings

Before analyzing the feature, read existing learnings using the canonical read protocol (`../../reference/references/learnings-read-protocol.md`): QMD/Obsidian first, flat-file fallback only when unavailable. This prevents creating duplicate learnings and grounds the analysis in what is already known.

### Collect Feature Artifacts

Read these if present:

```text
.beads/artifacts/<feature_slug>/CONTEXT.md
.beads/artifacts/<feature_slug>/discovery.md
.beads/artifacts/<feature_slug>/approach.md
.beads/artifacts/<feature_slug>/plan.md
.beads/artifacts/<feature_slug>/phase-contract.md
.beads/artifacts/<feature_slug>/story-map.md
.beads/review-findings.md
.beads/artifacts/<feature_slug>/debug-notes.md
.beads/STATE.json or HANDOFF artifacts
.beads/ or `br show` output
```

Missing files are skipped silently; compounding still works with partial context.

Get feature commit history:

```bash
git log --oneline main..HEAD
# If already merged, use: git log --oneline --merges --grep="<feature-name>" main
```

If no history files exist, fall back to recent git diff and conversation/session summaries.

## 2. Three-Category Analysis

Launch three subagents in parallel. Each writes to a staging file under `.beads/artifacts/<feature_slug>/`.

### Agent 1: Pattern Extractor

Task summary:
- identify reusable code, architecture, process, and integration patterns
- for each pattern, provide name, why it matters, first location, and `applicable-when`
- write to `.beads/artifacts/<feature_slug>/compounding-patterns.md`

### Agent 2: Decision Analyst

Task summary:
- identify significant good calls, bad calls, surprises, and trade-offs
- for each decision, describe what was chosen, how it played out, tag it, and recommend future handling
- write to `.beads/artifacts/<feature_slug>/compounding-decisions.md`

### Agent 3: Failure Analyst

Task summary:
- identify failures, blockers, wasted effort, wrong assumptions, missing prerequisites, and test gaps
- for each one, describe what went wrong, root cause, cost, and a prevention rule
- write to `.beads/artifacts/<feature_slug>/compounding-failures.md`

Subagent output is staging only — see the HARD-GATE in SKILL.md for the orchestrator-writes rule.

## 3. Synthesis and Triage

### Read the Staging Files

```text
.beads/artifacts/<feature_slug>/compounding-patterns.md
.beads/artifacts/<feature_slug>/compounding-decisions.md
.beads/artifacts/<feature_slug>/compounding-failures.md
```

### Dedup Before Writing

Use the learnings-read protocol (`../../reference/references/learnings-read-protocol.md`) to check for existing similar learnings. Preferred path: QMD semantic search first, flat-file fallback when unavailable.

```bash
# Preferred: semantic dedup via QMD
qmd query "<learning title>" --json 2>/dev/null
```

```bash
# Fallback: flat-file search
# Use your content search tool to search .beads/learnings/ for "<learning title>"
```

If a similar learning exists, merge instead of creating a new one.

### Triage Tags

For every learning, assign:
- `domain`
- `severity` (`routine | useful | critical`)
  - **routine**: standard operational learning, no special action; kept in the feature learnings file only
  - **useful**: influences future planning or execution approach; highlight clearly in the learnings file
  - **critical**: would save 30+ minutes or prevent a recurring failure; candidate for `critical-patterns.md` after approval
- `applicable-when`
- `category` (`pattern | decision | failure | anti-pattern`)

### Determine the Slug

Use `<feature_slug>` (the immutable feature slug from the epic, not a topic-based name).

### Write the Learnings File

Use `learnings-template.md` and write the learnings file (see HARD-GATE in SKILL.md for the one-file-per-feature rule).

Canonical path: write to `.beads/learnings/`:

```bash
mkdir -p .beads/learnings
```

Use your file writing tool to create `.beads/learnings/YYYYMMDD-<slug>.md` with the learnings content.

Optional mirror: if Obsidian CLI is available and mirroring is desired, copy to the vault:

```bash
obsidian create path="beo-learnings/YYYYMMDD-<slug>.md" content="<learnings content>" silent 2>/dev/null
```

If both write surfaces are available and it is useful to keep a vault copy, mirror the final content into the Obsidian vault as well.

### Refresh QMD Index

```bash
qmd update 2>/dev/null && qmd embed 2>/dev/null
```

### Clean Up Staging Files

After the learnings file is written and verified, remove the staging files:

```text
.beads/artifacts/<feature_slug>/compounding-patterns.md
.beads/artifacts/<feature_slug>/compounding-decisions.md
.beads/artifacts/<feature_slug>/compounding-failures.md
```

These are intermediate analysis artifacts, not durable project records. The learnings file in `.beads/learnings/` is the final output.

## 4. Critical Promotion Workflow

For every `severity: critical` learning, promote only if all are true:
- applies beyond a single feature
- would save meaningful future effort
- generalizes well enough to matter again

### Proposal Rule

Propose the promotion to the user first (see HARD-GATE in SKILL.md for the no-auto-append rule).

### After Approval

Use the canonical approval rule from `../../reference/references/approval-gates.md`, then append to `.beads/critical-patterns.md`:

Use your file editing tool to append to `.beads/critical-patterns.md` using the entry format from `learnings-template.md` § critical-patterns.md Entry Format.

Refresh QMD after promotion if available.

## 5. State Update and Checkpointing

### Graph Verification

Before writing the final state, verify that the bead graph reflects completion — all executed beads and the epic must be `closed` in `br`, not just tracked in conversation:

```bash
br dep list <EPIC_ID> --direction up --type parent-child --json
# Check: every bead should have status "closed"; epic should be "closed"
```

If any bead is still open, stop and report the inconsistency to the user. Do not auto-close. Route back to `beo-reviewing` if the open beads represent unfinished work. If this is the second consecutive compounding→reviewing loop for the same feature, escalate to the user instead of routing back automatically.

### Normal Completion

Update `.beads/STATE.json`:

```json
{
  "schema_version": 1,
  "phase": "compounding",
  "status": "completed",
  "feature": "<epic-id>",
  "feature_slug": "<feature_slug>",
  "tasks": "N/A (post-execution skill)",
  "next": "beo-router",
  "planning_mode": "<single-phase | multi-phase — use actual feature value>",
  "has_phase_plan": "<true if phase-plan.md existed — use actual feature value>",
  "current_phase": "<final phase number — use actual feature value>",
  "total_phases": "<total phases — use actual feature value>",
  "phase_name": "<current phase name>"
}
```

> `completed` is the canonical terminal state for a feature after compounding. This value is defined in `status-mapping.md` as a feature-level terminal state.

Also record alongside the state file:
- Learnings file: `.beads/learnings/YYYYMMDD-<slug>.md`
- Critical promotions: N (or 0)

Then flush bead state:

```bash
br sync --flush-only
```

### Context-Budget Checkpoint

If context usage exceeds 65%, use the canonical shapes from `../../reference/references/state-and-handoff-protocol.md` for `HANDOFF.json` and `STATE.json`, then include:
- current phase
- which analysis agents have completed
- what remains to synthesize or promote
