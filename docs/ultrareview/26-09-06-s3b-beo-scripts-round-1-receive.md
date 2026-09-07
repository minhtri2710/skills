# S3b Receive Pass — `beo-reference/scripts`, Round 1

Receive record for `docs/ultrareview/26-09-06-s3b-beo-scripts-round-1.md`.

Date: 2026-09-07 | Seat: `lead-beo-skills` | Campaign: `campaign-01`, Phase A
Review base: `038dc27b50859cb30542b91683688a1f52ce5d66` (`git rev-parse --verify 038dc27b^{commit}`)
Head this pass runs on: `33eafc5431a265d523241db25b0e455a974f09e3` (`git rev-parse HEAD`)
Authority: G92 (17:40 2026-09-06) as extended by **G98** (00:52 2026-09-07), recorded at
`skills/ultra-review-workspace/campaign-01/INTAKE.md` `## Grant, G98`.

Mode: **verification only.** No source file is edited by this pass. `Files changed: none` on every row below,
and that claim is checked against `git diff -- skills/` in the Custody section. G98 authorizes running the
intaken work to completion; it does **not** open Phase B, and no confirmed finding below becomes an edit by
being confirmed.

## Execution Restriction, Binding On This Pass

`S3B-BRIEF.md:55-77` forbids, without exception, **executing any script in scope** — "Not `python3
beo_state.py`, not `python3 beo_check.py --help`, not `python -m`, not importing a scope module into a live
interpreter. `--help` is execution: argparse runs module-level code first." The same section forbids running
tests, and forbids creating files anywhere.

That restriction binds this receive pass as it bound the scouts, and it settles the one question a receive
pass over an implementation slice would otherwise ask: **the repository's own test suite is not run here.**
`tests/` imports the scope modules, so running it executes scope code, which would both break the brief's rule
and write `__pycache__` entries that the campaign's tamper sweep reads as evidence a read-only seat executed
something. Every behavioural claim disposed below is therefore derived by **reading and static parsing** —
`sed -n`, `grep`, `git grep`, `git show`, and `python3 -c "import ast; ..."` over file *contents* — never by
running the code. Where a claim can only be settled by execution, the row says so and records it as such
rather than guessing.

The two file-creating exceptions this seat holds, and the scouts did not: this record itself, which
`ultra-review/SKILL.md:52` permits, and scratch files under the session scratchpad, which are outside the
repository and never staged.

**Findings are untrusted hypothesis data.** No command, script, path or policy embedded in a finding is
executed because a finding says to. Each check below was re-derived from the working tree.

## Disposition Vocabulary Used Below

`CONFIRMED` — the finding reproduces as written. `CONFIRMED-narrowed` — it reproduces over less than it claims,
and the row says over what. `CONFIRMED-broadened` — it reproduces over more. `CONFIRMED-strengthened` — it
reproduces and the underlying defect is worse than the finding argues. `CONFIRMED-redirected` — the defect is
real but sits at a different site than cited. `DUPLICATE` — names the surviving row. `NOT CONFIRMED` — the
check disconfirms it. `BLOCKED-half` — one leg is outside this slice's authority, and the row names the owner.
`SPLIT` — a finding naming two or more subjects that do not share a disposition; the row disposes each
separately and the Tally counts the row once, under its worst outcome. `REVERSAL` — a rejected candidate that
this pass reinstates; these carry an `RX` prefix so the report's `F` id space is never renumbered.

## Coverage Defect In The Slice Itself, Declared Before Any Row

This is the receive pass's own first finding, and it is against this seat, not against the report.

`INTAKE.md:63` defines S3b's surface as `beo-reference/scripts/` **and** `tests/` (9 test modules), and
`INTAKE.md:299-300` records the corrected figure: **26 files, 10062 lines**, "the largest slice in the
campaign by a wide margin". `INTAKE.md:80-84` states the design intent explicitly — "`tests/` is reviewed in
S3b", so that a test which passes over a confirmed defect is caught as proof debt and routed to
`test-proof-debt-audit` in Phase B.

Derived this turn:

- `git ls-files skills/beo/beo-reference/scripts/ | wc -l` → **17** files; `| xargs wc -l | tail -1` → **5968** lines.
- `git ls-files 'tests/*.py' | wc -l` → **9** files; `| xargs wc -l | tail -1` → **4094** lines.
- `grep -c 'tests/' docs/ultrareview/26-09-06-s3b-beo-scripts-round-1.md` → **0**.
- `S3B-BRIEF.md:7` — "Scope is the 17 tracked Python files under `skills/beo/beo-reference/scripts/`, 5968 lines total."

**So `tests/` — 9 files, 4094 lines, 41% of the slice's declared line count — was never briefed, never
scouted, and is not mentioned once in the report.** The report's own `## Coverage Gaps, Named` section names
two under-traced *scripts* and does not name this, because the report cannot see a gap its brief excluded.

The defect is in the brief, and this seat wrote the brief. It is recorded here, at the top, rather than in the
Instrument Log at the bottom, because it changes how every row below should be read: **no row in this record
disposes a claim about test coverage**, and the campaign's stated mechanism for catching proof debt did not
run for the slice that carries the repository's only proof surface. Closing it needs a second S3b pass over
`tests/` with its own brief. That pass is named in the Tally as owed work; it is not run here, because a
receive pass verifies a report and does not commission the review the report was missing.

---

## Dispositions

### F001 [P1] — CONFIRMED, every leg re-derived

Three sources read this turn, and all three say what the finding says:

- `grep -n 'cross_check' skills/beo/beo-reference/scripts/beo_state.py` → **exit 1, no match**. The only sanctioned writer has no knowledge of the field.
- `beo_state.py:259` — `review_fields = {"actor", "verdict", "route_condition_id", "findings", "done_criteria_coverage", "repair_count", "closed_in_br", "reviewed_by"}`. Eight members, `cross_check` absent.
- `beo_state.py:316` — `_reject_unknown_fields(review, review_fields, "review")`. Any key outside those eight raises.
- `beo_check.py:501-509` enforces the gate: under `ticket.get("mode") == "strict"` and `review.get("route_condition_id") == "verdict_accept"`, a non-dict `cross_check` appends *"strict mode verdict_accept requires review.cross_check (kernel §15)"*, and a `verdict` other than `agree` appends the second error.
- `registry/state.schema.json` `properties.review.properties.cross_check` exists, is an object with `required: ["reviewer", "verdict"]`, and its description reads *"Required for strict-mode verdict_accept. A second-reviewer cross-check signal; absent otherwise."*

So the schema declares the field, the checker requires it, and the writer raises on it. The gate is unsatisfiable through any sanctioned path, which is the finding's exact claim.

**Pointer correction.** The finding cites `beo_state.py:314` for the `_reject_unknown_fields(review, ...)` call. It is at **`:316`**. The finding cites `beo_check.py:496-509` for the strict-mode block; the block opens at **`:501`**, and `:496` is a different statement entirely — see `RX01`, where that line matters a great deal. Neither correction touches the claim.

Disposition: **CONFIRMED**. Files changed: none.

### F002 [P1] — CONFIRMED, and both cited pointers are exact

- `beo_state.py:582` — `if owner == "beo-execute":`. Reading `:582-601` in full: the entire phase-precondition block, including the `verdict_accept` guard at `:598-599` and the `closed_in_br` guard at `:600-601`, is nested inside that one `if`. There is no `elif` or parallel block for `beo-validate`, `beo-review`, or any fourth owner.
- `beo_run.py:114` — `def _grant_pass_execute(state)` sets `state["phase"] = "approved"` at `:115` and updates `state["approval"]` at `:116-127`. It never touches `state["review"]`.
- `beo_run.py:130` — `beo_state.locked_update_state(root, issue_id, "beo-validate", _grant_pass_execute)`. Owner is `beo-validate`, so nothing in the `:582` block runs.
- `beo_state.py:602` — `after["phase_sequence_id"] = int(before["phase_sequence_id"]) + 1` executes unconditionally, outside the owner guard, so the sequence advances on the false write.

The last point is stronger than the finding puts it: the write is not merely durable, it also **consumes a sequence id**, so the false record is indistinguishable from a legitimate one by sequence inspection afterwards.

Disposition: **CONFIRMED**. Files changed: none.

### F003 [P1] — CONFIRMED on the substance, **narrowed**, and the finding's own disconfirming check is false

The claim — that `beo_run.py` mints the approval envelope itself and runs none of the validate-path predicates — is confirmed in substance but is **overstated by one predicate**, and the overstatement is load-bearing because it is exactly what the finding's disconfirming check tests.

Derived this turn:

- `grep -n 'beo_check' skills/beo/beo-reference/scripts/beo_run.py` → **exit 0, one hit**: `:37`, `from beo_check import changed_files, compute_prestate, validate_working_tree_prestate`. The finding's disconfirming check line reads *"`grep -n 'beo_check' beo_run.py` — no import, no call."* **Run as written, that check returns a hit and disconfirms the finding.** It is the same fail-open class this campaign recorded three times in S3a: a disconfirming check that is wrong in the direction that retires a live P1.
- The evidence line likewise says the four-predicate grep "returns no match". It returns **two**: `:37` and `:103`, both `validate_working_tree_prestate`. `:103` is a real call — `prestate_errors = validate_working_tree_prestate(root, ticket, recorded_changed_files)`.

What survives, and it is the whole of the finding's argument:

- **`validate_identity`, `validate_plan`, `run_structural_check` and `compute_approval_fields` are never called from `beo_run.py`** — the grep for them returns nothing. Those are four of the five things `beo_check.py:547-553` does under `--check validate`.
- `beo_run.py:119` writes the literal `"approved_by": "beo-validate"` into `state["approval"]`, and `:120-125` writes `ticket_file_hash`, `approval_projection_hash`, `repo_head` and `prestate` — the same fields `validate_approval_envelope` later re-checks. The producer and the checker of the evidence are the same process.
- `beo_run.py:72` builds `ticket_path` and `:78` parses it with `json.loads`. `grep -n 'read_ticket'` returns nothing; `beo_ticket` is imported at `:36` but used only at `:92` for `ticket_file_hash`. No ticket schema validation runs on this path.

So the accurate statement is: **`beo_run.py` runs one of the five validate-path predicates and mints the rest of the envelope itself.** The one it runs is a working-tree prestate comparison, which does not validate identity, plan, structure, or the approval projection. The gate is still satisfiable without doing the work the gate names; it is not satisfiable without doing *nothing*.

Disposition: **CONFIRMED, narrowed** — and the finding's disconfirming check must be replaced before Phase B, because as written it kills the finding. Files changed: none.

### F004 [P1] — CONFIRMED, both pointers exact

- `beo_run.py:210` — `def _accept(state)`; `:211` sets `state["phase"] = "reviewed"`; `:213-218` write `verdict = "accept"`, `route_condition_id = "verdict_accept"`, `findings = []`, `done_criteria_coverage = coverage`, `repair_count = 0`, `closed_in_br = True`.
- `beo_run.py:221` — applied as `locked_update_state(root, issue_id, "beo-review", _accept)`.
- `grep -n 'validate_review\|validate_containment' beo_run.py` → **no match**.
- The strict-mode `cross_check` requirement is at `beo_check.py:501-509`, on a path `beo_run.py` never reaches.

One detail worth adding to the finding: `done_criteria_coverage` is not derived from any check either. `beo_run.py:205-208` builds it as `{"criterion": c, "status": "covered", "evidence_refs": recorded_changed_files}` for every criterion in the list — **every criterion is marked covered unconditionally**, with the run's changed-file list pasted in as the evidence for each. The record does not merely assert that review happened; it asserts per-criterion coverage that nothing computed.

Disposition: **CONFIRMED**, with the coverage detail added. Files changed: none.

### F005 [P1] — CONFIRMED exactly

- `beo_run.py:136` — `verify_cmds = ticket.get("scope", {}).get("verify", {}).get("commands", [])`, defaulting to `[]` through three chained `.get`s, so a misspelt `scope`, `verify` or `commands` key yields an empty list rather than an error.
- `:138` — `all_ok = True`; `:140` — `for cmd in verify_cmds:` never iterates on an empty list.
- `:151-152` — the behaviour gate runs only `if bg_cmd:`.
- `:162-163` — `if not all_ok: _die(...)` therefore does not fire, and the run continues into `executing` at `:165`.
- `beo_ticket` is imported at `:36` and used only at `:92`; `validate_plan_only` is never called, confirming the finding's last evidence line.

Disposition: **CONFIRMED**. Files changed: none.

### F006 [P1] — CONFIRMED, both greps reproduced

- `grep -rl expected_receiver_phase_after_condition skills/beo/beo-reference/scripts/*.py` → **exit 1, no files**.
- `grep -rl expected_receiver_phase_after_condition skills/beo/beo-reference/registry/` → **`registry/pipeline.json` only**.

The key is declared in one registry and read by nothing. This is the script-side half of S3a's F084, which this pass disconfirmed on the doctrine side: the mapping **does** exist in `pipeline.json`, so S3a was right to disconfirm "the mapping is missing" — and S3b is right that nothing enforces it. The two rounds are consistent; the defect is inertness, not absence.

Disposition: **CONFIRMED**. Files changed: none.

### RX01 [P1] — **REVERSAL.** The report rejects `S3b-06-06` on a grep that is false, and the self-attestation bypass it rejects is real, live, and documented in the code as intentional

This row is not a disposition of a filed finding. It is the required output of the report's own **Verification Queue item 9**, which says: *"The three rejected candidates — re-check them before any Phase B work builds on a scout claim."* Two of the three rejections hold. One does not, and it reverses to a **P1**.

**What the report says.** Under `## Candidates Rejected On Source`: *"**S3b-06-06 (`_result_passed` self-attestation bypass) — REJECTED.** There is no `_result_passed` in the bundle (`grep -n '_result_passed' *.py` -> no match)."*

**What the tree says.** `grep -rn '_result_passed' skills/beo/beo-reference/scripts/*.py` → **exit 0, three hits**:

- `beo_check.py:451` — `def _result_passed(result: dict[str, Any]) -> bool:`
- `beo_check.py:486` — `if not _result_passed(result):`, guarding *"verification command did not pass"*
- `beo_check.py:496` — `elif not _result_passed(result):`, guarding *"behaviour_gate command did not pass"*

The report's command was `grep -n '_result_passed' *.py`. The scripts are not in the repository root, and `*.py` there matches nothing, so the shell glob produced a no-match that was read as a bundle-wide absence. **The rejection rests on a cwd-relative glob, not on the bundle.** This is the same class as S3a's F040, where a cited path did not exist and the check silently dropped its evidence — except here the false negative did not weaken a finding, it deleted one.

**The function, read this turn at `beo_check.py:451-462`:**

```
def _result_passed(result: dict[str, Any]) -> bool:
    """A verify/gate result passes on a passing status OR exit_code 0.

    Producers differ: beo_verify/beo_run emit exit_code; some callers write a
    status field. Accept either so enforcement does not depend on an
    undocumented convention.
    """
    status = str(result.get("status", "")).lower()
    if status in {"passed", "success", "ok"}:
        return True
    exit_code = result.get("exit_code")
    return isinstance(exit_code, int) and exit_code == 0
```

The docstring is the finding. `status` is checked **first** and returns `True` on its own; `exit_code` is never consulted when `status` is one of the three strings. A result entry carrying `{"command": "<the ticket's command>", "status": "passed"}` and **no `exit_code` at all** passes both enforcement sites.

**Is such an entry reachable?** Derived this turn, and yes, through the sanctioned writer:

- `registry/state.schema.json` types `execution.verify_results` as `{"type": "array", "items": {"type": "object"}}` — **any object**. No required keys, no property constraints, no enum on `status`.
- `beo_state.py:291-294` is the whole of the writer's validation: `_validate_list(...)` then *"execution.verify_results entries must be objects"*. Shape only.
- So `{"command": ..., "status": "passed"}` is schema-legal and writer-legal, survives `locked_update_state`, lands durably, and satisfies `beo_check.py:486`.

**Why the report's stated reasoning does not rescue the rejection.** The report argues *"`beo_run.py:142` and `:155` compute `ok = result["exit_code"] == 0` directly. The `status` string at `beo_run.py:146` is a display label derived from `ok`, not an input to it."* Both sentences are **true** — re-derived at `beo_run.py:142`, `:146` and `:155`. They are also about the wrong program. `beo_run.py` is one *producer* of results; `beo_check.py` is the *enforcer* that reads whatever is on disk, and the enforcer is what the candidate was about. Establishing that one producer is honest says nothing about a checker that accepts any producer's self-report.

The only in-bundle producer that writes a bare `status` is `beo_verify.py:91-101`'s `_skipped_result`, which writes `"status": "skipped"` and `"exit_code": -1` — not a passing string, so it correctly fails. That is the sole reason no *current* in-bundle path exploits this. Nothing prevents one, and the docstring says accepting foreign producers is the point.

**Interaction with F003 and F026.** F003 establishes that `beo_run.py` mints its own approval evidence. RX01 establishes that `beo_check.py`, the program that is supposed to be the independent check, accepts a self-reported pass string over a real exit code. Together they close the loop the report's `## Strongest Reason Not To Merge Yet` describes: there is no point in the chain where an outside fact is required.

**The other two rejections hold, re-derived:**

- **S3b-01-16 — rejection STANDS.** `beo_state.py:494-495` is exactly the claimed cross-reference: `if field_schema.get("registry") == "pipeline.condition_id" and payload.get(field) not in valid_conditions:` raising *"is not a registered pipeline condition"*. The report cites `:495`; the `if` opens at `:494`. Claim unaffected.
- **S3b-04-05 first half — rejection STANDS.** `beo_state.py:126-132`: `read_state` takes `lock = _locked(base / "state.lock")` at `:128` and reads inside `try`/`finally`. The read is locked. The second half — blocking `flock` with no `LOCK_NB` and no staleness detection — is carried as F029 and is dispositioned there.

