# Validating Guardrails

## Red Flags

| Flag | Description |
|------|-------------|
| **Skipping validation entirely** | "The plan looks fine" is not validation |
| **Auto-approving without user** | The approval gate is non-negotiable |
| **Ignoring spike NO results** | A failing spike means the plan is broken |
| **Fixing failures without re-checking** | After fixing, re-run the failed dimension check |
| **Validating without CONTEXT.md** | Decisions are the source of truth for requirement coverage |
| **Spending >1 hour on validation** | If it takes that long, the plan probably needs rework |
| **Validating a bead set that has no phase contract** | Phase contract defines the closed loop |
| **Validating a story map that cannot explain "why now" for Story 1** | Story 1 must have an obvious reason to exist first |
| **A phase exit state that is not observable** | "Improve quality" is not an exit state |
| **A bead's "done" does not connect to any story** | Every bead must trace to a story |

## Anti-Patterns

| Pattern | Why It's Wrong | Instead |
|---------|---------------|---------|
| Rubber-stamping approval | Defeats the purpose of the gate | Every dimension gets a genuine check |
| Running spikes for LOW-risk tasks | Waste of time | Spikes are for HIGH-risk only |
| Fixing plan issues during validation | Scope creep | Note issues, route back to beo-planning if >2 failures |
| Adding implementation tasks during validation | That's planning work; only spikes are allowed | Route back to beo-planning for missing tasks |
| Skipping deduplication | Wastes worker time on redundant tasks | Always check for overlap |
| Approving when bead descriptions are empty | Workers will freelance with no spec | FAIL and route back to planning |
