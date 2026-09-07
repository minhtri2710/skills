# Receive: s1-herdr-delivery-workflow Round 1

Report verified: `docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1.md`
(846 lines, 28 findings F001-F028, derived on this turn by `wc -l` and
`grep -cE '^### F[0-9]{3}'`).

Skill: `ultra-review-receive`, run as written and unfixed. **Verification only.**
The Human granted a review of the project's skills, not remediation
(`ultra-review-receive/SKILL.md:36`: "If the user requested audit or verification
only, return dispositions without edits"). No source file is edited by this pass.
`Files changed` is `none` on every row below, and that is a claim this record
makes about itself, checked at the end against `git status`.

## Preflight

Derived on the turn this header was written:

- HEAD `038dc27b50859cb30542b91683688a1f52ce5d66`; the report's Scope line names
  `038dc27`, so the snapshot matches. `git rev-parse HEAD`.
- `git --no-optional-locks status --porcelain --untracked-files=all` -> 9 lines,
  none inside `skills/`. `git diff -- skills/` -> 0 lines. The reviewed scope is
  unmodified since the report was written.
- `skills/herdr-delivery-workflow/scripts/gate_row.py`: 229 lines, sha256
  `a4b1ed731f625d7f77bb6b2042cc0c6ebc76e242c0f356b65f8573f98141bb78`. This is the
  file S1 reviewed and the file every behavioural check below runs.
- Report structure conforms to the skill's Required Input: Metadata header
  (Date, Review name, Round, Scope, Report path), `## Prior Round Guard`,
  `## Findings` with `F001`-`F028`, `## Verification Queue`,
  `## Strongest Reason Not To Merge Yet`.

**Real-ledger custody.** Six findings (F001, F002, F008, F020, F021, F023) are
checks that invoke `gate_row.py` against a ledger, and the report's own Verification
Queue correction warns that F021 and F023 name no scratch target, so an operator
following them literally would write the project's append-only gate ledger. Every
invocation in this pass passes `--ledger` pointing into a scratch directory outside
the repository. Enforcement, not intent: `~/.herdr/projects/beo-skills/gates.md` is
145 lines, sha256 `f3863c8ce9d74b77a1aba0d7a1df965e0ac635e98f4237fbf2cc9a3541360f21`
before the first check; the same two figures are re-derived and recorded at the end
of this file.

## Input-contract block: the premise audit

`docs/ultrareview/26-09-06-project-architecture-premise-audit.md` was offered to
this skill in the same slice and is **BLOCKED at input**, not verified.
`ultra-review-receive/SKILL.md:12` requires a Metadata header, Prior Round Guard,
`F###` findings, a Verification Queue and a Strongest Reason section; `:14` says to
block a report that is malformed. That file has none of the four: its findings are
`A1`-`A6`, it has no Prior Round Guard and no Verification Queue, because it is an
`architecture-premise-audit` output and not an ultra-review report. Derived on this
turn by `grep -nE '^#{1,3} '` over both files.

Forcing it through would be the receive skill's own failure mode, so it is recorded
here instead. **A1-A6 still owe Phase A a ranking**, on their own derivation, and
must not be dropped because this skill could not ingest the file that carries them.

## Dispositions

One row per finding, in the order verified. Columns are the skill's
(`ultra-review-receive/SKILL.md:53`): ID, disposition, decisive evidence, source pointers, files changed,
validation and result, reviewer evidence, remaining blocker.

### F001 [P1] — CONFIRMED

- **Decisive evidence.** A tamper matrix run on this turn against the scratch
  ledger. One valid push row was built by the script itself, then hand-edited one
  field at a time and re-checked. Six of six tampers pass with exit 0 and
  `ok: G1 checks out`: `boundary-check=""` rewritten to
  `boundary-check="src/fabricated.py"`; `record=timely` rewritten to
  `record=bogus`; `quote="scratch"` emptied to `quote=""`; the branch `main`
  rewritten to `nonexistent-branch`; and `channel=bogus:bogus` and
  `writer=NOT_A_SEAT` inserted. The unmodified control also passes, so the check
  is running.
- **The build/check asymmetry the finding names is reproduced directly.** The same
  script, asked to *build* a row with `--status resolved:granted --quote ""`,
  refuses: `gate_row: quote= is required unless status=open`. `check()` accepts
  the identical field, because `:181` tests `quote is None` and an empty string is
  not `None`.
- **Source pointers.** `gate_row.py:132-182` is the whole of `check()`, and it
  re-derives exactly two things: `rev-parse --verify <head>^{commit}` at `:156`
  and the push `count` at `:171`. `KIND_RE` and `STATUS_RE` are applied at
  `:146-150`; the timestamp is regex-shaped at `:151`; `:158-163` tests
  `field.startswith(known)` for `channel=`, `writer=`, `record=` and never the
  value. `boundary` is captured by `PUSH_RE` at `:36` and used nowhere in
  `check()`. `merge-base --is-ancestor` appears once in the file, at `:65`, inside
  `derive_push`, which `check()` never calls. Against
  `human-gates-and-closeout.md:71`: "re-reads the appended line from disk,
  re-derives each of those, and exits non-zero on any mismatch … the re-derivation
  proves it adds up."
- **Files changed:** none. **Validation:** the tamper matrix above; no repository
  file and no real ledger touched, every invocation carried
  `--ledger <scratch>/t.md --repo <scratch>/work`.
- **Reviewer evidence:** none staffed; the behaviour is mechanical and not
  disputed. **Remaining blocker:** none for verification. Phase B only.

### F002 [P1] — CONFIRMED

- **Decisive evidence.** The report's own disconfirming check, run on this turn in
  a scratch repository built for it: base commit, then commit 1 adding
  `src/out-of-boundary.py`, then commit 2 deleting it, with `--boundary docs`.
  The script emitted `push=<base>..<head> count=2 boundary-check=""`. The
  doctrine's algorithm from `human-gates-and-closeout.md:35-43`, run over the same
  range — `git rev-list base..head` piped through
  `git diff-tree --root -m --no-commit-id --name-only -r` — lists
  `src/out-of-boundary.py`. The two answers differ on the exact case the finding
  predicts, in the direction that lets an out-of-boundary write pass clean.
- **Source pointers.** `gate_row.py:69`, `git(repo, "diff", "--name-only",
  f"{base}..{head}")`, against `human-gates-and-closeout.md:35-43`, which states
  in prose that the union is wanted "not the index or only the final tree diff".
- **Files changed:** none. **Validation:** the scratch range above; ledger written
  was `<scratch>/scratch-gates.md`.
- **The first-party instance the finding names does not hold, and this was
  re-derived rather than asserted.** `G90` in the real ledger carries
  `push=0ded528ac3494f980a2f5d7ddc64b19468ef6456..038dc27b50859cb30542b91683688a1f52ce5d66 count=1 boundary-check=""`.
  Read-only on this turn: `git diff --name-only 0ded528a..038dc27b` returns the
  single path `skills/herdr-delivery-workflow/evals/evals.json`, and the doctrine's
  algorithm over the same range —
  `git rev-list 0ded528a..038dc27b | git diff-tree --root -m --no-commit-id --name-only -r --stdin`
  — returns the same single path; `diff` of the two sorted outputs is empty. The
  range carries one commit (`git rev-list --count`, 1) and no path that leaves and
  returns, so the two algorithms cannot disagree on it. `G90`'s empty
  `boundary-check` is correct. Append-only prevented correcting the row, not
  re-deriving it; my first pass said the opposite and was wrong.
- **Reviewer evidence:** none staffed. **Remaining blocker:** none for
  verification. The defect is demonstrated in the scratch range and is latent in
  the real ledger rather than realised in it.

### F003 [P1] — CONFIRMED

- **Decisive evidence, and it is an absence claim, so the search was exhaustive
  rather than a sample.** `git ls-files 'skills/herdr-delivery-workflow/*'` returns
  11 files on this turn; `grep -n 'gates\.md'` over all 11 returns 8 hits, in
  `evals.json` (:156, :160, :358 — all gate-*write* cases), `human-gates-and-
  closeout.md:71` and `:74` (the append path), `project-config.md:11` (locates the
  file beside the config), `supervisor-policy.md:17` (the Supervisor may read it to
  audit), and `gate_row.py:188` (argparse help). `intake-policy.md` contains the
  string zero times. **No step in any route reads the ledger for a prior grant.**
  `grep -ni 'revok\|revoc'` over the same 11 files returns 3 hits: the bare
  sentence `human-gates-and-closeout.md:52` "The waiver remains revocable", and two
  restatements of it inside `evals.json`. No status value, no mechanism, no check.
- **The layering contradiction is textual and reproduced verbatim.**
  `herdr-delivery-workflow/SKILL.md:48`: a Supervisor message "can add a constraint; none can move a
  decision from one seat to another, remove a gate, or authorize an external
  write." `human-gates-and-closeout.md:49-54` lets a Supervisor extend a standing
  waiver to "a seat that did not exist when the Human granted it", which makes an
  external write permissible for a seat the Human never named. `evals.json:409`
  and `:415` score that extension as correct behaviour, so it is the intended
  reading, not a slip.
- **The compounding pair is also verbatim.** `:49` "A standing waiver is
  per-project, not per Human session", against `:26` "Only the current request
  qualifies: a prior request, a config key, or an inferred preference never
  resolves a gate."
- **Files changed:** none. **Validation:** the two exhaustive greps above, file
  list enumerated from `git ls-files`.
- **Reviewer evidence:** none staffed. **Remaining blocker:** which layer should
  own waiver extension is a design decision for Phase B, not a verification result.

### F004 [P1] — CONFIRMED

- **Decisive evidence.** `grep -n 'add_argument' skills/herdr-delivery-workflow/
  scripts/gate_row.py` on this turn returns 12 lines and the complete option set:
  `--ledger`, `--repo`, `--check`, `--kind`, `--status`, `--channel`, `--writer`,
  `--record`, `--push-base`, `--boundary`, `--note`, `--quote`. There is no
  `--head` and no `--branch`. The search is over the whole file, so the absence is
  decisive rather than sampled.
- **The consequence is in the source, not inferred.** `build()` at `:104-105`
  takes both `branch` and `head` from `git rev-parse` at invocation time and
  nothing compares them to the SHA the gate is about. The push block at `:119-125`
  additionally requires `ls-remote origin refs/heads/<branch>` to equal current
  `HEAD`, so a past push cannot be recorded at all. Against
  `human-gates-and-closeout.md:77`, which mandates `--record reconstruction` for a
  resolved-but-unrecorded gate — a gate that by definition describes a past head.
  `--record reconstruction` is accepted by argparse at `:196` and changes exactly
  one thing in `build()`: the `:101-102` guard, which re-tests a `note` the code
  has already required non-empty at `:87-88` and so can never fire.
- **Files changed:** none. **Validation:** the grep above plus a read of `build()`
  end to end.
- **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F005 [P1] — CONFIRMED, with one sub-claim not re-derivable here

- **Decisive evidence.** `human-gates-and-closeout.md:81` read end to end on this
  turn: it requires a runtime-denial row per refused command, says to "retry in the
  narrowest allowed shape before treating it as blocking", then moves on to who may
  type the row. It states no attempt count, no failure signature, and no
  terminating condition. `grep -n 'lead-policy' ` over the whole file returns two
  hits, `:24` and `:30`, both about attention events and waivers — **the file never
  cites `lead-policy.md` on retries.**
- **The terminator does exist, verbatim, one file away.** `lead-policy.md:103`:
  "When the same command fails the same way twice — a launch that returns an error,
  a check that cannot start, a prompt that is refused — the third attempt is not a
  retry, it is a decision: inspect the prerequisite first (the binary, its auth or
  quota, the pane's state, the Lead's own permission), and when the prerequisite is
  not the Lead's to fix, route `BLOCKED` to the Human with both failures verbatim."
  A refused prompt is a named trigger and the Lead's own permission is a named
  prerequisite, so the rule covers a refused `gate_row.py` call squarely. The
  finding is right that the halves are unwired.
- **Sub-claim resolved on disk, and it is a first-party instance of F009.** The
  finding also corrects this project's own record, citing
  `iteration-19/HANDOFF.md:81-84`. `git ls-files` contains no `iteration-*` path
  and no `HANDOFF.md`, so a resolver that reads the index alone finds nothing — but
  `find skills -name HANDOFF.md` on this turn returns sixteen files, among them
  `skills/herdr-delivery-workflow-workspace/iteration-19/HANDOFF.md` at 189 lines,
  hidden from the index by `.gitignore:16` `skills/*-workspace/`, which
  `git check-ignore -v` names as the matching rule. Read at the cited lines: `:81`
  is "terminator exists at `lead-policy.md:103`:" and `:83-84` open a block quote of
  that rule, under a heading at `:78` reading "Second correction, made 2026-09-06
  during the S1 ultra-review of this same skill." The correction the finding asks
  for has already been made in the handoff, against the same `lead-policy.md:103`
  this row quotes. **My first pass called this half unverifiable, and it was
  wrong**: the file was invisible because I searched the index, which is exactly
  the blindness F009 reports and this record confirms.
- **Files changed:** none. **Validation:** the two reads and the cross-reference
  grep above.
- **Reviewer evidence:** none staffed. **Remaining blocker:** whether "the same
  command" means the refused operation or its literal shape is undecided in the
  text, which is the finding's own solution hypothesis and a Phase B question.

### F006 [P1] — BLOCKED

- **What is verified.** The finding's premises hold at this head. `json.load` over
  `evals/evals.json` gives 43 cases (`evals` key, not `cases`). The seven cases the
  finding names — 1, 2, 4, 11, 16, 20, 22 — contain the string `config` nowhere in
  prompt, expected output, files or assertions, checked case by case on this turn;
  each opens a delivery or review-only intake. The five it calls clean — 18, 19,
  26, 31, 43 — do state config state, and so, it turns out, do 32 and 34, which the
  finding does not name and which do not open a fresh intake. The three doctrine
  sites are present and agree: `herdr-delivery-workflow/SKILL.md:14`, `intake-policy.md:11`,
  `project-config.md:11`, the last stating outright that when the config is absent
  the seat must "stop and ask the Human whether to create one" and "Never create
  the file or assume defaults without that answer."
- **Why this is BLOCKED and not CONFIRMED.** The finding's own disconfirming check
  is a question about the eval harness — whether condition c pre-seeds a
  `config.md` — and the harness is not in this repository. `git ls-files | grep -i
  eval` returns exactly one path, `skills/herdr-delivery-workflow/evals/evals.json`:
  a case file with no runner, no condition definition, and no fixture directory. No
  tracked file defines "condition c". The evidence that would decide scorability is
  outside the checkout, which is the skill's definition of `BLOCKED`
  (`ultra-review-receive/SKILL.md:29`, evidence or environment missing).
- **What would decide it.** The harness that runs these 43 cases, or any tracked
  statement of what condition c seeds. Either resolves this to `CONFIRMED` or
  `DISPROVEN` without further inspection of this head.
- **Files changed:** none. **Validation:** the per-case scan and the `git ls-files`
  search above. **Reviewer evidence:** none staffed.

### F007 [P1] — CONFIRMED

- **Decisive evidence, absence claims searched exhaustively over the whole case
  file.** Case-insensitive `grep -c` over `evals/evals.json` on this turn:
  `solo-lead` 0, `architect` 0, `council_request` 0, `record-only` 0, `gate_row` 0.
  The file holds 43 cases (`json.load`, `len(d['evals'])`).
- **The four rules are real, so these are gaps and not phantom coverage.** Over the
  tracked bundle excluding `evals.json`: `solo-Lead` 44 hits, `COUNCIL_REQUEST` 8,
  and the record-only direct-push clause exists at `human-gates-and-closeout.md:32`,
  "a direct push to the product line without review is permitted only for a
  record-only class declared at intake for that run". The second-death terminator
  is at `herdr-delivery-workflow/SKILL.md:78`. Each is a settled rule with zero measurement.
- **The imbalance the finding names is understated, not overstated.** A regex scan
  for quiesce/commit language matches 19 of 43 cases (1, 2, 5, 7, 10, 14, 16, 20,
  21, 22, 23, 24, 25, 28, 30, 31, 32, 38, 40), against zero for any of the four.
  The finding cites six; the wider count is recorded here because it is derived on
  this turn by a different query and is the same defect, larger.
- **The strongest consequence stands.** The unmeasured record-only clause is the
  one whose implementation F002 proves wrong. An eval on it would have caught F002
  empirically, which makes F007 and F002 the same hole seen from two sides.
- **Files changed:** none. **Validation:** the greps and the case scan above.
- **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F008 [P2] — CONFIRMED, and both predicted failures occurred in a single trial

- **Decisive evidence.** Six `gate_row.py` invocations launched concurrently
  against one scratch ledger (`--ledger <scratch>/conc.md --repo <scratch>/work`,
  `&` then `wait`). Result, derived from the scratch file on this turn: **6 rows
  appended, 5 distinct gate ids — `G1 G2 G3 G3 G4 G5`** — and **one process exited
  1 with `gate_row: the row read back from disk is not the row written`** on a row
  that is present in the file. That is both halves of the finding at once: a
  duplicate id from the unlocked `next_id()`, and a false read-back failure from
  `rows[-1]` positional matching.
- **The false failure is the inverse of the advertised property.**
  `human-gates-and-closeout.md:71` says read-back "proves the row landed". Here a
  row landed and read-back said it had not. A seat following `:81` would retry, and
  the retry appends a duplicate into a file the doctrine says cannot be repaired.
- **Source pointers.** `gate_row.py:55-61` (`next_id`, max+1, no lock),
  `:214-220` (append, then `[-1]`, then compare). `grep -n
  'flock\|fcntl\|lockf\|O_EXCL\|tempfile'` over the file returns nothing.
- **Files changed:** none. **Validation:** the concurrency trial above, entirely in
  the scratch directory. **Reviewer evidence:** none staffed. **Remaining
  blocker:** none. The finding's stated confidence was medium-high; the trial
  raises it to demonstrated.

### F009 [P2] — CONFIRMED, with a pointer correction

- **Decisive evidence, the finding's own disconfirming check run in this
  checkout.** `.gitignore:16` is `skills/*-workspace/`.
  `git --no-optional-locks status --porcelain --untracked-files=all` matches
  `workspace` **0 times**; the same command with `--ignored` matches it **499
  times**; and `skills/ultra-review-workspace/campaign-01/` exists on disk holding
  `INTAKE.md`, `S1-BRIEF.md`, `S1-CANDIDATES.md` — this campaign's own custody
  files, invisible to every custody check in the workflow.
- **`--ignored` appears nowhere in the bundle.** `grep -c -- '--ignored'` over all
  tracked bundle files returns 0 everywhere, so the exclusion is not named, not
  chosen, and not documented.
- **Pointer correction, which does not change the disposition.** The finding's
  title says five sites; its `Source pointer:` line enumerates six, one of them
  `human-gates-and-closeout.md:118`. That line is a
  closeout bullet about unexplained tracked change and does not contain the
  command. The actual sites, from `grep -n 'untracked-files=all'` over the tracked
  bundle on this turn, are **six**: `herdr-delivery-workflow/SKILL.md:59`, `lead-policy.md:65`, `:173`,
  `peer-policy.md:123`, `:152`, `:188`. The finding missed `peer-policy.md:188`,
  the post-verdict recomputation — which is the site where blindness matters most,
  because it is the comparison that is supposed to catch a Reviewer that wrote
  something. One named pointer is wrong and one real site is unnamed, so the true
  count is six against the title's five: the defect is larger than filed, not
  smaller.
- **Files changed:** none. **Validation:** the two porcelain runs and the two
  greps above. **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F010 [P2] — CONFIRMED

- **Decisive evidence.** The solo-Lead requirement is stated without exception at
  `herdr-delivery-workflow/SKILL.md:43`, `lead-policy.md:46` ("In `solo-Lead` mode, the Reviewer must
  differ from the Lead by both kind and model"), `peer-policy.md:156` and `:158`.
  `peer-policy.md:156` is the decisive line, because it carries the availability
  escape and scopes it away from solo-Lead: "Run the review on a kind that differs
  from every Engineer's kind **when another kind is installed**; in solo-Lead mode,
  run it on a kind and model that both differ from the Lead." The escape clause
  governs the partitioned half of the same sentence and not the solo-Lead half.
- **Partitioned mode has a degraded path and solo-Lead has none.**
  `lead-policy.md:46` and `:48` supply the same-kind-with-pinned-distinct-model
  fallback and its disclosed kind-collision residual risk; `project-config.md:39`
  repeats it. Every occurrence of that fallback vocabulary across the tracked
  bundle — searched exhaustively on this turn for `same-kind`, `kind-collision`,
  `distinct pinned model` — is scoped to an Engineer-kind collision. No solo-Lead
  fallback exists at this head.
- **`peer-policy.md:167` does list `same-kind-distinct-model` as a legal
  `INDEPENDENCE:` value**, in the same line that ends "in solo-Lead mode, both kind
  and model must differ from the Lead", so the template offers a value the mode
  forbids.
- **Intake never checks.** `intake-policy.md:78` declares solo-Lead as a mode with
  no kind-availability precondition; no tracked file makes two installed kinds a
  condition of declaring it.
- **Files changed:** none. **Validation:** the greps and full-line reads above.
- **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F011 [P2] — CONFIRMED, decided from doctrine and a live read-only observation

- **The textual disagreement is exact.** `herdr-delivery-workflow/SKILL.md:59` and `peer-policy.md:152`
  gate the quiesce on "every staffed Engineer is idle"; `lead-policy.md:37` also
  says "idle"; `lead-policy.md:62` says "A quiesce point requires every staffed
  Engineer to be **idle or done**". Two phrasings of the ending condition of the
  parallel phase, in one bundle.
- **The runtime produces the one the majority phrasing excludes.**
  `herdr-cli.md:57-59` defines `idle` as "ready for input, **and its tab has been
  seen in the focused Herdr UI**" and `done` as "the same underlying idle state
  after unseen background work finishes"; `:181` instructs "Use `--no-focus` for
  background work unless the user asked to switch context", and `lead-policy.md:42`
  repeats `--no-focus` as the default.
- **Observed live, read-only, on the two `herdr agent list` runs of this pass.**
  The first, mid-pass: five agents, `lead-munsu` at `agent_status: done` with
  `focused: false`, `supervisor` at `idle` with `focused: true`. The second, at the
  end of the pass: the same five seats, `lead-munsu` now `idle` with
  `focused: false` and `supervisor` now `done` with `focused: true`. **The two
  rosters together are the stronger evidence**, and they say something narrower than
  one roster would: `done` is not predicted by `focused: false`, the assignment
  moved for two different seats inside one pass, and both states occur on settled
  seats. That is `herdr-cli.md:57-59` exactly — `done` is the transient label a
  settled seat wears until its tab is seen. A quiesce check therefore reads one
  unchanged Engineer as `idle` on one turn and `done` on the next, so the bundle's
  two phrasings are not two wordings of one condition. **No agent was started to
  test this**;
  the finding's own disconfirming check would have required dispatching one, which
  is a control-plane mutation and outside a verification pass.
- **Files changed:** none. **Validation:** the doctrine reads plus the roster
  above. **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F012 [P2] — CONFIRMED, with one mitigation the finding does not cite

- **Decisive evidence, an absence.** Peer posture is specified in detail —
  `peer-policy.md:37-45` defines `allowlisted`, `bypassed`, `none`,
  `human-started`, `prompting`, and `:163` puts `posture=` in the roster line. A
  case-insensitive search over the tracked bundle for `lead-args` and for `lead`
  near `posture` returns no line that defines a posture **for the Lead's own seat**:
  every hit is the Lead recording or reading a Peer's posture. `project-config.md`
  has `engineer-args` and `reviewer-args` and no Lead equivalent.
- **The receiving-end failure is documented in the CLI reference and unowned in the
  policies.** `herdr-cli.md:104`: `agent prompt` "refuses an agent already sitting
  at an approval or question dialog with `agent_blocked` before sending any input."
  Every Peer report goes through that call.
- **Mitigation the finding does not cite, recorded because it narrows the claim.**
  `herdr-cli.md:138` does say what happens to a bounced send: "A rejected send —
  `agent_blocked` because the Lead sits at a dialog, or any error — is not retried:
  the Peer stops, and the Lead reads the pane at its next wake." So the report is
  not silently discarded by design; it waits in the Peer's pane. What is still
  unowned is the wake itself: an idle Lead's only wake source is the prompt that
  just bounced, and the workflow forbids polling, so nothing produces the "next
  wake" the sentence relies on. The finding's contract claim survives that
  narrowing; its phrase "silently drops every Peer report" should read "leaves
  every Peer report unread until something else wakes the Lead".
- **Not tested by inducing the state.** Reproducing it would require putting a Lead
  at a dialog, which is a control-plane mutation and not verification.
- **Files changed:** none. **Validation:** the greps and reference reads above.
- **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F013 [P2] — CONFIRMED, with one adjacent sentence the finding does not weigh

- **Decisive evidence.** "this run" occurs 21 times across six tracked bundle files
  (`SKILL.md` 2, `herdr-cli.md` 3, `human-gates-and-closeout.md` 8,
  `lead-policy.md` 5, `peer-policy.md` 2, `project-config.md` 1; `grep -c` per file
  on this turn). Read at the closeout sites — `herdr-delivery-workflow/SKILL.md:64` "close only resources
  created by this run", `human-gates-and-closeout.md:115` "Close only panes, tabs,
  workspaces, and agents created by this run" — none of the 21 defines whether the
  run is the delivery or the acting seat.
- **The case that makes it bite is doctrine's own.** `lead-policy.md:157`: "A
  relaunch is a fresh start pointed at a context pack, not a resume", and the
  replacement seat holds none of the outgoing seat's run context. A replacement
  Lead did not create the panes the first Lead created.
- **The adjacent sentence, recorded because it is the strongest counterargument.**
  `lead-policy.md:155` says "the replacement takes the same seat name after the old
  one is cleared, so one canonical Lead survives the exchange." A reader can argue
  continuity from it. It binds the *seat name*, not the run, and the closeout
  predicate is written on the run — so the ambiguity survives, but a fix should
  build on `:155` rather than invent a new continuity notion.
- **Files changed:** none. **Validation:** the per-file counts and the site reads
  above. **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F014 [P2] — CONFIRMED

- **Decisive evidence, an absence searched over the whole bundle.**
  `grep -ni 'abandon\|cancel\|withdraw'` over the tracked bundle excluding
  `evals.json` returns three hits and not one is a lifecycle exit:
  `intake-policy.md:38` lists "cancellation" among the misfit triggers, and
  `structural-misfit-policy.md:30` and `:32` are about wrappers and duplicate
  state. **No abandonment, cancellation or withdrawal path exists for a delivery.**
- **The slot rule is the one the absence traps.** `lead-policy.md:52`: "A delivery
  leaves the flight slot only through the whole chain: every staffed Engineer's
  evidence report … independent `PASS` on that exact head, integration onto the
  product line, the Human decision for any external effect". One delivery in flight
  per project, and only one exit.
- **The rogue stash is routed with no resolver.** `lead-policy.md:64` makes a new
  stash a blocker ("a new stash means work has been hidden from porcelain"),
  and no text names who disposes of it or when the block clears.
- **Files changed:** none. **Validation:** the absence grep and the two line reads.
- **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F015 [P2] — CONFIRMED

- **Decisive evidence.** `grep -n 'deployed-head'` over the tracked bundle returns
  exactly two hits on this turn: `lead-policy.md:164`, the use site, and one string
  inside `evals.json` that restates the same command in an expected output. **The
  token is used and never defined**; no file records a deployed head, and
  `project-config.md` has no key for one.
- **The repository the command runs against is unnamed too.** `:164` says to
  "compare each hash with `git rev-parse <deployed-head>:<path>`" without saying
  which checkout — the skill source tree or the product repository under delivery —
  and a relaunching seat is by construction in the latter.
- **The eval papers over it, exactly as the finding says.** Case 12's prompt hands
  the value to the model: "a start prompt that names
  `~/.herdr/projects/<project-slug>/context-pack.md` **and the exact head the
  workflow skill was deployed from**". The instrument supplies what doctrine does
  not, so the gap cannot be scored.
- **Files changed:** none. **Validation:** the grep and the case-12 prompt read.
- **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F016 [P2] — CONFIRMED

- **Decisive evidence.** `lead-policy.md:157`: "Doctrine and the permission
  allow-list load at seat start, not at runtime. A Lead seat that predates a
  doctrine redeploy or settings change keeps the old doctrine and allow-list until
  relaunched." `:164` opens "After compaction **or relaunch**, run this short
  checklist before acting: first confirm the doctrine itself, by comparing every
  installed file against the head it was deployed from". The check hashes files on
  disk. On the compaction branch the seat has not reloaded anything, so a clean
  match is a statement about the disk and not about the rules the seat is running.
- **The compaction-specific instruction the finding says is missing really is
  missing.** A case-insensitive search for `compact` over the tracked bundle
  excluding `evals.json` returns seven hits — `herdr-delivery-workflow/SKILL.md:74`, `intake-policy.md:96`,
  `lead-policy.md:26`, `:157`, `:164`, `supervisor-policy.md:13`, `:18` — and none
  says that compaction cannot pick up a doctrine change or that the hash check is
  insufficient on that branch.
- **This receive pass is itself an instance.** This seat has compacted repeatedly
  during this campaign and ran `:164`'s comparison at seat start; the match said
  nothing about which doctrine text the compacted seat was executing.
- **Files changed:** none. **Validation:** the two line reads and the absence
  search. **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F017 [P2] — CONFIRMED

- **Decisive evidence, both lines read in full.** `lead-policy.md:155` names the
  only authorised replacers and the only two reasons — "Only the Human, or the
  Supervisor acting under the explicit Human-permission rule … replaces a Lead —
  because it cannot recover, or because the Human instructs the exchange for a
  healthy one — never on the Lead's own initiative or the Supervisor's." Context
  growth is neither reason. `lead-policy.md:157` contains both halves of the
  collision in one sentence: "Relaunch only at a slice or delivery boundary, never
  mid-flight with Peers outstanding", and "When the run context grows past what can
  hold the verification ledger, gate records, and agent inventory reliably,
  **compact or relaunch the seat** on a bounded context pack". The second is
  addressed to the seat, in the imperative, and offers relaunch as an option the
  seat may take — which `:155` forbids it to take.
- **The instrument resolves it; the doctrine does not.** Eval case 41 is the
  mid-flight redeploy scenario with two Engineers outstanding, and its expected
  output supplies the tie-break in full: "a relaunch happens only at a slice or
  delivery boundary, never mid-flight with Peers outstanding, so the seat finishes
  the outstanding slice first", and "Does not replace its own seat on its own
  initiative". Its assertions state both. That is a tie-break the doctrine text
  never states — the eval encodes the intended reading, so the intent is settled
  and only the prose is ambiguous. This strengthens the finding's solution
  hypothesis (`:157` should read "compact, or signal for relaunch") rather than
  weakening the finding.
- **The finding's disconfirming check is partly overtaken.** It says eval 41 "does
  not exercise the mid-flight collision"; read on this turn, case 41 exercises it
  squarely. What the finding gets right is that the resolution lives only in the
  instrument.
- **Files changed:** none. **Validation:** the two line reads and the case-41 dump.
- **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F018 [P2] — CONFIRMED

- **Decisive evidence.** `grep -n 'workspace record'` over the tracked bundle
  returns two hits and no definition: `human-gates-and-closeout.md:77`, which caps
  `--note` because "narrative belongs in the delivery's workspace record", and
  `gate_row.py:92`, the same sentence as an error string. No file says what the
  workspace record is, where it lives, or who writes it.
- **The asymmetry the finding names holds.** `human-gates-and-closeout.md:69`
  externalises the gate ledger on the argument that "A gate that lives only in the
  Lead's run context dies with the pane", and the ledger gets a path, a script, a
  read-back and an append-only rule. The verification ledger and the final handoff
  block carry the identical exposure and get no file destination anywhere in the
  bundle.
- **Files changed:** none. **Validation:** the grep and the site reads.
- **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F019 [P2] — CONFIRMED

- **Decisive evidence.** `grep -n 'recorded:'` over the tracked bundle excluding
  `gate_row.py` returns **zero hits**. The `recorded:<x>` status prefix exists only
  in `STATUS_RE` at `gate_row.py:30`; no doctrine rule produces it, names it, or
  says when it applies.
- **Both fields are required and neither has a vocabulary.**
  `gate_row.py:212-213` makes `--kind` and `--status` mandatory for an append;
  `KIND_RE` at `:29` accepts any lowercase token. `human-gates-and-closeout.md:81`
  requires a runtime-denial row "naming the refused command" and states no `--kind`
  and no `--status` value for it. A ledger meant to be greppable has a free-text
  key on its denial rows.
- **Files changed:** none. **Validation:** the greps and the regex reads.
- **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F020 [P2] — CONFIRMED

- **Decisive evidence, the finding's own disconfirming check.** Two rows appended
  to a scratch ledger by the script itself; row 1 then hand-edited to
  `kind=CORRUPTED` with its `note=` emptied — two things `check()` does reject when
  it looks at them. `--check` printed **`ok: G2 checks out`, exit 0**. A corrupted
  row is invisible the moment a later row is appended.
- **Nothing owns running it.** `grep -n -- '--check'` over `SKILL.md` and all eight
  references returns **zero hits**: the flag is named nowhere outside the script.
  The natural owner, `lead-policy.md:164`, describes manual reconciliation after
  compaction or relaunch and never mentions the script — and that step fires only
  on compaction or relaunch, so a continuous seat never runs it at all.
- **Source pointers.** `gate_row.py:206` builds the row list, `:209` calls
  `check(rows[-1], ...)`. No loop, no whole-file mode, no chaining.
- **Files changed:** none. **Validation:** the two-row corruption trial above, in
  the scratch directory. **Reviewer evidence:** none staffed. **Remaining
  blocker:** none.

### F021 [P2] — CONFIRMED, both vectors in one invocation

- **Decisive evidence.** One invocation with `--ledger <scratch>/foreign.md`,
  `--repo /Users/beowulf/Work/beo-skills` — a checkout the ledger has nothing to do
  with — `--kind merge --status resolved:granted --writer supervisor-as-hands
  --quote "not typed by any Human"`. It appended clean, exit 0:
  `G1 | … | kind=merge | main@038dc27b… | status=resolved:granted |
  writer=supervisor-as-hands | record=timely | …`. The row asserts a resolved merge
  gate, attributes itself to the Supervisor acting as the Human's hands, and quotes
  words no Human said — and every field the script derives is internally consistent,
  because the script derived them all from a repository nobody authorised it to
  describe.
- **Why that is the finding's exact claim.** `--writer` is validated only by
  `WRITER_RE` at `:32` (shape, not identity) and `--repo` defaults to `cwd()` at
  `:189` with no comparison against the project slug implied by `--ledger`. The row
  presents attribution and subject as derived facts; both are accepted on trust.
- **Scratch discipline.** The invocation went to a scratch ledger. The real ledger
  was not opened; its custody figures are re-derived at the end of this file.
- **Files changed:** none. **Validation:** the invocation above.
  **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F022 [P2] — CONFIRMED, with three pointer corrections and one underived count

- **The core claim holds and was checked assertion by assertion.** Case 40's prompt
  has the Engineer report "Ledger row appended." Only the Lead writes the ledger
  (`human-gates-and-closeout.md:81`). All five of case 40's assertions were read on
  this turn: [1] count mismatch, [2] re-derivation, [3] treats the append as
  unproven until read back, [4] routes the correction, [5] names what was counted.
  **None scores the authority breach** — [3] treats the claim as unproven, which is
  a different defect from an Engineer having claimed ledger authority at all. The
  finding is right.
- **Genuine bundles, verified.** Case 20[5] scores four independently-failable
  behaviours in one line — quiesce condition, porcelain confinement, staging by
  owned paths, and who commits. Case 20[4] scores two. Case 33[3] scores three.
  Partial compliance has no defined score on any of them.
- **Three pointer corrections.** The finding's index for each of its three sharpest
  sub-claims is off by one:
  - the absolute-versus-hedged Reviewer-independence pair is **20[6]** ("Reviews the
    exact Lead-committed head on a kind different from every Engineer's kind")
    against **16[5]** ("Staffs the Reviewer on a different agent kind, **or** records
    same-kind review as residual risk"), not 20[5] against 16[4]. The substance is
    real: neither prompt states which kinds are installed, so one transcript can
    pass one and fail the other.
  - the unstaged-scenario assertion is **17[6]**, which scores the Supervisor-opened
    pane rule (`herdr-cli.md:177`), against case 17's prompt — "Clean up the agents
    you spun up for it before moving on to the next issue" — which stages no
    Supervisor and no Supervisor-opened pane. 17[5] is "Ties teardown to closeout",
    which the prompt does stage.
  - case 19's tension is real as described: the prompt ends "Keep repairing until it
    passes", the assertions require stopping at the cap, and
    `human-gates-and-closeout.md:26` says a plain instruction in the current request
    is itself the Human's decision. The doctrine does not settle which wins.
- **The "seven bundled" count does not survive enumeration, and the disconfirming
  check's comparator is itself bundled.** Of the eight assertion sites the source
  pointer lists, 12[2], 14[3], 17[5] and 42[1] each read as one behaviour; 42[1]'s
  two clauses are one prohibition stated twice. And the finding's comparator — case
  2, "whose assertions are cleanly separated one behaviour each" — has 2[4] scoring
  two branches with two `and`s. The defect class is real and reproducible; the
  count and the comparator are not derived.
- **Files changed:** none. **Validation:** a full dump of every assertion in cases
  2, 7, 12, 14, 16, 17, 19, 20, 25, 33, 40 and 42 with `and`-counts, plus the
  prompts of 17, 19 and 40, all on this turn. **Reviewer evidence:** none staffed.
- **Remaining blocker:** none for verification. Phase B should fix the assertions,
  and fix this finding's pointers before using it as a work list.

### F023 [P2] — CONFIRMED, five of six sub-claims demonstrated, one wrong

Every sub-claim was run against the scratch repository and scratch ledgers.

- **Branch containing `|`** — `git checkout -b 'a|b'` succeeds. The script then
  **appends** `G1 | … | a|b@49160d5… | status=open | …` to the ledger and only
  afterwards fails read-back with `gate_row: field 'a|b@49160d5…' is not
  <branch>@<head>`, exit 1. The unparseable row is in the append-only file. Exactly
  the finding's claim: detected after the append, not before it.
- **Branch containing `@`** — `git check-ref-format refs/heads/feat@v2` reports
  valid; the row appends as `feat@v2@49160d5…` and read-back rejects it the same
  way. `HEAD_RE` at `:33` excludes both characters from the branch group.
- **`\v` in `--note`** — `"\n" in note` at `:94` does not catch it. The row appends
  and fragments: the stored bytes contain `note=line one\x0bline two`, which
  `splitlines()` counts as **2 lines**, and read-back fails with "the row read back
  from disk is not the row written". One logical row, two physical lines, in an
  append-only file.
- **Missing parent directory** — `--ledger <scratch>/nonexistent-dir/g.md` exits on
  an unhandled `FileNotFoundError` traceback from `io.open`, not the documented
  exit-1 `gate_row:` contract. `main()` catches `RowError` only. A project's first
  gate crashes.
- **No `encoding="utf-8"`** — the four I/O sites are `:60`, `:206`, `:215`, `:217`
  and none passes an encoding, while G52 makes Vietnamese diacritics mandatory in
  `--quote`.
- **The `~`-prefixed `--ledger` sub-claim is wrong about its consequence.**
  `--ledger '~/scratch-tilde-test.md'` does **not** create a literal `./~` tree: no
  `~` directory appeared and no file was created in the real home. It raises the
  same unhandled `FileNotFoundError`, because the literal `~` parent does not exist.
  The underlying defect — no `.expanduser()`, and `Path` arguments taken on trust —
  is real and lands in the traceback bucket above; the stated failure mode is not.
- **Files changed:** none. **Validation:** every trial above ran with
  `--repo <scratch>/work` and a scratch `--ledger`; the branches `a|b` and `feat@v2`
  were created in the scratch repository and it was returned to `main`.
- **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F024 [P3] — CONFIRMED, all four cells read against their cited sources

- **`:39` "any approval dialog" is a Human gate.**
  `human-gates-and-closeout.md:13` carves it out in the same breath: "an approval or
  question shown by the agent UI, other than the routine command approval" that the
  `Approval dialogs` section below sets apart. `lead-policy.md:98` confirms the carve-out
  has real consequences — a routine approval for a charter-named command is "a
  pre-arm miss … no ledger line". The table omits the exception.
- **`:42-44` "Who staffs it: Lead".** `peer-policy.md:42` states the opposite for
  one posture: under `human-started` the Lead "does not silently downgrade to
  `prompting` and does not staff the seat itself: it states the exact `herdr agent
  start` line" and the Human runs it. `herdr-delivery-workflow/SKILL.md:29` already records the same
  exception for a Supervisor acting as the Human's hands, so the table contradicts
  its own file nine lines earlier.
- **`:40`, the Supervisor row, whose `Never` cell opens "instruct a Peer".** `herdr-delivery-workflow/SKILL.md:29` and
  `supervisor-policy.md:32` both permit the Human-instructed seat start executed by
  the Supervisor. The cell states an absolute the sources qualify.
- **`:48` "each seat reads its own layer"** names the Lead's layer and the Peer's
  and stops. `project-config.md:11` grants the Supervisor an audit read of the
  config, so a third seat has a defined layer the sentence does not mention.
- **Files changed:** none. **Validation:** each cell read against the section it
  summarises, on this turn. **Reviewer evidence:** none staffed. **Remaining
  blocker:** none.

### F025 [P3] — CONFIRMED

- **Decisive evidence, from the router's own text.** `herdr-delivery-workflow/SKILL.md:24-29` gives four
  route descriptions and no ordered procedure. The delivery entry test is "a source
  change needs bounded ownership, implementation-to-review handoff, or explicit
  bounded monitoring/closeout" — the ownership analysis that produces that answer
  lives in `intake-policy.md`, which the same paragraph says to read **after**
  choosing the route. The router needs its own output.
- **The overlaps are real on the literal text.** "one bounded prompt to an existing
  agent" (lightweight) and "a source change needs bounded ownership" (delivery) both
  cover a prompt telling a running agent to edit code, and the two branches carry
  opposite ceremony with no tie-break sentence anywhere in the section. Lightweight
  is a comma list — "one command, one pane, read-only inspection, or one bounded
  prompt" — whose disjunctive reading licenses unbounded read-only fan-out while the
  same clause forbids reading the policies that would bound it.
- **The trigger is lexical.** Every route sentence and the preflight are written
  around being "inside Herdr"; a Herdr-shaped task phrased without the word has no
  entry.
- **Not disconfirmed by running a dozen tasks.** The finding's check is to route a
  dozen realistic tasks and see the ambiguities reproduce; the ambiguity is
  demonstrable from the text itself, and routing exercises would be judgment, not
  evidence.
- **Files changed:** none. **Validation:** `herdr-delivery-workflow/SKILL.md:24-29` and
  `intake-policy.md:15-43` read in full. **Reviewer evidence:** none staffed.
- **Remaining blocker:** none.

### F026 [P3] — CONFIRMED

- **Decisive evidence, every `wait` site in the CLI reference checked for
  applicability.** `grep -n 'wait'` over `herdr-cli.md` returns 10 lines. `:84` and
  `:88` are `pane wait-output`, documented for a pane running a command — and `:88`
  adds that with a `working` or `blocked` agent in the pane, `pane read` returns
  only the viewport, so the pane-level tools are not the agent-exit observer. `:101`
  is `herdr agent wait <name> --timeout 30000`, shown once in the agent-start block.
  `:104`, `:106` and `:128` are the no-`--wait` report channel. **None of the ten is
  the teardown wait.**
- **The required step has no permitted implementation.** `:177` instructs "send its
  own quit sequence with `herdr agent send-keys <name> …`, **wait for it to leave
  the pane**, then close the pane", while `herdr-delivery-workflow/SKILL.md:78` forbids the Lead to "block
  on a Peer, sleep, poll `herdr agent list`, or run a standing watch".
- **Files changed:** none. **Validation:** the grep and per-site reads above.
- **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F027 [P3] — CONFIRMED, on a disconfirming check this pass constructed

**Disclosure first, because the finding does not supply one.** F027 is the finding
the report's own Verification Queue flags as missing four of the seven mandatory
subfields, including `Disconfirming check:`. It bundles **seventeen** independent
sub-claims — `awk '/^### F027/,/^### F028/' <report> | grep -c '^- '`, derived on
this turn. This row first stated sixteen while enumerating nine run, seven not run
and one uncorroborated, which is seventeen; the count was wrong and the enumeration
was right, and S2 F007 is the finding that caught it. Rather than block F027 for
want of a check, this pass constructed one per sub-claim and ran nine of them; the
disposition rests on those nine, and the seven not run are named below so no reader
mistakes silence for verification.

**Run and confirmed:**

- **`herdr-delivery-workflow/SKILL.md:27`'s SHA test passes an unreachable commit.** In the scratch
  repository: commit, capture the SHA, `git reset --hard HEAD~1`. `git rev-parse
  --verify <sha>^{commit}` exits **0**, and `git branch --contains <sha>` lists
  **0 branches**. A review-only route can return `PASS` on a SHA no branch contains.
- **The `unknown` lifecycle state has no roster branch.** `herdr-cli.md:61` defines
  a fifth state — "an agent is present but Herdr cannot classify it confidently;
  this never proves completion" — and it occurs once in that file and nowhere in
  `lead-policy.md` or `herdr-delivery-workflow/SKILL.md`. `lead-policy.md:98` and `herdr-delivery-workflow/SKILL.md:78` branch on
  idle, done, blocked and missing.
- **The push check hardcodes `origin`.** `gate_row.py:120`,
  `git(repo, "ls-remote", "origin", …)`, against `project-config.md:28`,
  `target-line: <default integration product line>` — a line, not a remote.
- **`project-config.md:41` does drop its qualifier.** Read in full, it ends
  "absent that instruction, the Lead does not write outside the repository" — an
  unqualified sentence that, taken alone, forbids the writes to `gates.md`, the
  context pack and the Supervisor notebook that this same skill mandates. The
  antecedent is the Human-owned files earlier in the sentence, so it is an ambiguous
  antecedent rather than a contradiction, exactly as the finding says.
- **`human-started` reaches no ledger row.** The string occurs 6 times in the
  bundle — `SKILL.md` 1, `peer-policy.md` 5 — and in none of them is it a `--kind`,
  a `--status`, or any ledger field.
- **The `material contract change` conflict is textual.**
  `human-gates-and-closeout.md:12` lists "material scope, architecture, dependency,
  data, or contract change" among the Human gates; `intake-policy.md:31` opens
  "Route the work as high-risk and stop for the applicable design or Human decision
  when it includes:" — a Design Gate the Lead can resolve.
- **The rename conflict is textual.** `peer-policy.md:172` requires renaming the
  Reviewer to `review-<first 12 hex>` per reviewed head; `herdr-cli.md:124` says
  "Rename works on an unnamed agent" and that a name "clears when that agent exits".
  Renaming an already-named seat is documented nowhere.
- **`gate_row.py:188`'s `--help` invents a Reviewer role for the ledger** — "the
  Reviewer round-trips against a scratch file". No policy file has a Reviewer touch
  the ledger; `human-gates-and-closeout.md:81` gives it to the Lead.
- **`gate_row.py:101-102`'s reconstruction guard is dead**, independently
  re-derived while verifying F004: `note` is required non-empty at `:87-88`, so
  `record == "reconstruction" and not note` can never be true.

**Not run, and therefore not verified by this pass:** the `:84` CI-run-ID amendment
against an append-only ledger and its wake definition; `lead-policy.md:99`'s "both
panes' evidence" presupposition; the terminal-restart-clears-a-name contradiction;
the context pack's lack of a delivery id and its unreachable read-back; the missing
back-reference on a resolution row; the trapped-output temporary-directory
convention; and the validation-run teardown path. Each is a textual claim a later
pass can check the same way.

**One sub-claim this pass could not corroborate as stated.** The finding says
`project-config.md:23-25` defines `engineer-args` as containing the allowlist while
`peer-policy.md:37` and eval 43 treat it as an opaque pass-through. Read on this
turn, `project-config.md:23` does define it as carrying "the pre-authorization of
the read-only and verify commands the charter names", and eval 43's expected output
says the Lead "Builds the allowlist from the charter's own commands" — which agrees
with the config rather than opposing it. Recorded so Phase B does not act on it
unchecked.

- **Files changed:** none. **Validation:** the nine checks above.
- **Reviewer evidence:** none staffed. **Remaining blocker:** the seven unrun
  sub-claims; a later pass can clear them without new authorization.

### F028 [P3] — BLOCKED

- **The descriptive claim is true and was checked.** `herdr-delivery-workflow/SKILL.md:70` reads: "a report
  whose stated count disagrees with its own enumeration is the proof that nothing
  was recounted." As written it detects exactly that disagreement, so a report
  carrying a stale count *and* its matching stale enumeration satisfies it. That
  follows from the sentence and needs no experiment.
- **Why it is `BLOCKED` and not `CONFIRMED`.** The skill's `CONFIRMED` requires
  that "current behavior violates the named contract"
  (`ultra-review-receive/SKILL.md:26`). F028 names no violated contract — its own
  `Contract violated:` field reads "Nothing, as written" — and its
  `Disconfirming check:` field reads "None available from this head." A finding that
  asserts no violation and offers no falsifier has nothing for a verification pass
  to confirm or disprove. `BLOCKED` is the skill's own named disposition for this
  case, not a residue: `ultra-review-receive/SKILL.md:29` reads "`BLOCKED`:
  evidence, environment, contract, authorization, or ownership is missing", and what
  is missing here is the contract.
- **It is preserved, not dismissed.** The observation is sound and belongs in the
  campaign's record as a known limit of the rule. It is not a defect in this head
  and should not enter a Phase B work list as one.
- **Files changed:** none. **Validation:** the rule read in full.
- **Reviewer evidence:** none staffed. **Remaining blocker:** by construction — no
  evidence at this head can settle it.

### C-01 — not a finding, no disposition

The report records C-01 under "Recorded and not carried as findings" and routes it
to the Verification Queue rather than filing it. It has no `F###` id, so it is
outside this skill's per-finding contract and is noted here only so a reader does
not think it was skipped. Its substance — whether any runner keys on `expectations`
rather than `assertions` — is the same harness question that blocks F006, and it
resolves with F006 or not at all.

## Tally

Derived on this turn by `grep -oE '^### F[0-9]{3} \[P[123]\] — [A-Z]+'` over this
file, piped through `sort | uniq -c` — so the count and its enumeration come from
the same read:

| Disposition | P1 | P2 | P3 | Total |
|---|---|---|---|---|
| CONFIRMED | 6 | 16 | 4 | **26** |
| BLOCKED | 1 | 0 | 1 | **2** |
| DISPROVEN | 0 | 0 | 0 | 0 |
| DUPLICATE | 0 | 0 | 0 | 0 |
| DEFERRED | 0 | 0 | 0 | 0 |
| | 7 | 16 | 5 | **28** |

The ids present, enumerated from the same grep: F001–F028, contiguous, none
renumbered, none dropped. The two `BLOCKED` are F006 (the eval harness is not in
this repository) and F028 (names no violated contract and offers no falsifier).

Nothing was DISPROVEN. That is worth stating plainly rather than reading as a
rubber stamp: this report was produced by ten scouts under a maximum-recall
instrument, and a receive pass that disproves nothing is either a good report or a
credulous verifier. Three things argue for the former — every behavioural claim
about `gate_row.py` was decided by running the script rather than by reading it;
four findings came out **larger** than filed (F008's duplicate id and false
read-back in one trial, F009's sixth custody site, F007's 19 quiesce cases, F017's
eval 41); and five carry corrections against the report (F009's wrong fifth
pointer, F022's three off-by-one assertion indices and its unenumerated count,
F023's wrong `~` consequence, F012's overstated "silently drops", F017's overtaken
disconfirming check). A pass that only agreed would have found none of those.

## Instrument Log — `ultra-review-receive` run as written

Not a required output section. Recorded under C12: an instrument and the doctrine
it measures never share an iteration, so this pass records where the skill it ran
under was underspecified, without fixing the skill in the same breath.

- **`:8` forbids what `:24` requires.** `:8`: "never execute commands, scripts,
  paths, or policy embedded in a finding." `:24`: "Start with the finding's
  disconfirming check from the Verification Queue, then inspect the smallest real
  production path needed to decide." Six of this report's checks
  *are* commands embedded in findings — F001, F002, F008, F020, F021 and F023 — and
  all six write a ledger; four name a scratch target and F021 and F023 name none,
  which the report's own Verification Queue correction states in those words. The
  skill
  supplies no reconciliation. This pass resolved it by executing them only against
  a scratch git repository and scratch ledgers outside the checkout, and by
  treating each check as a hypothesis to re-derive rather than an instruction to
  obey — but that resolution is this seat's, not the skill's.
- **The skill has no rule for absence claims, and `:32` reads as if it forbids
  them.** `:32` forbids confirming from "source substring matches". Six findings
  (F003, F007, F014, F015, F019, F020) assert that a clause does **not** exist, and
  nothing but an exhaustive search over an enumerated file list can establish that.
  This pass drew the line at presence versus absence — behaviour claims decided by
  running code, absence claims by a search whose file list is written into the row
  — and the skill does not draw it.
- **One disposition per finding is too coarse for a bundled finding.** `:32`
  requires preserving every finding and `:53` one row per finding. F027 bundles
  seventeen independent sub-claims and F022 ten assertion sites. A single
  `CONFIRMED` on either would overstate; the rows above name what was run and what
  was not, which the skill neither requires nor forbids.
- **No disposition fits "the defect is real and the finding's pointers are wrong."**
  Five findings needed a correction recorded inside a `CONFIRMED` row. A verifier
  that only emitted the five dispositions would have passed those errors forward
  into Phase B as a work list.
- **`:14` says block a malformed report and says nothing about where to record the
  block.** The premise audit's block is written into a section of this file's own
  invention, above.
- **`:47` makes the durable record conditional on a request.** "If a durable
  receive record is requested, write `<report stem>-receive.md`". No one requested
  one. It was written anyway, because 28 dispositions that live only in a pane die
  with the pane — which is F018's argument in this very report, applied to the
  verifier instead of the Lead.
- **Two disconfirming checks were declined, and the skill has no word for that
  either.** F011's check dispatches an agent and F012's requires a Lead sitting at a
  dialog. Both are control-plane mutations, and a verification pass that creates a
  seat has created a resource with teardown obligations. Both findings were decided
  from doctrine plus one read-only observation instead; the rows say so.

## Strongest Reason Not To Merge Yet

Unchanged in substance from the report, and now demonstrated rather than argued.

`human-gates-and-closeout.md:71` tells every seat that `--check` re-derives six
fields and that "the re-derivation proves it adds up." On this turn, seven separate
tampers of a row — a fabricated boundary-check, a relabelled `record=`, an emptied
quote, a nonexistent branch, a bogus channel, a bogus writer, and a corrupted
earlier row — each returned `ok: … checks out`, exit 0. The same script refuses to
*build* a row with the empty quote it will happily *check*. And the field that
gates an unreviewed push to the product line is computed by the algorithm the
doctrine writes out longhand as the wrong one: given a commit that leaves the
boundary and a commit that reverts it, the script emitted `boundary-check=""` while
the doctrine's own snippet named the path.

That is a false assurance rather than a gap, and it is cited by name in the
doctrine as the reason a seat may stop reading the ledger. `G90` in this project's
real ledger carries a `boundary-check=""` produced by that code path. Re-derived
read-only on this turn, that particular value is correct — its range carries one
commit and no path that leaves and returns, so the two algorithms agree on it. The
defect is latent in an append-only file rather than realised in it, which is the
reason to fix the instrument before the next push row rather than after.

Nothing here is authorized for repair. Phase B opens only after the whole
campaign's confirmed findings are ranked, and opening it is the Human's decision.

## Custody, re-derived at the end of this pass

Every figure below was derived after the last check ran.

- **The real gate ledger is untouched.** `~/.herdr/projects/beo-skills/gates.md`:
  145 lines, sha256
  `f3863c8ce9d74b77a1aba0d7a1df965e0ac635e98f4237fbf2cc9a3541360f21` — identical to
  the two figures recorded in the Preflight before the first check. Every
  `gate_row.py` invocation in this pass carried a scratch `--ledger`.
- **HEAD** `038dc27b50859cb30542b91683688a1f52ce5d66`, unmoved. **Stash** 0.
- **`git diff -- skills/`** is 0 lines. No file under review was modified, which is
  the claim the header made about itself and is now checked.
- **`git --no-optional-locks status --porcelain --untracked-files=all`** is 10
  lines: one modified `AGENTS.md` that predates this campaign and is untouched by
  it, eight untracked `docs/ultrareview/` files with this record among them, and
  `scratchpad/c8-intake.md`. Nothing is staged, committed, merged, pushed, or
  gated.
- **Pointer verification of this file, on this turn.** Every `` `path:line` ``
  pointer was resolved against `git ls-files` by unique suffix match and its line
  checked non-blank: **87 distinct pointers, 116 instances, 2 failures**, counted
  with these two bullets in place, after
  every bare `SKILL.md:NN` shorthand was written out across eighteen lines, because
  both a `herdr-delivery-workflow/SKILL.md` and an `ultra-review-receive/SKILL.md`
  are cited in this record and a bare pointer resolves to neither — the ambiguity
  S5 F024 records, reproduced here and fixed here. **Both failures are one
  pointer,** `iteration-19/HANDOFF.md:81-84`, cited twice: in F005 and in this
  paragraph. It fails against the index and resolves on disk at
  `skills/herdr-delivery-workflow-workspace/iteration-19/HANDOFF.md`, which
  `.gitignore:16` hides. A pointer checker built on `git ls-files` cannot see it,
  which is the defect F009 confirms — now in the instrument as well as in the
  doctrine.
- **Quote verification of this file, on this turn.** 240 double quotes, even
  parity, longest pair span 413 characters. **102 quoted strings of 12 characters
  or more; 96 match a tracked file, the S1 report, or the gitignored handoff, and
  none of the other 6 is a quotation of a source**: `src/fabricated.py` and
  `not typed by any Human` are arguments this pass typed into scratch commands,
  `Who staffs it: Lead` is a table header joined to its cell rather than a literal
  line, and the last two are this record's own wording — the replacement phrase
  proposed in F012 and a heading in the Instrument Log, and the sixth is the
  misquotation named below, reproduced here so the correction is legible. **Three
  quotation defects
  were found by this check and fixed on this turn:** `lead-policy.md:64` had been
  quoted as "work has been set aside outside the record" where it reads
  "a new stash means work has been hidden from porcelain";
  `ultra-review-receive/SKILL.md:24` had been cut at a full stop the source does not
  carry; and the nested `Approval dialogs` inside the
  `human-gates-and-closeout.md:13` quotation had been re-punctuated.
- **Scratch artifacts** live under the session scratchpad, outside the repository
  and outside `~/.herdr/`: one git repository, one bare origin, and seven scratch
  ledgers. The scratch repository was left on `main` after the `a|b` and `feat@v2`
  branches were created in it.

No delivery, merge, push or deploy is authorized by this pass.