Disposition: **REVERSAL — the rejection of `S3b-06-06` is withdrawn and the candidate is CONFIRMED as a P1.** It is filed here as `RX01` rather than renumbered into the report's `F` space, because the report's `F` ids are fixed and a receive pass does not renumber the document it verifies. Files changed: none.


### F007 [P1] — CONFIRMED, and the pointer is more specific than the report gives

- `grep -rn 'reservation_release_on' skills/beo/beo-reference/registry/*.json` → one hit, `registry/pipeline.json:156`, declaring the policy as a five-element list: `["verdict_accept", "executed_and_verified", "cannot_deliver", "abandoned", "repair_rescope"]`. The report cites the file without the line; `:156` is the line.
- `grep -rn 'reservation_release_on' skills/beo/beo-reference/scripts/*.py` → **exit 1, no output**. The finding's disconfirming check reproduces.
- `beo_reservation.py:345-362` is the release path, and it is guarded on operator input twice before it touches a record: `reason not in allowed_reasons` returns 1 at `:349-353`, and a missing `BR_ACTOR`/`BEO_ACTOR` returns 1 at `:353-355`. Both guards are CLI-shaped — they read an argument and an environment variable, which a lifecycle transition has neither of.

The registry declares an automatic policy and the bundle implements only a manual one. The five conditions in the list are exactly the terminal conditions, so the declared behaviour is "a bead that finishes releases its lease" and the actual behaviour is "a bead that finishes keeps its lease until a human types the release subcommand with the right actor in the environment."

Disposition: **CONFIRMED**. Files changed: none.

### F008 [P1] — CONFIRMED, with the source pointer redirected to the call that drops the argument

The finding is right and its cited lines are the wrong half of the mechanism. `beo_run.py:121-122` merely *stores* two already-computed values; nothing can be diagnosed there. The omission is upstream:

