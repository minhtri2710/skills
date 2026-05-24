# BEO in One Page (Kernel Invariants)

BEO is a repo-local, script-based safety and evidence overlay for `br`-tracked issues selected and oriented through `br` and `bv`. It is not an independent workflow manager. Work on exactly one verified issue at a time.

## 1. Fast-Path Pipelines

Three postures scaled by risk: **quick** (repo-only, low-risk), **standard** (moderate, declares risk/rollback), **strict** (stateful/external, requires contracts). See `beo-reference` -> `registry/profiles.json` for canonical definitions.

Normal delivery path: `plan -> validate -> execute -> review`. See `beo-reference` -> `registry/pipeline.json` for all transitions. See `lifecycle.md` for claim invariants and decomposition.

Authority split: `br` is transactional lifecycle truth, `bv` is read-only graph orientation only, `.beads/artifacts/<issue-id>/` is BEO safety/evidence truth (`TICKET.md` for intake/scope, `state.json` for current approval/execution/review state, `runtime-events.jsonl` for append-only non-normal events), `qmd` is advisory semantic recall, and Obsidian CLI is durable learning-note persistence. Do not duplicate state across them.

There is no required `beo` executable. BEO entry points are repo-local scripts under `beo-reference` -> `scripts/`. Registry command IDs are authority contract IDs, not shell commands.

Path reservation is a BEO-local concurrency guard implemented by `beo-reference` -> `scripts/beo_reservation.py`. It is not a native `br` feature and must not be documented as a `br` path-reservation command.

---

## 2. Hard Invariants (Never Bypass)

1. **Strict Claim**: Never mutate files, write ticket projections, or run code changes without atomically claiming the issue using `br update --claim`.
2. **Strict Containment**: Never execute code mutations outside `scope.files.allow` or declared generated outputs.
3. **No Validation Bypass**: Never execute without a current, valid `PASS_EXECUTE` token written by `beo-validate`.
4. **No Direct Closure**: Never close a ticket or bypass `beo-review`. Only `beo-review` can route to `close` — via `verdict_accept` for normal delivery, or via `abandoned` with registered abandon reason and user visibility.
5. **No Glob Expansion**: Never use broad globs (e.g. `**`, `src/**`) without explicit Human Gate authorization.
6. **No Stateful Mutation Without Contract**: Stateful external operations (DB migration, third-party API state, destructive mutations) require strict side-effect contracts. See `safety.md`.
7. **Memory**: `qmd` recall is advisory only. See `memory.md`.
