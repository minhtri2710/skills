# Ultra Review Receive: s2-ultra-review-pair Round 1

Report received: `docs/ultrareview/26-09-06-s2-ultra-review-pair-round-1.md`
Report sha256: `04e33e7b1b86c828eba771c73789297afdf3b068fa979ac60f0ff990d1cecb9d`, 934 lines
Findings in the report: 46 (`grep -c '^### F[0-9]' `), ids F001-F046 contiguous
Receiver: `lead-beo-skills`, solo-Lead, no Peer staffed
Mode: **verification only.** No source file is edited by this pass. `Files changed: none` on every
row below, and that claim is checked against `git diff -- skills/` in the Custody section.
Date: 26-09-06

**C12 disclosure, stated before the first disposition.** This report's findings are *about*
`ultra-review-receive`, and the instrument this pass runs is `ultra-review-receive`. The instrument
is grading its own report card. Three consequences are accepted rather than smoothed over:

1. Where a finding names a defect in the receive skill, the primary evidence for it is what this pass
   and the S1 pass **did** when they ran under that skill, not a fresh reading of the skill's prose.
   The S1 receive record's Instrument Log
   (`docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1-receive.md`, sha256
   `e3a53b3bcd6671db221050edc22191e915d36e66a93e9b42490ab0267d0ec697`, 995 lines) was written before this report
   was opened, by the same seat, without S2's findings in view. It is cited below as first-party
   evidence for F005, F006, F007, F017, F019, F024, F026 and F040, and each such row says so.
2. A finding this pass cannot verify without changing the skill is not fixed to make it verifiable.
   The skill is run as written.
3. Where the instrument's own defect shaped this record, the row says which defect and where.

**Input contract.** `ultra-review-receive/SKILL.md:12` requires a Metadata header, a Prior Round
Guard, findings identified `F001`-style, a Verification Queue, and a Strongest Reason Not To Merge
Yet. All five are present at `:1-13`, `:40`, `:59`, `:820` and `:875` of the report. `:14` requires
blocking a malformed report; this one is not malformed and is not blocked. Two departures the report
discloses about itself are accepted as disclosed rather than treated as malformation: five metadata
lines the script does not write were added by the coordinator (the report's own F036), and the
mandated closing sentence at `## Next Receive Prompt` is reproduced and then explicitly revoked
rather than used as the report's last words (the report's own F001).

## Dispositions

### F001 [P1] — CONFIRMED

- **Decisive evidence, read on this turn.**
  `create_ultra_review_report.py:102` is inside the returned f-string with no
  conditional above it and no branch anywhere in `markdown_template()`: `Use
  $ultra-review-receive to verify {report_path.as_posix()} and implement confirmed
  owner-clean fixes.` The only interpolation is `report_path`. `ultra-review/SKILL.md:129-133`
  mandates that exact string as the report's closing text, in a fenced `text`
  block. `ultra-review-receive/SKILL.md:36` reads "Verification does not imply
  write permission … Apply a fix only when the current request explicitly
  authorizes remediation and the files are within the caller's writable scope."
  The generated closing line contains the authorizing words, and `:36` names no
  requirement that the authorization originate outside the artifact.
- **The disconfirming check was run in full and returns nothing that falsifies it.**
  `sed -n '95,133p' skills/ultra-review/SKILL.md` carries no `--audit-only`, no
  mode branch and no alternate closing form; the script has no argument that
  changes `:102`; `ultra-review-receive/SKILL.md:30-40` has no clause about the
  provenance of the request; `ultra-review-receive/agents/openai.yaml:4` hedges
  ("implement **only explicitly authorized** owner-clean fixes") while the string
  written to disk does not, exactly as the finding says.
- **`the caller's writable scope` is undefined, as filed.** It occurs once in the
  whole skill, at `:36`, and is not among the Required Input at `:12`.
- **The first-party instance holds and has since been disclosed in the artifact.**
  `docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1.md`'s `## Next
  Receive Prompt` carries the sentence truncated before "and implement confirmed
  owner-clean fixes", followed by a block headed "**Disclosure added 26-09-06.**"
  that names the removal, calls it correct on the merits and unauthorized as a
  deviation, and points at this finding. The finding's closing claim — "A dated note has been added to S1 recording the
  third fact." — is true at this head.
- **Files changed:** none. **Validation:** the four reads of the disconfirming
  check plus the two greps above. **Reviewer evidence:** none staffed; the text is
  mechanical and not disputed. **Remaining blocker:** none for verification.

### F002 [P1] — CONFIRMED, with one sub-claim not re-derivable at this head

- **Decisive evidence.** `awk 'NR>=56 && NR<=103' create_ultra_review_report.py |
  grep -n 'mode\|sha256\|scout_count\|directive_count'`, run on this turn, returns
  exactly one line — `30:Plausible failure mode:`, the template's own literal
  subfield label, not the `mode` parameter. Zero of the four parameters is
  interpolated. All four are declared at `:47-54`, all four are passed from
  `main()` at `:169-174`, and the JSON at `:177-189` carries three of them
  (`review_brief_sha256`, `scout_count`, `directive_count`) to stdout but not
  `mode`, and stdout is not the artifact.
- **`--mode`'s help text is affirmatively false.** `:121`: "Review execution mode
  recorded in the artifact." It is recorded nowhere — not in the file, not in the
  JSON.
- **Corroborated against output.** `grep -c 'sha256'` over the S1 report returns 0
  and over this report returns 8; every one of the 8 is coordinator-added prose or
  a finding, not generated text. The S1 report contains the string `brief` 0 times.
- **The digest cannot be validated by the script, and this is structural.** The
  only check is `re.fullmatch(r"[0-9a-f]{64}", args.review_brief_sha256)` at
  `:144`. No argument names the brief file, so there is nothing to hash and nothing
  to compare. That half needs no anecdote.
- **The C-02 anecdote is not re-derivable at this head, and does not carry the
  finding.** F002 states the value passed at scaffold time was
  `bf8fa48164b2305393dac8b43c03e3fa3198263574f5e4b5eb05bca6d8a4e4a2`, one character
  off. Derived on this turn: `shasum -a 256
  skills/ultra-review-workspace/campaign-01/S2-BRIEF.md` is
  `bf8fa48164b2305293dac8b43c03e3fa3198263574f5e4b5eb05bca6d8a4e4a2`, and the
  report's own header at `:10` carries that same correct value. If a wrong digest
  was typed at the command line it left no trace in any artifact — which is the
  finding's point, but it means the incident is asserted rather than shown. The
  structural claim above is what this row confirms.
- **Files changed:** none. **Validation:** the awk/grep above, the two `shasum`
  runs, and the four line reads. **Reviewer evidence:** none staffed. **Remaining
  blocker:** none for verification.

### F003 [P1] — CONFIRMED, and the first-party breach is larger than filed

- **Decisive evidence.** `ultra-review/SKILL.md:52`: "The coordinator may create
  exactly one report under `docs/ultrareview/` and no other workspace artifact."
  Read in full, the sentence is a permission with an explicit exclusion, not a
  silence. `:16` fixes the scout count at ten; `:107` requires preserving every
  candidate; `:12` and `:106` forbid the Raw Candidate Ledger and the Scout
  preservation counters. The disconfirming check asks whether `:52` carries an
  exception clause for gitignored custody; read on this turn, it carries none.
- **The breach count is 13, not five.** `find skills/ultra-review-workspace/campaign-01
  -type f | wc -l`, on this turn: **13** — one `INTAKE.md`, six `S*-BRIEF.md` and
  six matching `S*-CANDIDATES.md`. Enumerated rather than counted: `INTAKE.md`, `S1-BRIEF.md`, `S2-BRIEF.md`,
  `S3A-BRIEF.md`, `S3B-BRIEF.md`, `S4-BRIEF.md`, `S5-BRIEF.md`,
  `S1-CANDIDATES.md`, `S2-CANDIDATES.md`, `S3A-CANDIDATES.md`,
  `S3B-CANDIDATES.md`, `S4-CANDIDATES.md`, `S5-CANDIDATES.md`. The finding named
  five because it was written at S2; the campaign has since produced eight more.
  `delivery-01/` holds four further files and predates this campaign, so it is not
  counted against it.
- **The survival argument is first-party and this seat can attest to it directly.**
  This is the fifth compaction of the campaign and the second on a fresh seat. The
  candidate rows for every slice after S1 survived those compactions because they
  were on disk in a file `:52` forbids. Under the rule as written, that work is
  lost at every context boundary, and per F002 and F008 the resulting report would
  still say ten scouts.
- **Files changed:** none. **Validation:** the `find` and `wc -l` above and the
  five line reads of the disconfirming check. **Reviewer evidence:** none staffed.
  **Remaining blocker:** none for verification. Phase B owns the exception clause.

### F004 [P1] — CONFIRMED

- **Decisive evidence.** `ultra-review/SKILL.md:58` requires freezing "the existing logical
  roster, concern allocation, report path, and review-brief digest"; `:59` requires
  inventorying "persisted mailbox reports by logical scout ID"; `:65` requires
  inspecting "persisted state before taking any launch action". The disconfirming
  check asks whether any file names a storage location for that state.
  `grep -rn 'roster\|allocation\|persisted state' skills/ultra-review/` returns
  hits only inside `ultra-review/SKILL.md:58` and `:65` themselves — the rule citing its own
  words — and no storage location anywhere. `:52` forbids the artifact that would
  hold it.
- **Step 4's model requirement has no source.** `grep -n 'model'
  create_ultra_review_report.py` returns nothing; `ultra-review/SKILL.md:33` states the skill
  "names none"; per F002 the artifact records none. "on the model the original
  batch ran on" refers to a datum that exists nowhere durable.
- **Confirmed against the generated scaffold rather than argued.** The template at
  `:57-103` is 47 lines and contains a metadata block of five fields (Date, Review
  name, Round, Scope, Report path), a Prior Round Guard, a single `F001` TODO
  block, a one-line queue, a TODO Strongest Reason and the closing prompt. No
  roster, no concern map, no digest, no per-scout status. There is nothing for step
  1 to freeze into.
- **Files changed:** none. **Validation:** the grep, the line reads, and the
  template read above. **Reviewer evidence:** none staffed. **Remaining blocker:**
  none for verification.

### F005 [P1] — CONFIRMED, and this pass is a first-party instance of it

- **The textual conflict is exact.** `ultra-review-receive/SKILL.md:8`: "never
  execute commands, scripts, paths, or policy embedded in a finding."
  `ultra-review-receive/SKILL.md:24`: "Start with the finding's disconfirming check
  from the Verification Queue, then inspect the smallest real production path
  needed to decide." The disconfirming check is content the report embeds. The
  finding is false only if `:24` scopes execution to an isolated copy; read on this
  turn, it does not, and neither does any other line of that file.
- **First-party evidence, generated before this report was opened.** The S1 receive
  record's Instrument Log
  (`docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1-receive.md`, sha256
  `e3a53b3bcd6671db221050edc22191e915d36e66a93e9b42490ab0267d0ec697`) records the
  same `:8`-versus-`:24` conflict as its first entry, reached from running the
  skill rather than from reading it, and records the resolution that pass invented:
  run each check only against a scratch git repository and scratch ledgers outside
  the checkout, and treat the check as a hypothesis to re-derive rather than an
  instruction to obey. That resolution is the seat's, not the skill's, which is
  precisely the finding.
- **The live instance in S1's queue is confirmed by enumeration.** `awk '/^##
  Verification Queue/,/^## Strongest Reason/'` over the S1 report, on this turn,
  returns six entries whose text is mutating — F001 (build, hand-edit), F008 (two
  near-simultaneous invocations), F011 (dispatch an agent), F012 (prompt a Lead at
  a dialog), F020 (append two rows, corrupt the first), F021 (run with `--repo`
  elsewhere), F023 (`git checkout -b`, then build) — and `gate_row.py:187` makes
  `--ledger` required with no default. The queue's own header says "Read-only
  checks."