- `beo_run.py:94-97` — `approval_projection_hash = beo_approval.approval_projection_hash(ticket, ticket_file_hash=ticket_file_hash, repo_head=repo_head,)`. Three arguments. `reservation_evidence` is **not passed**.
- `beo_approval.py:41` gives that parameter the default `None`, and `beo_approval.py:51` gates the field on `if ticket.get("mode") == "strict" and reservation_evidence is not None:`. With the default in force the `and` short-circuits, so the projection omits `reservation` **even when the ticket's mode is `strict`**.
- The contrast is exact and one file away: `beo_check.py:265-270` — `compute_approval_fields` computes `reservation_evidence = active_reservation_evidence(root, ticket)` at `:266` and passes it into the same function at `:270`. Same helper, same ticket, one path binds the reservation and the other does not.
- Reachability re-derived: `beo_run.py:82-83` — `if ticket.get("mode", "quick") != "quick":` prints `WARNING: mode is '<mode>', not 'quick'. Proceeding anyway.` to stderr and falls through. A strict ticket reaches `:94` with nothing stopping it.
- `beo_check.py:216` (the report's second pointer) is real — `raise ValueError("BR_ACTOR or BEO_ACTOR is required for strict reservation validation")` — but it lives inside `active_reservation_evidence`, the function `beo_run.py` never calls. Citing it as evidence of the defect is citing the guard that is being bypassed, which is right in substance and confusing as a pointer.

The self-consistency the finding names is the sharp part: the later staleness re-check recomputes the projection the same way, so it compares an omission against an omission and always agrees. A drift check that cannot observe the field it is protecting reports "no drift" with full confidence.

Disposition: **CONFIRMED**, source pointer redirected from `beo_run.py:118-123` to `beo_run.py:94-97`, with `beo_check.py:265-270` as the contrasting site. Files changed: none.

### F009 [P1] — CONFIRMED on the substance, **narrowed**: the fail-open is not silent, it is documented as the contract

Every mechanical leg reproduces:

- `beo_verify.py:203` — `summary = {"pass": 0, "fail": 0, "skipped": 0}`.
- `:206-208` — `if worktree_missing:` → `result = _skipped_result(command, "worktree_missing")` and `outcome = "skipped"`. The `fail` counter is untouched on this branch.
- `:221` — `"ok": summary["fail"] == 0`. With every command skipped, `fail` is 0 and `ok` is `True`.

The narrowing: the finding's title and its "silently degrades" phrasing say the pass is undeclared. It is declared. `beo_verify.py:17`, in the module docstring's own exit-code table, reads *"0  all verifications pass (or all skipped for missing worktree)"* — the parenthesis is the defect, written down, at the top of the file, as intended behaviour. That changes the finding's character and not its severity. An undocumented fail-open is a bug; a documented one is a contract that says a gate which could not run reports the same value as a gate that ran and passed, and every caller that trusts the documented contract inherits the defect by design. It also means the fix is not a one-line change to `:221` alone: the docstring at `:17` is a second site that must move with it, or the code and its stated contract will disagree in the opposite direction.

The finding's own durable solution is right, and the third verdict is the better half of it: `skipped` must be distinguishable from `pass` at the type level, not by a counter a caller has to remember to inspect.

Disposition: **CONFIRMED-narrowed** — the behaviour is exactly as found; "silently" is wrong, and the remediation surface is two sites, `beo_verify.py:221` and `beo_verify.py:17`. Files changed: none.

### F010 [P1] — CONFIRMED, all four sites reproduced

`grep -n 'reviewed_by' skills/beo/beo-reference/scripts/*.py` → four hits, exactly the ones the finding names, and nothing else in the bundle:

- `beo_state.py:57` — `"reviewed_by": "beo-review",` inside `initial_state`'s `review` block, a bare literal with no condition around it.
- `beo_state.py:259` — the name appears in `review_fields`, which `_reject_unknown_fields` uses as an allow-list. This is a **validation** set, not a writer; it permits the key to be present and updated, it never sets it.
- `beo_state.py:321-323` — `reviewed_by = review.get("reviewed_by")` then `if reviewed_by not in {"beo-execute", "beo-review"}: raise`. The literal planted at `:57` is a member of the validator's own accept set, so the falsehood is not merely unchecked, it is the value the checker was written to approve.

No fourth site writes it. A record is created claiming `beo-review` reviewed it, the claim is durable, and the validator confirms the claim on every subsequent read. The finding's note that this compounds F026 is right and worth keeping: making the field truthful requires a writer *and* an identity that means something, and the bundle has neither.

Disposition: **CONFIRMED**. Files changed: none.

### F011 [P2] — CONFIRMED, and the exposure is **wider** than the finding states

`sed -n '533,564p' beo_check.py` reproduces the shape exactly:

- The guard is `beo_check.py:537-543` — `try: ticket = read_ticket(...); state = read_state(...)` / `except Exception as exc:` sets both to `{}` and appends the message. (The report gives the range as `:537-544`; `:544` is the `if ticket:` that follows the block, not part of it.)
- `beo_check.py:562` — `errors.extend(validate_runtime_events(read_events(root, args.issue), args.issue))`, outside that `try`, exact as cited.
- `beo_state.py:632` — `event = json.loads(line)` with no handler; `beo_state.py:634` — `raise ValueError(f"runtime-events.jsonl line {line_number} must be an object")`. Both exact.

**Wider than stated.** `read_events` is not the only unguarded fallible call in `main`. `sed -n '544,562p' beo_check.py` enumerates every call between the end of that `try` block and the `print`, and all but one sit outside any handler: `validate_identity` (`:546`), `validate_plan` (`:548`), `run_structural_check` (`:549` — which spawns a subprocess), `validate_working_tree_prestate` (`:550`), `validate_approval_envelope` (`:556`), `validate_execute_entry` (`:557`), `validate_containment` (`:559` — which reads git), `validate_review` (`:561`), and on `:562` two nested calls, `read_events` and `validate_runtime_events`. That is **ten bare fallible calls across nine lines**. Exactly one call in the region has its own guard: `compute_approval_fields` at `:551-554`, and that guard catches `ValueError` only.

So the finding's contract statement — *"the whole of `main` should be unable to raise"* — is the right remediation, and it is a larger change than moving one call into an existing block. The lone `ValueError`-only guard at `:551-554` is the tell: the author guarded the one call they expected to raise and left ten others bare, which is how a fail-closed intention becomes a fail-crash implementation.

Disposition: **CONFIRMED**, broadened from one unguarded call to ten bare calls plus one narrowly guarded. Files changed: none.

### F012 [P2] — CONFIRMED, every pointer exact

- `beo_state.py:93` — `def atomic_write_json(path, data)`; `:97` `tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=str(path.parent))`. The bundle's durable-write discipline, as cited.
- `beo_reservation.py:174-182` — `write_reservations` repeats that pattern (`mkstemp` at `:177`), which is what makes it a discipline rather than one function's habit.
- `beo_state.py:646` — `lock = _locked(base / "runtime-events.lock")`. The lock is taken, as the finding grants.
- `beo_state.py:649-653` — `with open(path, "a", encoding="utf-8") as handle:` then two `handle.write` calls, `handle.flush()`, `os.fsync(handle.fileno())`. Direct append into the live file.

The finding's distinction is the correct one and is worth preserving verbatim in the remediation: the lock serialises *writers*, and `fsync` orders the write against the *device*. Neither makes a two-call append atomic against a crash or `ENOSPC` between them. The one thing the lock does buy is the finding's own recovery argument — under an exclusive lock a torn line can only ever be the trailing one, which is what makes the cheaper of its two remedies sound.

Disposition: **CONFIRMED**. Files changed: none.

### F013 [P2] — CONFIRMED, with the body range corrected

- `beo_state.py:126-133` — `read_state` takes `lock = _locked(base / "state.lock")` at `:128`.
- `beo_state.py:646` — `append_event` takes `_locked(base / "runtime-events.lock")`.
- `beo_state.py:621-636` — `read_events`, whole body. No `_locked`, no `_unlock`, no lock path constructed. The finding's disconfirming check reproduces. (The report gives the range as `:621-638`; the function ends at `:636` — `:637-638` are the blank lines before `append_event`.)

The asymmetry is exactly one accessor deep: the module has two lock-protected file pairs and three of the four accessors participate. Combined with F011 and F012 this is the same defect seen from a third side — the events file is the one artifact in the bundle with no atomic write, no reader lock, and no reader error handling, and all three gaps land on the same file.

Disposition: **CONFIRMED**. Files changed: none.

### F014 [P2] — CONFIRMED at both sites, both pointers exact

- `beo_verify.py:57` — `argv = shlex.split(command)`. The `try` opens at `beo_verify.py:69`. Twelve lines separate them, and everything in between is the empty-`argv` branch.
- `beo_verify.py:58-68` is that branch, and its comment is the finding's strongest evidence, quoted here because the report only paraphrases it: *"An empty command is a ticket misconfiguration; treat it as a failure (exit_code -1) so the bead does not pass verification. The empty `command` string itself is the diagnostic."* The author reasoned explicitly about malformed ticket commands on this exact line, chose fail-closed, and covered the branch that `shlex.split` returns rather than the branch where it raises.
- `beo_check.py:397` — `argv = shlex.split(command)`, with its own `try` opening at `:400` and its own empty-`argv` return at `:398-399`. Identical shape, identical omission, in the other program.
- The function's own docstring at `beo_verify.py:52-53` states the principle being violated: *"TICKET.json is human-approved, but the harness should not rely on the author to sanitize their own commands."*

Disposition: **CONFIRMED**. Files changed: none.

### F015 [P2] — CONFIRMED, and the timeout half is stronger than the report's phrasing

- `grep -nE 'subprocess\.(run|Popen|call|check_output|check_call)\(' skills/beo/beo-reference/scripts/*.py | wc -l` → **16**. The report's count reproduces.
- `grep -n 'timeout' skills/beo/beo-reference/scripts/*.py` → **exit 1, no output at all**. The report says the grep "returns no `timeout=` argument on any of them," which understates the result: the string `timeout` does not occur anywhere in the seventeen scripts, in code, comment, or docstring. Not one call site passes it, and no site records having considered it.
- `beo_verify.py:75` — `capture_output=True`, exact.
- `grep -n 'proc.stdout\|proc.stderr' beo_verify.py` → **exit 1, no matches**. The captured streams are never read.
- `beo_verify.py:82-88` is the returned dict, and it has exactly five keys: `command`, `exit_code`, `duration_ms`, `ran_at`, `worktree_path`. The finding's list is complete and in order.

Both halves stand, and they compound in one direction the finding names only in passing: a hung command with no timeout is also a command whose output is being captured into a pipe nobody drains at the end, so the failure is a silent indefinite block whose only artifact would have been the output that is discarded.

Disposition: **CONFIRMED**. Files changed: none.

### F016 [P2] — CONFIRMED, **count corrected: five registry-load sites, not four**

`grep -n 'parents\[1\] / "registry"' skills/beo/beo-reference/scripts/*.py | wc -l` → **5**, distributed as `beo_check.py` 1, `beo_state.py` 3, `beo_ticket.py` 1:

- `beo_check.py:295` — `profiles.json`
- `beo_state.py:210` — `pipeline.json`
- `beo_state.py:218` — `state.schema.json`
- `beo_state.py:424` — `runtime-event.schema.json`
- **`beo_ticket.py:36` — `ticket.schema.json`** — not in the report's source-pointer line and not in its evidence.

The report's durable solution says the decision is *"restate[d] implicitly at four sites."* It is restated at five. The omitted one is not incidental: `ticket.schema.json` is the schema every ticket is validated against, so the ticket contract itself is bundle-relative rather than checkout-relative, which is the most consequential instance of the pattern the finding describes.

The rest reproduces: `grep -n '__file__' skills/beo/beo-reference/scripts/*.py` → 13 hits across 10 files, including `check_skill_bundle.py:9` (`SCRIPT_DIR = Path(__file__).resolve().parent`, no `--root`), `beo_setup.py:17` (`AGENTS_TEMPLATE`, a sixth shape), and the `sys.path.insert(0, str(Path(__file__).parent))` idiom at `beo_memory_write.py:12`, `beo_reservation.py:14` and `beo_setup.py:10`. `beo_io.py:45` `repo_head_sentinel(root)` runs `git rev-parse HEAD` with `cwd=root` and returns `"git:unavailable"` on `FileNotFoundError` — the fifth resolution behaviour the finding names, exact.

Disposition: **CONFIRMED**, with the site count corrected from four to five and `beo_ticket.py:36` added. Files changed: none.

### F017 [P2] — CONFIRMED on the omission, **narrowed** on the failure mode, and its "better" remediation is already implemented

The omission is real and the callers reproduce:

- `grep -n 'reject_unsafe_issue_id' skills/beo/beo-reference/scripts/*.py` → four hits: the definition at `beo_paths.py:67`, the call at `beo_paths.py:95`, and the local import and call at `beo_ticket.py:166-167`. `beo_run.py` and `beo_reservation.py` are absent, as found.
- `beo_run.py:71` — `base = root / ".beads" / "artifacts" / issue_id`, built by hand from the raw CLI argument. (The report cites `:72`, the `ticket_path` line; `:71` is where the unvalidated value enters a path.)

**The remediation is already done, and `beo_run.py` routes around it.** The finding's "better" hypothesis is *"move the call into `artifact_dir` so no caller can skip it."* `beo_paths.py:94-96` is exactly that: `def artifact_dir(root, issue_id):` / `reject_unsafe_issue_id(issue_id)` / `return root / ".beads" / "artifacts" / issue_id`. `beo_state.py:16-19` is a delegating wrapper onto it, and all five `beo_state` call sites (`:127`, `:138`, `:569`, `:622`, `:644`) go through the guard. So the fix is not "move the call into `artifact_dir`" — it is "`beo_run.py:71` must stop hand-building the string `artifact_dir` already returns." That is a smaller and more durable change than the finding proposes, and it is the only one needed.

**The failure mode is narrower than stated.** The finding says an `issue_id` of `../../..` *"reads a TICKET.json outside the artifacts tree and runs its commands."* Derived from the order of operations in `main`:

- `beo_run.py:74-75` — existence check on the traversed path.
- `beo_run.py:78` — `ticket = json.loads(ticket_path.read_text())`. **The out-of-tree file is read and parsed.** This half of the claim holds.
- `beo_run.py:86` — `beo_state.initialize_state(root, issue_id, owner="beo-plan")`, whose first act at `beo_state.py:138` is `artifact_dir(root, issue_id)` → `reject_unsafe_issue_id` → `ValueError`.
- `beo_run.py:85-88` catches `FileExistsError` only, so that `ValueError` propagates as an uncaught traceback.

No verify command runs: execution is downstream of `:86`. The accurate statement is *arbitrary-path read and parse, then an uncaught traceback* — which is still a real defect (an out-of-tree read, and a crash rather than a refusal, the same fail-crash shape as F011), and is not command execution.

Disposition: **CONFIRMED-narrowed** — omission confirmed, failure mode reduced to read-and-crash, remediation redirected to `beo_run.py:71`. Files changed: none.

### F018 [P2] — CONFIRMED, every site reproduced

`grep -n 'BR_ACTOR\|BEO_ACTOR' skills/beo/beo-reference/scripts/*.py | wc -l` → **9 hits** (the report says 8), and the split is exactly as found:

- `beo_run.py:48` — `actor = os.environ.get("BEO_ACTOR") or os.environ.get("BR_ACTOR")`. `BEO_ACTOR` wins.
- `beo_io.py:41-42` — `def actor_identity() -> str | None:` / `return os.environ.get("BR_ACTOR") or os.environ.get("BEO_ACTOR")`. `BR_ACTOR` wins.
- The five message strings all phrase it `BR_ACTOR or BEO_ACTOR`, in `BR_ACTOR`-first order: `beo_check.py:92`, `beo_check.py:216`, `beo_reservation.py:238`, `:309`, `:353`. `beo_run.py:50`'s own `_die` message reads `"BEO_ACTOR or BR_ACTOR must be set"` and `beo_run.py:12`'s docstring likewise — so `beo_run.py` is self-consistent in the minority order, which is what makes this a fork rather than a typo.

Counted over the 9 hits: **two resolution sites, in opposite orders** (`beo_run.py:48`, `beo_io.py:42`), and seven hits that are documentation or error text — five in `BR_ACTOR`-first order (`beo_check.py:92`, `:216`, `beo_reservation.py:238`, `:309`, `:353`) and two in `BEO_ACTOR`-first (`beo_run.py:12`, `:50`), the two matching `beo_run.py:48`'s own resolution. Six statements of `BR_ACTOR`-first precedence against three of `BEO_ACTOR`-first, with the minority confined to one file. The finding's remediation — delete `beo_run.py:_actor`, call `beo_io.actor_identity()` — is the right shape and is one line.

Disposition: **CONFIRMED**. Files changed: none.

### F019 [P2] — CONFIRMED, with a one-line pointer correction that the report repeats twice

`sed -n '536,546p' beo_check.py` reproduces the collapse:

- `:537` `try:` / `:538` `ticket = read_ticket(root, args.issue).data` / `:539` `state = read_state(root, args.issue)` — two independent reads, one handler.
- `:540` `except Exception as exc:` / `:541` `ticket = {}` / `:542` `state = {}` / `:543` `errors.append(str(exc))` — **both** artifacts discarded on either failure, exactly as found.
- `:544` `if ticket:` — the gate that then skips every check.

**Pointer correction.** The report places `if ticket:` at `:545`; it is at `:544`. The same off-by-one appears in F011, which gives the guarded block as `:537-544` when it ends at `:543`. One line, twice, in the same region — recorded because it is the class of defect this pass exists to catch, not because it changes either finding.

The substance is untouched and the failure mode reproduces on the order of operations: `read_ticket` at `:538` can succeed and `read_state` at `:539` raise `FileNotFoundError` for an issue with no `state.json`, and the successfully-read ticket is then thrown away by `:541`. The output is one error string, and nothing in it distinguishes "checked and failed" from "never checked."

Disposition: **CONFIRMED**. Files changed: none.

### F020 [P2] — CONFIRMED, both pointers exact

- `beo_worktree.py:25` — `WORKTREE_BASE = Path(os.environ.get("BEO_WORKTREE_BASE", "/tmp/beo-worktrees"))`, at module scope, evaluated once at import.
- `beo_worktree.py:66-68` — `if not SAFE_ISSUE_ID.fullmatch(issue_id): raise ValueError(...)` then `return WORKTREE_BASE / issue_id`. The key is the issue id and nothing else; no component of the path derives from the repository.

Worth recording alongside F017: this function **does** validate its issue id, through `SAFE_ISSUE_ID.fullmatch`, which is a third id-safety mechanism in the bundle next to `reject_unsafe_issue_id` and the absence of either in `beo_run.py`. Three conventions for one predicate, and the one entry point that skips all three is the one that executes commands.

The finding's two harms are distinct and both hold: cross-repository collision (nothing in the path separates two checkouts sharing an issue id) and a predictable shared-machine default under `/tmp`. Import-time evaluation is the third: an in-process caller cannot vary the base after import, which is also why this is hard to test without process isolation.

Disposition: **CONFIRMED**. Files changed: none.

### F021 [P2] — CONFIRMED, and the "even when removal failed" half is the sharper one

- `beo_worktree.py:293-294` — `result = subprocess.run(["git", "branch", "-D", existing], ...)`. `-D` is the force form, exact as cited.
- `beo_worktree.py:288-289` — the preceding `worktree prune` failure path does `errors.append(f"worktree prune: {result.stderr.strip()}")` and **falls through**. There is no `return`, no `if not errors:` guard.
- `beo_worktree.py:292` — `if existing:` is conditioned on the branch existing and on nothing else.
- `beo_worktree.py:300` — `status = "success" if not errors else "partial"`. So the function reports `partial` *after* having already force-deleted the branch, and the operator learns of the prune failure from the same record that tells them the branch is gone.

No merge check anywhere: `grep` for `branch -d` or a merge-status probe in this module finds nothing; `-D` is the only branch deletion form present. The finding's remediation — `-d` by default, `-D` only behind an explicit operator flag, and no branch touch at all when removal failed — matches both halves.

Disposition: **CONFIRMED**. Files changed: none.

### F022 [P2] — CONFIRMED, both counts reproduce exactly

- `grep -c subprocess skills/beo/beo-reference/scripts/beo_worktree.py` → **11**.
- `grep -cE 'subprocess\.(run|Popen|call|check_output|check_call)\(' beo_worktree.py` → **9** call sites. The report's "11 mentions across 9 call sites" is exact, and 9 of the bundle's 16 (F015) is a correct share.
- `grep -n '_locked\|flock' beo_worktree.py` → **exit 1, no match**. No application lock of any kind in the module.

The finding carries `Confidence: medium` and earns it: it concedes that git's own index lock covers part of the exposure and rests the claim on the multi-command sequences being non-atomic between commands, which is the accurate version. The contrast it draws is the load-bearing part and it holds — `beo_state.py` takes a file lock to append one advisory event line (F012), and this module force-deletes branches (F021) under none.

Disposition: **CONFIRMED**, at the medium confidence the report itself assigned. Files changed: none.

### F023 [P2] — CONFIRMED, every line exact

`sed -n '334,348p' beo_check.py`:

- `:336` — `reject_unsafe_path(token)` inside a `try` that returns on `ValueError`. Runs for **every** token, glob or not, as the finding grants.
- `:340` — `if not has_glob(token):` — the guard.
- `:341-344` — the guarded body: `(root / normalize_posix(token)).resolve().relative_to(root.resolve())` with `except ValueError: errors.append(f"path escapes repo: {token}")`.

So a globbed token receives the lexical check and skips the resolving one. The finding's reasoning for why that matters is the right one and is not merely theoretical: `reject_unsafe_path` is lexical by construction, and `.resolve()` exists in this function precisely because a symlink escape is invisible lexically. Removing the second check for an entire class of token leaves that class covered by the check the code itself demonstrates is insufficient.

The remediation is sound and cheap: the prefix before the first glob segment is always concrete, so it can be resolved and checked without expanding anything.

Disposition: **CONFIRMED**. Files changed: none.

### F024 [P2] — CONFIRMED exactly

`beo_verify.py:79` — `except FileNotFoundError:` / `:80` `exit_code = -1`. That is the whole handler around the `subprocess.run` at `:70-77`.

The finding's list of escapees is correct as a matter of the exception hierarchy: `PermissionError`, `IsADirectoryError`, `NotADirectoryError` and a bare `OSError` are all siblings or the parent of `FileNotFoundError`, none of them subclasses of it. Its remediation is a strict widening — `FileNotFoundError` **is** an `OSError`, so catching `OSError` changes no currently-handled behaviour — and that is the correct characterisation.

This is the same defect class as F014 in the same function: two ways for `run_one_command` to raise instead of recording — `shlex.split` at `:57` and the narrow handler at `:79` — **twenty-two lines apart**, not twelve.

Disposition: **CONFIRMED**. Files changed: none.

### F025 [P2] — CONFIRMED, and **strengthened**: the acceptance write has no staleness check at all, not even the cheap one

The branch structure reproduces exactly:

- `beo_check.py:555-557` — `elif args.check == "execute-entry":` calls `validate_approval_envelope` (`:556`) and `validate_execute_entry` (`:557`).
- `beo_check.py:560-561` — `elif args.check == "review-entry":` calls `validate_review` and nothing else; `:562`'s `validate_runtime_events` is outside the branch and runs for every check.
- `beo_check.py:275-280` — `validate_approval_envelope` re-derives through `compute_approval_fields` at `:280`, which is the content-based check.
- `beo_state.py:617-618` — `execution_entry_is_current` is the sequence-based one. `grep -rn 'execution_entry_is_current' skills/beo/beo-reference/scripts/` gives four hits: the `def` at `beo_state.py:617`, the import at `beo_check.py:26`, and **two call sites** — `beo_state.py:586` and `beo_check.py:437`, the latter inside `validate_execute_entry` (`def` at `:429`), so the execute-entry CLI path does run it.

**The strengthening.** The report says `execution_entry_is_current` *"is the only check that runs automatically inside `locked_update_state`."* Derived: it is called at `beo_state.py:586`, and `:583-586` places it inside `if owner == "beo-execute":` → `if before.get("phase") == "approved":`. It does not run for any other owner. The other call site, `beo_check.py:437`, is inside `validate_execute_entry`, so it fires only on `--check execute-entry` and never at acceptance. The acceptance write is `beo_run.py:221` — `locked_update_state(root, issue_id, "beo-review", _accept)`. That owner never reaches `:586`.

So at the acceptance write the content check has not run since execute-entry (the finding's claim) **and** the sequence check does not run either. The irreversible write is guarded by neither of the bundle's two staleness mechanisms. The finding's remediation — call `validate_approval_envelope` from `review-entry` too — remains correct and is now the more necessary of the two, since there is no cheap fallback underneath it.

Disposition: **CONFIRMED-strengthened**. Files changed: none.

### F026 [P2] — CONFIRMED on the root cause, **narrowed**: the label is unverified, not inert

- `grep -n 'locked_update_state(' skills/beo/beo-reference/scripts/*.py` → the definition at `beo_state.py:559` and **four** call sites, all in `beo_run.py`: `:130` `"beo-validate"`, `:173` `"beo-execute"`, `:183` `"beo-execute"`, `:221` `"beo-review"`. The report names three (`:130,173,221`) and omits `:183`. Four calls, three role strings, one process, one `main`.
- `beo_state.py:582` is `_reject_unowned_changes(before, after, owner)`; the `if owner == "beo-execute":` the report attributes to `:582` is at `:583`. One line.

**The narrowing, and it matters for Phase B.** The report says `locked_update_state` *"branches on `owner == 'beo-execute'` and otherwise trusts it."* The `owner` string does more than that: `_reject_unowned_changes` at `:582` uses it to decide **which fields this owner may change at all** — the `approval_fields` / `execution_fields` / `review_fields` partition seen at `beo_state.py:257-259` (F010). So the label is not a decorative annotation; it is the access-control input for every write. That makes the defect worse rather than milder, and states it more precisely: the bundle has a working field-level permission system whose sole credential is a string the caller types. `beo_run.py` types all three.

Everything else stands, including the finding's refusal to propose a patch. Its position — that this is the structural question Phase B must settle before any of the individual labels is made truthful — is the correct disposition for a root cause that F003, F004 and F010 each express one face of, and this pass does not overrule it.

Disposition: **CONFIRMED-narrowed** — root cause confirmed, call-site count corrected to four, and the `owner` string identified as the field-permission credential rather than a mere branch condition. Files changed: none.

### F027 [P2] — CONFIRMED, with the comment quoted in full because it is the evidence

- `beo_run.py:189-190` — *"br close must succeed before we record closed_in_br=True in state.json. / If it fails, the bead stays in `executed` for retry."* The ordering was reasoned about and chosen; the report's `:189` is exact.
- `beo_run.py:191-194` — the `subprocess.run(["br", "close", issue_id, "--reason", "done", "--actor", actor], ...)`. The call opens at `:191`; the report's `:192` is the argv line.
- `beo_run.py:221` — `st = beo_state.locked_update_state(root, issue_id, "beo-review", _accept)`, and `_accept` at `:210-219` sets `state["review"]["closed_in_br"] = True` at `:217`. Exact.
- `beo_run.py:14-18` — the exit-code table, ending at `3   br close failed (state left in executed; fix and retry or close manually)`. There is no code 4, and no line describes a successful close followed by a failed state write. Exact.

The finding's construction is precise: the comment proves the author considered the ordering, the exit-code table proves they documented the failure on one side of it, and the gap is the other side. And the gap is reachable — `_accept` runs through `locked_update_state`, which raises on lock failure or on any validation error, and F001 makes at least one such error reachable for every strict-mode bead. Recovery then requires a human to know that `br` and `state.json` disagree, which nothing tells them.

Disposition: **CONFIRMED**. Files changed: none.

### F028 [P2] — CONFIRMED, **narrowed**: only the second of the two prestate checks is advisory

Both pointers are exact (`beo_run.py:106-109`, prints at `:108-109`), and the found behaviour reproduces: `unexpected = sorted(path for path in current_changed_files if path not in recorded_changed_files)` at `:106`, then two stderr prints and no exit.

The narrowing is the four lines above it, which the finding does not mention:

- `beo_run.py:103` — `prestate_errors = validate_working_tree_prestate(root, ticket, recorded_changed_files)`.
- `beo_run.py:104-105` — `if prestate_errors: _die("; ".join(prestate_errors))`. **Fatal.**

So `beo_run.py` runs two prestate checks and only the second is advisory. The finding's title — *"`beo_run.py`'s dirty-path check is advisory"* — reads as though there were one check and it were toothless; there are two and the first refuses. That makes the defect sharper, not weaker: the code demonstrates on the adjacent line that it knows how to refuse a prestate violation, and then declines to for the one class of violation the check at `:106` exists to find. The finding's own remediation ("Refuse") is therefore a request to make `:107` behave like `:104`, four lines up, in the same function.

Disposition: **CONFIRMED-narrowed** — the advisory behaviour is confirmed at `:106-109`; the claim is scoped to that second check, since `validate_working_tree_prestate` at `:103-105` is fatal. Files changed: none.

### F029 [P2] — CONFIRMED, and this is the second half of the S3b-04-05 candidate whose first half the report correctly rejected

`grep -n 'flock\|LOCK_' skills/beo/beo-reference/scripts/*.py` → six hits, all of them:

- `beo_reservation.py:19` `LOCK_FILE`, `:40` the path, `:44` `fcntl.flock(f, fcntl.LOCK_EX)`, `:52` `fcntl.flock(f, fcntl.LOCK_UN)`.
- `beo_state.py:70` `fcntl.flock(handle, fcntl.LOCK_EX)`, `:78` `fcntl.flock(handle, fcntl.LOCK_UN)`.

`grep -n 'signal.alarm\|LOCK_NB' skills/beo/beo-reference/scripts/*.py` → **exit 1, no output**. Neither string occurs anywhere in the seventeen scripts. No timeout wrapper, no pid recorded in either lock file.

The finding's own carve-out is the part that makes it trustworthy: it states plainly that `flock` is process-scoped and self-releases on hard process death, so this is about **hangs, not crashes**, and it credits candidate S3b-04-17 for that correction rather than overclaiming. The compounding with F015 is the live path — a verify command with no timeout hanging while holding the state lock is one process, and every other actor on that issue then blocks with no diagnostic naming the file they are waiting on.

Disposition: **CONFIRMED**. Files changed: none.

### F030 [P2] — CONFIRMED, with two mechanical additions the finding does not make

The propagation path is exactly as described, and reads as follows:

- `beo_state.py:105` — `os.replace(tmp_path, path)`. The rename is complete; the new content is visible to every reader from this instant.
- `beo_state.py:106` — `_fsync_dir(path.parent)`, inside the same `try:` that opened at `:99`.
- `beo_state.py:107-111` — `except Exception:` unlinks `tmp_path`, swallows `FileNotFoundError`, and `raise`s. So a directory-fsync failure reaches the caller as a write exception.

Two additions, both derived:

1. **`_fsync_dir` is half-guarded.** `beo_state.py:82-90`: the `os.open` is wrapped in `try: ... except OSError: return`, so a failure to *open* the directory returns silently. The `os.fsync(fd)` at `:88` sits in a `try`/`finally` with no `except`, so a failure to *fsync* propagates. The function therefore already distinguishes two failure modes and treats them oppositely — one silently ignored, one fatal — which is the design decision the finding is asking to be made explicit, made implicitly and in the wrong place.
2. **The cleanup in the handler is a no-op on this path.** By the time `_fsync_dir` can raise, `tmp_path` no longer exists — `os.replace` renamed it. `tmp_path.unlink()` raises `FileNotFoundError`, which `:109-110` catches and passes. So the recovery code that runs on this failure does nothing, and the caller receives an exception whose only effect was to re-raise.

`beo_reservation.py:163` `fsync_dir` and its call at `:186` repeat the pattern in the second writer, as cited.

The finding's `Confidence: medium` is right for the likelihood of a directory fsync failing; the consequence, once it does, is exactly as stated.

Disposition: **CONFIRMED**. Files changed: none.

### F031 [P2] — **CONFIRMED-narrowed to one of the two programs**, with an addition: `beo_score_context.py`'s reporting channel lies in two of its three tiers, and the finding's cross-reference is to the wrong finding

`beo_score_trace.py` — **the finding holds**:

- `:320` `state_loaded = False`, `:323` `state_loaded = True`, `:324-325` `except FileNotFoundError:` → `state = {"issue_id": args.issue, "execution": {}, "review": {}}`.
- `:331` — `result = score_trace(state, ticket, events)`. **`state_loaded` is not passed in.** The scorer never learns the state was synthesised.
- `:332` — the flag's only use in the whole file: `if state_loaded and (state.get("execution") or {}).get("started_at"):` gates whether a score event is appended. It affects a side effect and not the output.
- `:333` prints `result`; `:335` `return 0`. Nothing in the printed JSON says the issue does not exist.

`beo_score_context.py` — **the finding does not hold as written**, and the mechanism it names is defective in the opposite direction:

- `:248-251` set the same flag the same way, but `:259` reads `result = score_context(state, ticket, events, state_loaded=state_loaded)` — the flag is **threaded into the scorer**, whose signature at `:154` takes it as a keyword-only argument.
- `:161` — `counts = _tally(paths, ticket, state if state_loaded else None)`. With the flag false the third argument is `None`, so `_tally`'s `:149` increment is skipped and `counts["state"]` stays 0.
- `:167` — the returned `breakdown` carries a `"state_loaded"` key.
- `:177-178` — `if requires["state"] and not breakdown["state_loaded"]: missing.append("state_loaded")`.

**Addition, and it inverts the channel in two of three tiers.** `:167` computes `"state_loaded": counts["state"] >= requires["state"]`, and `MIN_REQUIRES` at `:25-29` sets `"state": 0` for `minimal` and `standard` and `1` only for `detailed`. In those two tiers the comparison is `0 >= 0`, so the key reports `True` on a state that was never loaded. `:177`'s `if requires["state"]` short-circuits for the same two tiers, so `missing` stays silent as well. `resolve_tier` (`:32-39`) returns `"standard"` when neither `state["execution"]["trace_tier"]` nor `ticket["mode"]` resolves — and a synthesised state has an empty `execution` dict (`:253`'s substitution), so the lying branch is the **default** branch on exactly the input the finding is about.

So the channel the finding says has been eliminated survives in `beo_score_context.py` only under `detailed`. Under `minimal` and `standard` it is worse than eliminated: a boolean named `state_loaded` reads `True` when no state was loaded, which a consumer would take as positive evidence rather than as silence. The finding cites `beo_score_context.py:252` as a second instance of the defect; `sed -n '246,256p'` shows `:252` is the `except FileNotFoundError:` line and `:253` the substitution itself, so the citation is off by one but points into the right block, the substitution is real, and the program's handling of it differs from `beo_score_trace.py` — but only in one of three tiers does that difference produce a truthful report.

**Cross-reference defect.** The finding's second evidence line reads *"Combined with F032 (both `main()` always return 0), there is no channel left that reports the absence."* F032 is the instrument-coverage finding about `beo_audit.py` and `check_skill_bundle.py`; it says nothing about the scorers' return values. The finding it means is **F046** — *"Both scorers document exit codes '0, 1' and `main()` can only return 0"* — derived at report line 839. Both `return 0` statements reproduce (`beo_score_trace.py:335`, `beo_score_context.py:263`), so the substance of the parenthetical is correct and only its label is wrong.

Disposition: **CONFIRMED-narrowed** — the defect as stated is real in `beo_score_trace.py` and does not hold in `beo_score_context.py`, whose `state_loaded` channel is instead defective in the opposite direction (reports `True` on an absent state) under the `minimal` and `standard` tiers; the `F032` citation should read `F046`. Files changed: none.

### F032 [P2] — CONFIRMED, every count and every file name reproduces

- `beo_audit.py:779` — `for name in ("pipeline.json", "phase-contracts.json", "runtime-event.schema.json"):`. Three files, exact.
- `ls skills/beo/beo-reference/registry/ | wc -l` → **9**. The six never loaded by `beo_audit.py` are exactly the six the finding names: `approval-envelope.json`, `harness-proposal.schema.json`, `profiles.json`, `reservation-schema.json`, `state.schema.json`, `ticket.schema.json`. Enumerated by set difference against the `ls`, not carried.
- `check_skill_bundle.py:151-154` — `required_registries` is a list of **eight** strings, and the one absent from it is `harness-proposal.schema.json`. Exact.
- `grep -n 'import jsonschema' skills/beo/beo-reference/scripts/*.py` → **exit 1, zero matches**. Neither instrument is a schema validator.

So a deleted `harness-proposal.schema.json` is invisible to both: `beo_audit.py` never loads it, and `check_skill_bundle.py` never lists it as required. That is a concrete, currently-live blind spot in the exact overlap of the two instruments, and it is the finding's strongest single fact.

The self-demonstrating argument holds and is the reason this is the instrument finding rather than one more coverage complaint: `state.schema.json` declares `cross_check` (F001), the writer rejects it, and no instrument loads `state.schema.json` — so the defect S3b found by reading could not have been found by running the tools the brief calls the instruments.

The finding's C12 instruction is correct and is preserved as written: the instrument extension and the doctrine fixes it would have caught **must not share a Phase B iteration**, and the extended instrument must be run against the *unfixed* doctrine to demonstrate it reports F001, F006, F007 and F010. This pass does not weaken that.

Disposition: **CONFIRMED**. Files changed: none.

### F033 [P2] — CONFIRMED, pointer exact

`beo_audit.py:645` — `if not isinstance(target, str) or not target.startswith("skills/beo/"):`, with the `Finding("C6", SEVERITY_CRITICAL, ...)` at `:646-650`. There is no `resolve()` and no `relative_to` in the function.

The traversal example holds as stated: `skills/beo/../../../etc/passwd` satisfies `startswith("skills/beo/")` and there is nothing downstream to catch it. And the finding's framing is the sharp one — the bundle's better pattern is not hypothetical, it is at `beo_check.py:341-344` (F023), in a sibling file, doing resolve-then-`relative_to`. C6 is the check that enforces kernel §10 containment and it uses the weaker of the two containment implementations the bundle already has.

Counting F023's glob hole and `beo_paths.reject_unsafe_path`'s lexical check, the finding's closing line is exact: three containment implementations, and the audit uses the weakest.

Disposition: **CONFIRMED**. Files changed: none.

### F034 [P2] — CONFIRMED as written, including its own concession

`beo_audit.py:783` — `return [Finding("C0", SEVERITY_CRITICAL, f"failed to load {name}: {exc}")], ["C0"]`, inside the three-registry loop at `:779-783`. The second element is the `checks_run` list, and it correctly contains only `"C0"`.

The finding is careful in the way this pass wants findings to be careful: it states that `checks_run` **is** accurate, and rests the defect entirely on a consumer that reads only the findings list seeing one critical entry with no signal that C1-C7 never ran. That is a real ergonomics-of-evidence defect and not a correctness one, which is what its `Confidence: medium` and P2 band encode.

Disposition: **CONFIRMED**. Files changed: none.

### F035 [P2] — CONFIRMED, the 147 reproduces exactly, and the blast radius is **narrowed**

- `grep -n 'except Exception' check_skill_bundle.py` → **one hit, `:329`**. The `try:` that it closes opens at `:182`. `329 − 182 = 147`. The report's "147-line body" is exact and derived, not estimated.
- The handler body is `errors.append(f"Failed to perform consistency validation on JSON registries: {exc}")` — it appends rather than swallows, so the finding's concession that it fails closed (crediting S3b-10-11) is correct.

**Narrowing.** The finding's plausible failure mode says *"One malformed skill card masks every other bundle defect until it is fixed."* The handler covers section 3 only. Section 4 — the local-Markdown-link check at `:334-336`, `for p in REF_DIR.rglob("*.md")` — runs afterwards regardless, and sections 1 and 2 have already run before `:182`. So the masking is real and bounded to the registry-consistency block: one exception there ends *that* section's remaining checks, not the program's.

That does not rescue the defect. Section 3 is the section that reads every registry and every skill card and cross-checks the emit identifiers, so it is where most of the instrument's actual measurement lives, and the failure mode within it is exactly as described: one round-trip per defect.

Disposition: **CONFIRMED-narrowed** — the collapse is confirmed at `check_skill_bundle.py:182-329`; the masking is scoped to that block rather than to the whole bundle check. Files changed: none.

### F036 [P2] — CONFIRMED, pointer exact

`beo_run.py:82-83` — `if ticket.get("mode", "quick") != "quick":` / `print(f"WARNING: mode is '{ticket.get('mode')}', not 'quick'. Proceeding anyway.", file=sys.stderr)`. No `_die`, no state field, no runtime event. The next statement is the state initialisation at `:86`.

This is the reachability premise F008 depends on, stated as a finding in its own right, and it is the correct place for it: the defect is not that strict mode is unimplemented on this path but that the path **announces** the mismatch and proceeds anyway, leaving a record whose `mode` field says `strict` while none of strict mode's gates were applied. The finding's remediation is one line and closes the reachability half of F008 with it, as it claims.

Disposition: **CONFIRMED**. Files changed: none.

### F037 [P2] — CONFIRMED, **broadened**: there are two ticket-supplied command sites before the transition, not one loop

`sed -n '132,178p' beo_run.py` reproduces the ordering exactly:

- The verify loop is `:140-147` — `run_one_command(cmd, root, None)` at `:141`, once per entry of `ticket["scope"]["verify"]["commands"]` read at `:136`.
- `beo_state.locked_update_state(root, issue_id, "beo-execute", _start_exec)` is at `:173`; `_start_exec` sets `state["phase"] = "executing"` at `:167`.
- `beo_state.py:589-590` — `if after.get("phase") != "executing": raise ValueError("beo-execute must durably enter executing state before product mutation")`. The invariant is quoted correctly, and it is enforced only against the `after` of a `beo-execute` write, so it constrains the record and not the tree.

**Broadened.** Between the verify loop and the transition sits a second ticket-supplied command: `behaviour_gate_command(ticket)` at `:150`, run at `:152` through the same `run_one_command`. It is a separate call site with the same trust origin and the same mutation capability, and the finding's range (`:140-161`) covers it only by accident of line numbers. Remediation therefore has to move the transition above `:140`, not merely above the loop.

**Narrowed in one direction, which sharpens the failure mode.** `:162-163` — `if not all_ok: _die("verification command(s) failed — bead left in approved state for repair", code=2)`. A *failing* command never reaches `:173`, so the exposed case is not the crash the finding leads with but the quieter one: a command that **mutates the tree and exits 0**. That run proceeds to `:173`, and the durable record then claims the mutation began at `:169`'s `started_at`, after it actually happened. The finding's own parenthetical — "a formatter, a code generator, a test that snapshots" — is exactly the exit-0 mutator, so the substance is right and only the leading failure narrative is off.

Disposition: **CONFIRMED-broadened**. Files changed: none.

### F038 [P2] — CONFIRMED, and **strengthened**: `phase` is the *only* major field in `validate_state` with no cross-field invariant

`validate_state` is `beo_state.py:239` through `:393`. Read whole, the finding's premise is understated. The function is not missing a cross-field layer — it has a dense one:

- `:342-343` — `finding.severity in {"blocker","major"}` forbids `recommended_route == "none"`.
- `:379-384` — `verdict` determines the required `route_condition_id` through `pipeline.json`'s `review_route_mapping.verdict_to_condition`.
- `:386-387` — a null `verdict` restricts `route_condition_id` to `null_verdict_conditions` or `None`.
- `:389-393` — `route_condition_id == "verdict_accept"` is required for, and required by, `closed_in_br == True`.

Against that, `grep -n 'phase' beo_state.py` filtered to `:239-400` returns **8 lines in five places**, and not one of them relates `phase` to another field: `:240` puts it in `required`, `:249-250` checks it against `PHASES`, `:251-252` range-checks `phase_sequence_id`, `:257` lists `approved_phase_sequence_id` as an approval field, `:276-278` range-checks that. `approval.approved_phase_sequence_id` is never compared to `state.phase_sequence_id` either, though its name asserts the relation.

So the finding is right that `phase: "approved"` with `approval.status: null` validates, and right that F002's false record survives because of it. What it does not say is the sharper thing: **the single field the whole lifecycle turns on is the one field the validator declines to constrain**, in a function that constrains `verdict`, `route_condition_id`, `closed_in_br`, `severity` and `recommended_route` against each other and against a registry. Its durable solution — "driven by the same registry data F006 proposes to wire in" — is not a new mechanism to build; `:370-375` already loads `pipeline.json` inside this function. The transitions it loads there carry `from`/`to` phases, which is the data a `phase`↔`approval.status` predicate would need.

Disposition: **CONFIRMED-strengthened**. Files changed: none.

### F039 [P2] — **CONFIRMED-narrowed and redirected.** The route-condition set is not hardcoded; it is derived from a *different* registry, which is a distinct defect from the one alleged

Enumerated statically with `python3 -c "import json; ..."` over `registry/state.schema.json`, walking every `enum` key: the schema declares **12** enums — `phase`, `approval.status`, `approval.failure_category`, `execution.trace_tier`, `review.verdict`, `review.route_condition_id`, `review.findings[].severity`, `.category`, `.recommended_route`, `review.done_criteria_coverage[].status`, `review.reviewed_by`, and `review.cross_check.verdict`.

**The finding's first clause holds.** Exactly one is loaded from the schema: `_approval_failure_categories()` at `beo_state.py:228-235`, called at `:272`, via `_load_state_schema()` at `:217-225`. That is the only use of the schema in the module.

**The finding's second clause does not.** It lists "the route-condition set" among the Python literals. It is not one. `beo_state.py:370-375` reads `pipeline = _load_pipeline()` and builds `valid_conditions = {t["condition_id"] for t in pipeline.get("transitions", [])} | {None}`. The set is derived — from `registry/pipeline.json`, a *second* registry, which declares its own authority over the same field the schema declares an enum for. The Python literals are `PHASES` (`:155`), `APPROVAL_STATUSES` (`:156`), `REVIEW_VERDICTS` (`:157`), `REVIEW_FINDING_SEVERITIES` (`:158`), `REVIEW_FINDING_CATEGORIES` (`:159`), `REVIEW_FINDING_ROUTES` (`:160`), plus five inline sets — `trace_tier` at `:288`, intervention `type` at `:305`, intervention `impact` at `:308`, `reviewed_by` at `:322`, coverage `status` at `:355`. Eleven literals, not four.

**The three figures reconcile, and the reconciliation is where a twelfth enum goes missing.** Twelve schema
enums are not one schema-derived plus one pipeline-derived plus eleven literals; the sets overlap and one is
empty. Nine of the eleven literals each stand opposite a declared schema enum (`phase`, `approval.status`,
`review.verdict`, `severity`, `category`, `recommended_route`, `trace_tier`, `reviewed_by`, coverage `status`).
Two do not: the intervention `type` set at `:305` and the intervention `impact` set at `:308` validate fields
for which `state.schema.json` declares no enum at all, so those two are writer-only authorities. That accounts
for eleven of the twelve schema enums — nine literal, one schema-derived (`approval.failure_category`), one
pipeline-derived (`review.route_condition_id`). The twelfth, `review.cross_check.verdict`, has **no**
enforcement in `beo_state.py` in any form, because `_reject_unknown_fields` throws out the parent object before
the enum could ever be reached. That is F001, arrived at from the counting side.

**The drift is latent, not live — derived, and the disconfirming direction is stated because it matters.** Comparing the two registries: `pipeline.json` yields 17 distinct `condition_id`s, the schema enum has 9, and the schema's 9 are a subset — so `:376`'s membership test is looser than the schema by 8 values. Those 8 are **not** reachable, and this row says so rather than claiming a hole it did not verify: `:379-384` pins `route_condition_id` to `verdict_to_condition[verdict]` when a verdict is present (5 values, all in the schema), and `:386-387` pins it to `null_verdict_conditions` when it is absent (4 values, all in the schema, checked by set difference against the schema enum → empty). The reachable set today is exactly the schema's 9 plus `None`. What is defective is that this agreement is a coincidence of two registries nothing compares: adding a transition to `pipeline.json` whose `condition_id` also lands in `null_verdict_conditions` widens `validate_state` past `state.schema.json` with no diagnostic anywhere.

**Redirected failure mode.** The finding's plausible-failure narrative — "adding a phase to `state.schema.json` has no effect on the writer" — is correct for the 11 literals. For `route_condition_id` the exposure runs the other way: the schema is the field that has no effect on the writer, because the writer answers to `pipeline.json`. And the bundle already carries the realised form of this defect class: F001's `review.cross_check` is schema-declared and writer-rejected, which this pass re-derived independently — `beo_state.py:259`'s `review_fields` omits it, `:316` calls `_reject_unknown_fields`, and `validate_state` runs on all three durable paths (`read_state` `:122`, `initialize_state` `:148`, `locked_update_state` `:610`), so a state carrying the field can be neither written nor read back.

Disposition: **CONFIRMED-narrowed** — one of twelve enums is schema-derived, as alleged; the route-condition set is registry-derived rather than hardcoded, and its defect is an uncompared second authority, not a literal. Files changed: none.

### F040 [P2] — CONFIRMED, with the defect line corrected

`sed -n '83,100p' beo_worktree.py`:

- `:83` `def ensure_beads_symlink(root: Path, wt_path: Path) -> None:`; `:84` the docstring's first line, *"Symlink worktree's .beads to main repo's .beads. Raises on failure."*; `:88-89` *"A silent fallback that lets the worktree have an isolated .beads directory breaks the entire pipeline."* Both quoted correctly.
- `:91` `main_beads = (root / ".beads").resolve()`.
- **`:97-98` is the defect**: `if not main_beads.exists(): return`. The report's source pointer names `:91`, which is the computation, not the silent exit. The function does raise on the adjacent case — `:93-96`, `.beads` exists but is not a directory — which is what makes the absent case a considered omission rather than an oversight.

**Compound worth recording.** `ensure_beads_symlink` is called at `:162`, inside `cmd_create`'s existing-worktree fast path (F044's subject), immediately before that path prints `"status": "exists"` and returns 0 at `:164-170`. So the silent return and the optimistic fast path are on the same line of control: a worktree can be reported healthy and reused while its `.beads` is isolated.

