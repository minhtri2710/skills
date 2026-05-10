# Go-Mode

## GO-01 — Go-mode is posture-only

Go-mode changes assumption posture only.

It does not bypass:

- owner selection
- Human Gates of any type (HG-01)
- UAT gates (HG-01)
- approval freshness (APP-01)
- integrity verification (INT-01)
- `PASS_EXECUTE` (APP-02)
- execution scope (APP-05)
- BR/PLAN consistency
- review (REV-01)
- learning thresholds (LEARN-01)

## GO-02 — Entry

Go-mode is active only when user explicitly says a phrase equivalent to:
- "go"
- "continue"
- "proceed"
- "do it"
- "no more questions unless blocked"

## GO-03 — Behavior

In go-mode:
- Avoid non-essential questions.
- Make reversible implementation-detail choices inside locked scope.
- Record assumptions.
- Continue through legal owner handoffs.
- Stop for Human Gates.
- Stop for approval requirements.
- Stop for stale integrity.
- Stop for scope/acceptance ambiguity.
- Stop for legal/security/privacy/access blockers.

## GO-04 — Assumption recording

Owners may record assumptions only when:
- Assumption does not affect acceptance.
- Assumption does not expand scope.
- Assumption does not change security/privacy/access/legal/business constraints.
- Assumption is reversible inside approved envelope.

## GO-05 — Suspend go-mode on these events

Suspend when:

- scope expands
- triage class increases (TINY-02)
- requirements become contradicted
- security/privacy/data-change/destructive risk appears
- a non-fallback Human Gate appears (HG-01)
- approval invalidates (APP-03)
- tiny reclassifies to standard (TINY-02)
- user request changes acceptance
- owner identity is unsafe
- root cause must be proven before mutation/verdict

Upward reclassification suspends inherited go-mode before `PASS_EXECUTE` or `accept`.

## GO-06 — Exit

Go-mode exits when:
- User asks to stop.
- Human Gate is active.
- Approval is missing/stale.
- Scope or acceptance ambiguity appears.
- Owner identity is unsafe.
- Root cause must be proven before mutation/verdict.
