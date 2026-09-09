# Structural Misfit Policy

Use these lenses only when architecture, ownership, lifecycle, protocol shape, scalability, latency, compatibility machinery, proof quality, or a local-patch-versus-foundation decision is materially in question. They are conditional search lenses, not a checklist every design must satisfy. This file is shared: `lead.md` cites it, and the Lead copies the relevant lenses into a charter when a Peer needs them (Peers read only their charter). Report only evidence-backed concerns inside the assigned scope. A custom design is not inherently wrong; visible complexity is justified when the domain requires it at proportionate cost.

## Causal mechanism

- **Wrong product category:** the whole system behaves like a different class of product than the goal, workload, scale, latency, cost, or operating model requires.
- **Imported completeness:** the design perfects a capability mature systems deliberately omit, constrain, approximate, precompute, or move offline. Proving a capability can exist does not prove the product should pay for it.
- **Mechanism-free claim:** a name promises an outcome but the required state or causal process does not exist — prediction without simulation/history, reconciliation without authoritative correction, lifecycle without an owning state machine, idempotency without identity/binding, durability without a durable commit.
- **Homemade proxy:** a timer, counter, retry, interpolation, snapshot, acknowledgment, or partial state copy is presented as prediction, navigation, admission, reconciliation, backpressure, transactionality, or completion without carrying the required semantics.
- **Information insufficiency:** the owner cannot compute its claimed output from the data it receives, so callers or downstream consumers guess missing facts.
- **Wrong archetype:** exact transactional work modeled as latest state, rapidly supersedable state journaled as exact work, keyed current state stored as an append-only queue, or eventual snapshots enforcing a transition needing total ordering.

## Mechanism examples

Domain-neutral examples, not mandatory checks:

- **Prediction** needs retained state or history, local application, and a correction/resimulation mechanism; a one-time step or snapshot is not prediction by name.
- **Reconciliation** needs authoritative truth or progress plus a rule for correction, replay, or conflict resolution; an acknowledgment or partial record is not reconciliation by itself.
- **Authoritative routing** needs an owned, validated route or equivalent support facts; interpolating toward a target does not acquire route semantics by name.
- **Supersedable state** and **exact commands** need different delivery semantics: latest-state replacement can discard obsolete values, while exact work needs durable identity, ordering, and terminal outcomes.
- **Expensive rollback or exact journaling** needs a named product constraint that justifies its storage, ordering, and recovery cost.

## Weak-foundation accommodation

Look for a wrapper, adapter, cache, fallback, retry loop, ordering rule, or feature flag that owns cancellation, invalidation, reset, synchronization, failure, or lifecycle semantics belonging in the dependency or owning module. Also: duplicate state or a parallel implementation kept only because the foundation is hard to repair; an interface exposing insufficient identity, admission, capacity, cancellation, typed output, or terminal semantics; a raw escape hatch, legacy path, test constructor, manual bootstrap, or fabricated accepted state that is the only complete route; or a local workaround that remains after the owner could be repaired.

## Bent code shape

Look for repeated special cases, mode flags, lossy translations, synthetic states treated as physical facts, collapsed error taxonomies, duplicated counters, and impossible state combinations used to bridge incompatible owners. Also: modules that must know another module's private queue, timing, allocation, reset behavior, or cleanup; caller-side retry/polling/timeout growth caused by a missing terminal transition; compatibility facades preserving obsolete authority; multiple layers converting the same fact without adding information, isolation, ownership, or policy; pass-through interfaces nearly as complex as the implementation; or a custom parallel pipeline fighting a framework/toolchain owner and creating synchronization or artifact-parity tax.

## Avoidable taxes

- **Latency and ordering:** head-of-line blocking, global ordering for independent work, extra round trips, synchronous coordination, or reliable delivery for values whose older versions are obsolete.
- **Bandwidth and amplification:** duplicate carriers, catch-up bursts, redundant snapshots, full-state publication where bounded deltas/current state suffice, or per-client products that could be shared safely.
- **Hot-path:** per-tick allocation, repeated encoding/decoding, avoidable copies, total-entity scans, locks across independent owners, or expensive reconstruction at the wrong frequency. Performance work that mainly recovers abstraction overhead is evidence of tax.
- **Buffering and failure:** unbounded queues, retry without terminal classification, overflow converted into session death, fallback with different semantics, or recovery that revives stale work.
- **Ownership and operations:** shadow authority, cross-module lifecycle coupling, process multiplication, hidden recovery state, hard-to-observe partial failure, or a larger blast radius than the product claim requires.
- **Migration and proof:** permanent dual paths, compatibility branches without an external obligation, tests that duplicate implementation, evidence that cannot cross the production route, or validation cost inflated by abstraction.
- **Cognitive maintenance:** generic vocabulary hiding domain rules, impossible states, configuration combinations with no product meaning, or an extension surface larger than real use cases.

## Overengineering

Look for a generic framework, projection bank, plugin system, compatibility layer, or public abstraction created before a real second use case requires it; a full state machine/schema advertising states the runtime cannot produce or consume; temporary scaffolding or parallel owners where one coherent final-state change exists; multiple services, queues, review artifacts, or coordination layers replacing a direct owner call without adding required isolation or scale; speculative failure taxonomies/configurability obscuring the current mechanism; or perfect modeling where a hard constraint, authored table, bounded approximation, precomputation, or explicit scope omission would satisfy the outcome.

## Local-excellence trap

Passing tests, polished modules, internal coherence, strong benchmarks, realism, repository precedent, and a small diff do not establish archetype fit. Ask whether the whole would still look strange if every local detail were excellent, which machinery exists only to support the macro choice, and what disappears under the boring route. Existing precedent may be accumulated drift rather than evidence the category is correct.

## Boundary and proof laundering

Look for transport send, acknowledgment, queue drain, connection state, timestamp adjacency, or log presence treated as application acceptance, authoritative mutation, command completion, or user-visible outcome. Also: downstream parsing of payloads, timing, logs, or counters to infer a typed semantic product the owner should publish directly; a mock, replica, fixture, source scan, compile success, or isolated green suite cited for a production causal chain it never reaches; or individually green components with no production entry connecting them to the named authority.

## Second opinion

A `COUNCIL_REQUEST` is an optional bounded gate, not a stage of delivery. Use it only after ordinary local analysis leaves patch-versus-foundation materially undecided, and only when the decision is expensive to reverse. Staff one Architect Peer (`lead.md`, "Writing charters"): a kind differing from every Engineer's when available, read-only access to the shared checkout at the exact head when one exists or the recorded quiesce state otherwise, no mutation, no subagents, no background work, a sealed seat, and one evidence-bound `Assessment` sent to the Lead by prompt as its final report. Name the exact head or quiesce state, the competing routes, and the specific question. The Lead retains the ruling and routes the outcome; the Architect's authority is fixed in `lead.md`, "Writing charters" (Disposition: Architect). Do not staff an Architect for routine bounded work, stack Architects to break a tie, or manufacture dissent when the evidence supports agreement.

## Assessment result

When a lens is triggered, report only what the evidence supports, in the shape of `templates/architect-assessment.txt`. Use `STANDARD_FIT` when the production mechanism has the required information and owner; `JUSTIFIED_DEVIATION` when a named constraint makes the deviation worthwhile at proportionate cost and the counterexample is handled; `STRUCTURAL_CONCERN` only when evidence shows a missing mechanism, wrong owner, avoidable tax, or proof boundary failure.