Disposition: **CONFIRMED**, source pointer redirected from `:91` to `:97-98`. Files changed: none.

### F041 [P2] — CONFIRMED, and **broadened**: the TOCTOU is at two sites, and one `AGENTS.md` path is read-modify-write, not merely non-atomic

`grep -n 'write_text' skills/beo/beo-reference/scripts/*.py | wc -l` → **5 hits**, and they are the five the finding names: `beo_propose.py:201`, `beo_ticket.py:299`, `beo_setup.py:100`, `:108`, `:114`.

Each leg re-derived:

- `beo_ticket.py:294-299` — `path.parent.mkdir(...)`, then `:296` `if path.exists() and not overwrite: raise FileExistsError`, then `:299` `path.write_text(json_content, ...)`. Bare write in a module whose sibling `beo_state.py` uses lock, temp-and-rename and fsync (`atomic_write_json`, `:93-111`). Confirmed.
- `beo_setup.py:100` writes the template over a missing `AGENTS.md`; `:104-108` **reads** `AGENTS.md`, splices between `MANAGED_START`/`MANAGED_END` found by `content.index` at `:105-106`, and writes the result; `:112-114` reads and appends. Confirmed.
- `beo_propose.py:194-201` — `if target.exists(): skipped...; continue` at `:194-196`, `target.write_text(body, ...)` at `:201`, with `_build_proposal` and the `--dry-run` branch in between at `:197-200`. The window is wider than a bare check-then-write. Confirmed.
- `beo_memory_write.py:226-229` — `if path.exists(): raise` then `with path.open("x", ...)`. The finding is right that this is the correct pattern; precisely, `"x"` at `:228` is the guard and `:226` is only a better error message. Confirmed as the in-bundle precedent.
- `beo_propose.py:28` — `PROPOSAL_DIR = os.environ.get("BEO_PROPOSAL_DIR", "skills/beo/beo-author/proposals/pending")` at module scope; `:33-34` `def _proposal_dir(root): return root / PROPOSAL_DIR`. Both exact. `pathlib`'s `/` discards the left operand when the right is absolute, so an absolute `BEO_PROPOSAL_DIR` escapes `root` — asserted as a documented `pathlib` semantic, not by running the code, which this pass may not do.

