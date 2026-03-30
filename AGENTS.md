# AGENTS.md -- beo

## What This Repo Is

A collection of 12 AI agent skills for structured feature development using `br` (beads_rust) and `bv` (Beads Viewer) as the execution backbone, with optional knowledge store integration via Obsidian CLI and QMD. No application code -- only skill definitions (Markdown).

## Repository Structure

```
skills/
  beo/
    router/SKILL.md              # Phase detection + skill routing
    exploring/SKILL.md           # Socratic requirements gathering
    planning/SKILL.md            # Epic/task decomposition + dependency wiring
    validating/SKILL.md          # 8-dimension plan verification gate
    swarming/                    # Parallel worker orchestration
      SKILL.md
      references/message-templates.md, worker-template.md
    executing/SKILL.md           # Per-worker implementation loop
    reviewing/SKILL.md           # 5-specialist review + compounding handoff
    compounding/                 # Learnings capture + critical-pattern promotion
      SKILL.md
      references/learnings-template.md
    debugging/SKILL.md           # Systematic debugging for blockers/failures
    dream/                       # Periodic learnings consolidation
      SKILL.md
      references/codex-source-policy.md, consolidation-rubric.md, pressure-scenarios.md
    writing-skills/              # Skill creation and pressure-testing
      SKILL.md
      references/creation-log-template.md, pressure-test-template.md
    reference/                   # CLI reference hub
      SKILL.md                       # Navigation hub
      references/                    # 6 reference docs (br, bv, deps, status, artifacts, knowledge-store)
```

## Skill Workflow (Pipeline)

```
beo-router -> beo-exploring -> beo-planning -> beo-validating -> beo-swarming -> beo-executing -> beo-reviewing -> beo-compounding
```

Support/meta skills (invoked on demand): `beo-debugging`, `beo-dream`, `beo-writing-skills`

1. **beo-router** -- Detects current project state via `br`/`bv` and routes to the correct skill
2. **beo-exploring** -- Socratic dialogue to lock decisions into `CONTEXT.md` before any planning
3. **beo-planning** -- Creates epic + task beads with dependencies, writes `plan.md`
4. **beo-validating** -- 8-dimension verification gate; must pass before any code is written
5. **beo-swarming** -- Orchestrates parallel worker agents for feature execution
6. **beo-executing** -- Per-worker implementation loop: claim, build prompt, dispatch, verify, report
7. **beo-reviewing** -- 5 specialist review agents, P1/P2/P3 severity, hands off to compounding
8. **beo-compounding** -- Captures learnings from completed features, promotes critical patterns
9. **beo-debugging** -- Systematic debugging for blocked workers, test failures, build errors
10. **beo-dream** -- Periodic consolidation of learnings across features
11. **beo-writing-skills** -- Guide for creating and pressure-testing new beo skills

**beo-reference** is the shared CLI reference loaded by all other skills.

## External Dependencies

| Tool | Version | Purpose |
|------|---------|---------|
| `br` | 0.1.28+ | beads_rust CLI -- issue tracking, task management -- [docs](https://github.com/Dicklesworthstone/beads_rust) |
| `bv` | 0.15.2+ | Beads Viewer -- graph analytics, triage, scheduling -- [docs](https://github.com/Dicklesworthstone/beads_viewer) |
| `obsidian` CLI | *(optional)* | Knowledge store write operations |
| `qmd` | *(optional)* | Knowledge store search/query operations |

## Editing Skills

When editing any `SKILL.md` file:

- All `br` and `bv` commands must match the CLI help output exactly (verify with `br <subcommand> --help`)
- Child beads use dotted IDs: `<parent-id>.<number>` (e.g., `pe-jju.13` is child of `pe-jju`)
- Use `br label add/remove <ID> -l <label>` for label operations (not `br update --add-label`)
- Always include `--no-daemon` on `br comments add` commands
- Artifact end markers use underscores: `---END_ARTIFACT---` (not hyphens)
- Status mapping must match `beo/reference/references/status-mapping.md` as the authoritative source
