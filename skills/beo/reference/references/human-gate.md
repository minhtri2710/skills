# Human Gate v2

## Human Gate discipline

Ask the user only when the answer can affect:

- acceptance
- user-visible scope
- non-goals
- compatibility
- security, privacy, business, or legal constraints
- external access
- secrets
- approval
- UAT

Do not ask the user for implementation preferences the current owner can safely decide inside locked scope.

Ask one blocking Human Gate question per round.

## Gate types

- `clarification`
- `approval`
- `UAT`
- `external_access`
- `secret`
- `legal_business`

## Fallback rule

Clarification gates may use go-mode fallback only when the canonical go-mode rule permits it.

Approval and UAT gates never fallback.

Secret material must not be persisted in Human Gate records.
