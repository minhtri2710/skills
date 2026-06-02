# Artifact Boundaries

This file owns BEO artifact placement rules. Other files should cite this file instead of restating these boundaries.

## Canonical ownership

| Artifact | Owns | Must not own |
|---|---|---|
| `br` | issue lifecycle, status, claims, dependencies, comments, ready queue, closure | BEO approval/execution/review internals |
| `bv` | read-only graph orientation | persisted lifecycle state, approval, verdict |
| `TICKET.yaml` | request, done criteria, approved scope, verification commands, risk/strict contracts | br lifecycle, approval state, execution state, review verdict, runtime event log, learning notes |
| `state.json` | approval, execution, review state | request/scope definition, br lifecycle, memory notes |
| `runtime-events.jsonl` | append-only non-normal events | normal successful transitions |
| qmd/Obsidian notes | advisory reusable lessons | approval, execution permission, verdict, closure, Human Gate authorization |
| `AGENTS.md` managed block | compact repo-level reminder | detailed BEO doctrine |

## Do not put

- Beads lifecycle/status in `TICKET.yaml`.
- `bv` triage ranking in `TICKET.yaml` or `state.json`.
- normal transitions in `runtime-events.jsonl`.
- approval state or review verdict in `TICKET.yaml`.
- learning notes in `beo-reference`.
- secrets, credentials, or customer-sensitive raw data in memory notes.
- product delivery decisions in `beo-setup`, `beo-reference`, or `beo-author`.
