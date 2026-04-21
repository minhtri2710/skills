# Compounding Operations

Operational playbook for `beo-compound`.

## 1. Gather Context

Read prior learnings with `learnings-read-protocol.md`.

Read these feature artifacts when present:
- `.beads/artifacts/<feature_slug>/CONTEXT.md`
- `.beads/artifacts/<feature_slug>/discovery.md`
- `.beads/artifacts/<feature_slug>/approach.md`
- `.beads/artifacts/<feature_slug>/plan.md`
- `.beads/artifacts/<feature_slug>/phase-contract.md`
- `.beads/artifacts/<feature_slug>/story-map.md`
- `.beads/artifacts/<feature_slug>/review-findings.md`
- `.beads/STATE.json` or handoff artifacts
- `br show` output for the feature

Skip missing files.

Get feature commit history:

```bash
git log --oneline main..HEAD
```

If the feature is already merged, use merge history or recent diff instead.

## 2. Single-Feature Analysis

Extract three categories into working notes:
1. reusable patterns
2. significant decisions and trade-offs
3. failures, blockers, or wrong assumptions

These are analysis lenses only, not separate durable artifacts.

## 3. Synthesis and Triage

### Dedup Before Writing

Use the learnings read protocol to check for similar learnings. Prefer QMD search; fall back to flat-file search.

If a similar learning exists, merge instead of creating a duplicate.

### Triage Tags

Assign for every learning:

| Tag | Values / rule |
| --- | --- |
| `domain` | assign domain |
| `severity` | `routine | useful | critical` |
| `applicable-when` | state when future agents should apply it |
| `category` | `pattern | decision | failure | anti-pattern` |

Severity rules:
- `routine` → keep in the feature learning file only
- `useful` → likely to influence future planning or execution
- `critical` → likely candidate for `critical-patterns.md` after approval

### Determine the Slug

Use the feature slug from the epic, not a topic-derived name.

### Write the Learnings File

Use `learnings-template.md`.

Canonical write path:

```bash
mkdir -p .beads/learnings
```

Create `.beads/learnings/YYYYMMDD-<slug>.md`.

Optional vault mirror:

```bash
obsidian create path="beo-learnings/YYYYMMDD-<slug>.md" content="<learnings content>" silent 2>/dev/null
```

### Refresh QMD Index

```bash
qmd update 2>/dev/null && qmd embed 2>/dev/null
```

Single-feature promotion into `.beads/critical-patterns.md` is allowed only after explicit approval and only when the promoted pattern is traceable to this feature. Corpus-wide consolidation remains `beo-dream` work.

## 4. State Update and Checkpointing

### Graph Verification

Before final state, verify graph completion:

```bash
br dep list <EPIC_ID> --direction up --type parent-child --json
```

Requirements:
- every executed bead is `closed`, or `deferred` with `cancelled` + `cancelled_accepted`
- the epic is `closed`

If any bead is still open, stop. Do not auto-close. Route back to `beo-review` if the feature is unfinished. If this is the second consecutive compound→review loop for the same feature, escalate to the user.

If the epic is not closed, stop and route back to `beo-review`. Review owns epic closure.

### Normal Completion

Write `.beads/STATE.json` with:
- `phase: "compounding"`
- `status: "completed"`
- `next: "beo-route"`
- actual planning-aware fields for the feature

Also record:
1. learnings file path
2. number of critical promotions, if any

Then flush:

```bash
br sync --flush-only
```

### Context-Budget Checkpoint

If context usage exceeds 65%, write canonical `STATE.json` and `HANDOFF.json`, then include:
1. current phase
2. completed analysis passes
3. what remains to synthesize or promote
