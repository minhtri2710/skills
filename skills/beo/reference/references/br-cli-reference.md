# br CLI Reference

All task and feature management uses the `br` CLI. Every command that returns structured data supports `--json` for machine-readable output.

## Table of Contents

- [Workspace Setup](#workspace-setup)
- [Create](#create)
- [Read](#read)
- [Update](#update)
- [Dependencies](#dependencies)
- [Scheduling](#scheduling)
- [Comments](#comments)
- [Audit](#audit)
- [Sync (Git Integration)](#sync-git-integration)
- [Other](#other)

## Workspace Setup

```bash
br init                          # Initialize .beads/ workspace (idempotent)
br --version                     # Check installation
br config list --json            # Read current configuration
br config set issue_prefix WAR   # Set issue prefix for this project
```

## Create

```bash
# Create epic (feature-level container)
br create "<Feature Name>" -t epic -p 1 --json

# Create task under an epic
br create "<Task Title>" -t task --parent <epic-id> -p <priority> --json

# Create task with an explicit blocking dependency
br create "<Task Title>" -t task --deps blocks:<depends-on-id> -p <priority> --json
```

**Priority scale**: 0 = critical/spike, 1 = high, 2 = normal, 3 = low, 4 = backlog

## Read

```bash
br show <id> --json              # Full bead details (labels, description, status, comments)
br show <id> --format toon       # Token-optimized LLM-friendly format
br list --json                   # List all open beads
br list --type epic --json       # List epics only
br list --type task --json       # List tasks only
br list -a --json                # List ALL beads (including closed)
br list -s <status> --json       # Filter by status (open, in_progress, closed, deferred)
```

## Update

```bash
br update <id> --status <s>            # Change status: open, in_progress, closed, deferred
br update <id> -p <n>                  # Change priority (0=critical/spike, 1=high, 2=normal, 3=low, 4=backlog)
br update <id> --description <content> # Set description (used for spec storage)
br update <id> --claim                 # Claim bead (sets assignee + status=in_progress)
br update <id> --assignee '' -s open   # Unclaim bead (release assignment)
br label add <id> -l <label>           # Add a label
br label remove <id> -l <label>        # Remove a label
br close <id>                          # Close bead (marks done/completed)
```

**Common labels**: `approved`, `blocked`, `failed`, `partial`, `cancelled`, `debug_attempted`, `in_progress`, `dispatch_prepared`, `review`, `review-p1`, `review-p2`, `review-p3`

## Dependencies

```bash
br dep add <child-id> <parent-id>                          # Add dependency edge
br dep remove <child-id> <parent-id>                       # Remove dependency edge
br dep list <id> --direction down --type blocks --json      # List what blocks this bead (upstream deps)
br dep list <id> --direction up --type parent-child --json  # List children under parent
br dep cycles --json                                        # Detect circular dependencies
```

## Scheduling

```bash
br ready --json                  # List actionable (unblocked, open) beads
br blocked --json                # List blocked beads
```

## Comments

```bash
br comments add <id> --message "<msg>" --no-daemon    # Add short comment
br comments add <id> --file <path> --no-daemon         # Add comment from file (for large content)
br comments list <id> --json --no-daemon                # List comments on a bead
```

## Audit

```bash
br audit record --kind <kind> --issue-id <id>   # Record audit event
br audit log <id> --json                         # View audit log
```

**Audit kinds**: tool-defined strings such as `llm_call`, `tool_call`, or `label`

## Sync (Git Integration)

```bash
br sync --flush-only     # Export DB to JSONL files (for git commit)
br sync --import-only    # Import JSONL files to DB (after git pull)
```

**Rule**: Run `br sync --flush-only` after any batch of mutations before committing to git.

## Other

```bash
br search "<query>" --json   # Full-text search
br stale --days 7 --json     # Find stale beads
br stats --json              # Project statistics
br doctor                    # Run diagnostics
br lint --json               # Lint issues
br changelog --json          # Generate changelog
```
