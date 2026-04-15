---
name: beo-reference
description: >-
  Use whenever a beo skill needs the canonical br/bv CLI command reference,
  status mapping, artifact protocol, slug handling, handoff/state format,
  approval rules, dependency reconciliation, or other shared workflow lookup
  tables. Load when a skill needs protocol docs not already referenced by path in its own instructions. If a
  beo skill says "use the canonical rule" or points to a shared reference, use
  this skill. Do not use for direct implementation work or when another beo
  skill already provides the needed reference inline.
---

<HARD-GATE>
Onboarding — see `references/shared-hard-gates.md` § Onboarding Check.
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

## Reference Index

Use this skill as a narrow lookup layer.
Read only the specific shared reference needed for the decision at hand unless a broader protocol conflict makes more context necessary.

**Cross-Cutting Gates:**
- `references/shared-hard-gates.md` — onboarding check, approval verification, multi-phase routing, context budget protocol, shared references convention

**CLI References:**
- `references/br-cli-reference.md` — exact `br` command syntax, flags, subcommands
- `references/bv-cli-reference.md` — exact `bv` command syntax for graph analytics or triage

**Status & State:**
- `references/status-mapping.md` — beo feature states ↔ `br` task statuses
- `references/state-and-handoff-protocol.md` — `STATE.json` / `HANDOFF.json` schema and field semantics
- `references/artifact-conventions.md#slug-lifecycle` — slug ID generation and validation

**Workflow Contracts:**
- `references/pipeline-contracts.md` — routing conditions, label lifecycle, skill handoff boundaries
- `references/approval-gates.md` — approval requirements and label ownership
- `references/dependency-and-scheduling.md` — bead dependency wiring and execution order
- `references/failure-recovery.md` — shared recovery rules for tool failures, malformed state, and resume corruption

**Artifacts & Files:**
- `references/artifact-conventions.md#artifact-protocol` — artifact storage conventions (`discovery.md`, `approach.md`, `plan.md`, etc.)
- `references/artifact-conventions.md#file-layout` — expected file locations and naming
- `references/bead-description-templates.md` — bead description format for `br` tasks

**Communication & Coordination:**
- `references/communication-standard.md` — agent output and inter-skill message format
- `references/agent-mail-coordination.md` — parallel worker coordination via agent mail
- `references/learnings-read-protocol.md` — prior learnings search and retrieval
- `references/worker-template.md` — canonical worker subagent spawn prompt for swarming and executing

**Knowledge Store:**
- `references/knowledge-store.md` — Obsidian/QMD knowledge store integration

## Planning-Aware Note

Shared references distinguish between:
- `approach.md` as the strategy artifact
- `phase-plan.md` as the optional whole-feature sequencing artifact
- `phase-contract.md` and `story-map.md` as **current-phase** artifacts

Use the shared references to avoid treating current-phase artifacts as whole-feature artifacts.

## Lookup Protocol

After resolving the lookup:
- state the canonical rule you found
- name the specific shared reference that supplied it when useful
- hand control back to the calling beo skill immediately

`beo-reference` is not the destination phase. It resolves the shared-rule question, then returns the caller to its own workflow.

## Canonical Ownership

The reference skill owns the single source of truth for **all 16 documents in `references/`**. Other skills MUST NOT duplicate protocol definitions — they should summarize briefly and point back here.

Any document listed in the Reference Index above is owned exclusively by this skill. If a reference doc and a local skill summary disagree, the reference doc wins.

## Maintenance Rule

Do not fork shared rules into individual skill bodies.
If a skill needs a shared rule, summarize it briefly and point back here.

## Red Flags & Anti-Patterns

- A skill duplicates a protocol table or status mapping instead of pointing to the reference doc
- A `br` or `bv` command in any skill uses flags not documented in the CLI reference
- STATE.json field semantics described outside `state-and-handoff-protocol.md`
- Status values used that don't appear in `status-mapping.md` or `pipeline-contracts.md` routing table
- Artifact paths that contradict `artifact-conventions.md`

## Handoff

After resolving the lookup, explicitly return to the calling beo skill and continue using the canonical rule you found here.
Prefer a concrete handback such as "Return to `beo-validating` and continue using `references/state-and-handoff-protocol.md` as the source of truth."
Do not leave duplicated or forked protocol text behind as a substitute for the shared source.

## Context Budget

Read only the specific reference file you need. If context usage exceeds 65%, prefer a narrow lookup and checkpoint using `references/state-and-handoff-protocol.md`.
