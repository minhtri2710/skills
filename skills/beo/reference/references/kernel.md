# BEO in One Page (Kernel Invariants)

BEO is a highly-disciplined, contract-driven pipeline for executing Beads issues. Work on exactly one verified issue at a time.

## 1. Fast-Path Pipelines

Three postures scaled by risk: **quick** (repo-only, low-risk), **standard** (moderate, declares risk/rollback), **strict** (stateful/external, requires contracts). See `registry/profiles.json` for canonical definitions.

Normal delivery path: `plan -> validate -> execute -> review`. See `registry/pipeline.json` for all transitions. See `references/lifecycle.md` for claim invariants and decomposition.

Authority split: `br` is transactional truth, `bv` is read-only graph orientation, `TICKET.md` is BEO safety/evidence truth, `qmd` is advisory semantic recall, and Obsidian CLI is durable learning-note persistence. Do not duplicate state across them.

---

## 2. Hard Invariants (Never Bypass)

1. **Strict Claim**: Never mutate files, write ticket projections, or run code changes without atomically claiming the issue using `br update --claim`.
2. **Strict Containment**: Never execute code mutations outside `scope.files.allow` or declared generated outputs.
3. **No Validation Bypass**: Never execute without a current, valid `PASS_EXECUTE` token written by `beo-validate`.
4. **No Direct Closure**: Never close a ticket or bypass `beo-review`. Only `beo-review` verdict acceptance can route to `close`.
5. **No Glob Expansion**: Never use broad globs (e.g. `**`, `src/**`) without explicit Human Gate authorization.
6. **No Stateful Mutation Without Contract**: Stateful external operations (DB migration, third-party API state, destructive mutations) require strict side-effect contracts. See `references/safety.md`.
7. **Memory**: `qmd` recall is advisory only. See `references/memory.md`.