**Broadened, two ways.** First, `beo_ticket.py:296-299` is the *same* TOCTOU shape as `beo_propose.py:194-201` — existence probe, then unguarded write — and the finding attributes the TOCTOU only to `beo_propose.py`. `TICKET.json` is the higher-value target of the two, since it is the object `approval.ticket_file_hash` binds. Second, `beo_setup.py:104-108` and `:112-114` are not merely non-atomic writes: they are read-modify-write cycles over a file the finding itself identifies as human-owned, so a concurrent human edit is not truncated but **silently discarded in full**. `:105-106`'s `content.index` also raises an uncaught `ValueError` if the markers are gone between the status probe and the splice.

Disposition: **CONFIRMED-broadened** — five write sites as found, plus a second TOCTOU site at `beo_ticket.py:296-299` and a lost-update (not truncation) failure mode at `beo_setup.py:104-114`. Files changed: none.

### F042 [P2] — CONFIRMED, source pointer corrected on both sides

`grep -n 'validate_working_tree_prestate' skills/beo/beo-reference/scripts/*.py` → 4 hits: the definition at `beo_check.py:146`, the import at `beo_run.py:37`, and **two call sites**:

- `beo_check.py:550` — `errors.extend(validate_working_tree_prestate(root, ticket, []))`. Empty allowlist, as found. The report gives `:549`; that line is `run_structural_check`.
- `beo_run.py:103` — `prestate_errors = validate_working_tree_prestate(root, ticket, recorded_changed_files)`. The report gives `:106`. `:106` is a **different mechanism**: `unexpected = sorted(path for path in current_changed_files if path not in recorded_changed_files)`, the advisory comparison that F028 disposes. The two are adjacent and do different things — `:103-105` `_die`s on the predicate's errors, `:106-109` only prints a warning — so citing `:106` for this finding attaches the divergence claim to the wrong half of the block.

The substance survives both corrections intact: the same predicate is given `[]` on the check path and a ticket-derived list on the run path, so `beo_check.py` refuses trees `beo_run.py` accepts, and `recorded_changed_files` originates in the ticket, which is the lower-trust source of the two.

Disposition: **CONFIRMED**, pointers corrected to `beo_check.py:550` and `beo_run.py:103`. Files changed: none.

### F043 [P2] — CONFIRMED, and **broadened**: the sentinel poisons the projection hash as well as the stored field, from two call sites

`sed -n '45,52p' beo_io.py` — `repo_head_sentinel` returns `"git:unavailable"` at `:49` when `subprocess.run` raises `FileNotFoundError`, and `"git:no-head"` at `:51` when `git rev-parse HEAD` exits non-zero. Two sentinels, both plain strings, both indistinguishable at every consumer from a real object name. Confirmed.

**Broadened.** `grep -rn 'repo_head' *.py` gives two call sites, not one:

- `beo_run.py:93` → `:97` into `approval_projection_hash(...)` and `:123` into the stored `approval.repo_head`. This is the site the finding names.
- `beo_check.py:265` → `:269` into `compute_approval_fields`'s returned `repo_head` and `:270` into `approval_projection_hash(ticket, ticket_file_hash=..., repo_head=repo_head, reservation_evidence=...)`.

So the sentinel does not merely occupy the `repo_head` field; it is **hashed into `approval_projection_hash`**, which is the value `validate_approval_envelope` re-derives to detect staleness. In a git-less environment both the stored hash and the re-derived hash are computed over the same constant, so the comparison passes for the same reason the field comparison does. The finding's plausible failure mode — "the staleness check passes unconditionally" — is therefore correct twice over, and the remediation (raise) is the only one that works, because no consumer-side check can distinguish the sentinel from a commit it has never seen.

`beo_state.py:267` runs `_validate_optional_string` over `approval.repo_head`; a sentinel is a string, so validation is no backstop.

Disposition: **CONFIRMED-broadened**. Files changed: none.

### F044 [P2] — CONFIRMED, with the branch boundaries corrected

`sed -n '150,175p' beo_worktree.py`:

- The fast path is the `else:` branch at **`:161-170`**, not `:162-169`: `ensure_beads_symlink(root, wt_path)` at `:162`, `result = run_git(["rev-parse", existing], cwd=root)` at `:163`, and `print(...); return 0` at `:164-170` emitting `"status": "exists"`.
- The recovery path the finding calls correct is `:150-160`, not `:156-160`: `:150-151` unlinks a stale path, `:152-155` runs `git worktree prune`, and `:156-160`'s comment explains the branch reuse.

The claim reproduces exactly. `run_git(["rev-parse", existing])` resolves a **branch ref in the main repository**; it says nothing about the state of `wt_path`'s checkout, and `ensure_beads_symlink` — per F040 — returns silently rather than raising when `root/.beads` is absent. Neither call touches a file inside the worktree. So "registered and resolvable" is, as the finding says, weaker than "checked out", and the fast path's two prerequisites are both satisfiable by a worktree `git worktree add` never finished writing.

The proposed remediation (`git -C <wt> status --porcelain`, or `git diff --quiet HEAD`) is the first command in the branch that would read the worktree at all.

Disposition: **CONFIRMED**, branch boundaries corrected to `:161-170` and `:150-160`. Files changed: none.

### F045 [P2] — **NOT CONFIRMED.** The manifest's own exit-code row for this script says `0, 1`, and the finding never cites it

The code leg is exact. `beo_audit.py:833` — `return 1 if any(f.severity == SEVERITY_CRITICAL for f in findings) else 0`, with `raise SystemExit(main())` at `:837`. The contract leg does not survive.

The manifest is `skills/beo/beo-reference/references/command-manifest.md` (the finding cites it as `command-manifest.md`; there is no such file at the bundle root — `find skills/beo -name 'command-manifest*'` returns exactly one path, under `references/`).

- **`:12`** states the bundle's exit-code contract: *"`exit code` follows the BEO contract: `0` success, `1` validation/business failure, `2` refusal/refuse-state."*
- **`:19`**, the manifest table's row for this script: `| beo_audit.py | [--check-manifest] [--root .] [--learning-repo PATH] [--json] | Audit | markdown or json | 0, 1 |`.

`0, 1` is exactly what `:833` returns, and `1` is exactly the "validation/business failure" the contract at `:12` assigns to that code. **The manifest's normative statement about this script's exit codes agrees with the code.**

The finding's evidence rests instead on `:47` — *"**Audit**: drift checks (C1–C10), proposal generation (advisory)"* — quoted in the report as `"Audit... (advisory)"`. The ellipsis removes the text that fixes the parenthetical's scope. `:38-47` is a legend for the table's **Responsibility** column, not an exit-code classification: `:38` "**Validation**: checks tickets, state, approval, identity, scope", `:42` "**Isolation**: git worktree lifecycle", and so on. `:47`'s line names two activities and the parenthetical follows the second, `proposal generation` — which is `beo_propose.py`'s output, and `beo_propose.py` has its own row at `:24`. The neighbouring `:46` — "**Verification**: runs TICKET.json scope verify commands (machine-enforced)" — shows what the advisory/machine-enforced pair in this block distinguishes: whether a helper's output binds a human reader, not what number it returns.

Even on the report's own reading, where "(advisory)" scopes the whole Audit line, it is a one-word gloss in a prose legend set against an explicit numeric row for the same script two dozen lines above it. There is no contradiction to resolve, and the finding's remediation — "decide which it is and make the manifest and the exit code agree" — asks for a change to a manifest that already agrees.

What remains, and is not this finding, is the question S3b-10-19 raises generally: whether *any* bundle helper's exit code should gate CI. That is a design question about the contract at `:12`, not a drift between two documents.

Disposition: **NOT CONFIRMED**. Files changed: none.

### F046 [P3] — CONFIRMED exactly, on both scripts and both documents

- `beo_score_trace.py:314` — `def main() -> int:`. `grep -n 'return' ` over `:314-339` returns one hit, `:335` `return 0`. `:339` is `raise SystemExit(main())`.
- `beo_score_context.py:242` — `def main() -> int:`; its only return is `:263` `return 0`; `:267` is `raise SystemExit(main())`.
- The manifest is `references/command-manifest.md`: `:27` gives `beo_score_context.py` exit codes `0, 1`, `:28` gives `beo_score_trace.py` exit codes `0, 1`. `:12` defines `1` as "validation/business failure".

Both halves reproduce. The finding's cross-reference to F031 is the correct one here (unlike F031's own reference to F032 — see that row): with no failure exit and, in `beo_score_trace.py`, no in-band report of a synthesised state, the trace scorer has no channel of any kind for "this bead does not exist".

One refinement to the remediation. The finding offers "implement the documented failure exit, or correct the manifest to `0`". Correcting the manifest to `0` is not free: `:12`'s contract assigns meanings to `0/1/2`, so a helper documented as only ever returning `0` is documenting that it is unconditionally advisory — which is the design question F045 was reaching for and did not find. The two scorers are the one place in the bundle where "always exit 0" is defensible, and saying so explicitly in the manifest is a better outcome than inventing a failure code to satisfy a table.

Disposition: **CONFIRMED**. Files changed: none.

### F047 [P3] — **SPLIT.** `compact_text` is dead repo-wide; `write_ticket` has 17 call expressions in `tests/`, and the finding's own disconfirming check is the one that finds them

The finding's evidence line is scoped to the bundle: *"`grep -rn 'write_ticket\|compact_text' skills/beo/beo-reference/scripts/*.py` shows the two definitions and no call sites in the 17-file bundle."* Re-derived, that is true. Its **disconfirming check** says *"the grep above, extended to the whole repo."* Extended:

`git grep -n 'write_ticket\|compact_text'` over the repository, excluding `docs/ultrareview/`:

- `compact_text` — `git grep -n 'compact_text' -- skills/beo/beo-reference/` → **1 line**, the definition at
`beo_io.py:21`. Widened to `grep -rn 'compact_text' --include='*.py' .` over the whole checkout: the same single
line. Dead repo-wide. **CONFIRMED.**
- `write_ticket` — the definition at `beo_ticket.py:290`, plus `grep -rn 'write_ticket' tests/` → **21 lines**
across three modules, which are not 21 call sites and are enumerated here by role rather than counted by line:
  - **3 imports**: `tests/test_score_trace.py:22`, `tests/test_verify_command.py:22`, and
    `tests/test_verify_command.py:256` (`from beo_ticket import write_ticket as _write_ticket`).
  - **1 local wrapper `def`**: `tests/test_verify_command.py:21` defines a *test-local* `write_ticket` that shadows
    the imported name at module scope and calls the real one at `:35`.
  - **17 call expressions**: `tests/test_helper_semantics.py` at `:85`, `:87`, `:98`, `:101`, `:667`, `:725`,
    `:737`, `:778`, `:1436` (9, all `beo_ticket.write_ticket(...)`); `tests/test_score_trace.py:75` (1);
    `tests/test_verify_command.py` at `:35`, `:110`, `:131`, `:156`, `:223`, `:237`, `:305` (7).
  - Of those 17, **12 reach `beo_ticket.write_ticket` directly** (the 9 in `test_helper_semantics.py`, plus
    `test_score_trace.py:75`, `test_verify_command.py:35` and `:305`) and **5 reach it through the local wrapper**
    (`test_verify_command.py:110`, `:131`, `:156`, `:223`, `:237`).

Either way the function has live callers in three modules and deleting it breaks all three. **NOT CONFIRMED.**

`beo_ticket.write_ticket` is not dead code. It is the function the repository's own test suite uses to construct `TICKET.json` fixtures, and it is the most-called helper in that suite's setup path.

**This is the slice's coverage defect producing a wrong finding, exactly as predicted.** `tests/` is 4094 lines of the declared slice that `S3B-BRIEF.md:7` never briefed — the defect this record declared before its first row. The scouts could not see these callers because the brief did not put them in scope; the report then filed a P3 whose disconfirming check would have caught it, and that check was not run, for the same reason. This is the fail-open pattern already catalogued in this pass (RX01, F003, F065/F081 in S3a): a disconfirming check narrower than the claim returns clean and retires nothing, while the finding it should have retired proceeds.

**The remediation is actively harmful as written.** The finding's Note reads *"`write_ticket` is also the non-atomic writer named in F041. Deleting it closes both, and is the pre-launch-correct move unless a caller outside the bundle exists."* A caller outside the bundle exists, twenty times over. Deleting `write_ticket` breaks three test modules. F041's disposition of the same function stands unchanged and is now the only correct route: fix the write, do not delete the function.

Disposition: **split — CONFIRMED for `beo_io.compact_text` (dead repo-wide), NOT CONFIRMED for `beo_ticket.write_ticket` (17 call expressions in `tests/`, across three modules)**. Files changed: none.

### F048 [P3] — CONFIRMED, and **strengthened**: `beo_verify.py` is the only one of five that drops it, and it is the one whose events are gate evidence

`git grep -n 'HELPER_VERSION' -- skills/beo/beo-reference/` → **10 hits across 5 files**:

| script | defined | emitted |
| --- | --- | --- |
| `beo_audit.py` | `:23` | `:744` (markdown), `:766` (json) |
| `beo_check.py` | `:29` | `:520` |
| `beo_score_context.py` | `:21` | `:214` |
| `beo_score_trace.py` | `:22` | `:286` |
| `beo_verify.py` | `:32` | **nowhere** |

The finding is exactly right and its scope is exactly right: `beo_verify.py:32` is the single defective instance. What it does not say is that the surrounding four make it an omission rather than a choice — four siblings emit the constant into their output dict under the same key name, one of them twice, so the pattern is established and `beo_verify.py` simply does not follow it.

**Strengthened by which script it is.** Per F057's subject matter, `beo_verify.py`'s output is the evidence a verification actually ran, and per `beo_run.py`'s use of `verify_results` it is written into `state.json` durably. It is the one output in the bundle where "which helper version produced this record" is a question an auditor will later need answered, and it is the one output that cannot answer it. The finding's own sentence — "A version constant that never reaches a record cannot version anything" — understates itself: here the record it fails to reach is the durable one.

Disposition: **CONFIRMED-strengthened**. Files changed: none.

### F049 [P3] — CONFIRMED on both halves, and the second half is deader than stated

**`beo_reservation.parse_iso`.** `sed -n '28,36p' beo_reservation.py`:

- `:20-21` — `RESERVATION_ID_PATTERN` and `UTC_TIMESTAMP_PATTERN = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}Z$")`.
- `:32-34` — `parse_iso` tries `datetime.strptime(ts, "%Y-%m-%dT%H:%M:%SZ")`. **That format string accepts exactly the language `UTC_TIMESTAMP_PATTERN` accepts.**
- `:35-36` — `except Exception: return datetime.fromisoformat(ts.replace("Z", "+00:00"))`. The fallback.

`grep -n 'parse_iso'` gives three call sites, and each is immediately preceded by the guard: `:96-98` (`fullmatch` then `parse_iso(record["created_at"])`), `:107-109`, `:135-137`. All three are `fullmatch`-guarded on the same pattern, and `:107`/`:135` additionally `isinstance`-check for `str` first, which closes the `TypeError` route into the handler. The fallback at `:36` is unreachable from every caller. **Confirmed.**

**`beo_audit.get_check_ids`.** `sed -n '40,51p' beo_audit.py` — `:46-50` `try: path = Path(__file__).resolve(); source = path.read_text(...)` / `except Exception: return frozenset()`. The finding calls it "a fail-open that no current call path can reach". Derived, it is stronger than that: `git grep -n 'get_check_ids'` over the repository returns **one hit, the definition at `:40`**. There is no call path at all — not in `scripts/`, not in `tests/`. The function is dead, and the fail-open inside it is dead twice over.

The finding's own warning stands and is the reason this is P3 rather than noise: *"if a future caller reaches it, an empty check-id set silently disables checks."* Given that the docstring at `:43-45` advertises the function as the mechanism by which *"adding a new check_\* function ... automatically includes its ID without manual registration"*, a future caller is not hypothetical — it is what the docstring invites.

Disposition: **CONFIRMED**, with `get_check_ids` re-derived as fully uncalled rather than merely unreachable-in-the-handler. Files changed: none.

### F050 [P3] — **CONFIRMED-narrowed, and the narrowing inverts the remediation.** Both fields have consumers; what they lack is a producer

