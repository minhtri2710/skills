# Default Reads for Delivery Skills

> All four delivery skills (`beo-plan`, `beo-validate`, `beo-execute`, `beo-review`) load these by default. Per-skill extras are listed in each skill's `## Read` section.

## Common reads

- `br show <issue-id> --json`
- `.beads/artifacts/<issue-id>/TICKET.json` (read or authored, depending on phase)
- `.beads/artifacts/<issue-id>/state.json`
- `.beads/artifacts/<issue-id>/runtime-events.jsonl` when present
- `beo-reference -> registry/pipeline.json` for emitted route
- `beo-reference -> registry/runtime-event.schema.json` before appending runtime events

## Out of scope

Skill-specific extras stay in their owning skill's Read section. Do not move
`PLAN.md` audit reads, registry-specific gates, or strict-mode helpers here
— the per-skill Read section is the only authoritative pointer to phase-specific
inputs.
