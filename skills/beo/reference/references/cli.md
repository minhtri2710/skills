# CLI

## Version checks

```bash
br --version
bv --version
```

## Agent-safe reads

```bash
br ready --json
br show <id> --json
br comments list <id> --json
```

## Mutations

```bash
br create --title "<title>" --type task --priority <n> --json
br update <id> --description "<text>" --json
br update <id> --status <status> --json
br comments add <id> --message "<text>" --json
br label add <id> -l <label> --json
br label remove <id> -l <label> --json
br dep add <child-id> <parent-id> --json
br sync --flush-only
```

## Beads Viewer

```bash
bv --version
```

Do not run bare `bv` in agent sessions. Use viewer guidance only through canonical beo references.

## Semantic load

BEO assigns specific meaning to the following `br` values. If `br` changes the semantics of any of these values, update this section and all beo-reference pointers before relying on existing beo doctrine.

| Value | Context | BEO semantic |
| --- | --- | --- |
| `approved` | bead label | bead is inside the current approval envelope; `beo-validate` writes/removes this as an operator-visible marker, but `ApprovalCurrent` still requires the approval record and STATE pointer |
| `reserved` | bead label | bead is claimed by an agent in progress; execution claim signal that may coexist with `approved` |
| `blocked` | bead status | bead cannot proceed; prerequisite or external dependency unresolved |
| `in_progress` | bead status | bead is actively being executed |
| `done` | bead status | bead execution complete and committed |
| `br dep add <child> <parent>` | dependency direction | child depends on parent; `ordered_batch` uses this to determine execution order |
