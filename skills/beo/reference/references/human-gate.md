# Human Gate

## HG-01 — Approval and UAT gates never fallback to go-mode

Approval and UAT gates never fallback to go-mode. Clarification gates may use go-mode fallback only when the canonical go-mode rule permits it (GO-01).

Required Human Gate blocks `PASS_EXECUTE` unless status is `resolved` or `not_applicable` with an explicit N/A reason.

## HG-02 — Secret material must not be persisted

Secret material must not be persisted in Human Gate records. For `secret` gates, record only that the secret was provided or access was confirmed. Do not record the secret value.

## When to ask

Before asking the user, answer: Can this answer change acceptance, user-visible scope, non-goals, existing user/data support, security/privacy/business/legal constraints, external access, secrets, approval, or UAT? If no, do not ask. Decide inside locked scope.

Ask the user only when the answer can affect:

- acceptance
- user-visible scope
- non-goals
- existing user/data support
- security, privacy, business, or legal constraints
- external access
- secrets
- approval
- UAT

Do not ask the user for implementation preferences the current owner can safely decide inside locked scope.

Ask one blocking Human Gate question per round unless grouping is necessary to unblock the same acceptance decision.

## Gate types

- `clarification`
- `approval`
- `UAT`
- `external_access`
- `secret`
- `legal_business`

## Human Gate output shape

```md
Human Gate:
Type:
Question:
Why blocking:
Fallback allowed: yes/no
Secret persisted: no
```
