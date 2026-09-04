# Intake Policy

Use this policy before creating a pane, agent, tab, or workspace for delivery work. Intake is a routing gate, not a ceremony checklist; it also decides whether the one issue in flight is run in declared solo-Lead mode or partitioned across Engineers. Choose the smallest lane that honestly covers blast radius, reversibility, uncertainty, and proof weakness.

## Repository guidance

Before classifying the lane or staffing an agent, read the repository's root `AGENTS.md` and the nested `AGENTS.md` files covering the paths this work owns. The root file carries the repository map, global invariants, canonical docs, and commands; a nested file carries subtree ownership, local invariants, local commands, and guardrails. Use the repository's own plan, workspace-protocol, and verification formats when it defines them.

Load context in proportion to the work: the repository map plus the contracts the outcome actually needs. Do not force indiscriminate exploration and do not turn a document catalog into a mandatory checklist. Repository guidance may add stricter local invariants; it may not weaken this workflow's safety boundaries. Name the guidance that governs the work in the intake record and pass it into every charter.

## Project config

Read the Human-owned project config at `~/.herdr/projects/<project-slug>/config.md` before classifying the lane or staffing an agent; `project-config.md` owns its format, precedence, and guards. When the file is absent, do not assume defaults: ask the Human whether to create one for this project and act only on their answer, recording `Config: none` only after they decline (`project-config.md`). Record the applied keys, or `Config: none`, in the intake record. A `lane-defaults` entry raises a lane floor only; hard-gate classes and Human gates are not configurable.

## Lanes

### Tiny

The work is local, low-risk, reversible, and directly verifiable. Keep the affected truth current. Use the lightweight Herdr route unless another agent or topology is explicitly needed. Create no durable planning or process artifact unless truth, a material decision, or handoff continuity must survive the current run.

### Normal

The work has a bounded owner and contract, a local rollback path, and an honest validation route. Create no durable planning or process artifact unless truth, a material decision, or handoff continuity must survive the current run. An active plan is not required by default for this lane.

### High-risk

The work has material security, authorization, privacy, audit, data, public-contract, migration, external-effect, runtime-boundary, cross-platform, concurrency, lifecycle, ordering, or performance impact; irreversible state; broad uncertainty; weak proof; or a restart/handoff that could materially damage continuity, ownership, state, or evidence. Make an active bounded plan before implementation.

## Hard-gate classes

Route the work as high-risk and stop for the applicable design or Human decision when it includes:

- material authentication, authorization, privacy, audit, secret-handling, credentials, or permission changes;
- data loss, irreversible migration, deletion, retention, replay, recovery, or reset behavior, except that a dormant capability is not itself the hard gate when the no-wiring and invocation-path conditions below are evidenced;
- money, user-visible delivery, non-idempotent external effects, push, pull-request mutation, merge, deploy, or another external write;
- coordinated replacement of a current contract, schema, protocol, authority, or implementation path;
- a compatibility, fallback, dual-read, dual-write, shim, facade, legacy parser, read-time upgrade, migration path, or version branch request;
- material runtime owner-boundary, lifecycle, concurrency, ordering, cancellation, cleanup, or cross-platform changes;
- weakening proof that protects a real security, data, contract, runtime, or external-system claim.

A dormant capability that can perform an irreversible action is not, by that fact alone, in the hard-gate class. The delivery must pin no-wiring as a named contract and evidence it, and must establish by reading the comparable script's invocation mechanism whether the build or deploy path reaches it. If either no-wiring or the actual invocation path and build/deploy reachability is missing, treat the irreversible action as a hard gate. A compatibility request is not an ordinary implementation detail. First identify the repository's actual compatibility obligation. If no such obligation is documented, require an explicit design decision and Human ruling before preserving an old path or adding alternate semantics. Do not silently treat compatibility machinery as harmless, and do not reject a documented public obligation without recording the conflict.

A label alone does not determine the lane. Material impact, irreversibility, uncertainty, or weak proof does.

## Design gate

Before implementation, resolve any choice that materially changes ownership, public behavior, safety, compatibility, data consequences, or another expensive-to-reverse direction. Record:

- constraints and governing contracts;
- meaningful alternatives;
- the chosen decision and why it fits the outcome;
- likely failure modes and disconfirming checks;
- the owner of the resulting lifecycle and evidence;
- any required Human decision.

