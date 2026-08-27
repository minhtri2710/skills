# Structural Misfit Policy

Use these lenses only when architecture, ownership, lifecycle, protocol shape, scalability, latency, compatibility machinery, proof quality, or a local-patch-versus-foundation decision is materially in question. They are conditional search lenses, not a checklist that every design must satisfy.

Report only evidence-backed concerns inside the assigned scope. A custom design is not inherently wrong; visible complexity is justified when the domain requires it at proportionate cost.

## Causal mechanism

Look for:

- **Wrong product category:** the whole system behaves like a different class of product than the goal, workload, scale, latency, cost, or operating model requires.
- **Imported completeness:** the design perfects a capability mature systems deliberately omit, constrain, approximate, precompute, or move offline. Machinery proving that a capability can exist does not prove the product should pay for it.
- **Mechanism-free claim:** a name promises an outcome but the required state or causal process does not exist. Examples include prediction without simulation/history, reconciliation without authoritative correction, lifecycle without an owning state machine, idempotency without identity/binding, and durability without a durable commit mechanism.
- **Homemade proxy:** a timer, counter, retry, interpolation, snapshot, acknowledgment, or partial state copy is presented as prediction, navigation, admission, reconciliation, backpressure, transactionality, or completion without carrying the required semantics.
- **Information insufficiency:** the owner cannot compute its claimed output from the data it receives, so callers or downstream consumers guess missing facts.
- **Wrong archetype:** exact transactional work is modeled as latest state, rapidly supersedable state is journaled as exact work, keyed current state is stored as an append-only queue, or eventual snapshots enforce a transition needing total ordering.

## Mechanism examples

Use these as domain-neutral examples, not mandatory checks:

- **Prediction** needs retained state or history, local application, and a correction/resimulation mechanism; a one-time step or snapshot is not prediction by name.
- **Reconciliation** needs authoritative truth or progress plus a rule for correction, replay, or conflict resolution; an acknowledgment or partial record is not reconciliation by itself.
- **Authoritative routing** needs an owned, validated route or equivalent support facts; interpolating toward a target does not acquire route semantics by name.
- **Supersedable state** and **exact commands** need different delivery semantics: latest-state replacement can discard obsolete values, while exact work needs durable identity, ordering, and terminal outcomes.
- **Expensive rollback or exact journaling** needs a named product constraint that justifies its storage, ordering, and recovery cost.

## Weak-foundation accommodation

Look for a wrapper, adapter, cache, fallback, retry loop, ordering rule, or feature flag that owns cancellation, invalidation, reset, synchronization, failure, or lifecycle semantics that belong in the dependency or owning module.

Also look for duplicate state or a parallel implementation kept only because the foundation is hard to repair; an interface that exposes insufficient identity, admission, capacity, cancellation, typed output, or terminal semantics; a raw escape hatch, legacy path, test constructor, manual bootstrap, or fabricated accepted state that is the only complete route; or a local workaround that remains after the owner could be repaired.

## Bent code shape

Look for repeated special cases, mode flags, lossy translations, synthetic states treated as physical facts, collapsed error taxonomies, duplicated counters, and impossible state combinations used to bridge incompatible owners.

Look for modules that must know another module's private queue, timing, allocation, reset behavior, or cleanup; caller-side retry/polling/timeout growth caused by a missing terminal transition; compatibility facades preserving obsolete authority; multiple layers converting the same fact without adding information, isolation, ownership, or policy; pass-through interfaces nearly as complex as the implementation; or a custom parallel pipeline fighting a framework/toolchain owner and creating synchronization or artifact-parity tax.

## Avoidable taxes

Check whether the design introduces:

- **Latency and ordering tax:** head-of-line blocking, global ordering for independent work, extra round trips, synchronous coordination, or reliable delivery for values whose older versions are obsolete.
- **Bandwidth and amplification tax:** duplicate carriers, catch-up bursts, redundant snapshots, full-state publication where bounded deltas/current state suffice, or per-client products that could be shared safely.
- **Hot-path tax:** per-tick allocation, repeated encoding/decoding, avoidable copies, total-entity scans, locks across independent owners, or expensive reconstruction at the wrong frequency. Performance work that mainly recovers abstraction overhead is evidence of tax.
- **Buffering and failure tax:** unbounded queues, retry without terminal classification, overflow converted into session death, fallback with different semantics, or recovery that revives stale work.
- **Ownership and operations tax:** shadow authority, cross-module lifecycle coupling, process multiplication, hidden recovery state, hard-to-observe partial failure, or a larger blast radius than the product claim requires.
- **Migration and proof tax:** permanent dual paths, compatibility branches without an external obligation, tests that duplicate implementation, evidence that cannot cross the production route, or validation cost inflated by abstraction.
- **Cognitive maintenance tax:** generic vocabulary hiding domain rules, impossible states, configuration combinations with no product meaning, or an extension surface larger than real use cases.

## Overengineering

Look for a generic framework, projection bank, plugin system, compatibility layer, or public abstraction created before a real second use case requires it; a full state machine/schema advertising states the runtime cannot produce or consume; temporary scaffolding or parallel owners where one coherent final-state change exists; multiple services, queues, review artifacts, or coordination layers replacing a direct owner call without adding required isolation or scale; speculative failure taxonomies/configurability obscuring the current mechanism; or perfect modeling where a hard constraint, authored table, bounded approximation, precomputation, or explicit scope omission would satisfy the outcome.

## Local-excellence trap

Passing tests, polished modules, internal coherence, strong benchmarks, realism, repository precedent, and a small diff do not establish archetype fit. Ask whether the whole would still look strange if every local detail were excellent, which machinery exists only to support the macro choice, and what disappears under the boring route. Existing precedent may be accumulated drift rather than evidence that the category is correct.

## Boundary and proof laundering

Look for transport send, acknowledgment, queue drain, connection state, timestamp adjacency, or log presence being treated as application acceptance, authoritative mutation, command completion, or user-visible outcome.

Look for downstream parsing of payloads, timing, logs, or counters to infer a typed semantic product the owner should publish directly; a mock, replica, fixture, source scan, compile success, or isolated green suite cited for a production causal chain it never reaches; or individually green components with no production entry connecting them to the named authority.

## Assessment result

When a lens is triggered, report only what the evidence supports:

```text
Assessment: STANDARD_FIT | JUSTIFIED_DEVIATION | STRUCTURAL_CONCERN
Evidence: <file/path, runtime observation, trace, or reproducible check>
Claim affected: <the outcome or contract at risk>
Tax: <latency, ownership, proof, cognitive, or other concrete cost>
Owner-clean alternative: <the smallest durable route, or none identified>
Disconfirming check: <what would falsify the concern>
```

Use `STANDARD_FIT` when the production mechanism has the required information and owner. Use `JUSTIFIED_DEVIATION` when a named constraint makes the deviation worthwhile at proportionate cost and the counterexample is handled. Use `STRUCTURAL_CONCERN` only when evidence shows a missing mechanism, wrong owner, avoidable tax, or proof boundary failure.
