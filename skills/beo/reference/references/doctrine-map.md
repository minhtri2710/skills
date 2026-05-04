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
| Owner selection, collision precedence, route suppression | `beo-route` | all owner skills |
| Delivery order and legal owner transitions | `pipeline.md` | all owner skills |
| Approval envelope and stale approval | `approval.md` | plan, validate, execute, review |
| Planning depth and ceremony compactness | `complexity.md` | plan, validate, operator-card |
| Artifact schemas | `artifacts.md` | explore, plan, execute, review, compound |
| State lifecycle, handoff freshness, operator view | `state.md` | route, onboard, all owner skills |
| Go-mode macro behavior and operator assumption rule | `go-mode.md` | route, onboard, all owner skills |
| Learning thresholds and conditional prior-learning consultation | `learning.md` | plan, validate, review, compound, dream |
| Human-facing summaries | `operator-card.md` | all owner skills |
| Status mapping | `status-mapping.md` | validate, execute |

## Canonical-source rules

- Each decision doctrine must have exactly one canonical home.
- Shared references may explain schemas, checklists, or operational mechanics, but must not redefine routing precedence owned by `beo-route`.
- `beo-reference -> skill-contract-common.md` may hold mechanical contract discipline only; it must not own routing, approval precedence, artifact schema, or legal transition semantics.
- If a rule changes, update the canonical file first and convert neighboring restatements into references or short inheritance notes.
- Neighboring files may include one-line summaries only when needed for local readability.
- Any multi-step decision rule must live in its canonical owner.

## Restatement policy

Allowed outside the canonical owner:
- one-line pointer to the canonical owner
- local example that illustrates local ownership without deciding behavior
- local hard stop that enforces the current owner's own boundary
- display-only summary that explicitly says it has no authority

Forbidden outside the canonical owner:
- multi-step decision rules from another owner
- copied schemas or command forms
- examples that restate another file's decision law
- output cards that grant approval, routing, readiness, review, or promotion authority
- fallback routing rules hidden in skill-local appendices

## Rewrite rule

When reducing duplicate wording:
- keep normative doctrine only in its canonical file
- replace neighboring restatements with one-line pointers
- preserve local examples only when they illustrate local ownership
- delete examples that restate another file’s decision law

## Cleanup workflow

1. Identify the duplicated doctrine and every file that restates it.
2. Pick the canonical owner from this map.
3. Move any unique surviving rule into the canonical owner before deleting it elsewhere.
4. Replace neighboring copies with a pointer or remove them when even a pointer adds noise.
5. Check inbound references before deleting or merging a file.
6. Pressure-review affected scenarios from `skills/beo/author/references/manual-pressure-scenarios.md`.

## Deletion rules

Delete or merge superseded doctrine only after migrating unique surviving rules to their canonical owner and confirming no inbound references remain. Prefer canonical owner files over small duplicate references.
