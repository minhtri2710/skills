---
name: beo-reference
description: Read-only BEO doctrine loader for kernel, Beads authority, decomposition, lifecycle, approval, mutation safety, events, modes, memory, registries, and templates.
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
3. Load exactly those narrow files (e.g., `safety.md`, `memory.md`).
4. Avoid loading all references by default to optimize token usage.

## Canonical homes

- Kernel invariants: `references/kernel.md`
- Lifecycle, Decomposition & Triage: `references/lifecycle.md`, `registry/pipeline.json`
- Safety & Path Rules: `references/safety.md`
- Execution Modes & Profiles: `registry/profiles.json`
- Approval Binding: `registry/approval-envelope.json`
- Ticket schema: `registry/ticket-schema.json`
- Ticket templates: `templates/TICKET.{quick,standard,strict}.md`
- Memory & Recall: `references/memory.md`
- Memory backends: `registry/memory-backends.json`
- Commands: `registry/command-contracts.json`