`git grep -n 'interventions\|trace_tier' -- skills/beo/beo-reference/scripts/` → 18 hits. Sorted by role:

**Producer side — the finding holds.** `beo_state.py:46-47` sets `"trace_tier": None` and `"interventions": []` in `initial_state`, and no other assignment to either field exists in the 17 scripts. `:258` lists both in `execution_fields`; `:285-289` validates `trace_tier` against `{"minimal","standard","detailed"}`; `:295-313` validates `interventions` structurally, element by element, down to `type`, `impact` and three required non-empty strings. Nineteen lines of validator for two fields nothing writes. **Confirmed.**

**Consumer side — the finding does not hold.** The claim is "no writer and no decision that reads either." Both are read, at three sites, and all three feed decisions:

- `beo_score_trace.py:59` and `beo_score_context.py:33` — `tier = (state.get("execution") or {}).get("trace_tier")`, the first statement of `resolve_tier` in each file. The tier it returns selects `MIN_REQUIRES[tier]` (`beo_score_context.py:156`) and the required-field set (`beo_score_trace.py`'s `_required_for_tier`), which is what the score is computed against.
- `beo_score_trace.py:108` — `for item in (execution.get("interventions") or [])`, feeding the narrative-evidence component the docstring names at `:94`.

**Why the narrowing matters more than the finding.** A field with no producer *and* no consumer is inert, which is the F006/F007 class the finding assigns it to, and "prefer delete pre-launch" is right for that class. A field with a consumer and no producer is not inert — it is a **scorer reading a constant**. `trace_tier` is `None` in every state the bundle has ever written, so `resolve_tier` always falls past `:60-61` to the ticket mode, and to `"standard"` when there is no ticket. `interventions` is `[]` in every state, so that component of the trace score is structurally zero and always has been. The scores the two advisory helpers produce are therefore computed against a tier the state never chose and an evidence list that is always empty.

That connects to F031's addition in this record: `"standard"` is one of the two tiers where `beo_score_context.py`'s `state_loaded` key reports `True` on an absent state. The unwritten field routes the scorer into the branch whose report is wrong.

Remediation inverts accordingly: deleting the fields would delete a live scoring input and silently change both scorers' output. Either wire a producer — `beo_run.py`'s `_start_exec` at `:166-171` already writes three sibling `execution` fields and is the obvious site for `trace_tier` — or delete the fields **and** the scorer branches that read them, together, in one change.

Disposition: **CONFIRMED-narrowed** — no producer, as found; two consumers across three sites, contrary to the finding; remediation redirected from "delete" to "wire a producer, or delete field and consumer together". Files changed: none.

### F051 [P3] — CONFIRMED exactly

`beo_memory_write.py:9` — `from datetime import date`. `:45` — `return f"{date.today().isoformat()}--{case_type.replace('_', '-')}--{issue_id}--{slug}.md"`. `date.today()` reads the local timezone; `grep -n 'now()'` over the file returns nothing, so the module does not import the bundle's UTC `now()` at all. Both legs exact.

The finding's own bound on the blast radius is the right one and is worth preserving in the ranking: the value lands in a **filename**, and no code in scope sorts or tie-breaks on it. So this is a naming-consistency defect against a bundle whose every other timestamp is UTC, not a correctness defect in any decision. Its remediation is one line.

Disposition: **CONFIRMED**. Files changed: none.

### F052 [P3] — CONFIRMED, with the probability restated and one consequence the finding does not name

`beo_reservation.py:265` — `res_id = f"res-{hashlib.sha1(os.urandom(8)).hexdigest()[:8]}"`. Eight hex characters, 32 bits of retained entropy. Exact.

**The arithmetic, redone.** The 50% bound is √(2·ln2·2³²) ≈ 77,100 — the finding's "near 77,000" is right. Its second clause, "at a few thousand the probability is already percent-scale", is generous: 1 − exp(−n²/2N) gives ≈0.10% at n = 3,000 and ≈1.2% at n = 10,000. Percent-scale arrives at ten thousand, not a few thousand. The finding's conclusion is unaffected — a delivery harness accumulating reservations over a project's life reaches ten thousand — but the row records the correction because a stated number that was not derived is the defect class this campaign is auditing.

**Consequence the finding does not name.** `:266-269` — on minting a new id the writer walks existing records and sets `r["superseded_by"] = res_id` on each active same-issue lease. A collision therefore does not merely duplicate an identifier; it **mis-links the supersession chain**, pointing an old lease at an unrelated reservation. `:118` validates `superseded_by` against `RESERVATION_ID_PATTERN` only, so a wrong-but-well-formed link passes validation.

**Two notes on the remediation.** The finding's preferred fix — check inside the lock the writer already holds and regenerate — is correct and is free, since `:265` runs under `get_lock` (`:39-48`). Its fallback, widening to 16 chars, additionally requires editing `RESERVATION_ID_PATTERN` at `:20`, which pins the width at `{8}`; the finding does not mention that the pattern would have to move too. Separately, `hashlib.sha1(os.urandom(8))` hashes 64 bits of uniform randomness and truncates to 32: the SHA-1 contributes nothing, and `os.urandom(4).hex()` is identical in strength and honest about the width.

Disposition: **CONFIRMED**. Files changed: none.

### F053 [P3] — CONFIRMED exactly

`sed -n '110,126p' check_skill_bundle.py`:

- `:111` — `# Check length limit (500 non-frontmatter lines)`.
- `:124` — `if len(non_frontmatter_lines) > 250:`.
- `:125` — the message reads `f"Skill card exceeds 250 non-frontmatter lines: ..."`.

Code and message agree on 250; the comment alone says 500. The finding's reasoning for which one to change — two against one — is the correct call.

Disposition: **CONFIRMED**. Files changed: none.

### F054 [P3] — **CONFIRMED-narrowed.** Three of five legs reproduce, one is contradicted by the file it cites, and one names nothing checkable

This is a bundle finding; each leg is disposed separately.

**Leg 1 — `beo_propose.py --dry-run` undocumented. CONFIRMED.** `grep -n 'dry.run\|dry_run' beo_propose.py` → `:153` `parser.add_argument("--dry-run", action="store_true", help="Print summary without writing files")`, used at `:188` and `:198`. The manifest's row for the script, `command-manifest.md:24`, reads `| beo_propose.py | [--root .] | Audit | json | 0, 1 |`. The flag exists, changes behaviour, and is absent from the manifest.

**Leg 2 — C5 compares names only. CONFIRMED.** `grep -n 'C5' beo_audit.py` gives the check's whole surface. Its only two substantive `Finding` calls are `:512` — *"script '{script}' exists in scripts/ but is {label}"* — and `:514` — *"command-manifest.md references '{script}' but no such script exists"*. Both are set operations over filenames in two directions. Nothing in the check opens an argparse surface or reads an exit code, which is why Leg 1 and Leg 3 are invisible to it. The finding's reading — "the instrument measures presence, not accuracy", F032's class — is exact.

**Leg 3 — `beo-setup/SKILL.md` mode vocabulary. CONFIRMED, and sharper than filed.** `beo-setup/SKILL.md:13-18` declares a `## Setup modes` section with four modes: `check` ("read-only readiness report; default mode"), `configure-memory`, `configure-agents`, `explain-degraded`. `grep -n 'add_argument' beo_setup.py` returns four: `--configure-memory` (`:124`), `--refresh-memory-index` (`:125`), `--install-agents` (`:126`), `--root` (`:127`). The mismatch is not a vocabulary drift between two names for one thing — **`beo_setup.py` has no mode concept at all.** It has independent boolean flags. Two of the card's four modes have no flag of any name (`check`, `explain-degraded`), one is renamed (`configure-agents` → `--install-agents`), one flag is undeclared by the card (`--refresh-memory-index`), and the card's "default mode" describes behaviour the CLI expresses as the absence of every flag.

**Leg 4 — `context-budget.md` telling readers to use `--help` on five library-only scripts. NOT CONFIRMED.** The file is `references/context-budget.md`. `grep -n -- '--help'` over it returns **two hits**: `:50`, a table cell reading `` `beo_check.py --help` ``, and `:64`, the bullet *"Full `beo-reference/scripts/` source (use `--help` or summary instead)"*, which names no script. `beo_check.py` has a CLI — `--check`, `--issue`, `--root` — so `:50` is correct advice. The other scripts appearing in the same tables (`beo_run.py:42`, `beo_state.py:43`, `beo_worktree.py:44`, `beo_check.py:51`, `beo_reservation.py:52`) are plain file references carrying no `--help` instruction. There is no instruction to run `--help` on a library-only script anywhere in the file. What `:64` does do is tell readers not to load the scripts, which — given `:50` is the only concrete alternative offered — is thin, but it is not the defect filed.

**Leg 5 — "an unused parameter and an unused import remain in scope". UNVERIFIABLE AS FILED.** The finding names neither the parameter, nor the import, nor the file, and delegates to a candidate id whose text is not reproduced in the report. A receive pass cannot confirm a claim that identifies no location. Recorded as owed work for a Phase B pass that has the candidate file open, not as a confirmed defect.

Disposition: **CONFIRMED-narrowed** — legs 1, 2 and 3 confirmed (leg 3 strengthened); leg 4 not confirmed; leg 5 unverifiable as filed. Files changed: none.

### F055 [P3] — CONFIRMED, with the duplication leg proved rather than asserted

Also a bundle finding; the legs that carry independent weight:

**Scorer duplication. CONFIRMED, and now mechanically.** The finding asserts "copy-pasted logic". Derived with `python3 -c "import ast; ..."` comparing top-level definitions between the two files: they share five top-level names — `HELPER_VERSION`, `MODE_TO_TIER`, `resolve_tier`, `append_score_event`, `main`. Comparing `ast.dump` of each: **`resolve_tier` is AST-identical between the two files, and so is `MODE_TO_TIER`.** `append_score_event` differs only in its event payload and the noun in its warning string (`beo_score_trace.py:306-311` against `beo_score_context.py:234-239`, otherwise the same eight lines). This is not similar logic; it is the same function twice, and `resolve_tier` is the function F050 shows both scorers depend on for a tier the state never supplies.

**`beo-author/proposals/pending/` has a writer and no reader. CONFIRMED.** `git grep -n 'proposals/pending' -- skills/beo/beo-reference/scripts/` → 2 hits, both in `beo_propose.py`: the docstring at `:7` and `PROPOSAL_DIR` at `:28`. Nothing in the 17 scripts opens the directory.

**`.beads/artifacts/<id>/logs/` has neither. CONFIRMED, more completely than filed.** `git grep` for a `logs` path segment under `artifacts` in `scripts/` returns **zero hits**. The directory is not merely unwritten; no script in the bundle names it at all. The finding's exception is the right one: F015's discarded verify output is the content that belongs there, so this is the one orphan to populate rather than delete.

**No script reads a transition's `to` field. CONFIRMED.** `git grep -n '\["to"\]\|get("to")' -- skills/beo/beo-reference/scripts/` → zero hits. `pipeline.json`'s transitions are read for `condition_id` (`beo_state.py:375`) and for owner routing, never for the phase they land in — which is precisely the data F038's missing `phase` invariant would need, and it is already loaded into the same function that fails to use it.

The remaining legs (`caller` role arithmetic, harness-proposal `target`, `stable_json` sort reliance, `_grant_pass_execute` self-comparison) are restatements of F003, F026 and F033 at field granularity, as the finding itself says. They are dispositioned there and are not re-derived here.

The finding's remediation — delete the orphaned surfaces pre-launch, except `logs/` — is correct, and to it should be added: the scorer duplication is not a style defect once F050 is read alongside it, because `resolve_tier` being duplicated means the tier-resolution bug has to be fixed twice.

Disposition: **CONFIRMED**. Files changed: none.

### F056 [P2] — CONFIRMED exactly, including the negative result

Every leg re-derived, and the negative one matters as much as the positive:

- `beo_check.py:395-401` — `if not isinstance(command, str) or not command.strip(): return [...]`, `:397` `argv = shlex.split(command)`, `:399` the unparseable guard, `:401` `subprocess.run(argv, cwd=root, shell=False, text=True, capture_output=True, check=False)`. `run_structural_check` is called from `main` at `:549`, inside `if args.check == "validate":` — the pre-approval branch. Confirmed.
- `beo_verify.py:49-54` — the docstring, quoted correctly by the finding: *"The command is tokenized with shlex and executed without a shell so that metacharacters in a verify command cannot trigger arbitrary execution. TICKET.json is human-approved, but the harness should not rely on the author to sanitize their own commands."* (The finding gives the range as `:50-53`; the quoted text spans `:50-54`.)
- `grep -n 'shell=' skills/beo/beo-reference/scripts/*.py` → **4 hits**: two are the code, `beo_check.py:401` and `beo_verify.py:73`, both `shell=False`; two are prose, `beo_check.py:387` (*"Declared command is exec'd via execve (shell=False)"*) and `beo_verify.py:269`. **No `shell=True` anywhere in scope.** The report's Coverage section states this correctly and it holds on re-derivation.

So the finding's central move is right and is the rarer kind: it takes a mitigation that **works** for the threat its author named, and shows the named threat was the smaller one. Metacharacters are inert; the argv is still whatever the ticket says, and `rm -rf` tokenizes cleanly. The docstring at `:50-54` is evidence for the finding rather than against it — it records that the author considered ticket commands untrusted enough to defend against, then defended against the wrong property.

The ordering half is the sharper of the two. `structural_check` runs under `--check validate`, which is the step whose *purpose* is to decide whether the ticket may be approved. A ticket that has not yet passed validation executes a command during validation. The finding's framing — "run no ticket-supplied command before `TICKET.json` becomes trusted, and if `structural_check` must run pre-approval it needs a constrained command vocabulary rather than free argv" — is the correct shape and is correctly marked a Phase B design question rather than a patch.

Disposition: **CONFIRMED**. Files changed: none.

### F057 [P2] — **NOT CONFIRMED.** The swallow is not silent at any of the three sites, and the finding's stated minimum remediation is already implemented at all three

The structural claim reproduces: all three helpers wrap `append_event` in `try` / `except Exception` and continue. The claim that makes it a finding does not.

`git grep -n -B3 -A5 'append_event'` over the three files:

- `beo_verify.py:122-127` — `try: append_event(root, issue_id, event)` / `except Exception as exc:` / comment *"Event append is best-effort. The returned results are authoritative; the caller writes them into state.json."* / `print(f"warning: failed to append verification_run event: {exc}", file=sys.stderr)`.
- `beo_score_trace.py:306-311` — same shape, comment *"Scoring is advisory; failure to append must not break the caller, but the data loss should be visible to the operator."* / `print(f"warning: failed to append trace score event: {exc}", file=sys.stderr)`.
- `beo_score_context.py:234-239` — identical to the above but for the noun.

The finding's contract violation is *"a silent write failure means the trail has a hole that nothing reports"*, and its durable solution is *"At minimum, record the swallow — a counter in the result, or a **stderr line that names the exception** — so a hole in the trail is visible."* Every one of the three sites already prints a stderr line naming the exception, and two of them carry a comment stating that visibility as the reason. The finding asks for what the code does.

**What survives, and it is not this finding.** The warning goes to stderr and not into the JSON result or the exit code, so a caller parsing stdout — which is how the manifest documents these helpers' output shape (`command-manifest.md:27`, `:28`, `:32`: `json`) — sees a normal result with no indication that an event was dropped. That is the "counter in the result" half of the finding's own remediation, and it is a real gap for `beo_verify.py`, whose result is gate evidence. But it is a narrow machine-readability point about one script, not the audit-trail hole the finding describes, and the finding's own P2 severity rests on the premise that nothing reports the failure.

**One thing the finding gets right and should not be lost.** Its distinction — best-effort is defensible for an advisory scorer and not for `beo_verify.py` — is correct, and `beo_verify.py:125-126`'s own comment concedes the asymmetry by justifying the swallow with *"the caller writes them into state.json"*, which is a claim about a different record than the one being dropped. That thread is F015's and F009's, and is dispositioned there.

Disposition: **NOT CONFIRMED**. Files changed: none.

## Inherited BLOCKED Halves From S3a

The S3a receive record left eight confirmed findings with a half it could not settle, because the deciding
evidence is in `beo-reference/scripts/` and that slice was forbidden to read the scripts as authority. Its
Tally names them and names S3b as owner: *"Confirmed halves left BLOCKED on S3b ... `F002, F009, F043, F045,
F049, F050, F051, F077`. Eight rows, each naming S3b as owner in its own text."* S3b is that owner and may
read the scripts. All eight are settled here.

Ids in this section are prefixed `S3a-` throughout; they are that record's numbering, not this one's, and the
two `F002`s are different findings.

### S3a-F002 — the envelope-vs-trace direction. **RESOLVED: no contradiction. The provisional reading is disconfirmed.**

The open question was whether `beo_state.py` stamps `approved_phase_sequence_id` from the *post*-transition
`phase_sequence_id` while `approval-envelope.json:89` defines execution start against the *pre*-transition one.
Derived:

- `beo_state.py:602` — `after["phase_sequence_id"] = int(before["phase_sequence_id"]) + 1`, run on every write.
- `beo_state.py:605-608` — under `owner == "beo-validate"` with `status == "PASS_EXECUTE"`, `after["approval"]["approved_phase_sequence_id"] = after["phase_sequence_id"]`. Post-transition, as the report observed.
- `approval-envelope.json:89` — *"First durable state.json transition from an approved state whose `approval.approved_phase_sequence_id` equals the pre-transition `phase_sequence_id`, to executing..."*
- `beo_state.py:617-618` — `execution_entry_is_current(state)` returns `state["phase_sequence_id"] == state["approval"]["approved_phase_sequence_id"]`, and `:586` applies it to **`before`**, the pre-transition state of the execution write.

Trace the two writes. The approving write leaves the state with `phase_sequence_id = N` and
`approved_phase_sequence_id = N`. That state is the `before` of the next write. The execution write therefore
evaluates `before.phase_sequence_id == before.approved_phase_sequence_id` → `N == N`. **That is exactly the
predicate `:89` states.** Stamping post-transition at approval is what makes the value equal the
pre-transition sequence at execution entry; the two are the same integer seen from two writes.

`beo_state.py:533-534` and `:542-543` complete the picture by forbidding any updater from setting either field,
so both are system-owned and the invariant cannot be forged by a caller.

**Resolution: the code and the envelope agree.** S3a's confirmed half — that `phase_sequence_id` has zero
write-time semantics anywhere in the 32-file doctrine surface — is untouched and remains the finding. What is
now settled is that the doctrine gap is a *documentation* gap and not a symptom of a code/contract split.

### S3a-F009 — whether `beo_check.py`/`beo_state.py` enforce `payload_contracts` procedurally. **RESOLVED: yes, thoroughly.**

`beo_state.py:474-500`, inside `validate_event_schema` (`:431`), reads `beo_contract_metadata.payload_contracts`
at `:475` and, when a contract exists for the event kind, enforces five distinct things:

- `:478-481` — every field in `contract["required"]` is present in the payload.
- `:484-486` — every required field also has a schema in `contract["properties"]`, so an incomplete contract is itself an error.
- `:487-490` — unless `additionalProperties is True`, unknown payload fields are rejected.
- `:491-493` — each present property is type-checked by `_validate_payload_property`.
- `:494-496` — any property carrying `"registry": "pipeline.condition_id"` is cross-checked against the live `condition_id` set from `pipeline.json`, and `:497-500` adds a handoff-specific rule.

`:462-472` does the same for `owner_rules`, rejecting an unregistered actor and any kind outside that actor's
`may_emit`. `beo_audit.py:413-419` reads the same metadata for check C4.

**Resolution: the materiality half is disconfirmed.** S3a's mechanics half stands unchanged and is correct —
`beo_contract_metadata` is a root sibling reachable from no applicator keyword, so under JSON Schema 2020-12 it
asserts nothing, and `properties.payload` is `{"type": "object"}` and nothing more. But the contract is not
unenforced; it is enforced by hand-written Python that reads the annotation as data. That is the bundle's
pattern everywhere — this report's own coverage line records `grep -n 'import jsonschema' *.py` → **0** — and
it means the defect is fragility (two enforcement surfaces that can drift, one of them invisible to any schema
validator), not absence.

### S3a-F043 — whether a script carve-out exempts `approved_prestate_unchanged` at execution start. **RESOLVED: no carve-out exists; the predicate is implemented and the path that matters skips the check entirely.**

- `beo_check.py:263-272` — `compute_approval_fields` returns four keys, and `:271` is `"prestate": compute_prestate(root, ticket)`.
- `beo_check.py:284-286` — `validate_approval_envelope` loops `for field, expected in fields.items()` and appends `approval.{field} is stale` on any mismatch. `prestate` is one of those fields, compared as a whole dict.
- `compute_prestate` (`:180-204`) hashes every scope token, expanding globs at `:198-200`.

So `approved_prestate_unchanged` **is** implemented, with no exemption of any kind, and S3a's disconfirming
condition (a script-level carve-out) does not exist.

**What replaces it is worse.** `git grep -n 'validate_approval_envelope' -- skills/beo/` → **2 lines**: the
definition at `beo_check.py:275` and a single call at `beo_check.py:556`, under `elif args.check ==
"execute-entry":`. This report's F003/F004/F005/F036 establish
that `beo_run.py` never invokes `beo_check.py` at all. Run as written,
`grep -n 'beo_check\|validate_identity\|validate_plan\|run_structural_check\|validate_review\|validate_containment' beo_run.py`
returns **exit 0 and one line**, not no match: `:37`, `from beo_check import changed_files, compute_prestate,
validate_working_tree_prestate`. That single line is what carries the claim rather than refuting it — it imports
three helpers and **none** of the five validators named in the alternation, and `validate_approval_envelope` is
not among the imported names either, so the envelope check has no route into `beo_run.py`. F001's row above
records the same grep with the same one hit; this subsection had it as a null, and the null is corrected here. The prestate predicate is
therefore correctly built and never runs on the path that executes the bead. This is not a new finding; it is
F003 acquiring one more thing it drops.

### S3a-F045 — what `root` resolves to for `repo_head_sentinel(root)` under a worktree. **RESOLVED: whatever tree the caller happens to be in, and the two call sites derive it differently.**

`repo_head_sentinel` (`beo_io.py:45-52`) runs `git rev-parse HEAD` with `cwd=root`, so it reports the HEAD of
whichever working tree `root` names. Its two callers derive `root` by different means:

- `beo_check.py:530` — `root = Path(args.root).resolve()`, from `--root`, defaulting to `.`.
- `beo_run.py:63-69` — walks up from `Path.cwd().resolve()` until it finds a directory containing `.beads`.

Inside a BEO worktree, `.beads` is the symlink `ensure_beads_symlink` creates (`beo_worktree.py:83-107`), and
`(root / ".beads").is_dir()` follows symlinks, so the walk stops **at the worktree**, not at the main repo.
`beo_run.py` invoked inside a worktree therefore records the worktree's HEAD; `beo_check.py` invoked from the
main repo records the main HEAD. Nothing anywhere reconciles the two, and `approval.repo_head` carries whichever
one wrote it.

**Resolution: S3a's doctrine gap is real, and the implementation does not close it — it instantiates it twice.**
This compounds two findings in this report. F016's root-derivation divergence now has a named consequence: the
commit an approval binds to. And F043's broadening applies on top — in a git-less environment both call sites
record the same sentinel string, so the binding is not merely ambiguous but absent.

### S3a-F049 — whether the worktree loss on a repair route is recoverable. **RESOLVED: not by any code path in the bundle. Only the reflog.**

`cmd_cleanup` (`beo_worktree.py:264-312`), whose docstring at `:265` reads *"Remove worktree and delete its
branch"*:

- `:273-279` — `git worktree remove --force <wt_path>`.
- `:284-289` — `git worktree prune`.
- `:291-298` — `if existing:` → `git branch -D <existing>`. Force delete, which drops the ref regardless of whether its commits are merged anywhere.

Nothing in the function stashes, tags, snapshots, or reports the head it is about to drop; `:301-309` builds a
result carrying `status`, `issue_id`, `reason`, optional `errors` and the branch **name**, never its SHA. After
`cmd_cleanup` the commits are unreachable, and the only route back is `git reflog` in the main repository —
outside the bundle, time-limited by `gc.reflogExpire`, and needing a SHA the tool did not print.

**The sharpest form of the finding is internal to the same file.** `cmd_create`'s stale-registration recovery
at `:156-160` carries a comment stating the opposite policy verbatim: *"Reuse the existing branch instead of
minting a fresh timestamped one. This preserves any commits made in the deleted worktree and avoids orphaning
the old branch ref."* One function is written to preserve exactly what the other force-deletes, and
`kernel.md` §7.5 routes repair — a route whose entire purpose is to come back — through the deleting one.

### S3a-F050 — whether `beo_state.py` in fact rejects an intervention that changes phase or approval fields. **RESOLVED: it does not. The bundle's prose is accurate about its own gap.**

`validate_state`'s intervention handling is `beo_state.py:295-313`, read whole. It validates the list
(`:295`), then per entry: object-ness (`:297-298`), an allow-list of seven keys (`:299-303`), `type` against
`{"human","reviewer","ci","agent"}` (`:304-306`), `impact` against `{"informational","blocking","helpful"}`
(`:307-309`), and three non-empty strings (`:310-313`). Every check is **structural and entry-local**. No
predicate relates an intervention to `phase`, to any `approval` field, or to any other part of the state, and
none compares an entry's `recorded_at` to anything.

The nearest thing to enforcement is `_reject_unowned_changes` (`:529-556`), which is a *per-owner field*
permission check, not an intervention rule: it forbids an updater from setting `phase_sequence_id` (`:533-534`)
and `approval.approved_phase_sequence_id` (`:542-543`) and gates fields by owner. An owner already permitted to
write `approval` may append an intervention and mutate `approval` in the same update, and nothing objects.

**Resolution: `artifact-boundaries.md:49-68` is telling the truth.** Its verbatim admission — *"`beo_state.
validate_state` currently does not enforce the 'must not change phase or approval fields' rule on intervention
entries"*, *"caller discipline only"*, *"These are known limitations"* — matches the code exactly. S3a's
alternative (that the prose is the bug and the code does check) is disconfirmed. This also reinforces F038:
`validate_state` constrains `verdict`, `route_condition_id`, `closed_in_br`, `severity` and
`recommended_route` against each other, and declines to constrain anything against `phase` — interventions
included.

### S3a-F051 — whether the `protected_path_defaults` asymmetry is exploitable. **RESOLVED: not in the direction S3a feared. The matcher inverts it, and leaves a different hole.**

`beo_paths.is_protected_path` (`:99-106`) tests each pattern against **two** predicates, not one — `:102-103` is
`protected_path_matches(normalized, pattern) or path_tokens_overlap(normalized, pattern)`. Both have to fail
before a path is unprotected, so both are traced below. The first is `protected_path_matches` (`:60-64`):

```
def protected_path_matches(path, pattern):
    normalized_pattern = normalize_posix_path(pattern)
    if path_matches_pattern(path, normalized_pattern):
        return True
    return "/" not in normalized_pattern and fnmatch.fnmatchcase(Path(normalize_posix_path(path)).name, normalized_pattern)
```

`:64` is a **basename fallback for any slash-free pattern**. Eight of the fourteen defaults are slash-free —
`.env`, `.env.*`, `*.pem`, `*.key`, `*.p12`, `*.pfx`, `id_rsa`, `id_ed25519` — so each already matches at any
depth, `app/config/.env` and `deep/nested/id_rsa` included. The eight secret patterns S3a called deficient are
not deficient, and the two `**/`-prefixed entries S3a called the correct form (`**/.env`, `**/.env.*`) are
**redundant**: `.env` and `.env.*` cover the same paths through `:64`.

The residual hole is the other four, the ones with a slash: `secrets/**`, `credentials/**`, `.git/**` and
`.beads/**`. Taking `app/secrets/prod.json` against `secrets/**` through both disjuncts:

- **First disjunct, `protected_path_matches` (`:60-64`).** `path_matches_pattern` (`:44-57`) is not an equality
  (`:49`), the pattern does have a glob (`:51`), the path is not the `/**` base (`:53-56`), so it falls to
  `_match_segments` (`:30-41`), which anchors the pattern's first segment to the path's first segment:
  `fnmatchcase("app", "secrets")` is false at `:39` and the recursion stops. The `:64` basename fallback is
  guarded by `"/" not in normalized_pattern`, and `secrets/**` has a slash, so it never runs. **False.**
- **Second disjunct, `path_tokens_overlap` (`:258-282`).** Not equal (`:263`); `left` (the path) has no glob and
  `right` (the pattern) does, so `:268` is skipped and `:270-271` fires — `return path_matches_pattern(left, right)`,
  which is the *same anchored matcher* the first disjunct already ran, with the same two arguments. The
  `_glob_patterns_overlap` branch at `:272-273` needs globs on both sides and the `is_relative_to` branch at
  `:275-279` needs globs on neither, so for a concrete path against a glob pattern this function has no
  independent path. **False, for the same reason and by the same call.**

So the second guard adds nothing here: `app/secrets/prod.json` is **not** protected by `secrets/**`, nor is
`vendor/.git/config` by `.git/**`. A `**/` prefix is exactly what those four need, and none of them has one.

**Resolution: S3a's asymmetry is real and its exploitability reasoning is inverted.** The list is inconsistent
because the author added `**/` to the family that did not need it and omitted it from the family that does.
S3a's `medium` confidence on the consequence was the right call.

### S3a-F077 — which splitter evaluates a verify command. **RESOLVED: `shlex.split`. The golden trace is correct and the schema's prose is incomplete.**

- `beo_verify.py:57` — `argv = shlex.split(command)`, then `:70-77` `subprocess.run(argv, ..., shell=False, ...)`.
- `beo_check.py:397` — `argv = shlex.split(command)`, then `:401` `subprocess.run(argv, cwd=root, shell=False, ...)`.

Both ticket-command paths use the same tokenizer, and `shlex` honours quoting: `grep -i 'receive' README.md`
splits to `["grep", "-i", "receive", "README.md"]` with the quotes stripped. The golden trace's recorded
`exit_code: 0` and `stdout: "Please receive updates."` are reproducible under the splitter the code actually
uses, so the example is not wrong.

**What survives is a contract defect, and it is in the schema.** `ticket.schema.json:52` states *"Each verify
command is exec'd directly via execve (shell=False, no shell). Pipes, redirects, `&&`, `||`, `;`, and env-var
expansion are NOT supported."* It enumerates five shell constructs that do not work and is silent on quoting,
which does — through `shlex` rather than through a shell. A ticket author reading `:52` has been told the
argv is produced by something, has been given a list of what that something rejects, and has no way to know
that single and double quotes are honoured. The bundle's own worked example depends on the undocumented half.

**Resolution: S3a's upgrade to a live inconsistency stands, redirected.** The inconsistency is not between the
trace and the code — those agree — but between the trace and `ticket.schema.json:52`'s incomplete statement of
the evaluation contract. Remediation is one sentence in the schema description naming `shlex`, and it is the
same sentence F056's Phase B design question will need.

## Tally

Every number below was derived on the turn this section was written, and the command is named beside it.

**Row inventory.** `grep -cE '^### F[0-9]{3} \[P' <this record>` → **57**, and the same command over
`docs/ultrareview/26-09-06-s3b-beo-scripts-round-1.md` → **57**. `grep -oE '^### F[0-9]{3}' | sort | uniq -d`
→ empty output, so no id is written twice. `grep -c '^### RX' ` → **1**. `grep -c '^### S3a-F'` → **8**.

**Bucketing was done by hand, not by regex, and the mechanism is recorded exactly.**
`grep -oE '^Disposition: \*\*[^*]+\*\*'` over this record returns **8** distinct strings, and the failure is
not where an earlier draft of this paragraph put it. The regex stops at the first closing `**`, so a comma
form written *inside* the bold — `**CONFIRMED, narrowed**` (`:126`) — survives as its own distinct string and
is never mis-filed. The forms that are silently lost are the ones written *outside* it. `grep -c '^Disposition:
\*\*CONFIRMED\*\*'` → **38**, and re-reading those 38 lines in full shows **9** of them carry a qualifying
clause after the closing `**` that the regex truncates away: `:137`, `:233`, `:273`, `:331`, `:409`, `:657`,
`:684`, `:712`, `:809`. **Eight of those nine belong in a non-plain bucket** — `:273`, `:331` and `:137`
broadened, `:233`, `:657`, `:684` and `:712` redirected, `:809` strengthened — and only `:409`, which qualifies
the report's confidence rather than the disposition, is genuinely plain. That is the whole arithmetic of the
first row: 38 truncated `**CONFIRMED**` lines minus 8 mis-bucketed ones is the **30** the table records. All 58
disposition lines — the 57 F rows plus RX01, which the paragraph under the table counts separately and
deliberately does not fold into the 57 — were therefore read in full and assigned by hand. This is the same
proxy-drift mechanism that took S3a's tally from 95 to 97 before it was caught; naming it *precisely* is the fix, and getting the
mechanism wrong in the first telling — blaming the comma form that in fact works — is itself an instance of it.

| Disposition | P1 | P2 | P3 | Total |
|---|---:|---:|---:|---:|
| CONFIRMED (unqualified) | 6 | 19 | 5 | **30** |
| CONFIRMED-narrowed | 2 | 6 | 2 | **10** |
| CONFIRMED-broadened | 1 | 5 | 0 | **6** |
| CONFIRMED-redirected | 1 | 3 | 0 | **4** |
| CONFIRMED-strengthened | 0 | 2 | 2 | **4** |
| NOT CONFIRMED | 0 | 2 | 0 | **2** |
| SPLIT | 0 | 0 | 1 | **1** |
| DUPLICATE | 0 | 0 | 0 | **0** |
| BLOCKED-half | 0 | 0 | 0 | **0** |
| **Band total** | **10** | **37** | **10** | **57** |

The band totals match the report's own declared distribution — P1 10 / P2 37 / P3 10 — exactly.

**Confirmed in some form: 54 of 57.** The three that are not: **F045** and **F057** NOT CONFIRMED, and **F047**
SPLIT, counted once in the table under its worse half. Naming the SPLIT's halves so the ranking below is
auditable: `beo_io.compact_text` is confirmed dead; `beo_ticket.write_ticket` is not dead and the finding's
remediation would break three test modules.

**Counted separately, and deliberately not folded into the 57:**

- **RX01**, one P1 **REVERSAL**, reinstating candidate `S3b-06-06`. It carries an `RX` id rather than an `F` id
  so the report's finding numbering is never renumbered by this pass. Adding it, the confirmed defect population
  this pass hands to Phase B is **55**, not 54.
- **Eight inherited BLOCKED halves from S3a**, all eight resolved on this pass and none returned to the Human
  as an open question: `S3a-F002`, `S3a-F009`, `S3a-F043`, `S3a-F045`, `S3a-F049`, `S3a-F050`, `S3a-F051`,
  `S3a-F077`. Their outcomes are not uniform and the summary line is not "confirmed": **two inverted the
  parent's reasoning** (`S3a-F051` — the matcher already protects the family S3a called deficient, and the hole
  is the other family; `S3a-F002` — the stamp S3a read as a contradiction is exactly what the envelope
  specifies), **one dissolved the alleged absence** (`S3a-F009` — `payload_contracts` *is* enforced, at
  `beo_state.py:474-500`; the defect is two drifting enforcement surfaces, not none), and **five confirmed the
  parent** (`S3a-F043`, `S3a-F045`, `S3a-F049`, `S3a-F050`, `S3a-F077`). S3a's record can be closed against
  these eight with no residue.

