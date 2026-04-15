# Approach: <feature-name>

## Contents

- [Problem Shape](#problem-shape)
- [Current Codebase Reality](#current-codebase-reality)
- [Gap Analysis](#gap-analysis)
- [Recommended Approach](#recommended-approach)
- [Alternatives Considered](#alternatives-considered)
- [Risk Map](#risk-map)
- [Relevant Learnings Applied](#relevant-learnings-applied)
- [Planning Mode Decision](#planning-mode-decision)
- [Current Phase Strategy](#current-phase-strategy)
- [Summary For plan.md](#summary-for-planmd)

## Problem Shape

What this feature needs to make true in practical terms.

- User/system outcome:
- What must become possible:
- What must remain true:
- What would count as a believable success state:

## Current Codebase Reality

### Existing capabilities
- <existing module / pattern / endpoint / component>
- <existing abstraction that should be reused>
- <existing workflow or contract already in place>

### Missing pieces
- <missing behavior>
- <missing contract>
- <missing data shape / UI path / integration step>

### Constraints
- <runtime constraint>
- <build/test constraint>
- <dependency constraint>
- <locked decision from CONTEXT.md that shapes implementation>

## Gap Analysis

### Must add
- <new capability / behavior / integration / path>

### Must change
- <existing file / abstraction / workflow that must be updated>

### Must avoid
- <tempting but wrong approach>
- <known failure pattern or anti-pattern>
- <scope expansion that should stay out>

## Recommended Approach

- Main implementation direction:
- Why this direction fits the current codebase:
- What will be reused:
- What will be introduced:
- How this approach honors locked decisions:
- What this approach intentionally does not solve yet:

## Alternatives Considered

### Alternative A: <name>
- Why it was considered:
- Why it was rejected:
- What risk or cost made it less suitable:

### Alternative B: <name>
- Why it was considered:
- Why it was rejected:
- What risk or cost made it less suitable:

## Risk Map

### LOW
- <work that follows existing patterns cleanly>

### MEDIUM
- <work that varies an existing pattern or touches several files>

### HIGH
- <work that is novel, externally dependent, or hard to prove without a spike>

## Relevant Learnings Applied

- Pattern reused:
- Prior failure avoided:
- Existing abstraction honored:
- Prior coordination / testing / migration lesson applied:

## Planning Mode Decision

- Mode: `single-phase` | `multi-phase`
- Why this mode fits the feature:
- Why a single closed loop is enough, OR why one phase would become too large / vague:
- If `multi-phase`, what later work should stay intentionally deferred:

## Current Phase Strategy

- Current phase outcome:
- Why this is the right first / next slice:
- What this phase unlocks:
- What remains for later phases, if any:

## Summary For plan.md

- One-paragraph summary:
- Main risks:
- Main tradeoff:
- Why this plan shape is credible:
