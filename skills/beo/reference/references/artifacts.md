# BEO Artifacts

## ART-01 — Current required surfaces only

BEO runtime uses only current required surfaces for the active lane and stage. Artifacts consolidate I/O, not owner authority. Owner boundaries remain even when multiple owners write different sections of the same file.

## ART-02 — Tiny required surface

Tiny lane requires `TICKET.md` only.

## ART-03 — Standard required surfaces

Standard lane required surfaces are stage-scoped. See the stage-scoped required-surface matrix below; `REVIEW.md` is not required before execution.

## ART-04 — Optional surfaces never override required surfaces

Optional surfaces (`STATE.json`, `HANDOFF.json`, learning files, BR descriptions) never override required surfaces.

## ART-05 — Precedence

When surfaces conflict, the canonical required surface wins. Mirrors and summaries are stale. Do not average conflicting surfaces. Identify the highest-precedence canonical surface, then repair by the owner that owns the defective surface.

Precedence order (standard):
1. Active owner contract
2. `TRACKER.json` owner-owned section for readiness/approval/integrity/execution
3. `CONTEXT.md` for locked requirements
4. `PLAN.md` for canonical bead graph, scope, dependencies, execution sets, verification
5. BR task descriptions for per-bead executable slices
6. `REVIEW.md` for terminal verdict
7. `STATE.json` display mirrors
8. `HANDOFF.json` resume context
9. Chat memory

If a BR task description conflicts with `PLAN.md`, `PLAN.md` wins.

## ART-06 — Generated outputs

Generated outputs are legal only when declared in the selected execution envelope or produced as approved verification byproducts.

Undeclared generated outputs block accept. Broad or nondeterministic generated outputs reclassify tiny to standard.

## ART-07 — Review evidence surfaces

Review reads cold evidence from current required surfaces and live declared files. Memory and chat summaries are never review evidence (REV-01).

## Evidence authority ladder

| Authority class | Examples | Can grant approval? | Can select execution set? | Can inform review? |
| --- | --- | ---:| ---:| ---:|
| Canonical required surface | `TICKET.md`, `CONTEXT.md`, `PLAN.md`, `TRACKER.json`, `REVIEW.md` when stage-required | Only through validate-owned approval fields | Yes, when canonical surface owns that field | Yes, when current and stage-appropriate |
| Helper integrity evidence | `beo_approval_check.py` output | No | No | Yes, only as integrity/status evidence |
| Contracted command output | `br`, `bv --robot-*`, documented verification commands | No | No | Yes, only when contract-defined, current, well-formed, and tied to current required surfaces |
| Live declared file evidence | files in approved declared scope | No | No | Yes |
| Mirror/display | `STATE.json`, display cards, setup reports | No | No | No, except as pointers to canonical evidence |
| Chat/user instruction | conversation text | No | No | No, except Human Gate answers captured into canonical surfaces |
| Optional/reference artifact | examples, notes, packets, summaries | No | No | Only as navigation aid |

Command output never overrides canonical required surfaces unless a canonical reference explicitly says so.

Uncontracted command output may be recorded as raw evidence only. It must not affect approval, readiness, integrity, scope, selected execution set, owner identity, review verdict, or learning provenance.

## Stage-scoped required-surface matrix

| Lane | Stage | Required surfaces |
| --- | --- | --- |
| `beo_tiny` | all runtime stages | `TICKET.md` |
| `standard` | explore | `CONTEXT.md` |
| `standard` | plan | `CONTEXT.md` + `PLAN.md` |
| `standard` | validate | `CONTEXT.md` + `PLAN.md` + `TRACKER.json` |
| `standard` | execute | `CONTEXT.md` + `PLAN.md` + `TRACKER.json` + selected BR descriptions only when canonical `PLAN.md`/`TRACKER.json` references selected BR tasks |
| `standard` | review | `CONTEXT.md` + `PLAN.md` + `TRACKER.json` + `REVIEW.md` when created + selected BR descriptions only when canonical `PLAN.md`/`TRACKER.json` references selected BR tasks + live declared files |
| `any` | learning case recording | selected source evidence + `.beads/learnings/<case_slug>.md` |

`REVIEW.md` is not required before execution. `TRACKER.json` is not required before standard planning initializes it. Owner predicates must say "current required surfaces for the active stage," not "all required surfaces."

## Artifact field ownership table

| Field/surface | Owner allowed to write | Notes |
| --- | --- | --- |
| request/acceptance/non-goals | explore | tiny `TICKET.md` or standard `CONTEXT.md` |
| Human Gate captured answers | explore, or validate only for approval evidence already required by validation | must be persisted into current required surface; secrets are never persisted (HG-02) |
| plan/bead graph/declared files/generated outputs | plan | `PLAN.md` or `TICKET.md` Plan section |
| readiness classification | validate | `TRACKER.json` or `TICKET.md` Approval section |
| approval fields and `approval_ref` | validate only | helper output is evidence, not writer (INT-03) |
| integrity evidence pointer/status | validate records after reading helper output | helper does not mutate runtime artifacts |
| execution evidence | execute | `TRACKER.json` or `TICKET.md` Execution section |
| review verdict/disposition | review | `REVIEW.md` or `TICKET.md` Review/Closure |
| bounded repair packet | review | evidence only; not executable scope |
| learning case file | compound | one observed learning case or false case |
| consolidated learning pattern | dream | repeated finalized case consolidation only |
| shared guidance | author by explicit request or selected evidence | never from single runtime review |
| STATE display mirrors | active owner that owns handoff | display only, loses to required surfaces |
| HANDOFF.json | active owner when pausing/transferring | never grants approval or verdict |

