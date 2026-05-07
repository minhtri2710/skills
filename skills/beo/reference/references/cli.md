# BEO CLI v2

## Purpose

This reference records exact command forms for bead and viewer operations only. CLI commands do not grant owner authority, approval, readiness, execution permission, or review verdicts.

## Beads

Use `br` for bead database operations when a loaded owner contract permits the mutation.

Common read-only forms:

```sh
br list
br show <id>
br deps <id>
```

Common mutation forms:

```sh
br create --title "<title>" --description "<description>"
br update <id> --status <status>
br dep add <id> <dependency-id>
```

Flush any bead DB mutation before handoff or session end.

## Viewer

Use `bv` for display only. Viewer output is advisory and never replaces canonical state or artifacts.
