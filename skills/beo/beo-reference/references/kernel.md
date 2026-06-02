# BEO in One Page

BEO is a thin, repo-local safety layer over Beads. It is not an independent workflow manager. Work on one verified issue at a time.

## Delivery loop

```text
beo-plan -> beo-validate -> beo-execute -> beo-review
```

Authority split:

- `br` owns issue lifecycle, claims, dependencies, comments, ready queue, and closure.
- `bv` is read-only graph orientation.
- `.beads/artifacts/<issue-id>/TICKET.yaml` owns request, done criteria, approved scope, verification commands, and risk/strict contracts.
- `.beads/artifacts/<issue-id>/state.json` owns approval, execution, and review state.
- `.beads/artifacts/<issue-id>/runtime-events.jsonl` is optional and records only non-normal events.
- qmd and Obsidian are advisory memory only.

Artifact placement boundaries are canonical in `references/artifact-boundaries.md`.

## Hard invariants

1. Work on exactly one claimed atomic issue at a time.
2. Fresh-read `br show <issue-id> --json` at each owner entry.
3. Mutate product files only after current `PASS_EXECUTE` from `beo-validate`.
4. Mutate only `scope.files.allow` and declared `scope.generated_outputs`.
5. Broad globs require explicit Human Gate authorization.
6. Stateful or external side effects require strict mode contracts.
7. Dirty approved files or generated outputs before validation fail closed.
8. qmd and Obsidian never grant approval, execution permission, verdicts, closure, or Human Gate resolution.
9. Only `beo-review` may close accepted work, and only through `verdict_accept`.
10. BEO artifacts and approval assertions do not expire by elapsed time. They remain valid until an explicit predicate fails, a newer artifact supersedes them, or a human/operator revokes or removes the authority. Agents must not infer expiry from age alone.
