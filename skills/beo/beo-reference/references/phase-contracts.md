# BEO Phase Contracts

> [!NOTE]
> This reference is subordinate to [references/kernel.md](file:///Users/beowulf/Work/personal/beo-skills/skills/beo/beo-reference/references/kernel.md). `references/kernel.md` is the canonical owner of BEO rules and invariants.

This file summarizes phase permissions. The canonical machine-readable permission matrix is `registry/phase-contracts.json`.

## Owner classes

Owner classes are canonical in `registry/phase-contracts.json`.

## Critical boundaries

- Only delivery owners advance delivery state.
- Support subroutines return evidence or advisory output to a delivery owner.
- Maintenance skills mutate only BEO control-plane materials or explicitly authorized setup.
- `beo-reference` is read-only.
- The permission matrix is canonical in `registry/phase-contracts.json`.

## Repair boundary

Use `repair_same_scope` only when all are true:

- approved file set remains valid,
- generated outputs remain valid,
- done criteria unchanged,
- verification commands unchanged or only need rerun,
- no new Human Gate is required,
- mode does not change.

Use `repair_rescope` when any are true:

- allowed files change,
- generated outputs change,
- done criteria change,
- verification contract changes,
- mode changes,
- new risk/human gate/strict contract is required.

## Evidence refs

Evidence refs must be durable and repo-relative.

Allowed:

- `.beads/artifacts/<issue-id>/checks/<file>`
- `.beads/artifacts/<issue-id>/logs/<file>`
- `br-comment:<id>`

Disallowed:

- raw secrets,
- absolute local paths,
- unredacted customer data,
- temporary terminal scrollback without durable file.
