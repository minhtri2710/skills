# Artifact Protocol

Tasks use three artifact types: **spec** (what to do), **report** (what was done), and **task_state** (machine-readable status snapshot). Each has a specific location within the bead system.

## Locations

| Artifact | Storage | Read Command | Write Command |
|----------|---------|-------------|---------------|
| `spec` | Bead description | `br show <id> --json` → `.description` | `br update <id> --description "<content>"` |
| `report` | Bead comment (latest) | `br comments list <id> --json` → scan for header | `br comments add <id> --message "<formatted>"` |
| `task_state` | Bead comment (latest) | `br comments list <id> --json` → scan for header | `br comments add <id> --message "<formatted>"` |

## Spec (Bead Description)

The task specification is the bead's description field. Write it once during task creation or planning.

```bash
# Write spec
br update <id> --description "## Objective
Implement the authentication middleware.

## Files
- src/middleware/auth.ts
- src/middleware/auth.test.ts

## Verification
- All existing tests pass
- New middleware rejects unauthenticated requests with 401
"
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
# Scan backwards for the last comment containing "---ARTIFACT:report:"
# The latest version wins (v2 supersedes v1)
```

## Task State (Comment-Backed)

Machine-readable status snapshot for orchestrator consumption. Same comment format.

### Format

```
---ARTIFACT:task_state:v<version>---
{
  "status": "done|blocked|failed|partial",
  "summary": "One-line summary",
  "blockerReason": "Why blocked (if blocked)",
  "learnings": ["What was learned"],
  "filesChanged": ["path/to/file.ts"]
}
---END_ARTIFACT---
```

### Writing Task State

```bash
br comments add <id> --message '---ARTIFACT:task_state:v1---
{
  "status": "done",
  "summary": "Implemented auth middleware with JWT validation",
  "learnings": ["JWT library requires explicit algorithm whitelist"],
  "filesChanged": ["src/middleware/auth.ts", "src/middleware/auth.test.ts"]
}
---END_ARTIFACT---' --no-daemon
```

## Version Semantics

- Versions are monotonically increasing integers: v1, v2, v3...
- When reading, always take the **latest** (highest version number) artifact of each kind
- When writing, increment the version if updating an existing artifact
- Multiple versions of the same artifact kind can coexist in comments — only the latest matters

## Batch Sync Rule

After writing multiple artifacts or making multiple br mutations:

```bash
br sync --flush-only   # Export DB to JSONL for git
```
