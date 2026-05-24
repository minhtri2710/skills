# BEO - Beads Execution Operator

BEO is a compact set of Claude skills and machine-checkable references for delivering one verified Beads issue at a time. It keeps delivery safe by separating planning, approval, execution, review, and learning authority instead of relying on ad hoc agent judgment.

## What lives here

| Path | Purpose |
| --- | --- |
| `skills/beo/*/SKILL.md` | Loadable owner contracts for each BEO role. |
| `beo-reference` -> `references/` | Canonical prose doctrine loaded narrowly as needed. |
| `beo-reference` -> `registry/` | Machine-readable contracts for pipeline, tickets, approvals, commands, and profiles. |
| `beo-reference` -> `scripts/...` | Deterministic helpers that check, recall, setup, and validate the control plane. |
| `beo-reference` -> `templates/` | Ticket templates for quick, standard, and strict work. |

## Workflow spine

Normal delivery remains intentionally small:

```text
beo-plan -> beo-validate -> beo-execute -> beo-review
```

Support and control-plane skills stay out of the normal path:

| Skill | Responsibility |
| --- | --- |
| `beo-debug` | Read-only diagnosis subroutine for execution/review blockers. |
| `beo-learn` | Selective success/failure case capture after accepted review or debug return. |
| `beo-author` | Edits BEO doctrine, registries, templates, and skill contracts. |
| `beo-setup` | Read-only integration health checks by default; memory maintenance requires explicit flags. |
| `beo-reference` | Read-only doctrine and registry loader. |

Canonical transition details live in `beo-reference` -> `registry/pipeline.json`.

## Authority boundaries

Keep one source of truth per decision:

- `br` owns issue identity, claims, comments, dependencies, lifecycle, ready queue, sync, and closure.
- `bv` robot mode is read-only graph orientation for triage, tracks, bottlenecks, and cycles.
- `TICKET.md` owns BEO safety state, approval projections, execution evidence, and review verdicts.
- `qmd` indexes and searches learning notes for advisory recall; Obsidian CLI writes durable learning notes. Neither grants `PASS_EXECUTE`, review verdicts, closure, or user authorization.

The full rules are in:

- `beo-reference` -> `references/kernel.md`
- `beo-reference` -> `references/lifecycle.md`
- `beo-reference` -> `references/safety.md`
- `beo-reference` -> `references/memory.md`
- `beo-reference` -> `registry/command-contracts.json`

## Common commands

Use `rtk` in front of shell commands when running through Claude Code.

```bash
# Validate BEO control-plane contracts
rtk python3 skills/beo/reference/scripts/beo_registry_check.py

# Check one ticket phase or lifecycle boundary
rtk python3 skills/beo/reference/scripts/beo_check.py --check validate --issue <issue-id>

# Read-only setup/integration health check
rtk python3 skills/beo/reference/scripts/beo_setup.py

# Explicit memory maintenance when authorized
rtk python3 skills/beo/reference/scripts/beo_setup.py --configure-memory
rtk python3 skills/beo/reference/scripts/beo_setup.py --refresh-memory-index

# Advisory recall for a Beads issue
rtk python3 skills/beo/reference/scripts/beo_recall.py --issue <issue-id>
```

## Learning loop

`beo-learn` records only reusable cases: recurring mistakes, failure patterns, near misses, cannot-deliver patterns, reusable debug diagnoses, or unusually valuable success patterns. Notes are written through Obsidian CLI when configured, fall back to issue-local markdown when needed, and may be indexed by `qmd` strictly as memory maintenance.

See `beo-reference` -> `references/memory.md` for the note contract and backend rules.

## Development checks

Before treating BEO control-plane edits as ready:

```bash
rtk python3 skills/beo/reference/scripts/beo_registry_check.py
rtk python3 -m compileall skills/beo/reference/scripts
rtk git diff --check
```
