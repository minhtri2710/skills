# AGENTS.md -- beo

## What This Repo Is

A collection of 12 operational beo skills plus a shared reference corpus for structured, contract-driven feature development using `br` (beads_rust) and `bv` (Beads Viewer) as the execution backbone, with optional knowledge store integration via Obsidian CLI and QMD. Primarily skill definitions (Markdown), plus onboarding scripts and template assets.

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
        go-mode.md
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
      SKILL.md                       # Navigation hub / index
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

1. **beo-route** -- Resolves canonical beo state and selects exactly one next target
2. **beo-explore** -- Locks product requirements into `CONTEXT.md` before any solution design
3. **beo-plan** -- Converts locked context into current-phase technical design, execution artifacts, and current-phase beads only
4. **beo-validate** -- Current-phase readiness gate; manages approval and selects `beo-execute` or `beo-swarm`
5. **beo-swarm** -- Coordinates parallel workers for approved, independent beads without implementing code as the coordinator
6. **beo-execute** -- Implements and verifies exactly one approved bead at a time
7. **beo-review** -- Assesses completed current-phase work and issues `accept`, `fix`, or `reject`
8. **beo-compound** -- Captures durable learnings from one accepted feature and proposes reusable pattern promotion
9. **beo-debug** -- Diagnoses one non-obvious blocker and applies the smallest verified unblock
10. **beo-dream** -- Consolidates learnings across multiple accepted features into corpus-level guidance
11. **beo-author** -- Creates, revises, and pressure-tests beo skills and supporting references
12. **beo-onboard** -- Verifies and minimally repairs beo tooling and bootstrap readiness for a repository

**beo-reference** is a shared reference corpus (not a loadable skill), accessed on demand when a skill needs canonical protocol docs beyond its inline references.

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
