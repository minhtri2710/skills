---
name: design
description: "Design decisions before implementation. Use when creating or reshaping HTTP or RPC endpoints, defining request and response types between a frontend and a backend or between services, or deciding error format, pagination, or idempotency for retried writes; when designing or comparing a module's interface, placing a seam, or finding deepening opportunities in a named area; when the user explicitly asks to audit whether a whole project is the right kind of system; or when a throwaway prototype should answer one design question, such as whether a state machine, data shape, or API surface holds up, or what a screen could look like. Do not use to build the real feature or for an ordinary architecture review."
---

# Design

Four branches, each a complete contract. Match the work to a row (more than one can
match), read that branch's file in full before acting, and follow it. When no row
matches, this skill does not apply. After a context compaction, read the branch file
again before continuing: compaction can keep this file and drop the branch file.

In a branch file, "this skill" means that branch, a branch named there is a row of this
table, and `<this-skill>` in a command is this skill's directory.

| Branch | Use it when | Read |
| --- | --- | --- |
| `api-contract-design` | Design the contract of an HTTP or RPC API before implementing it: resource shape, one error format, boundary validation, pagination, naming, and correct idempotency for state-changing calls. Use when creating or reshaping endpoints, defining the request and response types between a frontend and a backend or between services, or when retries, duplicates, or timeouts on a write need a deliberate answer. Do not use for an in-process module interface; that is a seam question. | `references/api-contract-design.md` |
| `deep-module-design` | Design or deepen a module's interface and seam placement using the deep-module vocabulary. Use when the user wants to design a module interface, decide where a seam goes, find deepening opportunities in a named area, or compare alternative interfaces. Do not use for a whole-project archetype audit. | `references/deep-module-design.md` |
| `architecture-premise-audit` | Audit a whole project for a possibly wrong system archetype by deriving expected product capabilities before trusting repository vocabulary. Use only for an explicitly requested broad premise audit, not ordinary architecture review or one named design concern. | `references/architecture-premise-audit.md`; it uses `references/architecture-premise-audit-structural-antipatterns.md` |
| `throwaway-prototype` | Build throwaway code that answers one design question, either a single-file HTML demo that drives a state model or several structurally different UI variants on one route. Use when the user wants to feel out whether a state machine, data shape, or API surface holds up, or to see a few options for what a screen should look like, before committing to an implementation. Do not use to build the real feature, to test production code, or to design or polish the real UI of an existing screen. | `references/throwaway-prototype.md` |
