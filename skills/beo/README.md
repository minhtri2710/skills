# BEO Skills

BEO is a repo-local skill package for Beads-backed delivery. Use these skills as one coordinated workflow, not as isolated standalone exports.

> [!IMPORTANT]
> **Primary Navigation:** Use the [BEO Doctrine Map](file:///Users/beowulf/Work/personal/beo-skills/skills/beo/reference/references/doctrine-map.md) as the primary entry point to locate core references, registries, and helper scripts.

## Canonical authority

- `reference/registry/pipeline.json` owns legal transitions and condition IDs.
- `reference/registry/command-contracts.json` owns command argv and authority boundaries.
- `reference/registry/*.json` owns machine-readable workflow, profile, ticket, approval, reservation, and command contracts.
- `reference/references/*.md` explains shared doctrine and invariants.
- Individual `SKILL.md` files are operator cards; they route agents to canonical registry/doctrine instead of duplicating it.

## Routing guide

| Situation | Load |
| --- | --- |
| Select, decompose, or scope one Beads issue | `beo-plan` |
| Decide whether a planned ticket may execute | `beo-validate` |
| Implement the approved scope | `beo-execute` |
| Audit execution, accept, close, or route repair | `beo-review` |
| Diagnose one blocker for execute/review without patching | `beo-debug` |
| Persist a reusable post-review/debug lesson | `beo-learn` |
| Maintain BEO doctrine, registries, templates, scripts, or skill contracts | `beo-author` |
| Check/install BEO tooling or authorized memory/qmd/Obsidian setup | `beo-setup` |
| Look up BEO doctrine, registries, templates, or command contracts read-only | `beo-reference` |

## Operating rules

- Work one claimed Beads issue at a time.
- Use one BEO delivery owner at a time: plan -> validate -> execute -> review.
- An emit is not an automatic handoff. After emitting a condition, stop and load the next owner before further action.
- Do not load multiple BEO delivery skills in the same turn for the same issue.
- `br` owns issue lifecycle; `bv` is read-only robot-mode graph orientation; qmd and Obsidian memory are advisory only.

## Directory names

Skill folders use short repo-local names (`plan`, `validate`, `execute`, etc.) while canonical skill names remain `beo-*`. See `manifest.json` for the machine-readable mapping.
