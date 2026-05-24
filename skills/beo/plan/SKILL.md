---
name: beo-plan
description: Plan, decompose, and scope a claimed Beads issue before BEO execution. Use when selecting, claiming, or scoping a Beads-tracked delivery issue, decomposing a bead into children, or creating/editing the BEO TICKET.md. Trigger on "claim this bead", "scope issue #X", or "decompose this feature into beads". Do not trigger for general task planning outside Beads/BEO context.
requires: br>=0.1.28
---
# beo-plan

## Use when

Start BEO delivery for one verified Beads issue, or decompose a non-atomic issue into child beads.

## Read

- Canonical issue state from `br show <issue-id> --json`.
- Graph orientation from `bv` robot output only when it affects selection, dependency order, or decomposition.
- `beo-reference` canonical contracts: `references/kernel.md`, `references/lifecycle.md`, `references/safety.md`, `registry/pipeline.json`, `registry/profiles.json`, `registry/ticket-schema.json`, and `registry/command-contracts.json`.
- Advisory memory only when useful; memory never changes scope or authority.

## Do

1. **Select and claim**: Resolve exactly one issue and claim it atomically before writing delivery artifacts, child beads, dependency edges, or planning comments.
2. **Decide atomicity**: Determine whether the issue is atomic; if not, decompose into child beads and dependency edges, then leave the parent open.
3. **Author ticket** (if atomic): Write `.beads/artifacts/<issue-id>/TICKET.md`. For Quick Mode, accelerate scoping by running `beo_quick_fill.py --issue <issue-id>` to auto-fill the ticket from contextual git diffs, stripping protected paths automatically.
4. **Decide reservation**: Determine whether profile, overlap, strict mode, or parallel risk requires path reservation.
5. **Run integrity checks**: Execute plan/identity integrity checks through `beo-reference` scripts as commands, not as source material to read.

## Write

- Plan-owned `TICKET.md` fields.
- Child beads and dependency edges during decomposition.
- Planning comments and triage records when they materially affected selection or decomposition.
- Path reservation only when the selected profile or risk requires it.

## Emit

- `plan_complete` -> stop and load `beo-validate` before any approval or mutation.
- `decomposition_recorded` -> stop; parent waits for children.
- `requirements_missing` or `human_gate_blocks` -> stop for user input.
- `abandoned` -> stop and load `beo-review`.

## Never

- Do not grant or imply `PASS_EXECUTE` (validation owns approval authority; planning is purely for scoping).
- Do not mutate product files (planning must be side-effect free to preserve pristine git status before validation).
- Do not execute verification as delivery evidence (verification runs strictly inside execute/review phases).
- Do not close issues or emit review verdicts (review owns final closure verdicts).
- Do not load another BEO delivery owner in the same turn for the same issue after emitting; stop first.
