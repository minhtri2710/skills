---
name: beo-reference
description: Read-only BEO doctrine loader for kernel, Beads authority, decomposition, lifecycle, approval, mutation safety, events, modes, memory, registries, recipes, and templates.
---

# beo-reference

Refs: `beo-reference -> references/kernel.md`.

## Decision

Load canonical BEO doctrine and registries without mutation.

## Enter

- BEO owner needs canonical doctrine or registry lookup.

## Owns

- Doctrine text and registry references.

## Stops

- Request requires product or Beads lifecycle mutation.



## Method

1. Load `references/kernel.md` first for always-on invariants.
2. Pick the narrow reference or registry needed for the active decision.
3. Load exactly those narrow files (e.g., `ticket.md`, `approval.md`).
4. Avoid loading all references by default to optimize token usage.

## Canonical homes

- Kernel invariants: `beo-reference -> references/kernel.md`
- Beads authority: `beo-reference -> references/beads-authority.md`
- Decomposition: `beo-reference -> references/decomposition.md`
- Ticket contract: `beo-reference -> references/ticket.md`, `registry/ticket-schema.json`
- Approval: `beo-reference -> references/approval.md`, `registry/approval-envelope.json`
- Mutation safety: `beo-reference -> references/mutation-safety.md`
- Lifecycle/Events: `beo-reference -> references/lifecycle-events.md`, `registry/pipeline.json`
- Modes: `beo-reference -> references/modes.md`, `registry/profiles.json`
- Memory/Recall: `beo-reference -> references/memory.md`
- Commands: `registry/command-contracts.json`
- Templates: `templates/*.md`

