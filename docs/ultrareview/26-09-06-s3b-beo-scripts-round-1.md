# Ultra Review: s3b-beo-scripts Round 1

Date: 26-09-06
Review name: s3b-beo-scripts
Round: 1
Scope: skills/beo/beo-reference/scripts at 038dc27: 17 tracked Python files, 5968 lines
Report path: docs/ultrareview/26-09-06-s3b-beo-scripts-round-1.md
Review brief sha256: e4456bd09ff81acf3104cad861d887e236f9fd82084a3974a522d185035acfa2
Scouts: 10 (`Explore` kind, model `sonnet`) | Directives: 10 (D01-D10)
Candidate file: `skills/ultra-review-workspace/campaign-01/S3B-CANDIDATES.md` (2212 lines, ten verbatim blocks)

## Prior Round Guard

Previous reports read:
- `docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1.md`
- `docs/ultrareview/26-09-06-s2-ultra-review-pair-round-1.md`
- `docs/ultrareview/26-09-06-s3a-beo-doctrine-round-1.md`

S3a deferred five questions to this slice. All five are settled below, three of them against a reading this campaign previously recorded. Two further S3a items carry `Q` numbers but were not deferrals and so are not in this list: **Q6** was a framing error in the coordinator's own brief and is dispositioned in the Coordinator Method Note; **Q7** is settled inside F045's evidence. Five deferrals, five entries:

- **Q1 (`approved_phase_sequence_id` stamp side) — NO DEFECT.** The prior campaign record said the doctrine's "pre-transition" wording was the wrong side. That record is withdrawn. `registry/approval-envelope.json:89` reads: *"First durable state.json transition from an approved state whose approval.approved_phase_sequence_id equals the pre-transition phase_sequence_id, to executing..."* — the transition it describes is **approved -> executing**, and "pre-transition" is the sequence id before *that* edge. `beo_state.py:608` stamps `approved_phase_sequence_id` at the **validate -> approved** write, and `execution_entry_is_current` (`beo_state.py:617`) compares it against `before["phase_sequence_id"]` at the approved -> executing edge. Those are the same number. Code and doctrine agree; a literal pre-increment stamp would make the check permanently off by one. Scouts 01 (S3b-01-21) and 10 (S3b-10-05, an explicit self-correction) reached this; scouts 02, 04, 09 and 03 filed the opposite reading and are overruled by the text.
- **Q2 (`payload_contracts` parsed?) — YES, PARTIALLY.** `beo_state.py:495` reads `field_schema.get("registry") == "pipeline.condition_id"` and validates the payload field against the pipeline's condition set. Enforcement covers `runtime-events.jsonl` entries only, not `state.json` top-level fields (S3b-03-15).
- **Q4 (`beo_worktree.py cleanup` branch ref) — CONFIRMED DEFECT.** `beo_worktree.py:294` runs `["git", "branch", "-D", existing]` unconditionally. See F021.
- **Q5 (`execution.interventions`) — VALIDATED, NEVER GATING.** Shape and enum are checked by `validate_state`; no in-scope script populates the field and no decision reads it (S3b-01-20, S3b-03-11). See F050.
- **Q8 (`review.reviewed_by`) — CONFIRMED DEFECT.** `beo_state.py:57` sets `"reviewed_by": "beo-review"` at record creation; no script in scope ever rewrites it. See F010.

## Coordinator Method Note — Three Errors In My Own Brief

These are the coordinator's errors, not the scouts'. Each is corrected here and each was corrected on-turn against the tree:

1. **"23 subprocess sites by grep" is a line-match count, not a call-site count.** `grep -nE 'subprocess\.(run|Popen|call|check_output|check_call)\(' *.py | wc -l` -> **16** call sites (`beo_check.py` 3, `beo_io.py` 2, `beo_run.py` 1, `beo_verify.py` 1, `beo_worktree.py` 9). `grep -n 'subprocess' *.py | wc -l` -> **23**, which is the figure the brief carried. Scout-02 (S3b-02-19) and scout-06 caught this correctly with 16. Scout-08 (S3b-08-08) also caught the class but derived **17**, which is wrong. The report's number is **16 call sites / 23 line matches**.
2. **The brief named the field `approval.reviewed_by`.** The field is `review.reviewed_by` (`beo_state.py:57`, `:321`). Caught by S3b-01-01.
3. **The brief framed Q6 as raw `fnmatch` semantics on full paths.** `beo_paths.py`'s matcher is a custom **per-segment** matcher in which `/` is a hard separator, so `protected_path_defaults` matching is effectively recursive in a way plain `fnmatch` would not be. Caught by S3b-02-11 and S3b-09-06. Q6 closes as **no defect, wrong framing in the brief**.

## Candidates Rejected On Source

Two candidates are rejected because the file contradicts them. Both were checked on the turn this report was written.

- **S3b-06-06 (`_result_passed` self-attestation bypass) — REJECTED.** There is no `_result_passed` in the bundle (`grep -n '_result_passed' *.py` -> no match). `beo_run.py:142` and `:155` compute `ok = result["exit_code"] == 0` directly. The `status` string at `beo_run.py:146` is a display label derived from `ok`, not an input to it. No self-reported status overrides an exit code on this path.
- **S3b-01-16 (`payload_contracts` "registry": "pipeline.condition_id" never validated) — REJECTED.** `beo_state.py:495` performs exactly that cross-reference check. The scout's own D07 sibling (S3b-01-22) records the opposite conclusion; the file supports S3b-01-22.
- **S3b-04-05, first half — PARTIALLY REJECTED.** The claim that `read_state` is unlocked is false: `beo_state.py:126-133` takes `_locked(base / "state.lock")` around the read. Scout-01 (S3b-01-09) has this right. The finding's second half — that `fcntl.flock(LOCK_EX)` is blocking with no `LOCK_NB` and no staleness detection — stands and is carried as F029.

## Findings

Severity scale used throughout. **P1**: a record already written is false, or a mandatory gate is unsatisfiable, or a mandatory gate is satisfiable without doing its work, or a machine-readable contract declares a constraint it structurally cannot impose. **P2**: a rule cannot be executed as written, or the instrument cannot measure what it claims. **P3**: clarity, robustness, dead surface.

### F001 [P1] `review.cross_check` is schema-legal, gate-required, and unconditionally rejected by the only sanctioned writer — the strict-mode acceptance gate is structurally unsatisfiable

Severity: P1 | Confidence: high
Candidates: S3b-01-02, S3b-07-01, S3b-03-09
Source pointer: `skills/beo/beo-reference/scripts/beo_state.py:259`, `beo_check.py:496-509`, `registry/state.schema.json`
Evidence (all three read on the turn this report was written):
- `registry/state.schema.json` declares `review.cross_check` as an object with `required: ["reviewer","verdict"]` and the description "Required for strict-mode verdict_accept."
- `beo_check.py:498-508` enforces it: when `ticket["mode"] == "strict"` and `review.route_condition_id == "verdict_accept"`, a missing or non-`agree` `cross_check` is an error.
- `beo_state.py:259` hardcodes `review_fields = {"actor","verdict","route_condition_id","findings","done_criteria_coverage","repair_count","closed_in_br","reviewed_by"}` — `cross_check` is absent — and `beo_state.py:314` calls `_reject_unknown_fields(review, review_fields, "review")`, which raises on any key not in that set.
- `validate_state` runs inside `locked_update_state` before `atomic_write_json`, so every sanctioned write path is covered.
Contract violated:
- A gate declared mandatory by both the schema and the checker cannot be satisfied through any write path the bundle offers. Writing `cross_check` raises; not writing it fails the gate.
Plausible failure mode:
- A strict-mode bead can never be accepted. Either the operator abandons strict mode, or the state file is hand-edited around the writer — which defeats the lock, the atomic write, and the audit trail simultaneously.
Durable solution hypothesis:
- Split the one hardcoded set into two: an allowlist (`review_fields | {"cross_check"}`) and a required-set (the current eight). Adding `cross_check` to the single existing set would make it unconditionally required for quick and standard mode as well, which is a second defect, not a fix. Better still, derive both sets from `state.schema.json`'s `review.properties` and `review.required` rather than restating them in Python — the schema already carries exactly this distinction.
Disconfirming check:
- `python3 -c "import beo_state; print('cross_check' in beo_state.__dict__)"` proves nothing; the real check is `grep -n cross_check beo_state.py`, which returns no match.

### F002 [P1] Re-running `beo_run.py` against a closed bead durably writes `phase=approved` beside a standing `verdict_accept` — a false record on disk

Severity: P1 | Confidence: high
Candidates: S3b-03-06, S3b-03-12, S3b-04-07, S3b-07-02
Source pointer: `beo_state.py:582-601`, `beo_run.py:114-130`
Evidence (trace re-derived from source this turn):
- `beo_state.py:582` opens the phase-precondition block with `if owner == "beo-execute":`. There is no equivalent block for `beo-validate` or `beo-review`.
- `beo_state.py:598-599` raises `"beo-execute may not emit verdict_accept; that route signals br close and is beo-review only"` — but only inside that `beo-execute` branch.
- `beo_run.py:114-124` defines `_grant_pass_execute`, which sets `state["phase"] = "approved"` and updates `state["approval"]`. It does not touch `state["review"]`.
- `beo_run.py:130` applies it as `locked_update_state(root, issue_id, "beo-validate", _grant_pass_execute)`. Owner is `beo-validate`, so the `verdict_accept` guard does not fire.
- `validate_state` checks phase set-membership only, never transition legality, so `reviewed -> approved` is accepted.
Contract violated:
- The state machine's ordering is enforced for exactly one of four owners. A record that says "approved, awaiting execution" is written on top of a record that says "reviewed, accepted, closed in br."
Plausible failure mode:
- An operator re-runs `beo_run.py` on an already-closed issue (a retry after a transient failure, a copy-pasted command, a script loop). The `beo-validate` write at `:130` lands. The subsequent `beo-execute` write at `:173` then raises on the `verdict_accept` guard and the process dies — but the false `phase=approved` is already durable, `phase_sequence_id` is already incremented, and the closed review is still attached. Nothing rolls it back.
Durable solution hypothesis:
- Move the transition-legality check out of the per-owner `if` and into `validate_state` (or a `legal_transition(before_phase, after_phase, owner)` predicate applied to every owner in `locked_update_state`), driven by the pipeline registry rather than by four hardcoded branches. `beo_run.py` should additionally refuse at entry when `review.route_condition_id == "verdict_accept"` or `review.closed_in_br` is set.
Disconfirming check:
- `sed -n '582,601p' beo_state.py` — if a non-`beo-execute` owner branch appears, this is false.

### F003 [P1] `beo_run.py` mints the entire approval envelope itself and calls none of `beo_check.py`'s predicates — the gate is satisfiable without doing any of its work

