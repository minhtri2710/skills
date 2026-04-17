# Compounding Operations

Operational playbook for `beo-compound`.

## Table of Contents

- [1. Gather Context](#1-gather-context)
- [2. Three-Category Analysis](#2-three-category-analysis)
- [3. Synthesis and Triage](#3-synthesis-and-triage)
- [4. Critical Promotion Workflow](#4-critical-promotion-workflow)
- [5. State Update and Checkpointing](#5-state-update-and-checkpointing)

## 1. Gather Context

### Read Prior Learnings

Read existing learnings with the canonical read protocol (`beo-reference` → `references/learnings-read-protocol.md`): QMD/Obsidian first, flat-file fallback only when unavailable.

### Collect Feature Artifacts

Read these if present:

```text
.beads/artifacts/<feature_slug>/CONTEXT.md
.beads/artifacts/<feature_slug>/discovery.md
.beads/artifacts/<feature_slug>/approach.md
.beads/artifacts/<feature_slug>/plan.md
.beads/artifacts/<feature_slug>/phase-contract.md
.beads/artifacts/<feature_slug>/story-map.md
.beads/artifacts/<feature_slug>/review-findings.md
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

## 2. Single-Feature Analysis

Review the feature evidence and extract three categories directly into your working notes before writing the final learnings artifact:

1. reusable patterns
2. significant decisions and trade-offs
3. failures, blockers, or wrong assumptions

These categories are analysis lenses, not separate durable artifacts.

## 3. Synthesis and Triage

### Dedup Before Writing

Use the learnings-read protocol (`beo-reference` → `references/learnings-read-protocol.md`) to check for similar learnings. Use QMD semantic search first, flat-file fallback when unavailable.

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

Use `learnings-template.md` and write the learnings file (see HARD-GATE in SKILL.md for the one-file-per-feature rule).

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

A feature learning may promote reusable patterns from the accepted feature into `.beads/critical-patterns.md`, but only after explicit approval and only when the pattern is traceable to that feature's evidence. Long-horizon merging, retirement, and corpus-wide consolidation remain owned by `beo-dream`.

## 4. State Update and Checkpointing

### Graph Verification

Before writing the final state, verify that the bead graph reflects completion. All executed beads and the epic must be `closed` in `br`:

```bash
br dep list <EPIC_ID> --direction up --type parent-child --json
# Check: every bead should have status "closed" (done) or "deferred" with "cancelled"/"failed" label; epic should be "closed"
```

If any bead is still open, stop and report the inconsistency to the user. Do not auto-close. Route back to `beo-review` if the open beads represent unfinished work. If this is the second consecutive compounding→reviewing loop for the same feature, escalate to the user instead of routing back automatically.

If the epic is not closed, stop and route back to `beo-review`. The reviewing skill owns epic closure.

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
  "next": "beo-route",
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

If context usage exceeds 65%, use the canonical shapes from `beo-reference` → `references/state-and-handoff-protocol.md` for `HANDOFF.json` and `STATE.json`, then include:

1. current phase
2. which analysis agents have completed
3. what remains to synthesize or promote
