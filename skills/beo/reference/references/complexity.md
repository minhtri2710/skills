# BEO Complexity

## Runtime lanes

BEO has only two runtime lanes:

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

Tiny still requires locked requirements, compact plan, validate readiness, fresh `approval_ref`, selected execution set, execution inside scope, same accept gate with shorter prose, and learning disposition.

## Upward reclassification

If live scope, risk, ambiguity, generated outputs, verification complexity, or unresolved human decisions outgrow `beo_tiny`, reclassify before `PASS_EXECUTE`.

Upward reclassification suspends inherited go-mode.


## Generated outputs in tiny path

`beo_tiny` may include generated outputs only when they are explicitly declared, deterministic, and reviewed through the same bundle/hash path.

Undeclared, broad, or nondeterministic generated outputs reclassify to `standard`.


## Tiny exit criteria

A `beo_tiny` feature must reclassify to `standard` before `PASS_EXECUTE` if any appears:

- more than one selected bead
- unclear or contradicted acceptance
- unresolved Human Gate
- unresolved approval or UAT requirement
- security/privacy/migration/destructive/permission/billing/compatibility risk
- undeclared generated output
- nondeterministic generated output
- file scope expands beyond the original narrow scope
- verification is no longer direct and cheap
- rollback boundary is non-trivial

Reclassification suspends inherited go-mode.