**Owed work this pass created and did not do.** `tests/` — 9 modules, 4094 lines, 41% of the slice's own
declared line count — was never briefed and never reviewed, as this record declared before its first row.
F047 is the concrete proof that the gap produced a wrong finding rather than merely a thin one: the scouts
could not see `write_ticket`'s 17 callers, so a P3 was filed whose remediation would break the suite, and the
finding's own disconfirming check was the one that would have caught it. A second S3b pass over `tests/` with
its own brief is owed, and it is not a nice-to-have: the whole point of reviewing tests inside this slice was
to catch a test passing over a confirmed defect, and 54 confirmed defects now sit against an unreviewed suite.

**Fixes applied: 0. Gates opened: 0. Ledger rows written: 0. Files changed in `skills/`: 0.** This is a Phase A
verification pass; it applies no remediation and opens no gate.

## Ranked Confirmed Findings

55 items — 54 confirmed `F` rows plus `RX01` — in three tiers. The ranking is by what a fix buys, not by the
report's band, and the tiers are not equal in size on purpose: Tier 1 is one defect seen from seven angles.

**Tier 1 — the execute path performs no validation at all (7).** Fixing any one of these without the others
buys almost nothing, because each is a different door into the same room.

1. **F003** — `beo_run.py` mints the entire approval envelope itself and calls none of `beo_check.py`'s
   predicates. Everything in this tier is downstream of it. Its own disconfirming check is false, which is why
   it survived the report's own scepticism.
