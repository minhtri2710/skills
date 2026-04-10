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

`beo-using-beo` is the bootstrap spoke.
It ensures the target repository has the required `.beads/` structure and the managed `AGENTS.md` block before any other beo skill proceeds.

`beo-router` loads this skill when onboarding is missing or stale.

## Hard Gates

<HARD-GATE>
If onboarding is not complete, do not continue into any other beo skill.
</HARD-GATE>

<HARD-GATE>
After onboarding finishes, hand back to `beo-router`. Do not route directly to exploring, planning, or execution.
</HARD-GATE>

<HARD-GATE>
Do not rerun onboarding when `.beads/onboarding.json` already exists and matches the current onboarding version.
</HARD-GATE>

## Script Location

The onboarding script lives at `scripts/onboard_beo.mjs` inside this skill package.
Resolve the absolute path from the installed skill directory before running it.
The script is standalone Node.js and has no npm dependencies.
When onboarding is current, it also installs the repo-local scout command `.beads/beo_status.mjs`.

## Onboarding Flow

1. Verify `node --version` is `>=18`. If not, stop and tell the user onboarding cannot run yet.
2. Run a dry check:
   - `node <skill-path>/scripts/onboard_beo.mjs --repo-root <repo-root>`
   - if the result is `needs_onboarding`, summarize the actions and ask for approval
   - if the result is `up_to_date`, optionally run `node <repo-root>/.beads/beo_status.mjs --json` for a quick scout, then hand back to `beo-router`
3. Apply onboarding when approved:
   - `node <skill-path>/scripts/onboard_beo.mjs --repo-root <repo-root> --apply`

For the full decision matrix, write surface, and JSON schemas, see `references/onboarding-flow.md`.

## Handoff

After onboarding is confirmed, hand back to `beo-router` for normal phase detection and routing.
Do not route directly to downstream beo skills from here.

## Context Budget

`beo-using-beo` should stay small and procedural.
If context usage exceeds 30% during onboarding, stop and check whether the script should be doing more of the work.
The 30% threshold (vs. the standard 65%) is intentional: this is a bootstrap skill that delegates heavy work to `onboard_beo.mjs`, so high context consumption signals logic leaking out of the script.

## Red Flags & Anti-Patterns

- Skipping onboarding checks and jumping straight into the pipeline
- Running onboarding again when the repository is already current
- Manually writing `.beads/onboarding.json` instead of using the script
- Routing directly to another beo skill instead of handing back to `beo-router`
