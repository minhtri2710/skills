---
name: beo-reference
description: |
  Use when another beo skill needs one specific canonical support document such as a protocol, contract, convention, gate, status map, scheduling rule, recovery rule, knowledge-store rule, communication standard, or CLI reference. Reference resolves and exposes only the targeted file. Do not use as a pipeline phase, routing target, or behavioral skill.
---

# beo-reference

Canonical shared reference corpus for beo skills.

This skill is lookup-only. It exists so other beo skills can cite `beo-reference` → `references/<file>` and load exactly the protocol document they need.

## Atomic purpose
Provide one targeted canonical reference document to a beo skill.

## Inputs
**Required**
- the specific reference document path or name needed by the calling skill

## Outputs
**Allowed reads only**
- targeted reference resolution from `references/<file>`

**Must not write**
- `STATE.json`
- `HANDOFF.json`
- feature artifacts
- implementation code

## Boundary rules
- `beo-reference` is not a routing destination.
- `beo-reference` does not make decisions, write state, edit artifacts, or perform feature work.
- Callers should load only the specific reference file they need, not the full corpus.

## Reference index
### CLI references
- `references/br-cli-reference.md` — canonical `br` command usage
- `references/bv-cli-reference.md` — canonical `bv` command usage

### Status and state
- `references/status-mapping.md` — canonical bead states and transitions
- `references/state-and-handoff-protocol.md` — `STATE.json` and `HANDOFF.json` schema and resume rules

### Artifacts
- `references/artifact-conventions.md` — artifact paths, ownership, and naming
- `references/bead-description-templates.md` — standard bead description formats

### Workflow protocols
- `references/pipeline-contracts.md` — routing table, allowed transitions, cross-skill invariants
- `references/approval-gates.md` — approval timing and label ownership
- `references/dependency-and-scheduling.md` — dependency reconciliation and scheduling cascade
- `references/failure-recovery.md` — failure classes and recovery rules
- `references/shared-hard-gates.md` — shared onboarding, session-boundary, and interaction rules
- `references/worker-template.md` — standard worker prompt template

### Knowledge and communication
- `references/knowledge-store.md` — knowledge-store rules and integration
- `references/learnings-read-protocol.md` — reading learnings and critical patterns safely
- `references/communication-standard.md` — communication rules for beo outputs
- `references/agent-mail-coordination.md` — coordinator / worker messaging protocol

## Red flags
- routing to `beo-reference`
- loading the entire corpus instead of one needed file
- treating reference docs as permission to change pipeline ownership
