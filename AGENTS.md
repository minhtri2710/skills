# AGENTS.md -- beo

## What This Repo Is

A collection of 13 AI agent skills for structured feature development using `br` (beads_rust) and `bv` (Beads Viewer) as the execution backbone, with optional knowledge store integration via Obsidian CLI and QMD. Primarily skill definitions (Markdown), plus onboarding scripts and template assets.

## Repository Structure

```
skills/
  beo/
    REVIEW-PLAN.md               # Repo-wide audit and cleanup tracker
    route/                       # Phase detection + skill routing
      SKILL.md
      agents/openai.yaml
      references/
        router-operations.md
        go-mode.md
    explore/                     # Socratic requirements gathering
      SKILL.md
      agents/openai.yaml
      references/
        context-template.md
        gray-area-probes.md
    plan/                        # Epic/task decomposition + dependency wiring
      SKILL.md
      agents/openai.yaml
      references/
        planning-prerequisites.md
        planning-state-and-cleanup.md
        artifact-writing-guide.md
        bead-ops.md
        discovery-reference.md
        approach-template.md
        plan-template.md
        phase-plan-template.md
        phase-contract-template.md
        story-map-template.md
    validate/                    # 8-dimension plan verification gate
      SKILL.md
      agents/openai.yaml
      references/
        validation-operations.md
        plan-checker-prompt.md
        bead-reviewer-prompt.md
    swarm/                       # Parallel worker orchestration
      SKILL.md
      agents/openai.yaml
      references/
        swarming-operations.md
        message-templates.md
        pressure-scenarios.md
    execute/                     # Per-worker implementation loop
      SKILL.md
      agents/openai.yaml
      references/
        execution-operations.md
        worker-prompt-guide.md
        blocker-handling.md
    review/                      # 5-specialist review + compounding handoff
      SKILL.md
      agents/openai.yaml
      references/
        reviewing-operations.md
        review-specialist-prompts.md
    compound/                    # Per-feature learnings capture + critical-pattern promotion
      SKILL.md
      agents/openai.yaml
      references/
        compounding-operations.md
        learnings-template.md
    debug/                       # Systematic debugging for blockers/failures
      SKILL.md
      agents/openai.yaml
      references/
        debugging-operations.md
        diagnostic-checklist.md
        message-templates.md
    dream/                       # Periodic cross-feature learnings consolidation
      SKILL.md
      agents/openai.yaml
      references/
        dream-operations.md
        consolidation-rubric.md
        agent-history-source-policy.md
        pressure-scenarios.md
    author/                      # Skill creation and pressure-testing
      SKILL.md
      agents/openai.yaml
      references/
        writing-skills-operations.md
        creation-log-template.md
        pressure-test-template.md
    onboard/                     # Onboarding bootstrap gate
      SKILL.md
      agents/openai.yaml
      assets/
      scripts/
      references/
        onboarding-flow.md
    reference/                   # Shared reference corpus (not a loadable skill)
      INDEX.md                       # Navigation hub
      references/                    # 16 reference docs
        br-cli-reference.md
        bv-cli-reference.md
        status-mapping.md
        artifact-conventions.md
        state-and-handoff-protocol.md
        approval-gates.md
        dependency-and-scheduling.md
        pipeline-contracts.md
        failure-recovery.md
        knowledge-store.md
        bead-description-templates.md
        learnings-read-protocol.md
        agent-mail-coordination.md
        communication-standard.md
        worker-template.md
        shared-hard-gates.md
```

The `*-workspace/` directories under `skills/beo/` are generated audit artifacts, not skill source.

## Skill Workflow (Pipeline)

```
beo-route -> beo-explore -> beo-plan -> beo-validate -> (beo-execute | beo-swarm -> beo-execute) -> beo-review -> beo-compound
```

Support/meta skills (invoked on demand): `beo-debug`, `beo-dream`, `beo-author`

1. **beo-route** -- Detects current project state via `br`/`bv` and routes to the correct skill
2. **beo-explore** -- Socratic dialogue to lock decisions into `CONTEXT.md` before any planning
3. **beo-plan** -- Runs discovery, writes `discovery.md`, `approach.md`, `plan.md`, optional `phase-plan.md`, then creates current-phase `phase-contract.md`, `story-map.md`, and beads for the current phase only
4. **beo-validate** -- Phase contract, story map, and bead graph verification gate (8 dimensions); must pass before any code is written
5. **beo-swarm** -- Orchestrates parallel worker agents for feature execution
6. **beo-execute** -- Per-worker implementation loop: claim, build prompt, dispatch, verify, report
7. **beo-review** -- 5 specialist review agents, P1/P2/P3 severity, hands off to compounding
8. **beo-compound** -- Captures learnings from completed features, promotes critical patterns
9. **beo-debug** -- Systematic debugging for blocked workers, test failures, build errors
10. **beo-dream** -- Periodic consolidation of learnings across features
11. **beo-author** -- Guide for creating and pressure-testing new beo skills
12. **beo-onboard** -- Onboarding bootstrap and version gate for new repositories

**beo-reference** is now a shared reference corpus (not a loadable skill), accessed on demand when a skill needs protocol docs beyond its inline references.

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
