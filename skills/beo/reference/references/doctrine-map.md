# BEO Doctrine Map

Each workflow rule has exactly one canonical home.
Owner files may contain local hard stops and rule pointers only.
Do not copy multi-step shared doctrine across owner files.

| Topic | Canonical home | May owner files restate? |
| --- | --- | --- |
| Runtime kernel / core invariants | runtime-kernel.md | no, pointer only |
| Topology / default path / exception path | pipeline.md | no, pointer only |
| Owner mechanics / shared stops | skill-contract-common.md | no, pointer only |
| Approval authority | approval.md | no, owner-specific action only |
| Integrity helper | approval-integrity.md | no, owner-specific action only |
| Artifact schemas / precedence | artifacts.md | no, pointer only |
| STATE / HANDOFF | state.md | no, pointer only |
| Command authority | tool-contracts.md | no, pointer only |
| Learning provenance | learning.md | no, route condition only |
| Human Gates | human-gate.md | no, pointer only |
| Go-mode | go-mode.md | no, pointer only |
| Tiny / standard lanes | complexity.md | no, pointer only |
| Route operations | route/references/router-operations.md | route only |
| Review operations | review/references/review-operations.md | review only |
| Debug diagnostics | debug/references/diagnostic-checklist.md | debug only |
| Execution operations | execute/references/execution-operations.md | execute only |
| Setup operations | setup/references/setup-operations.md | setup only |
| Authoring method | author/references/skill-writing-method.md | author only |

Command behavior belongs in `tool-contracts.md`, not in owner prose, chat, examples, or artifact summaries.