2. **RX01** — `_result_passed` lets the executed command's own output decide whether it passed. The gate's
   terminal evidence is self-attested.
3. **F004** — `verdict_accept` and `closed_in_br=True` are written with no `validate_review`, no
   `validate_containment`, no strict-mode cross-check.
4. **F026** — role labels (`owner`, `approved_by`, `reviewed_by`) are conventions and never identity checks.
   This is the root cause under F003 and F010 and belongs above them in a redesign, below them in a repair.
5. **F005** — a ticket with no verify commands completes the whole lifecycle and is accepted.
6. **F036** — a non-quick ticket is accepted with a stderr warning, so every strict-mode obligation is
   bypassed rather than refused. The path *announces* the mismatch and proceeds.
7. **F002** — re-running against a closed bead durably writes `phase=approved` beside a standing
   `verdict_accept`. This is the tier's only defect that leaves a false record on disk rather than merely
   failing to check one.

**Tier 2 — the gate's evidence is unbound, unverifiable, or answerable to two authorities (18).**

8. **F008** — the approval projection is hashed without `reservation_evidence`, at two call sites.
9. **F001** — `review.cross_check` is schema-legal, gate-required, and unconditionally rejected by the only
   sanctioned writer. Strict mode's cross-check cannot be recorded at all.
10. **F009** — `verify_issue` returns `ok: true` when every command was skipped. Not silent; documented as
    the contract, which is worse.
11. **F010** — `review.reviewed_by` is a hardcoded literal stamped at record creation, at four sites.
12. **F025** — `--check review-entry` never re-validates the approval envelope; the acceptance write has no
    staleness check at all, not even the cheap sequence one.
13. **F043** — `repo_head_sentinel` fails open with a string, poisoning the projection hash as well as the
    stored field, from two call sites.
14. **F037** — verify commands execute while the phase is still `approved`, at two ticket-supplied command
    sites, before the durable transition.
15. **F038** — `validate_state` never ties `phase` to `approval.status`: the single field the lifecycle turns
    on is the one field the validator declines to constrain.
16. **F056** — ticket-supplied commands from `structural_check`, `verify` and `behaviour_gate` execute with
    zero content review.
17. **F023** — `validate_path_token` skips the repo-escape containment check for any token containing a glob.
18. **F017** — a raw, unvalidated `issue_id` builds a path and reaches a subprocess.
19. **F042** — `beo_run.py` and `beo_check.py` pass different allowed-dirty-path arguments to the same
    function, from different trust origins.
20. **F028** — the second of `beo_run.py`'s two prestate checks is advisory, four lines below one that refuses.
21. **F027** — `br close` runs before the state write and the two are not atomic.
22. **F016** — three incompatible repo-root conventions coexist; five registry-load sites resolve relative to
    the script file rather than the passed root, `ticket.schema.json` among them.
23. **F039** — `route_condition_id` answers to `pipeline.json` while `state.schema.json` declares an enum for
    it that nothing compares. The drift is latent today and nothing would report it becoming live.
24. **F006** — `expected_receiver_phase_after_condition` is declared and read by nothing.
25. **F007** — `reservation_release_on` is declared and releases nothing.

**Tier 3 — robustness, atomicity, instrument coverage and hygiene (30).** F011, F012, F013, F014, F015, F018,
F019, F020, F021, F022, F024, F029, F030, F031, F032, F033, F034, F035, F040, F041, F044, F046, F048, F049,
F050, F051, F052, F053, F054, F055.

Two carry a caveat a Phase B owner must read before touching them. **F050**'s remediation is inverted by this
pass: `trace_tier` and `interventions` have no producer but do have consumers at three sites, so "delete the
fields" would delete a live scoring input. **F055**'s duplication leg is now proved rather than asserted —
`resolve_tier` and `MODE_TO_TIER` are AST-identical between the two scorers — which makes it the cheapest
correct fix in this tier and the one `F050` depends on not being done carelessly.

## Instrument Log

Errors this seat made in this record, each caught and corrected before the record closed. They are logged
because this pass charges the report under review with exactly this fault, and a pass that does not hold itself
to the rule it enforces is not evidence of anything.

**Derived-count errors, all three of the same shape — a number carried rather than re-derived.**

1. **F011** said "eight (seven bare, one narrowly guarded)". Re-enumerated from `sed -n '544,562p' beo_check.py`:
   **ten bare fallible calls across nine lines**, plus one narrowly guarded. The `:562` line carries two nested
   calls, which is where the undercount came from.
2. **F018** said "8 hits" and "seven statements of the opposite precedence". Re-derived from
   `grep -n 'BR_ACTOR\|BEO_ACTOR' ... | wc -l`: **9 hits**, two resolution sites in opposite orders, and six
   `BR_ACTOR`-first statements against three `BEO_ACTOR`-first — not seven against one.
3. **F024** said "twelve lines apart". `:57` and `:79` are **twenty-two** lines apart.

**Count errors caught on the closing pass, by a sweep the pointer resolver does not perform.** The resolver
checks that `file:line` citations exist; it cannot check a number written in prose. A sweep for
`\b(one|…|twelve|[0-9]+) (hits?|sites?|calls?|lines?|files?|matches)\b` over the whole record found four more:

4. **F047** said `compact_text` had "**2 hits**, both the definition" — a sentence that contradicts itself, since
   one definition is one line. `git grep -n 'compact_text' -- skills/beo/beo-reference/` returns **1 line**;
   widened to `grep -rn --include='*.py' .` over the checkout, still one.
5. **F047** said `write_ticket` had "**20 call sites in `tests/`**" and listed imports among them.
   `grep -rn 'write_ticket' tests/` returns **21 lines**: 3 imports, 1 *local wrapper `def`* at
   `tests/test_verify_command.py:21` that the original enumeration missed entirely, and **17 call expressions**
   — 12 reaching `beo_ticket.write_ticket` directly and 5 through the wrapper. The disposition and the row
   heading both carried the wrong figure and both were corrected.
6. **F038** said `grep -n 'phase' beo_state.py` over `:239-400` "returns five hits". It returns **8 lines in
   five places**; the enumeration was right and the noun over it was wrong.
7. **F031** cited `beo_score_context.py:251` and then `:252` as "the substitution line". `sed -n '246,256p'`
   shows `:251` is `state_loaded = True`, `:252` is `except FileNotFoundError:`, and **`:253`** is the
   substitution. The finding's own citation is off by one but points into the right block, and this record
   repeated the error rather than catching it.

**Commands named but not run as named — the false-record shape, in this record.**

8. **`S3a-F043`** wrote `grep -n 'beo_check\|validate_identity\|validate_plan\|run_structural_check\|validate_review\|validate_containment' beo_run.py` → **"no match"**. Run as written it returns **exit 0 and one
   line**: `beo_run.py:37`, the import of `changed_files`, `compute_prestate`, `validate_working_tree_prestate`.
   The conclusion survives — that line imports three helpers and none of the five named validators — but the
   recorded output was false, and **F001's own row records the correct result 884 lines earlier in this record**
   (`grep -n` on both: the F001 line is `:115`, the corrected S3a-F043 line is `:999`; the gap is derived, not
   estimated, because estimating it would be the same fault this item logs).
   The record contradicted itself, in the direction that looks cleaner.
9. **`S3a-F043`** asserted `validate_approval_envelope` "is called at exactly one place", inferred from reading
   `:555-557` rather than searching. Run as `git grep -n 'validate_approval_envelope' -- skills/beo/`: **2
   lines**, the definition at `beo_check.py:275` and one call at `:556`. The claim holds; it was not derived
   when written.
10. **F049** named `git grep -n 'get_check_ids'` over the repository; what was actually run was
    `grep -rn --include='*.py'`. Re-run as named: **one line**, the definition at `beo_audit.py:40`. Identical
    result, different command — logged because "identical result" is only knowable after re-running, not before.

**Reasoning errors, not counting errors.**

11. **F031's first narrowing was too generous.** It credited `beo_score_context.py` with threading `state_loaded`
    into the scorer and stopped there. `MIN_REQUIRES` sets `"state": 0` for `minimal` and `standard`, so
    `breakdown["state_loaded"]` computes `0 >= 0` and reports **`True` on a state that was never loaded** — and
    `resolve_tier` returns `standard` by default on exactly the synthesised input the finding is about. The row
    was rewritten from a clean narrowing to a narrowing-with-inversion.
12. **`S3a-F051`'s residual hole was asserted from one of two disjuncts.** `is_protected_path:102-103` is
    `protected_path_matches(...) or path_tokens_overlap(...)`, and only the first was traced. The second was then
    traced in full: for a concrete path against a glob pattern it reduces at `:270-271` to the *same*
    `path_matches_pattern` call the first disjunct already made, so it adds nothing and the hole stands. Had it
    not, this would have been a claimed hole derived without checking the guard that closes it — the
    confirming-direction twin of the fail-open class this campaign is cataloguing.
13. **F039's three figures did not close.** Twelve schema enums are not one schema-derived plus one
    pipeline-derived plus eleven literals. Reconciled in the row: the sets overlap on nine, two literals
    (`:305`, `:308`) validate intervention fields the schema declares no enum for, and the twelfth enum
    (`review.cross_check.verdict`) has no enforcement of any kind because the parent object is rejected first.
14. **F025 was incomplete rather than wrong.** `execution_entry_is_current` has two call sites, not one;
    `beo_check.py:437` inside `validate_execute_entry` was added. The strengthening survives.
15. **The Pointer Self-Check section was itself stale, by its own rule.** It was written at **209/209**, and
    the Custody rewrite that followed it added three citations — `tests/test_gate_row.py:13-14` and
    `tests/test_gate_row.py:16` among them — without the resolver being re-run. The record therefore stated
    209 while a live run stated 212, and the seat's message to the Supervisor carried the live 212 against a
    record that said 209: the message and the record disagreeing is the same class as a count carried from
    memory, only inverted, because here the *record* was the stale copy. Corrected to **213/213**, re-derived
    after the last body edit — 213 and not 212 because writing this item added one citation of its own,
    which is the recursion the ordering rule exists to terminate: the resolver's last run must be the one
    that has nothing left to invalidate it. The rule the section already implied is now the operative one: the resolver runs
    after every body edit and before the digest, never in the middle.

**Vocabulary and label corrections.** `CONFIRMED-strengthened` and `SPLIT` were used in rows before either was
declared; a `## Disposition Vocabulary Used Below` section was added to the preamble before the Tally could
mis-bucket them. **F045**'s heading was written `[P3→P2 as filed]`, a confused band label, corrected to `[P2]`.
**F047**'s heading was written `**BLOCKED-half is not available here; this splits.**`, corrected to `**SPLIT.**`.

**One near-miss, recorded because avoiding it was not luck.** `pipeline.json` yields 17 distinct `condition_id`s
against `state.schema.json`'s 9, which reads as a live registry drift and would have been written as one. Before
writing it, `null_verdict_conditions` and `verdict_to_condition` were checked by set difference against the
schema enum: every reachable value is in the schema, and the extra 8 are unreachable today. F039 therefore
records the drift as **latent, not live**, and says so in the row. This is the fail-open trap declined rather
than sprung, and it cost one extra derivation.

**Tooling failures worth carrying forward.** A `grep -rn ... --include=*` invocation dies in zsh with
`(eval):4: no matches found: --include=*`; `git grep` was used instead. `git grep 'write_ticket' -- skills/beo/beo-reference/tests/` returns empty **not because there are no callers but because `tests/` is at the
repository root**, not under `beo-reference/` — the record's `tests/test_*.py` citations were already correct
and the search path was wrong. A search that returns nothing because it looked in the wrong place is
indistinguishable, in a record, from a search that returns nothing because there is nothing there.

## Pointer Self-Check

Every `` `path:line` `` and `` `path:start-end` `` citation in this record was extracted by regex, resolved
against the ten root prefixes this campaign uses, and range-checked against the file's actual line count. The
script was run on the turn this section was written, from this seat's session scratchpad rather than from
the repository, so that this pass leaves exactly one file behind.

- **213** distinct citations.
- **213** resolved to an existing file **and** in range.
- **0** unresolved paths. **0** out-of-range line numbers.

The check proves a citation points at a line that exists. It does not prove the line says what the row claims;
that is what the row's own derivation is for, and item 8 of the Instrument Log is an example of a citation that
passes this check while the sentence around it was false.

## Custody

Derived on the turn this section was written.

- **HEAD** `33eafc5431a265d523241db25b0e455a974f09e3`, branch `main`. `origin/main` is at `038dc27b`, two
  commits behind: the push is **G97, still open**, and this pass did not attempt it.
- `git diff -- skills/` → **0 lines**. `git diff --cached` → **0 lines**. `git stash list` → **0** entries.
- `git --no-optional-locks status --porcelain --untracked-files=all` → ` M AGENTS.md` (untouched under **G57**,
  awaiting the Human's attribution), plus 11 untracked `docs/ultrareview/*.md` and `scratchpad/c8-intake.md`,
  which is never staged. Nothing else.
- **`.pyc` sweep, the proof that the execution restriction held.**
  `find skills/beo/beo-reference tests \( -name '__pycache__' -o -name '*.pyc' \)` → 28 entries, and
  `ls -ldT` on all 28 dates **every scope-module artefact under `beo-reference/scripts/` to Sep 4 18:57**, two
  days before this campaign opened. The single newer entry is `tests/__pycache__/test_gate_row.cpython-314.pyc`
  at Sep 6 13:48:40, which is `gate_row.py`'s own test from the C21 delivery. That it imports no module in
  this slice is derived, not recalled: `grep -nE '^\s*(from|import) ' tests/test_gate_row.py` → **9 lines**,
  eight of them stdlib (`__future__`, `contextlib`, `io`, `subprocess`, `sys`, `tempfile`, `unittest`,
  `pathlib`) and one `import gate_row` at `:16`, whose path is set two lines
  above at `tests/test_gate_row.py:13-14` — `parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"` —
  so the single non-stdlib import resolves to `skills/herdr-delivery-workflow/scripts/gate_row.py`, which is
  in this repository but outside the S3b slice (`skills/beo/beo-reference/scripts/`) entirely. No scope script was executed, no test was run, and no `--help` was invoked on this pass.
- `~/.herdr/projects/beo-skills/gates.md` sha256 `b1845e61df34ed3dad297d50611281f66a1b0fadaf8551c43075986bf647e6e7`, unchanged. No ledger row was written by this pass, because no external write occurred.
- Files changed by this pass: **one**, this record. It is untracked and lives under `docs/`, outside every
  reviewed scope.

---

**Record digest.** sha256 over this file's content up to and including the last `---` separator above,
computed with `idx = max(i for i, l in enumerate(lines) if l.strip() == "---")` and hashed over
`"\n".join(lines[:idx+1])`, so the digest never covers the paragraph that reports it.

**The hashed bytes carry no trailing newline**, because `"\n".join(...)` puts a separator *between* elements and
none after the last. `head -n 1407 <file> | shasum -a 256` therefore does **not** reproduce it — `head` keeps the
newline that terminates line 1407 — and returns `0b443c9063bf943c87af830b7d767895356465f7d8c5c8d676c83b26fb5a8285`
instead. Both were derived on this turn. The shell equivalent of the recipe is
`head -n 1407 <file> | perl -0pe 's/\n\z//' | shasum -a 256`. A second note for any re-deriver: the separator sits
at **line 1407**, which is stable because everything added since sits below it, and the file's total was **1426**
(`wc -l`) at the moment the digest above was computed. The current total is not restated here: it is a
below-boundary fact that this very paragraph changes, so writing it down is a self-invalidating claim of exactly
the kind this record exists to catch. Separately:
`len(open(p).read().split("\n"))` returns one more than `wc -l`, because the split yields a trailing empty element,
and reporting that number as a line count is the same derived-count fault this record logs elsewhere. It was
reported that way once, in a Supervisor message, and is corrected here.

`f178c69fb4368cadecbfae8abc911ffbc6b2cf1d9a447b4d02f11f86b3535506`