Describe the outcome and boundary, not private file choreography or pseudocode. Do not prescribe private implementation details unless they are themselves part of a public or owner contract.

Human confirmation is required when requested behavior, destructive scope, external mutation, security consequence, compatibility obligation, or proof weakening remains materially ambiguous.

## High-risk plan

Before implementation, make a small active plan. Use a repository-defined plan format and location when one exists. Otherwise keep the plan in the current Herdr run context and record:

- outcome and in-scope/out-of-scope boundaries;
- owners and governing repository contracts;
- material constraints, design decisions, and alternatives rejected;
- ordered implementation slices and dependencies;
- claim-shaped validation for each slice;
- rollback, recovery, and stop conditions;
- unresolved risks and required Human gates.

The plan remains active until the Lead accepts the work or explicitly closes or supersedes it. Do not create a large planning framework merely to imitate a formal process.

## Partition

After the lane is classified and before any Engineer is staffed, analyze the issue against the code and decide the delivery mode and, in `partitioned` mode, how many Engineers it gets. The delivery runs on one branch in one shared working tree, so the only thing that keeps two agents from corrupting each other's work is that they never touch the same path. The partition is that guarantee, written down before anyone edits.

`partitioned` mode staffs one or more Engineers. `solo-Lead` mode is declared at intake, is not a config key or fallback, staffs zero Engineers for the whole run, and records the Lead-owned scope; a run that staffed an Engineer which then died restaffs or blocks, never entering solo-Lead. One scope is the base case and needs no justification. In `partitioned` mode, split into several scopes only when all of the following hold on the evidence, not on the issue title:

- each scope's owned paths are disjoint from every other scope's, stated as concrete paths or globs;
- no scope changes a contract another scope consumes — an interface, exported type, schema, shared config, dependency manifest, lockfile, generated file, or build definition. A change like that is a contract slice: run it first with one agent, quiesce and commit, then partition the rest against the new head. A contract that does not exist yet is different: when the Lead pins it in both charters — path, signature, and behavior — the producing and consuming scopes can run in parallel, because neither edits a file the other owns and the final head is what gets checked; the consumer's charter then says the module is absent while it works and that it mocks the pin rather than stubbing the producer's path; leave it unpinned and the consumer becomes a second wave;
- each scope's claim can be checked on the final quiet head with the recorded acceptance commands;
- the scope count stays within `worker-cap` (default 3, project config). Merge small scopes rather than queueing a second wave.

Paths no scope owns — the root config, lockfiles, generated output, shared fixtures — belong to no Engineer. A change there is routed by the Lead as a sequential slice or a `DEPENDENCY_REQUEST` ruling, never picked up by whichever agent reaches it first. In `solo-Lead` mode, the Lead owns the declared source scope directly and no Engineer owns any path.

Each scope inherits the delivery's lane, plan, gates, and validation claims; the partition never lowers any of them. If the analysis shows the issue cannot be split honestly, say so and run one scope; a partition that exists to look parallel is two writers on one tree with a label.

## Intake record

Before mutation, state this compact result in the Lead's current run context:

```text
Lane: tiny | normal | high-risk
Reason: <material reason for the lane>
Lead: lead-<project-slug>
Supervisor: supervisor | none
Owners: <Lead, Engineer/Reviewer owners, governing contracts>
Guidance: <the repository guidance that governs this work, or none found>
Plan: <active plan reference or none>
Validation: <claim-shaped checks and expected outcomes>
Mode: partitioned | solo-Lead
Partition: <partitioned scope name: owned paths, one line per scope; or solo-Lead owned scope>
Config: <applied project-config keys or none>
```

Include target repository/product line, exclusions, base/merge-base, dependencies, Human gates, and Herdr resources created by the run alongside this result. Name the Lead seat before writing it (`lead-policy.md`, "Seats") and look up the Supervisor seat once. Pass the lane, plan reference, governing contracts, validation claims, the Lead seat name, and the scope's owned paths and peer scopes into every relevant charter.

## Reopen rule

An implementation or review finding that fails a premise of the charter, or increases blast radius, irreversibility, uncertainty, ownership impact, or proof weakness, reopens intake. Stop before crossing the new boundary and report `REOPEN_REQUEST` in the one shape it has, under `lead-policy.md`, "Escalation routing".

Do not lower the lane to keep work moving. Do not let a local fix silently become a contract, architecture, security, data, or external-effect change.
