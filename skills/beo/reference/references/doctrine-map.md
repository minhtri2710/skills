# BEO Doctrine Map

Use this map to choose the narrowest BEO reference for a question. Load `kernel.md` first when safety invariants matter, then load only the specific file or registry needed.

## Core references

- `kernel.md`: core invariants, authority split, normal delivery path, and hard stops.
- `lifecycle.md`: `br`/`bv` authority, claim sequence, decomposition, runtime events, sync boundary, and labels.
- `safety.md`: execution modes, mutation safety, path containment, path reservation, external side effects, and approval lifecycle.
- `memory.md`: advisory `qmd` recall, Obsidian learning persistence, fallback learning notes, and non-authority rules.
- Ticket schema and templates: use `registry/ticket-schema.json`, `registry/approval-envelope.json`, and `templates/TICKET.*.md` directly.

## Machine contracts

- `beo-reference` -> `registry/pipeline.json`: legal delivery, support, post-hook, and maintenance transitions.
- `beo-reference` -> `registry/profiles.json`: quick, standard, and strict mode requirements.
- `beo-reference` -> `registry/ticket-schema.json`: `TICKET.md`, `state.json`, and `runtime-events.jsonl` field ownership.
- `beo-reference` -> `registry/approval-envelope.json`: approval projection and freshness binding.
- `beo-reference` -> `registry/command-contracts.json`: allowed command shapes and command authority.
- `beo-reference` -> `registry/reservation-schema.json`: path reservation record shape.
- `beo-reference` -> `registry/registry.schema.json`: lightweight registry schema anchor.

## Helper entry points

- `beo-reference` -> `scripts/beo_check.py`: identity, validation, execution, review, and status evidence checks.
- `beo-reference` -> `scripts/beo_reservation.py`: path reservation reserve/check/renew/release/gc/list.
- `beo-reference` -> `scripts/beo_state.py`: locked `state.json` and runtime event updates.
- `beo-reference` -> `scripts/beo_recall.py`: advisory memory recall.
- `beo-reference` -> `scripts/beo_memory_write.py`: learning note persistence with Obsidian fallback.
- `beo-reference` -> `scripts/beo_setup.py`: setup and optional memory index maintenance.
- `beo-reference` -> `scripts/beo_registry_check.py`: semantic registry consistency check.
- `beo-reference` -> `scripts/beo_command.py`: command-contract argv adapter.
- `beo-reference` -> `scripts/beo_utils.py`: shared helper utilities.

## Consolidated names

Older or broader concept names map to the current smaller reference set:

- Authority, Beads authority, triage, lifecycle, events, and modes of Beads interaction: `lifecycle.md`.
- Mutation safety, approval, execution modes, strict side effects, and path reservation: `safety.md`.
- Semantic memory, learning, recall, qmd, and Obsidian persistence: `memory.md`.
