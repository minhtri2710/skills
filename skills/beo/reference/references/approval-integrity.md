# BEO Approval Integrity

## INT-01 — Required integrity is tool-owned

LLMs must not calculate SHA-256 or manually write approval hash strings. Integrity verification belongs to deterministic tooling. Agents consume status only.

## INT-02 — Helper must fail closed

The helper must fail closed on missing, contradictory, stale, unsupported, or unverifiable fields. Missing baseline is `integrity: invalid`, not a warning.

## INT-03 — Helper output is evidence only

Helper output alone does not grant approval. `beo-validate` grants approval after reading helper evidence.

`safe_for_execute: true` in helper output means "evidence supports approval." It does not mean "mutation is authorized."

## INT-04 — Helper integrity statuses

Helper global integrity statuses are: `verified | stale | invalid | unavailable`. No other global integrity status is valid.

Field-level helper sub-fields use: `complete | missing | invalid | unavailable`. These describe evidence completeness per field, not global integrity.

Do not use `N/A` as a status value. Do not use `pass | fail` as status values.

Any helper output that contains `status: pass` or `status: fail` is using stale output format and must be treated as `unavailable` until re-run.

## Helper output contract

```json
{
  "schema_version": 2,
  "feature_slug": "...",
  "lane": "beo_tiny | standard",
  "readiness": "PASS_EXECUTE | FAIL_PLAN | FAIL_EXPLORE | BLOCK_USER | FAIL_STATE",
  "approval_ref": "...",
  "selected_execution_set": "...",
  "integrity": "verified | stale | invalid | unavailable",
  "approval_bearing_hash": "...",
  "checked_at": "...",
  "declared_files_status": "complete | missing | invalid | unavailable",
  "forbidden_paths_status": "complete | missing | invalid | unavailable",
  "generated_outputs_status": "complete | missing | invalid | unavailable",
  "verification_contract_status": "complete | missing | invalid | unavailable",
  "safe_for_execute": true | false,
  "helper_authority": "advisory_integrity_check",
  "machine_hashes": {},
  "errors": [],
  "warnings": []
}
```

`safe_for_execute: true` may appear only when readiness is `PASS_EXECUTE` and global integrity is `verified`. `safe_for_execute: false` or absent must not be treated as approval. `helper_authority` must not imply approval authority. Approval still belongs to `beo-validate`.

Global `integrity: verified` is required before `PASS_EXECUTE` (INT-03). Helper output alone does not grant approval (INT-03). The helper must fail closed (INT-02). Manual hash computation is forbidden (INT-01).

If dropping any additional field, update every owner/reference consumer in the same phase.

## Helper CLI contract

```bash
python reference/scripts/beo_approval_check.py \
  --feature <feature_slug> \
  --lane beo_tiny|standard \
  --artifact-root .beads/artifacts/<feature_slug> \
  --state .beads/STATE.json \
  --output-json
```

Optional modes:

```bash
--check validate   # evidence needed before PASS_EXECUTE
--check execute    # evidence needed immediately before first mutation
--check review     # evidence needed before terminal verdict
--strict           # default; fail closed on all missing baselines and contradictions
```

## Exit codes

| Exit code | Meaning |
| ---:| --- |
| 0 | `integrity: verified` and `safe_for_execute: true` for requested check |
| 1 | `integrity: invalid` or `stale` |
| 2 | `integrity: unavailable` due to unreadable/missing required surface |
| 3 | helper usage/configuration error |

## CLI conflict handling

If both positional `feature_slug` and `--feature` are provided and differ, fail closed:

```text
error: conflicting feature slug values
exit non-zero
no approval result emitted
```

Do not silently prefer one value.

## Schema stability

- Output keys are stable.
- New keys are additive only.
- Global integrity vocabulary remains `verified | stale | invalid | unavailable`.
- Field-level status vocabulary is `complete | missing | invalid | unavailable` only.
- `safe_for_execute` is present in every output and is never a substitute for approval.
- If hash normalization changes, increment `schema_version`.

## Owner use

- `beo-validate` calls the helper, records integrity status, and grants/refuses `PASS_EXECUTE`.
- `beo-execute` checks helper status immediately before first mutation and stops on stale/invalid/unavailable required integrity (APP-01).
- `beo-review` checks integrity, may rerun helper when live evidence is suspicious, and refuses accept on stale/invalid integrity (REV-01).

Malformed or contradictory required surfaces produce `invalid`. Missing or unreadable required surfaces produce `unavailable`. Missing baseline is `invalid`.

## Staleness

Approval becomes stale when approval-bearing content changes in `TICKET.md`, `CONTEXT.md`, `PLAN.md`, selected BR task descriptions, selected execution set, declared files, forbidden paths, generated outputs, verification contract, risk proof, rollback boundary, or required Human Gates.

## Parser tolerance

The helper should tolerate safe markdown variants:
- trailing whitespace in headings;
- heading case differences where safe;
- extra blank lines;
- table spacing differences;
- common capitalization variants such as `Machine Hashes` vs `Machine hashes`.

The helper must not tolerate semantic ambiguity:
- duplicate approval sections;
- multiple conflicting lane values;
- multiple conflicting readiness values;
- approval ref mismatch;
- declared files contradiction;
- forbidden path contradiction.

## Hashing rules

Approval-bearing hash must exclude machine-generated hash output itself.

Hash normalization should be documented here. If hash normalization changes, increment `schema_version`.

## Learning non-authority

Learning has no runtime authority; see `references/learning.md`.

## Tool contract registration

The approval helper is registered as a workflow-visible command in `references/tool-contracts.md`, but its output authority remains defined here.
