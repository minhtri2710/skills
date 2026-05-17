---
name: beo-setup
description: Sets up or checks BEO repository integration without starting feature delivery.
---

# beo-setup

Before acting, load and obey `beo-reference -> references/skill-contract-common.md`.

## Decision

Install, check, or explain repository integration.

## Enter

- Direct setup, health check, managed block, repository bootstrap orientation, or version check is requested.

## Owns

- Repository integration setup/checks only.

## Writes

- Target `AGENTS.md` BEO managed block and setup surfaces only.

## Stops

- Requested mutation is outside setup.
- target `AGENTS.md` contains partial, malformed, nested, or duplicate BEO managed markers.
- Target `AGENTS.md` has conflicting unmarked BEO instructions.

## Exits

- `setup_complete` -> `done`
- `user_confirmation_needed` -> `user`

## Method

1. Treat `beo-reference -> assets/AGENTS.template.md` as the exact managed-block payload.
2. Inspect the target repository `AGENTS.md` for BEO managed markers before editing:
   - if `AGENTS.md` is missing, create it from the template;
   - if `AGENTS.md` has partial, malformed, nested, or duplicate BEO managed markers, stop with `user_confirmation_needed`;
   - if `AGENTS.md` has exactly one valid BEO managed block, replace only that marker-delimited span;
   - if `AGENTS.md` has no BEO managed block but has unmarked BEO integration instructions, stop with `user_confirmation_needed`;
   - if `AGENTS.md` has no BEO managed block and no conflicting unmarked BEO integration instructions, append the template after a blank-line separator and preserve existing content.
3. Do not rewrite, normalize, or delete non-managed `AGENTS.md` content.
4. Use contracted setup commands for version checks.
5. Report setup result.
6. Do not start feature delivery; the user initiates `beo-explore`.