Rule: if an owner `SKILL.md` writable surface conflicts with this table, the owner file is wrong unless the table is updated in the same doctrine edit.

## Tiny TICKET.md schema

```md
# TICKET: <feature_slug>

## Lane
beo_tiny

## Request
<user request in one compact paragraph>

## Acceptance
- <one clear acceptance outcome>

## Non-goals
- <N/A or explicit out-of-scope item>

## Scope
Allowed files:
- <path>

Forbidden paths:
- <path or pattern>

Generated outputs:
- <N/A or declared generated output>

## Risk
Security/privacy: N/A | <risk>
Data/destructive: N/A | <risk>
Permissions/billing/legal: N/A | <risk>
Existing user/data support: N/A | <risk>

## Human Gates
Required gates:
- none
or
- <blocking gate>

## Plan
Bead:
- ID: B1
- BR task: <br-id or N/A>
- Action: <smallest executable action>
- Verification: <direct cheap check>

## Approval
Readiness: PASS_EXECUTE | FAIL_PLAN | FAIL_EXPLORE | BLOCK_USER | FAIL_STATE
Approval ref: <ref or N/A>
Integrity: verified | stale | invalid | unavailable
Approved execution set: B1
Execution mode: single

## Execution
Status: not-started | completed | blocked
Changed files:
- <path>

Verification evidence:
- <command/check/result>

Blocked by:
- <N/A or blocker>

## Review
Verdict: pending | accept | fix | reject
Evidence:
- <specific evidence>

Learning case: none | present
learning_source:
  origin_owner: <owner or N/A>
  source_surface: <surface or N/A>
  source_section_or_pointer: <pointer or N/A>
  case_type: <type or N/A>
  case_status: candidate
  affected_owner: <owner or none>
  target_path: <path or none>
  runtime_status: runtime_complete | runtime_active | user_blocked

## Closure
Next owner: <owner | done | user>
Reason: <one line>
```

## Standard schemas

### CONTEXT.md

```md
# CONTEXT: <feature_slug>

## Request
...

## Acceptance requirements
- A1: ...

## Non-goals
- ...

## Constraints
Security/privacy:
Existing user/data support:
Access/secrets:
Legal/business:
Performance:
UX/API:

## Human Gates
Required:
- ...

Resolved:
- ...

N/A:
- ...

## Assumptions
- ...

## Trace anchors
- A1: ...
```

Approval-bearing content: acceptance requirements, non-goals, constraints, required Human Gates, scope/acceptance assumptions, and trace anchors.

### PLAN.md

```md
# PLAN: <feature_slug>

## Requirement trace
| Acceptance ID | Plan coverage | Verification |
| --- | --- | --- |
| A1 | B1 | V1 |

## Execution beads
| Bead ID | BR task ID | Purpose | Depends on | Declared files | Generated outputs | Verification |
| --- | --- | --- | --- | --- | --- | --- |
| B1 | br-123 | ... | none | ... | ... | V1 |

## Execution sets
| Set ID | Mode | Beads | Stop rule |
| --- | --- | --- | --- |
| ES1 | single | B1 | stop on block |

## Declared files
- ...

## Forbidden paths
- ...

## Generated outputs
- N/A

## Verification contract
- V1: ...

## Risk proof
Security/privacy: N/A | ...
Data/destructive: N/A | ...
Permissions/billing/legal: N/A | ...
Existing user/data support: N/A | ...

## Rollback boundary
- ...

## Human blockers
- none
```

Approval-bearing content: execution beads, BR task bead mapping, execution sets, mode, selected bead IDs, declared files, forbidden paths, generated outputs, verification contract, risk proof, rollback boundary, and human blockers.

### TRACKER.json schema

`TRACKER.json` is the only standard tracking record for readiness, approval, integrity, execution, and review pointers.

