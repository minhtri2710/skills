# BEO Tool Contracts

## TC-01 — No implicit command semantics

A command has BEO workflow meaning only when this reference defines its contract.

Agents must not infer command behavior from:
- command name
- shell alias
- local convention
- chat
- memory
- examples
- previous usage
- package scripts
- terminal output not defined by contract

If a command has no contract here, its output is not workflow authority.

Uncontracted command output may be recorded only as raw implementation or verification evidence when the active owner already has permission to run that kind of command and the command does not mutate unauthorized surfaces.

Uncontracted command output must not affect:
- owner selection
- approval
- readiness
- integrity
- execution scope
- selected execution set
- declared files
- forbidden paths
- generated outputs
- verification contract
- review verdict
- learning provenance
- Human Gate status

## Command authority default

Workflow-visible command output has no authority over:

- approval
- readiness
- integrity
- selected execution set
- scope
- owner identity
- review verdict
- learning provenance

unless this file defines the exact command/subcommand output as authority for that exact field.

## TC-02 — Command output authority levels

Every command or subcommand contract must declare exactly one authority level:

- `none`
- `navigation`
- `evidence`
- `integrity_evidence`
- `artifact_mutation`
- `product_mutation`

| Authority level | Meaning |
|---|---|
| `none` | Output is informational only and must not affect workflow decisions. |
| `navigation` | Output may help locate surfaces but does not prove workflow state. |
| `evidence` | Output may support an owner decision but does not grant authority by itself. |
| `integrity_evidence` | Output may support integrity status but does not grant approval by itself. |
| `artifact_mutation` | Command may write workflow artifacts only as stated by the contract and only when the active owner owns that write. |
| `product_mutation` | Command may mutate product files only when `beo-execute` is active with fresh approval and mutation is inside the approved envelope. |

No command output may grant approval, refresh approval, emit review verdicts, select owners, bypass Human Gates, or override current required surfaces unless a canonical BEO reference explicitly grants that authority to the active owner.

## TC-03 — Missing contract means unavailable

If an owner needs a workflow-visible command and the exact command or subcommand has no contract, the command is unavailable for workflow authority.

The owner must stop before relying on that command output.

The owner may continue only if the command output is not needed for workflow authority and the active owner can safely proceed from current required surfaces.

## TC-04 — Command result classification

Command results must be classified as:

- `usable`
- `invalid`
- `unavailable`
- `contradictory`
- `stale`

Rules:

- missing command -> `unavailable`
- missing command contract -> `unavailable`
- missing subcommand contract -> `unavailable`
- missing required output field -> `invalid`
- malformed output -> `invalid`
- output contradicts current required surfaces -> `contradictory`
- output older than an approval-bearing change -> `stale`
- output from an unknown command contract -> `unavailable`
- output outside allowed owner or stage -> `invalid`

Failed command output must not be upgraded by inference.

## TC-05 — Subcommands require explicit contracts

A top-level command contract does not authorize every subcommand.

Each subcommand that affects workflow decisions must define:
- purpose
- allowed owner
- allowed stage
- reads
- writes
- output format
- required output fields
- authority level
- staleness rule
- failure handling
- forbidden interpretations

Unknown subcommands are unavailable for workflow authority.

Top-level command contracts define command boundaries only.
Subcommand contracts define actual workflow authority.

---

## Command contract schema

Each workflow-visible command or subcommand contract must use this shape:

### Command: `<name>`

Purpose:
<one sentence>

Command form:
```sh
<canonical command invocation>
```

Allowed callers:
- <owner or none>

Allowed stages:
- <stage or none>

Reads:
- <surface or file class>

Writes:
- <surface or file class, or none>

Output format:
- human_text | json | markdown | file_mutation | exit_code_only

Required output fields:
- <field or N/A>

Exit codes:
| Code | Meaning |
|---:|---|
| 0 | success |
| 1 | invalid |
| 2 | unavailable |
| 3 | usage error |

Authority level:
- none | navigation | evidence | integrity_evidence | artifact_mutation | product_mutation

May grant approval?
- no

May refresh approval?
- no

May select execution set?
- no

May mutate product files?
- no, unless authority level is `product_mutation` and `beo-execute` is active with fresh approval

May mutate workflow artifacts?
- no, unless listed under Writes and allowed by the active owner

Staleness rule:
<when output becomes stale>

Failure handling:
<how the active owner classifies failures>

Forbidden interpretations:
- <what agents must not infer>

A command contract is invalid if it lacks allowed callers, allowed stages, reads, writes, output format, required output fields, authority level, staleness rule, or failure handling.

---

### Command: `br`

Purpose:
Boundary contract for BR task command usage.

Command form:
```sh
br <subcommand> <args>
```

Allowed callers:
- none at top-level

Allowed stages:
- none at top-level

Reads:
- undefined at top-level

Writes:
- undefined at top-level

Output format:
- undefined at top-level

Required output fields:
- undefined at top-level

Exit codes:
| Code | Meaning |
|---:|---|
| 0 | top-level command availability only; not workflow authority |
| 1 | invalid request or invalid BR state |
| 2 | record missing or DB unavailable |
| 3 | usage error |

Authority level:
- none at top-level

May grant approval?
- no

May refresh approval?
- no

May select execution set?
- no

May mutate product files?
- no

May mutate workflow artifacts?
- no at top-level

Staleness rule:
All top-level `br` output is unavailable for workflow authority.

Failure handling:
Treat top-level `br` output as unavailable for workflow authority unless an exact subcommand contract applies.

Forbidden interpretations:
- Do not infer approval from a BR task description.
- Do not infer execution scope from BR alone.
- Do not let BR output override `PLAN.md`.
- Do not use BR output as review evidence unless the exact subcommand contract permits evidence authority and current required surfaces reference that BR task.

