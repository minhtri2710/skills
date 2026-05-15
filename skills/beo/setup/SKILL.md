---
name: beo-setup
description: |
  Sets up and checks BEO repository integration. Use for direct AGENTS.md managed block, repository bootstrap orientation, version checks, setup health checks, and repository bootstrap requests. Not for canonical reference lookup, runtime delivery, approval, execution, review, debugging, learning, routing, or product implementation.
---

# beo-setup

## Purpose

Install, check, and explain repository integration.

## Decision Card

Decision: install, check, or explain repository integration.

Can enter when:
- direct setup, health check, managed block, repository bootstrap orientation, or version check is requested

Can write:
- `AGENTS.md` managed block and setup surfaces only

Must stop when:
- requested mutation is outside repository integration setup/checks

Exit summary (non-authoritative):
- `setup_complete` -> `done`
- `user_confirmation_needed` -> `user`

Never:
- mutate runtime artifacts, approvals, execution evidence, verdicts, or product files

Reads:
- AGENTS template, runtime kernel, operator cockpit, pipeline, command contracts, and tool versions

## Contract

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

Acts when:
- direct setup, health check, managed block, repository bootstrap orientation, or version check is requested

Owns:
- repository integration setup/checks only

Local stops:
- owner-specific entry evidence is missing, stale, contradictory, or out of scope

Writes:
- `AGENTS.md` managed block and setup surfaces only

Reads:
- `beo-reference -> assets/AGENTS.template.md`, `beo-reference -> references/operator-cockpit.md`, `beo-reference -> references/runtime-kernel.md`, `beo-reference -> registry/pipeline.json`, `beo-reference -> registry/command-contracts.json`, command contracts `python.version`, `br.version`, `bv.version`

Local forbids:
- runtime artifacts, approvals, execution evidence, verdicts, product files

Exits:
- `setup_complete` -> `done`
- `user_confirmation_needed` -> `user`

## Setup Operations

Setup may create or update the managed AGENTS block, check command contracts `python.version`, `br.version`, and `bv.version`, and explain usage. It must not create feature artifacts or runtime approval/evidence/verdicts.