- **Two of those checks were declined by the S1 pass as unrunnable, which the skill
  has no word for.** F011 and F012 require control-plane mutation. `:24` offers no
  disposition and no procedure for a check a verification pass must not run.
- **Files changed:** none. **Validation:** the two line reads, the awk enumeration,
  the `grep -n 'required=True'` on `gate_row.py`, and the S1 receive record's own
  Instrument Log. **Reviewer evidence:** none staffed. **Remaining blocker:** none
  for verification.

### F006 [P1] — CONFIRMED

- **Decisive evidence, the finding's own check run on this turn.**
  `grep -c '^### F[0-9]'` over the S1 report returns **28**; `awk '/^##
  Verification Queue/,/^## Strongest Reason/' | grep -c '^- \*\*F'` returns **16**.
  Equal counts would falsify the finding; they are not equal. The twelve absent
  ids, derived from the difference of the two sets: F013, F014, F016, F017, F018,
  F019, F022, F024, F025, F026, F027, F028 — exactly the twelve the finding names.
- **`ultra-review/SKILL.md:116` is the violated contract, read in full:** "Build a
  Verification Queue containing every finding and its read-only disconfirming
  check."
- **First-party consequence, already realised.** The S1 receive pass took the
  twelve missing entries from each finding's own `Disconfirming check:` field
  inside the Findings block, because the queue had nothing to offer — the exact
  improvisation the finding predicts. For F027 even that was unavailable (F007), so
  that pass constructed seventeen checks itself and disclosed the construction.
- **Files changed:** none. **Validation:** the two counts above and the set
  difference. **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F007 [P1] — CONFIRMED, and its count is right where my own S1 receive record was wrong

- **Decisive evidence, counted on this turn.** Over the S1 report:
  `grep -c '^### F[0-9]'` is 28, while `grep -c` for each of `^Contract violated:`,
  `^Plausible failure mode:`, `^Durable solution hypothesis:` and
  `^Disconfirming check:` is **27** each, and `^Severity:`, `^Source pointer:` and
  `^Evidence:` are 28 each. Exactly one finding is missing exactly those four
  fields. Reading `### F027` through `### F028` confirms it is F027: it carries
  `Severity: P3 | Confidence: mixed`, `Source pointer: as listed`, `Evidence:`, and
  then ends.
- **The bundle is 17, and the finding is right.**
  `awk '/^### F027/,/^### F028/' <s1> | grep -c '^- '` returns **17** on this turn.
  **The S1 receive record stated sixteen while enumerating nine run, seven not run
  and one uncorroborated** — seventeen. That record's own count disagreed with its
  own enumeration, which is the defect `herdr-delivery-workflow/SKILL.md:70`
  describes, committed by the pass that verified the report containing it. It has
  been corrected in that record on this turn, in both places, with the correction
  named and attributed to this finding.
- **The disposition conflict the finding predicts is not hypothetical.** The S1
  receive pass could not assign one disposition honestly: it ran nine sub-claims,
  named seven it did not run, and recorded one (`engineer-args`) it could not
  corroborate as stated — three different epistemic states under a single
  `CONFIRMED`.
- **Files changed:** none in `skills/`. One correction was applied to
  `docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1-receive.md`, a
  campaign record and not a file under review; the Custody section re-derives
  `git diff -- skills/` to show no reviewed file moved. **Validation:** the six
  counts above. **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F008 [P1] — CONFIRMED

- **Decisive evidence.** `--scout-count` is validated only by
  `args.scout_count <= 0` at `:147`, and `--directive-count` only by `< 0` at the
  same line. Per F002 neither reaches the artifact. The documented invocation at
  `ultra-review/SKILL.md:95` carries the literal `--scout-count 10`, so the number is typed by
  the launcher and never measured against anything that returned.
- **The finding's own falsifier fails to fire.** It is false if any finding
  subfield records a concern ID. `grep -n 'concern' skills/ultra-review/SKILL.md`
  returns six lines — `:21`, `:34`, `:35`, `:45`, `:46`, `:58` — every one about
  assigning concerns to scouts, none about recording one in a finding. `grep -c
  '^Concern'` over all nine files in `docs/ultrareview/` returns 0 in every file.
  The seven mandatory subfields at `ultra-review/SKILL.md:109-115` contain no concern field.