#### Command: `br show <task_id>`

Status: undefined until documented
Authority level: none
Workflow authority: unavailable until this subcommand defines required output fields and failure handling

#### Command: `br list <args>`

Status: undefined until documented
Authority level: none
Workflow authority: unavailable until this subcommand defines required output fields and failure handling

#### Command: `br ready`

Status: undefined until documented
Authority level: none
Workflow authority: unavailable until this subcommand defines required output fields and failure handling

#### Command: `br create <args>`

Status: undefined until documented
Authority level: none
Workflow authority: unavailable until this subcommand defines writes, output fields, and failure handling

#### Command: `br update <task_id> <args>`

Status: undefined until documented
Authority level: none
Workflow authority: unavailable until this subcommand defines writes, output fields, and failure handling

#### Command: `br close <task_id>`

Status: undefined until documented
Authority level: none
Workflow authority: unavailable until this subcommand defines writes, output fields, and failure handling

#### Command: `br sync <args>`

Status: undefined until documented
Authority level: none
Workflow authority: unavailable until this subcommand defines writes, output fields, and failure handling

#### Command: `br init`

Status: undefined until documented
Authority level: none
Workflow authority: unavailable until this subcommand defines writes, output fields, and failure handling

No `br` subcommand may affect workflow decisions until its own contract is complete.

A completed `br` subcommand contract must state whether output is:
- navigation only
- evidence
- artifact mutation
- unavailable

No `br` subcommand may grant approval, refresh approval, select execution sets, or override `PLAN.md`.

---

### Command: `bv`

Purpose:
Boundary contract for BV command usage.

Command form:
```sh
bv <subcommand> <args>
```

Allowed callers:
- none at top-level

Allowed stages:
- none at top-level

Reads:
- undefined at top-level

Writes:
- undefined at top-level

Output format:
- undefined at top-level

Required output fields:
- undefined at top-level

Exit codes:
| Code | Meaning |
|---:|---|
| 0 | top-level command availability only; not workflow authority |
| non-zero | unavailable for workflow authority |

Authority level:
- none at top-level

May grant approval?
- no

May refresh approval?
- no

May select execution set?
- no

May mutate product files?
- no

May mutate workflow artifacts?
- no at top-level

Staleness rule:
All top-level `bv` output is unavailable for workflow authority.

Failure handling:
Treat all top-level `bv` output as unavailable for workflow authority unless an exact subcommand contract applies.

Forbidden interpretations:
- Do not infer that `bv` means BEO validate.
- Do not infer that `bv` grants readiness.
- Do not infer that `bv` refreshes approval.
- Do not infer that `bv` verifies integrity.
- Do not infer that `bv` is safe to run during execution.
- Do not use bare `bv` TUI in agent sessions.

#### Command: `bv --robot-triage`

Status: undefined until documented
Authority level: none
Workflow authority: unavailable until this subcommand defines reads, output fields, staleness, and failure handling

#### Command: `bv --robot-next`

Status: undefined until documented
Authority level: none
Workflow authority: unavailable until this subcommand defines reads, output fields, staleness, and failure handling

#### Command: `bv --robot-plan`

Status: undefined until documented
Authority level: none
Workflow authority: unavailable until this subcommand defines reads, output fields, staleness, and failure handling

#### Command: `bv --robot-insights`

Status: undefined until documented
Authority level: none
Workflow authority: unavailable until this subcommand defines reads, output fields, staleness, and failure handling

#### Command: `bv --robot-history`

Status: undefined until documented
Authority level: none
Workflow authority: unavailable until this subcommand defines reads, output fields, staleness, and failure handling

#### Command: `bv --robot-diff --diff-since <ref>`

Status: undefined until documented
Authority level: none
Workflow authority: unavailable until this subcommand defines reads, output fields, staleness, and failure handling

No `bv` robot subcommand may affect workflow decisions until its own contract is complete.

A completed `bv` robot subcommand contract must state whether output is:
- navigation only
- evidence
- artifact mutation
- product mutation
- unavailable

No `bv` subcommand may grant approval, refresh approval, emit `PASS_EXECUTE`, verify integrity, or emit review verdicts.

---

### Command: `beo_approval_check.py`

Purpose:
Produce deterministic approval-integrity evidence.

Canonical authority:
`beo-reference -> references/approval-integrity.md`

Command form:
```sh
python reference/scripts/beo_approval_check.py \
  --feature <feature_slug> \
  --lane beo_tiny|standard \
  --artifact-root .beads/artifacts/<feature_slug> \
  --state .beads/STATE.json \
  --output-json
```

Allowed callers:
- beo-validate
- beo-execute
- beo-review

Allowed stages:
- validation before `PASS_EXECUTE`
- execution immediately before first mutation
- review before terminal accept when integrity evidence must be checked

Reads:
- current required surfaces for the active feature
- `.beads/STATE.json` only as an input path, not approval authority

Writes:
- none

Output format:
- json

Required output fields:
Defined in `approval-integrity.md`.

Exit codes:
| Code | Meaning |
| ---:| --- |
| 0 | `integrity: verified` and `safe_for_execute: true` for requested check |
| 1 | `integrity: invalid` or `stale` |
| 2 | `integrity: unavailable` due to unreadable/missing required surface |
| 3 | helper usage/configuration error |

Authority level:
- integrity_evidence

May grant approval?
- no

May refresh approval?
- no

May select execution set?
- no

May mutate product files?
- no

May mutate workflow artifacts?
- no

Staleness rule:
Defined in `approval-integrity.md`.

Failure handling:
Defined in `approval-integrity.md`.

Forbidden interpretations:
- `safe_for_execute: true` is not approval.
- helper output does not authorize mutation.
- helper output does not refresh approval.
- helper output does not emit review verdict.
