# Agent Skills

Each skill is a set of instructions a coding agent can load for a particular task. Use the catalog to choose one; its linked `SKILL.md` gives the steps, prerequisites, and limits.

## Use a skill

The installation unit is the **whole skill directory**, not just `SKILL.md`. For example, `bug-diagnosis` includes a [script for reproductions that need a human](skills/bug-diagnosis/scripts/hitl-loop.sh). A skill may also carry references, templates, or agent metadata.

In Claude Code, a personal copy of that skill lives at `~/.claude/skills/bug-diagnosis/`; a project copy lives at `.claude/skills/bug-diagnosis/`. Either directory can be a symlink to `skills/bug-diagnosis/` in this checkout. See the [Claude Code skills guide](https://code.claude.com/docs/en/skills) for installation and invocation.

Try `/bug-diagnosis Export sometimes returns an empty CSV`. Claude can also select most skills from the request. A leading `/` in the catalog marks a skill **you must invoke by name** (`disable-model-invocation: true`).

[`repo-refresh` defaults to a read-only audit](skills/repo-refresh/SKILL.md#invocation-and-mode). Use `/repo-refresh apply <repo> <scope>` to request cleanup; the scope can be in any language. A [Paseo delivery or review](skills/paseo-delivery-workflow/SKILL.md#delivery-and-review-preflight) requires a connected daemon; a status request does not start a Watcher.

## Standalone skills

### Plan and design

| Skill | Use it to |
| --- | --- |
| [`api-contract-design`](skills/api-contract-design/SKILL.md) | Define an HTTP or RPC contract, including validation, errors, pagination, and safe retries. |
| [`architecture-premise-audit`](skills/architecture-premise-audit/SKILL.md) | Check whether a whole project is built around the right kind of system. |
| [`capability-map`](skills/capability-map/SKILL.md) | Split one requirement into independently testable modules and order their dependencies. |
| [`decision-record-discipline`](skills/decision-record-discipline/SKILL.md) | Record project terms, consequential decisions, and durable reasons for rejecting a proposal. |
| [`deep-module-design`](skills/deep-module-design/SKILL.md) | Design an in-process interface that hides complexity from its callers. |
| [`design-grilling`](skills/design-grilling/SKILL.md) | Resolve open design questions with the user before writing a spec or code. |
| [`effort-charting`](skills/effort-charting/SKILL.md) | Map open decisions in a large effort, then split the agreed spec into deliverable slices. |

### Implement and diagnose

| Skill | Use it to |
| --- | --- |
| [`behavior-preserving-port`](skills/behavior-preserving-port/SKILL.md) | Move code to another language, runtime, or framework while preserving what callers can observe. |
| [`bug-diagnosis`](skills/bug-diagnosis/SKILL.md) | Reproduce a hard bug with a repeatable pass/fail signal before testing causes. |
| [`frontend-design`](skills/frontend-design/SKILL.md) | Build a UI change and verify its layout, states, and interactions in the rendered result. |
| [`human-step-wizard`](skills/human-step-wizard/SKILL.md) | Generate a resumable Bash wizard for steps only a person can perform. |
| [`performance-verification`](skills/performance-verification/SKILL.md) | Measure a bottleneck and keep a fix only if its improvement exceeds the noise. |
| [`source-grounded-implementation`](skills/source-grounded-implementation/SKILL.md) | Check a framework or library API against official sources for the installed version. |
| [`telemetry-questions-first`](skills/telemetry-questions-first/SKILL.md) | Add logs, metrics, and traces that answer specific on-call questions. |
| [`test-first-seams`](skills/test-first-seams/SKILL.md) | Build behavior in red-green slices through agreed public interfaces. |
| [`throwaway-prototype`](skills/throwaway-prototype/SKILL.md) | Answer one design question with a disposable logic demo or alternative UI layouts. |
| [`/untangle-codebase`](skills/untangle-codebase/SKILL.md) | Restructure code so a requirement change lands in one place without changing behavior. |

### Review and verify

| Skill | Use it to |
| --- | --- |
| [`/change-impact-review`](skills/change-impact-review/SKILL.md) | Trace a concrete change past direct callers and check its critical assumptions on the real code path. |
| [`spec-conformance-review`](skills/spec-conformance-review/SKILL.md) | Compare a change with its named spec and cite the requirement behind each finding. |
| [`test-proof-debt-audit`](skills/test-proof-debt-audit/SKILL.md) | Check what a named test or gate actually proves, or identify redundant tests in a named set. |
| [`verification-skill-lifecycle`](skills/verification-skill-lifecycle/SKILL.md) | Create or maintain a project-local verification skill that maps features to real user routes and evidence. |
| [`worst-case-data-review`](skills/worst-case-data-review/SKILL.md) | Review an existing UI with extreme but admissible data and report what breaks. |

### Safety and quality checks

| Skill | Use it to |
| --- | --- |
| [`dependency-intake-audit`](skills/dependency-intake-audit/SKILL.md) | Evaluate a package, control install scripts, and triage advisories by reachability. |
| [`destructive-path-guard`](skills/destructive-path-guard/SKILL.md) | Prove containment and ownership before deleting, moving, or overwriting a computed path. |
| [`destructive-scope-guard`](skills/destructive-scope-guard/SKILL.md) | Verify tenancy, identity, inventory, and consent before removing provider-held resources. |
| [`devops-pipeline`](skills/devops-pipeline/SKILL.md) | Decide which existing checks belong in pre-commit, pre-push, or CI. |
| [`llm-trust-boundary`](skills/llm-trust-boundary/SKILL.md) | Constrain what retrieved text, model output, and model-accessible tools can do. |
| [`quality-floor`](skills/quality-floor/SKILL.md) | Record enforceable quality constraints and flag diffs that weaken them. |
| [`security-setup`](skills/security-setup/SKILL.md) | Design an offline-capable local security baseline; gate implementation and any CI mirror separately. |

### Agent work and documentation

| Skill | Use it to |
| --- | --- |
| [`agent-delivery-workflow`](skills/agent-delivery-workflow/SKILL.md) | Coordinate a bounded delivery or review in Herdr, Rex, or herdr core (`hc`). |
| [`agent-doc-writing`](skills/agent-doc-writing/SKILL.md) | Write or prune instructions an agent reads: skills, agent rules, and their references. |
| [`context-boundary-routing`](skills/context-boundary-routing/SKILL.md) | Decide at a phase boundary whether to continue, clear context, hand off, delegate, or compact. |
| [`doc-manager`](skills/doc-manager/SKILL.md) | Reconcile human-facing Markdown with its sources and validate operational steps without performing them. |
| [`jev`](skills/jev/SKILL.md) | Get an optional advisory judgment on a finding or decision; it never grants approval. |
| [`paseo-delivery-workflow`](skills/paseo-delivery-workflow/SKILL.md) | Coordinate a delivery or an exact-commit review by agents running in Paseo. |
| [`pr-body`](skills/pr-body/SKILL.md) | Write a pull request description covering the change, merge risk, and observed evidence. |
| [`prompt-leverage`](skills/prompt-leverage/SKILL.md) | Turn a raw prompt into instructions with an explicit output and stopping condition. |
| [`/repo-refresh`](skills/repo-refresh/SKILL.md) | Audit stale repository material, apply explicitly requested cleanup, or verify an earlier pass. |
| [`/session-retro`](skills/session-retro/SKILL.md) | Trace problems in named sessions to lasting causes and propose one change per cause. |

## Repository checks and hooks

The [repository checks](AGENTS.md#checks) are the CI of record. The [Claude Code hooks](hooks/README.md) are separate from the skills and are installed manually.

See the [license](LICENSE) and [third-party notices](THIRD_PARTY_NOTICES.md) for reuse and attribution.
