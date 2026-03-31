# Planning Guardrails

Red flags and anti-patterns for `beo-planning`.

## Red Flags

| Flag | Description |
|------|-------------|
| **Creating tasks without a plan** | Always write plan.md first (except in promotion flow) |
| **Tasks without verification criteria** | Every task must have concrete "how to verify" |
| **Overlapping file scopes** | If two independent tasks modify the same file, they must be sequenced |
| **Skipping dependency validation** | Always run `br dep cycles --json` after wiring |
| **Risk-inflating everything to HIGH** | Be honest — most tasks in a well-scoped feature are LOW or MEDIUM |
| **Tasks that are too granular** | "Add import statement" is not a task. Tasks should be 30-90 min of work |
| **Tasks that are too large** | "Implement the entire feature" is not a task. Break it down. |
| **Skipping learnings retrieval** | Phase 0 is mandatory, not optional |
| **Creating beads before a phase contract exists** | Phase contract defines what "done" means for the whole phase |
| **Creating beads before stories are clear** | Stories explain why the work order exists |
| **Stories with no clear unlock or contribution** | Every story must advance the exit state |
| **Exit states that are vague or non-observable** | "Improve performance" is not an exit state |
| **Handing off beads with empty descriptions** | Every bead must have a complete spec before handoff |

## Anti-Patterns

| Pattern | Why It's Wrong | Instead |
|---------|---------------|---------|
| Planning without CONTEXT.md | Assumptions will bite you | Route back to beo-exploring |
| One giant task per feature | No parallelism, no incremental progress | Decompose into 3-8 tasks |
| Dependencies everywhere | Over-constraining kills parallelism | Only add dependencies that are truly required |
| Copy-pasting CONTEXT.md into every task | Bloats descriptions, drifts | Reference the decision IDs (D1, D2) |
| Research without synthesis | Raw findings are not a plan | Always write the approach section |
| Jumping from plan.md to beads | Skips the phase/story layer | Write phase-contract.md and story-map.md first |
| Creating a bead without immediately writing its description | Empty descriptions break execution | Treat create + update --description as one atomic operation |
