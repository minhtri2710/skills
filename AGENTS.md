# AGENTS.md -- beo

## What This Repo Is

A collection of 7 AI agent skills for structured feature development using `br` (beads_rust) and `bv` (Beads Viewer) as the execution backbone. No application code -- only skill definitions (Markdown).

## Repository Structure

```
skills/
  beo/router/SKILL.md       # Phase detection + skill routing
  beo/exploring/SKILL.md    # Socratic requirements gathering
  beo/planning/SKILL.md     # Epic/task decomposition + dependency wiring
  beo/validating/SKILL.md   # 8-dimension plan verification gate
  beo/executing/SKILL.md    # Dispatch, scheduling, status mapping
  beo/reviewing/SKILL.md    # 5-specialist review + learnings capture
  beo/reference/             # CLI reference hub
    SKILL.md                     # Navigation hub
    references/                  # 5 reference docs (br, bv, deps, status, artifacts)
```

## Skill Workflow (Pipeline)

```
router -> exploring -> planning -> validating -> executing -> reviewing
```

1. **beo/router** -- Detects current project state via `br`/`bv` and routes to the correct skill
2. **beo/exploring** -- Socratic dialogue to lock decisions into `CONTEXT.md` before any planning
3. **beo/planning** -- Creates epic + task beads with dependencies, writes `plan.md`
4. **beo/validating** -- 8-dimension verification gate; must pass before any code is written
5. **beo/executing** -- Dispatches tasks to workers, maps statuses, handles blocked/partial/failed
6. **beo/reviewing** -- 5 specialist review agents, P1/P2/P3 severity, learnings capture

**beo/reference** is the shared CLI reference loaded by all other skills.

## External Dependencies

| Tool | Version | Purpose |
|------|---------|---------|
| `br` | 0.1.28+ | beads_rust CLI -- issue tracking, task management |
| `bv` | 0.15.2+ | Beads Viewer -- graph analytics, triage, scheduling |

## Editing Skills

When editing any `SKILL.md` file:

- All `br` and `bv` commands must match the CLI help output exactly (verify with `br <subcommand> --help`)
- Child beads use dotted IDs: `<parent-id>.<number>` (e.g., `pe-jju.13` is child of `pe-jju`)
- Use `br label add/remove <ID> -l <label>` for label operations (not `br update --add-label`)
- Always include `--no-daemon` on `br comments add` commands
- Artifact end markers use underscores: `---END_ARTIFACT---` (not hyphens)
- Status mapping must match `beo/reference/references/status-mapping.md` as the authoritative source
