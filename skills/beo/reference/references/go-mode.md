# Go-Mode

## Go-mode invariant

Go-mode changes assumption posture only.

It does not bypass owner selection, Human approval gates, UAT gates, validation, approval freshness, `PASS_EXECUTE`, execution scope, review, or learning thresholds.

## Suspension

Suspend go-mode when:

- scope expands
- triage class increases
- requirements become contradicted
- security/privacy/migration/destructive risk appears
- a non-fallback Human Gate appears
- approval invalidates

Upward reclassification suspends inherited go-mode before `PASS_EXECUTE` or `accept`.
