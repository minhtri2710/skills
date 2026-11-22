---
name: human-step-wizard
description: Generate a resumable bash wizard that walks a human through the steps only they can do, opening each URL, saying what to click and copy, and writing the captured values to .env and CI secrets. Use when a task hits credentials, third-party dashboards, account provisioning, or a one-off manual cutover that the agent cannot perform, instead of writing prose instructions. Do not use for steps the agent can run itself.
---

# Human Step Wizard

Use the [wizard template](scripts/wizard-template.sh) for steps only a person
can perform, such as approving an OAuth app or retrieving a key. Keep the
library above `STAGES` intact; it handles progress, hidden input, reuse of
values saved locally, and reporting skipped GitHub writes. Author the stages
below the marker.

## 1. Scope the procedure

Inventory the **names** the task needs from example configuration, the README,
application config, and CI references to `secrets.*` and `vars.*`. Do not read
live `.env` values or collect a credential the platform already supplies. For
a cutover, also identify the current state, target state, and irreversible acts.
Show the user the proposed stages in order so they can add, drop, or reorder them.

Done when each value has a human source, a sensitivity, and its intended
destinations: local `.env`, a repository secret or variable, or a combination.
A stage that only performs an action need not capture a value.

## 2. Map each stage's path

For each stage, write the exact route a stranger could follow: which URL, what to
click, where the value appears, which variable it fills ("Dashboard, Developers,
API keys, Reveal test key, copy"). Where the current UI or command is not known,
say so and ask or check the docs; an invented step costs the human more than a
question.

## 3. Author the stages

Copy the template to a scratch path or `scripts/`, replace the example stage with
one `stage` per step in dependency order, each at column 0 so `banner` counts it.
Open the URL before asking for its value. Use `ask_secret` for a secret and
`ask` for a non-secret. Use `write_env` only for a local destination,
`set_secret` for a CI secret, and `set_var` only for a non-secret CI variable.
A CI-only secret is not also written to `.env`. Gate irreversible actions with
`if confirm ...; then ...; fi`: under `set -e`, a bare `confirm` would exit on
"no" instead of skipping the action. Keep one task per stage.

## 4. Verify statically and hand off

`bash -n`, `shellcheck` when available, `chmod +x`. Never run it end to end: it
opens browsers and blocks on input. Trace it instead: every value from step 1 is
captured and lands where step 1 said, and every CI write matches the corresponding
`secrets.*` or `vars.*` reference. Tell the user the command to run. The wizard
is deleted when the job is done unless the user wants a repeatable setup path
kept in the repository.
