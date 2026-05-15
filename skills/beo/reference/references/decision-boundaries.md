# Decision Boundaries

Authority: canonical for ask/assume posture, go-mode, Human Gates, and secret gate handling.

## Ask vs assume

Assume only when the assumption is low-risk, reversible, inside locked scope, and does not change acceptance, approval, security/privacy, legal/business constraints, or external access. Ask when the answer can change scope, acceptance, non-goals, compatibility, approval, security/privacy, access, legal/business constraints, or user-visible commitments.

Record low-risk reversible assumptions in `assumptions` or `risk_scope`. Do not create a Human Gate for an assumption that cannot block approval.

## Go mode

Go mode changes assumption posture only. It never bypasses owner selection, Human Gates, validation, approval freshness, integrity, `PASS_EXECUTE`, declared execution scope, review, or learning thresholds.

## Human Gates

A Human Gate is a required human decision that can block approval because it can affect scope, acceptance, non-goals, compatibility, approval, security/privacy, access, legal/business constraints, or business commitments.

Human Gate status is approval-bearing. `PASS_EXECUTE` is blocked unless status is `resolved` or `not_applicable`. User answers affect runtime only after the owning owner records the resolution in the canonical artifact.

Do not use Human Gates for soft assumptions. If an assumption later becomes approval-blocking, `beo-explore` records or updates the Human Gate before validation.

Human Gate entries do not carry `severity`, `blocking`, or `approval_bearing` fields. Every listed gate is approval-bearing until resolved or removed by the owning owner.

Aggregate status is a hard invariant:
- `status: not_applicable` means gates are empty or omitted.
- `status: resolved` means every listed gate has `resolution_status: resolved`.
- `status: unresolved` means at least one listed gate has `resolution_status: unresolved`.

Canonical shape:

```yaml
human_gates:
  status: resolved | unresolved | not_applicable
  gates:
    - id: HG-1
      type: clarification | choice | authorization | secret | execution_preview
      question: <human-facing decision>
      affects: [scope | acceptance | security | access | business | approval]
      resolution_status: resolved | unresolved
      resolution_ref: <artifact section | user message ref | env:HANDLE>
      notes: <optional, no secrets>
```

Gate types are `clarification`, `choice`, `authorization`, `secret`, and `execution_preview`.

Secret gates store only an external handle such as `env:PROVIDER_API_TOKEN`; secret values must not enter artifacts, logs, hashes, handoffs, review, debug output, or learning.

Preview requests are modeled as `execution_preview` gates and do not replace approval.

## Human Gate lifecycle
<!-- beo:human-gate:lifecycle -->

| Phase | Owner | Responsibility | Must Not Do |
|---|---|---|---|
| Discover | `beo-explore` | identify Human Gates and record status | plan scope or approve |
| User input | `user` | provide required decision/secret/authorization | write artifacts |
| Record answer | `beo-explore` | update gate status and `resolution_ref` | approve or execute |
| Scope selection | `beo-plan` | stop if required user input blocks scope | resolve gates |
| Readiness | `beo-validate` | evaluate recorded gate status | resolve gates |
| Execution | `beo-execute` | require resolved/not_applicable gates before mutation | bypass gates |
| Review | `beo-review` | check execution evidence respected gates | retroactively approve missing gates |

`beo-validate` evaluates gate status only; it never resolves gates. If the user answered a gate but `beo-explore` has not recorded current status, return to `beo-explore`. Missing, stale, or contradictory gate status fails closed.
