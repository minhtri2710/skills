---
name: beo-reference
description: >-
  Use whenever a beo skill needs the canonical br/bv CLI command reference,
  status mapping, artifact protocol, slug handling, handoff/state format,
  approval rules, dependency reconciliation, or other shared workflow lookup
  tables. Load alongside any beo skill that references shared protocols. If a
  beo skill says "use the canonical rule" or points to a shared reference, use
  this skill.
---

> **Onboarding gate:** If `.beads/onboarding.json` is missing or stale, stop and load `beo-using-beo` before continuing.

# Beo Reference

## Overview

This is the shared reference layer for beo.
Load it when another beo skill points to canonical rules, lookup tables, or shared protocol docs.

**Core principle:** shared canonical references win over local summaries when they disagree.

## Source of Truth Rule

<HARD-GATE>
When a local skill summary and a shared protocol appear to disagree, the shared reference wins.
Do not invent a hybrid rule.
</HARD-GATE>

Keep high-risk shared concepts centralized here:
- approval behavior
- status mapping
- handoff and state shape
- slug safety
- artifact semantics
- dependency conventions

Dependent skills should summarize these rules, not fork them.

## When to Load `beo-reference`

Load this skill whenever another beo skill:
- says to use the canonical rule
- points to a shared protocol or lookup table
- needs approval gates, slug safety, handoff format, artifact semantics, or status interpretation

## Quick Routing Guide

- exact `br` syntax -> `references/br-cli-reference.md`
- exact `bv` syntax -> `references/bv-cli-reference.md`
- approval behavior -> `references/approval-gates.md`
- `STATE.md` / `HANDOFF.json` shape -> `references/state-and-handoff-protocol.md`
- task or epic status interpretation -> `references/status-mapping.md`
- artifact storage or read/write protocol -> `references/artifact-protocol.md`
- slug preservation and artifact path safety -> `references/slug-protocol.md`
- dependency and scheduling rules -> `references/dependency-and-scheduling.md`
- current-phase artifact and pipeline semantics -> `references/pipeline-contracts.md`
- artifact locations, directory layout, file paths -> `references/file-conventions.md`
- Obsidian/QMD knowledge store integration -> `references/knowledge-store.md`
- bead description format and templates -> `references/bead-description-templates.md`
- learnings search and retrieval workflow -> `references/learnings-read-protocol.md`

## Planning-Aware Note

Shared references distinguish between:
- `approach.md` as the strategy artifact
- `phase-plan.md` as the optional whole-feature sequencing artifact
- `phase-contract.md` and `story-map.md` as **current-phase** artifacts

Use the shared references to avoid treating current-phase artifacts as whole-feature artifacts.

## Process

Use this skill as a narrow lookup layer.
Read only the specific shared reference needed for the decision at hand unless a broader protocol conflict makes more context necessary.

After resolving the lookup:
- state the canonical rule you found
- name the specific shared reference that supplied it when useful
- hand control back to the calling beo skill immediately

`beo-reference` is not the destination phase. It resolves the shared-rule question, then returns the caller to its own workflow.

## Maintenance Rule

Do not fork shared rules into individual skill bodies.
If a skill needs a shared rule, summarize it briefly and point back here.

## Handoff

After resolving the lookup, explicitly return to the calling beo skill and continue using the canonical rule you found here.
Prefer a concrete handback such as "Return to `beo-validating` and continue using `references/state-and-handoff-protocol.md` as the source of truth."
Do not leave duplicated or forked protocol text behind as a substitute for the shared source.

## Context Budget

Read only the specific reference file you need when possible.
If context usage exceeds 65%, prefer a narrow lookup and checkpoint using `references/state-and-handoff-protocol.md` instead of loading broad summaries.
