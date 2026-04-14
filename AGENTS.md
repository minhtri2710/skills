# AGENTS.md -- beo

## What This Repo Is

A collection of 13 AI agent skills for structured feature development using `br` (beads_rust) and `bv` (Beads Viewer) as the execution backbone, with optional knowledge store integration via Obsidian CLI and QMD. Primarily skill definitions (Markdown), plus onboarding scripts and template assets.

## Repository Structure

```
skills/
  beo/
    REVIEW-PLAN.md               # Repo-wide audit and cleanup tracker
    router/                      # Phase detection + skill routing
      SKILL.md
      agents/openai.yaml
      references/
        router-operations.md
        go-mode.md
    exploring/                   # Socratic requirements gathering
      SKILL.md
      agents/openai.yaml
      references/
        context-template.md
        gray-area-probes.md
    planning/                    # Epic/task decomposition + dependency wiring
      SKILL.md
      agents/openai.yaml
      references/
        planning-prerequisites.md
        planning-state-and-cleanup.md
        artifact-writing-guide.md
        task-creation-ops.md
        discovery-guide.md
        discovery-template.md
        approach-template.md
        plan-template.md
        phase-plan-template.md
        phase-contract-template.md
        story-map-template.md
        bead-creation-guide.md
    validating/                  # 8-dimension plan verification gate
      SKILL.md
      agents/openai.yaml
      references/
        validation-operations.md
        plan-checker-prompt.md
        bead-reviewer-prompt.md
    swarming/                    # Parallel worker orchestration
      SKILL.md
      agents/openai.yaml
      references/
        swarming-operations.md
        message-templates.md
        pressure-scenarios.md
    executing/                   # Per-worker implementation loop
      SKILL.md
      agents/openai.yaml
      references/
        execution-operations.md
        worker-prompt-guide.md
        blocker-handling.md
    reviewing/                   # 5-specialist review + compounding handoff
      SKILL.md
      agents/openai.yaml
      references/
        reviewing-operations.md
        review-specialist-prompts.md
    compounding/                 # Learnings capture + critical-pattern promotion
      SKILL.md
      agents/openai.yaml
      references/
        compounding-operations.md
        learnings-template.md
    debugging/                   # Systematic debugging for blockers/failures
      SKILL.md
      agents/openai.yaml
      references/
        debugging-operations.md
        diagnostic-checklist.md
        message-templates.md
    dream/                       # Periodic learnings consolidation
      SKILL.md
      agents/openai.yaml
      references/
        dream-operations.md
        consolidation-rubric.md
        agent-history-source-policy.md
        pressure-scenarios.md
    writing-skills/              # Skill creation and pressure-testing
      SKILL.md
      agents/openai.yaml
      references/
        writing-skills-operations.md
        creation-log-template.md
        pressure-test-template.md
    using-beo/                   # Onboarding bootstrap gate
      SKILL.md
      agents/openai.yaml
      assets/
      scripts/
      references/
        onboarding-flow.md
    reference/                   # Shared CLI reference hub
      SKILL.md                       # Navigation hub
      agents/openai.yaml
      references/                    # 14 reference docs
        br-cli-reference.md
        bv-cli-reference.md
        status-mapping.md
        artifact-conventions.md
        state-and-handoff-protocol.md
        approval-gates.md
        dependency-and-scheduling.md
        pipeline-contracts.md
        knowledge-store.md
        bead-description-templates.md
        learnings-read-protocol.md
        agent-mail-coordination.md
        communication-standard.md
        worker-template.md
```

Every skill directory also contains an `evals/` subdirectory for evaluation data.
The `*-workspace/` directories under `skills/beo/` are generated audit artifacts, not skill source.

## Skill Workflow (Pipeline)

```
beo-router -> beo-exploring -> beo-planning -> beo-validating -> beo-swarming -> beo-executing -> beo-reviewing -> beo-compounding
```

Support/meta skills (invoked on demand): `beo-debugging`, `beo-dream`, `beo-writing-skills`

1. **beo-router** -- Detects current project state via `br`/`bv` and routes to the correct skill
2. **beo-exploring** -- Socratic dialogue to lock decisions into `CONTEXT.md` before any planning
3. **beo-planning** -- Runs discovery, writes `discovery.md`, `approach.md`, `plan.md`, optional `phase-plan.md`, then creates current-phase `phase-contract.md`, `story-map.md`, and beads for the current phase only
4. **beo-validating** -- Phase contract, story map, and bead graph verification gate (8 dimensions); must pass before any code is written
5. **beo-swarming** -- Orchestrates parallel worker agents for feature execution
6. **beo-executing** -- Per-worker implementation loop: claim, build prompt, dispatch, verify, report
7. **beo-reviewing** -- 5 specialist review agents, P1/P2/P3 severity, hands off to compounding
8. **beo-compounding** -- Captures learnings from completed features, promotes critical patterns
9. **beo-debugging** -- Systematic debugging for blocked workers, test failures, build errors
10. **beo-dream** -- Periodic consolidation of learnings across features
11. **beo-writing-skills** -- Guide for creating and pressure-testing new beo skills
12. **beo-using-beo** -- Onboarding bootstrap and version gate for new repositories

**beo-reference** is the shared CLI reference hub, loaded on demand when a skill needs protocol docs beyond its inline references.

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
