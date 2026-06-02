---
name: beo-setup
description: "Check or configure BEO readiness. br is required; bv, qmd, and Obsidian are optional degraded tools. Setup writes require explicit user authorization."
---
# beo-setup

## Read

- The explicit setup or health-check request
- `beo-reference -> references/degraded-tools.md`
- Existing environment variables relevant to BEO memory only when needed

## Setup modes

- `check`: read-only readiness report; default mode.
- `configure-memory`: authorized qmd/Obsidian/local learning setup.
- `explain-degraded`: explain missing optional tools.

Any write requires explicit user authorization.

## Do

1. Report required tool readiness separately from optional degraded tools.
2. Treat missing `br` or artifact parsing dependencies as blocking.
3. Treat missing `bv`, qmd, or Obsidian as degraded, not blocking.
4. Require explicit user authorization before setup writes or memory/index configuration.

## Write

- No delivery artifacts.
- Local learning directory or qmd/Obsidian setup only when explicitly authorized.
- Setup status output only by default.

## Emit

- `setup_complete`
- `setup_degraded`
- `setup_blocked`
- `user_confirmation_needed`

## Never

- Do not grant approval or review verdicts.
- Do not mutate product files.
- Do not close issues.
- Do not make qmd/Obsidian authoritative.
