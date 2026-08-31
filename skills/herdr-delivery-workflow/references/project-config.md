# Project Config

A project may keep standing delivery preferences in a Human-owned config file:

```text
~/.herdr/projects/<project-slug>/config.md
```

The same directory holds the project's gate ledger (`gates.md`, defined in `human-gates-and-closeout.md`). Read the config at the start of a delivery or review-only route, before staffing any agent; the lightweight route does not read it. When the file is present, apply it. When it is absent, do not silently fall back to defaults: stop and ask the Human whether to create one for this project, offering the two outcomes — create the config now (record the settings they give, or seed the template below with the values this run would use and confirm them, then apply it) or proceed this run on workflow defaults — and act only on their answer. Record `Config: none`, in the intake record or beside the review boundary on a review-only route, only after the Human declines a config. Never create the file or assume defaults without that answer.

## Format

One `key: value` line per setting; every key is optional:

```markdown
# Delivery config — <project-slug>

- implementation-kind: <preferred agent kind>
- reviewer-kind: <preferred reviewer kind>
- reviewer-fallback: <pre-chosen fallback reviewer kind>
- checks: <claim-shaped commands, `;`-separated>
- lane-defaults: <path or change class = tiny|normal|high-risk, comma-separated>
- target-line: <default integration product line>
- always-gate: <decisions always routed to the Human, comma-separated>
- repair-cap: <max repair cycles before escalation>
- worker-cap: <max implementation agents in one partition; default 3>
```

Report an unknown key to the Human instead of guessing its meaning; do not act on it.

## Precedence and guards

- An explicit Human instruction in the current request overrides the config; the config overrides workflow defaults.
- The config may add stricter local preferences; it may not weaken this workflow's safety boundaries. A `lane-defaults` entry raises a lane floor and never lowers a lane below what the hard-gate classes in `intake-policy.md` require. `always-gate` adds Human gates; no key removes one, authorizes an external write, or skips review. `worker-cap` bounds how many implementation agents share the tree at once; it never permits overlapping owned paths or an agent that commits.
- The config is Human-owned and read-only during a run. The run edits it only when the Human explicitly asks to record a setting, and reports the change plainly.
- Record the applied keys, or `Config: none`, in the intake record, and pass applied staffing and validation values into the affected charters.
