---
name: beo-execute
description: |
  Deliver one approved serial bead. Use when exactly one approved ready bead is selected with mode=`serial` and mutation stays in approved scope. Do not use when root cause is unproven or parallel coordination is required.
---

# beo-execute

## Purpose
Deliver one approved serial bead.

## Primary owned decision
Deliver exactly one approved bead inside approved scope.

## Enter when
- readiness=`PASS_SERIAL`
- approval is current
- mode=`serial`
- one ready bead is selected
- planned mutation stays inside approved file scope

## Writable surfaces
- product files inside the selected bead's approved file scope only
- bead status/evidence surfaces described by `references/execution-operations.md` and `beo-references -> status-mapping.md`, only for the selected bead
- review evidence bundle fields described by `beo-references -> artifacts.md`, only to report terminal execution scope, changed files, verification evidence, and approval reference
- shared `STATE/HANDOFF` surfaces under `beo-references -> skill-contract-common.md`

## Decision packet
- shared decision packet under `beo-references -> skill-contract-common.md`
- no local packet extensions beyond execution evidence carried in owned artifact surfaces

## Exit routing

Use `beo-references -> approval.md` for approval invalidation routing details.
Use `beo-route` for collision precedence when more than one owner appears plausible.

| Observation | Next owner |
| --- | --- |
| external approval, secret, access, or clarification is missing | user |
| required mutation falls outside approved file scope | beo-plan |
| stale or invalid approval before product mutation, with artifacts otherwise current | beo-validate |
| blocker prevents progress and root cause is unproven | beo-debug |
| selected bead complete and required verification passed | beo-review |
| stale or invalid approval after product mutation and changed files remain, with terminal scope impact still needing assessment | beo-review |
| stale or invalid approval after product mutation and evidence already proves plan or scope repair is required | beo-plan |

## Allowed next owners
- beo-review
- beo-debug
- beo-plan
- beo-validate
- user

## Local hard stops
- Do not widen file scope.
- Do not continue execution after approval or scope drift with unresolved changed files.
- Do not diagnose unknown blockers by mutation.

## References
- `beo-references -> operator-card.md`
- `beo-references -> approval.md`
- `beo-references -> pipeline.md`
- `beo-references -> state.md`
- `beo-references -> status-mapping.md`
- `references/execution-operations.md`
