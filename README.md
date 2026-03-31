# beo

Twelve AI agent skills for structured, plan-first feature development. Uses [`br`](https://github.com/Dicklesworthstone/beads_rust) (beads_rust) for issue tracking and [`bv`](https://github.com/Dicklesworthstone/beads_viewer) (Beads Viewer) for graph analytics to enforce a disciplined pipeline from requirements gathering through code review, with optional knowledge store integration via Obsidian CLI and QMD.

This is a pure content repository -- no application code, no build system, only Markdown skill definitions and YAML metadata. The skills are designed to be loaded by AI coding agents (Claude Code, OpenCode, Codex, etc.) that support skill/instruction loading.

> [MIT with Commons Clause](LICENSE) -- Copyright (c) 2026 minhtri2710

---

## Table of Contents

- [Why beo?](#why-beo)
- [Skills Overview](#skills-overview)
  - [Core Pipeline](#core-pipeline)
  - [Support and Meta Skills](#support-and-meta-skills)
  - [Shared Reference Hub](#shared-reference-hub)
- [How It Works](#how-it-works)
  - [Pipeline Flow](#pipeline-flow)
  - [What Each Skill Does](#what-each-skill-does)
  - [Key Artifacts Produced](#key-artifacts-produced)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Claude Code](#claude-code)
  - [OpenCode](#opencode)
  - [OpenAI Codex](#openai-codex)
  - [Manual Loading](#manual-loading)
- [Usage](#usage)
  - [Starting a New Feature](#starting-a-new-feature)
  - [Resuming Work](#resuming-work)
  - [Standalone Debugging](#standalone-debugging)
  - [Capturing Learnings](#capturing-learnings)
- [Project Structure](#project-structure)
  - [Repository Layout](#repository-layout)
  - [Skill Directory Structure](#skill-directory-structure)
  - [Reference Documents](#reference-documents)
- [Architecture](#architecture)
  - [Pipeline State Machine](#pipeline-state-machine)
  - [Bead Lifecycle](#bead-lifecycle)
  - [Agent Coordination](#agent-coordination)
  - [Knowledge Flywheel](#knowledge-flywheel)
- [Skill Reference](#skill-reference)
  - [beo-router](#beo-router)
  - [beo-exploring](#beo-exploring)
  - [beo-planning](#beo-planning)
  - [beo-validating](#beo-validating)
  - [beo-swarming](#beo-swarming)
  - [beo-executing](#beo-executing)
  - [beo-reviewing](#beo-reviewing)
  - [beo-compounding](#beo-compounding)
  - [beo-debugging](#beo-debugging)
  - [beo-dream](#beo-dream)
  - [beo-writing-skills](#beo-writing-skills)
  - [beo-reference](#beo-reference)
- [Editing Skills](#editing-skills)
- [FAQ](#faq)
- [License](#license)

---

## Why beo?

AI coding agents are powerful but undisciplined. Without structure, they jump straight to code, skip requirements, produce plans nobody verified, and forget what they learned last time. beo solves this by encoding a proven development workflow as agent skills:

- **No code without a verified plan.** The validating gate enforces 8-dimension verification before any implementation begins.
- **Requirements are locked first.** Exploring uses Socratic dialogue to surface and freeze decisions into `CONTEXT.md` before planning starts.
- **Parallel execution with coordination.** Swarming orchestrates multiple worker agents via Agent Mail, with file reservations and blocker handling.
- **Institutional memory.** Compounding captures learnings after every feature. Dream consolidates them periodically. Critical patterns are read by every future planning phase -- the system gets smarter over time.
- **Debuggable.** When a worker gets stuck, the debugging skill provides systematic root-cause analysis instead of guessing.

---

## Skills Overview

### Core Pipeline

The 8 core skills execute in sequence. Each skill has a clear entry condition, produces specific artifacts, and hands off to the next.

```
beo-router --> beo-exploring --> beo-planning --> beo-validating --> beo-swarming --> beo-executing --> beo-reviewing --> beo-compounding
```

| Skill               | Purpose                                                                                                 |
| ------------------- | ------------------------------------------------------------------------------------------------------- |
| **beo-router**      | Detects project state via `br`/`bv` CLI and routes to the correct phase skill                           |
| **beo-exploring**   | Socratic dialogue to lock requirements and decisions into `CONTEXT.md`                                  |
| **beo-planning**    | Creates epic + task beads with dependency wiring; writes `plan.md`, `phase-contract.md`, `story-map.md` |
| **beo-validating**  | 8-dimension verification gate -- plan must pass before any code is written                              |
| **beo-swarming**    | Orchestrates parallel worker agents for feature execution via Agent Mail                                |
| **beo-executing**   | Per-worker implementation loop -- claim, build prompt, dispatch, verify, report                         |
| **beo-reviewing**   | 5 specialist review agents with P1/P2/P3 severity; hands off to compounding                             |
| **beo-compounding** | Captures learnings from completed features, promotes critical patterns                                  |

### Support and Meta Skills

These are invoked on demand at any pipeline stage.

| Skill                  | Purpose                                                                                          |
| ---------------------- | ------------------------------------------------------------------------------------------------ |
| **beo-debugging**      | Systematic root-cause analysis for blocked workers, test failures, build errors, runtime crashes |
| **beo-dream**          | Periodic consolidation of learnings across features into refined knowledge                       |
| **beo-writing-skills** | TDD-for-skills methodology: create, pressure-test, and iterate on new beo skill definitions      |

### Shared Reference Hub

| Skill             | Purpose                                                                                             |
| ----------------- | --------------------------------------------------------------------------------------------------- |
| **beo-reference** | Navigation hub for 8 shared reference documents (CLI refs, status mapping, artifact protocol, etc.) |

---

## How It Works

### Pipeline Flow

```
                    CORE PIPELINE
                    ─────────────
   ┌────────┐    ┌───────────┐    ┌──────────┐    ┌────────────┐
   │ router │───>│ exploring │───>│ planning │───>│ validating │
   └────────┘    └───────────┘    └──────────┘    └─────┬──────┘
                                                        │
                                                        │  human
                                                        │  approval
                                                        ▼
  ┌─────────────┐    ┌───────────┐    ┌───────────┐    ┌──────────┐
  │ compounding │<───│ reviewing │<───│ executing │<───│ swarming │
  └──────┬──────┘    └───────────┘    └─────┬─────┘    └──────────┘
         │                                  │
         │  promotes                        │  on blocker
         ▼                                  ▼
  ┌──────────────────┐              ┌───────────┐
  │ critical-patterns│              │ debugging │  (on demand)
  │ .md              │              └───────────┘
  └────────┬─────────┘
           │  read by future
           │  planning cycles
           ▼
      ┌─────────┐
      │  dream  │  (periodic consolidation)
      └─────────┘
```

1. **Router** inspects `br`/`bv` state (beads, labels, statuses) and determines which phase the project is in
2. **Exploring** runs a Socratic Q&A to extract decisions from the human; produces `CONTEXT.md`
3. **Planning** reads `CONTEXT.md`, researches the codebase, creates beads with dependencies, writes the plan
4. **Validating** verifies the plan across 8 dimensions; runs spikes for high-risk items; requires human approval
5. **Swarming** launches parallel worker agents, monitors via Agent Mail, handles blockers and file conflicts
6. **Executing** (per worker) claims a task bead, builds a focused prompt, implements, tests, and reports
7. **Reviewing** runs 5 specialist review sub-agents, triages findings by severity, conducts human UAT
8. **Compounding** analyzes the completed feature for patterns, decisions, and failures; promotes critical learnings

### What Each Skill Does

**beo-router** reads the `.beads/` directory (created by `br`) and checks labels on beads to determine the current pipeline phase. If no beads exist, it routes to exploring. If beads exist but aren't validated, it routes to validating. If all beads are done, it routes to reviewing. This is the entry point you load first.

**beo-exploring** asks the human targeted questions to surface ambiguity, lock scope, and freeze constraints. It won't proceed until the human confirms the decisions. Output is a `CONTEXT.md` file that becomes the single source of truth for all downstream skills.

**beo-planning** runs discovery (codebase research), synthesis (approach selection), then decomposition (creating beads). It uses `br` to create an epic bead and child task beads with dependency edges. It also writes `phase-contract.md` (scope, success criteria, constraints) and `story-map.md` (user stories mapped to task beads).

**beo-validating** checks the plan across 8 dimensions: completeness, dependency graph validity, scope creep, risk assessment, bead quality, story coverage, contract alignment, and critical-pattern compliance. It uses `bv` for graph analytics (cycle detection, critical path, orphan detection). High-risk items get time-boxed spikes. Human must explicitly approve before any code is written.

**beo-swarming** is the orchestrator -- it never writes code directly. It uses Agent Mail to dispatch workers, monitors for completions and blockers, coordinates file reservations to prevent conflicts, and rescues stuck workers. Hands off to reviewing when all beads are closed.

**beo-executing** is the per-worker skill. A worker claims a bead via `br update <ID> --status in-progress`, builds a focused implementation prompt from the bead description and context, implements the change, runs tests, and reports completion via Agent Mail. Two modes: worker (under swarming) and standalone (for single-task fixes).

**beo-reviewing** launches 5 specialist sub-agents in parallel: correctness, security, performance, maintainability, and test coverage. Each produces findings with P1 (blocker), P2 (should-fix), or P3 (nice-to-have) severity. P1s must be fixed before the feature closes. After fixes, the human runs UAT. Then hands off to compounding.

**beo-compounding** runs 3 parallel analysis sub-agents examining patterns, decisions, and failures from the completed feature. Synthesizes findings into a learnings file at `.beads/learnings/YYYYMMDD-<slug>.md` and promotes critical items to `.beads/critical-patterns.md`. This file is read by every future planning phase -- this is the flywheel that makes the ecosystem smarter over time.

### Key Artifacts Produced

| Artifact                      | Producer    | Consumer                        | Purpose                              |
| ----------------------------- | ----------- | ------------------------------- | ------------------------------------ |
| `CONTEXT.md`                  | exploring   | planning, all downstream        | Frozen requirements and decisions    |
| `plan.md`                     | planning    | validating                      | Human-readable plan narrative        |
| `phase-contract.md`           | planning    | validating, swarming            | Scope, success criteria, constraints |
| `story-map.md`                | planning    | validating                      | User stories mapped to task beads    |
| `.beads/` directory           | `br` CLI    | all skills                      | Bead database, JSONL export, config  |
| `.beads/critical-patterns.md` | compounding | planning, validating, debugging | Institutional memory                 |
| `.beads/learnings/*.md`       | compounding | dream                           | Per-feature learnings                |

---

## Prerequisites

| Tool                                                      | Version | Required | Install                                                          | Purpose                                 |
| --------------------------------------------------------- | ------- | -------- | ---------------------------------------------------------------- | --------------------------------------- |
| [`br`](https://github.com/Dicklesworthstone/beads_rust)   | 0.1.28+ | Yes      | `cargo install beads_rust`                                       | Local-first issue tracker for AI agents |
| [`bv`](https://github.com/Dicklesworthstone/beads_viewer) | 0.15.2+ | Yes      | See [bv docs](https://github.com/Dicklesworthstone/beads_viewer) | Graph analytics, triage, scheduling     |
| `obsidian` CLI                                            | any     | No       | [Obsidian CLI](https://github.com/Yakitrak/obsidian-cli)         | Knowledge store write operations        |
| `qmd`                                                     | any     | No       | See qmd docs                                                     | Knowledge store search/query            |

You also need an AI coding agent that supports skill/instruction loading:

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code) (loads from `~/.agents/skills/`)
- [OpenCode](https://opencode.ai) (loads from `~/.agents/skills/`)
- [OpenAI Codex](https://openai.com/index/codex/) (uses `agents/openai.yaml` manifests)

---

## Installation

### Claude Code

Copy or symlink the skill directories into your Claude Code skills directory:

```bash
# Clone the repository
git clone https://github.com/minhtri2710/skills.git beo-skills

# Symlink all beo skills into Claude Code's skill directory
mkdir -p ~/.agents/skills
for skill in beo-skills/skills/beo/*/; do
  name=$(basename "$skill")
  ln -sf "$(pwd)/$skill" ~/.agents/skills/beo-$name
done
```

Each skill becomes available as `beo-router`, `beo-exploring`, etc.

### OpenCode

Same directory structure -- OpenCode reads from `~/.agents/skills/`:

```bash
mkdir -p ~/.agents/skills
for skill in beo-skills/skills/beo/*/; do
  name=$(basename "$skill")
  ln -sf "$(pwd)/$skill" ~/.agents/skills/beo-$name
done
```

### OpenAI Codex

Each skill includes an `agents/openai.yaml` manifest for Codex platform discovery. Point Codex at the repository or copy the skill directories into your Codex agent configuration.

### Manual Loading

If your agent doesn't support automatic skill discovery, you can load any skill by reading its `SKILL.md` file directly. The router skill is the recommended entry point:

```bash
# Read the router skill
cat skills/beo/router/SKILL.md
```

---

## Usage

### Starting a New Feature

Load the router skill in your AI coding agent. It will:

1. Check for `br`/`bv` CLI availability
2. Initialize `.beads/` if needed (`br init`)
3. Detect the current project state
4. Route to the appropriate phase skill

```
Agent: Load beo-router
Router: No beads found. Routing to beo-exploring.
Exploring: What feature are you building? [Socratic Q&A begins]
```

The typical first-run flow:

1. **Exploring** -- Agent asks targeted questions, you provide answers, agent writes `CONTEXT.md`
2. **Planning** -- Agent researches codebase, creates beads, writes plan
3. **Validating** -- Agent verifies plan, you review and approve
4. **Swarming/Executing** -- Agent orchestrates implementation
5. **Reviewing** -- 5-specialist review, you run UAT
6. **Compounding** -- Learnings captured for next time

### Resuming Work

Load `beo-router` again. It reads the current bead state and routes you to wherever you left off. If beads are in-progress, it routes to swarming. If all beads are done but unreviewed, it routes to reviewing.

### Standalone Debugging

When a worker hits a blocker or tests fail:

```
Agent: Load beo-debugging
Debugging: What's the error? [Systematic root-cause analysis begins]
```

The debugging skill reads `.beads/critical-patterns.md` to avoid re-solving known issues and follows a structured diagnostic checklist.

### Capturing Learnings

After a feature is merged and reviewed:

```
Agent: Load beo-compounding
Compounding: [Runs 3 parallel analysis sub-agents, writes learnings, promotes critical patterns]
```

Trigger phrases: "what did we learn", "capture learnings", "compound", "lessons learned".

---

## Project Structure

### Repository Layout

```
beo-skills/
├── .gitignore                    # Ignores .beads/, .cass/, .bv/, .gitnexus
├── AGENTS.md                     # Machine-readable project description for AI agents
├── LICENSE                       # MIT with Commons Clause
├── README.md                     # This file
└── skills/
    └── beo/
        ├── router/               # Entry point and phase detection
        ├── exploring/            # Requirements gathering
        ├── planning/             # Plan decomposition
        ├── validating/           # Plan verification gate
        ├── swarming/             # Parallel worker orchestration
        ├── executing/            # Per-worker implementation
        ├── reviewing/            # Multi-specialist review
        ├── compounding/          # Learnings capture
        ├── debugging/            # Systematic debugging
        ├── dream/                # Learnings consolidation
        ├── writing-skills/       # Skill authoring guide
        └── reference/            # Shared CLI reference hub
```

### Skill Directory Structure

Every skill directory follows the same pattern:

```
<skill-name>/
├── SKILL.md                      # Complete skill instructions (Markdown with YAML frontmatter)
├── agents/
│   └── openai.yaml               # OpenAI Codex agent manifest (display_name, description, prompt)
└── references/                   # (optional) Supporting templates, prompts, and checklists
    ├── template-1.md
    └── template-2.md
```

- `SKILL.md` contains YAML frontmatter (`name`, `description`) followed by the full skill instructions
- `agents/openai.yaml` provides metadata for OpenAI Codex platform discovery (does not affect skill logic)
- `references/` holds supporting documents that the skill loads on demand

Two skills (`router` and `exploring`) have no `references/` directory. The other 10 do.

### Reference Documents

The `beo-reference` skill is a shared hub loaded by all other skills. It provides 8 reference documents:

| Document                       | Purpose                                                                       |
| ------------------------------ | ----------------------------------------------------------------------------- |
| `br-cli-reference.md`          | Complete `br` (beads_rust) CLI command reference                              |
| `bv-cli-reference.md`          | Complete `bv` (Beads Viewer) CLI command reference                            |
| `status-mapping.md`            | Authoritative task status transitions (the single source of truth for status) |
| `artifact-protocol.md`         | How skills read/write task artifacts                                          |
| `dependency-and-scheduling.md` | Dependency sync and scheduling procedures                                     |
| `file-conventions.md`          | Pipeline artifact and state file naming/locations                             |
| `pipeline-contracts.md`        | State routing, HANDOFF schema, label lifecycle, task enumeration              |
| `knowledge-store.md`           | Obsidian CLI / QMD integration protocol                                       |

Skill-specific reference documents (20 across all skills) provide templates, prompts, and checklists for individual phases. See the [Skill Reference](#skill-reference) section for details.

---

## Architecture

### Pipeline State Machine

The router determines the current phase by inspecting bead labels and statuses:

```
No beads               --> exploring
Beads without plan     --> planning
Plan without approval  --> validating
Approved, not started  --> swarming
In-progress beads      --> swarming (resume)
All beads done         --> reviewing
Review complete        --> compounding
```

Phase transitions happen via labels on the epic bead (e.g., `plan-approved`, `review-complete`) and status changes on task beads. The `status-mapping.md` reference document is the authoritative source for valid transitions.

### Bead Lifecycle

A "bead" is a task tracked by `br`. Each bead has:

- **ID**: Short hash, auto-generated by `br` (e.g., `pe-jju`)
- **Status**: `open` -> `in-progress` -> `done` (with `blocked` as an escape state)
- **Dependencies**: Edges to other beads (`br dep add <from> <to>`)
- **Labels**: Metadata tags (`br label add <ID> -l <label>`)
- **Artifacts**: Attached outputs (implementation notes, test results)

Child beads use dotted IDs: `pe-jju.1`, `pe-jju.2`, etc. The epic bead is the parent; task beads are children.

```
Epic Bead (pe-jju)
├── pe-jju.1  (task: set up database schema)
├── pe-jju.2  (task: implement API endpoint)  depends-on: pe-jju.1
├── pe-jju.3  (task: write frontend component) depends-on: pe-jju.2
└── pe-jju.4  (task: add integration tests)    depends-on: pe-jju.2, pe-jju.3
```

`bv` provides graph analytics on the bead graph: cycle detection, critical path computation, PageRank, betweenness centrality, k-core decomposition, and orphan detection.

### Agent Coordination

When swarming dispatches multiple workers:

- **Agent Mail** handles inter-agent messaging (completions, blockers, status updates)
- **File reservations** prevent two workers from editing the same files simultaneously
- **Build slots** coordinate access to shared resources (test runners, build systems)
- **Blocker protocol** defines how workers escalate and how the orchestrator rescues them

The orchestrator (swarming skill) never implements tasks directly. It monitors, coordinates, and intervenes. Workers (executing skill) do the actual coding.

### Knowledge Flywheel

The compounding and dream skills form a feedback loop that improves the system over time:

```
Feature Complete
    │
    ▼
Compounding ──> .beads/learnings/YYYYMMDD-<slug>.md  (per-feature)
    │
    ▼
Promotes critical items ──> .beads/critical-patterns.md  (cumulative)
    │
    ▼
Read by Planning/Validating/Debugging in every future feature
    │
    ▼
Dream (periodic) ──> Consolidates and refines learnings across features
```

`critical-patterns.md` is the key artifact. Every planning phase reads it to avoid repeating past mistakes. Every debugging session checks it before starting fresh analysis. Over time, the system accumulates institutional knowledge that makes each feature faster and more reliable.

---

## Skill Reference

### beo-router

**Entry point.** Bootstraps the workspace and determines the current pipeline phase.

- Checks `br` and `bv` CLI availability
- Initializes `.beads/` if needed
- Reads bead state (labels, statuses, counts)
- Routes to the correct phase skill
- 380 lines | No reference documents

### beo-exploring

**Requirements gathering.** Socratic dialogue to extract and lock decisions.

- Asks targeted questions to surface ambiguity
- Freezes decisions into `CONTEXT.md`
- Won't proceed until human confirms
- Reads `critical-patterns.md` for institutional knowledge
- 266 lines | No reference documents

### beo-planning

**Plan decomposition.** Researches the codebase and creates the execution plan.

- Runs discovery phase (codebase research)
- Runs synthesis phase (approach selection)
- Creates epic bead + child task beads with dependency edges via `br`
- Writes `plan.md`, `phase-contract.md`, `story-map.md`
- 380 lines | 5 references: bead-creation-guide, discovery-guide, phase-contract-template, planning-guardrails, story-map-template

### beo-validating

**Verification gate.** 8-dimension plan verification before any code is written.

- Completeness, dependency validity, scope creep, risk assessment
- Bead quality, story coverage, contract alignment, critical-pattern compliance
- Uses `bv` for graph analytics (cycles, critical path, orphans)
- Time-boxed spikes for HIGH-risk items
- Requires explicit human approval
- 426 lines (longest skill) | 2 references: plan-checker-prompt, bead-reviewer-prompt

### beo-swarming

**Orchestration.** Dispatches and coordinates parallel worker agents.

- Launches workers via Agent Mail with focused prompts
- Monitors for completions, blockers, and file conflicts
- Manages file reservations and build slots
- Rescues stuck workers, coordinates course corrections
- Never implements tasks directly -- only tends
- 302 lines | 2 references: message-templates, worker-template

### beo-executing

**Implementation.** Per-worker task execution loop.

- Claims bead via `br update <ID> --status in-progress`
- Builds focused implementation prompt from bead context
- Implements the change
- Runs tests and verification
- Reports completion/blockers via Agent Mail
- Two modes: worker (under swarming) and standalone
- 339 lines | 3 references: blocker-handling, execution-guardrails, worker-prompt-guide

### beo-reviewing

**Quality gate.** Multi-specialist review before feature closure.

- Launches 5 specialist sub-agents: correctness, security, performance, maintainability, test coverage
- Each produces findings with P1/P2/P3 severity
- P1 findings are blockers -- must be fixed before close
- Conducts human UAT after fixes
- Hands off to compounding
- 272 lines | 1 reference: review-specialist-prompts

### beo-compounding

**Learning capture.** Extracts and promotes institutional knowledge.

- Runs 3 parallel analysis sub-agents: patterns, decisions, failures
- Synthesizes into `.beads/learnings/YYYYMMDD-<slug>.md`
- Promotes critical items to `.beads/critical-patterns.md`
- Trigger phrases: "what did we learn", "capture learnings", "compound"
- 348 lines | 1 reference: learnings-template

### beo-debugging

**Root-cause analysis.** Systematic debugging for any pipeline stage.

- Invoked standalone or by other skills (reviewing on UAT failure, executing on blocker)
- Reads `critical-patterns.md` to avoid re-solving known issues
- Follows structured diagnostic checklist
- Writes debug notes for compounding to capture later
- 293 lines | 1 reference: diagnostic-checklist

### beo-dream

**Consolidation.** Periodic refinement of accumulated learnings.

- Manual dream-style pass over artifacts and learnings
- Bootstrap-first scans, recurring-window updates
- Ambiguity resolution: merge / create new / skip
- Approval-gated critical-pattern proposals
- 159 lines (shortest core skill) | 3 references: codex-source-policy, consolidation-rubric, pressure-scenarios

### beo-writing-skills

**Meta skill.** Guide for creating and pressure-testing new beo skills.

- TDD-for-skills methodology: write skill, write pressure tests, iterate
- Creation log template for tracking design decisions
- Pressure test template with adversarial scenarios
- Ensures skills are bulletproof against agent rationalization
- 205 lines | 2 references: creation-log-template, pressure-test-template

### beo-reference

**Reference hub.** Navigation table pointing to 8 shared reference documents.

- Loaded by every other skill that needs CLI or protocol references
- Not a workflow skill -- purely a lookup hub
- 25 lines (shortest overall) | 8 references: br-cli-reference, bv-cli-reference, dependency-and-scheduling, status-mapping, artifact-protocol, file-conventions, pipeline-contracts, knowledge-store

---

## Editing Skills

When modifying any `SKILL.md`:

- **Verify CLI commands**: All `br` and `bv` commands must match CLI help output exactly. Run `br <subcommand> --help` and `bv --help` to confirm.
- **Dotted child IDs**: Child beads use `<parent-id>.<number>` format (e.g., `pe-jju.13` is child of `pe-jju`).
- **Label operations**: Use `br label add/remove <ID> -l <label>` (not `br update --add-label`).
- **Comments**: Always include `--no-daemon` on `br comments add` commands.
- **Artifact end markers**: Use underscores: `---END_ARTIFACT---` (not hyphens in the separator).
- **Status transitions**: Must match `beo-reference/references/status-mapping.md` as the authoritative source.
- **Frontmatter**: Every `SKILL.md` must have YAML frontmatter with `name` and `description` fields.

---

## FAQ

**Do I need all 12 skills?**
No. At minimum you need `beo-router` (entry point) and the core pipeline skills for the phases you want to use. The router will tell you which skill to load next. You can skip swarming/executing and just use exploring -> planning -> validating for plan-only workflows.

**What if I don't have `br` or `bv` installed?**
The router skill checks for these tools on startup. Without them, the pipeline cannot track beads or perform graph analytics. Install them first -- see [Prerequisites](#prerequisites).

**Can I use these skills with agents other than Claude Code?**
Yes. Any agent that can read Markdown instructions can use these skills. The `SKILL.md` files are self-contained. The `agents/openai.yaml` files provide additional metadata for OpenAI Codex but don't affect the skill logic.

**What's the `agents/openai.yaml` file in each skill?**
OpenAI Codex agent manifests for platform discovery and UI integration. They contain `display_name`, `short_description`, and `default_prompt`. Purely metadata -- unnecessary if you're not deploying to Codex.

**How does the knowledge flywheel work?**
After each feature, `beo-compounding` analyzes what happened and writes learnings. Critical items are promoted to `.beads/critical-patterns.md`. Every future planning and validating phase reads this file, so the system avoids repeating past mistakes. `beo-dream` periodically consolidates learnings across features for deeper refinement.

**Can I use individual skills without the full pipeline?**
Yes. `beo-debugging` works standalone for any debugging task. `beo-executing` has a standalone mode for single-task fixes. `beo-compounding` can be invoked after any completed work, not just the full pipeline.

**What's the difference between `beo-swarming` and `beo-executing`?**
Swarming is the orchestrator -- it dispatches and monitors multiple workers but never writes code. Executing is the worker -- it claims a task, implements it, and reports back. Swarming uses executing. In standalone mode, executing works without swarming for single tasks.

---

## License

[MIT with Commons Clause](LICENSE) -- Copyright (c) 2026 minhtri2710

The Commons Clause restricts selling the Software: you may not provide the skills as a paid hosted service or consulting offering whose value derives substantially from them. All other MIT permissions (use, modify, distribute) apply.