- **The count gate exists only on the recovery path.** "After all ten logical
  scouts complete, consolidate once" is `:63`, inside Restart Recovery. `##
  Finding Consolidation` at `:104-116` states no count gate at all.
- **The three-scouts-per-directive rule is unsatisfiable above three directives, as
  filed**, since `:27` requires three scouts per directive against `:32`'s exactly
  ten, and `:147` bounds `--directive-count` only at `>= 0`. This slice is the
  demonstration in the other direction: ten concerns over ten scouts still did not
  give every scout one, which is this report's own F046.
- **Files changed:** none. **Validation:** the two greps, the line reads at `:16`,
  `:95`, `:106`, `:116-117`, `:147-149`, and the nine-file `grep -c`. **Reviewer
  evidence:** none staffed. **Remaining blocker:** none.

### F009 [P2] — CONFIRMED

- **The finding's own falsifier fails to fire.** It is false if any of
  `ultra-review/SKILL.md:33`, `:41-51`, `:118-122` names where the model choice is recorded.
  `grep -rn 'model' skills/ultra-review/` on this turn returns **two lines in the
  whole skill directory**: `:33`, which states the rule and says "this skill names
  none", and `:61`, which *consumes* the datum — "on the model the original batch
  ran on". A rule and a consumer, and no producer, no channel and no store. The
  Scout Packet at `:41-51` has eight items and none is a model; the Report Shape at
  `:118-127` lists five metadata fields and none is a model.
- **The rule binds scouts and sub-agents, not the coordinator, and this run is the
  live instance.** `:33` says "every scout and sub-agent". This report's own header
  records scouts on `sonnet` and the coordinator on Opus 5. Clustering is the
  judgement-heavy step and it is outside the rule.
- **The rationale has no consumer, as filed.** `:106` groups by root cause and
  discards multiplicity; `ultra-review-receive/SKILL.md:32` forbids confirming from
  scout count. Nothing downstream converts cross-scout agreement into confidence.
- **The first-party correction is real and already applied.**
  `skills/ultra-review-workspace/campaign-01/INTAKE.md:97-98` carries a paragraph
  headed "**Corrected 26-09-06.**" stating that the earlier wording wrongly claimed
  `ultra-review/SKILL.md:33` asks the caller to name the model in each report's metadata.
- **Files changed:** none. **Validation:** the recursive grep, the three line-range
  reads, and the `INTAKE.md` read. **Reviewer evidence:** none staffed. **Remaining
  blocker:** none.

### F010 [P2] — CONFIRMED, and the first-party exposure is real at this head

- **Decisive evidence, the finding's own check re-implemented in a scratch
  `python3 -c` that opened no project file.** Rebuilding
  `ROUND_RE_TEMPLATE = r".*-{name}-round-(\d+)\.md$"` and the
  `*-{review_name}-round-*.md` glob and running both over a synthetic name list:
  with `review_name="fix"`, **both** the regex and the glob match
  `26-01-01-auth-fix-round-3.md`. Zero false matches would falsify the finding;
  there were two matches where one was intended, and the glob prefilter agrees with
  the regex on the false one, so neither catches the other.
- **The first-party exposure was verified, not assumed.** With
  `review_name="herdr-delivery-workflow"`, the same pattern matches this
  repository's `26-09-06-s1-herdr-delivery-workflow-round-1.md`. A Phase B review
  named `herdr-delivery-workflow` — the obvious name for it — would start at round
  2 and list this campaign's S1 report as its own prior round.
- **The key is the name alone.** `next_round(report_dir, review_name)` at `:29`
  takes no scope and no digest; `main()` passes neither.
- **Files changed:** none. **Validation:** the scratch re-implementation above and
  the reads of `:18` and `:29-40`. **Reviewer evidence:** none staffed. **Remaining
  blocker:** none.

### F011 [P2] — CONFIRMED

- **Decisive evidence, re-implemented in a scratch process.** `slugify` over
  `"Auth Fix"`, `"AUTH-FIX"`, `"Auth/Fix"`, `"auth-fix"` returns `'auth-fix'` for
  all four. Four distinct outputs would falsify the finding; there is one output.
- **The second half of the title holds too, by reading the order in `main()`.**
  `slugify` runs at `:143`; `next_round` at `:156`; the round number is baked into
  `relative_report_path` at `:157` and the file is written at `:193`; the JSON
  carrying `review_name` and `round` is printed at `:195`, after the write. The
  caller never sees the resolved slug before the round is committed.
- **Files changed:** none. **Validation:** the scratch probe and the `main()` order
  read above. **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F012 [P2] — CONFIRMED

- **Decisive evidence, re-implemented in a scratch process.** `slugify` over
  `"!!!"`, `"   "` and `"日本語レビュー"` raises `ValueError: review name slug is
  empty` in all three cases. In `main()` the call at `:143` is unguarded, so the
  exception propagates through `SystemExit(main())` at `:203` as a traceback and
  exit 1.
- **The convention it breaks is applied five times in the same function.**
  `:139-141` (workspace missing, return 2), `:144-146` (bad digest, 2),
  `:147-149` (bad counts, 2), `:150-153` (bad date, 2), `:160-162` (existing
  report, 3). Every one is `print(..., file=sys.stderr); return N`. `slugify` alone
  raises.
- **Files changed:** none. **Validation:** the scratch probe and the six line-range
  reads. The script itself was not invoked. **Reviewer evidence:** none staffed.
  **Remaining blocker:** none.

### F013 [P2] — CONFIRMED

- **Decisive evidence, from the code path rather than from running it.**
  `next_round` at `:29-40` returns `prior[-1][0] + 1` whenever any prior round
  exists, with no argument and no mode that suppresses the increment. The overwrite
  guard at `:160-162` tests `report_path.exists()` — and `report_path` is built at
  `:157-158` from the **already incremented** `round_number`, so on a re-run it
  tests a filename that by construction does not exist yet and cannot fire. The
  disconfirming check asks whether any of `ultra-review/SKILL.md:54-65` or the script names a
  resume mode; read on this turn, none does.
- **`ultra-review/SKILL.md:56` states the intent the default defeats:** a restart notice "is a
  recovery trigger, not permission to restart the review from scratch." Restart
  Recovery never says not to re-run the script, and the script's behaviour when it
  is re-run is to start from scratch under a new number.
- **The spurious file is permanent input.** `next_round`'s glob and regex match any
  `*-<name>-round-*.md`, with no test for content, so a half-written scaffold is
  returned in `prior_reports` and listed under "Previous reports read" forever.
- **Files changed:** none. **Validation:** the three line-range reads and the
  control-flow trace above; the script was not invoked. **Reviewer evidence:** none
  staffed. **Remaining blocker:** none.

### F014 [P2] — CONFIRMED

- **The finding's own falsifier is loose, and was resolved by reading rather than
  by counting hits.** Its queue entry ends "Any named bound falsifies it."
  `grep -n 'cap\|timeout\|attempt' skills/ultra-review/SKILL.md` returns exactly
  one line, `:62` — "A replacement attempt continues the same logical scout ID;
  never create an eleventh logical scout or duplicate completed work." That is an
  identity rule, not a bound: it caps the number of concurrent logical scouts at
  ten and says nothing about how many times one may be replaced, how long to wait,
  or what to do when a scout never returns. No retry cap, no timeout and no
  authorized fallback below ten exists in the file.
- **The gate is `:63` and it is unconditional:** "After all ten logical scouts
  complete, consolidate once into the existing report." `:56` names exactly one
  non-completion trigger, "A system notice that subagents or background tasks stopped due to a server
  restart". A scout that times out, errors silently, or
  returns a refusal matches no named trigger.
- **`revive` versus `restart`, as filed.** `:61` offers both verbs for the same
  action without distinguishing them, and no mechanism in the skill resumes a
  killed subagent's partial work.
- **Files changed:** none. **Validation:** the grep above and the read of
  `:54-65`. **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F015 [P2] — CONFIRMED

- **Decisive evidence.** `grep -n 'logical scout\|missing'
  skills/ultra-review/SKILL.md` on this turn returns five lines — `:59`, `:61`,
  `:62`, `:63` and `:81`. Four of them *use* the term "logical scout" and the fifth
  (`:81`) is the unrelated Search Surface bullet "missing essential mechanisms".
  The term is used four times and defined zero times, and "missing" at `:61` has no
  predicate: no deadline, no liveness test, no mailbox state that counts as absent.
- **The "exactly once" guarantee names no mechanism.** `:60` requires preserving
  every completed report exactly once; `:62` forbids an eleventh logical scout but
  is silent on two live agents under one ID; nothing supplies a tie-break when both
  return.
- **The late report has no path in.** `:63` fires consolidation once; nothing
  reopens it. `ultra-review/SKILL.md:10`'s "Never filter a candidate out of the artifact" is
  then violated by omission rather than by a decision, and per F008 nothing records
  that it happened.
- **Files changed:** none. **Validation:** the grep and the read of `:58-63`.
  **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F016 [P2] — CONFIRMED, and this pass is producing the invisible artifact

- **Decisive evidence, the finding's own check run on this turn.**
  `grep -rn 'receive.md' skills/ultra-review/SKILL.md
  skills/ultra-review-receive/SKILL.md
  skills/ultra-review/scripts/create_ultra_review_report.py` returns **exactly one
  line**: `ultra-review-receive/SKILL.md:47`, and there only as an output. A second
  hit as an input would falsify the finding; there is none.
- **The structural invisibility was reproduced, not inferred.** In a scratch
  `python3 -c`, `ROUND_RE_TEMPLATE` with `name="s1-herdr-delivery-workflow"`
  matches `26-09-06-s1-herdr-delivery-workflow-round-1.md` and does **not** match
  `26-09-06-s1-herdr-delivery-workflow-round-1-receive.md`. The receive record can
  never enter `prior_reports`, and `ultra-review/SKILL.md:88` tells the Prior Round Guard to
  read earlier reports, not receive records.
- **First-party: this campaign is generating the problem right now.** Two receive
  records exist at this head, and neither is reachable by any mechanism in either
  skill. Whatever this pass disproves, a Phase B round 2 of the same review name
  will re-surface with no warning.
- **Files changed:** none. **Validation:** the recursive grep, the scratch regex
  probe, and the read of `:86-88`. **Reviewer evidence:** none staffed. **Remaining
  blocker:** none.

### F017 [P2] — CONFIRMED, on first-party evidence generated before it was read

- **Decisive evidence.** `grep -n 'receive record' skills/ultra-review-receive/SKILL.md`
  returns one line, `:47`: "If a durable receive record is requested, write
  `<report stem>-receive.md` beside the report." That is the whole specification —
  a conditional trigger, a filename, and a location. No template, no required
  fields, no round or version discipline, and no authorization clause. `:36`'s
  write gate is about source edits and does not reach it.
- **The first-party instance predates this finding's reading.** The S1 receive
  record's Instrument Log recorded, independently, that `:47` makes the durable
  record conditional on a request; that no one requested one; and that it was
  written anyway because dispositions that live only in a pane die with the pane.
  This record is the second such unrequested write. Both are tracked-directory
  files produced by a pass whose own header says it edits nothing.
- **The clobber risk is structural, not speculative.** The filename is a pure
  function of the report stem, so a second receive pass over the same report writes
  the same path. There is no round number in it and no rule about appending.
- **Files changed:** none under `skills/`. **Validation:** the grep and the two
  line reads. **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F018 [P2] — CONFIRMED

- **Decisive evidence, both lines read in full on this turn.**
  `ultra-review-receive/SKILL.md:24` ends "Assign exactly one disposition:".
  `:42` is item 3 of the numbered list at `:38-46`, whose lead-in at `:38` is "For
  each authorized `CONFIRMED` finding:", and it reads "Do not add compensation
  around an out-of-scope broken foundation; mark it `BLOCKED` and escalate." A
  finding that has already been assigned `CONFIRMED` is instructed, inside the
  `CONFIRMED` branch, to be marked `BLOCKED`. No transition graph exists anywhere
  in the file.
- **Files changed:** none. **Validation:** the reads of `:24`, `:38` and `:42`.
  **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F019 [P2] — CONFIRMED, on first-party evidence from the S1 pass

- **Decisive evidence.** The five dispositions at `:26-30` were read in full.
  `CONFIRMED` requires both that behaviour violates the contract **and** that there
  is "an in-scope durable owner"; `DISPROVEN` requires decisive evidence ruling the
  failure out. A finding that is certainly true and has no in-scope owner satisfies
  neither, and lands in `BLOCKED` — whose definition is a list of missing things.
  Certainty-without-a-home and absence-of-evidence share one label.
- **First-party corroboration from the S1 pass, recorded before this report was
  opened.** Its Instrument Log's fifth entry reads that no disposition fits "the
  defect is real and the finding's pointers are wrong", and names five findings
  that needed a correction recorded inside a `CONFIRMED` row. That is the
  partly-true / confirmed-but-narrower case this finding names, met in practice.
  The same pass met the certainty-without-a-home case at S1 F027, where nine
  sub-claims were confirmed, seven unrun and one uncorroborated under one label.
- **One narrowing.** The finding's BLOCKED-collapse argument is right about the
  conflation but slightly overstates the closure: `:29` lists five distinct missing
  things (evidence, environment, contract, authorization, ownership), so BLOCKED
  can at least name *which* is missing in prose. It has no field for it, and the
  vocabulary still cannot distinguish "true, unownable" from "undecided" at the
  disposition level. The defect stands; its shape is a missing sub-field rather
  than a wholly absent concept.
- **Files changed:** none. **Validation:** the read of `:26-30` and the S1 receive
  record's Instrument Log. **Reviewer evidence:** none staffed. **Remaining
  blocker:** none.

### F020 [P2] — CONFIRMED

- **Decisive evidence, all three lines read in full.** `:28` is the entire
  specification of the disposition: "`DUPLICATE`: same root cause as another
  finding; keep the ID and point to it" No canonicality rule, no cycle rule, no
  severity-conflict rule. `:12` permits "any finding-ID restriction" with no
  requirement that a DUPLICATE's target be inside it. `:47` forbids modifying
  source for a DUPLICATE.
- **The worst case the finding names is reachable from those three lines alone.** A
  pass restricted to `F003` marks it DUPLICATE of `F007`; `F007` is outside the
  restriction so it is never dispositioned; `:47` forbids editing for `F003`; and
  `:53`'s completion row has no field that would show the gap.
- **Files changed:** none. **Validation:** the three line reads and the read of
  `:53`. **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F021 [P2] — CONFIRMED

- **Decisive evidence, both lines read in full.** `:53` enumerates the completion
  row's eight columns: "ID, disposition, decisive evidence, source pointers, files
  changed, validation and result, reviewer evidence, and remaining blocker." There
  is no severity column and no post-remediation column. `:55` then forbids claiming
  "a confirmed finding is fixed without an adequate behavior-level oracle" — a
  prohibition on asserting a state the row has no field to hold.
- **The severity half is confirmed by the same read.** `:26-30`'s five dispositions
  carry no severity, and nothing anywhere lets a verifier record that the scout's
  severity was wrong. Every row in this record inherits the report's P-level
  unexamined, which is the defect in operation.
- **Files changed:** none. **Validation:** the reads of `:26-30` and `:53-55`.
  **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F022 [P2] — CONFIRMED

- **Decisive evidence.** `grep -n 'independent' skills/ultra-review-receive/SKILL.md`
  returns exactly two lines and they state different triggers. `:20`: "Use one
  focused independent reviewer only for a materially disputed or high-risk
  finding." `:51`: "Require focused independent review for P0/P1, security,
  authorization, data integrity, concurrency, lifecycle, public-contract, or
  foundation changes." The word "only" at `:20` reads as a ceiling and the word
  "Require" at `:51` reads as a floor; neither cites the other, and no third line
  reconciles them.
- **Neither names the reviewer or handles disagreement.** No kind, no model, no
  independence criterion, and no arbitration rule; `:53`'s single row carries one
  disposition, so two verdicts cannot both be recorded in the contracted shape.
- **First-party, and disclosed rather than excused.** This pass staffed no
  independent reviewer for any of the P1 findings above. Under `:51` that is a gate
  not met; under `:20` it is defensible because nothing here is disputed. That the
  same pass can be both compliant and non-compliant on the same facts is the
  finding, met in practice. Every row below and above says "Reviewer evidence: none
  staffed" for exactly this reason.
- **Files changed:** none. **Validation:** the grep and the two line reads.
  **Reviewer evidence:** none staffed — see above. **Remaining blocker:** the
  unmet `:51` gate is recorded here and carried to Phase A ranking; it is not
  waivable by this row.

### F023 [P2] — CONFIRMED

- **Decisive evidence.** `grep -n 'escalat' skills/ultra-review-receive/SKILL.md`
  returns exactly one line, `:42`: "Do not add compensation around an out-of-scope
  broken foundation; mark it `BLOCKED` and escalate." No recipient, no mechanism,
  no completion condition, and the word occurs nowhere else in the file to define
  it. The half of the sentence that has a mechanism — marking BLOCKED — is
  satisfiable alone, and nothing detects that the other half was skipped.
- **The `materially disputed` trigger at `:20` presupposes a dispute the workflow
  does not produce.** The whole file describes a single verifier; no step creates a
  second opinion before `:20` is consulted. It can only fire when the verifier
  disputes the report with itself.
- **Files changed:** none. **Validation:** the grep and the reads of `:20` and
  `:42`. **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F024 [P2] — CONFIRMED, on first-party evidence from both passes

- **Decisive evidence.** `:18` requires that "callers, consumers, contracts, and
  lifecycle are reconstructed from current code" before a pointer counts as
  evidence — the activity most likely to surface something the report does not
  contain. `:32` requires preserving every original finding and forbids deleting or
  renumbering; `:47` forbids rewriting the original report; `:38`'s remediation
  list is scoped to an existing authorized `CONFIRMED`. Read together, the three
  leave a verifier-discovered defect with no carrier: not addable to the report,
  not a finding, not remediable.
- **First-party, twice.** The S1 receive pass discovered that S1 F009's fifth
  pointer was wrong and that a sixth site existed, that S1 F022's three assertion
  indices were each off by one, and that S1 F023's `~`-prefixed claim was wrong.
  None of those is a finding in any report; each survives only as prose inside a
  `CONFIRMED` row. This pass has added a seventh such discovery — S1 F002's
  first-party `G90` instance does not hold — with the same non-carrier.
- **No void protocol exists.** `:14`'s block is an input-time judgement about form.
  Nothing covers a report that parses cleanly and is unsound.
- **Files changed:** none. **Validation:** the three line reads and the two receive
  records. **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F025 [P2] — CONFIRMED

- **Decisive evidence, the finding's own check.**
  `grep -n 'restart\|resume\|recovery' skills/ultra-review-receive/SKILL.md`
  returns **no hits at all** over the whole 55-line file. Any hit would falsify the
  finding. The producer's `ultra-review/SKILL.md:54-65` is a twelve-line protocol
  for the same failure.
- **The asymmetry is the finding and it is asymmetric in the dangerous direction.**
  The producer's passes are read-only by `:52`; the consumer's may hold write
  authority under `:36`. The half that can leave a half-edited tree is the half
  with no resumption rule.
- **First-party, and disclosed.** This campaign has compacted five times. Nothing
  in the receive skill told this seat how to resume a receive pass; the resumption
  discipline used — re-derive every count on the turn it is written, and treat the
  written file as the only state — is this seat's, carried from
  `herdr-delivery-workflow`, not from the skill under review.
- **Files changed:** none. **Validation:** the grep above. **Reviewer evidence:**
  none staffed. **Remaining blocker:** none.

### F026 [P2] — CONFIRMED

- **Decisive evidence, all eight cited lines read on this turn.** On the receive
  side: `:14` blocks on the *report's* scope against the requested workspace; `:18`
  compares "the report scope, review name, and prior-round context with current
  source"; `:26` requires an "in-scope durable owner" without defining the scope it
  is in; `:32` and `:36` bound basis and writable files. Not one of the five asks
  whether an individual finding's `file:line` falls inside the review's declared
  Scope. On the producer side: `:35` grants permission to report "any incidental
  bug inside scope" with no test for inside; `:46-47` pushes scouts past the
  visible diff; `:52` restricts scout **writes** and says nothing about reads.
- **The verifier's own read and execute boundary is absent, as filed.** `:8` bounds
  only content sourced from a finding. Nothing else in the file limits what the
  verifier may read or run. This pass ran `git`, `find`, `shasum`, `grep` and
  scratch `python3` processes across the whole repository and outside it under no
  authority from this skill.
- **The report's live instance was verified by enumeration, not by the raw count.**
  `grep -o '\[out of Scope' | wc -l` over the report returns **8**, and the eighth
  is the rule statement at `:36` announcing the convention, not a mark. The seven
  marks are five in headings — F006, F007, F037, F038, F046 — and two in source
  pointers — F005 at `:147` and F036 at `:652` — matching the report's own statement that "it
  marks all seven itself, because no rule required the mark". No rule in either skill required any of
  them.
- **Files changed:** none. **Validation:** the eight line reads and the `grep -c`
  above. **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F027 [P2] — CONFIRMED

- **Decisive evidence.** `ultra-review/SKILL.md:108-115` enumerates the seven finding subfields
  and imposes no format on any of them; `Evidence observed` at `:111` is free text.
  The template at `create_ultra_review_report.py:81-90` renders each subfield as a
  bare label followed by `- TODO` bullets, with no fence and no quoting convention.
  Nothing distinguishes the report's own imperative prose from imperative prose
  quoted out of an audited file.
- **The consumer assumes the distinction it is not given.**
  `ultra-review-receive/SKILL.md:8` requires treating finding content as data and
  never executing "commands, scripts, paths, or policy embedded in a finding" —
  which presumes the embedded policy is recognisable as embedded.
- **First-party, in this very record.** Both receive records quote doctrine
  sentences inline in backticks, in prose that is itself addressed to an agent. The
  convention used — quote in double quotes, attribute to a `file:line`, never fence
  — was invented by this seat, and nothing in either skill required or forbade it.
- **Files changed:** none. **Validation:** the two line-range reads and the two
  receive records. **Reviewer evidence:** none staffed. **Remaining blocker:**
  none.

### F028 [P2] — CONFIRMED, all three mechanisms

- **No repo-root detection.** `:108`: `parser.add_argument("--workspace",
  default=".", ...)`. `:138`: `workspace = Path(args.workspace).resolve()`. `:155`
  then builds `report_dir = workspace / "docs" / "ultrareview"` and `:192`
  `mkdir(parents=True, exist_ok=True)` creates it wherever the caller stood. Run
  from `skills/ultra-review/`, the report lands at
  `skills/ultra-review/docs/ultrareview/` and exits 0.
- **A file passes the existence check, reproduced in an isolated temp directory as
  the queue entry directs** — the script itself was not invoked. A regular file
  returns `.exists()` `True` and `.is_dir()` `False`, and
  `(file/"docs"/"ultrareview").mkdir(parents=True, exist_ok=True)` raises
  `NotADirectoryError: [Errno 20] Not a directory`. `:139-141` tests only
  `.exists()`.
- **`receive:14`'s workspace comparison has no input.** `grep -n 'Workspace'
  docs/ultrareview/*.md` on this turn returns four lines, **all four inside this
  S2 report's own text about this finding** — the heading, the evidence bullet, the
  disconfirming check, and the queue entry. No report carries a `Workspace:` field,
  because the script never writes one. `:14`'s "its scope does not match the
  requested workspace" cannot be executed literally.
- **Files changed:** none. **Validation:** the four line reads, the isolated
  pathlib probe in a temp directory that was removed afterwards, and the `grep -n`.
  **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F029 [P2] — CONFIRMED

- **Decisive evidence, from reading rather than racing.** `:160-162` is
  `if report_path.exists(): print(...); return 3`. `:191-193` is
  `if not args.dry_run: report_dir.mkdir(...); report_path.write_text(content,
  encoding="utf-8", newline="\n")` — truncate mode. Thirty lines of work separate
  the test from the write. `grep -n "O_EXCL\|'x'\|lock"` over the whole script
  returns no hits; an `open(..., 'x')` or `O_EXCL` would falsify the finding. **The
  race was not reproduced**, per the queue's own instruction not to run two
  concurrent invocations.
- **The skill's own recovery section anticipates the concurrency.** `ultra-review/SKILL.md:65`
  tells a resumed coordinator to inspect persisted state before launching, with no
  ownership claim and nothing that lets a stale instance learn it lost the claim.
- **Files changed:** none. **Validation:** the two line-range reads and the grep.
  **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F030 [P2] — CONFIRMED

- **Decisive evidence.** `:168` passes `scope=args.scope.strip()`, and `:62` of the
  template is `Scope: {scope}` — a bare f-string interpolation into the metadata
  block, on the line directly above `Report path:` and four lines above the `##
  Prior Round Guard` heading. No escaping, no newline rejection, no length bound.
  The only validation `--scope` receives anywhere in `main()` is `.strip()`.
- **The consequence is structural, not cosmetic.** `ultra-review-receive/SKILL.md:12`
  requires reading the report by its sections; a `--scope` containing a newline and
  a `##` line adds a heading to the document the consumer parses.
- **Severity kept as filed.** The input is caller-supplied rather than
  scout-supplied, so this is a templating defect rather than the trust-boundary
  problem F005 describes. Recorded, not raised.
- **Files changed:** none. **Validation:** the two line reads. **Reviewer
  evidence:** none staffed. **Remaining blocker:** none.

### F031 [P2] — CONFIRMED on the host fact; the version half is narrowed

- **Decisive evidence, measured on this host on this turn.** `which python` prints
  "python not found" and exits 1. `which python3` prints
  `/opt/homebrew/bin/python3` and exits 0. `python3 --version` is `Python 3.14.7`.
  `ultra-review/SKILL.md:95` is `python scripts/create_ultra_review_report.py …`; the shebang at
  `:1` is `#!/usr/bin/env python3`. The documented command fails at the shell
  before any of the script's own error handling runs.
- **The version half is narrowed to what was checked.** `is_relative_to` appears at
  `:171` and `:182` and `write_text(..., newline="\n")` at `:193`; both are read in
  the source and both are documented as 3.9 and 3.10 additions. **No old
  interpreter was installed or run**, so this row confirms that no minimum version
  is declared anywhere — no `requires-python`, no docstring statement, no runtime
  check — and does not independently confirm the two version numbers. The scouts
  flagged the same limit; it is preserved rather than smoothed.
- **Files changed:** none. **Validation:** the three shell commands and the four
  line reads. **Reviewer evidence:** none staffed. **Remaining blocker:** none for
  the host fact.

### F032 [P2] — CONFIRMED

- **Decisive evidence.** `ultra-review/SKILL.md:100-102` reads "Replace every `TODO`. If scouts
  submitted no candidates, state `No candidates reported.`" The template at
  `:77-90` seeds a full `### F001 [P?] TODO short title` block with eight labelled
  lines, and `:94` seeds `- F001: TODO read-only check`. "Replace every TODO" and
  "state No candidates reported" do not say whether the skeleton is deleted,
  emptied, or left with its labels — three different documents, all defensible.
- **The consumer's rejection criterion is a single undefined word.**
  `grep -n 'malformed' skills/ultra-review-receive/SKILL.md` returns exactly one
  line, `:14`, and the word is defined nowhere in the file. A residual `TODO` or a
  `[P?]` token has no stated status: block, disposition, or ignore.
- **Files changed:** none. **Validation:** the two line-range reads and the grep.
  **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F033 [P2] — CONFIRMED

- **Decisive evidence, both lines read in full.**
  `ultra-review-receive/SKILL.md:45`: "Run the narrowest adequate validation, then
  expand only when boundaries require it." Neither "narrowest" nor "adequate" is
  defined anywhere in the file, and no other line supplies a comparator.
  `ultra-review/SKILL.md:88`: "Give relevant scouts concise warnings about confirmed
  fixes, rejected false positives, unresolved routes, and regression risks" —
  "relevant" has no test, and the file contains no rule for deciding which scouts
  qualify.
- **The `:88` half is the softer instance, as the scout said.** The criterion is
  inferable from the concern allocation, which does exist as a concept at `:21` and
  `:45`, but is never written as the test. Recorded at that strength rather than
  raised.
- **Files changed:** none. **Validation:** the reads of `:45` and `:86-88`.
  **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F034 [P2] — CONFIRMED, both halves

- **Decisive evidence, all four files read.**
  `ultra-review/agents/openai.yaml:3` is `short_description: "Artifact-based
  parallel review pipeline"` — no "ultra review", no "bug hunt", no "scout", none
  of the words `ultra-review/SKILL.md:3` uses to trigger. The `SKILL.md`
  description is properly trigger-phrased ("Use when the user asks for an ultra
  review, a scout-based bug hunt…"). The two describe the same skill by different
  criteria.
- **The second half is exact.** `ultra-review-receive/SKILL.md:3` triggers on a
  user who "asks to verify or triage ultra-review findings" — no path required.
  `:12`, the first operative line of the body, requires "the exact report path
  under the current repository's `docs/ultrareview/`", and `:14` blocks when it is
  absent. Nothing in the file resolves a report from a review name or a date. The
  description admits a caller the body immediately blocks, and offers no fallback.
- **Files changed:** none. **Validation:** the four line reads. **Reviewer
  evidence:** none staffed. **Remaining blocker:** none.

### F035 [P2] — CONFIRMED, but its disconfirming check is wrong and was corrected here

- **The check as written fires and should not have.** It says
  `grep -n 'sha256\|generated' docs/ultrareview/*.md` with "no hits is the defect."
  Run on this turn there are hits in seven of the nine files — 14 in this report, 5
  in S5, 4 in S3a, 4 in S4, 2 in S3b, 3 and 12 in the two receive records — and 0
  in the S1 report and 0 in the premise audit. Read rather than counted, **every
  hit is hand-typed**: coordinator-added `Review brief: … sha256 …` metadata lines,
  which are F036's improvisation, plus unrelated prose uses of the word
  "generated". Not one is written by `create_ultra_review_report.py`. A verifier
  who ran the check literally and stopped would have marked this DISPROVEN on
  evidence that proves the opposite.
- **Confirmed on the narrower ground the check should have named.** The script's
  template at `:57-103` emits no digest, no generator marker, no version and no
  workspace (F002 and F028), so the artifact carries no machine-checkable
  provenance. `ultra-review-receive/SKILL.md:14`'s admission test is "the exact
  report path under the current repository's `docs/ultrareview/`" plus the section
  headings at `:12`. Any hand-written markdown at that path with those headings is
  admitted.
- **Files changed:** none. **Validation:** the `grep -c` across all nine files, the
  read of each class of hit, and the reads of `:14` and the template. **Reviewer
  evidence:** none staffed. **Remaining blocker:** none.

### F036 [P2] — CONFIRMED

- **Decisive evidence.** `ultra-review/SKILL.md:120-127` names exactly six
  headings and lists the Metadata header's five fields — Date, Review name, Round,
  Scope, Report path. There is no seventh slot and no permitted extension. `:12`
  and `:106` forbid a "Raw Candidate Ledger", an "Execution Receipt", "Scout
  preservation counters" and "Merge Notes", and define none of the four.
- **Both instances are real and they differ, which is the finding.**
  `docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1.md:9-13` carries an
  un-headed paragraph between the metadata fields and `## Prior Round Guard`,
  holding scout count, model, subagent kind and custody notes. This report instead
  extended the Metadata header itself with five extra lines and disclosed the
  choice at `:14-19`. Two reports from one skill, two shapes, neither contracted.
- **The scout's own restraint is preserved.** The finding does not claim the S1
  paragraph *is* an "Execution Receipt", because the term is undefined; it claims
  the content sits outside the six contracted sections. That is the accurate
  statement and this row does not strengthen it.
- **Files changed:** none. **Validation:** the reads of `:12`, `:106`, `:118-127`,
  and of `:1-15` of the S1 report and `:1-19` of this one. **Reviewer evidence:**
  none staffed. **Remaining blocker:** none.

### F037 [P2] — CONFIRMED

- **Decisive evidence, the finding's own check.** `sed -n '732,752p'` over the S1
  report shows a section headed `### Recorded and not carried as findings` holding
  six bullets, none with an `F` prefix: the empty `files` field (declared retracted
  and adjudicated by the coordinator against the schema), citation integrity
  (declared clean), "No project-identity leak" (declared), branch lifecycle
  (declared out of scope), the Supervisor notebook (declared to need no rule), and
  candidate `C-01` (queued under a non-`F` id). `grep -n '^### F'` confirms the
  section's items are outside the F001-F028 numbering.
- **The violated contract reads exactly as the finding says.**
  `ultra-review/SKILL.md:12`: "Verification and rejection belong to
  `ultra-review-receive`." `:10`: "Never filter a candidate out of the artifact
  because it is speculative, unique, low-confidence, weakly evidenced, duplicated,
  or hard to classify." `:107`: "Preserve all unique or speculative bug candidates
  in `Findings`."
- **First-party consequence, already met.** The S1 receive pass had no disposition
  path for `C-01` and recorded it as "not a finding, no disposition" outside the
  F-numbered rows — precisely the exclusion this finding predicts.
- **Files changed:** none. **Validation:** the `sed` range, the `grep -n '^### F'`,
  and the three line reads. **Reviewer evidence:** none staffed. **Remaining
  blocker:** none.

### F038 [P2] — CONFIRMED, and already remediated in the record it is about

- **Decisive evidence.** `ultra-review/SKILL.md:33` reads in full: "run every scout
  and sub-agent on one model, chosen by the caller: this skill names none, and the
  overlap it depends on must come from assignment and search angle, never from a
  difference in model." It contains no reference to metadata and imposes no
  recording obligation.
- **The overstatement is confirmed from the corrected text itself.**
  `skills/ultra-review-workspace/campaign-01/INTAKE.md:97-98` now carries a
  paragraph headed "**Corrected 26-09-06.**" quoting the earlier wording — that
  naming the model here and in each report's metadata "is what that line asks of
  the caller" — and stating "It is not." The correction is dated and in place, so
  the defect is confirmed as having existed and as fixed in the campaign record.
- **`INTAKE.md` is a campaign record, not a file under review.** No source file was
  touched by that correction or by this row.
- **Files changed:** none. **Validation:** the two reads above. **Reviewer
  evidence:** none staffed. **Remaining blocker:** none; the durable half is F009.

### F039 [P3] — CONFIRMED

- **Decisive evidence.** `ultra-review/SKILL.md:120-122` says "Preserve these
  headings:" and lists "Metadata header (Date, Review name, Round, Scope, Report
  path)" as the first of six. `ultra-review-receive/SKILL.md:12` says "Read the
  whole report: Metadata header, Prior Round Guard, Findings…". The template at
  `create_ultra_review_report.py:57-63` emits `# Ultra Review: …` then a blank line
  then five bare `Key: value` lines — no `##`, no heading of any level. Two
  contracts name a heading the implementation does not emit.
- **Files changed:** none. **Validation:** the three reads. **Reviewer evidence:**
  none staffed. **Remaining blocker:** none.

### F040 [P3] — CONFIRMED

- **Decisive evidence.** `ultra-review-receive/SKILL.md:32` enumerates the
  disallowed bases: "scout count, report prose, source substring matches,
  compilation alone, mocks, synthetic fixtures, logs, acknowledgements, or queue
  drain." A finding's own assertion that it has already been verified is not among
  them, and `ultra-review/SKILL.md:111`'s `Evidence observed` is free text with no
  format constraint, so a scout can put such an assertion there.
- **The structural separation the scout credited is real and preserved.** The seven
  subfields at `:109-115` contain no disposition field, so a scout cannot write a
  disposition into the report. The gap is narrower than "a scout can self-confirm":
  it is that `:32`'s list is enumerative and one enabling case is missing from it.
- **Severity kept at P3.** "report prose" at `:32` arguably already covers an
  evidence assertion; the finding's point is that it is not named, and a rule that
  works by enumeration should enumerate it.
- **Files changed:** none. **Validation:** the reads of `:24-32` and `:108-115`.
  **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F041 [P3] — CONFIRMED

- **Decisive evidence, the finding's own check.** `grep -rn 'status\|queue'
  skills/ultra-review/SKILL.md skills/ultra-review-receive/SKILL.md` returns two
  lines, both in the receive skill: `:18`, "working-tree status", about git, and
  `:32`, "queue drain", in the disallowed-basis list. Neither is a handoff status.
  Nothing in `ultra-review/SKILL.md:129-133` or in the `default_prompt` at
  `skills/ultra-review/agents/openai.yaml:4` and
  `skills/ultra-review-receive/agents/openai.yaml:4`
  owns confirming that the receive step happened.
- **Observable at this head.** `docs/ultrareview/` holds nine files; two of them
  are receive records, and the only way to tell which reports have been verified is
  to look for a matching `-receive.md` by hand — which is the F016 mechanism that
  no rule requires and no code reads.
- **Files changed:** none. **Validation:** the recursive grep and the directory
  listing. **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F042 [P3] — CONFIRMED on the prose-invisibility half; the loop half is narrowed

- **Decisive evidence for the first half.**
  `skills/ultra-review-receive/agents/openai.yaml` carries
  `policy:\n  allow_implicit_invocation: false` at `:5-6`;
  `skills/ultra-review/agents/openai.yaml` has four lines and no `policy` key at
  all. `grep -n 'implicit' skills/ultra-review-receive/SKILL.md` returns **no
  hits**, so a prose statement would falsify the finding and there is none. The
  asymmetry is real and is invisible to anyone reading the two `SKILL.md` files.
- **Both readings of the design are carried, as the report carries them.** Gating
  the write-capable half to explicit invocation is defensible on its own terms, and
  scout-06 and scout-07 recorded it as a correct guardrail. This row confirms the
  *documentation* defect and takes no position on the policy, which is what the
  finding asks.
- **The loop half is narrowed to what the report itself already narrowed.**
  `:51`'s "materially new stable snapshot" has no comparator, and the scout that
  raised it downgraded it because both `default_prompt`s frame invocation as
  user-initiated. Confirmed as an underspecified threshold, not as an unbounded
  machine loop.
- **Files changed:** none. **Validation:** the two `cat`s, the grep, and the read
  of `:51`. **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F043 [P3] — CONFIRMED, with the second half's evidence source disclosed

- **The soft overlap holds.** `skills/test-proof-debt-audit/SKILL.md:3` reads
  "Audit one named behavioral claim and the test, validator, benchmark, or gate
  cited as proof. Do not use for ordinary implementation, failing tests, weak
  coverage, or the presence of mocks." `ultra-review/SKILL.md:79` offers
  "test/proof gaps, fake-pass evidence, and mocked production claims" as one of
  twelve lenses, and `:3` carries no exclusion pointing at the cheaper skill. The
  fence exists on one side only.
- **The `code-review` collision is real, and the check as written cannot find it.**
  The queue says `grep -rn 'ultra' ~/.claude/skills/code-review/SKILL.md` "if
  installed". Run on this turn: **that file does not exist**, and no `code-review`
  entry appears among the 24 directories under `~/.claude/skills/`. A marketplace
  plugin does exist at
  `~/.claude/plugins/marketplaces/claude-plugins-official/plugins/code-review`, and
  `grep -rn 'ultra'` over it returns **no hits** — that plugin has no "ultra"
  effort level. **The collision is nonetheless live, and the evidence is this
  session's own runtime rather than any file in this checkout:** the environment
  instructions this seat runs under describe `/code-review ultra` as a multi-agent
  cloud review of the current branch, with `/ultrareview` as a deprecated alias for
  the same command. The scout reached the collision from the text alone; this pass
  can confirm the command exists but cannot confirm it from a repository artifact,
  and says so rather than citing a file that does not exist.
- **The live instance the finding names is checkable and holds.**
  `skills/ultra-review-workspace/campaign-01/INTAKE.md` records the same ambiguity
  as a disclosure to the Supervisor before S1 launched — that the Human's words
  could have meant the built-in command rather than these project skills.
- **Files changed:** none. **Validation:** the two `:3` reads, the `ls` of
  `~/.claude/skills/`, the `find` and `grep` over the plugin directory, and the
  `INTAKE.md` read. **Reviewer evidence:** none staffed. **Remaining blocker:** the
  second half rests on runtime evidence that a later pass in a different
  environment may not be able to reproduce; that limit is recorded here rather than
  hidden.

### F044 [P3] — CONFIRMED

- **Decisive evidence.** `:151` is `re.fullmatch(r"\d{2}-\d{2}-\d{2}", date_slug)`
  and nothing else validates `--date`. Re-implemented in a scratch process on this
  turn, `"99-99-99"` matches. `date_slug` is then interpolated straight into the
  filename at `:157`, so the impossible date becomes the report's permanent sort
  key.
- **Files changed:** none. **Validation:** the read of `:150-153` and the scratch
  regex probe. **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F045 [P3] — CONFIRMED

- **Decisive evidence, traced rather than executed.** `prior_reports` is produced
  only by `next_round` at `:29-40`, whose sole source is
  `report_dir.glob(f"*-{review_name}-round-*.md")` at `:33`, and `report_dir` is
  `workspace / "docs" / "ultrareview"` at `:155`. Every path in the list is
  therefore under `workspace` by construction, so
  `path.relative_to(workspace) if path.is_relative_to(workspace) else path` at
  `:171` and again at `:182` can never take the `else` arm.
- **Severity and framing kept as filed.** The scout reported it under the
  no-suppression rule and did not claim it was worth fixing. This row confirms it
  as dead surface, not as a failure mode.
- **Files changed:** none. **Validation:** the read of `:168-185` plus `:29-40` and
  `:155`. **Reviewer evidence:** none staffed. **Remaining blocker:** none.

### F046 [P3] — CONFIRMED

- **Decisive evidence.** `ultra-review/SKILL.md:45` requires each Scout Packet to
  carry "assigned concern IDs and tailored search angles", and `:34` requires
  giving "every scout at least one assigned concern".
  `grep -oE 'G[0-9]{2}' skills/ultra-review-workspace/campaign-01/S2-BRIEF.md | sort
  -u` returns exactly ten distinct ids, `G01` through `G10`, and
  `grep -c 'G[0-9][0-9]'` over the same file returns 10 lines carrying them. The report
  header's own Directives line records the allocation: scout-03 carried G03 and
  G08, and scout-10 carried none.
- **The ten packets themselves are not in this checkout.** They were prompts, not
  files, so this pass verifies the concern list and the coordinator's own recorded
  allocation, not the dispatched text. The coordinator states the omission in the
  finding and again in the header; nothing at this head contradicts it, and nothing
  at this head independently corroborates the packet contents. Recorded so the
  strength of the evidence is not overstated.
- **The violation is this run's, not the skill's**, exactly as filed. The durable
  half is F008: no artifact field would ever have recorded it.
- **Files changed:** none. **Validation:** the two line reads, the `grep -oE` and
  the header read. **Reviewer evidence:** none staffed. **Remaining blocker:**
  none.

## Tally

Derived on this turn by
`grep -oE '^### F[0-9]{3} \[P[123]\] — [A-Z]+' <this file> | awk '{print $3,$5}' | sort | uniq -c`
over this record, and by `grep -c '^### F'` over both files.

| Disposition | P1 | P2 | P3 | Total |
|---|---|---|---|---|
| CONFIRMED | 8 | 30 | 8 | **46** |
| DISPROVEN | 0 | 0 | 0 | 0 |
| DUPLICATE | 0 | 0 | 0 | 0 |
| BLOCKED | 0 | 0 | 0 | 0 |
| DEFERRED | 0 | 0 | 0 | 0 |

46 rows, `F001`–`F046`, contiguous with no gap — checked by extracting the row ids
in order and comparing each against its ordinal. The report under review carries 46
findings at the same severities (8 P1 / 30 P2 / 8 P3), so every filed finding has
exactly one disposition and no disposition names a finding the report does not
carry.

**A 46-for-46 confirmation rate is itself a finding about this pass, and it is
recorded rather than celebrated.** Three reasons it came out this way, in
decreasing order of how much they should reassure a reader:

1. **Most of the findings are textual claims about two short files.** Classified by
   each row's own **Validation:** clause on this turn, 15 of the 46 were decided by
   reading named lines alone and 31 needed a command — but in nearly every one of
   those 31 the command is a search or a count over the same four artifacts:
   `ultra-review/SKILL.md` (133 lines), `ultra-review-receive/SKILL.md` (55 lines),
   the two `agents/openai.yaml`, and `create_ultra_review_report.py` (203 lines).
   Only F010, F011, F012, F028 and F044 executed anything at all, and all five ran a
   scratch re-implementation rather than the system under review. That class of
   claim is cheap to falsify and the scouts did not miss.
2. **Six rows were narrowed, and the narrowings are real reductions in scope**, not
   decoration: F002's C-02 anecdote is not re-derivable and the digest in the
   header is in fact correct; F019's `:29` does list five missing things, so the
   defect is a missing sub-field and not an absent concept; F031 confirms only that
   no minimum version is declared, since no old interpreter was installed or run;
   F035's disconfirming check as written *fires* and a literal verifier would have
   marked it DISPROVEN on evidence proving the opposite; F042's second half is an
   underspecified threshold, not a machine loop; F046 rests on the coordinator's own
   recorded allocation because the ten packets were prompts and are not in this
   checkout. A pass that could not narrow could not disconfirm either.
3. **The instrument grading its own report card cuts toward confirmation**, and
   this is the reason to distrust the rate. Where a finding says
   `ultra-review-receive` lacks a rule, the check is "read the 55 lines and see
   that the rule is absent" — and absence is easy to confirm and nearly impossible
   to disconfirm from the same text. Three of the eight P1s — F003, F004 and F008 —
   are absence claims of exactly that shape; F001 and F005 are textual chains
   across the two files; only F002, F006 and F007 rest on something other than
   reading, and two of those three are counts over the S1 artifact rather than over
   the pair. The same shape dominates the P2s about the receive skill. The C12 disclosure in this record's header
   names the conflict; this line records what it did to the numbers.

**No independent reviewer was staffed for any finding in this pass.**
`ultra-review-receive/SKILL.md:51` **requires** focused independent review for P0/P1
and security findings. Eight P1 findings were dispositioned without it. That is an
unmet gate, recorded here as unmet, not waived — see the Instrument Log and the
Strongest Reason.

## Instrument Log — `ultra-review-receive` run as written

The skill was run as written and not amended to make a finding verifiable. What the
run exposed, in the skill's own terms:

- **`:12`'s Required Input was satisfiable and was satisfied.** The report path, the
  review name, the round, the scope and the five section headings were all present
  and were read before any disposition — `:1-13`, `:40`, `:59`, `:820`, `:875`. No
  finding-ID restriction was given, so all 46 were in scope. Nothing triggered
  `:14`'s block.
- **`:24`'s "start with the finding's disconfirming check" held for every row but
  one, and the one failed in the direction the skill cannot detect.** F035's queue entry
  says `grep -n 'sha256\|generated' docs/ultrareview/*.md` and "no hits is the
  defect." Run on this turn it produces hits in seven of the nine files —
  14 in the report under review, 5 in S5, 4 in S3a, 4 in S4,
  2 in S3b, 3 in the S1 receive record and a moving number in this one,
  against 0 in the S1 report and 0 in the premise audit — and every hit is
  hand-typed coordinator metadata. Starting with that check and stopping there
  yields DISPROVEN on a finding that is true. The skill has no rule for a
  disconfirming check that is itself wrong, and `:26-30`'s five dispositions have no
  slot for "the finding holds but its own falsifier is invalid" — the row carries it
  in prose because there is nowhere structural to put it. This is a first-party
  instance of the report's own F017 and F019.
- **`:20` and `:51` disagree, and this pass could not obey both.** `:20` permits one
  focused independent reviewer "**only** for a materially disputed or high-risk
  finding"; `:51` **requires** one for every P0/P1. Eight P1 findings here are
  neither disputed nor high-risk in the `:20` sense — they are undisputed textual
  gaps in a 55-line file — so `:20` says do not staff and `:51` says must staff. The
  report's F022 is exactly this contradiction, and this pass resolved it by
  following `:20`, staffing nobody, and recording `:51` as unmet. A pass that
  followed `:51` instead would have staffed eight reviewers to re-read the same 55
  lines. Neither reading is available as a compliant option, which is the finding.
- **`:36`'s remediation boundary was not crossed.** No file under `skills/` was
  edited by this pass; `git diff -- skills/` returns 0 lines on this turn. The
  current request authorizes review — *xem lại* — and not remediation, so `:38-46`'s
  authorized-CONFIRMED path was never entered and every row's **Files changed** line
  reads `none`.
- **`:47` is the only reason this file exists**, and it specifies the name
  (`<report stem>-receive.md`) and the location (beside the report) and nothing
  else. The tally table, the Instrument Log, the Strongest Reason and this Custody
  section are all improvised. `:53` names eight completion-row columns for a fix
  that was applied; it names no shape for a verification-only record. Two receive
  records now exist in this repository and they share a shape only because the same
  seat wrote both — the report's F017 and F020 predicted this, and the prediction is
  now first-party true twice over.
- **`:55` was never reached.** Nothing was claimed fixed, so no behavior-level
  oracle was owed.
- **Four queue instructions told this pass not to run something, and all four were
  obeyed.** Do not run S1's F021 or F023 checks to test F005; do not run the script
  against a file path to reproduce `NotADirectoryError` — pathlib's behaviour was
  reproduced in a scratch temp directory instead, which was removed; do not run two
  concurrent invocations to reproduce the F029 race, so that row confirms the
  absence of `O_EXCL`, `'x'` and any lock by reading, and does **not** claim the race
  was observed; do not invoke the script for F012, so `slugify` and
  `ROUND_RE_TEMPLATE` were re-implemented in a scratch `python3 -c` with no project
  file opened.
- **One thing this record does that the skill does not ask for: it corrects a
  sibling record.** S2's F007 caught that the S1 receive record's F027 row stated
  sixteen while enumerating seventeen. The S1 record was corrected on this turn and
  its sha256 changed as a result. `ultra-review-receive` has no rule for a receive
  record that invalidates an already-reported one, and no field in which to record
  that a prior report's numbers are now stale. The correction was made and is
  reported upward; the absence of a mechanism is the report's F041, confirmed from
  the inside.

## Strongest Reason Not To Merge Yet

**Eight P1 findings are confirmed, and the pair's two highest-consequence defects
are that the report artifact carries no provenance and that the verification step
has no contract for its own output.**

`create_ultra_review_report.py:43-55` accepts `mode`, `review_brief_sha256`,
`scout_count` and `directive_count`, and its template body at `:57-103` interpolates
none of them — verified by `awk`ing the body and grepping for interpolations, which
returns only the literal `Plausible failure mode:`. Every provenance fact a reader
would use to judge a report is therefore hand-typed or absent, which is why this
report's own header carries five improvised metadata lines (its F036) and why the
S1 report carries a different improvisation in a different place. `ultra-review-
receive/SKILL.md:14` admits any markdown file at the right path with the right
headings, so nothing downstream can tell a generated report from a written one.
That is a chain, not a list: no provenance in, no admission test out.

The second half is this record itself. `:47` names a filename and a location for a
receive record and specifies no shape; `:53`'s eight columns describe a fix that was
applied and are silent on verification-only. Two receive records now exist, both
written by this seat, both improvised, and a third written by a different seat would
share nothing with them. A verification step whose output has no contract cannot be
audited by the thing it feeds.

**And the gate this pass did not meet: `:51` requires focused independent review for
every P1, and eight P1 findings were dispositioned by one seat with no reviewer.**
`:20` forbids staffing one for an undisputed finding, so the skill's two rules point
opposite ways and this pass chose `:20`. The dispositions above are one seat's
reading of two short files. They are reproducible — every row names the command or
the line — but they are not independently reviewed, and a merge that relied on them
would be relying on an unmet gate.

Nothing here was fixed. Phase A writes files, not gates. No delivery, merge, push or
deploy is authorized by this pass.

## Custody, re-derived at the end of this pass

Every value below was derived by running the named command on this turn, after the
last edit to this file.

- `git rev-parse HEAD` → `038dc27b50859cb30542b91683688a1f52ce5d66`, unchanged since
  the start of the campaign.
- `git stash list | wc -l` → `0`.
- `git diff -- skills/` → `0` lines. No file under review was touched.
- `git --no-optional-locks status --porcelain --untracked-files=all` → **11 lines**:
  ` M AGENTS.md`, nine untracked files under `docs/ultrareview/` — of which this
  record is one — and `scratchpad/c8-intake.md`. `AGENTS.md` stays untouched, neither
  staged nor reverted, until the Human attributes the edit; `scratchpad/c8-intake.md`
  is never staged.
- `ls docs/ultrareview/ | wc -l` → **9** files: the premise audit, six round-1
  reports — S1, S2, S3a, S3b, S4, S5 — and two `-receive.md` records. One audit plus
  six reports plus two receives is nine.
- The real gate ledger `~/.herdr/projects/beo-skills/gates.md`: `wc -l` → **145**,
  `shasum -a 256` →
  `f3863c8ce9d74b77a1aba0d7a1df965e0ac635e98f4237fbf2cc9a3541360f21` — byte-identical
  to the digest recorded before this pass began. No row was written and no gate was
  opened.
- Nothing was committed, staged, merged, pushed, or gated by this pass.

**One sibling artifact changed on this turn and its recorded digest is now stale
upstream.** `docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1-receive.md`
was corrected — F027's count moved from sixteen to seventeen in the row and again in
its Instrument Log — after S2's F007 caught the error. That file is now **995 lines**
with sha256
`e3a53b3bcd6671db221050edc22191e915d36e66a93e9b42490ab0267d0ec697`. Any earlier
report of that record's length or digest is superseded by these figures.

**This record was checked against its own sources before it was reported**, by two
scratch scripts run on this turn and kept outside the repository.

- **Pointers resolve on disk, not in the index.** 60 `` `path:line` `` instances,
  46 distinct, **0 failures**: every one names a file that exists in the working
  tree and a line that exists and is non-blank. The checker walks the tree rather
  than `git ls-files`, because **3 of the 60 instances** name files git does not
  track — `INTAKE.md` under the gitignored `skills/ultra-review-workspace/` twice,
  and the untracked S1 report once — and an index-based checker reports all 3 as
  missing when all 3 resolve on disk. That is exactly S1's F009, and I committed it during the S1
  pass; it is not repeated here.
- **Seventeen ambiguous pointers were qualified on this turn.** Sixteen bare
  `` `SKILL.md:NN` `` shorthands were rewritten to `ultra-review/SKILL.md:NN`,
  because with two skills under review a bare `SKILL.md` resolves to neither, and
  one bare `agents/openai.yaml` at line 4 was split into the two full paths it
  meant,
  because a third `agents/openai.yaml` exists under `skills/repo-refresh/`.
- **Quotations: 103 quoted strings of twelve characters or more, of which 97 match
  a source** byte-for-byte after normalising `…`, emphasis characters and
  whitespace. The six that do not are correctly not quotations: two are command
  arguments (`` O_EXCL\|'x'\|lock ``, the grep pattern from the F029 row) and
  observed shell output (`python not found`, from F031), and four are this record's
  own phrasings offered as paraphrase and marked as such — `true, unownable`,
  `a scout can self-confirm`, `read the 55 lines and see that the rule is absent`,
  and `the finding holds but its own falsifier is invalid`.
- **Six misquotations were found by this check and none by reading.** Two dropped a
  sentence-initial capital inside the quotation marks (`A dated note has been added
  to S1 recording the third fact.` in F001, `A system notice that subagents or
  background tasks stopped due to a server restart` in F014). One added a terminal
  full stop that `ultra-review-receive/SKILL.md:28` does not carry. One capitalised
  `report prose` from `:32`. One quoted the F014 falsifier in lower case where the
  queue reads `Any named bound falsifies it.` **And one was fabricated**: the F026
  row attributed the phrase *seven marks in all* to the report, which does not
  contain it; the report's actual words are "it marks all seven itself, because no
  rule required the mark", and the row now quotes those. A phrase invented and
  attributed to a source is the most serious defect in this record, and it was
  caught mechanically rather than by re-reading — which is the argument for the
  check, and the reason it is reported here rather than quietly fixed.
