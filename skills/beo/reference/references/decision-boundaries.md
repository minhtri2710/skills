# Decision Boundaries

Authority: canonical for ask/assume posture, go-mode, Human Gates, secret gate handling, and owner mutation boundaries.

## Ask vs assume

Assume only when the assumption is low-risk, reversible, inside locked scope, and does not change acceptance, approval, security/privacy, legal/business constraints, external access, or user-visible commitments. Record low-risk reversible assumptions in the owning artifact's `assumptions` or `risk_scope`; do not create a Human Gate for a fact that cannot block approval.

Ask or block when guessing could change scope, acceptance, non-goals, compatibility, approval, security/privacy, access, legal/business constraints, user-visible commitments, or irreversible action.

## Go mode

Go mode changes assumption posture only. It never bypasses owner selection, Human Gates, validation, approval freshness, integrity, `PASS_EXECUTE`, declared execution scope, review, or learning thresholds.

## Owner boundary table

| Owner | Owns decision | May write | Must not |
|---|---|---|---|
| `beo-explore` | clarify problem, lock requirements, record Human Gate status | `FEATURE.json`, compact explore fields (`request`, `done`, `human_gates`, `assumptions`, `non_goals`, `constraints`), or full `CONTEXT.md` | approve, execute, review, plan executable scope |
| `beo-plan` | proposed executable scope | compact scope/plan fields including `acceptance_criteria`, or full `PLAN.md` non-Approval sections | approve, execute, review |
| `beo-validate` | readiness, selected execution set, approval ref, integrity, execution mode | compact approval fields or full Approval section only | execute, review, resolve Human Gates |
| `beo-execute` | approved execution-set delivery | declared product files/generated outputs and execution evidence | approve, review, widen scope |
| `beo-review` | phase-terminal verdict | Review section and accepted-review closure bookkeeping | patch, approve |
| `beo-debug` | one blocker root-cause diagnosis | debug diagnosis artifact | patch, approve, plan, verdict |
| `beo-route` | unsafe owner/feature identity repair | STATE/HANDOFF identity metadata and structured owner identity mirrors only when allowed by `state.md` and proven by artifact evidence | normal resume, execute, approve, review |
| `beo-reference` | doctrine lookup and citation | no file writes; returns an answer to the requester only | route, approve, execute, review, author |
| `beo-setup` | repository integration setup/checks | target `AGENTS.md` BEO managed block and setup surfaces only; preserve non-managed `AGENTS.md` content | runtime artifacts, feature execution, unmarked BEO instruction cleanup without confirmation |
| `beo-learn` | accepted learning case or repeated-pattern consolidation | learning case/pattern records | approve, execute, review, doctrine edit |
| `beo-author` | workflow docs and BEO skill contracts | BEO docs named by the request | product feature work, runtime artifacts |

## Human Gate ladder

1. Is a required fact missing? If no, continue.
2. Would guessing affect scope, acceptance, non-goals, compatibility, security, privacy, access, legal, business, approval, user-visible commitment, or irreversible action? If yes, Human Gate.
3. If the answer is already in artifacts, load the legal owner/reference. Use `beo-route` only for unsafe owner/feature identity repair.
4. If safe to proceed around the unknown, narrow scope and declare an assumption; otherwise block.

Human Gate is an authority-preserving stop, not a failure. Every listed gate is approval-bearing until resolved or removed by the owning owner. Do not use Human Gates for soft assumptions; record reversible low-risk unknowns as assumptions instead.

## Human Gate status invariants

Human Gate entries do not carry `severity`, `blocking`, or `approval_bearing` fields. Every listed gate is approval-bearing and blocks approval until resolved or removed by the owning owner.

Aggregate status is a hard invariant:
- `status: not_applicable` means gates are empty or omitted.
- `status: resolved` means every listed gate has `resolution_status: resolved`.
- `status: unresolved` means at least one listed gate has `resolution_status: unresolved`.

Gate types are `clarification`, `choice`, `authorization`, `secret`, and `execution_preview`. Preview requests are modeled as `execution_preview` gates and do not replace approval.

Secret gates store only an external handle such as `env:PROVIDER_API_TOKEN`; secret values must not enter artifacts, logs, hashes, handoffs, review, debug output, or learning.

## Human Gate lifecycle

| Phase | Owner | Responsibility | Must not |
|---|---|---|---|
| Discover | `beo-explore` | identify Human Gates and record status | plan scope or approve |
| User input | `user` | provide required decision/secret/authorization | write artifacts |
| Record answer | `beo-explore` | update gate status and `resolution_ref` | approve or execute |
| Scope selection | `beo-plan` | stop if required user input blocks scope | resolve gates |
| Readiness | `beo-validate` | evaluate recorded gate status | resolve gates |
| Execution | `beo-execute` | require resolved/not_applicable gates before mutation | bypass gates |
| Review | `beo-review` | check execution evidence respected gates | retroactively approve missing gates |

`beo-validate` evaluates gate status only; it never resolves gates. If the user answered a gate but `beo-explore` has not recorded current status, return to `beo-explore`. Missing, stale, or contradictory gate status fails closed.
