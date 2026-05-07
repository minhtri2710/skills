# BEO Complexity v2

## Runtime lanes

BEO v2 has only two runtime lanes:

- `beo_tiny`
- `standard`

Do not use micro-compact, small-change, standard-feature, high-ceremony, or planning-depth lane names as runtime authority.

## Tiny path

`beo_tiny` reduces artifact size and prose only. It never bypasses owner transitions, validation, approval, execution-set selection, review, or learning disposition.

Tiny is allowed only when all are true:

- one active feature
- locked requirements are clear
- one selected bead
- narrow declared file scope
- no unresolved Human Gate
- no security/privacy/migration/destructive/permission/billing/compatibility risk
- verification is direct and cheap
- no upward reclassification occurred

Tiny still requires locked requirements, compact plan, validate readiness, fresh `approval_ref`, selected execution set, execution inside scope, review-lite only when review-lite gates pass, and learning disposition.

## Upward reclassification

If live scope, risk, ambiguity, generated outputs, verification complexity, or unresolved human decisions outgrow `beo_tiny`, reclassify before `PASS_EXECUTE`.

Upward reclassification suspends inherited go-mode.
