# Project Config

A project may keep standing delivery preferences in a Human-owned config file:

```text
~/.herdr/projects/<project-slug>/config.md
```

`<project-slug>` is the basename of the checkout's repository root (`basename "$(git rev-parse --show-toplevel)"`), lowercased; the same checkout always resolves to the same directory, which is what lets the gate ledger and this config survive a pane restart. The same directory holds the project's gate ledger (`gates.md`, defined in `lead.md`, "Gates and ledger"). This file is shared and cited, not copied.

The config is the Lead's layer: the Lead reads it at the start of a delivery or review-only route, before staffing any agent; the Supervisor may read it to audit; a Peer never reads it and receives the applied values through its charter; the lightweight route does not read it. When present, apply it. When absent, do not silently fall back to defaults: stop and ask the Human whether to create one, offering the two outcomes — create it now (record the settings they give, or seed the template below with the values this run would use and confirm them, then apply it) or proceed this run on workflow defaults — and act only on their answer. Record `Config: none` (in the intake record, or beside the review boundary on a review-only route) only after the Human declines a config. Never create the file or assume defaults without that answer.

## Format

One `key: value` line per setting, in the shape of `templates/config.txt`; every key is optional. Report an unknown key to the Human instead of guessing its meaning; do not act on it.

## Precedence and guards

- An explicit Human instruction in the current request overrides the config; the config overrides workflow defaults.
- The config may add stricter local preferences; it may not weaken this workflow's safety boundaries. A `lane-defaults` entry raises a lane floor and never lowers a lane below what the hard-gate classes (`lead.md`, "Intake") require. `always-gate` adds Human gates; no key removes one, authorizes an external write, or skips review. `worker-cap` bounds how many Engineers share the tree at once; it never permits overlapping owned paths or an agent that commits. When `reviewer-fallback` equals `engineer-kind`, the Lead reports a config conflict in the intake record rather than accepting it silently; if that fallback is ever used, independence requires a distinct model pinned through `reviewer-fallback-args`, and without one the fallback is unusable and conflicting, not independent.
- `*-args` values pre-arm routine command approval so agents do not stall on per-command prompts; they never authorize push, PR mutation, merge, deploy, or another external write. Prefer an allowlist or scoped mode when the kind offers one, and for `reviewer-args`/`reviewer-fallback-args` one that withholds writes to the tree. A blanket permission skip is recorded here only as the Human's standing waiver for that kind: the Lead passes it because the key exists, records the Peer's posture as `bypassed` residual risk (`charters.md`, "Writing charters"), and never adds the flag on its own when the key is absent.
- The config and other Human-owned files outside the repository — a global tool config, an installed skill directory — are read-only during a run. The run writes such a file only when the current Human explicitly instructs it to record that setting, reports the external change plainly, and appends one ledger line for the external write; absent that instruction, the Lead does not write outside the repository.
- Record the applied keys, or `Config: none`, in the intake record, and pass applied staffing and validation values into the affected charters.