Severity: P1 | Confidence: high
Candidates: S3b-06-01, S3b-06-03, S3b-09-02, S3b-01-03, S3b-03-01, S3b-02-10, S3b-03-08
Source pointer: `beo_run.py:114-130`, `beo_run.py:72-80`, `beo_check.py:546-556`
Evidence:
- `beo_run.py:119` writes the literal `"approved_by": "beo-validate"` into `state["approval"]`. No function named `beo-validate` runs; the string is the only evidence that validation happened.
- `beo_check.py:546-556` shows what `--check validate` actually does: `validate_identity`, `validate_plan`, `run_structural_check`, `validate_working_tree_prestate`, `compute_approval_fields`. `beo_run.py` calls none of them — `grep -n 'validate_identity\|validate_plan\|run_structural_check\|validate_working_tree_prestate' beo_run.py` returns no match.
- `beo_run.py:72-80` builds `ticket_path = base / "TICKET.json"` and parses it with raw `json.loads`, not `beo_ticket.read_ticket`, so no ticket schema validation runs either.
- The fields `beo_check.py`'s later `validate_approval_envelope` re-checks (`ticket_file_hash`, `repo_head`, `approval_projection_hash`, `prestate`) are all computed and written by `beo_run.py` itself at `:118-123`.
Contract violated:
- The approval envelope is supposed to be an independent attestation. On the `beo_run.py` path it is a self-report: the same process computes the evidence, writes it, and is the only thing that ever compared it to anything.
Plausible failure mode:
- Any ticket that reaches `beo_run.py` is approved. Path-safety violations, broad globs requiring a human gate, missing structural checks, a stale plan — none of them can stop it, because none of them is consulted.
Durable solution hypothesis:
- `beo_run.py` should not have a private validate phase. It should call the same predicate functions `beo_check.py --check validate` calls, and refuse on any error, or it should shell out to `beo_check.py` and refuse on a non-zero exit. One live gate implementation, not two.
Disconfirming check:
- `grep -n 'beo_check' beo_run.py` — no import, no call.

### F004 [P1] `beo_run.py` records `verdict_accept` and `closed_in_br=True` without calling `validate_review`, `validate_containment`, or the strict-mode cross-check

Severity: P1 | Confidence: high
Candidates: S3b-06-05, S3b-03-04
Source pointer: `beo_run.py:211-221`, `beo_check.py:496-509`
Evidence:
- `beo_run.py:211` sets `state["phase"] = "reviewed"` and the surrounding `_accept` updater writes the acceptance route; `beo_run.py:221` applies it as owner `beo-review`.
- `grep -n 'validate_review\|validate_containment' beo_run.py` returns no match.
- The strict-mode `cross_check` requirement lives only in `beo_check.py:498-508`, on the `--check review-entry` path, which `beo_run.py` never invokes.
Contract violated:
- Acceptance is the terminal, irreversible state transition, and on this path it is unreviewed. The containment check that proves the change stayed inside its declared scope is never run.
Plausible failure mode:
- A bead is accepted and closed in `br` with changes outside its approved scope, no second reviewer, and no done-criteria coverage check. The durable record asserts all three happened.
Durable solution hypothesis:
- Same as F003: `_accept` must run the review predicates or delegate to `beo_check.py --check review-entry` and refuse on failure. Note the interaction with F001 — once acceptance actually runs the strict-mode check, strict-mode beads become unacceptable until F001 is fixed. Fix F001 first.
Disconfirming check:
- `sed -n '205,225p' beo_run.py`.

### F005 [P1] A ticket with no verify commands completes the entire lifecycle and is accepted, with nothing executed

Severity: P1 | Confidence: high
Candidates: S3b-09-03, S3b-06-10
Source pointer: `beo_run.py:136-162`
Evidence:
- `beo_run.py:136` reads `verify_cmds = ticket.get("scope", {}).get("verify", {}).get("commands", [])`, defaulting to `[]` on any missing key.
- `all_ok` is initialised `True` at `:138` and the loop at `:140` never executes on an empty list. `behaviour_gate_command(ticket)` at `:150` returns nothing when absent.
- `beo_run.py:162` therefore does not fire, and the run proceeds to `executing`, `executed`, and acceptance.
- `beo_ticket.py`'s `validate_plan_only` schema requirement of at least one verify command is on a path `beo_run.py` never touches (see F003).
Contract violated:
- "Verified" is the claim the accepted record makes. On an empty command list the claim is vacuously true and structurally meaningless.
Plausible failure mode:
- A malformed or minimal ticket — `scope.verify` misspelled, `commands` omitted, an empty array left by a generator — passes the full gate chain and is recorded as verified and accepted.
Durable solution hypothesis:
- Refuse at entry when `verify_cmds` is empty. Vacuous truth is never an acceptable gate result; an empty gate should be a hard error, not a pass.
Disconfirming check:
- `sed -n '136,163p' beo_run.py`.

### F006 [P1] `registry/pipeline.json` declares `expected_receiver_phase_after_condition` and no script in the bundle reads it

Severity: P1 | Confidence: high
Candidates: S3b-01-15
Source pointer: `skills/beo/beo-reference/registry/pipeline.json`
Evidence (derived on-turn):
- `grep -rl expected_receiver_phase_after_condition skills/beo/beo-reference/scripts/*.py` -> no files.
- `grep -rl expected_receiver_phase_after_condition skills/beo/beo-reference/registry/` -> `pipeline.json` only.
Contract violated:
- A machine-readable registry declares a post-condition mapping — which phase the receiver must be in after each routing condition — that nothing in the bundle can impose. The declaration reads as a live constraint and is inert.
Plausible failure mode:
- A reader (human or agent) treats the mapping as enforced and builds on it. The phase after a condition is in fact whatever the owning script writes, which F002 shows is unconstrained for three of four owners.
Durable solution hypothesis:
- Either wire it into `locked_update_state`'s transition check (which F002 needs anyway — this key is the natural data source for it), or delete it. A declared-but-unenforced constraint in a registry is worse than no declaration.
Disconfirming check:
- The two greps above.

### F007 [P1] `registry/pipeline.json` declares `reservation_release_on` and nothing releases a reservation on any listed condition

Severity: P1 | Confidence: high
Candidates: S3b-01-17
Source pointer: `skills/beo/beo-reference/registry/pipeline.json`
Evidence (derived on-turn):
- `grep -rl reservation_release_on skills/beo/beo-reference/scripts/*.py` -> no files.
- `beo_reservation.py` has a release path, but it is CLI-driven (`beo_reservation.py:353` guards the release subcommand on actor identity); no lifecycle condition triggers it.
Contract violated:
- The registry declares an automatic release policy. There is no automatic release.
Plausible failure mode:
- Reservations accumulate and never expire. A bead that reaches a listed terminal condition keeps its reservation, so the next actor to claim that issue is blocked by a reservation the policy says was released.
Durable solution hypothesis:
- Call the release path from `locked_update_state` when the recorded `route_condition_id` matches a `reservation_release_on` entry, or delete the key.
Disconfirming check:
- The grep above.

### F008 [P1] `beo_run.py` hashes the approval projection without `reservation_evidence`, so strict mode's reservation binding is silently absent from the hash

Severity: P1 | Confidence: high
Candidates: S3b-01-05, S3b-03-02, S3b-10-06
Source pointer: `beo_run.py:118-123`, `beo_check.py:216`
Evidence:
- `beo_run.py:121-122` writes `ticket_file_hash` and `approval_projection_hash` computed earlier in the same function.
- `grep -n 'reservation' beo_run.py` returns no reservation computation; `beo_check.py:216` is the only site that raises for a missing actor "for strict reservation validation," and it is on the `beo_check.py` path.
- `beo_run.py:82-83` accepts a non-quick ticket with a stderr warning and "Proceeding anyway" (S3b-03-03, S3b-06-04), so a strict-mode ticket can reach this code.
Contract violated:
- In strict mode the approval hash is supposed to bind the reservation. On this path it binds a projection that omits it, and the later staleness re-check compares the same omission against itself, so it always agrees.
Plausible failure mode:
- A strict-mode bead executes with no valid reservation, and the approval envelope's own integrity check reports no drift, because the field that would have shown drift was never in the hash.
Durable solution hypothesis:
- `beo_run.py` must refuse any ticket whose `mode` is not `quick` rather than warning (this single change also closes S3b-06-04 and S3b-03-03), since every strict-mode obligation in the bundle lives on the `beo_check.py` path.
Disconfirming check:
- `sed -n '78,90p' beo_run.py` for the warning; `grep -n reservation_evidence skills/beo/beo-reference/scripts/*.py`.

### F009 [P1] `verify_issue` returns `ok: true` when every command was skipped

