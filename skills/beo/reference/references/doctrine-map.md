# Doctrine Map

Authority: canonical map of BEO doctrine homes. It maps topics to sources; it does not restate their rules.

## Canonical homes

| Topic | Canonical home | Notes |
|---|---|---|
| Reference index and tiers | `references/README.md` | Navigation only |
| Global protocol invariants | `references/protocol-core.md` | No owner-specific details |
| Shared owner contract | `references/skill-contract-common.md` | Loaded by every owner |
| Legal transitions | `registry/pipeline.json` | Only transition topology |
| Artifact ownership and prose shape | `references/artifacts.md` | Human-readable ownership and density shape |
| Artifact machine shape | `registry/artifact-schemas.json` | Schemas and shared shapes |
| Approval semantics | `references/approval.md` | Validate-owned authority |
| Approval envelope fields | `registry/approval-envelope.json` | Machine-readable approval contract |
| Transition provenance and meta-targets | `references/transition-provenance.md` | `return_to_caller`, `restored_owner`, handoff provenance |
| STATE/HANDOFF mirrors | `references/state.md` | Mirrors and contradiction rules |
| Lifecycle, closure, reopen, abandonment | `references/lifecycle.md` | Human-readable lifecycle narrative |
| Human Gates and ask/assume posture | `references/decision-boundaries.md` | Gate semantics and missing-user-input boundary |
| Artifact density | `references/density.md` | Compact/single-ticket vs full selection |
| Operator dashboard | `references/operator-cockpit.md` | Quick routing, no new authority |
| Operator explanation | `references/operator-guide.md` | Examples and explanations only |
| Read-only resume orientation | `references/resume-resolution.md` | Writes nothing |
| Unsafe identity repair | `references/route-resolution.md` | Route algorithm only |
| Runtime artifact loading/reload | `references/loading.md` | Reload timing |
| Context-loss survival | `references/context-management.md` | Resume inputs and output handling |
| Execution ledger model | `references/execution-ledger.md` | Full-density execution state |
| Learning record boundary | `references/learning.md` | Post-runtime learning capture |
| Runtime vocabulary | `registry/vocabulary.json` | Runtime enums only |
| Style wording policy | `registry/style-policy.json` | Non-authoritative aliases and preferred terms |
| Learning extension vocabulary | `registry/learning-vocabulary.json` | Learning enums |
| Command authority | `registry/command-contracts.json` | Contracted commands |
| Helper output fields | `registry/helper-output-schema.json` | Helper JSON shape |
| Glossary terms | `references/glossary.md` | Terminology only |
| Compact minimal operator form | `assets/compact-ticket.min.md` | Advisory drafting aid |
| Compact reference operator form | `assets/compact-ticket.reference.md` | Advisory examples |
| Skill authoring | `../../author/SKILL.md` | Doctrine editing boundary |

## Canonical-home rule

If two files disagree, the canonical home wins. If a rule appears in two canonical homes, one home must be demoted to a pointer.

## Duplication rule

Non-canonical surfaces may summarize a rule only when they name the canonical source, add no conditions, do not restate machine fields as fallback authority, and cannot be used as fallback authority.
