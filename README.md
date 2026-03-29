# beo

Seven AI agent skills for structured, plan-first feature development. Uses `br` (beads_rust) for issue tracking and `bv` (Beads Viewer) for graph analytics to enforce a disciplined pipeline from requirements gathering through code review.

> [MIT with Commons Clause](LICENSE)

---

## Skills

The skills form a sequential pipeline:

```
router -> exploring -> planning -> validating -> executing -> reviewing
```

| Skill | Purpose |
|-------|---------|
| **beo/router** | Detects project state via `br`/`bv` CLI and routes to the correct phase skill |
| **beo/exploring** | Socratic dialogue to lock requirements and decisions into `CONTEXT.md` before planning |
| **beo/planning** | Creates epic + task beads with dependency wiring; writes `plan.md` |
| **beo/validating** | 8-dimension verification gate -- plan must pass before any code is written |
| **beo/executing** | Dispatches tasks to workers, maps statuses, handles blocked/partial/failed states |
| **beo/reviewing** | 5 specialist review agents with P1/P2/P3 severity, learnings capture |
| **beo/reference** | Shared CLI reference hub loaded by all other skills (br, bv, deps, status, artifacts) |

---

## Prerequisites

| Tool | Version | Install |
|------|---------|---------|
| `br` | 0.1.28+ | `cargo install beads_rust` -- [docs](https://github.com/Dicklesworthstone/beads_rust) |
| `bv` | 0.15.2+ | Beads Viewer -- graph analytics companion to br |

---

## Project Structure

```
skills/
  beo/router/SKILL.md
  beo/exploring/SKILL.md
  beo/planning/SKILL.md
  beo/validating/SKILL.md
  beo/executing/SKILL.md
  beo/reviewing/SKILL.md
  beo/reference/
    SKILL.md                     # Navigation hub
    references/
      br-cli-reference.md       # br command reference
      bv-cli-reference.md       # bv command reference
      dependency-and-scheduling.md
      status-mapping.md          # Authoritative status transitions
      artifact-protocol.md       # Artifact format specification
```

---

## Usage

These skills are designed to be loaded by AI coding agents (Claude Code, OpenCode, etc.) that support skill/instruction loading. Each `SKILL.md` file contains the complete instructions for its phase.

The **beo/router** skill is the entry point. It inspects the project's beads state and routes to the appropriate phase skill automatically.

### Typical flow

1. Agent loads `beo/router` -- detects phase from `br`/`bv` state
2. Router routes to `beo/exploring` -- user and agent lock decisions into `CONTEXT.md`
3. Router routes to `beo/planning` -- agent creates epic bead, task beads, dependency edges
4. Router routes to `beo/validating` -- plan verified across 8 dimensions; human approval gate
5. Router routes to `beo/executing` -- tasks dispatched to worker agents, status tracked
6. Router routes to `beo/reviewing` -- 5 specialist reviews, learnings captured, feature closed

---

## Editing Skills

When modifying any `SKILL.md`:

- Verify all `br` and `bv` commands against `br <subcommand> --help`
- Child beads use dotted IDs: `<parent-id>.<number>` (e.g., `pe-jju.13`)
- Use `br label add/remove <ID> -l <label>` for label operations
- Always include `--no-daemon` on `br comments add` commands
- Artifact end markers use underscores: `---END_ARTIFACT---`
- Status transitions must match `beo/reference/references/status-mapping.md`

---

## License

[MIT with Commons Clause](LICENSE) -- Copyright (c) 2026 Minh Tri Nguyen
