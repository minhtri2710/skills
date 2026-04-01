# Artifact Protocol

Tasks use three artifact types: **spec** (what to do), **report** (what was done), and **task_state** (machine-readable status snapshot). Each has a specific location within the bead system.

## Table of Contents

- [Locations](#locations)
- [Spec (Bead Description)](#spec-bead-description)
- [Report (Comment-Backed)](#report-comment-backed)
- [Task State (Comment-Backed)](#task-state-comment-backed)
- [Version Semantics](#version-semantics)
- [Batch Sync Rule](#batch-sync-rule)

## Locations

| Artifact | Storage | Read Command | Write Command |
|----------|---------|-------------|---------------|
| `spec` | Bead description | `br show <id> --json` → `.description` | `br update <id> --description "<content>"` |
| `report` | Bead comment (latest) | `br comments list <id> --json` → scan for header | `br comments add <id> --no-daemon --message "<formatted>"` |
| `task_state` | Bead comment (latest) | `br comments list <id> --json` → scan for header | `br comments add <id> --no-daemon --message "<formatted>"` |

## Spec (Bead Description)

The task specification is the bead's description field. Write it once during task creation or planning, always in Markdown format.

### Required Spec Structure

Use `bead-description-templates.md` as the single source of truth for all bead description formats.

- Planned execution beads → **Planned Task Bead Template**
- Reactive fix beads → **Reactive Fix Bead Template**
- Review/debug follow-up beads → **Follow-Up Bead Template**

Every bead description must be Markdown-formatted.

Reactive fix beads (created by beo-reviewing, beo-debugging, beo-router instant path) are exempt from the Story Context requirement, but they must still follow the shared reactive template.

```bash
# Write spec
br update <id> --description "<Markdown content using the appropriate shared bead template>"
```

## Report (Comment-Backed)

The report captures what the worker accomplished. It is appended as a bead comment with a specific header format.

### Format

```
---ARTIFACT:report:v<version>---
<markdown content>
---END_ARTIFACT---
```

### Writing a Report

```bash
# For short reports (< 32KB)
br comments add <id> --message "---ARTIFACT:report:v1---
## Summary
Implemented auth middleware with JWT validation.

## Changes
- Created src/middleware/auth.ts (new file, 45 lines)
- Added tests in src/middleware/auth.test.ts (3 test cases)

## Verification
- All 156 tests pass
- Manual test: unauthenticated request returns 401
---END_ARTIFACT---" --no-daemon

# For large reports, write to a temp file first
cat > /tmp/report.md << 'EOF'
---ARTIFACT:report:v1---
## Summary
...
---END_ARTIFACT---
EOF
br comments add <id> --file /tmp/report.md --no-daemon
```

### Reading the Latest Report

```bash
# List all comments, find the latest report artifact
br comments list <id> --json --no-daemon
# Inspect the returned comments and scan backwards for the last report artifact header
# The latest version wins (v2 supersedes v1)
```

## Task State (Comment-Backed)

The task_state artifact is a machine-readable status snapshot used by the orchestrator and monitoring tools. It follows the same comment-backed format as reports.

### Format

```
---ARTIFACT:task_state:v<version>---
beo_status: <pending | dispatch_prepared | in_progress | done | blocked | failed | partial | cancelled>
worker: <agent-name or empty>
claimed_at: <ISO-8601 or empty>
blocked_by: <bead-id list or empty>
blocker_type: <MISSING_CONTEXT | DEPENDENCY_NOT_MET | TECHNICAL_FAILURE | AMBIGUITY or empty>
context_pct: <estimated context usage percentage>
---END_ARTIFACT---
```

### Writing a Task State

```bash
br comments add <id> --message "---ARTIFACT:task_state:v1---
beo_status: in_progress
worker: BlueLake
claimed_at: 2026-03-15T10:30:00Z
blocked_by:
blocker_type:
context_pct: 35
---END_ARTIFACT---" --no-daemon
```

Task state is optional. Workers update it when claiming, blocking, or completing beads. The orchestrator reads the latest version to build the swarm status view.

## Version Semantics

- Versions are monotonically increasing integers: v1, v2, v3...
- When reading, always take the **latest** (highest version number) artifact of each kind
- When writing, increment the version if updating an existing artifact
- Multiple versions of the same artifact kind can coexist in comments. Only the latest matters.

## Batch Sync Rule

After writing multiple artifacts or making multiple br mutations:

```bash
br sync --flush-only   # Export DB to JSONL for git
```
