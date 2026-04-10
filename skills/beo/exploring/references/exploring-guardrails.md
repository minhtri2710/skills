# Exploring Guardrails

## Red Flags

| Flag | Description |
|------|-------------|
| **Asking implementation questions** | "Should we use a Map or an Object?" is planning, not exploring |
| **Accepting "I don't care"** | Propose a concrete default instead |
| **Skipping gray areas** | Most non-trivial features have at least 2 gray areas. If you find fewer, verify that you have not overlooked edge cases, but do not invent artificial uncertainty. |
| **Writing CONTEXT.md before decisions are locked** | Decisions first, document second |
| **Spending >15 min on one question** | If it's that complex, lock what you can and mark the rest as an open question for planning |
| **Answering your own questions instead of waiting for user response** | Exploring must lock user-facing behavior with the user, not silently invent it |

## Anti-Patterns

| Pattern | Why It's Wrong | Instead |
|---------|---------------|---------|
| Starting to plan during exploring | Premature commitment | Lock decisions only; planning comes next |
| Asking about tech stack choices | That's a planning decision | Ask about behavior and requirements |
| Copying the user's words verbatim as decisions | Users speak loosely | Restate precisely and confirm |
| Creating tasks during exploring | No tasks until planning | Only the epic bead should exist |
| Summarizing requests without redaction | Can leak secrets or noisy payloads into durable artifacts | Summarize in your own words and redact sensitive literals |
| Skipping exploring for non-instant features | Even "simple" features at Quick scope still have gray areas | At minimum, do a Quick-depth pass. Only work classified as **instant-path** by `beo-router` (single file, <30 min) skips exploring. |
| Running full Standard/Deep exploration on Quick-scope work (`<=2` files, all decisions obvious) | Burns time and context without adding decision clarity | Run the Quick path, resolve the gray areas, then move on |
