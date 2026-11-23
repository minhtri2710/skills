# Agent Skills

Each skill is a set of instructions a coding agent can load for one task or for a few related ones. Use the catalog to choose one. A skill with one task gives its steps, prerequisites, and limits in its linked `SKILL.md`; a skill with branches uses `SKILL.md` to choose the branch, and the branch file gives them.

## Use a skill

The installation unit is the **whole skill directory**, not just `SKILL.md`. For example, `diagnosis` includes a [script for reproductions that need a human](skills/diagnosis/scripts/hitl-loop.sh). A skill may also carry references, templates, or agent metadata.

In Claude Code, a personal copy of that skill lives at `~/.claude/skills/diagnosis/`; a project copy lives at `.claude/skills/diagnosis/`. Either directory can be a symlink to `skills/diagnosis/` in this checkout. See the [Claude Code skills guide](https://code.claude.com/docs/en/skills) for installation and invocation.

Try `/diagnosis Export sometimes returns an empty CSV`. Claude can also select most skills from the request. A leading `/` in the catalog marks a skill **you must invoke by name** (`disable-model-invocation: true`).

[`repo-refresh` defaults to a read-only audit](skills/repo-refresh/SKILL.md#invocation-and-mode). Use `/repo-refresh apply <repo> <scope>` to request cleanup; the scope can be in any language. A [Paseo delivery or review](skills/paseo-delivery-workflow/references/supervisor-and-lead.md#delivery-and-review-preflight) requires a connected daemon; a status request does not start a Watcher.

## Standalone skills

A skill with branches covers a few related tasks; [Branches](#branches) lists them.

### Plan and design

| Skill | Use it to |
| --- | --- |
| [`design`](skills/design/SKILL.md) | Settle a design before building: an API contract, a module interface, a whole-project premise audit, or a disposable prototype. |
| [`planning`](skills/planning/SKILL.md) | Plan work before it starts: resolve open questions with the user, split a requirement into modules, chart a large effort, and record terms and decisions. |

### Implement and diagnose

| Skill | Use it to |
| --- | --- |
| [`diagnosis`](skills/diagnosis/SKILL.md) | Find what a running system does wrong: reproduce a hard bug, fix a measured bottleneck, or add telemetry that answers on-call questions. |
| [`frontend`](skills/frontend/SKILL.md) | Build a UI change and verify it in the rendered result, or review an existing UI with extreme but admissible data. |
| [`human-step-wizard`](skills/human-step-wizard/SKILL.md) | Generate a resumable Bash wizard for steps only a person can perform. |
| [`migration`](skills/migration/SKILL.md) | Port code to another language, runtime, or framework while preserving what callers can observe, or check a framework or library API against official sources for the installed version. |
| [`/untangle-codebase`](skills/untangle-codebase/SKILL.md) | Restructure code so a requirement change lands in one place without changing behavior. |

### Review and verify

| Skill | Use it to |
| --- | --- |
| [`/change-impact-review`](skills/change-impact-review/SKILL.md) | Trace a concrete change past direct callers and check its critical assumptions on the real code path. |
| [`verification`](skills/verification/SKILL.md) | Prove a change: build test-first, check what a test or gate proves, maintain a project verification skill, or compare a change with its spec. |

### Safety and quality checks

| Skill | Use it to |
| --- | --- |
| [`destructive-guard`](skills/destructive-guard/SKILL.md) | Prove what a delete, move, overwrite, or provider-side removal will hit before it runs. |
| [`quality-floor`](skills/quality-floor/SKILL.md) | Record enforceable quality constraints, flag diffs that weaken them, and decide which checks belong in pre-commit, pre-push, or CI. |
| [`security`](skills/security/SKILL.md) | Harden a project: a local security baseline, dependency intake and advisory triage, and limits on what model output and model-accessible tools can do. |

### Agent work and documentation

| Skill | Use it to |
| --- | --- |
| [`agent-delivery-workflow`](skills/agent-delivery-workflow/SKILL.md) | Coordinate a bounded delivery or review in Herdr, Rex, or herdr core (`hc`). |
| [`context-boundary-routing`](skills/context-boundary-routing/SKILL.md) | Decide at a phase boundary whether to continue, clear context, hand off, delegate, or compact. |
| [`docs`](skills/docs/SKILL.md) | Write what a project keeps: agent instructions, human-facing Markdown reconciled with its sources, pull request descriptions, and prompts. |
| [`jev`](skills/jev/SKILL.md) | Get an optional advisory judgment on a finding or decision; it never grants approval. |
| [`paseo-delivery-workflow`](skills/paseo-delivery-workflow/SKILL.md) | Coordinate a delivery or an exact-commit review by agents running in Paseo. |
| [`/repo-refresh`](skills/repo-refresh/SKILL.md) | Audit stale repository material, apply explicitly requested cleanup, or verify an earlier pass. |
| [`/session-retro`](skills/session-retro/SKILL.md) | Trace problems in named sessions to lasting causes and propose one change per cause. |

## Branches

Each branch has its own file; its skill's `SKILL.md` chooses among them.

| Skill | Branch | Use it to |
| --- | --- | --- |
| `design` | [`api-contract-design`](skills/design/references/api-contract-design.md) | Define an HTTP or RPC contract, including validation, errors, pagination, and safe retries. |
| `design` | [`deep-module-design`](skills/design/references/deep-module-design.md) | Design an in-process interface that hides complexity from its callers. |
| `design` | [`architecture-premise-audit`](skills/design/references/architecture-premise-audit.md) | Check whether a whole project is built around the right kind of system. |
| `design` | [`throwaway-prototype`](skills/design/references/throwaway-prototype.md) | Answer one design question with a disposable logic demo or alternative UI layouts. |
| `planning` | [`design-grilling`](skills/planning/references/design-grilling.md) | Resolve open design questions with the user before writing a spec or code. |
| `planning` | [`capability-map`](skills/planning/references/capability-map.md) | Split one requirement into independently testable modules and order their dependencies. |
| `planning` | [`effort-charting`](skills/planning/references/effort-charting.md) | Map open decisions in a large effort, then split the agreed spec into deliverable slices. |
| `planning` | [`decision-record-discipline`](skills/planning/references/decision-record-discipline.md) | Record project terms, consequential decisions, and durable reasons for rejecting a proposal. |
| `diagnosis` | [`bug-diagnosis`](skills/diagnosis/references/bug-diagnosis.md) | Reproduce a hard bug with a repeatable pass/fail signal before testing causes. |
| `diagnosis` | [`performance-verification`](skills/diagnosis/references/performance-verification.md) | Measure a bottleneck and keep a fix only if its improvement exceeds the noise. |
| `diagnosis` | [`telemetry-questions-first`](skills/diagnosis/references/telemetry-questions-first.md) | Add logs, metrics, and traces that answer specific on-call questions. |
| `frontend` | [`frontend-design`](skills/frontend/references/frontend-design.md) | Build a UI change and verify its layout, states, and interactions in the rendered result. |
| `frontend` | [`worst-case-data-review`](skills/frontend/references/worst-case-data-review.md) | Review an existing UI with extreme but admissible data and report what breaks. |
| `migration` | [`behavior-preserving-port`](skills/migration/references/behavior-preserving-port.md) | Move code to another language, runtime, or framework while preserving what callers can observe. |
| `migration` | [`source-grounded-implementation`](skills/migration/references/source-grounded-implementation.md) | Check a framework or library API against official sources for the installed version. |
| `verification` | [`test-first-seams`](skills/verification/references/test-first-seams.md) | Build behavior in red-green slices through agreed public interfaces. |
| `verification` | [`test-proof-debt-audit`](skills/verification/references/test-proof-debt-audit.md) | Check what a named test or gate actually proves, or identify redundant tests in a named set. |
| `verification` | [`verification-skill-lifecycle`](skills/verification/references/verification-skill-lifecycle.md) | Create or maintain a project-local verification skill that maps features to real user routes and evidence. |
| `verification` | [`spec-conformance-review`](skills/verification/references/spec-conformance-review.md) | Compare a change with its named spec and cite the requirement behind each finding. |
| `destructive-guard` | [`destructive-path-guard`](skills/destructive-guard/references/destructive-path-guard.md) | Prove containment and ownership before deleting, moving, or overwriting a computed path. |
| `destructive-guard` | [`destructive-scope-guard`](skills/destructive-guard/references/destructive-scope-guard.md) | Verify tenancy, identity, inventory, and consent before removing provider-held resources. |
| `quality-floor` | [`quality-floor`](skills/quality-floor/references/quality-floor.md) | Record enforceable quality constraints and flag diffs that weaken them. |
| `quality-floor` | [`devops-pipeline`](skills/quality-floor/references/devops-pipeline.md) | Decide which existing checks belong in pre-commit, pre-push, or CI. |
| `security` | [`security-setup`](skills/security/references/security-setup.md) | Design an offline-capable local security baseline; gate implementation and any CI mirror separately. |
| `security` | [`dependency-intake-audit`](skills/security/references/dependency-intake-audit.md) | Evaluate a package, control install scripts, and triage advisories by reachability. |
| `security` | [`llm-trust-boundary`](skills/security/references/llm-trust-boundary.md) | Constrain what retrieved text, model output, and model-accessible tools can do. |
| `docs` | [`agent-doc-writing`](skills/docs/references/agent-doc-writing.md) | Write or prune instructions an agent reads: skills, agent rules, and their references. |
| `docs` | [`doc-manager`](skills/docs/references/doc-manager.md) | Reconcile human-facing Markdown with its sources and validate operational steps without performing them. |
| `docs` | [`pr-body`](skills/docs/references/pr-body.md) | Write a pull request description covering the change, merge risk, and observed evidence. |
| `docs` | [`prompt-leverage`](skills/docs/references/prompt-leverage.md) | Turn a raw prompt into instructions with an explicit output and stopping condition. |

## Repository checks and hooks

The [repository checks](AGENTS.md#checks) are the CI of record. The [Claude Code hooks](hooks/README.md) are separate from the skills and are installed manually.

See the [license](LICENSE) and [third-party notices](THIRD_PARTY_NOTICES.md) for reuse and attribution.
