# br CLI Reference

Canonical `br` commands for beo. Prefer `--json` whenever structured output is available.

## Workspace Setup

```bash
br init                          # Initialize .beads/ workspace (idempotent)
br --version                     # Check installation
br config list --json            # Read current configuration
br config set issue_prefix WAR   # Set issue prefix for this project
```

## Create

```bash
br create "<Feature Name>" -t epic -p 1 --json
br create "<Task Title>" -t task --parent <epic-id> -p <priority> --json
br create "<Task Title>" -t task --deps blocks:<depends-on-id> -p <priority> --json
```

Priority scale: `0` critical or spike, `1` high, `2` normal, `3` low, `4` backlog.

## Read

```bash
br show <id> --json
br show <id> --format toon
br list --json
br list --type epic --json
br list --type task --json
br list -a --json
br list -s <status> --json
```

## Update

```bash
br update <id> --status|-s <s>
br update <id> -p <n>
br update <id> --description <content>
br update <id> --claim
br update <id> --assignee '' -s open
br label add <id> -l <label>
br label remove <id> -l <label>
br close <id>
```

Common labels: `approved`, `blocked`, `failed`, `partial`, `cancelled`, `debug_attempted`, `in_progress`, `dispatch_prepared`, `review`, `review-p1`, `review-p2`, `review-p3`.

## Dependencies

```bash
br dep add <child-id> <parent-id>
br dep remove <child-id> <parent-id>
br dep list <id> --direction down --type blocks --json
br dep list <id> --direction up --type parent-child --json
br dep cycles --json
```

## Scheduling

```bash
br ready --json
br blocked --json
```

## Comments

```bash
br comments add <id> --message "<msg>" --no-daemon
br comments add <id> --file <path> --no-daemon
br comments list <id> --json --no-daemon
```

## Audit

```bash
br audit record --kind <kind> --issue-id <id> [--tool-name <name>]
br audit log <id> --json
```

Audit kinds are tool-defined strings such as `llm_call`, `tool_call`, or `label`.

## Sync

```bash
br sync --flush-only
br sync --import-only
```

Rules:
- always use `--no-daemon` on `br comments add` and `br comments list`
- always run `br sync --flush-only` after any batch of mutations before commit or session end
- never run bare `br sync`

## Other

```bash
br search "<query>" --json
br stale --days 7 --json
br stats --json
br doctor
br lint --json
br changelog --json
```
