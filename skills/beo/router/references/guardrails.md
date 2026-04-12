# Red Flags and Anti-Patterns

## Red Flags

- **Treating conversational phrasing as non-pipeline work**: "Can you research X with me", "let's explore X", or "help me think through X" are feature intake signals, not freeform chat. Always route through the state table
- **Starting implementation without state detection**: Always run Phase 1 first
- **Creating a second epic while one is active**: One feature at a time unless user explicitly requests parallel features
- **Skipping HANDOFF.json on resume**: If the file exists, read it
- **Classifying everything as instant**: If there is any doubt about scope, route to exploring
- **Routing to executing before planning**: Unless the feature has an `approved` label and tasks exist, do not skip planning
- **Bypassing validation for instant work**: Instant-path work must still go through `beo-validating`. Do not set `approved` in the router or route directly to executing
- **Routing to swarming without validated plan**: Swarming requires the same `approved` label as executing
- **Skipping compounding after review**: Learnings capture is part of the pipeline, not optional

## Anti-Patterns

| Pattern | Why It's Wrong | Instead |
|---------|---------------|---------|
| `br create` without checking existing epics | Creates duplicate features | Always list epics first |
| Routing based on user's words alone | User may not know current state | Always query bead graph |
| Bypassing pipeline for casual-sounding prompts | "Research with me" is still a feature intake | Route through state table regardless of phrasing |
| Skipping `br doctor` on first session | Silent corruption goes undetected | Run doctor on bootstrap |
| Hardcoding epic IDs | IDs change between sessions | Always query dynamically |
| Routing to executing instead of swarming for parallel work | Executing is single-worker; swarming orchestrates multiple | Check task count and independence before choosing |
| Using dream for one-off fixes | Dream consolidates learnings; debugging fixes issues | Route to `beo-debugging` for errors |
