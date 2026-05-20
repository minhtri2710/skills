---
name: beo-setup
description: Initial validation, environment health checks, and mandatory configuration for BEO-on-Beads integration.
---

# beo-setup

Refs: `beo-reference -> references/kernel.md`, `beo-reference -> references/memory.md`.

## Decision

Confirm BEO-on-Beads compatibility and install/update integration.

## Enter

- User asks to set up, check, or update BEO-on-Beads.

## Owns

- Setup health checks and AGENTS managed block.

## Stops

- `br` is unavailable.
- Required capabilities/commands cannot be confirmed.

## Exits

- `setup_complete` -> `done`
- `user_confirmation_needed` -> `user`

## Method

1. Check `br --version`, `bv --version`, and `.beads` workspace.
2. Verify capabilities for `ready`, `show`, `comments add`, `update --claim`, and `close`.
3. Verify `--claim` atomically sets assignee and `status=in_progress`.
4. Check optional `bv` orientation tool availability without blocking core delivery.
5. Detect optional memory surfaces (Obsidian, qmd) without blocking.
6. Install or update the BEO managed block in `AGENTS.md` from template.