Severity: P1 | Confidence: high
Candidates: S3b-04-10
Source pointer: `beo_verify.py:221`
Evidence:
- `beo_verify.py:221` computes the issue verdict as `"ok": summary["fail"] == 0`.
- `summary` is `{"pass": 0, "fail": 0, "skipped": 0}` (`beo_verify.py:176`) and skipped commands increment `skipped`, never `fail`.
- With a missing worktree, every command resolves to skipped, `fail` stays 0, and the issue is reported `ok: true`.
Contract violated:
- "No failures" is not "verified." A gate that cannot run reports success.
Plausible failure mode:
- The worktree is missing or misresolved (see F016's root-resolution divergence). Verification silently degrades to zero commands and reports a pass that a caller cannot distinguish from a real one.
Durable solution hypothesis:
- `ok` must require `summary["pass"] > 0 and summary["fail"] == 0 and summary["skipped"] == 0`, or the skipped case must be a distinct third verdict that no caller may treat as a pass. Fail closed.
Disconfirming check:
- `sed -n '218,226p' beo_verify.py`.

### F010 [P1] `review.reviewed_by` is a hardcoded literal stamped at record creation and never written by any actor — the field asserts a reviewer that never acted

Severity: P1 | Confidence: high
Candidates: S3b-10-02, S3b-01-06, S3b-09-11, S3b-02-17 (closes S3a Q8)
Source pointer: `beo_state.py:57`, `beo_state.py:321-323`
Evidence:
- `beo_state.py:57` sets `"reviewed_by": "beo-review"` inside `initial_state`, unconditionally, before any review exists.
- `beo_state.py:321-323` validates it against `{"beo-execute","beo-review"}` — so the default always passes its own validator.
- `grep -n 'reviewed_by' skills/beo/beo-reference/scripts/*.py` returns only those three sites plus the `review_fields` set at `:259`. No writer.
Contract violated:
- Every state record ever created claims it was reviewed by `beo-review`, including records created seconds ago that have never been reviewed. The record is false from the moment it is written.
Plausible failure mode:
- Any audit that reads `reviewed_by` to establish who reviewed a bead gets a constant. The field cannot distinguish a reviewed record from an unreviewed one, which is precisely what it exists to do.
Durable solution hypothesis:
- Initialise `reviewed_by` to `null` and require the accepting writer to set it to the acting identity (the same `actor` resolution used elsewhere). Its validator then becomes "null, or one of the two roles." Note this compounds F026: the roles are labels, not verified identities, so setting it truthfully is necessary but not sufficient.
Disconfirming check:
- `grep -n 'reviewed_by' skills/beo/beo-reference/scripts/*.py`.

### F011 [P2] `beo_check.py:main` reads runtime events outside its own guarded block, so a corrupt event file crashes the checker instead of failing it

Severity: P2 | Confidence: high
Candidates: S3b-04-12, S3b-07-04
Source pointer: `beo_check.py:537-544` (the guard), `beo_check.py:562` (the unguarded call)
Evidence:
- `beo_check.py:537-544` wraps `read_ticket` and `read_state` in `try/except Exception`, converting a read failure into a recorded error and an empty dict. That part fails closed correctly.
- `beo_check.py:562` calls `validate_runtime_events(read_events(root, args.issue), args.issue)` outside that block.
- `beo_state.py:632` calls `json.loads(line)` per line with no exception handling and `beo_state.py:634` raises directly on a non-object line.
Contract violated:
- The checker's output contract is a JSON error record. A traceback is not that record, and a caller parsing stdout gets nothing to parse.
Plausible failure mode:
- A torn last line in `runtime-events.jsonl` (see F012) makes every `beo_check.py` invocation for that issue exit with a traceback. The issue becomes uncheckable, and the failure looks like a broken tool rather than a broken artifact.
Durable solution hypothesis:
- Move the `read_events` call inside the existing guarded block, or give it its own guard that appends the exception text to `errors`. The whole of `main` should be unable to raise.
Disconfirming check:
- `sed -n '533,564p' beo_check.py`.

### F012 [P2] `append_event` writes into the live JSONL with no temp-and-rename, so a crash mid-write leaves a torn line that permanently breaks every future reader

Severity: P2 | Confidence: high
Candidates: S3b-08-01
Source pointer: `beo_state.py:649-653` against `beo_state.py:93` (`atomic_write_json`)
Evidence:
- `atomic_write_json` (`beo_state.py:93`) uses mkstemp + fsync + `os.replace`; `beo_reservation.py:write_reservations` follows the same pattern.
- `append_event` takes the lock correctly (`beo_state.py:646`) and fsyncs (`:652-653`), but writes with `open(path, "a")` directly into the live file (`beo_state.py:649-651`). The lock prevents interleaving between processes; it does not make the write atomic against a crash or a full disk.
- `read_events` has no error handling (F011), so one torn line is terminal for the file.
Contract violated:
- The bundle has one durable-write discipline and this path does not follow it.
Plausible failure mode:
- Power loss, OOM kill, or ENOSPC between the two `handle.write` calls leaves a partial JSON line. Every subsequent `read_events` raises, and by F011 every `beo_check.py` run on that issue crashes.
Durable solution hypothesis:
- Either write the line to a temp file and append via `os.replace` of the whole file, or — cheaper and idiomatic for JSONL — have `read_events` tolerate exactly one malformed trailing line by truncating it, since a torn line can only ever be the last one under an exclusive lock. Pick one; do not do both.
Disconfirming check:
- `sed -n '639,656p' beo_state.py`.

### F013 [P2] `read_events` takes no lock while `read_state` and `append_event` both do

Severity: P2 | Confidence: high
Candidates: S3b-01-09, S3b-08-02
Source pointer: `beo_state.py:621-638` against `beo_state.py:126-133` and `beo_state.py:646`
Evidence:
- `read_state` (`beo_state.py:126-133`) acquires `state.lock` around its read.
- `append_event` (`beo_state.py:646`) acquires `runtime-events.lock` around its write.
- `read_events` (`beo_state.py:621-638`) acquires nothing. It is the only reader/writer pair member in the module that opts out.
Contract violated:
- The file has a lock and a discipline; one of its two accessors ignores both.
Plausible failure mode:
- A reader interleaves with a concurrent append and sees a partially flushed final line, raising the same uncaught `json.loads` error as F012 but without any crash having occurred — a transient, unreproducible failure.
Durable solution hypothesis:
- Wrap `read_events` in the same `_locked(base / "runtime-events.lock")` / `_unlock` pair the writer uses. Note this is a shared-lock use case; `fcntl.LOCK_SH` is the correct mode for readers if the module grows a shared variant, but `LOCK_EX` is correct and sufficient today.
Disconfirming check:
- `sed -n '621,638p' beo_state.py` — no `_locked` call appears.

### F014 [P2] `shlex.split` on a ticket-supplied command sits outside the try, so malformed quoting crashes the gate instead of failing it

Severity: P2 | Confidence: high
Candidates: S3b-02-03, S3b-02-04, S3b-06-07, S3b-08-05
Source pointer: `beo_verify.py:57`, `beo_check.py:397`
Evidence:
- `beo_verify.py:57` calls `argv = shlex.split(command)`; the `try` that guards execution does not begin until `beo_verify.py:69`.
- `shlex.split` raises `ValueError("No closing quotation")` on an unbalanced quote.
- `beo_check.py:397` has the same shape in `run_structural_check`.
- The empty-command case immediately below (`beo_verify.py:58-68`) is handled deliberately and correctly, which shows the author considered malformed input on this exact path and covered only one of the two shapes.
Contract violated:
- A gate must refuse cleanly on bad input. This one raises, which is a different exit path with a different exit code and no JSON record.
Plausible failure mode:
- A ticket with `pytest -k "foo` in `scope.verify.commands` produces a traceback rather than a recorded verification failure.
Durable solution hypothesis:
- Move `shlex.split` inside the guarded region and map `ValueError` to the same `exit_code: -1` misconfiguration result the empty-command branch already returns. The comment there names the right principle; apply it to both shapes.
Disconfirming check:
- `sed -n '55,70p' beo_verify.py`.

### F015 [P2] No subprocess call in the bundle has a timeout, and verify output is captured and then discarded

Severity: P2 | Confidence: high
Candidates: S3b-08-06, S3b-02-08
Source pointer: `beo_verify.py:69-78`, and all 16 call sites
Evidence (derived on-turn):
- `grep -nE 'subprocess\.(run|Popen|call|check_output|check_call)\(' *.py | wc -l` -> **16** call sites; `grep -n 'timeout' *.py` returns no `timeout=` argument on any of them.
- `beo_verify.py:75` passes `capture_output=True`, and the function returns only `exit_code`, `duration_ms`, `ran_at`, `worktree_path`, `command`. `proc.stdout` and `proc.stderr` are never read.
Contract violated:
- The verification record is supposed to be the audit trail for the gate. It records that a command failed and destroys the only evidence of why.
Plausible failure mode:
- A hung verify command blocks the lifecycle indefinitely with the state lock implications of F029. Separately, every verification failure is un-diagnosable from the record; the operator must re-run by hand and hope it reproduces.
Durable solution hypothesis:
- Add an explicit `timeout=` sourced from the ticket with a bounded default, and persist truncated stdout/stderr into the result dict and the runtime event. If size is the reason for discarding, truncate with an explicit marker rather than dropping.
Disconfirming check:
- `sed -n '69,80p' beo_verify.py`; the grep above.

### F016 [P2] Three incompatible repo-root conventions coexist, and the registry is loaded relative to the script file rather than the passed root

Severity: P2 | Confidence: high
Candidates: S3b-09-01, S3b-01-24, S3b-09-14
Source pointer: `beo_check.py:295`, `beo_state.py:210,218,424`, `check_skill_bundle.py:9`
Evidence (derived on-turn):
- `beo_state.py:210`, `:218`, `:424` and `beo_check.py:295` all resolve registry files as `Path(__file__).resolve().parents[1] / "registry" / ...` — the script's own location, ignoring the `root` argument threaded through every other call.
- `check_skill_bundle.py:9` sets `SCRIPT_DIR = Path(__file__).resolve().parent` and exposes no `--root` flag at all — a fourth convention among the scripts the brief calls instruments.
- `beo_io.py:45` `repo_head_sentinel(root)` relies on git walking up from `root`, a fifth resolution behaviour.
Contract violated:
- `root` is passed everywhere as if it selected the repository under inspection. For registry reads it does not: the bundle always validates against the registry sitting next to the installed script.
Plausible failure mode:
- A checkout whose `skills/beo/beo-reference/registry/` differs from the installed bundle's is validated against the installed one. The operator believes they checked the tree in front of them.
Durable solution hypothesis:
- One resolution function, used everywhere, taking `root` explicitly. If the registry is deliberately bundle-relative rather than checkout-relative, that is a design decision the code must state in one place rather than restate implicitly at four sites — and `check_skill_bundle.py` must grow the same `--root` surface as its siblings.
Disconfirming check:
- `grep -n '__file__' skills/beo/beo-reference/scripts/*.py`.

### F017 [P2] `beo_run.py` builds the ticket path from a raw, unvalidated `issue_id` and passes the same value to a subprocess

Severity: P2 | Confidence: high
Candidates: S3b-03-07, S3b-02-09, S3b-06-12, S3b-02-06
Source pointer: `beo_run.py:72`, `beo_paths.py:67`
Evidence (derived on-turn):
- `beo_paths.py:67` defines `reject_unsafe_issue_id`; `grep -n 'reject_unsafe_issue_id' *.py` shows callers at `beo_paths.py:95` and `beo_ticket.py:166-167` only. `beo_run.py` is not among them.
- `beo_run.py:72` builds `ticket_path = base / "TICKET.json"` where `base` derives from the CLI `issue_id`.
- The same unvalidated `issue_id` reaches `br` as a subprocess argv element.
- `beo_reservation.py` likewise never validates the format (S3b-02-13).
Contract violated:
- The bundle has a single issue-id safety predicate and two of its entry points do not call it. `beo_ticket.py` does, which is what makes the omission a drift rather than a design.
Plausible failure mode:
- An `issue_id` of `../../..` reads a TICKET.json outside the artifacts tree and runs its commands. This requires control of the CLI argument, so it is a consistency and robustness defect rather than a remote-input one — but the predicate exists precisely so no caller has to reason about that.
Durable solution hypothesis:
- Call `reject_unsafe_issue_id` at the top of `main` in `beo_run.py` and `beo_reservation.py`, before any path construction. Better: move the call into `artifact_dir` so no caller can skip it.
Disconfirming check:
- `grep -n 'reject_unsafe_issue_id' skills/beo/beo-reference/scripts/*.py`.

### F018 [P2] Actor-identity precedence is inverted between `beo_run.py` and every other consumer

Severity: P2 | Confidence: high
Candidates: S3b-04-15, S3b-01-04, S3b-03-16
Source pointer: `beo_run.py:48` against `beo_io.py`, `beo_check.py:92`, `beo_reservation.py:238`
Evidence (derived on-turn):
- `beo_run.py:48`: `actor = os.environ.get("BEO_ACTOR") or os.environ.get("BR_ACTOR")` — `BEO_ACTOR` wins.
- `beo_check.py:92`, `beo_check.py:216`, `beo_reservation.py:238`, `:309`, `:353` all phrase the requirement as "BR_ACTOR or BEO_ACTOR", and `beo_io.py:actor_identity()` resolves `BR_ACTOR` first.
Contract violated:
- Two identity resolutions with opposite precedence, both feeding durable records.
Plausible failure mode:
- With both variables set to different values — a CI runner exporting one and a developer shell the other — `beo_run.py` binds one identity into `approval.actor` and `execution.actor` while `beo_check.py`'s later validation resolves the other. The recorded actor is not the actor the checker believes acted.
Durable solution hypothesis:
- One `actor_identity()` in `beo_io.py`, called by every consumer including `beo_run.py`. Delete `beo_run.py:_actor`. Precedence is then defined once, whichever order is chosen.
Disconfirming check:
- `grep -n 'BR_ACTOR\|BEO_ACTOR' skills/beo/beo-reference/scripts/*.py`.

### F019 [P2] `beo_check.py:540` collapses two independent fallible reads, so a state-read failure discards a valid ticket and mislabels a crash as a check failure

Severity: P2 | Confidence: high
Candidates: S3b-02-14, S3b-07-15
Source pointer: `beo_check.py:537-544`
Evidence:
- `beo_check.py:538-539` reads the ticket and the state in one `try`. `beo_check.py:541-542` sets **both** to `{}` on any exception from either.
- The `if ticket:` at `:545` then skips every check, including the identity check that would have reported the real problem.
Contract violated:
- A checker must distinguish "the check failed" from "the checker could not run." This path reports the second as the first, and loses a successfully-read artifact in the process.
Plausible failure mode:
- `state.json` is absent for a not-yet-initialised issue. The ticket read succeeded, but it is thrown away, all checks are skipped, and the output is a single error string with no indication that nothing was actually checked.
Durable solution hypothesis:
- Two separate `try` blocks with two separate error entries, and a `checks_run` list in the output so a caller can tell an empty check set from a passing one.
Disconfirming check:
- `sed -n '536,546p' beo_check.py`.

### F020 [P2] `BEO_WORKTREE_BASE` defaults to a shared, world-writable, repo-unaware `/tmp` path read once at import time

Severity: P2 | Confidence: high
Candidates: S3b-08-03, S3b-09-12, S3b-03-17
Source pointer: `beo_worktree.py:25`, `beo_worktree.py:68`
Evidence:
- `beo_worktree.py:25`: `WORKTREE_BASE = Path(os.environ.get("BEO_WORKTREE_BASE", "/tmp/beo-worktrees"))` — module scope, evaluated at import.
- `beo_worktree.py:68` returns `WORKTREE_BASE / issue_id`. The key is the issue id alone; the repository root is not part of the path.
Contract violated:
- Two checkouts of different repositories that share an issue id share a worktree directory. Nothing in the path distinguishes them.
Plausible failure mode:
- Two beads with the same issue id in different repos collide: one run's `git worktree add` lands where the other's worktree lives, or a cleanup deletes the other's tree. On a shared machine the default path is also predictable and writable by other users.
Durable solution hypothesis:
- Key the path by a hash of the resolved repo root plus the issue id, and resolve the environment variable at call time rather than import time so tests and callers can vary it.
Disconfirming check:
- `sed -n '25p;66,70p' skills/beo/beo-reference/scripts/beo_worktree.py`.

### F021 [P2] `beo_worktree.py cleanup` force-deletes the branch ref with no merge check, and does so even when worktree removal failed (closes S3a Q4)

Severity: P2 | Confidence: high
Candidates: S3b-02-18, S3b-04-01, S3b-01-25, S3b-09-13
Source pointer: `beo_worktree.py:294`
Evidence:
- `beo_worktree.py:294` runs `["git", "branch", "-D", existing]`. `-D` is the force form; `-d` would refuse an unmerged branch.
- There is no preceding merge-status check and no guard on the outcome of the worktree removal that precedes it.
Contract violated:
- Cleanup is supposed to reclaim a resource, not discard work. `-D` on an unmerged branch discards commits.
Plausible failure mode:
- A bead is cleaned up before its work is merged — an aborted run, a cleanup issued against the wrong issue id, or a partial failure earlier in the same function. The commits survive only in the reflog, which expires, and nothing in the output says a branch was deleted unmerged.
Durable solution hypothesis:
- Use `git branch -d` and let git refuse; escalate to `-D` only behind an explicit `--force` flag the operator passes. If removal of the worktree failed, do not touch the branch at all.
Disconfirming check:
- `sed -n '288,298p' skills/beo/beo-reference/scripts/beo_worktree.py`.

### F022 [P2] `beo_worktree.py` holds no application lock around `git merge` / `worktree add` / `worktree remove` / `branch -D`

Severity: P2 | Confidence: medium
Candidates: S3b-08-04
Source pointer: `beo_worktree.py`, 9 of the bundle's 16 subprocess call sites
Evidence (derived on-turn):
- `grep -c subprocess beo_worktree.py` -> 11 mentions across 9 call sites; `grep -n '_locked\|flock' beo_worktree.py` -> no match.
- `beo_state.py` and `beo_reservation.py` both take file locks for far cheaper operations.
Contract violated:
- The module performs the bundle's most destructive operations with the least concurrency protection in it.
Plausible failure mode:
- Two beads running against one repository interleave `worktree add` and `worktree prune`/`remove`. Git's own index lock covers some of this; the sequences here are multi-command and not individually atomic, so a partially-created worktree can be pruned by the other run between two of the first run's commands.
Durable solution hypothesis:
- One repo-scoped lock file taken for the duration of each `cmd_create` / `cmd_cleanup`, matching the discipline `beo_state.py` already establishes.
Disconfirming check:
- `grep -n 'flock\|_locked' skills/beo/beo-reference/scripts/beo_worktree.py`.

### F023 [P2] `validate_path_token` skips the repo-escape containment check for any token containing a glob

Severity: P2 | Confidence: high
Candidates: S3b-02-12, S3b-09-09
Source pointer: `beo_check.py:341-345`
Evidence:
- `beo_check.py:340`: `if not has_glob(token):` guards the `(root / normalize_posix(token)).resolve().relative_to(root.resolve())` containment check.
- `reject_unsafe_path(token)` at `:336` still runs for every token, so the lexical `..` rejection applies; the resolve-based check — the one that catches symlink escapes — does not.
Contract violated:
- Two containment checks exist because the lexical one is insufficient. Glob tokens get only the insufficient one.
Plausible failure mode:
- A scope path like `vendor/*/src` where `vendor/x` is a symlink outside the repo passes containment. `reject_unsafe_path` sees nothing lexically wrong.
Durable solution hypothesis:
- Resolve and check the glob-free prefix of the token (everything before the first glob segment), which is always a concrete path. That restores the resolve-based check without needing to expand the glob.
Disconfirming check:
- `sed -n '334,348p' skills/beo/beo-reference/scripts/beo_check.py`.

### F024 [P2] `run_one_command` catches only `FileNotFoundError`, so other `OSError` subclasses escape as tracebacks

Severity: P2 | Confidence: high
Candidates: S3b-02-05
Source pointer: `beo_verify.py:79`
Evidence:
- `beo_verify.py:79`: `except FileNotFoundError: exit_code = -1`. `PermissionError`, `IsADirectoryError`, `OSError(ENOEXEC)` and `NotADirectoryError` (a bad `cwd`) are not caught.
Contract violated:
- Same class as F014: a gate raises where it should record a failure.
Plausible failure mode:
- A verify command pointing at a non-executable file, or a `cwd` that vanished, produces a traceback rather than an `exit_code: -1` result.
Durable solution hypothesis:
- Catch `OSError` — `FileNotFoundError` is a subclass, so this is a strict widening with no behaviour change for the currently-handled case.
Disconfirming check:
- `sed -n '78,82p' skills/beo/beo-reference/scripts/beo_verify.py`.

### F025 [P2] `--check review-entry` never re-validates the approval envelope, so the ticket can change between execute-entry and review-entry undetected

Severity: P2 | Confidence: high
Candidates: S3b-06-08, S3b-06-02, S3b-03-05, S3b-10-03
Source pointer: `beo_check.py:560-562`, `beo_check.py:275`, `beo_state.py:617`
Evidence:
- `beo_check.py:556-557` (`execute-entry`) calls both `validate_approval_envelope` and `validate_execute_entry`.
- `beo_check.py:560-562` (`review-entry`) calls only `validate_review` and `validate_runtime_events`; neither re-derives the approval hashes.
- `validate_approval_envelope` (`beo_check.py:275`) is the content-based staleness check: it re-derives `ticket_file_hash`, `repo_head` and `approval_projection_hash` from the current tree. `execution_entry_is_current` (`beo_state.py:617`) is the cheap sequence-based one and is the only check that runs automatically inside `locked_update_state`.
Contract violated:
- Content staleness is checked once, at execute-entry, and never again before the irreversible acceptance write.
Plausible failure mode:
- `TICKET.json` is edited after execution starts — scope widened, done criteria weakened. Review-entry passes because it never re-hashes the ticket, and `phase_sequence_id` is still current, so the sequence check agrees too.
Durable solution hypothesis:
- Call `validate_approval_envelope` from the `review-entry` branch as well. The two checks are complementary — sequence currency and content currency — and acceptance needs both.
Disconfirming check:
- `sed -n '546,556p' skills/beo/beo-reference/scripts/beo_check.py`.

### F026 [P2] Role labels (`owner`, `approved_by`, `reviewed_by`) are conventions, never identity checks — the root cause under F003 and F010

Severity: P2 | Confidence: high
Candidates: S3b-10-01
Source pointer: `beo_state.py:579-583`, `beo_run.py:130,173,221`
Evidence:
- `locked_update_state(root, issue_id, owner, updater)` takes `owner` as a caller-supplied string. `beo_state.py:582` branches on `owner == "beo-execute"` and otherwise trusts it.
- `beo_run.py` passes `"beo-validate"`, `"beo-execute"` and `"beo-review"` from one process, in one function, seconds apart.
- Nothing binds `owner` to `actor`, to a credential, or to which skill is running.
Contract violated:
- The separation-of-duties the phase model describes is enforced by a string literal the caller chooses.
Plausible failure mode:
- One process performs every role. This is not hypothetical — `beo_run.py` is exactly that process, which is why F003, F004 and F010 exist as separate findings with one shared cause.
Durable solution hypothesis:
- This is the structural question Phase B must answer before the individual fixes: either the roles are genuinely separate processes with separable evidence, or the labels should be removed and the record should stop claiming a separation that does not exist. Patching each label in turn without settling this produces a record that is precisely as false and harder to audit.
Disconfirming check:
- `grep -n 'locked_update_state(' skills/beo/beo-reference/scripts/*.py`.

### F027 [P2] `br close` runs before the state write, and the two are not atomic

Severity: P2 | Confidence: high
Candidates: S3b-04-08, S3b-06-11
Source pointer: `beo_run.py:187-192`, `beo_run.py:211-221`
Evidence:
- `beo_run.py:189` states the intent in a comment: "br close must succeed before we record closed_in_br=True in state.json."
- `beo_run.py:192` runs the subprocess; `beo_run.py:221` performs the state write afterwards.
- Exit code 3 is documented (`beo_run.py:18`) for a failed `br close`; there is no documented code for a successful close followed by a failed state write.
Contract violated:
- Two durable stores, one logical commit, no ordering recovery. The comment shows the ordering was chosen deliberately; the failure between them was not addressed.
Plausible failure mode:
- `br close` succeeds and the `locked_update_state` at `:221` raises (a lock timeout, a validation error — F001 makes this reachable for every strict-mode bead). The issue is permanently closed in `br` while `state.json` still says `executed`. Re-running is F002.
Durable solution hypothesis:
- Write the state first with a `closing` marker, then close in `br`, then clear the marker — so a crash leaves a state that names the inconsistency instead of hiding it. Or make the state write idempotent and retry it. Either way the recovery path must exist and be documented alongside exit code 3.
Disconfirming check:
- `sed -n '186,195p' skills/beo/beo-reference/scripts/beo_run.py`.

### F028 [P2] `beo_run.py`'s dirty-path check is advisory; unexpected changes print a warning and continue

Severity: P2 | Confidence: high
Candidates: S3b-09-15
Source pointer: `beo_run.py:106-109`
Evidence:
- `beo_run.py:107-109` prints "WARNING: unexpected dirty paths" and "Continuing; these are outside the bead's approved scope." to stderr, then proceeds.
- No exit, no state field, no runtime event records that the tree was dirty outside scope.
Contract violated:
- The prestate check exists to bound what the bead may touch. It reports a violation of that bound and permits it.
Plausible failure mode:
- Changes made outside the approved scope — by a concurrent process, or by the operator — are folded into an execution the record describes as scoped. The warning is on stderr and is lost in any non-interactive run.
Durable solution hypothesis:
- Refuse. If a permissive mode is genuinely needed, it should be an explicit flag and the permitted paths should be recorded in `state.json` so the acceptance record shows what was tolerated.
Disconfirming check:
- `sed -n '104,110p' skills/beo/beo-reference/scripts/beo_run.py`.

### F029 [P2] Every lock is a blocking `flock(LOCK_EX)` with no `LOCK_NB`, no timeout, and no staleness detection

Severity: P2 | Confidence: high
Candidates: S3b-04-05 (second half)
Source pointer: `beo_state.py:_locked`, `beo_reservation.py`
Evidence (derived on-turn):
- `grep -n 'flock' skills/beo/beo-reference/scripts/*.py` shows `LOCK_EX` only; no `LOCK_NB` appears anywhere.
- No `signal.alarm`, no timeout wrapper, no lock-holder pid recorded in the lock file.
Contract violated:
- A hung holder is indistinguishable from a busy one, and waits forever.
Plausible failure mode:
- A verify command with no timeout (F015) hangs while its process holds the state lock. Every other actor on that issue blocks indefinitely with no diagnostic. Note the correct half of this: `beo_state.py` and `beo_reservation.py` locks *are* process-scoped and self-release on hard process death (S3b-04-17), so this affects hangs, not crashes.
Durable solution hypothesis:
- Acquire with `LOCK_NB` in a bounded retry loop and fail with a diagnostic naming the lock file. Write the holder's pid and start time into the lock file so a stale holder can be identified rather than guessed at.
Disconfirming check:
- `grep -n 'flock\|LOCK_' skills/beo/beo-reference/scripts/*.py`.

### F030 [P2] A directory-fsync failure after `os.replace` is reported to the caller as a total write failure, though the data is already durable

Severity: P2 | Confidence: medium
Candidates: S3b-08-09, S3b-04-06
Source pointer: `beo_state.py:82` (`_fsync_dir`), `beo_reservation.py:163` (`fsync_dir`)
Evidence:
- Both `atomic_write_json` and `write_reservations` call `os.replace` and then fsync the parent directory. An exception from the directory fsync propagates.
- At that point the rename has already happened; the new content is visible to every reader.
Contract violated:
- The caller's error handling is told the write did not happen. It did.
Plausible failure mode:
- A caller that retries or rolls back on a write exception operates on a false premise. `beo_run.py` would `_die` and leave the operator believing state was unchanged when it changed.
Durable solution hypothesis:
- Catch the directory-fsync failure separately and surface it as a durability warning distinct from a write failure, since the two need opposite recovery.
Disconfirming check:
- `sed -n '93,113p' skills/beo/beo-reference/scripts/beo_state.py`.

### F031 [P2] Advisory scorers turn "no such issue" into "an issue with an empty trace"

Severity: P2 | Confidence: high
Candidates: S3b-07-05
Source pointer: `beo_score_trace.py:324`, `beo_score_context.py:252`
Evidence:
- Both catch `FileNotFoundError` and substitute an empty structure, producing a well-formed score for an issue that does not exist.
- Combined with F032 (both `main()` always return 0), there is no channel left that reports the absence.
Contract violated:
- A scorer that cannot find its input reports a score. The output is indistinguishable from a real measurement of an empty trace.
Plausible failure mode:
- A typo'd issue id yields a confident score of zero, read as a finding about the bead rather than as a missing file.
Durable solution hypothesis:
- Distinguish the two: emit an explicit `"status": "not_found"` and a non-zero exit, or let the exception propagate. Advisory does not mean the output may be wrong.
Disconfirming check:
- `sed -n '320,330p' skills/beo/beo-reference/scripts/beo_score_trace.py`.

### F032 [P2] `beo_audit.py` and `check_skill_bundle.py` cannot detect any of the four defect classes S3a found, and the brief calls them the instruments

Severity: P2 | Confidence: high
Candidates: S3b-08-07, S3b-10-09, S3b-05-05, S3b-05-04, S3b-05-08
Source pointer: `beo_audit.py:779`, `check_skill_bundle.py:151-154`
Evidence (derived on-turn):
- `beo_audit.py:779` loads exactly three registry files: `pipeline.json`, `phase-contracts.json`, `runtime-event.schema.json`. Six of the nine files in `registry/` are never loaded (S3b-05-02): `approval-envelope.json`, `harness-proposal.schema.json`, `profiles.json`, `reservation-schema.json`, `state.schema.json`, `ticket.schema.json`.
- `check_skill_bundle.py:151-154` lists eight required registries and omits `harness-proposal.schema.json` (S3b-05-03), so a deleted schema file is invisible to both instruments.
- Neither program is a JSON-Schema validator: `grep -n 'import jsonschema' skills/beo/beo-reference/scripts/*.py` returns **0** matches, and no code anywhere in scope reads a schema `pattern` key (S3b-05-04). The `safe_path` regex is therefore duplicated across schemas with no mechanism that could detect drift between the copies or between them and `beo_paths.py`'s hand-written implementation.
Contract violated:
- The instruments claim bundle-level consistency. They measure three registry files, filename presence, and skill-card length.
Plausible failure mode:
- Exactly what happened: `state.schema.json` declares `cross_check` (F001) and no instrument noticed that the writer rejects it, because no instrument loads `state.schema.json`.
Durable solution hypothesis:
- **C12 applies: this fix and the doctrine fixes it would have caught must not share a Phase B iteration.** Extend the instrument first, on its own head, and re-run it against the unfixed doctrine to demonstrate it now reports F001, F006, F007 and F010. An instrument validated only against already-fixed code has not been shown to measure anything.
Disconfirming check:
- `sed -n '779,781p' beo_audit.py`; `sed -n '151,155p' check_skill_bundle.py`; `ls skills/beo/beo-reference/registry/ | wc -l` -> 9.

### F033 [P2] `beo_audit.py`'s C6 check uses the same naive string-prefix containment it exists to police

Severity: P2 | Confidence: high
Candidates: S3b-05-01, S3b-10-07, S3b-07-08
Source pointer: `beo_audit.py:645-650`
Evidence:
- `beo_audit.py:645`: `if not isinstance(target, str) or not target.startswith("skills/beo/")`.
- `skills/beo/../../../etc/passwd` satisfies `startswith("skills/beo/")`. There is no `resolve()` and no `relative_to`.
- `beo_check.py:341-345` shows the bundle's own better pattern — resolve, then `relative_to` — which C6 does not use.
Contract violated:
- The check that enforces kernel §10 containment on proposal targets has the traversal hole S3a flagged in the schema it backstops.
Plausible failure mode:
- A harness proposal targeting a path outside the bundle passes C6 and is reported clean.
Durable solution hypothesis:
- Reuse `beo_check.validate_path_token` or the resolve-then-`relative_to` pattern. One containment implementation in the bundle, not three.
Disconfirming check:
- `sed -n '644,652p' skills/beo/beo-reference/scripts/beo_audit.py`.

### F034 [P2] `beo_audit.py` fails fast on C0 and returns a `checks_run` list of one, so a registry load failure silently truncates the audit

Severity: P2 | Confidence: medium
Candidates: S3b-05-20
Source pointer: `beo_audit.py:783`
Evidence:
- `beo_audit.py:783`: `return [Finding("C0", SEVERITY_CRITICAL, f"failed to load {name}: {exc}")], ["C0"]` — the second element is the `checks_run` list.
- Every other check is skipped, and the returned `checks_run` correctly says so — but a consumer that reads only the findings list sees one critical finding and no indication that C1-C7 never ran.
Contract violated:
- An audit that ran one check and an audit that ran eight are distinguishable only by a field a caller may not read.
Plausible failure mode:
- A CI job asserts "no critical findings beyond the known one" and treats a truncated audit as a complete one.
Durable solution hypothesis:
- Make the truncation loud in the findings themselves: emit an additional finding naming the checks that were skipped.
Disconfirming check:
- `sed -n '778,783p' skills/beo/beo-reference/scripts/beo_audit.py`.

### F035 [P2] `check_skill_bundle.py` funnels a 147-line body through one `except Exception`, collapsing many distinct findings into one message

Severity: P2 | Confidence: medium
Candidates: S3b-05-19, S3b-10-11
Source pointer: `check_skill_bundle.py`
Evidence:
- The single broad handler wraps the whole check body. It fails closed (S3b-10-11 verified this and it is correct), so this is not a fail-open defect.
- It does mean the first exception ends the check, and the remaining checks in that body never report.
Contract violated:
- Same class as F034: partial measurement presented without a marker that it was partial.
Plausible failure mode:
- One malformed skill card masks every other bundle defect until it is fixed, one round-trip at a time.
Durable solution hypothesis:
- Scope the handler to each independent check so one failure does not end the others, and record which checks completed.
Disconfirming check:
- `grep -n 'except Exception' skills/beo/beo-reference/scripts/check_skill_bundle.py`.

### F036 [P2] `beo_run.py` accepts a non-quick ticket with a stderr warning, so every strict-mode obligation is bypassed rather than refused

Severity: P2 | Confidence: high
Candidates: S3b-06-04, S3b-03-03
Source pointer: `beo_run.py:82-83`
Evidence:
- `beo_run.py:82-83` warns and proceeds when the ticket's `mode` is not `quick`.
- Strict mode's obligations — reservation evidence (F008), worktree isolation, the `cross_check` requirement (F001, F004) — live entirely on the `beo_check.py` path, which this script never enters (F003).
Contract violated:
- Mode is a contract about which gates apply. Warning and proceeding applies none of them while the record still says `mode: strict`.
Plausible failure mode:
- A strict-mode bead runs through the quick lifecycle end to end and is accepted. The state file records strict mode and none of its guarantees hold.
Durable solution hypothesis:
- `_die` on any mode other than `quick`. This one change closes S3b-06-04, S3b-03-03, and the reachability half of F008.
Disconfirming check:
- `sed -n '80,86p' skills/beo/beo-reference/scripts/beo_run.py`.

### F037 [P2] Verify commands execute while the phase is still `approved`, before the durable transition to `executing`

Severity: P2 | Confidence: high
Candidates: S3b-06-09
Source pointer: `beo_run.py:140-162` against `beo_run.py:173`
Evidence:
- The verify loop runs at `beo_run.py:140-161`; the `locked_update_state(..., "beo-execute", _start_exec)` that writes `phase = "executing"` is at `:173`.
- `beo_state.py:590` enforces "beo-execute must durably enter executing state before product mutation" — the invariant the ordering here inverts, since a verify command is an arbitrary ticket-supplied process that can mutate the tree.
Contract violated:
- The bundle states the rule explicitly in its own error message and this path runs mutation-capable commands ahead of it.
Plausible failure mode:
- A verify command that writes (a formatter, a code generator, a test that snapshots) mutates the product while the record still says `approved`. A crash there leaves a mutated tree with no `executing` record and no `execution.started_at`.
Durable solution hypothesis:
- Transition to `executing` before running any ticket-supplied command. If pre-execution verification is genuinely wanted, it needs its own phase, not the absence of one.
Disconfirming check:
- `sed -n '136,175p' skills/beo/beo-reference/scripts/beo_run.py`.

### F038 [P2] `validate_state` never ties `phase` to `approval.status`

Severity: P2 | Confidence: medium
Candidates: S3b-01-19
Source pointer: `beo_state.py:validate_state`
Evidence:
- `validate_state` checks each field against its own enum and required-set. No cross-field predicate relates `phase` to `approval.status`, or `phase` to `review.route_condition_id`.
- This is the same absence F002 exploits from the transition side.
Contract violated:
- A state object can be internally contradictory and still validate: `phase: "approved"` with `approval.status: null`, or `phase: "plan"` with `PASS_EXECUTE`.
Plausible failure mode:
- F002's false record validates cleanly precisely because of this. Fixing F002's transition guard without adding the cross-field invariant leaves the contradictory *state* representable.
Durable solution hypothesis:
- Add cross-field invariants to `validate_state`, driven by the same registry data F006 proposes to wire in. The transition guard and the state invariant are complementary: one constrains edges, the other constrains nodes.
Disconfirming check:
- `sed -n '240,330p' skills/beo/beo-reference/scripts/beo_state.py`.

### F039 [P2] `validate_state` loads exactly one enum from the schema and hardcodes the rest

Severity: P2 | Confidence: high
Candidates: S3b-03-10
Source pointer: `beo_state.py:218`, and the module-level enum constants
Evidence:
- `beo_state.py:218` loads `state.schema.json` — but only `approval.failure_category` is resolved from it dynamically.
- `PHASES`, `APPROVAL_STATUSES`, `REVIEW_VERDICTS` and the route-condition set are Python literals in the module.
Contract violated:
- The schema is the declared source of truth for exactly one of five enums. The other four can drift from it silently — and F001 is precisely that drift, in the required-field set rather than an enum.
Plausible failure mode:
- Adding a phase to `state.schema.json` has no effect on the writer, and a schema-valid state is rejected at write time with no diagnostic pointing at the mismatch.
Durable solution hypothesis:
- Derive all five from the schema at import, as `failure_category` already is. This is the same mechanism F001's durable fix needs, so the two should be designed together even though C12 keeps them off the instrument's iteration.
Disconfirming check:
- `grep -n 'PHASES\|APPROVAL_STATUSES\|REVIEW_VERDICTS' skills/beo/beo-reference/scripts/beo_state.py`.

### F040 [P2] `beo_worktree.py` silently skips the `.beads` symlink when `root` is wrong, contradicting its own docstring

Severity: P2 | Confidence: high
Candidates: S3b-09-05
Source pointer: `beo_worktree.py:83-92`
Evidence:
- `beo_worktree.py:84-89` documents the contract: "Raises on failure... an isolated .beads directory breaks the entire pipeline."
- `beo_worktree.py:91` computes `main_beads = (root / ".beads").resolve()`; when that path does not exist the function returns without linking and without raising.
Contract violated:
- The docstring states "no silent fallback" as the reason the function raises. It has one.
Plausible failure mode:
- A wrong `root` (F016 makes this reachable) yields a worktree with an isolated `.beads`. Every state write inside it goes to a directory nothing else reads, and the run appears to succeed.
Durable solution hypothesis:
- Raise when `main_beads` is absent, as the docstring says it does.
Disconfirming check:
- `sed -n '83,100p' skills/beo/beo-reference/scripts/beo_worktree.py`.

### F041 [P2] Non-atomic writes to shared, human-owned files: `TICKET.json`, `AGENTS.md`, and proposal files

Severity: P2 | Confidence: high
Candidates: S3b-04-04, S3b-04-21, S3b-04-22, S3b-10-15, S3b-09-07, S3b-03-18
Source pointer: `beo_ticket.py:299`, `beo_setup.py:100,108,114`, `beo_propose.py:194-201`, `beo_propose.py:28,33-34`
Evidence:
- `beo_ticket.py:299` writes the canonical `TICKET.json` with a bare `path.write_text` — no lock, no temp-and-rename, no fsync, in a module whose sibling `beo_state.py` does all three.
- `beo_setup.py:100`, `:108`, `:114` perform three separate `write_text` calls against the project's `AGENTS.md`, a file that may hold unrelated human content.
- `beo_propose.py:194-201` does `target.exists()` then `target.write_text` — a TOCTOU window and a non-atomic write. `beo_memory_write.py:223-229` gets this right with exclusive-create `"x"` mode (S3b-04-23), which shows the correct pattern exists in the bundle and was not applied here.
- `beo_propose.py:28`: `PROPOSAL_DIR = os.environ.get("BEO_PROPOSAL_DIR", ...)` read at import; `:34` returns `root / PROPOSAL_DIR`. When the variable holds an absolute path, `pathlib`'s `/` discards `root` entirely, and the result feeds `mkdir(parents=True)` and a write.
Contract violated:
- The bundle establishes an atomic-write discipline in `beo_state.py` and `beo_reservation.py` and abandons it for the files a human is most likely to be editing concurrently.
Plausible failure mode:
- A crash mid-`write_text` truncates `AGENTS.md` or `TICKET.json`. For `beo_propose.py`, an absolute `BEO_PROPOSAL_DIR` writes outside the repository with no containment check.
Durable solution hypothesis:
- Route all four through the existing `atomic_write_json` / a text equivalent. Reject an absolute `BEO_PROPOSAL_DIR`, or resolve-and-contain it against `root`. Resolve the env var at call time, not import time. Note that `beo_propose.py`'s `_proposal_dir` correctly handles the *relative* case (S3b-04-24 records this as clean); only the absolute case is defective.
Disconfirming check:
- `grep -n 'write_text' skills/beo/beo-reference/scripts/*.py`.

### F042 [P2] `beo_run.py` and `beo_check.py` pass different allowed-dirty-path arguments to the same function, from different trust origins

Severity: P2 | Confidence: medium
Candidates: S3b-07-07
Source pointer: `beo_run.py:106`, `beo_check.py:549`
Evidence:
- `beo_check.py` calls `validate_working_tree_prestate(root, ticket, [])` — an empty allowlist.
- `beo_run.py` computes `recorded_changed_files` from the ticket itself and compares against it (`beo_run.py:106`), then warns rather than refuses (F028).
Contract violated:
- The same prestate predicate is given a caller-derived allowlist on one path and none on the other, so the two paths disagree about what a clean tree is.
Plausible failure mode:
- A tree that `beo_check.py` would reject is accepted by `beo_run.py`, and the divergence is invisible because the two are never run against each other.
Durable solution hypothesis:
- One definition of the allowlist, derived in one place. Follows from F003's fix.
Disconfirming check:
- `grep -n 'validate_working_tree_prestate' skills/beo/beo-reference/scripts/*.py`.

### F043 [P2] `repo_head_sentinel` fails open with a sentinel string instead of raising

Severity: P2 | Confidence: medium
Candidates: S3b-03-20
Source pointer: `beo_io.py:45`
Evidence:
- `beo_io.py:45-52` returns a sentinel string when git is unavailable or the repo has no HEAD, rather than raising.
- That value is written into `approval.repo_head` (`beo_run.py:123`) and later compared by `validate_approval_envelope`.
Contract violated:
- `repo_head` binds an approval to a commit. A sentinel binds it to nothing, and compares equal to itself on re-check.
Plausible failure mode:
- In an environment without git on PATH, every approval records the same sentinel and the staleness check passes unconditionally.
Durable solution hypothesis:
- Raise. An approval that cannot name its commit is not an approval.
Disconfirming check:
- `sed -n '45,55p' skills/beo/beo-reference/scripts/beo_io.py`.

### F044 [P2] `beo_worktree.py cmd_create`'s existing-worktree fast path trusts registration without verifying checkout completeness

Severity: P2 | Confidence: medium
Candidates: S3b-04-09
Source pointer: `beo_worktree.py:162-169`
Evidence:
- The fast path accepts a live worktree registration plus a successful `git rev-parse` as proof the worktree is usable.
- Neither establishes that the checkout completed. The adjacent stale-registration recovery path (`beo_worktree.py:156-160`) is correct (S3b-04-18); only this branch is optimistic.
Contract violated:
- "Registered and resolvable" is weaker than "checked out."
Plausible failure mode:
- A previous run interrupted during `git worktree add` leaves a registered worktree with a partial tree. The next run reuses it and verifies against incomplete sources.
Durable solution hypothesis:
- Verify with `git -C <wt> status --porcelain` or a `git diff --quiet HEAD` before taking the fast path, and fall through to recreation on failure.
Disconfirming check:
- `sed -n '154,172p' skills/beo/beo-reference/scripts/beo_worktree.py`.

### F045 [P2] `beo_audit.py` exits 1 on any critical finding while the manifest classifies it as advisory

Severity: P2 | Confidence: high
Candidates: S3b-10-10
Source pointer: `beo_audit.py:833`
Evidence:
- `beo_audit.py:833`: `return 1 if any(f.severity == SEVERITY_CRITICAL for f in findings) else 0`.
- `command-manifest.md` classifies the script as "Audit... (advisory)".
Contract violated:
- A gate-shaped exit code on a nominally advisory tool. A caller wiring it into CI on the strength of the manifest gets a blocking gate; a caller reading the exit code as a gate is contradicted by the manifest.
Plausible failure mode:
- Either the advisory label or the exit code is wrong, and both are load-bearing for different readers. This is the concrete instance of S3b-10-19's advisory-vs-gate confusion.
Durable solution hypothesis:
- Decide which it is and make the manifest and the exit code agree. If advisory, always exit 0 and report severity in the JSON.
Disconfirming check:
- `sed -n '830,835p' skills/beo/beo-reference/scripts/beo_audit.py`.

### F046 [P3] Both scorers document exit codes "0, 1" and `main()` can only return 0

Severity: P3 | Confidence: high
Candidates: S3b-07-10, S3b-05-15
Source pointer: `beo_score_trace.py:314,335`, `beo_score_context.py`
Evidence: `beo_score_trace.py:314` defines `main() -> int` and `:335` is its only `return`, returning 0. `command-manifest.md` documents both scripts as exiting "0, 1". Combined with F031, an advisory scorer has no failure channel at all.
Durable solution hypothesis: either implement the documented failure exit (which F031 needs anyway) or correct the manifest to "0". Do not leave both standing.
Disconfirming check: `grep -n 'return [01]' skills/beo/beo-reference/scripts/beo_score_trace.py`.

### F047 [P3] Dead functions: `beo_ticket.write_ticket` and `beo_io.compact_text`

Severity: P3 | Confidence: high
Candidates: S3b-05-13, S3b-05-14, S3b-07-12, S3b-10-17
Source pointer: `beo_ticket.py:290`, `beo_io.py:21`
Evidence (derived on-turn): `grep -rn 'write_ticket\|compact_text' skills/beo/beo-reference/scripts/*.py` shows the two definitions and no call sites in the 17-file bundle.
Note: `write_ticket` is also the non-atomic writer named in F041. Deleting it closes both, and is the pre-launch-correct move unless a caller outside the bundle exists.
Durable solution hypothesis: delete both. If `write_ticket` is intended as the future canonical writer, it must be fixed per F041 before it acquires a caller, not after.
Disconfirming check: the grep above, extended to the whole repo.

### F048 [P3] `beo_verify.py:32` defines `HELPER_VERSION` and never emits it

Severity: P3 | Confidence: high
Candidates: S3b-07-13
Source pointer: `beo_verify.py:32`
Evidence: `HELPER_VERSION = "beo-verify/v1"` at `:32`; `grep -n 'HELPER_VERSION' beo_verify.py` shows the definition and nothing else. No result dict or runtime event carries it.
Durable solution hypothesis: emit it in the verification result so a record can be attributed to a helper version, or delete it. A version constant that never reaches a record cannot version anything.
Disconfirming check: `grep -n 'HELPER_VERSION' skills/beo/beo-reference/scripts/*.py`.

### F049 [P3] `beo_reservation.parse_iso`'s fallback branch is unreachable given the upstream regex guard, and `beo_audit.get_check_ids`'s fail-open is currently dead

Severity: P3 | Confidence: medium
Candidates: S3b-07-06, S3b-04-11
Source pointer: `beo_reservation.py:32`, `beo_audit.py:40`
Evidence: `parse_iso` has a fallback path for a timestamp shape the upstream regex validation already rejects. `beo_audit.get_check_ids` has `except Exception: return frozenset()` — a fail-open that no current call path can reach.
Durable solution hypothesis: delete both. The `get_check_ids` handler is latent rather than harmless: if a future caller reaches it, an empty check-id set silently disables checks — the F034 truncation class, without the finding.
Disconfirming check: `sed -n '32,48p' beo_reservation.py`; `sed -n '40,50p' beo_audit.py`.

### F050 [P3] `execution.interventions` and `execution.trace_tier` are validated and never populated or read (closes S3a Q5)

Severity: P3 | Confidence: high
Candidates: S3b-01-20, S3b-01-23, S3b-03-11
Source pointer: `beo_state.py` (`validate_state`)
Evidence: both fields are structurally validated; `grep -n 'interventions\|trace_tier' skills/beo/beo-reference/scripts/*.py` shows no writer and no decision that reads either.
Durable solution hypothesis: this is the F006/F007 class one level down — a declared field with no producer and no consumer. Wire or delete, and prefer delete pre-launch.
Disconfirming check: the grep above.

### F051 [P3] `beo_memory_write.py:45` builds a filename from local-timezone `date.today()` against a UTC-everywhere codebase

Severity: P3 | Confidence: high
Candidates: S3b-04-14, S3b-03-19
Source pointer: `beo_memory_write.py:45`
Evidence: `beo_memory_write.py:45` uses `date.today().isoformat()` in the filename. Every other timestamp in scope goes through `now()`, which is UTC. `beo_verify.py` correctly uses `time.monotonic()` for durations (S3b-04-20).
Plausible failure mode: two notes written minutes apart across local midnight, or from two machines in different zones, sort and group wrongly. Note this is naming only — no code in scope sorts or tie-breaks on a timestamp field (S3b-04-16 verified this), so the blast radius is the filename.
Durable solution hypothesis: use the same UTC `now()` the rest of the bundle uses.
Disconfirming check: `sed -n '43,47p' skills/beo/beo-reference/scripts/beo_memory_write.py`.

### F052 [P3] Reservation ids are 8 hex chars of `sha1(os.urandom(8))` with no collision check

Severity: P3 | Confidence: high
Candidates: S3b-01-14, S3b-03-21
Source pointer: `beo_reservation.py:265`
Evidence: 8 hex chars is 32 bits. The birthday bound puts a 50% collision probability near 77,000 reservations; at a few thousand the probability is already percent-scale.
Durable solution hypothesis: check the generated id against existing records inside the lock the writer already holds and regenerate on collision — the lock makes this free. Widening to 16 chars alone would reduce the probability without removing the class.
Disconfirming check: `sed -n '262,270p' skills/beo/beo-reference/scripts/beo_reservation.py`.

### F053 [P3] `check_skill_bundle.py`'s comment says 500 lines and the code enforces 250

Severity: P3 | Confidence: high
Candidates: S3b-10-12
Source pointer: `check_skill_bundle.py:111` vs `:124-125`
Evidence: `:111` reads `# Check length limit (500 non-frontmatter lines)`; `:124` is `if len(non_frontmatter_lines) > 250:` and `:125`'s message says 250.
Durable solution hypothesis: correct the comment. The code and the error message agree with each other, so the comment is the wrong one.
Disconfirming check: `sed -n '110,126p' skills/beo/beo-reference/scripts/check_skill_bundle.py`.

### F054 [P3] Manifest and documentation drift: undocumented flags, wrong vocabulary, inapplicable instructions, and a naming inconsistency in the CLI surfaces

Severity: P3 | Confidence: high
Candidates: S3b-07-11, S3b-10-13, S3b-10-20, S3b-10-21, S3b-07-09, S3b-10-08, S3b-07-14
Source pointer: `command-manifest.md`, `beo-setup/SKILL.md`, `context-budget.md`, `beo_audit.py` (C5)
Evidence:
- `beo_propose.py --dry-run` exists and is undocumented in the manifest (S3b-07-11); S3b-10-13 tabulates further drift between the manifest and the actual argparse surfaces.
- `beo-setup/SKILL.md` uses mode vocabulary that does not match `beo_setup.py`'s CLI flags (S3b-10-21).
- `context-budget.md` instructs readers to "use `--help` instead" for five scripts that are library-only and have no CLI (S3b-10-20).
- `beo_audit.py`'s C5 manifest-consistency check compares script filenames only, never documented flags or exit codes (S3b-07-09, S3b-10-08) — which is exactly why none of the above is detected. This is F032's class: the instrument measures presence, not accuracy.
- An unused parameter and an unused import remain in scope (S3b-07-14).
Durable solution hypothesis: fix the documentation, then extend C5 to compare documented flags and exit codes against the parsers — subject to C12, on a separate iteration from the doc fixes it would have caught.
Disconfirming check: `grep -n 'dry-run' skills/beo/beo-reference/scripts/beo_propose.py`; `sed -n '/C5/,/^def /p' skills/beo/beo-reference/scripts/beo_audit.py`.

### F055 [P3] Duplicated scorer logic, and orphaned directories with no producer or no consumer

Severity: P3 | Confidence: high
Candidates: S3b-10-18, S3b-05-16, S3b-10-14, S3b-05-17, S3b-10-16, S3b-05-06, S3b-05-07, S3b-05-09, S3b-01-08, S3b-01-07
Source pointer: `beo_score_context.py` / `beo_score_trace.py`; `skills/beo/beo-author/proposals/pending/`; `.beads/artifacts/<id>/logs/`
Evidence:
- The two scorers share copy-pasted logic (S3b-10-18) — the same duplication class as F016's five root conventions.
- `beo_propose.py` writes to `beo-author/proposals/pending/` and nothing in the bundle reads it (S3b-05-16, S3b-10-14).
- Nothing writes `.beads/artifacts/<id>/logs/` (S3b-05-17, S3b-10-16), which is the natural home for the verify output F015 discards.
- No script reads a pipeline transition's `to` field (S3b-05-06) — the same declared-but-unread class as F006.
- The `caller` role appears in 5 transitions across 2 skills, not "five skills" as framed, and its resolution semantics are undefined in code (S3b-05-07).
- The harness-proposal `target` field has no code-side enforcement point in scope beyond F033's naive check (S3b-05-09).
- `approval_projection_hash` relies on `stable_json`'s sorting for key-order independence and never asserts it (S3b-01-08); `_grant_pass_execute` compares fields against values the same process just computed (S3b-01-07) — both are F003 and F026 restated at field granularity.
Durable solution hypothesis: pre-launch, delete the orphaned surfaces rather than wiring them. The exception is `logs/`, which F015 gives a reason to populate.
Disconfirming check: `grep -rn 'proposals/pending\|artifacts.*logs' skills/beo/beo-reference/scripts/*.py`.

### F056 [P2] Ticket-supplied commands from `structural_check`, `verify` and `behaviour_gate` are executed with zero content review, and `structural_check` runs pre-approval

Severity: P2 | Confidence: high
Candidates: S3b-02-01, S3b-02-02, S3b-09-04, S3b-02-07
Source pointer: `beo_check.py:397`, `beo_verify.py:50-78`
Evidence:
- `beo_check.py:397` tokenizes `scope.structural_check.command` with `shlex.split` and executes it as part of `--check validate` — that is, before approval is granted.
- `beo_verify.py:50-53`'s docstring states the design explicitly: "The command is tokenized with shlex and executed without a shell so that metacharacters in a verify command cannot trigger arbitrary execution. TICKET.json is human-approved, but the harness should not rely on the author to sanitize their own commands."
- Argv tokenization semantics are therefore settled (this closes S3a Q7, S3b-02-07): `shell=False` with `shlex.split`, so shell metacharacters are inert — `grep -n 'shell=' *.py` shows only `shell=False` at `beo_check.py:401` and `beo_verify.py:73`, and **no `shell=True` anywhere in scope** (derived on-turn).
- What remains is not injection but arbitrary execution by design: the argv itself is whatever the ticket says, so `rm -rf` needs no metacharacters.
Contract violated:
- The docstring's stated threat model is metacharacter injection, and the mitigation is correct for that threat. The unstated and larger exposure is that an unreviewed `TICKET.json` is an arbitrary-command file, and `structural_check` runs one before the human gate that is supposed to approve it.
Plausible failure mode:
- A ticket authored or modified by anything other than the approving human executes its commands during `--check validate`, before approval exists to be withheld.
Durable solution hypothesis:
- Establish when `TICKET.json` becomes trusted and run no ticket-supplied command before that point. If `structural_check` must run pre-approval, it needs a constrained command vocabulary rather than free argv. This is a design question for Phase B, not a patch.
Disconfirming check:
- `sed -n '395,405p' skills/beo/beo-reference/scripts/beo_check.py`; `grep -n 'shell=' skills/beo/beo-reference/scripts/*.py`.

### F057 [P2] Best-effort event-append handlers swallow exactly the failures that would reveal a broken audit trail

Severity: P2 | Confidence: high
Candidates: S3b-08-10
Source pointer: `beo_verify.py`, `beo_score_trace.py`, `beo_score_context.py`
Evidence:
- Each wraps its `append_event` call in a broad handler and continues on failure.
- The exceptions being swallowed are the ones F012 and F013 produce: a torn line, a lock failure, a validation rejection.
Contract violated:
- The runtime event log is the audit trail. A silent write failure means the trail has a hole that nothing reports.
Plausible failure mode:
- `runtime-events.jsonl` is corrupted (F012). Every subsequent `append_event` raises inside `validate_event_schema` or the write, each is swallowed, and verification appears to run normally while recording nothing.
Durable solution hypothesis:
- Best-effort is defensible for an advisory scorer and not for `beo_verify.py`, whose events are gate evidence. At minimum, record the swallow — a counter in the result, or a stderr line that names the exception — so a hole in the trail is visible.
Disconfirming check:
- `grep -n -B2 -A4 'append_event' skills/beo/beo-reference/scripts/beo_verify.py`.

## Candidate Reconciliation

182 candidate ids were filed across ten scout blocks (derived on-turn: `S3b-NN-MM` regex over the ten indexed ranges in `S3B-CANDIDATES.md`, contiguous `01..N` per scout, no gaps). All 182 are accounted for: **161** are cited by a finding above, and the **21** below are reconciled here. Both counts were derived on this turn by an `S3b-NN-MM` regex over this file, truncated at this heading for the first and confined to this section for the second. The regex matches 22 ids in this section, not 21: the extra is `S3b-10-02`, which appears here only as the referent inside `S3b-10-04`'s parenthetical and is itself cited by F010 above.

**Reconciled as scout-verified negative results (checked and found correct):** S3b-01-10 (`locked_update_state`'s read-modify-write is entirely inside the lock, both modules), S3b-01-11 (`atomic_write_json` is same-directory mkstemp + `os.replace` + parent fsync), S3b-01-12 (lock files never unlinked while held; no flock-unlink race), S3b-01-13 (no wholesale directory deletion of `.beads/artifacts/<id>/`), S3b-01-18 (`phase_sequence_id` cannot go backwards, skip, or collide under `locked_update_state`), S3b-04-13 (the majority of the 28 `except Exception` sites fail closed or are explicitly advisory), S3b-04-19 (`run_one_command` correctly converts a worktree-disappeared TOCTOU into a clean failure), S3b-05-10 / S3b-05-11 (`_safe_file_hash` and `validate_path_token` both resolve-then-check soundly — F023 is the glob carve-out, not the whole predicate), S3b-05-12 (`beo_worktree.py`'s issue_id handling uses an allowlist, not a denylist), S3b-05-18 (script-name-level manifest is in sync — F054 is about flags and exit codes, not names), S3b-09-08 (the containment checks resolve-then-compare correctly).

**Reconciled as duplicate statements of a cited candidate:** S3b-02-15 (the full accounting of all 28 `except Exception` sites, whose defective members are cited individually), S3b-03-13 (`pipeline.json`'s transitions encode owner routing, not phase legality — the premise of F002 and F038), S3b-04-03 (`repo_head_sentinel` is resilient to which `root` is passed, but the two call sites derive `root` differently — the F016 divergence), S3b-07-03 (`beo_run.py` bypasses ticket-conformance validation when granting `PASS_EXECUTE` — F003), S3b-10-04 (the grep evidence supporting S3b-10-02 — F010).

**Reconciled as the Q1 reading this report overrules (see Prior Round Guard):** S3b-02-16, S3b-03-14, S3b-04-02, S3b-09-10. Each asserts the doctrine's "pre-transition" wording is wrong. `registry/approval-envelope.json:89` does not support that; the code and the doctrine agree. Recorded here rather than dropped, because four scouts reached it and a future round will reach it again if the reasoning is not on the record.

## Verification Queue

Ordered by what a receive pass should check first. Each entry is a read-only check; none applies a fix.

1. **F001** — `grep -n cross_check skills/beo/beo-reference/scripts/beo_state.py` returns nothing; `sed -n '496,509p' beo_check.py` shows the requirement; the schema declares the field. Three sources, one contradiction.
2. **F002** — `sed -n '582,601p' beo_state.py` shows the guard exists only under `if owner == "beo-execute":`; `sed -n '114,130p' beo_run.py` shows `_grant_pass_execute` applied as `beo-validate` without touching `review`.
3. **F003 / F004 / F005 / F036** — `grep -n 'beo_check\|validate_identity\|validate_plan\|run_structural_check\|validate_review\|validate_containment' beo_run.py` returns no match. One command settles all four.
4. **F006 / F007** — `grep -rl 'expected_receiver_phase_after_condition\|reservation_release_on' skills/beo/beo-reference/scripts/` returns no files.
5. **F010** — `grep -n reviewed_by skills/beo/beo-reference/scripts/*.py` returns four sites, none a writer.
6. **F009** — `sed -n '218,226p' beo_verify.py` shows `"ok": summary["fail"] == 0`.
7. **F011 / F012 / F013** — `sed -n '533,564p' beo_check.py` and `sed -n '621,656p' beo_state.py` together.
8. **F032** — `sed -n '779,781p' beo_audit.py` (three registries loaded), `sed -n '151,155p' check_skill_bundle.py` (eight of nine listed), `ls skills/beo/beo-reference/registry/ | wc -l` (nine).
9. **The three rejected candidates** — re-check them before any Phase B work builds on a scout claim: `grep -n '_result_passed' skills/beo/beo-reference/scripts/*.py` (no match, rejects S3b-06-06), `sed -n '495p' beo_state.py` (rejects S3b-01-16), `sed -n '126,133p' beo_state.py` (rejects the first half of S3b-04-05).
10. **Everything else** — each finding above carries its own Disconfirming check line.

## Coverage And Derivation

Every number in this report was derived on the turn it was written. The commands:

- **Scope:** `git ls-files skills/beo/beo-reference/scripts/` -> 17 tracked Python files, 5968 lines. Head `038dc27b50859cb30542b91683688a1f52ce5d66`, branch `main`, stash 0.
- **Findings:** 57 (10 P1 / 37 P2 / 10 P3), derived by `grep -oE '^### F[0-9]{3} \[P[123]\]' | sort | uniq -c` over this file.
- **Candidate ids:** 182, from a `S3b-NN-MM` regex applied to each of the ten indexed block ranges in `S3B-CANDIDATES.md`. Contiguous `01..N` per scout: 08→10, 05→20, 02→19, 09→15, 06→12, 04→24, 01→25, 07→15, 03→21, 10→21.
- **Reconciliation, both directions, derived on this turn.** Against the ids cited anywhere in this report: `comm -13` -> **0** (no id is cited that no scout filed) and `comm -23` -> **0** (every filed id is accounted for). Against the narrower set cited inside a finding body only — the report truncated at the `## Candidate Reconciliation` heading — **161** ids are cited by a finding and **21** are not; those 21 are the ones named and dispositioned individually in Candidate Reconciliation. An earlier draft of this line said 26; that number was carried, not derived, and is corrected here.
- **Subprocess call sites:** `grep -nE 'subprocess\.(run|Popen|call|check_output|check_call)\(' *.py | wc -l` -> **16** (`beo_check.py` 3, `beo_io.py` 2, `beo_run.py` 1, `beo_verify.py` 1, `beo_worktree.py` 9). The brief's 23 is `grep -n 'subprocess' *.py | wc -l`, a line-match count.
- **Broad handlers:** `grep -n 'except Exception' *.py | wc -l` -> **28**, matching the brief.
- **Shell usage:** `grep -n 'shell=' *.py` -> `shell=False` at `beo_check.py:401` and `beo_verify.py:73`, plus two docstring mentions. **No `shell=True` anywhere in scope.**
- **Schema validation library:** `grep -n 'import jsonschema' *.py` -> **0**. Neither instrument validates against a JSON Schema (F032).
- **Registry files:** `ls skills/beo/beo-reference/registry/ | wc -l` -> **9**. `beo_audit.py:779` loads 3; `check_skill_bundle.py:151-154` lists 8.
- **Block index:** the ten block ranges were re-derived by exact content match of each scout's transcript against `S3B-CANDIDATES.md` (`assert s.count(block) == 1`, then `s.index`), which also proves each stored block is byte-identical to its source. Ranges: 08 33-255, 05 259-458, 02 462-691, 09 695-866, 06 870-1145, 04 1149-1323, 01 1327-1497, 07 1501-1759, 03 1763-1983, 10 1987-2212.

**Consolidation method, disclosed.** Each of the ten blocks was read from `S3B-CANDIDATES.md` on disk during this consolidation, in bounded passes against the index above, rather than from a map held in context. Every source pointer cited in a finding was additionally read from the file it names on this turn; where the file contradicted the scout, the scout is overruled and the contradiction is recorded (three cases, in Candidates Rejected On Source). This is the explicit correction to the S3a round, where placeholder pointers reached a published report.

**Pointer verification, mechanical.** A first draft of this report located pointers by symbol grep rather than by exact line, and seventeen of them named a line adjacent to the code they described (`beo_state.py:583` for `if owner == "beo-execute":`, which is `:582`; `beo_check.py:556` for the unguarded `validate_runtime_events(read_events(...))` call, which is `:562`; `beo_verify.py:74` for `capture_output=True`, which is `:75`; and fourteen others of the same shape). All seventeen were corrected against the source before this report was final. Every load-bearing pointer was then re-checked mechanically: a script asserting an expected substring on the exact cited line of the exact cited file reported **88 pointers checked, 0 failures**. The seventeen corrections changed no finding's claim, severity, or reasoning — only the line number the reader is sent to — and the class is recorded here because an unverified pointer is the S3a defect this round exists to not repeat.

**Scout custody, disclosed.** Ten scouts, `Explore` kind, model `sonnet`, one batch. `Explore` retains `Bash`, so the scouts' read-only status is enforced by charter and by the coordinator's own tree comparison, not by the tool list. The post-batch sweep: marker `2026-09-06T12:20:34Z`; HEAD unchanged at `038dc27b`; stash 0; `git diff --stat -- skills/beo` empty; a repo-wide `-newer` sweep with `__pycache__` deliberately included (a new `.pyc` is the only positive evidence a scout executed a script) returned exactly two files, both coordinator writes — `S3B-BRIEF.md` and `S3B-CANDIDATES.md`. A second sweep, run after this report was written and derived on that turn — `find . -path ./.git -prune -o -newer <marker> -type f -print` — returned **3** files: those two plus this report itself, which is the only workspace artifact `ultra-review/SKILL.md:52` permits the coordinator to create. The marker timestamp above is the marker file's own mtime read as UTC (`TZ=UTC stat -f '%Sm'`); an earlier draft of this line printed `2026-09-06T19:20:34Z`, which was the local (+07:00) clock with a `Z` appended and therefore a false UTC label. The sweep itself is `-newer <marker file>`, mtime-based, so the window it measured was correct and only the printed label was wrong; it is corrected here rather than silently. All 17 `.pyc` files date to Sep 4, two days before the marker. The sweep covers the repository only.

**Coverage gaps, named.** The directives asked for a full trace of `beo_setup.py` and `beo_memory_write.py`; both are covered only by the incidental findings F041 and F051, because no scout took them as a primary assignment. `beo_paths.py`'s matcher was settled (Q6) but its interaction with `profiles.json`'s `protected_path_defaults` at scale was not traced. No scout executed any script, so every behavioural claim in this report is derived from reading, not from running.

## Strongest Reason Not To Merge Yet

**F001 and F002 together mean the bundle cannot record a true accepted state, and can record a false one.**

F001: a strict-mode bead cannot be accepted at all, because the field the gate requires is the field the writer rejects. The gate is not strict — it is unsatisfiable, which is a different and worse thing, since the only way past it is to stop using strict mode or to edit `state.json` outside the writer that holds the lock.

F002: re-running `beo_run.py` against a bead that is already closed writes `phase=approved` on top of a standing `verdict_accept`, durably, before the run dies on a later guard. The record on disk then asserts two contradictory things about the same bead, and `validate_state` accepts it because it checks set membership, not transition legality (F038).

Behind both sits F026: the roles the record names — `beo-validate`, `beo-execute`, `beo-review` — are strings the caller chooses, and `beo_run.py` chooses all three in one function within seconds. F003, F004, F005 and F010 are that same fact seen from four angles: an approval nothing validated, an acceptance nothing reviewed, a verification with nothing to verify, and a reviewer name no reviewer wrote.

That is the merge blocker: not that individual checks are missing, but that **the durable record makes claims the code cannot support, and one of those claims (F010) is false in every record the bundle has ever written.** Patching the checks one at a time without settling F026 first would leave the record exactly as false and considerably harder to audit.

**C12 applies to the remediation, not to this report.** `beo_audit.py` and `check_skill_bundle.py` (F032, F033, F034, F045, and C5 in F054) are instruments over the doctrine the other findings are about. They must not be fixed in the same Phase B iteration as the doctrine they measure: extend the instrument on its own head and re-run it against the *unfixed* doctrine to demonstrate it now reports F001, F006, F007 and F010. An instrument validated only against already-fixed code has not been shown to measure anything.

## Next Receive Prompt

The mandated sentence, reproduced verbatim:

> Use $ultra-review-receive to verify docs/ultrareview/26-09-06-s3b-beo-scripts-round-1.md and implement confirmed owner-clean fixes.

**This sentence is not an authorization.** It is the closing line the ultra-review skill mandates and generates (`create_ultra_review_report.py:102`). In this campaign `ultra-review-receive` runs in verification-only mode and applies no fix: Phase A writes files, not gates. No delivery, merge, push or deploy is authorized by this report. Whether Phase B opens — and whether any fix above is applied — is the Human's decision, taken after Phase A has ranked the confirmed findings across all slices.
