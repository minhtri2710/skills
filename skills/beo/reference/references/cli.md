<!-- owner: beo-reference -->
<!-- version: 2026-04-29 -->
<!-- last-reviewed: 2026-04-29 -->

# CLI

## Exact command forms

| Purpose | Command form |
| --- | --- |
| add comment | `br comments add <id> --message <text> --no-daemon` |
| show version | `bv --version` |
| create bead | `br create --title <title> --type task --priority <n> --no-daemon` |
| update description | `br update <id> --description <text> --no-daemon` |
| update status | `br update <id> --status <status> --no-daemon` |
| update status and label | `br update <id> --status <status> --label <label> --no-daemon` |
| add dependency | `br dep add <child-id> <parent-id> --no-daemon` |
| flush bead DB | `br sync --flush-only` |
