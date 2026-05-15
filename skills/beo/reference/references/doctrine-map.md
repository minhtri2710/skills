# Doctrine Map

Authority: canonical map of BEO doctrine homes and surface classes.

## Surface classes

| Class | Meaning |
|---|---|
| Canonical | May define workflow authority. |
| Generated | Derived/advisory only; must cite canonical sources and introduce no new rule. |
| Advisory | Orientation only; cannot grant authority. |
| Template | Seed content only; cannot override canonical sources. |

Generated/advisory/template files must not duplicate canonical rules unless they explicitly cite the canonical source and are marked non-authoritative.

## Canonical homes

| Concern | Canonical home | May be summarized elsewhere? |
|---|---|---|
| Reference navigation | `references/README.md` | summary only |
| Operator navigation and read order | `references/operator-cockpit.md` | summary only |
| Normal resume owner orientation | `references/resume-resolution.md` | summary only |
| Operator terminology | `references/glossary.md` | summary only |
| Runtime invariants | `references/runtime-kernel.md` | yes, summary only |
| Runtime artifact loading | `references/loading.md` | summary only |
| Execution ledger | `references/execution-ledger.md` | summary only |
| Context-loss survival | `references/context-management.md` | summary only |
| Feature lifecycle | `references/lifecycle.md` | summary only |
| Owner common contract | `references/skill-contract-common.md` | no verbatim duplicate |
| Transition topology | `registry/pipeline.json` | no duplicate topology |
| Owner and utility classification | `registry/vocabulary.json` | no duplicate enum lists outside generated summaries |
| Registry shape schema | `registry/registry.schema.json` | no prose duplicate of machine fields |
| Core runtime vocabulary/enums | `registry/vocabulary.json` | no duplicate enum lists outside generated summaries |
| Learning extension vocabulary | `registry/learning-vocabulary.json` | no duplicate enum lists outside generated summaries |
| Artifact density/ownership/human shape | `references/artifacts.md` | summary only |
| Artifact machine schema | `registry/artifact-schemas.json` | no prose duplicate of machine fields |
| Approval model and helper authority | `references/approval.md` | summary only |
| Approval envelope fields | `registry/approval-envelope.json` | no prose duplicate of machine fields |
| State and handoff semantics | `references/state.md` | summary only |
| Decision boundaries, go-mode, Human Gates | `references/decision-boundaries.md` | location references only |
| Unsafe identity repair and meta-target semantics | `references/route-resolution.md` | summary only |
| Compact operator form | `assets/operator-forms/compact-ticket.md` advisory only | summary only |
| Command authority | `registry/command-contracts.json` | no duplicate command tables outside generated summaries |
| Helper output schema | `registry/helper-output-schema.json` | no prose duplicate of machine fields |
| Learning extension | `references/learning.md` | summary only |
| Skill authoring | `../../author/SKILL.md` | summary only |

## Duplication rule

A non-canonical surface may summarize a rule only when:

1. it names the canonical source;
2. it does not add conditions;
3. it does not restate machine fields verbatim unless generated from the machine source;
4. it cannot be used as fallback authority.

## No fallback authority

Removed or merged surfaces must not be kept as advisory fallback. Use only the canonical homes listed above.
