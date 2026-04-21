# Approach: <feature-name>

```markdown
# Approach: <feature-name>

## Problem Shape
- User or system outcome:
- What must become possible:
- What must remain true:
- Believable success state:

## Current Codebase Reality
### Existing capabilities
- <module, pattern, endpoint, component, or workflow already present>

### Missing pieces
- <missing behavior, contract, integration, or path>

### Constraints
- <runtime, build, dependency, or locked-decision constraint>

## Gap Analysis
### Must add
- <new capability or integration>

### Must change
- <existing file, abstraction, or workflow that must move>

### Must avoid
- <tempting but wrong path, known failure pattern, or scope leak>

## Recommended Approach
- Main direction:
- Why it fits the codebase:
- What will be reused:
- What will be introduced:
- How locked decisions are honored:
- What this intentionally does not solve yet:

## Alternatives Considered
### Alternative A: <name>
- Why considered:
- Why rejected:
- What cost or risk made it worse:

### Alternative B: <name>
- Why considered:
- Why rejected:
- What cost or risk made it worse:

## Risk Map
### LOW
- <work that follows existing patterns cleanly>

### MEDIUM
- <work that varies an existing pattern or touches several files>

### HIGH
- <novel, externally dependent, or hard-to-prove work>

## Relevant Learnings Applied
- Pattern reused:
- Prior failure avoided:
- Existing abstraction honored:
- Prior testing, coordination, or migration lesson applied:

## Planning Mode Decision
- Mode: `single-phase` | `multi-phase`
- Why this mode fits:
- Why one closed loop is enough, or why one loop would be too large or vague:
- If `multi-phase`, what later work is intentionally deferred:

## Current Phase Strategy
- Current phase outcome:
- Why this is the right first or next slice:
- What this phase unlocks:
- What remains for later phases:

## Summary For `plan.md`
- One-paragraph summary:
- Main risks:
- Main tradeoff:
- Why this plan shape is credible:
```
