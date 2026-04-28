# Doctrine map

## Canonical source-of-truth registry

Use this table to decide where shared beo doctrine is allowed to live.
If a file explains a rule it does not own, replace it with a one-line pointer.
If a restatement can change behavior, delete it or move it to the canonical owner.
If an example restates decision law from another file, delete it.

| Doctrine | Canonical file |
| --- | --- |
| Operator first-pass view | `beo-references -> operator-card.md` |
| Owner selection, collision precedence, route suppression | `beo-route` |
| Delivery order and legal owner transitions | `beo-references -> pipeline.md` |
| Artifact schemas, writer boundaries, provenance chain | `beo-references -> artifacts.md` |
| Approval model, approval schema, grant/refresh/invalidation rules | `beo-references -> approval.md` |
| State lifecycle, stale/live field discipline, handoff freshness | `beo-references -> state.md` |
| Go-mode macro behavior and operator assumption rule | `beo-references -> go-mode.md` |
| Complexity modes and planning depth classes | `beo-references -> complexity.md` |
| Learning thresholds, no-learning, consolidation thresholds | `beo-references -> learning.md` |
| Shared contract boilerplate and decision packet | `beo-references -> skill-contract-common.md` |
| CLI command forms and local operational mechanics | `beo-references -> cli.md` or skill-local appendix when explicitly local |

## Canonical-source rules

- Each decision doctrine must have exactly one canonical home.
- Shared references may explain schemas, checklists, or operational mechanics, but must not redefine routing precedence owned by `beo-route`.
- `beo-references -> skill-contract-common.md` may hold mechanical contract discipline only; it must not own routing, approval precedence, artifact schema, or legal transition semantics.
- If a rule changes, update the canonical file first and convert neighboring restatements into references or short inheritance notes.
- Neighboring files may include one-line summaries only when needed for local readability.
- Any multi-step decision rule must live in its canonical owner.

## Rewrite rule

When reducing duplicate wording:
- keep normative doctrine only in its canonical file
- replace neighboring restatements with one-line pointers
- preserve local examples only when they illustrate local ownership
- delete examples that restate another file’s decision law
