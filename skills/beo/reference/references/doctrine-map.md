<!-- owner: beo-reference -->
<!-- version: 2026-04-29 -->
<!-- last-reviewed: 2026-04-29 -->

# Doctrine map

## Canonical source-of-truth registry

Use this table to decide where shared beo doctrine is allowed to live.
If a file explains a rule it does not own, replace it with a one-line pointer.
If a restatement can change behavior, delete it or move it to the canonical owner.
If an example restates decision law from another file, delete it.

| Doctrine | Canonical file |
| --- | --- |
| Operator first-pass view | `beo-reference -> operator-card.md` |
| Owner selection, collision precedence, route suppression | `beo-route` |
| Delivery order and legal owner transitions | `beo-reference -> pipeline.md` |
| Artifact schemas, writer boundaries, provenance chain | `beo-reference -> artifacts.md` |
| Approval model, approval schema, grant/refresh/invalidation rules | `beo-reference -> approval.md` |
| State lifecycle, stale/live field discipline, handoff freshness | `beo-reference -> state.md` |
| Go-mode macro behavior and operator assumption rule | `beo-reference -> go-mode.md` |
| Complexity modes and planning depth classes | `beo-reference -> complexity.md` |
| Learning thresholds, no-learning, consolidation thresholds | `beo-reference -> learning.md` |
| Shared contract boilerplate and decision packet | `beo-reference -> skill-contract-common.md` |
| CLI command forms and local operational mechanics | `beo-reference -> cli.md` or skill-local appendix when explicitly local |

## Canonical ownership map

This map is an index of authority only. It does not add routing rules or become
a runtime authority.

| Doctrine | Canonical surface | Local consumers |
| --- | --- | --- |
| Owner routing and collision | `beo-route`, `pipeline.md` | all owner skills |
| Approval envelope and stale approval | `approval.md` | plan, validate, execute, swarm, review |
| Planning depth and ceremony compactness | `complexity.md` | plan, validate, operator-card |
| Artifact schemas | `artifacts.md` | explore, plan, execute, review, compound |
| State, handoff, go-mode, operator view | `state.md`, `go-mode.md` | route, onboard, all owner skills |
| Coordination and worker protocol | `coordination.md`, `swarm/references/swarming-operations.md` | swarm |
| Learning thresholds and startup-critical policy | `learning.md` | plan, validate, review, compound, dream |
| Human-facing summaries | `operator-card.md` | all owner skills |
| Status mapping | `status-mapping.md` | execute, swarm |

## Canonical-source rules

- Each decision doctrine must have exactly one canonical home.
- Shared references may explain schemas, checklists, or operational mechanics, but must not redefine routing precedence owned by `beo-route`.
- `beo-reference -> skill-contract-common.md` may hold mechanical contract discipline only; it must not own routing, approval precedence, artifact schema, or legal transition semantics.
- If a rule changes, update the canonical file first and convert neighboring restatements into references or short inheritance notes.
- Neighboring files may include one-line summaries only when needed for local readability.
- Any multi-step decision rule must live in its canonical owner.

## Rewrite rule

When reducing duplicate wording:
- keep normative doctrine only in its canonical file
- replace neighboring restatements with one-line pointers
- preserve local examples only when they illustrate local ownership
- delete examples that restate another file’s decision law

## Deletion rules

Delete or merge obsolete doctrine only after migrating unique surviving rules to their canonical owner and confirming no inbound references remain. Prefer canonical owner files over small duplicate references.

## Legacy removal policy

A legacy surface may be removed only after:
1. replacement canonical owner is identified
2. all inbound references are migrated
3. onboarding or runtime migration path is defined when persisted repo state may contain the legacy form
4. grep audit shows no live references
5. at least one pressure scenario covers the removal

Do not keep compatibility aliases as hidden doctrine. Compatibility may exist only in migration code and must not be emitted by current templates.
