---
name: beo-reference
description: >-
  Use whenever a beo skill needs the canonical br/bv CLI command reference,
  status mapping, artifact protocol, slug handling, handoff/state format,
  approval rules, dependency reconciliation, or other shared workflow lookup
  tables. Load when a skill needs protocol docs not already referenced by path in its own instructions. If a
  beo skill says "use the canonical rule" or points to a shared reference, use
  this skill.
---

<HARD-GATE>
If `.beads/onboarding.json` is missing or stale, stop and load `beo-using-beo` before continuing.
</HARD-GATE>

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

## Quick Routing Guide

- exact `br` syntax -> `references/br-cli-reference.md`
- exact `bv` syntax -> `references/bv-cli-reference.md`
- approval behavior -> `references/approval-gates.md`
- `STATE.json` / `HANDOFF.json` shape -> `references/state-and-handoff-protocol.md`
- task or epic status interpretation -> `references/status-mapping.md`
- artifact storage or read/write protocol -> `references/artifact-protocol.md`
- slug preservation and artifact path safety -> `references/slug-protocol.md`
- dependency and scheduling rules -> `references/dependency-and-scheduling.md`
- current-phase artifact and pipeline semantics -> `references/pipeline-contracts.md`
- artifact locations, directory layout, file paths -> `references/file-conventions.md`
- Obsidian/QMD knowledge store integration -> `references/knowledge-store.md`
- bead description format and templates -> `references/bead-description-templates.md`
- learnings search and retrieval workflow -> `references/learnings-read-protocol.md`
- multi-agent coordination and Agent Mail -> `references/agent-mail-coordination.md`
- shared communication conventions -> `references/communication-standard.md`

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


## Canonical Ownership

The reference skill owns the single source of truth for all shared protocol documents. Other skills MUST NOT duplicate protocol definitions — they should point here instead.

| Document | Owns |
|---|---|
| `br-cli-reference.md` | All `br` command syntax and flags |
| `bv-cli-reference.md` | All `bv` command syntax and flags |
| `status-mapping.md` | Task and feature state machines |
| `pipeline-contracts.md` | Routing table, artifact hierarchy, slug rules |
| `state-and-handoff-protocol.md` | STATE.json schema and field semantics |
| `artifact-protocol.md` | Artifact naming and storage conventions |
| `slug-protocol.md` | Slug lifecycle procedures |
| `approval-gates.md` | Approval label rules and back-edge removal |
| `dependency-and-scheduling.md` | Task dependency wiring and scheduling |
| `file-conventions.md` | `.beads/` directory layout |
| `communication-standard.md` | Agent-to-agent message format |
| `agent-mail-coordination.md` | Agent mail delivery protocol |
| `bead-description-templates.md` | Bead description format |
| `learnings-read-protocol.md` | How skills read learnings |

## Red Flags

- A skill duplicates a protocol table or status mapping instead of pointing to the reference doc
- A `br` or `bv` command in any skill uses flags not documented in the CLI reference
- STATE.json field semantics described outside `state-and-handoff-protocol.md`
- Status values used that don't appear in `status-mapping.md` or `pipeline-contracts.md` routing table
- Artifact paths that contradict `file-conventions.md`

## Handoff

After resolving the lookup, explicitly return to the calling beo skill and continue using the canonical rule you found here.
Prefer a concrete handback such as "Return to `beo-validating` and continue using `references/state-and-handoff-protocol.md` as the source of truth."
Do not leave duplicated or forked protocol text behind as a substitute for the shared source.

## Context Budget

Read only the specific reference file you need when possible.
If context usage exceeds 65%, prefer a narrow lookup and checkpoint using `references/state-and-handoff-protocol.md` instead of loading broad summaries.
