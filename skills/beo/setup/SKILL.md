---
name: beo-setup
description: Use for explicit BEO-on-Beads setup or health checks; default checks are read-only.
---
# beo-setup
Refs: `references/kernel.md`, `references/memory.md`.

## Decision
Confirm installed BEO tool compatibility without participating in ticket delivery.

## Enter
- User requests BEO setup, health check, or integration update.

## Owns
- Read-only environment/capability evidence and explicitly authorized memory setup/index maintenance.

## Does Not Own
- Ticket delivery, product mutation, approval tokens, verdicts, issue closure, or learning case authoring.

## Stops
- Required `br` command support is missing, atomic claim support cannot be verified, required memory-tool syntax is unknown, or requested memory writes lack authorization. Missing `bv`, `qmd`, or Obsidian support is degraded unless the requested setup action depends on it.

## Exits
- `setup_complete` -> `done`
- `user_confirmation_needed` -> `user`

## Method
1. Run `beo_setup.py` only for explicit setup/check/update requests; never run setup during ticket delivery.
2. Default to read-only capability checks for `br`, `bv`, `qmd`, `obsidian`, vault path, and learning collection state.
3. Verify Obsidian CLI create/vault syntax before enabling Obsidian-backed learning writes.
4. Use `--configure-memory` or `--refresh-memory-index` only when the user explicitly authorizes memory setup or qmd maintenance.
