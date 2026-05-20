# Decomposition

Only atomic beads can be validated or executed.

## Levels

- Epic bead: user-facing initiative or milestone; never executed directly.
- Feature bead: capability group; usually decomposed before execution.
- Atomic bead: one independently approvable execution unit.

## Atomic criteria

An atomic bead has one done target, one risk posture, one approval projection, one small declared file set, one verification contract, one verdict, no unrelated concerns, no hidden side effect, and an independent revert/repair path.

## Parent handling

`beo-plan` applies the claim rule from `beo-reference -> references/beads-authority.md`, creates child atomic beads, creates dependency edges, labels children when useful, and comments the parent. Optional `DECOMPOSITION.md` is planning-only and contains no approval, execution, or verdict fields.

Parent beads remain open until Beads reports children are closed/eligible. Use Beads lifecycle commands, not BEO approval, for parent closure.
