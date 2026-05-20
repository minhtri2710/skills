# Ticket

The normal BEO artifact is `.beads/artifacts/<issue-id>/TICKET.md` plus helper outputs under `checks/`.

Active phase is inferred from present owner fields, latest legal runtime event, pipeline transition, and Beads issue state.

## Minimal shape

See `beo-reference -> templates/TICKET.quick.md`. Machine schema: `beo-reference -> registry/ticket-schema.json`.

## Owner additions

- `beo-plan`: intake fields, Human Gates, scope, acceptance, atomicity, mode/profile/posture, generated outputs, side-effect posture, risk, rollback, strict artifacts, optional issue-selection or decomposition `triage_records`.
- `beo-validate`: readiness, execution set/mode, approval ref, integrity.
- `beo-execute`: execution evidence, prestate, changed files, verification.
- `beo-review`: verdict, findings, closure evidence.
- Runtime support: append-only `runtime_events` (see `beo-reference -> references/lifecycle-events.md`), optional non-approval `debug` diagnosis evidence owned by `beo-debug`, and recall artifacts owned by `beo-recall`.
- Learning: learning candidates are runtime events; learning notes live outside normal delivery fields.


Future-owned fields stay absent until their owner acts. Strict tickets bind `STRICT.md` and `ROLLBACK.md` through `strict.artifact_hashes`.

`beo-validate` refuses `PASS_EXECUTE` unless:

```yaml
atomicity:
  decision: atomic
  reason: <why this is one executable unit>
  rejects_multi_task: true
```

Machine schema lives in `registry/ticket-schema.json`.
