# Authoring

## Placement rules

| Location | Owns | Must not own |
| --- | --- | --- |
| `SKILL.md` | behavior, trigger, ownership predicate, primary decision, writable surfaces, boundaries, next owners | duplicated schemas, command syntax, shared protocol detail |
| shared refs | schemas, registries, mappings, protocols, exact command forms | skill trigger logic, owner selection, fallback routing |
| skill-local refs | static assets, prompt templates, checklists, exact local command appendices | branching logic, route decisions, neighboring-skill ownership |
| author local refs | skill-writing method and manual pressure scenarios | checker scripts, route fixtures, release gates, topology validation |

## Beo author ownership

`beo-author` owns only skill contract authorship:
- create skill contracts
- rewrite skill contracts
- simplify skill wording
- dedupe overlapping responsibilities
- normalize skill-local references
- create manual pressure scenarios for skill authoring

For audits and hardening, prefer manual pressure scenarios over checker scripts, fixture suites, or release gates.

`beo-author` does not own:
- checker scripts
- fixture suites
- release gates
- runtime validation
- topology validation
- product delivery

## Reference taxonomy

| Type | Allowed content |
| --- | --- |
| `REFERENCE` | static schemas, registries, mappings, shared protocols |
| `APPENDIX` | exact commands or linear steps after owner is already chosen |
| `ASSET` | prompts, checklists, message templates, non-normative examples |

## Dependency declaration doctrine

Every packaged BEO skill must declare `metadata.dependencies`, including `[]`
when the skill is intentionally dependency-free.

Dependency item shape:

```yaml
metadata:
  dependencies:
    - id: beads-cli
      kind: command
      command: br
      missing_effect: unavailable
      reason: Required to inspect and update bead graph.
```

Supported `missing_effect` values:
- `degraded`
- `unavailable`
- `unavailable_for_swarm`

Missing dependencies must never silently downgrade safety. If a skill can still
proceed in degraded mode, it must say so explicitly in its contract and record
the fallback evidence.

## Manual pressure doctrine

For beo contract audits/hardening, default to manual pressure scenarios instead of executable validation surfaces.

Recommended baseline set:
- one happy path
- one owner collision
- one stale approval or stale handoff case
- one forbidden-surface temptation
- one debug return or rollback case
- one user-clarification vs go-mode case

## Owner manifest

Use `beo-references -> doctrine-map.md` as the short source-of-truth registry for shared doctrine ownership.

| Concept | Canonical owner | Section |
| --- | --- | --- |
| skill contract authorship | `beo-author` | Ownership test |
| manual pressure scenario prose | `references/skill-writing-method.md` | Pressure scenario shape |
| checker scripts | out of `beo-author` scope | none |
| fixture suites | out of `beo-author` scope | none |
| release gates | out of `beo-author` scope | none |
| topology validation | out of `beo-author` scope | none |
| ownership predicates | each `SKILL.md` | Ownership test |
| shared doctrine registry | `beo-references -> doctrine-map.md` | Canonical source-of-truth registry |
| collision precedence | `beo-route` | Ownership test / Enter when |
| approval record schema and invalidation | `beo-references -> approval.md` | Approval record / invalidation protocol |
| artifact layout and schemas | `beo-references -> artifacts.md` | Artifact schemas |
| shared contract boilerplate | `beo-references -> skill-contract-common.md` | Shared contract doctrine |
| exact `br` / `bv` command syntax | `beo-references -> cli.md` | Exact command forms |
| compact/expanded ceremony and planning depth classes | `beo-references -> complexity.md` | Ceremony modes / Planning depth classes |
| Agent Mail reservation/report protocol | `beo-references -> coordination.md` | Coordination protocols |
| deletion and merge criteria | `beo-references -> deletion-policy.md` | Deletion policy |
| learning and consolidation schemas | `beo-references -> learning.md` | Learning schemas |
| delivery order and allowed handoffs | `beo-references -> pipeline.md` | Allowed handoffs |
| state, handoff freshness, route evidence, go-mode marker | `beo-references -> state.md` | State schemas |
| bead/status/label mapping | `beo-references -> status-mapping.md` | Status mapping |
| go-mode macro behavior | `beo-references -> go-mode.md` | Operator behavior |

## Canonical-source discipline

When wording a beo contract, prefer reference-over-restatement:
- put owner trigger, writable surfaces, forbidden surfaces, and allowed next owners in `SKILL.md`
- put shared schema and protocol truth in the corresponding shared reference
- let `beo-references -> pipeline.md` own allowed handoffs and state-transition routing
- let `beo-references -> approval.md` own approval freshness, grant, refresh, and invalidation semantics
- let `beo-references -> artifacts.md` own artifact schemas and writer boundaries
- let `beo-references -> state.md` own handoff freshness and route/state evidence fields