```json
{
  "schema_version": 2,
  "feature_slug": "example_feature",
  "lane": "standard",
  "readiness": {
    "status": "PASS_EXECUTE",
    "classified_by": "beo-validate",
    "selected_execution_set_id": "ES1",
    "execution_mode": "single",
    "selected_beads": ["B1"],
    "selected_br_tasks": ["br-201"],
    "next_owner": "beo-execute",
    "blockers": []
  },
  "approval": {
    "approval_ref": "approval-2026-05-07-001",
    "approved_by_owner": "beo-validate",
    "approved_declared_files": [],
    "approved_forbidden_paths": [],
    "approved_generated_outputs": [],
    "verification_contract_ref": "PLAN.md#verification-contract",
    "status": "fresh"
  },
  "integrity": {
    "method": "tool",
    "tool": "beo_approval_check.py",
    "status": "verified",
    "context_status": "complete",
    "plan_status": "complete",
    "br_description_status": "complete",
    "selected_execution_set_status": "complete",
    "declared_files_status": "complete",
    "forbidden_paths_status": "complete",
    "verification_contract_status": "complete",
    "errors": []
  },
  "execution": {
    "status": "not-started",
    "changed_files": [],
    "generated_outputs": [],
    "file_change_baseline": [],
    "final_file_evidence": [],
    "verification_evidence": [],
    "review_packet": {
      "feature_slug": "example_feature",
      "execution_set_id": "ES1",
      "execution_mode": "single",
      "selected_beads": ["B1"],
      "changed_files": [],
      "declared_files_checked": true,
      "forbidden_paths_checked": true,
      "generated_outputs": ["N/A"],
      "verification_evidence_refs": [],
      "integrity_status_at_execution": "verified",
      "known_deviations": [],
      "blocked_items": [],
      "ready_for_review": false
    },
    "ready_for_review": false,
    "blocked_by": null
  },
  "review_pointer": {
    "review_path": "REVIEW.md",
    "verdict": "pending"
  },
  "history": []
}
```

`history` is append-only and short. Do not turn it into a transcript.

### REVIEW.md

```md
# REVIEW: <feature_slug>

## Verdict
accept | fix | reject

## Evidence reviewed
- CONTEXT.md:
- PLAN.md:
- BR task descriptions:
- TRACKER.json:
- changed files:
- verification evidence:

## Trace coverage
| Acceptance | Evidence | Status |
| --- | --- | --- |

## Findings
| Severity | Finding | Evidence | Required next owner |
| --- | --- | --- | --- |

## Integrity status
verified | stale | invalid | unavailable

## Generated outputs
Declared/approved:
- ...

Observed:
- ...

Status:
- ok | mismatch

## Learning case
none | present

## learning_source
origin_owner: <owner or N/A>
source_surface: <surface or N/A>
source_section_or_pointer: <pointer or N/A>
case_type: <type or N/A>
case_status: candidate
affected_owner: <owner or none>
target_path: <path or none>
runtime_status: runtime_complete | runtime_active | user_blocked

## Next owner
done | beo-plan | beo-explore | beo-debug | beo-compound | user

## Reason
...
```

## Tiny lane compression rule

Tiny keeps the same authority invariants as standard but collapses the required surfaces into `TICKET.md`.

Tiny must not require separate CONTEXT, PLAN, TRACKER, or REVIEW files.

Tiny requires exactly:

- one request paragraph
- one acceptance outcome
- explicit allowed files
- explicit forbidden paths
- generated outputs or N/A
- one executable bead
- one verification contract
- one approval block
- one execution block
- one review/closure block

Tiny remains tiny only when:

- one meaningful bead is enough
- file scope is small and explicit
- generated outputs are N/A or deterministic and declared
- verification is direct and cheap
- no multi-phase or ambiguous Human Gate is required

Reclassify to standard when:

- multiple meaningful beads are needed
- scope cannot fit explicit allowed files
- generated outputs are broad or nondeterministic
- risk proof needs multiple surfaces
- approval/review evidence would become ambiguous in one file

## Learning artifacts

`.beads/learnings/<case_slug>.md` records one observed learning case or false case.
`.beads/learnings/<pattern_slug>.md` may record one consolidated learning pattern.

Learning artifacts:
- Learning has no runtime authority; see `references/learning.md`.
- May be read only by `beo-compound`, `beo-dream`, or `beo-author` when their predicates are active.

`beo-compound` reads only the selected source evidence for one learning case.

`REVIEW.md` is compound-readable only when review produced the learning case or the user explicitly selected `REVIEW.md` as source evidence. Otherwise, compound reads the actual source output from debug, validate, execute, route, or user-provided selected case text.

See `learning.md` for learning case and pattern templates.

## BR task bead decomposition

`PLAN.md` is the canonical graph and source of truth. A `br` task description is only the executable slice for that bead and never grants approval.

Do not copy full `CONTEXT.md`, full `PLAN.md`, all other beads, tracker state, review doctrine, learning doctrine, setup doctrine, or irrelevant owner contract text into BR descriptions.

## Rollback boundary

`PLAN.md` must state one of:

- `rollback: not_applicable` with reason
- `rollback: revert declared file changes`
- `rollback: manual user decision required`
- `rollback: impossible/destructive` with risk proof and Human Gate before approval

Rollback boundary is approval-bearing. Changing it stales approval.

## Review evidence packet

The review packet in `TRACKER.json.execution.review_packet` or `TICKET.md` Execution section is a navigation aid, not authority. `beo-review` must still read current required surfaces and live declared files. If the packet conflicts with canonical artifacts or live evidence, the packet loses.
