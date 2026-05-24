# BEO Skills

BEO Skills defines the domain language for the Beads-backed BEO workflow and its agent skill contracts.

## Language

**Canonical Authority**:
The artifact family that owns the binding meaning of a workflow rule when other prose or generated views disagree.
_Avoid_: Source of truth, final doc

**Registry**:
A machine-readable BEO contract file under `skills/beo/reference/registry/` that defines workflow, profile, command, schema, or pipeline rules.
_Avoid_: Config, JSON docs

**Doctrine**:
Shared human-readable BEO guidance under `skills/beo/reference/references/` that explains invariants and operating principles.
_Avoid_: Narrative docs, prose rules

**Operator Card**:
A short `SKILL.md` body that tells an agent what to read, decide, write, emit, and never do while delegating detailed authority to the canonical registry and doctrine.
_Avoid_: Full standalone manual, copied reference

**Routing Reference**:
A local per-skill prose file that restates workflow transitions for one skill.
_Avoid_: Transition source of truth

**Ticket Template**:
A reusable artifact skeleton under `skills/beo/reference/templates/` for authoring BEO ticket files consistently with the ticket schema.
_Avoid_: Plan asset template, ticket example

**Quick Mode**:
The low-risk BEO delivery posture that keeps the four delivery gates but uses compact repo-only artifacts and minimal checks.
_Avoid_: Single-pass mode, bypass mode

**Path Reservation**:
A BEO-local concurrency guard that temporarily reserves declared paths for a claimed issue according to the selected mode/profile.
_Avoid_: br reservation, lock

**PASS_EXECUTE**:
A validation grant that allows execution only while its approved scope and commit-based freshness binding remain current.
_Avoid_: Approval flag, execute permission

**Debug Subroutine**:
A support routine that diagnoses one blocker without product-file mutation or delivery authority, while recording bounded BEO diagnosis evidence for the caller.
_Avoid_: Debug phase, repair owner

**Per-Owner Claim**:
A Beads claim model where each BEO owner claims the issue before performing that owner’s lifecycle, artifact, approval, execution, or review writes.
_Avoid_: Plan-only claim, inherited claim

**Done Target**:
The single user-visible outcome that makes an atomic BEO ticket complete.
_Avoid_: Done checklist, acceptance criteria

**Runtime Event Log**:
The append-only `runtime-events.jsonl` artifact for non-normal BEO events, separate from ticket-owned fields and state projections.
_Avoid_: Runtime events field, ticket events

**Repair Budget**:
The mode-specific maximum number of repair attempts allowed before review routes the issue out of the normal repair loop.
_Avoid_: Retry count, loop limit

**Execution Bead**:
A Beads issue selected from the refactor plan because it materially improves BEO drift resistance, safety authority, or operator experience.
_Avoid_: Plan bullet, cleanup task

**Repo-Local Skill**:
A BEO skill that is only promised to operate as part of the full `skills/beo` package with shared registry and doctrine available.
_Avoid_: Globally portable skill, isolated skill

**Standalone Skill**:
A skill package that carries enough local reference material to operate independently from shared BEO registry and doctrine.
_Avoid_: Self-contained copy

## Relationships

- A **Registry** and **Doctrine** together form the preferred **Canonical Authority** for BEO workflow behavior.
- An **Operator Card** depends on **Canonical Authority** instead of duplicating it.
- A **Repo-Local Skill** is the portability baseline for BEO skills.
- A **Standalone Skill** trades lower shared dependency for higher duplication risk.
- A **Routing Reference** should not survive as manually maintained local authority once an **Operator Card** points to the **Registry**.
- A **Ticket Template** belongs with shared BEO reference material, not an individual planning skill.
- **Quick Mode** still follows plan, validate, execute, and review gates.
- **Path Reservation** is off by default in **Quick Mode**, conditional in standard mode, and mandatory for strict or parallel-risk work.
- **PASS_EXECUTE** becomes stale when the repo commit or approved prestate binding changes.
- A **Debug Subroutine** returns evidence to its caller rather than claiming or steering the main Beads lifecycle itself.
- A **Per-Owner Claim** protects each owner’s writes without making one phase inherit another phase’s authority.
- A **Done Target** is checked by one or more acceptance criteria.
- A **Runtime Event Log** is an external artifact, not a field owned inside `TICKET.md`.
- A **Repair Budget** is defined by mode: quick one attempt, standard two attempts, strict explicit.
- An **Execution Bead** should be created only for refactor work with clear drift, safety, or operator-experience ROI.

## Example dialogue

> **Dev:** "Should `beo-plan` keep its own routing file?"
> **Domain expert:** "No — the **Registry** is the **Canonical Authority**; `beo-plan` should be an **Operator Card** that points to the canonical transition IDs."

## Flagged ambiguities

- "source of truth" was used broadly; resolved: use **Canonical Authority** for the artifact family that wins when duplicate workflow descriptions conflict.
- "standalone" was treated as a possible requirement for every BEO skill; resolved: the minimum portability target is **Repo-Local Skill**, not isolated standalone export.
- `ROUTING.md` files were treated as possible local authorities; resolved: a **Routing Reference** should be removed after operator cards point to `pipeline.json`.
- Ticket templates existed both in plan assets and reference templates; resolved: **Ticket Template** means the shared template under `skills/beo/reference/templates/`.
- "quick" was ambiguous between faster artifacts and fewer gates; resolved: **Quick Mode** means compact artifacts, not collapsed phases.
- **Path Reservation** was conditional in `beo-plan` prose but unconditional in `pipeline.json`; resolved: reservation policy should be explicit by mode/profile.
- `PASS_EXECUTE` freshness could mean wall-clock TTL or file-hash checks; resolved: prefer commit-based freshness, with prestate binding as supporting evidence.
- `beo-debug` read-only could mean no writes at all or no product writes; resolved: **Debug Subroutine** may record bounded BEO diagnosis evidence but should not claim/comment the delivery bead by default.
- Claim semantics could be plan-only or broad per-owner; resolved: use **Per-Owner Claim**, with debug verifying caller claim unless it owns a separate debug bead.
- `done` was a list while doctrine required one target; resolved: **Done Target** should be a scalar outcome, with acceptance criteria as the checklist.
- `runtime_events` appeared as both external log and owner field; resolved: use **Runtime Event Log** as a separate append-only artifact.
- `repair_budget_exceeded` existed without a visible budget policy; resolved: define **Repair Budget** per mode.
- The refactor plan listed 100+ issues, but not all bullets deserve execution; resolved: create **Execution Beads** only for issues with clear drift, safety, or operator-experience ROI.