If a doctrine concept already has a canonical home, neighboring files should point to it instead of re-specifying the same rule in parallel prose.
Startup templates, onboarding surfaces, and skill-local appendices should stay pointer-oriented as well: they may summarize the happy-path shape briefly, but must defer routing, approval, and state semantics to their canonical files.

## Migration ledger

| Source file | Source concept | Destination file | Destination section | Obsolete reason if dropped |
| --- | --- | --- | --- | --- |
| author-owned checker/release automation surface | checker and release automation | none | none | outside `beo-author` scope |
| author-owned executable route regression surface | executable route regression fixtures | none | none | outside `beo-author` scope |
| author route fixture scenario registry asset | route fixture scenario registry | none | none | executable fixture ownership removed |
| author release surface asset | release gate list | none | none | release ownership removed |
| author pressure template asset | pressure scenario aid | `references/skill-writing-method.md` | Pressure scenario shape | merged into manual writing asset |
| `references/validation-operations.md` | readiness operations, PASS/FAIL, validation handoffs | `beo-validate`; `beo-references -> approval.md`; `beo-references -> pipeline.md` | Primary decision; Approval; Allowed handoffs | local runtime doctrine merged |
| `references/reviewing-operations.md` | verdict operations, reactive fix, approval retention | `beo-review`; `beo-references -> artifacts.md`; `beo-references -> approval.md` | Primary decision; REVIEW schema; approval invariants | local runtime doctrine merged |
| `references/compounding-operations.md` | accepted-review learning flow | `beo-compound`; `beo-references -> learning.md` | Primary decision; Feature learning schema | local runtime doctrine merged |
| `references/debugging-operations.md` | root-cause flow and return behavior | `beo-debug`; `beo-references -> state.md` | Primary decision; Debug return metadata | local runtime doctrine merged |
| `references/message-templates.md` | debug output message shapes | `references/diagnostic-checklist.md` | Message shape prompts | merged to reduce local asset count |
| `references/dream-operations.md` | consolidation flow | `beo-dream`; `beo-references -> learning.md` | Primary decision; Consolidation record schema | local runtime doctrine merged |
| `references/consolidation-rubric.md` | evidence threshold and owner clarity | `beo-dream`; `beo-references -> learning.md` | Ownership test; Provenance schema | rubric merged |
| legacy author operations reference | authoring severity, placement, version bump | `beo-author`; `beo-references -> authoring.md` | Must not; Placement rules | skill-writing doctrine merged |
| `references/escalation.md` | escalation doctrine | `beo-references -> pipeline.md` | Allowed handoffs / wait statuses | obsolete split owner |
| `references/bead-description-templates.md` | bead description template | `beo-references -> artifacts.md` | Bead description schema | duplicate template |
| `references/go-mode.md` | go-mode route state | `beo-references -> state.md` | Go-mode marker | duplicate state protocol |
| `references/context-template.md` | CONTEXT schema | `beo-references -> artifacts.md` | CONTEXT.md schema | duplicate schema |
| `references/go-mode.md` | go-mode behavior and marker | `beo-explore`; `beo-references -> state.md` | Enter when; Go-mode marker | split behavior/schema |
| `references/plan-template.md` | PLAN schema | `beo-references -> artifacts.md` | PLAN.md schema | duplicate schema |
| `references/discovery-reference.md` | planning discovery | `beo-plan`; `beo-references -> artifacts.md` | Enter when; Artifact schemas | planning behavior merged |
| `references/artifact-writing-guide.md` | artifact writing behavior | `beo-plan` | Writable surfaces | behavior merged |
| `references/planning-prerequisites.md` | planning entry conditions | `beo-plan` | Ownership test | predicate merged |
| `references/planning-state-and-cleanup.md` | approval cleanup | `beo-references -> approval.md`; `beo-plan` | invalidation protocol; Enter when | protocol merged |
| `references/blocker-handling.md` | blocker classification | `beo-execute` | Must not / Allowed next owners | behavior merged |
| `references/worker-prompt-guide.md` | worker payload | `references/swarming-operations.md` | Worker payload schema | swarm-owned appendix |
| `references/pressure-scenarios.md` | pressure cases | none | none | executable fixture ownership removed |
| `references/pressure-scenarios.md` | pressure cases | none | none | executable fixture ownership removed |
