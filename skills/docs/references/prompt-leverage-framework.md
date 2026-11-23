# Prompt Leverage Framework

The framework follows a structured goal-to-done pipeline:

`Objective -> Context -> Work Style -> Tool Rules -> Output Contract -> Done Criteria`

## Block Definitions

### Objective

State the task in one or two lines. Define success in observable terms.

### Context

Specify relevant files, URLs, constraints, assumptions, and information boundaries. Say when the agent must retrieve facts instead of guessing.

### Work Style

Control how the agent approaches the task. Use constraints specific to this task; generic reasoning coaching adds tokens without changing what the agent does.

- Name where breadth matters and where depth matters in this particular system.
- Name the invariants, prior decisions, or areas the agent must not change.

### Tool Rules

Define when browsing, file inspection, tests, or external tools are required. Prevent skipping prerequisite checks.

### Output Contract

Define exact structure, tone, formatting, depth, and any required sections or schemas.

### Done Criteria

Define what must be true before the agent stops. Name the objective checks that decide done: tests to run, a command's output, sources to cite. Do not ask the agent to re-review its own work.

## Task-Type Adjustments

### Coding

- Emphasize repo context, file inspection, smallest correct change, validation, and edge cases.

### Research

- Emphasize source quality, evidence gathering, synthesis, uncertainty, and citations.

### Writing

- Emphasize audience, tone, structure, constraints, and revision criteria.

### Review

- Emphasize fresh-eyes critique, failure modes, alternatives, and explicit severity.
