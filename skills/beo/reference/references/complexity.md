# BEO Complexity

## Runtime lanes

BEO has only two runtime lanes: `beo_tiny`, `standard`.

Do not use informal lane aliases as runtime authority.

## TINY-01 — Tiny reduces artifact size and prose only

`beo_tiny` reduces artifact size and prose only. It never bypasses owner transitions, validation, approval, execution-set selection, review, or learning case recording.

## TINY-02 — Upward reclassification to standard

Upward reclassification to standard suspends inherited go-mode before `PASS_EXECUTE`.

Reclassify to standard before `PASS_EXECUTE` when any appears:

- more than one selected bead
- unclear or contradicted acceptance
- unresolved Human Gate
- unresolved approval or UAT requirement
- security/privacy/data-change/destructive/permission/billing/existing-user-data-support risk
- undeclared generated output
- nondeterministic generated output
- file scope expands beyond the original narrow scope
- verification is no longer direct and cheap
- rollback boundary is non-trivial
- implementation requires investigation beyond locked scope
- root cause is unproven
- review cannot be cold from ticket evidence
- dependencies across unrelated files

## Tiny compact packet

A `beo_tiny` feature should fit this shape:

- Feature: `<slug>`
- Acceptance: `<one clear outcome>`
- Non-goals: `<one line or N/A>`
- Scope: `<narrow declared files>`
- Bead: `<one selected bead>`
- Verification: `<direct cheap check>`
- Human Gates: `none` or `<blocking gate>`
- Risk: `N/A` for all risk categories
- Approval: fresh `approval_ref` required before execution
- Review: same accept gate, shorter prose
- Learning: `none` unless a concrete learning case is routed to compound

## Tiny exit criteria

A `beo_tiny` feature must reclassify to `standard` before `PASS_EXECUTE` if any criterion in TINY-02 is met.

## Generated outputs in tiny path

`beo_tiny` may include generated outputs only when they are explicitly declared, deterministic, and reviewed through current execution evidence. Undeclared, broad, or nondeterministic generated outputs reclassify to `standard`.

## Tiny lane rules

1. Lane value must be `beo_tiny`. Do not write `tiny`.
2. Do not add fenced JSON approval envelope to `TICKET.md`.
3. Keep approval fields normalized using canonical readiness and integrity vocabulary.
4. Keep `## Risk` and `## Human Gates` as separate headings unless helper parser is updated in the same phase.
5. If tiny needs multiple meaningful BR beads, reclassify to standard (TINY-02).
6. Tiny review can record `learning_source` in `TICKET.md`; this is canonical for tiny.
7. STATE may mirror tiny `learning_source` but loses to `TICKET.md`.
8. Tiny helper compatibility: before changing tiny headings or field labels, update helper parser in the same phase or keep existing headings/labels.
