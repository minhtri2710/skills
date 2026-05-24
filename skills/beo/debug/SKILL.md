---
name: beo-debug
description: Diagnose blockers for BEO-tracked Beads delivery in read-only support mode. Use when a BEO execution or review phase emits a debug handoff, or when the user says "debug this bead", "diagnose this BEO blocker", or "why is this bead failing?". Do not trigger for general debugging outside Beads/BEO context.
requires: br>=0.1.28
---
# beo-debug

## Use when

A BEO owner has emitted a debug handoff or explicitly asks for diagnosis of one blocker before it can continue.

## Read

- The caller owner, issue ID, blocker question, target scope, and latest matching handoff event.
- Canonical issue state from `br show <issue-id> --json`.
- Relevant ticket, state, runtime events, verification output, logs, and code paths needed to diagnose the blocker.
- `beo-reference` canonical contracts: `references/kernel.md`, `references/lifecycle.md`, `references/safety.md`, `registry/pipeline.json`, `registry/ticket-schema.json`, and `registry/command-contracts.json`.
- qmd or memory only as advisory recall.

## Do

1. Verify the caller, caller actor, blocker question, target scope, and active delivery claim.
2. Use read-only probes only; avoid commands with product, external, lifecycle, or stateful side effects.
3. Minimize the root cause or classify the blocker as inconclusive or user-owned.
4. Return evidence to the caller instead of selecting a delivery route.

## Write

- A concise diagnosis artifact or debug-owned ticket field when useful.
- A bounded `return` event in `runtime-events.jsonl` with caller actor, diagnosis status, and evidence ref.
- Optional `learning_candidate` metadata only after returning to the caller.

## Emit

- `debug_returned` -> stop and return control to the caller owner.
- `debug_abandoned` -> stop and return control to the caller owner.
- `learning_candidate` -> after the return route, stop and load `beo-learn` only for the learning hook.

## Never

- Do not mutate product files or implement repairs.
- Do not grant approvals, issue review verdicts, or close issues.
- Do not claim or comment on the delivery bead by default; verify the caller claim unless this is a separate debug bead.
- Do not route delivery directly to the user; the caller owns user routing.
- Do not load another BEO delivery owner in the same turn for the same issue after emitting; stop first.
