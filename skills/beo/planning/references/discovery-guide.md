# Discovery Guide

Detailed instructions for Phase 1 (Discovery) of `beo-planning`.

## Research Questions

From CONTEXT.md, extract:
- **Architecture questions**: "How is the existing code structured?"
- **Pattern questions**: "What patterns does this codebase use?"
- **Constraint questions**: "What limits or requirements exist?"
- **External questions**: "What do external APIs/libraries require?"

## Parallel Research Subagents

Launch 2-4 parallel research subagents using the session's normal subagent/task-dispatch mechanism, focused on:

1. **Architecture Agent**: Explore codebase structure relevant to the feature
   - File organization, module boundaries, import patterns
   - Existing code that will be modified or extended

2. **Pattern Agent**: Identify patterns to follow
   - How similar features are implemented
   - Testing patterns, error handling conventions
   - Naming conventions, file placement rules

3. **Constraint Agent**: Discover hard limits
   - Type system constraints, API contracts
   - Performance requirements, compatibility needs
   - Dependencies and version constraints

4. **External Agent** (if needed): Research external dependencies
   - API documentation, SDK usage patterns
   - Known issues, migration guides
   - Community best practices

Each agent writes findings to a structured format. Collect all results.

## Synthesis

Combine research into a discovery summary:
- What exists today (architecture)
- What patterns to follow (conventions)
- What constraints apply (limits)
- What external factors matter (dependencies)

Write findings to `.beads/artifacts/<feature-name>/discovery.md`.
