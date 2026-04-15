---
name: beo-using-beo
description: >-
  Bootstrap and onboarding gate for the beo workflow. Use when a repository
  needs beo onboarding, when onboarding status must be checked, or when another
  beo skill reports that onboarding is missing or stale. Use for prompts like
  "onboard this repo", "set up beo", or "check beo status". Do not use it
  when the repository is already onboarded and current.
---

# Beo Using Beo

## Overview

Ensure the target repository has the required `.beads/` structure and managed `AGENTS.md` block before any other beo skill proceeds.
> See `../reference/references/shared-hard-gates.md` § Shared References Convention.


`beo-router` loads this skill when onboarding is missing or stale.

## Hard Gates

<HARD-GATE>
Do not continue into any other beo skill until onboarding completes.
</HARD-GATE>

<HARD-GATE>
After onboarding, hand back to `beo-router`. Do not route directly to exploring, planning, or execution.
</HARD-GATE>

<HARD-GATE>
Do not rerun onboarding when `.beads/onboarding.json` exists and matches the current onboarding version.
</HARD-GATE>

## Script Location

The onboarding script lives at `scripts/onboard_beo.mjs` inside this skill package.
Resolve the absolute path from the installed skill directory before running it.
Use standalone Node.js; no npm dependencies.
When onboarding is current, it also installs the repo-local scout command `.beads/beo_status.mjs`.

## Onboarding Flow

1. Verify `node --version` is `>=18`. If not, stop and tell the user onboarding cannot run yet.
2. Run a dry check:
   `node <skill-path>/scripts/onboard_beo.mjs --repo-root <repo-root>`
3. Use the script-level `status` field from the JSON response, not a STATE.json routing state:

   | Status | Action |
   | --- | --- |
   | `"needs_onboarding"` | Summarize actions and ask for approval. |
   | `"up_to_date"` | Optionally run `node <repo-root>/.beads/beo_status.mjs --json` for a quick scout, then hand back to `beo-router`. |

4. If the script errors or returns an unexpected status, surface the raw error output, do not proceed, and ask whether to inspect prerequisites (Node version, filesystem permissions) or the script itself.
5. Apply onboarding when approved:
   `node <skill-path>/scripts/onboard_beo.mjs --repo-root <repo-root> --apply`

| File | Use for |
| --- | --- |
| `references/onboarding-flow.md` | Full decision matrix, write surface, and JSON schemas. |
| `../reference/references/failure-recovery.md` | Malformed state files, failed artifact writes, or missing `br`/`bv` prerequisites surfaced during bootstrap checks. |

## Handoff

After onboarding is confirmed, hand back to `beo-router` for normal phase detection and routing.
Do not route directly to downstream beo skills.

## Context Budget

`beo-using-beo` uses a **30%** threshold, not the standard 65%, because it is a lightweight bootstrap skill. If context usage exceeds 30%, stop and check whether the onboarding script should do more of the work.

## Red Flags & Anti-Patterns

- Skipping onboarding checks and jumping straight into the pipeline
- Running onboarding again when the repository is already current
- Manually writing `.beads/onboarding.json` instead of using the script
