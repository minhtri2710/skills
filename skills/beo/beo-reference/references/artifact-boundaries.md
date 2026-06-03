# Artifact Boundaries

> [!NOTE]
> This reference is subordinate to [references/kernel.md](file:///Users/beowulf/Work/personal/beo-skills/skills/beo/beo-reference/references/kernel.md). `references/kernel.md` is the canonical owner of BEO rules and invariants.

This file owns BEO artifact placement rules. Other files should cite this file instead of restating these boundaries.

## Canonical ownership

| Artifact | Owns | Must not own |
|---|---|---|
| `br` | issue lifecycle, status, claims, dependencies, comments, ready queue, closure | BEO approval/execution/review internals |
| `bv` | read-only graph orientation | persisted lifecycle state, approval, verdict |
| `PLAN.md` | parent epic/feature requirement intake, clarification record, recommended assumptions, goals, non-goals, overall completion criteria, constraints, risks, verification strategy, decomposition strategy, proposed atomic child beads with suggested mode/risk, dependency graph, and unresolved user/operator decisions that block `plan_validated` until resolved | approval state, execution state, review verdict, product implementation, atomic ticket scope authority |
| `TICKET.yaml` | request, done criteria, approved scope, verification commands, risk/strict contracts | br lifecycle, approval state, execution state, review verdict, runtime event log, learning notes |
| `state.json` | approval, execution, review state | request/scope definition, br lifecycle, memory notes |
| `runtime-events.jsonl` | append-only non-normal events | normal successful transitions |
| qmd/Obsidian notes | advisory reusable lessons | approval, execution permission, verdict, closure, Human Gate authorization |
| `AGENTS.md` managed block | compact repo-level reminder | detailed BEO doctrine |

## Do not put

- Beads lifecycle/status in `TICKET.yaml`.
- `bv` triage ranking in `TICKET.yaml` or `state.json`.
- epic brainstorm notes or proposed child-bead backlog in `TICKET.yaml`; put them in `.beads/artifacts/<issue-id>/PLAN.md`.
- atomic approval fields in `PLAN.md`; parent plans guide decomposition but never grant `PASS_EXECUTE`.
- parent epic/feature brainstorming in child `TICKET.yaml`; child Beads descriptions or decomposition comments should link back to the parent `PLAN.md`. Do not add a new parent/plan field to `TICKET.yaml` because `registry/ticket.schema.json` is closed with `additionalProperties: false`.
- normal transitions in `runtime-events.jsonl`.
- approval state or review verdict in `TICKET.yaml`.
- learning notes in `beo-reference`.
- secrets, credentials, or customer-sensitive raw data in memory notes.
- product delivery decisions in `beo-setup`, `beo-reference`, or `beo-author`.
