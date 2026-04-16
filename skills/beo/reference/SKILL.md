---
name: beo-reference
description: |
  Use when a beo skill needs canonical protocol documents: CLI references, status mapping, artifact conventions, state/handoff protocol, pipeline contracts, approval gates, dependency scheduling, failure recovery, knowledge store, or communication standards. Read individual reference documents as needed — do not co-load this entire corpus. Use this index to locate the specific shared reference files that beo skills depend on.
---

# beo-reference

Shared reference corpus for all beo skills. **This is not a behavioral skill — it provides canonical protocol documents only.** This corpus is not a routing target. No skill should hand off to `beo-reference`; it exists only as an index for locating shared protocol documents.


Shared reference corpus for all beo skills. **This is not a behavioral skill — it provides canonical protocol documents that other skills reference by name.**

> **Convention**: Other skills reference these documents as `beo-reference` → `references/<file>`. Load this skill to resolve those references.

## CLI References

| Document | Path | Purpose |
|----------|------|---------|
| br CLI Reference | `references/br-cli-reference.md` | Canonical br command syntax and usage |
| bv CLI Reference | `references/bv-cli-reference.md` | Canonical bv command syntax and usage |

## Status & State

| Document | Path | Purpose |
|----------|------|---------|
| Status Mapping | `references/status-mapping.md` | 8 bead states, allowed transitions, terminal states |
| State & Handoff Protocol | `references/state-and-handoff-protocol.md` | STATE.json and HANDOFF.json schemas, write timing, resume protocol |

## Artifacts

| Document | Path | Purpose |
|----------|------|---------|
| Artifact Conventions | `references/artifact-conventions.md` | Artifact types, paths, slugs, read/write ownership |
| Bead Description Templates | `references/bead-description-templates.md` | Standard bead description formats |

## Workflow Protocols

| Document | Path | Purpose |
|----------|------|---------|
| Pipeline Contracts | `references/pipeline-contracts.md` | State routing table, skill transitions, cross-skill invariants |
| Approval Gates | `references/approval-gates.md` | 6 approval moments, label ownership matrix |
| Dependency & Scheduling | `references/dependency-and-scheduling.md` | Reconciliation procedure, scheduling cascade |
| Failure Recovery | `references/failure-recovery.md` | 5 failure classes, recovery rules |
| Shared Hard Gates | `references/shared-hard-gates.md` | Onboarding, approval verification, context budget |
| Worker Template | `references/worker-template.md` | Standard worker prompt template for execute/swarm |

## Knowledge Store

| Document | Path | Purpose |
|----------|------|---------|
| Knowledge Store | `references/knowledge-store.md` | Knowledge hierarchy, Obsidian integration |
| Learnings Read Protocol | `references/learnings-read-protocol.md` | How skills read learnings and critical-patterns |

## Communication

| Document | Path | Purpose |
|----------|------|---------|
| Communication Standard | `references/communication-standard.md` | User communication format and rules |
| Agent Mail Coordination | `references/agent-mail-coordination.md` | Inter-agent messaging protocol for swarm/execute |