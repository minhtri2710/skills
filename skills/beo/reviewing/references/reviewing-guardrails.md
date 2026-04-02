# Reviewing Guardrails

## Red Flags

| Flag | Description |
|------|-------------|
| **Auto-passing UAT** | Silence, politeness, or "looks good" vibes are not approval. Review requires explicit human confirmation. |
| **Closing with unresolved P1s** | Any P1 finding still open means the feature is not ready to finish. |
| **Reviewing while later phases remain** | Multi-phase work is not feature-complete just because the current phase shipped cleanly. |
| **Writing fixes inside review** | Review exists to find truth, classify findings, and route work. Implementation belongs in execution. |
| **No verification evidence** | Claims about build, test, lint, or runtime health without concrete evidence are not review results. |
| **Changed intent treated as a bug** | If the user now wants different behavior, that is a planning/context change, not a normal review nit. |

## Anti-Patterns

| Pattern | Why It's Wrong | Instead |
|---------|---------------|---------|
| Skipping artifact verification because the code "looks fine" | Review can miss unwired outputs, placeholders, or dead paths | Run the L1/L2/L3 artifact check against promised outputs |
| Collapsing P1/P2/P3 into one bucket | Blocking semantics and routing depend on severity staying distinct | Keep canonical severities and route each one correctly |
| Creating non-blocking follow-ups under the current epic | P2/P3 work should not silently block feature completion | Create follow-up beads outside the epic unless the user explicitly wants otherwise |
| Letting automated review replace human UAT | The user is the final source of truth for intent satisfaction | Walk locked decisions and exit-state claims one at a time |
| Treating "current phase complete" as "whole feature complete" | This breaks multi-phase routing and can skip later planned work | Route back to planning whenever later phases remain |
| Patching implementation during review to save time | It bypasses execution bookkeeping and hides the real state of the feature | Create a reactive fix bead and route it through execution |
