# BEO CLI

## Purpose

This reference records exact command forms for bead and viewer operations only. CLI commands do not grant owner authority, approval, readiness, execution permission, or review verdicts.

## Beads

Use `br` only when the project explicitly uses a bead database and a loaded owner contract permits the mutation. `br` output is not canonical unless mirrored in `PLAN.md`.

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

Flush any optional bead metadata mutation before handoff or session end. Canonical workflow authority remains in `PLAN.md`, state, and artifacts.

## Viewer

Use `bv` for display only. Viewer output is advisory and never replaces canonical state or artifacts.
