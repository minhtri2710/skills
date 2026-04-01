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

# Beo Reference

Complete reference for the CLI-driven beo workflow. Load this skill when another beo skill says "see beo-reference" or when you need lookup tables for status mapping, artifact protocol, or CLI commands.

This skill is the canonical source for shared beo workflow conventions. When another beo skill and a shared protocol seem to disagree, reconcile against the reference files here rather than inventing a hybrid rule.

## Source of Truth Rule

Use this reference layer as the maintenance anchor for shared beo behavior.

- update shared protocol docs here before or alongside dependent skill summaries
- when a skill body and a shared protocol disagree, the shared protocol wins
- keep high-risk shared concepts centralized here: approval rules, status mapping, state/handoff shape, slug safety, artifact semantics, dependency conventions
- dependent skills should summarize these rules, not fork them

## Default Use Rule

Load `beo-reference` whenever another beo skill:
- says to use the canonical rule
- points to a shared protocol or lookup table
- depends on status mapping, slug safety, approval gates, handoff format, or artifact semantics

## Quick Routing Guide

- Need exact `br` syntax -> `references/br-cli-reference.md`
- Need exact `bv` syntax -> `references/bv-cli-reference.md`
- Need approval behavior -> `references/approval-gates.md`
- Need `STATE.md` / `HANDOFF.json` shape -> `references/state-and-handoff-protocol.md`
- Need task or epic status interpretation -> `references/status-mapping.md`
- Need artifact storage or read/write protocol -> `references/artifact-protocol.md`
- Need slug preservation or artifact path safety -> `references/slug-protocol.md`
- Need dependency or scheduling rules -> `references/dependency-and-scheduling.md`

## Planning-Aware Notes

The shared references now distinguish between:

- `approach.md` as the strategy artifact
- `phase-plan.md` as the optional whole-feature sequencing artifact for multi-phase work
- `phase-contract.md` and `story-map.md` as **current-phase** artifacts

When a feature is multi-phase, use the shared references to avoid treating current-phase artifacts as whole-feature artifacts.

## Quick Navigation

| Need | Reference File |
|------|---------------|
| Run a br command | `references/br-cli-reference.md` |
| Run a bv command | `references/bv-cli-reference.md` |
| Map task status to br commands | `references/status-mapping.md` |
| Read/write task artifacts | `references/artifact-protocol.md` |
| Use canonical Markdown templates for bead descriptions | `references/bead-description-templates.md` |
| Preserve and recover feature slugs | `references/slug-protocol.md` |
| Read/write STATE.md and HANDOFF.json safely | `references/state-and-handoff-protocol.md` |
| Read prior learnings before planning/debugging/validation | `references/learnings-read-protocol.md` |
| Apply canonical human approval rules | `references/approval-gates.md` |
| Sync dependencies or check scheduling | `references/dependency-and-scheduling.md` |
| Integrate with knowledge store | `references/knowledge-store.md` |
| Locate pipeline artifacts and state files | `references/file-conventions.md` |
| State routing, HANDOFF schema, label lifecycle, task enumeration | `references/pipeline-contracts.md` |

## Context Budget

This hub skill is low-overhead, but if context usage exceeds 65%, read only the specific reference file you need, then checkpoint using `references/state-and-handoff-protocol.md` instead of loading broad summaries.

## Anti-Patterns

- Do not fork shared rules into skill bodies; summarize and link back here.
