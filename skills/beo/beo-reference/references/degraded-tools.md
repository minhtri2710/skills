# Degraded Tool Guidance

> [!NOTE]
> This reference is subordinate to [references/kernel.md](file:///Users/beowulf/Work/personal/beo-skills/skills/beo/beo-reference/references/kernel.md). `references/kernel.md` is the canonical owner of BEO rules and invariants.

This file guidance focuses on setup checks. Authority invariants are canonical in `references/kernel.md`.

## Tool requirements

| Tool | Status | Purpose | If missing |
| --- | --- | --- | --- |
| `br` | Required | Issue lifecycle, claims, comments, closure | Block BEO delivery readiness. |
| PyYAML | Required | Parse BEO YAML/JSON artifacts | Block helper execution. |
| `bv` | Optional | Read-only graph orientation | Use `br ready --json` and `br show --json`. |
| `qmd` | Optional | Advisory semantic recall | Disable semantic search. |
| Obsidian | Optional | Reusable learning note vault | Fall back to `.beads/learning/`. |

## Minimum viable BEO

BEO delivery can run when:

- `br` works,
- BEO artifacts can be read/written,
- YAML/JSON helper dependencies work,
- repo working tree can be inspected.

BEO delivery does not require:

- `bv`,
- qmd,
- Obsidian CLI,
- semantic memory.

## Reporting

`beo_setup.py` reports:

- control-plane readiness: `ready|blocked`
- advisory memory status: `ok|degraded|missing`
- operator guidance for the narrow missing dependency or degraded capability

Keep degraded reports short, concrete, and separated by authority class.
