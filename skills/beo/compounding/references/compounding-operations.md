# Compounding Operations

Operational playbook for `beo-compounding`.

## Table of Contents

- [1. Gather Context](#1-gather-context)
- [2. Three-Category Analysis](#2-three-category-analysis)
- [3. Synthesis and Triage](#3-synthesis-and-triage)
- [4. Critical Promotion Workflow](#4-critical-promotion-workflow)
- [5. State Update and Checkpointing](#5-state-update-and-checkpointing)

## 1. Gather Context

### Read Prior Learnings

Read existing learnings with the canonical read protocol (`../../reference/references/learnings-read-protocol.md`): QMD/Obsidian first, flat-file fallback only when unavailable.

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

Skip missing files.

Get feature commit history:

```bash
git log --oneline main..HEAD
# If already merged, use: git log --oneline --merges --grep="<feature-name>" main
```

If no history files exist, use recent git diff and conversation/session summaries.

## 2. Three-Category Analysis

Launch three subagents in parallel. Each writes to `.beads/artifacts/<feature_slug>/`.

### Agent 1: Pattern Extractor

1. Identify reusable code, architecture, process, and integration patterns.
2. For each pattern, provide name, why it matters, first location, and `applicable-when`.
3. Write to `.beads/artifacts/<feature_slug>/compounding-patterns.md`.

### Agent 2: Decision Analyst

1. Identify significant good calls, bad calls, surprises, and trade-offs.
2. For each decision, describe what was chosen, how it played out, tag it, and recommend future handling.
3. Write to `.beads/artifacts/<feature_slug>/compounding-decisions.md`.

### Agent 3: Failure Analyst

1. Identify failures, blockers, wasted effort, wrong assumptions, missing prerequisites, and test gaps.
2. For each one, describe what went wrong, root cause, cost, and a prevention rule.
3. Write to `.beads/artifacts/<feature_slug>/compounding-failures.md`.

Subagent output is staging only.

## 3. Synthesis and Triage

### Read the Staging Files

```text
.beads/artifacts/<feature_slug>/compounding-patterns.md
.beads/artifacts/<feature_slug>/compounding-decisions.md
.beads/artifacts/<feature_slug>/compounding-failures.md
```

### Dedup Before Writing

Use the learnings-read protocol (`../../reference/references/learnings-read-protocol.md`) to check for similar learnings. Use QMD semantic search first, flat-file fallback when unavailable.

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

Assign these tags for every learning:

| Tag | Values / rule |
| --- | --- |
| `domain` | assign domain |
| `severity` | `routine | useful | critical` |
| `applicable-when` | state when future agents should apply it |
| `category` | `pattern | decision | failure | anti-pattern` |

| Severity | Use when |
| --- | --- |
| `routine` | standard operational learning; keep in the feature learnings file only |
| `useful` | influences future planning or execution approach; highlight clearly in the learnings file |
| `critical` | would save 30+ minutes or prevent a recurring failure; candidate for `critical-patterns.md` after approval |

### Determine the Slug

Use `<feature_slug>` from the epic, not a topic-based name.

### Write the Learnings File

Use `learnings-template.md` and write one learnings file for the feature.

Canonical path: write to `.beads/learnings/`:

```bash
mkdir -p .beads/learnings
```

Create `.beads/learnings/YYYYMMDD-<slug>.md` with the learnings content.

Optional mirror: if Obsidian CLI is available and mirroring is desired, copy to the vault:

```bash
obsidian create path="beo-learnings/YYYYMMDD-<slug>.md" content="<learnings content>" silent 2>/dev/null
```

If both write surfaces are available and a vault copy is useful, mirror the final content there.

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

These are intermediate analysis artifacts. The learnings file in `.beads/learnings/` is the final output.

## 4. Critical Promotion Workflow

Promote every `severity: critical` learning only if all are true:

1. It applies beyond a single feature.
2. It would save meaningful future effort.
3. It generalizes well enough to matter again.

### Proposal Rule

Propose the promotion to the user first.

### After Approval

Use the canonical approval rule from `../../reference/references/approval-gates.md`, then append to `.beads/critical-patterns.md`:

Append using the entry format from `learnings-template.md` § critical-patterns.md Entry Format.

Refresh QMD after promotion if available.

## 5. State Update and Checkpointing

### Graph Verification

Before writing the final state, verify that the bead graph reflects completion. All executed beads and the epic must be `closed` in `br`:

```bash
br dep list <EPIC_ID> --direction up --type parent-child --json
# Check: every bead should have status "closed" (done) or "deferred" with "cancelled"/"failed" label; epic should be "closed"
```

If any bead is still open, stop and report the inconsistency to the user. Do not auto-close. Route back to `beo-reviewing` if the open beads represent unfinished work. If this is the second consecutive compounding→reviewing loop for the same feature, escalate to the user instead of routing back automatically.

If the epic is not closed, stop and route back to `beo-reviewing`. The reviewing skill owns epic closure.

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

> `completed` is the canonical terminal state for a feature after compounding.

Also record alongside the state file:

1. Learnings file: `.beads/learnings/YYYYMMDD-<slug>.md`
2. Critical promotions: N (or 0)

Then flush bead state:

```bash
br sync --flush-only
```

### Context-Budget Checkpoint

If context usage exceeds 65%, use the canonical shapes from `../../reference/references/state-and-handoff-protocol.md` for `HANDOFF.json` and `STATE.json`, then include:

1. current phase
2. which analysis agents have completed
3. what remains to synthesize or promote
