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

1. Environment verification: Run `beo_setup.py` to check dependencies (`br`, `bv`, `qmd`, `obsidian`), resolve Obsidian vault environment, and configure/index the `qmd` collection.
2. Beads capability validation: Ensure atomicity of `--claim` and verify standard command contracts.
3. Managed rules integration: Install or update the always-on BEO rules block in `AGENTS.md` from template.

