---
name: beo-onboard
description: |
  Verify and repair managed beo startup surfaces. Use when onboarding freshness is false, managed bootstrap surfaces are missing/invalid, or repair is requested. Do not use when doctrine edits are requested.
---

# beo-onboard

## Purpose
Verify and repair managed beo startup surfaces.

## Primary owned decision
Decide whether managed startup is current and repair only managed surfaces.

## Enter when
- onboarding freshness is false
- required managed bootstrap surfaces are missing or invalid
- the user explicitly requests onboarding repair

## Writable surfaces
- managed startup surfaces described by `references/onboarding-flow.md`, including `AGENTS.md` managed block and `.beads/onboarding.json`
- `.beads/beo_status.mjs` and `.beads/critical-patterns.md` only as allowed by `references/onboarding-flow.md`
- `.beads/artifacts/` only for managed directory, placeholder, or index creation marked by `references/onboarding-flow.md`
- `.beads/learnings/` only for managed directory, placeholder, or index creation marked by `references/onboarding-flow.md`
- shared `STATE/HANDOFF` surfaces under `beo-references -> skill-contract-common.md`

## Decision packet
- shared decision packet under `beo-references -> skill-contract-common.md`
- no local packet extensions beyond managed repair evidence in owned startup surfaces

## Managed repair limits
- create managed directories, placeholders, or indexes only when `references/onboarding-flow.md` marks them as managed
- never write feature-specific artifact or learning content here
- never overwrite parseable live state with guessed bootstrap values

## Allowed next owners
- beo-route
- user

## Local hard stops
- Do not rewrite feature-specific artifact content under the pretense of onboarding repair.
- Do not overwrite parseable live state with guessed bootstrap values.
- Do not edit doctrine files here.

## References
- `beo-references -> operator-card.md`
- `beo-references -> state.md`
- `beo-references -> artifacts.md`
- `beo-references -> pipeline.md`
- `references/onboarding-flow.md`
