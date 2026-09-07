---
name: architecture-premise-audit
description: Audit a whole project for a possibly wrong system archetype by deriving expected product capabilities before trusting repository vocabulary. Use only for an explicitly requested broad premise audit, not ordinary architecture review or one named design concern.
---

# Architecture Premise Audit

Determine whether the project is built around the right system archetype, not
merely whether its current modules are internally consistent. Audit read-only
unless the user separately requests changes.

## Boundaries

- Work at the whole-project or named broad-system boundary requested by the user.
- Derive the expected product model before treating repository terminology,
  architecture docs, tests, or benchmarks as authoritative.
- Treat passing proof as evidence about an implementation, not proof that the
  mechanism should exist.
- Complexity is a finding only when it lacks a required product need, owner,
  lifecycle, consumer, scaling contract, or failure contract.
- Do not turn a broad audit into implementation, issue creation, or a second
  review workflow.
- Ask only when one missing fact would reverse the verdict and cannot be bounded
  with an explicit assumption.

For realtime multiplayer, MMO, or another system with a suspected structural
misfit, read
[references/structural-antipatterns.md](references/structural-antipatterns.md)
before constructing the expected capability map. Use its patterns as search
lenses, not as a checklist that every design must satisfy.

## Audit Slice

Judge work by product responsibility rather than repository module. Each audit
slice should identify:

- job to be done and production consumer;
- authoritative owner, state, and lifecycle;
- inputs, outputs, and trust boundaries;
- scaling or adversarial variable;
- failure, overload, and backpressure behavior;
- reusable-platform versus application responsibility.

A slice may cross modules, and one module may contain several slices.

## Procedure

1. **Set the claim.** State the product category, requested boundary, expected
   outcome, material assumptions, and completion rule.
2. **Build the expected atlas.** From product needs and established domain
   mechanisms, list the responsibilities that should exist, likely owners,
   scaling variables, and work that must be bounded or isolated.
3. **Build the observed map, and record it as the coverage ledger.** Trace
   production entry points, authoritative state, durable effects, expensive
   operations, queues, schedulers, external outputs, deployment boundaries, and
   cited proof. Record one ledger row for each item as you discover it: the item,
   which of those nine categories it belongs to, and where it is represented.
   Record a category you traced and found empty as a row stating that derived
   absence. This ledger is the artifact step 6 stops on and output item 2
   reports. A later step that discovers an item this trace missed returns here to
   record it and re-runs the steps after; no step appends a row while checking
   coverage. Do not copy the repository's decomposition without testing it.
4. **Compare every slice.** Ask what demonstrated requirement forces each
   mechanism, whether cost follows useful work, whether normal and exceptional
   paths are reversed, and whether removing or relocating the mechanism loses
   an established requirement.
5. **Deep-check serious candidates.** Trace real callers and consumers, name the
   exact amplification route, construct the cleaner counterfactual, identify
   machinery that disappears, give the strongest counterargument, and state
   evidence that would falsify the finding.
6. **Check coverage.** Stop only when every row step 3 recorded in the coverage
   ledger — in all nine of its categories, not a subset — has been carried into a
   comparison at step 4 or 5, or carries a stated exclusion with the rule that
   excludes it. Judge each row by the category step 3 gave it. An empty ledger
   does not satisfy this gate: it means step 3 traced nothing, and the audit
   returns there rather than terminating.

Do not report generic improvements. Classify supported candidates as architecture
defect, owner defect, implementation drift, justified divergence, quarantined
scaffold, or insufficient evidence.

## Verdict And Output

Lead with one verdict:

- `KEEP_FOUNDATION`
- `REPAIR_FIRST`
- `REDIRECT_RECOMMENDED`
- `STOP_AND_REDIRECT`
- `INSUFFICIENT_EVIDENCE`

Then provide only the material sections needed to support it:

1. expected-versus-observed map;
2. the coverage ledger built at step 3, compact, with its exclusions;
3. ranked findings with production evidence, hidden premise, tax, and
   amplification route;
4. counterfactual architecture and machinery removed or relocated;
5. counterargument and falsifier for each serious finding;
6. `STOP_OPTIMIZING` and `PROBABLY_JUSTIFIED` items;
7. prioritized decisions and realistic fitness scenarios.

Make the best evidence-supported judgment available. Expose assumptions, but do
not end with an unranked option menu or an interview questionnaire.
