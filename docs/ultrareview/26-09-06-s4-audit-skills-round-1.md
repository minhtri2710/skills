# Ultra Review: s4-audit-skills Round 1

Date: 26-09-06
Review name: s4-audit-skills
Round: 1
Scope: skills/architecture-premise-audit and skills/test-proof-debt-audit at 038dc27: 4 tracked files, 318 lines
Report path: docs/ultrareview/26-09-06-s4-audit-skills-round-1.md
Review brief sha256: e2b91fd1a19ff8ded309932ab00dd0ae4bc2a4b46852f08e2ad9bc64022a01ea
Scouts: 10 (`Explore` kind, model `sonnet`) | Concerns: 10 (G01-G10)
Candidate file: `skills/ultra-review-workspace/campaign-01/S4-CANDIDATES.md` (295 lines, ten verbatim blocks)

## Prior Round Guard

Previous reports read:
- `docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1.md`
- `docs/ultrareview/26-09-06-s2-ultra-review-pair-round-1.md`
- `docs/ultrareview/26-09-06-s3a-beo-doctrine-round-1.md`
- `docs/ultrareview/26-09-06-s3b-beo-scripts-round-1.md`

**No prior round deferred a question to this slice.** Derived on this turn: `grep -n -i 'defer' docs/ultrareview/26-09-06-s{1,2,3a,3b}*.md` returns **six** hits, and none defers anything to this slice. Four are the word used inside the reviewed doctrine or the disposition enum, not a deferral by a round (`s1:673`, `s1:838`, `s2:186`, `s2:920`); `s3b:19` is S3a's five deferrals *to S3b*, all settled there; `s3a:1227` defers one vocabulary question to a `references/command-manifest.md` cross-check, not to S4 and not to either skill in scope. S3a's closing line names S4 only as remaining campaign scope, "for the record and not as authorization". So this round opens with no inherited deferral list, unlike S3b.

**One prior finding is qualified by this round.** `s2` F043 (P3) recommended fixing `ultra-review`'s description "in the shape `architecture-premise-audit` and `repo-refresh` already use" — that is, `architecture-premise-audit/SKILL.md:3`'s explicit negative-scope clause was cited as the exemplar to copy. This round finds that clause supplies no test either direction (F031) and that the same description's positive scope noun is narrower than the skill's own Boundaries line (F030). The S2 recommendation is not withdrawn — an explicit exclusion clause is still better than none, and that is what F043 was about — but the exemplar it names is itself a finding here, so a Phase B fix that copies APA's shape into `ultra-review` would propagate F031. `repo-refresh`'s token-based form (`Use only when the user explicitly invokes $repo-refresh`) is the half of F043's exemplar pair that survives this round intact.

**S2 F043 also states the mirror of F045 from the other side**: it records the soft overlap between `ultra-review` and `test-proof-debt-audit` as scout-09 9.6 saw it from inside `ultra-review`. F045 below reaches the same overlap from inside `test-proof-debt-audit`, independently, and adds `repo-refresh`. Two rounds, two directions, one unstated precedence.

**S3b correction of record.** The S3b report was reported to the Supervisor at sha256 `016f6d29…` and then corrected twice. Its current sha256 is `c8fae92c14814ec6969a33da44bc949a2544e528364a69589031ef8cd509d241`; the earlier shas are superseded and should not be cited. Three corrections, all disclosed inside that report: (1) the scout-custody paragraph printed `2026-09-06T19:20:34Z` for a marker whose UTC mtime is `2026-09-06T12:20:34Z` — a local +07:00 clock with a `Z` appended; the sweep itself was `-newer <marker file>` and mtime-based, so the measured window was always correct and only the printed label was wrong. (2) A sentence claiming a second custody sweep was written before that sweep was run; it was then run, returned exactly the 3 files claimed, and the sentence was rewritten to name the command and the derived count. (3) The Supervisor message reporting S3b said "All five … (Q1, Q2, Q4, Q5, Q6, Q7, Q8)" — seven ids in a parenthetical against a count of five. **The report was correct and the message was wrong**; S3b line 19 says five and enumerates Q1, Q2, Q4, Q5, Q8. A clarifying clause was added to the report naming where Q6 and Q7 are settled, so a reader holding both documents is not left with an unexplained gap. All three are the same class as the class this campaign keeps finding in its targets: a record asserting something the derivation does not support.

## Coordinator Method Note — The Disclosed Conflict, And One Re-Derivation

**No error was found in the S4 brief.** S3b's method note carried three; this one carries none, and the absence is stated rather than padded. What this note carries instead is the conflict of interest the brief disclosed up front and one candidate the coordinator owed a re-derivation on.

1. **The conflict, restated so the reader can discount for it.** `architecture-premise-audit` is scheduled to be *run* later in this same campaign, at the project boundary, on this repository. This slice *reviews* that skill's bundle. Reviewing an instrument and executing it are separate iterations, so C12 holds; but the coordinator writing this report is also the seat that will later invoke the skill, and a finding that complicates that run is a finding this seat has an interest in softening. The brief told all ten scouts so, in those words, and told them not to soften. Three scouts came back with findings that make the coming run harder to call complete (S4-03-07, S4-05-04, S4-10-14), and they are consolidated here as **F003, a P1** — the highest severity in this report — rather than folded into a clarity note. The reader should treat that as the check on the conflict, not as proof the conflict was absent.

2. **The one candidate owing coordinator re-derivation, and its result.** S4-05-09 compares the two in-scope descriptions against sibling descriptions elsewhere in the repository — outside the frozen scope, so the scout's own comparison was tagged in the candidate file as owed a coordinator check before it could be carried. Re-derived on this turn by printing line 3 of every `skills/*/SKILL.md`: the nine `beo-*` descriptions anchor on concrete domain nouns (BEO, `PASS_EXECUTE`, `TICKET.json`, `PLAN.md`, Beads, `br`/`bv`, `references/command-manifest.md`); `repo-refresh/SKILL.md:3` and `herdr-delivery-workflow/SKILL.md:3` anchor on explicit invocation tokens (`$repo-refresh`; "explicitly mentions Herdr"); `ultra-review/SKILL.md:3`, `prompt-leverage/SKILL.md:3` and `frontend-design/SKILL.md:3` give concrete positive phrasings. The two in-scope descriptions give neither a token nor a worked example. **The scout's characterization is confirmed**; it is carried as F046 at P3, the severity a pattern observation over a small sample earns.

3. **Two out-of-scope pointer sets are carried with an explicit tag rather than silently.** The brief promised every `file:line` in this report is mechanically verified. F045 cites `ultra-review/SKILL.md:3` and three `repo-refresh/SKILL.md` lines (`:3`, `:14`, `:78-85`); F046 cites `repo-refresh/SKILL.md:3`, `herdr-delivery-workflow/SKILL.md:3`, `ultra-review/SKILL.md:3`, `prompt-leverage/SKILL.md:3` and `frontend-design/SKILL.md:3`. Seven distinct pointer sites across five files, derived on this turn. These files are outside the frozen scope, and they are included in the pointer-verification run anyway — the count in Coverage And Derivation covers them.

## Candidates Rejected On Source

Only one candidate is contradicted by the files. Everything else survives; that is itself a result, and the reason is stated in Coverage And Derivation.

- **S4-10-15, on one word — PARTIALLY REJECTED.** The candidate says `structural-antipatterns.md:3` is a "verbatim dup" of `architecture-premise-audit/SKILL.md:29-30`. It is not verbatim. `:3` reads "Use this catalog as search lenses, not a checklist that every design must satisfy."; `:29-30` reads "Use its patterns as search / lenses, not as a checklist that every design must satisfy." Two differences ("this catalog" vs "its patterns"; "not a checklist" vs "not as a checklist"). The claim that survives is the one the finding rests on — the two sentences carry the same instruction and the reference's copy adds no information the agent lacks, because `:29-30` is in the unconditionally-read file and is what sends the agent to the reference in the first place. S4-08-01 says "near-verbatim" and is the accurate wording. Carried at that strength in F042.

## Findings

Severity scale, adapted from the scale used in S1, S2, S3a and S3b, with one clause added because those slices audited code and this one audits prose instructions. **P1**: a mandatory gate is unsatisfiable, or a mandatory gate is satisfiable without doing its work, or a record already written is false, or a machine-readable contract declares a constraint it structurally cannot impose — **plus, added for this slice: a mandatory output cannot carry the result the procedure produces.** **P2**: a rule cannot be executed as written, or the instrument cannot measure what it claims. **P3**: clarity, robustness, dead surface.

Applying a code-shaped scale to prose is the judgment call in this report. Where a P1 is claimed, the finding names which clause it satisfies and why the satisfying/unsatisfiable language is literal rather than metaphorical.

### F001 [P1] The coverage ledger step 6 stops on is never constructed by any step, so the only termination gate in the procedure is satisfiable without doing its work

Severity: P1 | Confidence: high
Candidates: S4-02-01, S4-03-03
Source pointer: `skills/architecture-premise-audit/SKILL.md:67`, `:86`, `:50`, `:53`
Evidence (derived on the turn this report was written):
- `SKILL.md:65-67`, step 6: "Stop only when every discovered ingress, authoritative / state family, durable effect, expensive operation, and external output is / represented in the coverage ledger or explicitly excluded by scope."
- `grep -n 'ledger' skills/architecture-premise-audit/SKILL.md` returns exactly two lines: `:67` and `:86`. There is no third occurrence in the bundle.
- `:86` is output item 2, "compact coverage ledger and exclusions" — a deliverable produced *after* the Procedure ends at `:71`, not an artifact any step populates.
- Steps 2 and 3 name their artifacts: `:50` "the expected atlas", `:53` "the observed map". Neither is called a ledger, and no step says to record anything into one.
Contract violated:
- The single stopping condition for a six-step procedure gates on an object no step creates. Step 6 asks whether every discovered item is "represented in the coverage ledger"; if no ledger exists, nothing is represented in it and nothing is excluded by scope, so the condition is either never satisfiable or vacuously satisfied depending on how the agent reads an empty set. Both readings are available and the text picks neither.
Plausible failure mode:
- The likelier of the two: the agent invents a ledger at write time to fill output item 2, and step 6 is answered against that improvised object rather than against anything the trace produced — so the gate is passed by an artifact created to pass it. The gate's work (checking that the trace covered what it discovered) is never done, and no reader can tell, because the ledger it checked against was authored in the same breath as the check.
Durable solution hypothesis:
- Instruct ledger construction at step 3: each traced item is recorded as a row when it is discovered. Step 6 then verifies an artifact that already exists and was populated by a different step than the one checking it, and output item 2 is that ledger rather than a fresh deliverable. This is the smallest change that makes the gate check something.
Disconfirming check:
- `grep -n 'ledger' skills/architecture-premise-audit/SKILL.md` — a third occurrence inside `:46-71` that constructs or populates the ledger falsifies this finding. Two hits, both cited above, is the confirming result.

### F002 [P1] Step 6's five coverage categories are a renamed subset of step 3's nine, so four categories the procedure requires tracing can never block termination

Severity: P1 | Confidence: high
Candidates: S4-03-02 (high), S4-02-05 (medium, with the disconfirming reading stated)
Source pointer: `skills/architecture-premise-audit/SKILL.md:53`, `:54`, `:65`, `:66`
Evidence (both lists counted on this turn against the printed source):
- Step 3, `:53-55`, traces **nine**: production entry points, authoritative state, durable effects, expensive operations, queues, schedulers, external outputs, deployment boundaries, cited proof.
- Step 6, `:65-67`, gates on **five**: ingress, authoritative state family, durable effect, expensive operation, external output.
- Set difference: **queues, schedulers, deployment boundaries, and cited proof appear in the trace list and in no gate.** Nothing anywhere in `:46-95` stipulates that "durable effect" or "expensive operation" subsumes them.
- Two of the five that do carry over are renamed without a definition: "production entry points" (`:53`) becomes "ingress" (`:65`); "authoritative state" (`:53-54`) becomes "authoritative state family" (`:66`).
Contract violated:
- The termination gate is a strict subset of the mandatory work. An audit can trace all nine, leave four of them entirely unaddressed, and satisfy step 6 literally. That is the "satisfiable without doing its work" clause in the plain case: the work is enumerated by the same document that then declines to check four ninths of it.
Plausible failure mode:
- Unbounded queues are the reference's own first "Buffering and failure" tax (`structural-antipatterns.md:76`). An audit traces a queue at step 3, never brings it to a comparison, reaches step 6, finds every ingress and state family accounted for, and stops — emitting a coverage ledger that is complete by the stated rule while the single tax the loaded reference leads with was discovered and dropped.
Durable solution hypothesis:
- Make the two lists identical, or state in one sentence why the gate is deliberately narrower and what happens to the other four. Renaming is the cheaper half: use "production entry points" in both places, or "ingress" in both.
Disconfirming check:
- `sed -n '53,55p;65,67p' skills/architecture-premise-audit/SKILL.md` and count. A stipulation elsewhere that the missing four are subsumed would falsify this; `grep -n -i 'queue\|scheduler\|deployment' skills/architecture-premise-audit/SKILL.md` returns only `:54`, `:55`, showing they appear once each, in step 3, and nowhere else in the file.
Dissent, recorded: S4-02-05 rates this medium and states the disconfirming reading explicitly — step 6's five may be the intended *coverage targets* while step 3's extra four are *supporting mechanisms* found en route, which would make this a clarity issue rather than a logic bug. S4-03-02 rates it high on the ground that no such distinction is stated. This report takes the high reading, because a rule that requires guessing which of two lists is authoritative is not executable as written whichever guess is correct; the dissent is recorded so a receive pass can weigh it.

### F003 [P1] Applied to a prose target, step 6's completion rule may resolve to nothing, so the audit can terminate immediately and report as coverage-checked — and this campaign is scheduled to run exactly that case

Severity: P1 | Confidence: medium-high
Candidates: S4-03-07, S4-05-04, S4-10-14
Source pointer: `skills/architecture-premise-audit/SKILL.md:65`, `:66`, `:3`, `:14`, `:26`, `:53`
Evidence:
- Step 6's five categories (`:65-66`) — ingress, authoritative state family, durable effect, expensive operation, external output — are properties of a running system. So are step 3's nine (`:53-55`), and so is the reference throughout (`structural-antipatterns.md:66-78`, the entire Avoidable taxes section, presumes traffic, queues and hot paths).
- Nothing in the description (`:3`) or Boundaries (`:14`) excludes a target that has none of them. `:3`'s only positive scope noun is "a whole project".
- **The literal-match answer to the disclosed conflict is yes.** S4-05-04 checked it directly: `:3` reads "Audit a whole project … Use only for an explicitly requested broad premise audit"; the campaign's scheduled job is a broad premise audit of this repository at the project boundary. The description selects the skill for that job word for word.
- Two gates the description leans on are undecided for that job. (a) *Requester*: `:3` says "explicitly requested" and names no requester; `:14` and `:23-24` assume a user who requests and can be asked follow-ups. The campaign's invocation is orchestrator-initiated inside a scheduled pipeline. Whether that satisfies "explicitly requested" is not decidable from the text. (b) *Domain*: the target is a set of Markdown prose bundles.
- `:26-27`'s load condition ("For realtime multiplayer, MMO, or another system with a suspected structural / misfit") does not fire on its face for a prose-bundle target either, which is S4-10-14's separate observation that the entire 151-line reference is dead surface for that run.
Contract violated:
- The only termination gate in the procedure is written in vocabulary that may have no referent in a target the description admits. When the referents are empty, "every discovered ingress … is represented in the coverage ledger" is true of the empty set, step 6 fires at once, and the report leads with a verdict under a heading that says coverage was checked. That is the "satisfiable without doing its work" clause in its sharpest form: not a gate that can be passed cheaply, a gate that passes before any work begins.
Plausible failure mode:
- The scheduled run emits `KEEP_FOUNDATION` or `INSUFFICIENT_EVIDENCE` with a coverage ledger of zero non-vacuous rows, and a later reader — including this campaign's own Phase A ranking — reads it as a coverage-checked audit of the repository. The alternative failure is the agent reinterpreting "ingress" as "an agent reads this skill" and "durable effect" as "a report file is written", which may be reasonable but is licensed by nothing in the text, so two runs may reinterpret differently and neither is wrong.
Durable solution hypothesis:
- State what the five categories map to when the audited system is not a runtime — or scope the description to exclude non-runtime targets, which is the honest option if the procedure was written for running products. Either fix also settles the requester gate by naming who counts as the requester when the caller is an orchestrator.
Disconfirming check — **falsifiable, scheduled, and owed by this campaign**:
- When `architecture-premise-audit` is run later at the project boundary, does its coverage ledger contain non-vacuous rows, and how did it resolve "explicitly requested" for an orchestrator-initiated invocation? Non-vacuous rows weaken this finding materially. A zero-row or improvised ledger confirms it. **The run must execute the skill as written, unfixed** — the same C12 rule S3b applied to `beo_audit.py`: an instrument validated only against already-fixed text has not been shown to measure anything, and a fixed step 6 would prove nothing about whether the shipped step 6 constrains an audit of this repository.

### F004 [P1] The mandatory report field list omits the disposition, so a fully compliant `test-proof-debt-audit` report never states which of the six the audit chose

Severity: P1 | Confidence: high
Candidates: S4-01-06 (high), S4-09-07
Source pointer: `skills/test-proof-debt-audit/SKILL.md:17`, `:28`, `:29`
Evidence:
- `:17`, step 6, is the terminal action of the whole procedure: "Choose `keep`, `replace`, `demote`, `closeout-only`, `delete`, or `escalate`."
- `:28-29` is the report contract, and it is a flat unconditional list: "Report location, claimed behavior, actual observation, disconfirming scenario, and / smallest replacement." The chosen disposition is not among the five fields.
- Nothing between `:28` and `:33` marks any field optional or adds the disposition by another name.
Contract violated:
- The audit's own result is the one thing its output format does not require. This is the added P1 clause: a mandatory output that cannot carry the result the procedure produces. The six-way vocabulary is the point of the skill and is invisible to the consumer of a report that satisfies every stated requirement.
Plausible failure mode:
- Two directions, both live. A conforming report is unusable for aggregation — no consumer can group audits by disposition, because the field is not there. And the fields that *are* mandatory do not fit two of the six: a `keep` has no disconfirming scenario (the proof is already sensitive to the claim, which is why it is kept) and no smallest replacement (nothing needs replacing); an `escalate` may have no determinable replacement, since undeterminability is why one escalates. So an agent finding clean proof either fabricates hollow fields or silently omits mandated ones, and neither is licensed by the text.
Durable solution hypothesis:
- Add "and chosen disposition" to `:28`, and make "disconfirming scenario" and "smallest replacement" conditional on a debt-bearing disposition. The two halves are one edit: once the disposition is a stated field, the conditionality has something to branch on.
Disconfirming check:
- `sed -n '17p;28,29p' skills/test-proof-debt-audit/SKILL.md`. Reading "smallest replacement" as implicitly encoding the disposition is an unstated inference — `:28-31` states no such link, and `keep` has no replacement to encode it with.

### F005 [P2] The reference opens by telling the agent to widen an audit the body's first instruction forbids widening, and closes with a bare mutation imperative to an agent with write access

Severity: P2 | Confidence: high
Candidates: S4-06-01, S4-06-02, S4-10-30
Source pointer: `skills/test-proof-debt-audit/references/catalog.md:3`, `:39`, `:7`, `:9`; `skills/test-proof-debt-audit/SKILL.md:8`, `:30`, `:31`
Evidence:
- `SKILL.md:8-10`: "Audit only the claim and proof route named by the user. Do not turn ordinary / implementation, a failing test, weak coverage, or the presence of mocks into a / repository-wide proof audit."
- `catalog.md:3`, the first sentence an agent reads on loading the reference: "Use this reference to widen an audit after the live claim and scan roots are known from the repository."
- `catalog.md:7` "Search for:" followed by seven generic-smell families at `:9-15`. Executing them is a repository-wide search; the mechanics are indistinguishable from the sweep `SKILL.md:8-10` prohibits.
- `catalog.md:39`: "Do not grow a proxy with more strings or patterns. Delete, demote, or replace it." The second sentence is an imperative applied to the artifact, never framed as report language.
- `SKILL.md:30-31`: "modify proof or production code / only when requested." That gate lives in a different file, read at a different time, and is not restated in the reference.
- `grep -n 'scan roots' skills/test-proof-debt-audit/` returns exactly one line, `catalog.md:3`. The term is defined nowhere.
Contract violated:
- A reference contradicting the skill that loads it, in its opening line; and an instruction to mutate issued from inside the file loaded precisely during the broad case, to an agent whose write access is ambient rather than granted by this skill.
Plausible failure mode:
- The agent cannot tell from its own actions which mode it is in, because widening and creeping have identical mechanics. And an agent reading `:39` in isolation deletes a proxy test the user asked only to have assessed; `SKILL.md:30-31` is the only thing that stops it, and nothing in the reference recalls it.
Durable solution hypothesis:
- Scope "widen" to the named claim's evidence chain rather than the repository, define or replace "scan roots", rephrase Better Routes and `:39` as report recommendations ("recommend deleting, demoting, or replacing it"), and restate the modify-only-when-requested gate locally in the reference.
Disconfirming check:
- `sed -n '3p;39p' skills/test-proof-debt-audit/references/catalog.md` against `sed -n '8,10p;30,31p' skills/test-proof-debt-audit/SKILL.md`. The reading that dissolves the contradiction — that `SKILL.md:33`'s "broad user-requested audit" branch licenses exactly this widening as a user-authorized exception — is live but unconfirmed: no cross-reference states it, in either direction. `:39`'s imperative survives that reading intact.

### F006 [P2] `escalate` is a mandatory disposition with no trigger, no addressee, and no defined mechanism, in a bundle whose sibling skill explicitly bans the actions it might name

Severity: P2 | Confidence: high
Candidates: S4-09-01 (high), S4-06-03 (medium-high), S4-10-23, S4-01-10 (low, dissent)
Source pointer: `skills/test-proof-debt-audit/SKILL.md:17`, `:29`, `:30`; `skills/architecture-premise-audit/SKILL.md:21`
Evidence:
- `grep -n -i 'escalat' skills/test-proof-debt-audit/SKILL.md skills/test-proof-debt-audit/references/catalog.md skills/architecture-premise-audit/SKILL.md skills/architecture-premise-audit/references/structural-antipatterns.md` returns **exactly one line** across all four files: `test-proof-debt-audit/SKILL.md:17`.
- Every other disposition gets follow-up guidance: `replace`, `demote`, `delete` at `:19-24` and `catalog.md:32-37`; `keep` and `closeout-only` at least appear in adjacent prose. `escalate` appears once, in the list, and never again.
- `SKILL.md:30` two lines later says "report and stop".
- `architecture-premise-audit/SKILL.md:21-22` explicitly forbids "implementation, issue creation, or a second / review workflow" — a constraint this file conspicuously lacks.
Contract violated:
- A token the procedure requires the agent to be able to choose, with no rule for when to choose it and no definition of what choosing it does. It cannot be executed as written.
Plausible failure mode:
- Two agents split. One prints the word and stops, honoring `:30`. The other escalates with the tools it has — opens an issue, pings an owner, invokes another skill — which the sibling skill bans by name and this one does not. The second behavior is not excluded by any sentence in the file.
Durable solution hypothesis:
- Define `escalate` as a report-only label with a stated trigger (the claim cannot be settled from the cited proof and the missing evidence is named) and an explicit disclaimer of autonomous follow-through, matching `architecture-premise-audit/SKILL.md:21-22`'s wording so the two skills read alike.
Disconfirming check:
- The grep above. Any line in either bundle defining escalate's trigger or recipient falsifies this; there is one occurrence and it is the list itself.
Dissent, recorded: S4-01-10 rates the same observation **low**, reasoning that `escalate` is plausibly self-explanatory in plain English and, unlike the other five, changes no artifact, so it may need no guardrail. This report takes the high reading precisely because "changes no artifact" is the assumption in question — nothing in the file says so, and S4-10-23 shows the guard at `:29` may exist because `escalate` is permissive enough to need one.

### F007 [P2] Four unreconciled spellings for "this is not actually a defect", across three vocabularies, none cross-referencing another

Severity: P2 | Confidence: high
Candidates: S4-01-01, S4-01-02, S4-02-08, S4-08-05, S4-10-13, S4-10-18
Source pointer: `skills/architecture-premise-audit/SKILL.md:70`, `:91`; `skills/architecture-premise-audit/references/structural-antipatterns.md:148`
Evidence (three sites, read on this turn):
- `SKILL.md:70`: "justified divergence", one of six unbackticked prose classifications at `:69-71`.
- `SKILL.md:91`, output item 6: "`STOP_OPTIMIZING` and `PROBABLY_JUSTIFIED` items". Both tokens occur only here; no Procedure step assigns either, and the `:69-71` classification list neither contains them nor maps onto them.
- `structural-antipatterns.md:148`: "Return `BORING_STANDARD` or `JUSTIFIED_DEVIATION` when the production mechanism has …" — two more tokens, for the same underlying idea, reachable only if the conditional reference loaded.
- No glossary, table, or equivalence sentence exists in either file. Both were read whole.
Contract violated:
- A closed output vocabulary that is neither closed nor single. Output item 6 is mandatory and its two tokens have no producing step, so the agent must invent the mapping from classification to token at write time.
Plausible failure mode:
- A candidate classified "justified divergence" at `:70` has no instruction on whether it also belongs in the `PROBABLY_JUSTIFIED` section, or is exonerated as `JUSTIFIED_DEVIATION`, or all three — double-counted or inconsistently labelled across runs. Nothing validates report shape, so the divergence is never detected. Compounding: the Exoneration section is unreachable for every audit that does not load the reference, so for the majority case the description advertises, two of the four spellings simply do not exist and the agent has no exoneration path in `SKILL.md`'s own classification list at all.
Durable solution hypothesis:
- One canonical token set used in all three places. If `BORING_STANDARD` and `JUSTIFIED_DEVIATION` are meant as distinct sub-cases rather than synonyms, say so and map both into `:69-71`, so the exoneration path exists whether or not the reference loaded.
Disconfirming check:
- `grep -n 'JUSTIFIED\|OPTIMIZING\|BORING\|justified divergence' skills/architecture-premise-audit/SKILL.md skills/architecture-premise-audit/references/structural-antipatterns.md` returns the three sites above and no reconciling line.

### F008 [P2] Step 4 compares "every slice" and step 5 deep-checks "serious candidates"; no step produces slices, and no rule promotes a comparison to a candidate

Severity: P2 | Confidence: high
Candidates: S4-02-02, S4-02-03
Source pointer: `skills/architecture-premise-audit/SKILL.md:57`, `:61`, `:34`, `:44`, `:50`, `:53`
Evidence:
- `grep -n 'slice' skills/architecture-premise-audit/SKILL.md` returns `:35`, `:44`, `:57` — the Audit Slice section's opening sentence, its closing sentence, and step 4. (Case-insensitively it returns four, the fourth being the `## Audit Slice` heading at `:32`; the case-sensitive form is the one quoted throughout this report.) `grep -n -i 'slice' skills/architecture-premise-audit/references/structural-antipatterns.md` returns nothing.
- `:34-44` defines a six-element slice schema but no numbered step constructs slices. Step 2 (`:50`) produces "the expected atlas"; step 3 (`:53`) "the observed map"; neither vocabulary maps onto the schema, and nothing in steps 2-3 gathers `:42`'s "reusable-platform versus application responsibility".
- `grep -n -i 'candidate' skills/architecture-premise-audit/SKILL.md` returns `:61` and `:69`. Step 4 (`:57-60`) never uses the word; it poses four comparison questions. "Candidates" first appears at `:61` as an *input* to step 5.
Contract violated:
- Two consecutive steps consume artifacts their predecessors do not produce. The boundary of "every slice" and the membership of "serious candidates" are both undefined at the moment they are required.
Plausible failure mode:
- The scope of the expensive step — real-caller tracing, counterfactual, falsifier — is wholly discretionary. Two runs deep-check disjoint sets and both are compliant. Step 6's coverage inherits the same indeterminacy, since it can only cover what step 4 compared.
Durable solution hypothesis:
- An explicit step between 3 and 4 that organizes atlas and map into slices per the `:37-42` schema, and a sentence in step 4 naming its output artifact plus the promotion rule step 5 consumes.
Disconfirming check:
- The two greps above. A construction instruction anywhere in `:46-71` falsifies this.

### F009 [P2] The reference gates all reporting on a "bounded checkpoint" that occurs once in the bundle and is defined nowhere

Severity: P2 | Confidence: high
Candidates: S4-08-02, S4-10-16
Source pointer: `skills/architecture-premise-audit/references/structural-antipatterns.md:4`; `skills/architecture-premise-audit/SKILL.md:26`, `:67`, `:86`
Evidence:
- `:4`: "Report only patterns supported by the bounded checkpoint." A definite article, pointing at nothing.
- `grep -n 'checkpoint' skills/architecture-premise-audit/SKILL.md skills/architecture-premise-audit/references/structural-antipatterns.md skills/test-proof-debt-audit/SKILL.md skills/test-proof-debt-audit/references/catalog.md` returns **exactly one line**: the one above.
- `SKILL.md`'s nearest analogues are the coverage ledger (`:67`, `:86`), the audit slice (`:32-44`), and "bounded" as an adjective on work at `:23` and `:52`. None is called a checkpoint.
- Per `SKILL.md:26-29` this reference is read *before* step 2, so at the moment `:4` applies, no artifact of any kind yet exists in the procedure.
Contract violated:
- A reporting filter whose satisfaction condition has no referent. The agent cannot decide what passes it.
Plausible failure mode:
- The agent invents a meaning, silently ignores an unresolvable constraint, or defers the whole file to an unspecified later point. All three change what gets reported, and none is detectable in the output.
Durable solution hypothesis:
- Name an already-defined referent — the coverage ledger of step 6, or the observed map of step 3 — and move the sentence to where that artifact exists.
Disconfirming check:
- The four-file grep above.

### F010 [P2] The reference's load condition is either circular or vacuous, and the text does not say which

Severity: P2 | Confidence: medium-high
Candidates: S4-04-01 (high), S4-04-02, S4-04-04, S4-02-07
Source pointer: `skills/architecture-premise-audit/SKILL.md:26`, `:27`, `:3`, `:48`, `:53`, `:57`; `skills/architecture-premise-audit/references/structural-antipatterns.md:8`
Evidence:
- `:26-28`: "For realtime multiplayer, MMO, or another system with a suspected structural / misfit, read / [references/structural-antipatterns.md](references/structural-antipatterns.md)".
- **Circular reading:** the reference *is* the catalog that defines what a structural misfit looks like (`structural-antipatterns.md:8-27`, the Causal mechanism section). An agent auditing a non-multiplayer system cannot know whether to suspect one until it has read the file the suspicion unlocks.
- **Vacuous reading:** `:3` says the skill exists to audit "a possibly wrong system archetype", so every legitimate invocation already satisfies "a suspected structural misfit", and the third disjunct is dead text — deleting it for an unconditional read would change no compliant agent's behavior.
- **Ordering problem, on either reading:** the judgment the third disjunct requires follows step 3 (`:53`, observed map) and step 4 (`:57`, compare), both of which run after the point at which the reference must already have been read.
Contract violated:
- A load condition that cannot be evaluated at the time it applies. Which of the two readings governs is itself undecidable from the prose, and that ambiguity — not either reading alone — is the finding.
Plausible failure mode:
- For a non-game project the agent either skips the reference (losing the whole misfit taxonomy for exactly the audit type the description advertises) or loads it unconditionally (making the condition dead). Both are defensible; the outputs differ substantially, since the reference is 151 of the bundle's 318 lines.
Durable solution hypothesis:
- Replace the third disjunct with a pre-reference-observable signal, or instruct an unconditional read at step 2 and delete the condition. The file is framed as search lenses rather than a checklist, so an unconditional read costs little.
Disconfirming check:
- `grep -n -i 'suspect\|misfit' skills/architecture-premise-audit/SKILL.md skills/architecture-premise-audit/references/structural-antipatterns.md` — a definition of "suspected structural misfit" grounded in something the agent knows before reading the reference falsifies this. The greps return the load condition and the reference's own title.

### F011 [P2] One artifact carries three names, so the step the reference-read must precede cannot be identified

Severity: P2 | Confidence: medium-high
Candidates: S4-04-03, S4-02-07
Source pointer: `skills/architecture-premise-audit/SKILL.md:29`, `:50`, `:85`
Evidence:
- `:29`, the load condition's temporal anchor: "before constructing the expected capability map".
- `:50`, Procedure step 2: "**Build the expected atlas.**"
- `:85`, output item 1: "expected-versus-observed map".
- Each phrase occurs once. No sentence equates any two.
Contract violated:
- The *when* of a mandatory read is undecidable, not merely the *whether*. `:29`'s anchor names no step number and matches no step title.
Plausible failure mode:
- An agent reading literally cannot locate "the expected capability map" in the Procedure at all, and either reads the reference at an arbitrary point or treats the condition as unanchored and skips it.
Durable solution hypothesis:
- One term throughout, plus an explicit step number in `:29` ("before step 2").
Disconfirming check:
- `grep -n -i 'expected atlas\|expected capability map\|expected-versus-observed' skills/architecture-premise-audit/SKILL.md` returns exactly the three sites, one each.

### F012 [P2] Step 1 requires the agent to author a completion rule that nothing downstream reads, while step 6 imposes a different fixed one

Severity: P2 | Confidence: medium-high
Candidates: S4-02-06 (medium-high), S4-10-06, S4-03-04 (low-moderate, dissent)
Source pointer: `skills/architecture-premise-audit/SKILL.md:49`, `:65`, `:66`, `:67`
Evidence:
- `:48-49`, step 1: "State the product category, requested boundary, expected / outcome, material assumptions, and completion rule."
- `grep -n 'completion rule' skills/architecture-premise-audit/SKILL.md` returns exactly one line, `:49`. The artifact is never read back.
- `:65-67`, step 6, states an independent stopping condition without referring to step 1.
Contract violated:
- Two candidate terminating conditions, no stated relationship, no tie-break. Either the step-1 artifact is discarded (dead text) or the agent authors one that can conflict with step 6 and nothing reconciles them.
Plausible failure mode:
- An agent satisfies a weak self-declared rule and treats it as license to skip step 6's exhaustive language; or treats step 6 as silently overriding step 1, making step 1's clause ceremony. The text supports either, so two agents exit at meaningfully different points and both are compliant.
Durable solution hypothesis:
- Delete the clause from step 1, or make step 6 read "verify the completion rule stated at step 1 against the coverage ledger", which turns the step-1 artifact into the thing step 6 checks.
Disconfirming check:
- `grep -n 'completion rule' skills/architecture-premise-audit/SKILL.md` — a second occurrence inside `:57-71` falsifies this.
Dissent, recorded: S4-03-04 rates this **low-moderate**, holding that a "declare, then verify" reading is at least as plausible as a contradiction. That reading is exactly the durable fix above; it is not, however, what the text says, since step 6 never mentions step 1.

### F013 [P2] The procedure has no fixpoint: step 5 routinely discovers items step 3 missed, and nothing returns to step 3

Severity: P2 | Confidence: high
Candidates: S4-03-01
Source pointer: `skills/architecture-premise-audit/SKILL.md:61`, `:65`, `:53`
Evidence:
- `:61`, step 5: "Trace real callers and consumers, name the / exact amplification route …" Tracing real callers routinely surfaces ingresses, effects and outputs step 3 did not reach.
- `:65-67`, step 6, stops when "every discovered" item is in the ledger. "Discovered" is not scoped to a step.
- The Procedure at `:46-67` is written strictly linear, 1 through 6. No loop-back instruction exists anywhere in `:46-95`.
Contract violated:
- A coverage gate over a set that later steps can grow, with no rule for re-entering earlier steps and no base case for stopping the growth.
Plausible failure mode:
- The agent reaches step 6, finds its ledger internally consistent with everything discovered *so far*, and emits a verdict — while step 5's own trace just added ingresses that were never fed through map-building or comparison. Discoveries made during step 6 itself are unaddressed by any rule.
Durable solution hypothesis:
- State the fixpoint explicitly: if step 4 or 5 discovers an item absent from the observed map, return to step 3 and re-run 4-6; terminate on a pass that adds nothing. That gives the procedure the base case it currently lacks.
Disconfirming check:
- `grep -n -i 'return to\|repeat\|again\|iterate' skills/architecture-premise-audit/SKILL.md` — any loop-back instruction falsifies this.

### F014 [P2] The only alternative to ledger coverage is an exclusion the auditing agent grants itself, with no justification required and no reviewer

Severity: P2 | Confidence: medium
Candidates: S4-03-05
Source pointer: `skills/architecture-premise-audit/SKILL.md:67`, `:14`, `:86`
Evidence:
- `:67`: "represented in the coverage ledger or explicitly excluded by scope."
- `:14`, Boundaries: "Work at the whole-project or named broad-system boundary requested by the user." Scope is set by the same agent that later invokes the exclusion, and nothing forbids narrowing it mid-audit.
- `:86`, output item 2, asks for "compact coverage ledger and exclusions" but states no required content for an exclusion — no justification, no count, no rationale field.
Contract violated:
- The escape hatch on the termination gate is unaudited. Nothing distinguishes a principled exclusion from one made to finish.
Plausible failure mode:
- Acute under the campaign's own scheduled run: an agent low on context marks the remaining bundles "excluded by scope", satisfies step 6, and produces a verdict that reads as complete coverage while being arbitrarily incomplete. The report format gives a reader no way to see how much was excluded.
Durable solution hypothesis:
- Require each exclusion to carry a one-line justification tied to the step-1 boundary, and require the verdict section to state exclusion count and rationale rather than leaving `:86` as an optional-looking bullet.
Disconfirming check:
- `sed -n '67p;86p' skills/architecture-premise-audit/SKILL.md` — a stated requirement on exclusion content falsifies this.

### F015 [P2] Six per-candidate classifications and five report verdicts, with no composition rule, and one term serving as both

Severity: P2 | Confidence: medium-high
Candidates: S4-01-04, S4-01-03, S4-03-09
Source pointer: `skills/architecture-premise-audit/SKILL.md:69`, `:71`, `:75`, `:81`
Evidence:
- `:69-71`: six mandatory classifications — architecture defect, owner defect, implementation drift, justified divergence, quarantined scaffold, insufficient evidence.
- `:75-81`: "Lead with one verdict" and five backticked tokens.
- No sentence in the Procedure (`:46-71`) or Verdict And Output (`:73-95`) states how classifications compose into the single leading verdict.
- `:71` "insufficient evidence" (per-candidate) and `:81` `INSUFFICIENT_EVIDENCE` (whole-report) are the same words in two semantic roles, in the same file, with no stated relationship.
Contract violated:
- A mandatory single verdict derived from a mandatory classification set by no stated rule.
Plausible failure mode:
- Two agents produce identical classifications and different leading verdicts; the verdict is non-reproducible, which matters because it is the first thing a reader acts on. On the shared term: an agent conflates one uncertain candidate with a blanket `INSUFFICIENT_EVIDENCE`, collapsing a mixed-evidence audit, or treats them as unrelated and never propagates candidate uncertainty upward at all.
Durable solution hypothesis:
- State the mapping — for instance, any supported "architecture defect" forces at least `REPAIR_FIRST` — and rename one of the two "insufficient evidence" uses.
Disconfirming check:
- `sed -n '69,71p;75,81p' skills/architecture-premise-audit/SKILL.md` and read `:57-67` for an aggregation rule. There is none.

### F016 [P2] Output item 3 requires a "hidden premise" and a "tax" per finding; no step produces either, and the only taxonomy for "tax" sits behind the conditional reference gate

Severity: P2 | Confidence: high
Candidates: S4-02-04, S4-01-09 (low, on the same field)
Source pointer: `skills/architecture-premise-audit/SKILL.md:87`, `:57`, `:58`, `:26`; `skills/architecture-premise-audit/references/structural-antipatterns.md:64`
Evidence:
- `:87-88`, output item 3: "ranked findings with production evidence, hidden premise, tax, and / amplification route".
- `grep -n -i 'premise' skills/architecture-premise-audit/SKILL.md` returns `:2` (the skill name), `:3` (description), `:6` (H1) and `:87`. The first three are the skill's own title; `:87` is the only body use, and nothing defines it.
- "Tax": step 4 at `:58` asks "whether cost follows useful work" but never instructs naming a tax as a labelled artifact. The only taxonomy is `structural-antipatterns.md:64`, the `## Avoidable taxes` section, loaded only under the `:26-30` condition.
Contract violated:
- Two mandatory per-finding fields with no producing step and, for one of them, no definition in context for any audit that does not load the conditional reference — that is, the whole-project non-realtime audit the description most directly advertises.
Plausible failure mode:
- The agent emits a "tax" per finding with no taxonomy ever in context, inventing categories per run; and fills "hidden premise" with free prose in one run and with the reference's lens names ("Wrong archetype") in another, depending on whether the reference loaded.
Durable solution hypothesis:
- Inline domain-neutral definitions of both in `SKILL.md`, or have step 4/5 produce each as a named artifact, or make the reference load unconditional. Any one of the three closes it; the first is smallest.
Disconfirming check:
- The premise grep above, plus `grep -n -i 'tax' skills/architecture-premise-audit/SKILL.md`, which returns only `:87`.
Dissent, recorded: S4-01-09 rates the "hidden premise" half **low**, arguing that the "search lenses, not a checklist" framing at `structural-antipatterns.md:3` and `SKILL.md:29-30` is itself evidence the lens names are deliberately not closed-vocabulary output labels. That is a good reason not to require lens names; it is not a reason for the field to be undefined.

### F017 [P2] The classification instruction is procedurally required, carries no step number, and depends on two undefined terms

Severity: P2 | Confidence: medium
Candidates: S4-02-09
Source pointer: `skills/architecture-premise-audit/SKILL.md:69`, `:70`, `:71`, `:73`
Evidence:
- `:69-71` sits after step 6 (`:65-67`) and before the `## Verdict And Output` header at `:73`, carrying no number, unlike the six numbered actions at `:48`, `:50`, `:53`, `:57`, `:61`, `:65`.
- It is procedurally necessary: the Verdict section consumes those classifications.
- It depends on "supported" and "candidates", neither defined — see F008 for "candidates".
Contract violated:
- The numbered sequence does not cover everything the Procedure requires, so a reader following the numbers can miss a mandatory action.
Plausible failure mode:
- Ambiguous whether classification happens once at the end, per candidate as they arise, inside step 6, or after it. Ordering changes which candidates get classified when step 6 terminates.
Durable solution hypothesis:
- Number it as step 7, or fold it into step 5 where candidates are already in hand.
Disconfirming check:
- `sed -n '65,73p' skills/architecture-premise-audit/SKILL.md` shows the unnumbered block between step 6 and the section header.

### F018 [P2] Step 5 requires "independent truth"; the term is undefined in the skill, and its only elaboration sits behind the conditional reference gate

Severity: P2 | Confidence: high
Candidates: S4-09-03
Source pointer: `skills/test-proof-debt-audit/SKILL.md:16`, `:3`, `:33`; `skills/test-proof-debt-audit/references/catalog.md:24`
Evidence:
- `:16`, step 5: "Check whether expected values come from independent truth."
- The term is defined nowhere in `SKILL.md`. `catalog.md:24` uses the phrase once — "a validator that accepts its own generated output without independent truth" — as an example smell, not a definition.
- `catalog.md` is gated at `SKILL.md:33`: "only for a broad user-requested audit or when concrete replacement examples are needed". The skill's own description at `:3` is "Audit one named behavioral claim" — the narrow case that gate does not clearly cover.
Contract violated:
- A mandatory step requiring a judgment the agent has no stated way to make, on the default path.
Plausible failure mode:
- The agent applies its own unstated notion. Is a golden file generated by the same code path independent truth? Is a spec document? Two audits of the same proof reach opposite step-5 results with no textual basis for calling either wrong.
Durable solution hypothesis:
- Define the term inline in `SKILL.md` — expected values derived from a source that would not change if the implementation under test changed.
Disconfirming check:
- `grep -n -i 'independent truth' skills/test-proof-debt-audit/SKILL.md skills/test-proof-debt-audit/references/catalog.md` returns `SKILL.md:16` and `catalog.md:24`, neither a definition.

### F019 [P2] The history-only rule offers three dispositions for one detected condition with no discriminator, and the reference repeats the same undiscriminated triple

Severity: P2 | Confidence: medium
Candidates: S4-09-05, S4-09-08, S4-10-29 (dissent)
Source pointer: `skills/test-proof-debt-audit/SKILL.md:22`, `:23`, `:24`, `:19`; `skills/test-proof-debt-audit/references/catalog.md:39`, `:32`
Evidence:
- `:22-24`: "Replace it with current-boundary cases, / demote it to closeout-only evidence, or delete it unless the historical value / is itself a current public machine/security contract." Three outcomes, one condition, no assignment rule.
- `:19-22` supplies the debt pattern and the derivability question, not a rule for choosing among the three.
- `catalog.md:39` repeats it for the general proxy case — "Delete, demote, or replace it." — omitting `closeout-only`, `keep` and `escalate` and adding no discriminator. Better Routes at `:32-37` is a list of per-smell substitution recipes, not a cross-smell chooser.
Contract violated:
- One diagnosed case maps to three terminal actions with no rule. The inverse of a disjointness failure, and equally non-executable.
Plausible failure mode:
- Identical inputs produce different dispositions across audits; one agent deletes what another replaces, and no text calls either wrong. Any downstream aggregation by disposition is meaningless.
Durable solution hypothesis:
- Add discriminators at `:22-24`: replace when a current-boundary equivalent exists; demote when the test still exercises real code but not the claimed behavior; delete when no code path remains. Then have `catalog.md:39` point back rather than restate.
Disconfirming check:
- `sed -n '19,24p' skills/test-proof-debt-audit/SKILL.md` and `sed -n '39p' skills/test-proof-debt-audit/references/catalog.md`.
Dissent, recorded: S4-10-29 reads `catalog.md:39` as a redundant restatement of three of the six tokens rather than as an undiscriminated choice, and notes the subset may implicitly narrow the applicable dispositions for proxies specifically — in which case it carries information `SKILL.md` does not. That reading is live and unstated; on either reading the line needs an edit.

### F020 [P2] The history-only rule's exception branch supplies a condition and no disposition token

Severity: P2 | Confidence: medium-high
Candidates: S4-09-06
Source pointer: `skills/test-proof-debt-audit/SKILL.md:23`, `:24`, `:17`
Evidence:
- `:23-24`: "… or delete it unless the historical value / is itself a current public machine/security contract."
- The clause identifies a live branch — the value is a current contract, so it is not proof debt — and attaches none of the six tokens at `:17` to it.
Contract violated:
- A branch of the procedure that the mandatory six-way vocabulary must cover and does not.
Plausible failure mode:
- The agent correctly identifies the exception, then has no instructed token. It may default to `escalate` (unwarranted — the case is resolved) or invent a phrase outside the six, breaking any consumer expecting one of the six literals.
Durable solution hypothesis:
- "… in which case choose `keep`." Note the dependency on F022: once `keep` has a stated condition, this branch resolves through it automatically.
Disconfirming check:
- `sed -n '17p;22,24p' skills/test-proof-debt-audit/SKILL.md`.

### F021 [P2] `demote` and `closeout-only` are listed as co-equal dispositions and used as verb-and-destination two lines later

Severity: P2 | Confidence: medium-high
Candidates: S4-09-04
Source pointer: `skills/test-proof-debt-audit/SKILL.md:17`, `:23`, `:26`
Evidence:
- `:17` lists `demote` and `closeout-only` as two of six co-equal choices.
- `:23`: "demote it to closeout-only evidence" — closeout-only is the *destination* of demoting, not an independent choice.
- `:26`: "Proxy evidence can support lint or closeout but cannot prove runtime behavior." reinforces closeout as a tier, not a verdict.
Contract violated:
- Two tokens in a closed vocabulary that cannot be shown disjoint. Either they are redundant, or one names an undocumented third state; neither reading is stated.
Plausible failure mode:
- Identical proxy-evidence cases get different tokens across audits, breaking any downstream grouping by disposition — the same consumer F004 already leaves without a disposition field at all.
Durable solution hypothesis:
- Merge them into `demote`, whose destination `:23` already states; or state what distinguishes choosing `closeout-only` directly from choosing `demote`.
Disconfirming check:
- `grep -n 'closeout' skills/test-proof-debt-audit/SKILL.md` returns `:17`, `:23`, `:26` — no line defines `closeout-only` as reachable other than via demotion.

### F022 [P2] `keep` is the healthy-case disposition and has no criteria anywhere

Severity: P2 | Confidence: medium-high
Candidates: S4-09-02
Source pointer: `skills/test-proof-debt-audit/SKILL.md:17`, `:19`, `:31`
Evidence:
- `grep -n '`keep`\|keep' skills/test-proof-debt-audit/SKILL.md` returns `:17` only. The token appears once, in the list.
- It is the nearest thing the skill has to "no debt found", and that mapping is never stated; it must be inferred by elimination from `:19-31`, which never use the word.
Contract violated:
- The disposition an audit reaches when nothing is wrong has no stated trigger, in a skill whose entire output is one of six tokens.
Plausible failure mode:
- Two agents auditing the same solid proof report different dispositions, because "the proof is fine" has no canonical token and `replace`/`demote` are the ones with worked guidance at `:19-24`.
Durable solution hypothesis:
- "Choose `keep` when the proof is deletion-sensitive at step 4 and its expected values trace to independent truth at step 5." That defines it out of the two tests the skill already performs, and closes F020's exception branch as a side effect.
Disconfirming check:
- The grep above — any sentence pairing "keep" with a condition falsifies this.

### F023 [P2] The widened search has an entry condition and no exit condition, and no route back into the disposition procedure

Severity: P2 | Confidence: high
Candidates: S4-03-08
Source pointer: `skills/test-proof-debt-audit/SKILL.md:33`, `:12`, `:30`; `skills/test-proof-debt-audit/references/catalog.md:3`, `:7`, `:17`
Evidence:
- `:12-17` is written for exactly one claim/proof pair; step 1 (`:12`) names the claim.
- `:33` authorizes loading the catalog for "a broad user-requested audit"; `catalog.md:3` confirms the reference exists to widen.
- Once widened, `catalog.md:7` "Search for:" opens seven families at `:9-15` with no stopping condition, no ledger, and no analog of `architecture-premise-audit`'s step 6.
- `catalog.md:17`: "Search hits are leads, not findings." Nothing states what closes a lead out.
- Step 1 is never re-entered for leads a widened search turns up. The only "stop" in the skill (`:30`) is conditioned on the user's request mode, not on completion.
Contract violated:
- A search mode with a defined entry and no exit, whose results have no defined path into the six-way disposition the skill exists to produce.
Plausible failure mode:
- Under a broad audit the agent may stop after the first hit, after one family, or never — all equally compliant — and no report field distinguishes "search space exhausted" from "search space abandoned".
Durable solution hypothesis:
- Require the report to enumerate the families actually run, require each lead to be dispositioned via the six or explicitly deferred, and state the stopping condition. Note this is *not* a contradiction with `:8-10`'s narrow scope — `:33`'s user-requested gate reconciles that; the gap is purely the missing exit.
Disconfirming check:
- `sed -n '33p' skills/test-proof-debt-audit/SKILL.md` and `sed -n '3p;7p;17p' skills/test-proof-debt-audit/references/catalog.md` — a stopping rule in either file falsifies this.

### F024 [P2] The catalog's load condition is undefined, unanchored to a step, and unreconciled with the skill's own single-claim scope

Severity: P2 | Confidence: medium
Candidates: S4-04-05, S4-04-06, S4-04-07, S4-10-24
Source pointer: `skills/test-proof-debt-audit/SKILL.md:33`, `:3`, `:8`; `skills/test-proof-debt-audit/references/catalog.md:3`
Evidence:
- `:33`: "only for a broad user-requested audit or when concrete replacement examples are needed". "Broad" carries no claim count, file count, or scope threshold.
- Unlike the sibling skill's condition, no Procedure step is named as the point to check it, so whether to check once or repeatedly across steps 1-6 is unstated.
- `:8-10` scopes the skill to "the claim and proof route named by the user" (singular) and forbids a repository-wide proof audit. If "broad" means the scope the skill disclaims, the first disjunct is unreachable under compliant use — dead text. If it means the user explicitly widening, the two are compatible. The text does not disambiguate.
- Part of the real precondition is stated only *inside* the gated file: `catalog.md:3`, "after the live claim and scan roots are known". An agent deciding when to open the file from `:33` alone learns the ordering advice only after it is too late to follow it.
Contract violated:
- A load condition whose key term is undefined, whose evaluation point is unstated, and part of whose precondition is unreadable until the condition has already been resolved.
Plausible failure mode:
- For the ordinary single-claim invocation the description promises, the first branch never fires, so the catalog is reached only via "concrete replacement examples are needed" — and Search Families and Common Smells, two of its three sections, go unread in typical use.
Durable solution hypothesis:
- Give "broad" an observable proxy, name the step at which the condition is evaluated, fold `catalog.md:3`'s precondition into `:33`, and state whether user-directed widening is the intended exception to `:8-10`.
Disconfirming check:
- `sed -n '3p;8,10p;33p' skills/test-proof-debt-audit/SKILL.md`. `catalog.md:3`'s framing implies widening is an anticipated legitimate mode, which favors the compatible reading and lowers confidence without resolving `SKILL.md`'s own text.

### F025 [P2] The read-only boundary is a prose prohibition with no self-check, in a procedure whose steps 3 and 5 invite exactly the drift it forbids

Severity: P2 | Confidence: high
Candidates: S4-06-04, S4-10-04
Source pointer: `skills/architecture-premise-audit/SKILL.md:9`, `:10`, `:21`, `:53`, `:61`, `:92`
Evidence:
- `:9-10`: "Audit read-only / unless the user separately requests changes."
- `:21-22`: "Do not turn a broad audit into implementation, issue creation, or a second / review workflow."
- Neither the Procedure (`:48-67`) nor Verdict And Output (`:73-95`) contains any pre-flight restriction, self-check, or completion-time verification that the agent stayed read-only.
- Step 3 (`:53`) traces entry points and step 5 (`:61`) constructs a counterfactual; output item 7 (`:92`) is "prioritized decisions". These are the points at which an agent with ambient write access has both motive and opportunity.
Contract violated:
- A boundary stated as a prohibition that nothing can detect being crossed. Enforcement rests entirely on the agent's own compliance, and the report format carries no evidence either way.
Plausible failure mode:
- An agent drifts into an edit while tracing or constructing the counterfactual; neither it nor a reviewer has any signal that the boundary was crossed, and the report reads identically.
Durable solution hypothesis:
- Add a completion-time self-check to the output: name every file created, edited, or deleted during the audit, or state that none was. That turns the prohibition into something a reader can verify, at the cost of one output line. Pair it with an explicit statement that write tools are not invoked regardless of ambient permissions.
Disconfirming check:
- `grep -n -i 'read-only\|do not edit\|do not modify\|no files' skills/architecture-premise-audit/SKILL.md` returns `:9` and nothing in the Procedure or output sections.

### F026 [P2] "A second review workflow" is undefined, and step 5's own mandatory deep-check is textually indistinguishable from one

Severity: P2 | Confidence: medium
Candidates: S4-06-05, S4-07-02
Source pointer: `skills/architecture-premise-audit/SKILL.md:21`, `:22`, `:61`, `:62`; `skills/architecture-premise-audit/references/structural-antipatterns.md:116`, `:121`
Evidence:
- `:21-22` forbids "a second / review workflow"; the phrase is defined nowhere in the 95-line file.
- `:61-64`, step 5, requires tracing real callers, naming the exact amplification route, constructing the cleaner counterfactual, giving the strongest counterargument, and stating a falsifier. At sufficient depth that reads exactly like an independent design review.
- `structural-antipatterns.md:116-124`, "Boundary and proof laundering" — transport ACK treated as application acceptance (`:116-118`); a mock or replica cited for a production causal chain it never reaches (`:121-122`) — is `test-proof-debt-audit`'s entire subject matter. If step 5 surfaces proof laundering, invoking the sibling skill on that citation is textually indistinguishable from the correct handoff and from the prohibited second workflow.
Contract violated:
- A prohibition with no positive definition, sitting against a mandatory step that satisfies any plain reading of it.
Plausible failure mode:
- Two agents facing an identical step-5 finding decide oppositely; one under-serves step 5's own requirement to name the amplification route with evidence, in order to stay clear of a boundary it cannot locate.
Durable solution hypothesis:
- Define the prohibition by exclusion — a standalone design document, a tracked ticket, or auditing modules outside the compared slice — so the forbidden thing is nameable.
Disconfirming check:
- `grep -n -i 'second review\|review workflow' skills/architecture-premise-audit/SKILL.md` returns `:21-22` only. The clause may be aimed at recursive `ultra-review` rather than at the sibling; the text does not say, so both readings stay live.

### F027 [P2] Nothing states that the five verdict tokens are labels for a reader rather than directives to the executing agent

Severity: P2 | Confidence: medium
Candidates: S4-06-07, S4-06-10
Source pointer: `skills/architecture-premise-audit/SKILL.md:75`, `:80`, `:9`, `:23`, `:94`
Evidence:
- `:75` "Lead with one verdict:" and `:77-81` list five tokens. `:80` is `STOP_AND_REDIRECT` — imperative in form, emitted by an agent that generally has write access.
- The read-only clause at `:9-10` may be read as a blanket override, but it sits 68 lines away with no cross-reference from the verdict list.
- `:23-24` ("Ask only when one missing fact would reverse the verdict") and `:94-95` ("do not end with an unranked option menu or an interview questionnaire") both push toward a decisive verdict rather than a consultation.
Contract violated:
- A controlled vocabulary in imperative form with no statement of its illocutionary force. Whether emitting `STOP_AND_REDIRECT` classifies a finding or instructs an action is left to inference.
Plausible failure mode:
- Compounded rather than standalone: the tokens read as instructions, and `:23-24` plus `:94-95` reduce the chance a human is consulted before the conclusion lands as a confident recommendation. Neither clause needs changing in isolation; one sentence on the tokens neutralizes the interaction.
Durable solution hypothesis:
- One sentence after `:81`: "These verdicts classify the audit for the reader; emitting one is not authorization to act on it."
Disconfirming check:
- `sed -n '75,81p' skills/architecture-premise-audit/SKILL.md` — a disclaimer in the verdict section falsifies this.

### F028 [P2] Two of the five verdicts name a redirect and the file never says what to redirect to

Severity: P2 | Confidence: medium
Candidates: S4-07-06
Source pointer: `skills/architecture-premise-audit/SKILL.md:79`, `:80`
Evidence:
- `:79` `REDIRECT_RECOMMENDED` and `:80` `STOP_AND_REDIRECT`. Both strongly imply routing somewhere; nothing in the 95-line file names a destination.
- Candidates the text leaves open: redirect to `test-proof-debt-audit`, to a human, to `repo-refresh`, or to a different architecture direction within the same project.
Contract violated:
- A named token implying a destination, in a closed vocabulary, with the destination unconstrained.
Plausible failure mode:
- Two agents emit the same verdict token and write completely different next-step prose; the report's actionable content varies with no textual basis.
Durable solution hypothesis:
- Define the redirect target inline — most likely "redirect the project's architecture direction", which is the reading the rest of the file supports — and say so, since the alternative reading (redirect the caller to another skill) makes this a boundary gap rather than a vocabulary gap.
Disconfirming check:
- `grep -n -i 'redirect' skills/architecture-premise-audit/SKILL.md` returns `:79`, `:80` and nothing else.

### F029 [P2] Each skill's body gestures at the other's domain; neither names the other, and neither states the handoff

Severity: P2 | Confidence: medium-high
Candidates: S4-07-01
Source pointer: `skills/test-proof-debt-audit/SKILL.md:29`; `skills/architecture-premise-audit/SKILL.md:17`, `:21`, `:55`
Evidence:
- `test-proof-debt-audit/SKILL.md:29`: "Weak proof does not authorize an architecture redesign." — `architecture-premise-audit`'s exact subject.
- `architecture-premise-audit/SKILL.md:17-18`: "Treat passing proof as evidence about an implementation, not proof that the / mechanism should exist." and `:55` "cited proof" in step 3 — `test-proof-debt-audit`'s exact subject.
- Confirmed by grep across all four files: **neither in-scope file names the other skill anywhere**; the only self-references are each file's own `name:` frontmatter at line 2.
Contract violated:
- A prohibition that gestures at a sibling domain without naming it or describing the handoff is not a decidable boundary.
Plausible failure mode:
- The agent cannot tell whether "do not authorize an architecture redesign" means stop entirely or route to the sibling. It silently drops the architectural implication, or invents an architecture judgment inline against its own assessment-only contract at `:30-31`.
Durable solution hypothesis:
- One sentence in each naming the other as the handoff destination, which also gives F028's `REDIRECT_RECOMMENDED` a concrete referent in at least one direction.
Disconfirming check:
- `grep -n 'architecture-premise-audit\|test-proof-debt-audit' skills/architecture-premise-audit/SKILL.md skills/test-proof-debt-audit/SKILL.md skills/architecture-premise-audit/references/structural-antipatterns.md skills/test-proof-debt-audit/references/catalog.md` returns the two frontmatter `name:` lines and nothing else.

### F030 [P2] The description's scope noun is narrower than the skill's own Boundaries line, so the case the reference was written for is invisible at selection time

Severity: P2 | Confidence: medium-high
Candidates: S4-05-01, S4-05-02
Source pointer: `skills/architecture-premise-audit/SKILL.md:3`, `:14`, `:26`, `:27`
Evidence:
- `:3`, the only text visible at selection: the sole positive scope noun is "a whole project".
- `:14`, Boundaries: "Work at the whole-project **or named broad-system** boundary requested by the user." A second, narrower scope the body explicitly serves.
- `:26-27`'s load trigger is written for exactly that narrower case — one named system with a suspected structural misfit, not an entire project.
Contract violated:
- A description that under-selects for a scope the body and its reference were written to handle.
Plausible failure mode:
- A user asking to audit one named subsystem for structural misfit — the reference's own use case — is not matched, and the skill plus its 151-line reference never fire for the case they exist for. Compounding: `:3`'s negative clause excludes "one named design concern", which a selecting agent may read as covering exactly that request.
Durable solution hypothesis:
- Make `:3`'s scope noun the same set as `:14`'s, and draw the line the two files currently leave undrawn: a design *decision* (excluded) versus a named subsystem's *archetype* (included).
Disconfirming check:
- `sed -n '3p;14p;26,27p' skills/architecture-premise-audit/SKILL.md`.

### F031 [P2] The description's negative scope clause supplies no test in either direction

Severity: P2 | Confidence: medium-high
Candidates: S4-05-03, S4-10-02
Source pointer: `skills/architecture-premise-audit/SKILL.md:3`
Evidence:
- `:3`: "Use only for an explicitly requested broad premise audit, not ordinary architecture review or one named design concern."
- Neither "ordinary architecture review" nor "one named design concern" has any test, example, or rule anywhere in the two `architecture-premise-audit` files that would let an agent compute whether a request falls inside or outside.
Contract violated:
- A clause that reads as a boundary and cannot steer a borderline decision either way — the deletion-sensitivity class applied to a selection clause. **This is the clause `s2` F043 held up as the exemplar to copy into `ultra-review`'s description** (see Prior Round Guard).
Plausible failure mode:
- Both directions. A plain "review whether our design fits our needs" is excluded on a phrasing technicality; a narrow single-component gripe framed with the word "broad" slips past and triggers the full six-step whole-project procedure.
Durable solution hypothesis:
- Anchor the negative clause in the Procedure's own vocabulary — excluded when the request names a mechanism rather than a product boundary, since a product boundary is what step 1 requires. Keep the clause: S4-10-02 shows it is the only gate preventing selection for narrow single-concern questions, and deleting it would make the description worse, not better.
Disconfirming check:
- `grep -n -i 'ordinary architecture review\|named design concern' skills/architecture-premise-audit/SKILL.md` returns `:3` only. If selection here is always done by a human who already knows the intended distinction, the ambiguity is harmless in practice — worth confirming against normal usage rather than assuming.

### F032 [P2] The description's closed list of proof artifacts omits the catalog's signature smell

Severity: P2 | Confidence: medium-high
Candidates: S4-05-05
Source pointer: `skills/test-proof-debt-audit/SKILL.md:3`, `:14`; `skills/test-proof-debt-audit/references/catalog.md:10`, `:22`, `:23`
Evidence:
- `:3`: "the test, validator, benchmark, or gate cited as proof" — a closed four-item list.
- `:14`, step 3, treats "proxy text/metadata" as one of four observation categories.
- `catalog.md:10` ("source reads, substring checks, regexes, headings, summaries, labels, markers, and registration names"), `:22` ("source or document text used as evidence that runtime behavior executes") and `:23` ("report prose or test registration used as proof that a scenario ran") make cited prose arguably the catalog's central smell.
Contract violated:
- Under-selection for the skill's own headline case. A caller whose cited proof is a README sentence or a code comment has no keyword in the description to match.
Plausible failure mode:
- "The README says this is deprecated, so it's handled" — the canonical proof-debt request — does not match any of the four nouns, and the skill is not selected.
Durable solution hypothesis:
- Extend `:3`'s list to include cited prose or metadata, matching `:14`'s own fourth category.
Disconfirming check:
- `sed -n '3p;14p' skills/test-proof-debt-audit/SKILL.md` and `sed -n '10p;22,23p' skills/test-proof-debt-audit/references/catalog.md`.

### F033 [P2] Two of the description's four exclusions turn away requests the body treats as in scope

Severity: P2 | Confidence: medium
Candidates: S4-05-06, S4-05-07
Source pointer: `skills/test-proof-debt-audit/SKILL.md:3`, `:15`; `skills/test-proof-debt-audit/references/catalog.md:10`, `:22`
Evidence:
- `:3` excludes "failing tests" and "weak coverage" outright.
- **Weak coverage**: the same phrase literally describes "a specific coverage-based gate cited as proof of one named claim, and that gate is weak" — squarely inside the positive clause on the same line. No text distinguishes the readings.
- **Failing tests**: a proxy or substring test that breaks on a benign behavior-preserving refactor while the real behavior is intact is the inverted case of the skill's own deletion-sensitivity test at `:15`, and matches `catalog.md:10`/`:22`. It presents to a user as "this test is failing but the code is fine".
Contract violated:
- Exclusions phrased broadly enough to exclude the skill's own subject matter.
Plausible failure mode:
- The user reporting precisely the proof-debt symptom is turned away by a verbatim exclusion, with no textual test separating "failing because the claim broke" from "failing because the proof route is brittle".
Durable solution hypothesis:
- Qualify both: exclude the general coverage *metric* rather than a cited coverage gate, and exclude genuine behavior regressions rather than all failing tests.
Disconfirming check:
- `sed -n '3p;15p' skills/test-proof-debt-audit/SKILL.md`.

### F034 [P2] The reference frames itself twice as search lenses and contains no search procedure, while its sibling catalog does

Severity: P2 | Confidence: high on the inconsistency, medium on the harm
Candidates: S4-08-01, S4-08-06
Source pointer: `skills/architecture-premise-audit/references/structural-antipatterns.md:3`, `:107`, `:8`; `skills/architecture-premise-audit/SKILL.md:29`; `skills/test-proof-debt-audit/references/catalog.md:5`, `:7`
Evidence:
- The framing appears at `structural-antipatterns.md:3` and again at `architecture-premise-audit/SKILL.md:29-30`.
- `grep -n -iE '\b(search|grep|trace|look for|inspect|scan|find)\b' skills/architecture-premise-audit/references/structural-antipatterns.md` returns **two** lines: `:3` (the framing sentence itself) and `:121` ("source scan", inside a pattern description). No verb of search directs the agent anywhere.
- Every section from `:8` to `:144` is a flat bulleted enumeration of named failure conditions — the shape of a checklist.
- Contrast the sibling: `test-proof-debt-audit/references/catalog.md:5` is a `## Search Families` header and `:7` is a literal "Search for:" followed by concrete substrings to hunt.
- The one exception inside the file is `:107-112`, "Local-excellence trap", the only section phrased as investigative questions an agent could apply while searching. It demonstrates in exactly one place what the file's own framing calls for.
Contract violated:
- A usage mode stated twice and operationalized nowhere. The instruction says "not a checklist" and the artifact is a checklist.
Plausible failure mode:
- The agent walks the bullet list top to bottom checking each pattern — the behavior the file disclaims — because that is the natural reading of a bulleted taxonomy with no search procedure.
Durable solution hypothesis:
- Add a per-section search procedure in the sibling catalog's shape, using `:107-112` as the in-file model; or drop the framing and document the file honestly as a classification taxonomy applied to evidence gathered elsewhere.
Disconfirming check:
- The search-verb grep above.

### F035 [P2] A mandatory step-3 field is answered from a four-item taxonomy or a six-item one depending on whether the optional reference was loaded

Severity: P2 | Confidence: medium
Candidates: S4-01-08, S4-01-07
Source pointer: `skills/test-proof-debt-audit/SKILL.md:14`, `:17`, `:23`, `:33`; `skills/test-proof-debt-audit/references/catalog.md:37`
Evidence:
- `:14`, step 3, mandatory: "behavior, machine-readable contract, performance, or proxy text/metadata" — four items.
- `catalog.md:37`: "Replace broad proof naming with the truthful category: test, benchmark, validation, lint, review aid, or closeout audit." — six items, for what is functionally the same question.
- The two share no term and are never reconciled. `catalog.md` is conditionally loaded per `:33`.
- Adjacent collision: `closeout-only` (disposition, `:17`, `:23`) versus "closeout audit" (truthful category, `catalog.md:37`) — near-synonyms, different spellings, no cross-reference.
Contract violated:
- The answer to a mandatory field changes depending on whether an optional reference was read — the F024 conditional-load gap made visible in the output.
Plausible failure mode:
- An agent that loaded the catalog conflates the relabeling category with the disposition action, or treats it as a seventh disposition. Report vocabulary becomes a function of the load path rather than of the audit.
Durable solution hypothesis:
- One taxonomy, stated in `SKILL.md:14`, with `catalog.md:37` referring to it rather than restating a different one; and rename either `closeout-only` or "closeout audit".
Disconfirming check:
- `sed -n '14p' skills/test-proof-debt-audit/SKILL.md` and `sed -n '37p' skills/test-proof-debt-audit/references/catalog.md`.

### F036 [P3] Every example under `## Domain examples` is game networking, in a file whose load trigger explicitly covers other domains

Severity: P3 | Confidence: high
Candidates: S4-08-03, S4-08-04
Source pointer: `skills/architecture-premise-audit/references/structural-antipatterns.md:126`, `:134`, `:137`, `:141`, `:72`, `:76`, `:116`; `skills/architecture-premise-audit/SKILL.md:26`
Evidence:
- `:126-144`, all five bullets: client-side prediction, reconciliation via ACK, server-authoritative click-to-move (`:134`), high-frequency supersedable movement (`:137`), large multiplayer worlds with interest management and rollback (`:141`). Not one example for payments, pipelines, storage, ETL, or collaboration.
- `SKILL.md:26-27`'s trigger extends explicitly to "another system with a suspected structural / misfit".
- Game vocabulary also appears inside sections carrying no domain qualifier: `:72` "per-tick allocation … scans proportional to total entities … pathfinding" in a generic hot-path list; `:76-78` "session death" in a generic buffering list; and `:118` "player-visible outcome" appended after three fully generic terms ("application acceptance, authoritative mutation, command completion") in Boundary and proof laundering, a section not scoped to games at all.
Contract violated:
- A section titled generically that delivers a single-domain sample, and domain-general lenses carrying domain-specific closing terms.
Plausible failure mode:
- Audits of non-game systems — the explicit majority case per the trigger — get zero grounded illustrations from the one section meant to supply them. Worse at `:118`: an agent auditing a batch pipeline reads "player-visible outcome", judges the bullet inapplicable, and loses the transport-ACK-versus-application-acceptance lens, which is valuable everywhere.
Durable solution hypothesis:
- Rename the section honestly, or add at least one non-game worked example; and make the closing terms in `:72`, `:76-78` and `:116-118` domain-neutral, moving the game phrasing into Domain examples where it belongs.
Disconfirming check:
- `sed -n '126,144p' skills/architecture-premise-audit/references/structural-antipatterns.md` and read for a non-game bullet.

### F037 [P3] Step 2 draws on "established domain mechanisms" and the bundle names no source for them outside the conditionally-loaded reference

Severity: P3 | Confidence: medium
Candidates: S4-02-10
Source pointer: `skills/architecture-premise-audit/SKILL.md:50`, `:51`, `:26`, `:3`
Evidence:
- `:50-52`, step 2: "From product needs and established domain / mechanisms, list the responsibilities that should exist …"
- The only named source of domain-mechanism knowledge in the bundle is `structural-antipatterns.md`, gated at `:26-30` to realtime multiplayer / MMO / suspected misfit.
- `:3` targets whole-project audits generally. For a payments backend, a CMS, or a data pipeline, no step says where those mechanisms come from.
Contract violated:
- A mandatory input with no stated provenance, so the atlas's completeness cannot be audited against any stated standard.
Plausible failure mode:
- The atlas rests entirely on the agent's latent knowledge, which may be an acceptable implicit default for an LLM-executed prose skill — but it is never stated as such, so a reader cannot tell whether a thin atlas reflects a thin domain or a thin model.
Durable solution hypothesis:
- Acknowledge the source explicitly ("draw on your own domain knowledge and state the mechanisms you assumed"), which also makes the assumption auditable; or broaden the reference so it covers non-game domains.
Disconfirming check:
- `sed -n '50,52p' skills/architecture-premise-audit/SKILL.md` and search the bundle for any other named source of domain mechanisms.

### F038 [P3] The Audit Slice schema requires an axis no later step, classification, or verdict ever consumes

Severity: P3 | Confidence: medium-high
Candidates: S4-10-08
Source pointer: `skills/architecture-premise-audit/SKILL.md:42`, `:57`, `:69`, `:85`
Evidence:
- `:42`: "- reusable-platform versus application responsibility." — one of six required slice elements.
- `grep -n -i 'platform' skills/architecture-premise-audit/SKILL.md` returns `:42` only. No Procedure step, classification token, or output item references the axis again.
Contract violated:
- Mandatory work whose product is never read. An agent can satisfy every downstream step and produce every required output section without ever determining it.
Plausible failure mode:
- Dead effort at best; at worst the agent skips it, correctly inferring it is unused, and a future edit that starts depending on it finds it absent.
Durable solution hypothesis:
- Wire it into step 4's comparison questions — "whether the mechanism belongs to a reusable platform or to this application" is a natural fifth question there — or delete it.
Disconfirming check:
- The grep above.

### F039 [P3] "Premise" is a live selection keyword with no operational referent in the body

Severity: P3 | Confidence: low-medium
Candidates: S4-05-08
Source pointer: `skills/architecture-premise-audit/SKILL.md:2`, `:3`, `:6`, `:87`
Evidence:
- `grep -n -i 'premise' skills/architecture-premise-audit/SKILL.md` returns four lines: `:2` (the `name:` field), `:3` (the description), `:6` (the H1), and `:87` ("hidden premise" of a specific finding — a different concept).
- The Procedure and everything the skill does is phrased in "archetype", "expected atlas", "observed map". What auditing "a premise" consists of, as distinct from auditing an archetype, is never operationalized.
Contract violated:
- Selection runs on name and description alone, so "premise" is a keyword a caller can match against with no defined referent in the body to check a request against.
Plausible failure mode:
- Mild. A caller asking to "audit the premise of our design" matches on a word the skill never defines; whether the skill is right for them depends on the archetype vocabulary they cannot see.
Durable solution hypothesis:
- Define the two as synonyms once in the body, or rename consistently. Cosmetic naming drift is common and may be harmless; filed because the brief forbids suppression.
Disconfirming check:
- The grep above.

### F040 [P3] The six classifications are unformatted prose where every other controlled vocabulary in the bundle is backticked

Severity: P3 | Confidence: low-medium
Candidates: S4-01-05
Source pointer: `skills/architecture-premise-audit/SKILL.md:69`, `:70`, `:71`, `:77`, `:91`; `skills/architecture-premise-audit/references/structural-antipatterns.md:148`
Evidence:
- `:69-71`, the six classifications, are plain prose. The five verdicts (`:77-81`), the two output tokens (`:91`), and the reference's two exoneration tokens (`:148`) are all backticked.
Contract violated:
- If backticking signals "this literal string must appear", the classification set's formatting leaves undecided whether "architecture defect" is a required literal or a paraphrasable category.
Plausible failure mode:
- Agents render it as "structural defect" or "architecture-level defect", defeating any grep-based consumer — material given that nothing validates report shape.
Durable solution hypothesis:
- Format the six identically to the other vocabularies, or state in one clause that they are descriptive categories rather than literals.
Disconfirming check:
- `sed -n '69,71p;77,81p;91p' skills/architecture-premise-audit/SKILL.md`.

### F041 [P3] Step 4 works over slices and step 6 covers a different axis entirely, so completing the ledger does not entail that every slice was compared

Severity: P3 | Confidence: low-moderate
Candidates: S4-03-06
Source pointer: `skills/architecture-premise-audit/SKILL.md:57`, `:65`, `:66`, `:44`
Evidence:
- `:57`, step 4, operates over slices — cross-cutting product-responsibility units, explicitly "A slice may cross modules, and one module may contain several slices" (`:44`).
- `:65-66`, step 6, covers ingress / state family / durable effect / expensive operation / external output, and never mentions slices.
Contract violated:
- The termination gate runs on a different decomposition than the mandatory comparison, with no stated relationship between the two.
Plausible failure mode:
- Every ingress, state, effect, operation and output is ticked while a cross-cutting slice — the platform-versus-application split for a capability spanning several already-covered mechanisms — was never separately compared.
Durable solution hypothesis:
- One ledger row per slice cross-referenced to its members; or state that the ingress/effect ledger is authoritative and slices are only an analysis lens. Rated P3 rather than higher because the two axes may be intended as equivalent decompositions — the text does not clarify, and F001 must be fixed before this one is even well-posed.
Disconfirming check:
- `sed -n '44p;57p;65,67p' skills/architecture-premise-audit/SKILL.md`.

### F042 [P3] Four rules are stated twice in different places, and in two cases the copies could drift apart

Severity: P3 | Confidence: medium
Candidates: S4-10-15 (partially rejected on its "verbatim" claim — see Candidates Rejected On Source), S4-10-01, S4-10-07, S4-06-08, S4-10-22
Source pointer: `skills/architecture-premise-audit/references/structural-antipatterns.md:3`; `skills/architecture-premise-audit/SKILL.md:29`, `:30`, `:3`, `:15`, `:16`, `:34`, `:35`, `:55`; `skills/test-proof-debt-audit/SKILL.md:30`, `:31`
Evidence, four pairs:
- **Framing.** `structural-antipatterns.md:3` and `architecture-premise-audit/SKILL.md:29-30` carry the same instruction in near-identical wording. `:29-30` is in the unconditionally-read file and is what sends the agent to the reference, so the reference's copy adds no information the agent lacks.
- **Description restating Boundaries.** `:3`'s "by deriving expected product capabilities before trusting repository vocabulary" is `:15-16`'s Boundaries rule restated. Dead only for post-load behavior — the description also does selection-time work, which is why this is P3 and not a deletion.
- **Anti-repository-trust, third statement.** `:55-56` "Do not copy the repository's / decomposition without testing it" follows `:15-16` and `:34-35`. An agent ignoring `:55` and honoring the other two behaves the same.
- **Assessment-only, two directions.** `test-proof-debt-audit/SKILL.md:30-31`: "If / the user requested assessment only, report and stop; modify proof or production code / only when requested." Honoring either half necessarily honors the other; no request partitions them differently.
Contract violated:
- None directly. This is redundancy, and the risk is that duplicated rules drift apart in a future edit — which is exactly the mechanism producing F005's contradiction between `catalog.md:3` and `test-proof-debt-audit/SKILL.md:8-10`.
Plausible failure mode:
- A later edit changes one copy and not the other, and the bundle then contains two rules where it meant to contain one.
Durable solution hypothesis:
- Keep each rule in one place. For the framing pair, let the reference own it, since it applies while reading the reference. For the description pair, keep both — the duplication is load-bearing at selection time. For `:55`, keep it if the just-in-time placement is deliberate and say so. For `:30-31`, keep the positive framing, which is the more general of the two.
Disconfirming check:
- `sed -n '3p' skills/architecture-premise-audit/references/structural-antipatterns.md` against `sed -n '29,30p' skills/architecture-premise-audit/SKILL.md`; and `sed -n '3p;15,16p;34,35p;55,56p' skills/architecture-premise-audit/SKILL.md`. For `:55`: construct a case where an agent honors `:15-16` and `:34-35` and would still copy the decomposition at step 3. If one exists, `:55` is load-bearing.

### F043 [P3] Two sentences state conditions no agent could deliberately violate

Severity: P3 | Confidence: medium-high
Candidates: S4-10-26, S4-10-12
Source pointer: `skills/test-proof-debt-audit/references/catalog.md:17`; `skills/architecture-premise-audit/SKILL.md:94`, `:75`
Evidence:
- `catalog.md:17`, first sentence: "Use repository-appropriate search and semantic tools." No agent deliberately uses repository-inappropriate tools; the sentence discriminates no behavior.
- `architecture-premise-audit/SKILL.md:94`: "Make the best evidence-supported judgment available." `:75` plus the fixed five-token list already force the agent to pick exactly one verdict.
- Note the contrast within the same line: `catalog.md:17`'s *second* sentence, "Search hits are leads, not findings.", is the only guard in the catalog against reporting raw search results as findings, and is load-bearing (see Candidate Reconciliation).
Contract violated:
- None. Dead surface.
Plausible failure mode:
- No behavioral failure; the cost is that a reader looking for the operative rule has to filter past sentences that are not one.
Durable solution hypothesis:
- Delete `catalog.md:17`'s first sentence, or replace it with the specific strategies a generic grep would miss. Delete `SKILL.md:94`'s first sentence, or replace it with a checkable constraint such as citing the strongest counter-evidence considered.
Disconfirming check:
- For `SKILL.md:94`: construct a case where an agent picks a valid verdict token yet demonstrably fails "best judgment" in a way no other rule catches. If one exists, the sentence is load-bearing.

### F044 [P3] Search Families and Common Smells describe substantially the same smells from two angles

Severity: P3 | Confidence: medium
Candidates: S4-10-28
Source pointer: `skills/test-proof-debt-audit/references/catalog.md:5`, `:11`, `:13`, `:19`, `:21`, `:22`, `:25`, `:26`
Evidence:
- Paired: `:13` ("negative tests that hard-code a retired representation") ↔ `:21` ("permanent tests whose only claim is that a retired name or dependency is absent"); `:11` ("validators or workflows whose names claim proof while their assertions only inspect metadata or prose") ↔ `:22-23`.
- Unpaired, and the scout's own scoping: `:25` (a pass-through wrapper tested more deeply than the owner it forwards to) and `:26` (full error-message prose locked where a typed rejection exists) have no clean Search Families counterpart, so the overlap is partial and the finding applies only to the paired subset.
Contract violated:
- None. Redundancy, not contradiction, so the risk is bloat rather than wrong output.
Plausible failure mode:
- Deleting either section leaves the other driving substantially the same behavior in most cases — meaning half the file's search guidance is doing the other half's work.
Durable solution hypothesis:
- Merge into one list pairing each search term with its recognition pattern, keeping `:25` and `:26` as recognition-only entries.
Disconfirming check:
- `sed -n '9,15p;21,28p' skills/test-proof-debt-audit/references/catalog.md` and pair them by hand.

### F045 [P3] Neither description states precedence against the three sibling skills whose descriptions match the same requests

Severity: P3 | Confidence: medium
Candidates: S4-07-04, S4-07-05, S4-07-03, S4-07-07, S4-05-10
Source pointer: `skills/architecture-premise-audit/SKILL.md:3`; `skills/test-proof-debt-audit/SKILL.md:3`, `:17`; `skills/ultra-review/SKILL.md:3`; `skills/repo-refresh/SKILL.md:3`, `:14`, `:78-85`; `skills/architecture-premise-audit/references/structural-antipatterns.md:91`, `:131`
Evidence — the last three source files are **outside the frozen scope**; they were read read-only and are included in this round's mechanical pointer verification:
- `ultra-review/SKILL.md:3`'s trigger, "a maximum-recall review of a scope before merge", is domain-unrestricted and would match "review this subsystem for architecture problems and weak test proof before we merge" as plausibly as either narrow audit. None of the three descriptions states precedence, exclusion, or composability. `s2` F043 recorded the mirror of this from `ultra-review`'s side.
- `repo-refresh/SKILL.md:3` claims "tests, proof machinery" and disposes of dead proof with `KEEP`/`MERGE`/`REWRITE`/`DEMOTE`/`DELETE`/`BLOCKED` (`:78-85`) — the same subject matter as `test-proof-debt-audit/SKILL.md:17` under a disjoint six-way vocabulary. `replace` and `closeout-only` have no `repo-refresh` analog; `MERGE`, `REWRITE`, `BLOCKED` have no `test-proof-debt-audit` analog. Neither file names the other. Mitigated by `repo-refresh/SKILL.md:14`'s "Never invoke this skill implicitly", which prevents accidental auto-selection but does not tell a human which skill to name.
- `architecture-premise-audit/SKILL.md:3` excludes "one named design concern" while the reference it loads is composed almost entirely of single-mechanism entries — `structural-antipatterns.md:91-92` (one plugin system before a second use case). "Is this plugin system overengineered before a second use case exists?" matches the catalog nearly verbatim while the description says the skill is not for it, and no other skill claims it either.
- Both in-scope descriptions use "named" as the discriminator — one excluding "one named design concern", the other requiring "one named behavioral claim" — which reads as a clean partition but is not: "our reconciliation system claims authoritative correction and the only test for it is a mock ACK check" matches `structural-antipatterns.md:131-133`'s own reconciliation example almost verbatim while being simultaneously excluded as a design concern and included as a behavioral claim.
- `test-proof-debt-audit/SKILL.md:3`'s positive clause is satisfied by almost any feature delivery including "a test proving the fix works"; only the caller's framing separates it from excluded "ordinary implementation", and neither the description nor `:8-10` states that framing test.
Contract violated:
- Descriptions that select on pattern-match order rather than on content, in a set where at least four skills claim adjacent ground.
Plausible failure mode:
- A caller gets either a noisy ten-scout recall list or a narrow single-claim judgment for a mixed request; or an audit-only assessment request gets a repository-wide `repo-refresh` sweep. Non-reproducible routing in both directions.
Durable solution hypothesis:
- A one-line disambiguator in each description naming the sibling that owns the adjacent case, which also gives F029's missing handoff a place to live.
Disconfirming check:
- `sed -n '3p' skills/ultra-review/SKILL.md skills/repo-refresh/SKILL.md skills/architecture-premise-audit/SKILL.md skills/test-proof-debt-audit/SKILL.md`. **If skills are always named explicitly by a human — as this campaign does — automatic selection never arbitrates and the whole class is inert.** That is worth confirming against normal usage rather than assuming, and is the reason this is P3.

### F046 [P3] Neither in-scope description offers a trigger token or a worked example, giving a selecting agent the least textual traction in the repository

Severity: P3 | Confidence: medium
Candidates: S4-05-09
Source pointer: `skills/architecture-premise-audit/SKILL.md:3`; `skills/test-proof-debt-audit/SKILL.md:3`; `skills/repo-refresh/SKILL.md:3`; `skills/herdr-delivery-workflow/SKILL.md:3`; `skills/ultra-review/SKILL.md:3`; `skills/prompt-leverage/SKILL.md:3`; `skills/frontend-design/SKILL.md:3`
Evidence — **coordinator re-derived on this turn**, because the comparison is outside the frozen scope (see Coordinator Method Note):
- `repo-refresh/SKILL.md:3` anchors on an explicit token ("Use only when the user explicitly invokes $repo-refresh"); `herdr-delivery-workflow/SKILL.md:3` similarly, on an explicit mention of Herdr.
- `ultra-review/SKILL.md:3`, `prompt-leverage/SKILL.md:3` and `frontend-design/SKILL.md:3` give concrete positive phrasings a selecting agent can match.
- The nine `beo-*` descriptions anchor on concrete domain nouns — BEO, `PASS_EXECUTE`, `TICKET.json`, `PLAN.md`, Beads, `br`/`bv`, `references/command-manifest.md`.
- Both in-scope descriptions rest on abstract qualifiers — "explicitly requested broad premise audit"; "one named behavioral claim… cited as proof" — with neither a token nor an example.
Contract violated:
- None directly; this is a comparative observation over the repository's own conventions, and the reason it is P3 rather than higher.
Plausible failure mode:
- Both false-positive and false-negative selection risk, which F030, F031, F032, F033 and F045 each instantiate concretely.
Durable solution hypothesis:
- Add one or two example phrasings in the `ultra-review`/`prompt-leverage` style. A fixed token is not appropriate here — these audits are meant to trigger from natural requests, which is why the `repo-refresh` form is not the right model for them.
Disconfirming check:
- `for f in skills/*/SKILL.md; do sed -n '3p' $f; done` and compare.

### F047 [P3] No individual bullet in the 151-line reference is mandatory, so the file's load-bearing content is thin relative to its size

Severity: P3 | Confidence: medium
Candidates: S4-10-17
Source pointer: `skills/architecture-premise-audit/references/structural-antipatterns.md:3`, `:8`, `:144`; `skills/architecture-premise-audit/SKILL.md:29`, `:57`, `:61`
Evidence:
- The file frames itself as search lenses at `:3` and is framed the same way at `SKILL.md:29-30`. Under that framing, an agent could drop any single one of the roughly thirty named antipatterns, taxes and domain examples across `:8-144` and remain fully compliant.
- No Procedure step or output requirement demands evidence that a specific named antipattern was checked; steps 4 (`:57`) and 5 (`:61`) speak generically of mechanism, cost, and requirement.
Contract violated:
- None if "use as lenses" is the genuine intent. This is a structural property, not a single-line bug, and it is a defect only if a reader expected the bullets to be individually enforceable.
Plausible failure mode:
- The file's cost — 151 of the bundle's 318 lines, roughly half — is not matched by enforceable content; only the load condition, the usage framing, and the Exoneration tokens are actually consumed by anything downstream.
Durable solution hypothesis:
- No change if the lens framing is intended; if enforceability is wanted, require the coverage ledger to record which lenses were applied, which also gives F001's ledger a second consumer.
Disconfirming check:
- Search `:46-95` of `SKILL.md` for any requirement that a named antipattern be checked. There is none.

### F048 [P3] "Wrong product category" and "Wrong archetype" sit under one header at the same level of abstraction with no stated distinction

Severity: P3 | Confidence: low
Candidates: S4-08-07
Source pointer: `skills/architecture-premise-audit/references/structural-antipatterns.md:6`, `:8`, `:24`
Evidence:
- `:6` is the `## Causal mechanism` header; `:8` "**Wrong product category:**" and `:24` "**Wrong archetype:**" both describe a system built on the wrong fundamental model, and no text distinguishes when a mismatch is one rather than the other.
Contract violated:
- None. Likely an under-explained two-grain distinction — category as what kind of system this should be, archetype as what consistency model its core state should follow — rather than a contradiction.
Plausible failure mode:
- Minor: neither label is a required output token, so a misassignment does not propagate into the verdict.
Durable solution hypothesis:
- One clarifying clause, or merge the two bullets.
Disconfirming check:
- `sed -n '8,10p;24,27p' skills/architecture-premise-audit/references/structural-antipatterns.md`.

### F049 [P3] Step 4's binary deletion-sensitivity test has no threshold for the performance category step 3 requires

Severity: P3 | Confidence: low
Candidates: S4-09-10
Source pointer: `skills/test-proof-debt-audit/SKILL.md:14`, `:15`
Evidence:
- `:14`, step 3, enumerates four observation categories including "performance".
- `:15`, step 4, asks a binary: "would it still pass if the claimed behavior disappeared?"
- Many benchmarks report a number or distribution rather than a pass/fail, so the test needs an implicit threshold neither step states.
Contract violated:
- A binary test applied to a non-binary observation category the same procedure required naming.
Plausible failure mode:
- The agent invents its own threshold, and deletion-sensitivity results for performance proofs vary across audits.
Durable solution hypothesis:
- "For performance proofs, would the recorded result remain within its accepted threshold if the claimed behavior disappeared?"
Disconfirming check:
- `sed -n '14,15p' skills/test-proof-debt-audit/SKILL.md`. If every performance proof in view is a threshold-gated CI check, the finding dissolves; the text says neither way, which is why it is P3.

### F050 [P3] The derivability question sits between the debt pattern and the disposition instruction and gates no branch

Severity: P3 | Confidence: low
Candidates: S4-09-09
Source pointer: `skills/test-proof-debt-audit/SKILL.md:21`, `:22`, `:19`, `:15`
Evidence:
- `:21-22`: "Ask whether the test could be derived from the current / contract without repository history." Both answers lead to the same next sentence.
- It adds no criterion beyond `:19`'s "history-only" definition and `:15`'s deletion sensitivity; it restates the test rather than gating a branch.
Contract violated:
- None established. Deletion sensitivity turned on the skill's own prose.
Plausible failure mode:
- None behavioral; the cost is a reader expecting a branch and finding none.
Durable solution hypothesis:
- Fold it into `:19`'s definition, or state what changes when the answer is yes versus no.
Disconfirming check:
- If removing it would leave an agent unable to catch a history-only case the enumerated list at `:19-21` misses, the sentence is load-bearing and this finding is void. Its phrasing is more general than the enumerated list, which is why confidence is low.

### F051 [P3] The description excludes ordinary implementation at selection time and the body permits modification when requested, with no text distinguishing them

Severity: P3 | Confidence: low-medium
Candidates: S4-06-09
Source pointer: `skills/test-proof-debt-audit/SKILL.md:3`, `:30`, `:31`
Evidence:
- `:3` excludes "ordinary implementation" at selection time; `:30-31` permits modification "when requested". No text distinguishes them.
Contract violated:
- A caller asking "audit this claim's proof, then fix it if it's weak" gets contradictory signals from the description and the body.
Plausible failure mode:
- Either the request is declined on the description's exclusion, or accepted and executed as an implementation task the description says the skill is not for.
Durable solution hypothesis:
- State that the exclusion is about the *request's subject* (implementing a feature) rather than about whether a fix may follow the audit.
Disconfirming check:
- `sed -n '3p;30,31p' skills/test-proof-debt-audit/SKILL.md`.

### F052 [P3] Output items 4 and 7 demand decision-grade content with no ceiling before the counterfactual becomes a redesign spec

Severity: P3 | Confidence: medium
Candidates: S4-06-06
Source pointer: `skills/architecture-premise-audit/SKILL.md:21`, `:89`, `:92`, `:94`
Evidence:
- `:21-22` forbids turning a broad audit into implementation.
- `:89`, output item 4: "counterfactual architecture and machinery removed or relocated". `:92`, item 7: "prioritized decisions and realistic fitness scenarios". `:94` urges "the best evidence-supported judgment available".
- No ceiling on detail is stated anywhere.
Contract violated:
- A prohibition on implementation alongside a mandatory output whose natural maximum is an implementable design.
Plausible failure mode:
- A thorough agent produces interfaces, schemas, or sequencing detailed enough to implement, and has satisfied both `:89`/`:92` and, arguably, violated `:21-22`. Nothing detects the crossing — the same undetectability as F025.
Durable solution hypothesis:
- Cap items 4 and 7 at narrative and decision-support level, explicitly excluding interfaces, schemas, and sequencing.
Disconfirming check:
- `sed -n '21,22p;89p;92p' skills/architecture-premise-audit/SKILL.md`.

## Candidate Reconciliation

111 candidate ids were filed across ten scout blocks (derived on-turn: an `S4-NN-MM` regex over `S4-CANDIDATES.md`, contiguous `01..N` per scout — 01→10, 02→10, 03→9, 04→8, 05→10, 06→10, 07→7, 08→7, 09→10, 10→30, no gaps). All 111 are accounted for: **100** are cited by a finding above, and the **11** below are reconciled here. Both counts were derived on this turn by the same regex over this file, truncated at this heading for the first and confined to this section for the second.

**Reconciled as scout-verified load-bearing rules — negative deletion-sensitivity results, the answer G10 asked for and the reason this round is not only a defect list (10 candidates).** Each was tested against "would an agent following the skill behave differently if this sentence were removed", and each answer was yes:

- **S4-10-03** — `architecture-premise-audit/SKILL.md:19-20`, "Complexity is a finding only when it lacks a required product need, owner, / lifecycle, consumer, scaling contract, or failure contract." The only rule preventing observed complexity from being reported as a defect. Removed, intentional justified complexity gets flagged with no principled screen, and the reference's Local-excellence and Exoneration sections are conditionally loaded and do not cover the general case. Keep — and cross-reference it from `:69-71` so "justified divergence" traces back to this gate, which would also help F007.
- **S4-10-05** — `SKILL.md:23-24`, the ask-only rule. The only constraint on mid-audit questioning; `:94-95` forbids ending the *report* with a questionnaire, not asking mid-procedure. Keep.
- **S4-10-09** — `SKILL.md:65-67`, step 6. The sole termination condition for the whole procedure. Removed, there is no stated stopping point at all. Keep — while noting F001, F002 and F003 are all about this same rule failing to do what it is the only candidate for.
- **S4-10-10** — `SKILL.md:77-81`, the five verdict tokens. The sole controlled vocabulary for `:75`'s "Lead with one verdict". Keep as canonical, and ensure no other file introduces a sixth de facto verdict — `structural-antipatterns.md:148`'s two are dispositions rather than verdicts, but F007 is the collision risk realized.
- **S4-10-11** — `SKILL.md:69-71`, the six classifications. The sole controlled per-finding disposition vocabulary; removed, `:87`'s "ranked findings" has no fixed scheme. Keep.
- **S4-10-19** — `test-proof-debt-audit/SKILL.md:15`, step 4's deletion-sensitivity question. The single discriminating test separating a real proof from a proxy — the premise of the skill's existence. Removed, steps 1-3 and 5 still run but nothing forces the proof-versus-proxy judgment the skill is named for. Keep. Step 5 is not an equivalent: it checks independence of expected values, a different axis.
- **S4-10-20** — `SKILL.md:17`, the six dispositions. The sole terminal action set; removed, `:28-29` would have nothing to report a disposition as. Keep — which is exactly why F004's omission of the disposition from `:28-29` is a P1.
- **S4-10-21** — `SKILL.md:19-24`, the history-only rule. The only passage in the 33-line body tying `replace`, `demote` and `delete` to a concrete worked scenario. Keep, and add at least one more worked example — `escalate` is the obvious candidate, which would also close F006.
- **S4-10-25** — `catalog.md:33`, "Derive malformed inputs from current authority, such as current width ± 1". The only concrete numeric worked example in the entire reference — exactly what `SKILL.md:33`'s second load branch promises to deliver. Removed, an agent loading the catalog for concrete examples finds only abstract prose. Keep; `SKILL.md:19-24` names the same categories without the ±1 mechanism and is not equivalent.
- **S4-10-27** — `catalog.md:17`, second sentence, "Search hits are leads, not findings." The only explicit guard inside the catalog against converting raw search results into reported findings. Keep, and consider moving it into `SKILL.md` so it applies even unloaded. Note the same line's *first* sentence is dead surface (F043) — one line, two opposite verdicts, which is why the finding cites the sentence and not the line.

**Reconciled as a scout-assessed benign trigger (1 candidate).**

- **S4-04-08** — `test-proof-debt-audit/SKILL.md:33`, "or when concrete replacement examples are needed". Filed by the scout only because the brief forbids suppression, and assessed by the scout itself as likely benign: self-assessed triggers are ordinary and not circular, and the agent learns from its own attempt to write `:29`'s "smallest replacement" whether it has enough of an idea, so the condition is decidable in-context at step 6. The coordinator agrees and carries no finding. Recorded rather than dropped so a later round does not re-derive it as new.

## Verification Queue

Ordered by what a receive pass should check first. Each entry is a read-only check; none applies a fix.

1. **F001** — `grep -n 'ledger' skills/architecture-premise-audit/SKILL.md` returns two lines, `:67` and `:86`, and neither is in a step that builds one. One command settles the whole finding.
2. **F002** — `sed -n '53,55p;65,67p' skills/architecture-premise-audit/SKILL.md` and count the two lists: nine against five. Then `grep -n -i 'queue\|scheduler\|deployment' skills/architecture-premise-audit/SKILL.md` to confirm the missing four appear only in step 3.
3. **F003** — the scheduled `architecture-premise-audit` run at the project boundary is this finding's own falsifier. Check its coverage ledger for non-vacuous rows and its record of how "explicitly requested" was resolved for an orchestrator-initiated invocation. **The run must execute the skill unfixed.**
4. **F004** — `sed -n '17p;28,29p' skills/test-proof-debt-audit/SKILL.md`. The disposition is chosen at `:17` and absent from `:28-29`.
5. **F006 / F009** — two greps across all four in-scope files: `grep -n -i 'escalat'` returns exactly one line; `grep -n 'checkpoint'` returns exactly one line. Both are the defect.
6. **F007** — `grep -n 'JUSTIFIED\|OPTIMIZING\|BORING\|justified divergence' skills/architecture-premise-audit/SKILL.md skills/architecture-premise-audit/references/structural-antipatterns.md` returns `:70`, `:91`, `:148` and no reconciling line.
7. **F008** — `grep -n 'slice' skills/architecture-premise-audit/SKILL.md` returns `:35`, `:44`, `:57` (case-insensitively four, adding the `:32` heading); `grep -n 'candidate'` returns `:61`, `:69`. Neither has a producing step.
8. **F005** — `sed -n '3p;39p' skills/test-proof-debt-audit/references/catalog.md` against `sed -n '8,10p;30,31p' skills/test-proof-debt-audit/SKILL.md`. Read all four lines together; the contradiction is only visible across files.
9. **F010 / F011** — `grep -n -i 'expected atlas\|expected capability map\|expected-versus-observed' skills/architecture-premise-audit/SKILL.md` returns three sites, one each, and `grep -n -i 'suspect\|misfit'` returns the load condition and the reference's title.
10. **F029 / F045** — `grep -n 'architecture-premise-audit\|test-proof-debt-audit' ` over all four in-scope files returns two `name:` lines and nothing else. Then `sed -n '3p' skills/ultra-review/SKILL.md skills/repo-refresh/SKILL.md skills/architecture-premise-audit/SKILL.md skills/test-proof-debt-audit/SKILL.md` for the selection overlap.
11. **The one partially rejected candidate** — re-check before any Phase B work builds on it: `sed -n '3p' skills/architecture-premise-audit/references/structural-antipatterns.md` against `sed -n '29,30p' skills/architecture-premise-audit/SKILL.md`. They are near-verbatim, not verbatim; S4-10-15's "verbatim" is the word rejected, and F042 carries the surviving claim.
12. **The ten load-bearing rules in Candidate Reconciliation** — a receive pass that only verifies defects will read this bundle as worse than it is. Confirm those ten before proposing any deletion in either file.
13. **Everything else** — each finding above carries its own Disconfirming check line.

## Coverage And Derivation

Every number in this report was derived on the turn it was written. The commands:

- **Scope:** `git ls-files skills/architecture-premise-audit skills/test-proof-debt-audit` -> 4 tracked files; `xargs wc -l` -> **318 lines** (`architecture-premise-audit/SKILL.md` 95, `references/structural-antipatterns.md` 151, `test-proof-debt-audit/SKILL.md` 33, `references/catalog.md` 39). Head `038dc27b50859cb30542b91683688a1f52ce5d66`, branch `main`, stash 0.
- **Findings:** 52 (4 P1 / 31 P2 / 17 P3), derived by `grep -oE '^### F[0-9]{3} \[P[123]\]' | grep -oE 'P[123]' | sort | uniq -c` over this file.
- **Candidate ids:** 111, from an `S4-NN-MM` regex over `S4-CANDIDATES.md`. Contiguous `01..N` per scout: 01→10, 02→10, 03→9, 04→8, 05→10, 06→10, 07→7, 08→7, 09→10, 10→30.
- **Reconciliation, both directions, derived on this turn.** `comm -13` (cited but never filed) -> **0**; `comm -23` (filed but never cited) -> **0**. Against the narrower set cited inside a finding body only — this file truncated at the `## Candidate Reconciliation` heading — **100** ids are cited by a finding and **11** are not; those 11 are named and dispositioned individually above.
- **Step 3 versus step 6 category counts (F002):** counted by hand against the printed source on this turn — step 3 (`:53-55`) names nine, step 6 (`:65-67`) names five, difference queues / schedulers / deployment boundaries / cited proof.
- **Single-occurrence terms, each `grep`-derived across all four in-scope files on this turn:** `escalat` -> 1 (`test-proof-debt-audit/SKILL.md:17`); `checkpoint` -> 1 (`structural-antipatterns.md:4`); `scan roots` -> 1 (`catalog.md:3`). Within `architecture-premise-audit/SKILL.md`: `ledger` -> 2 (`:67`, `:86`); `slice` -> 3 case-sensitively (`:35`, `:44`, `:57`), 4 with `-i` (adding the `:32` heading); `candidate` -> 2 (`:61`, `:69`); `completion rule` -> 1 (`:49`); `premise` -> 4 (`:2`, `:3`, `:6`, `:87`); `tax` -> 1 (`:87`); `platform` -> 1 (`:42`); `redirect` -> 2, `-i` required because both are the uppercase tokens `REDIRECT_RECOMMENDED` and `STOP_AND_REDIRECT` (`:79`, `:80`).
- **Search verbs in the reference (F034):** `grep -n -iE '\b(search|grep|trace|look for|inspect|scan|find)\b' skills/architecture-premise-audit/references/structural-antipatterns.md` -> **2** lines, `:3` (the framing sentence itself) and `:121` ("source scan", inside a pattern description). Contrast `test-proof-debt-audit/references/catalog.md`, which has a `## Search Families` header at `:5` and a literal "Search for:" at `:7`.
- **`agents/openai.yaml` presence:** stated in the brief and re-derived here — `git ls-files 'skills/*/agents/*'` shows exactly 3 of the 17 skill bundles carry one (`ultra-review`, `ultra-review-receive`, `repo-refresh`). Neither bundle in scope has one, so neither has a machine-readable contract that could contradict its prose. No finding in this report rests on one.

**Consolidation method, disclosed.** Each of the ten scout blocks was read from `S4-CANDIDATES.md` on disk during this consolidation, in bounded passes, rather than from a map held in context. Every source pointer cited in a finding was additionally read from the file it names on this turn — all four in-scope files were printed whole with `cat -n` before any finding was written, which is why only one candidate is rejected on source: at 318 lines the scouts could and did read everything, and the class of error S3a produced (pointers located by symbol rather than by line) had less room to occur.

**Pointer verification, mechanical.** Promised to the scouts in the brief, in these words: *"Every `file:line` in this round will be mechanically verified against an expected substring on that exact line before the report is called final."* A script checked an expected substring on the exact cited line of the exact cited file for every pointer in this report, including every out-of-scope pointer in F045 and F046 — five written full-path and two `repo-refresh` shorthand, seven sites across five files. Result: **138 pointers checked, 0 failures**. The table covers all 54 distinct full-path `file:line` pointers in this report plus every bare `:NN` shorthand resolved against its anchoring file; a second assertion in the same script confirms the 54 are a subset of the table. That assertion is mechanical for the 54 full-path pointers only. The bare `:NN` shorthand has no file in the string, so no regex can enumerate it: each shorthand was resolved by hand against the file its surrounding paragraph anchors it to and then added to the same expected-substring table, where it is checked mechanically like the rest. The manual step is the resolution, not the check, and it is disclosed here because it is the step that can silently omit a pointer — three APA shorthand pointers (`:32`, `:37`, `:46`) were missing from the table until a by-eye pass over the list added them. Range pointers (`:53-55`) were checked at their start line, and that rule is disclosed here rather than left implicit.

**Scout custody, disclosed.** Ten scouts, `Explore` kind, model `sonnet`, one batch. `Explore` retains `Bash`, so the scouts' read-only status is enforced by charter and by the coordinator's own tree comparison, not by the tool list. The post-batch sweep: marker `2026-09-06T13:14:47Z` (the marker file's own mtime read as UTC with `TZ=UTC stat -f '%Sm'` — the label error S3b made and corrected is not repeated here); HEAD unchanged at `038dc27b`; stash 0; `git diff --stat` empty on both target bundles; a repo-wide `-newer` sweep with `__pycache__` deliberately included, because a new `.pyc` is the only positive evidence a scout executed a script, returned **0** `.pyc` files newer than the marker. A second sweep, run after this report was written and derived on that turn — `find . -path ./.git -prune -o -newer <marker> -type f -print` — returned **4** files: `S4-BRIEF.md`, `S4-CANDIDATES.md`, this report — the only workspace artifact `skills/ultra-review/SKILL.md:52` permits the coordinator to create — and `docs/ultrareview/26-09-06-s3b-beo-scripts-round-1.md`, which this seat edited on this turn to apply the three S3b corrections named in the Prior Round Guard. All four are coordinator writes; none is a scout write. The sweep covers the repository only.

**Coverage gaps, named.** No scout executed either skill, so every claim in this report is derived from reading the prose, not from observing an agent follow it. That is the correct method for a review round and it is also the limit: F003 in particular states a behavioral prediction — that step 6 can fire vacuously against a prose target — which only the scheduled run can confirm, and the report says so. Seven pointer sites in F045 and F046 name files outside the frozen scope (`ultra-review`, `repo-refresh`, `herdr-delivery-workflow`, `prompt-leverage`, `frontend-design`); they were read read-only, are verified by the same pointer script as everything else, and are tagged in the findings that cite them. No comparison was made against skills outside this repository.

## Strongest Reason Not To Merge Yet

**`architecture-premise-audit` has exactly one termination gate, and all three of the P1s about it say it does not gate.**

F001: step 6 stops when every discovered item is "represented in the coverage ledger", and no step in the procedure builds a coverage ledger. The object the gate checks against does not exist until the agent invents it to answer the check — so the gate is passed by an artifact created to pass it.

F002: even taking the ledger as given, step 6's five categories are a strict subset of step 3's nine. Queues, schedulers, deployment boundaries and cited proof are mandatory to trace and cannot block termination. An audit can discover an unbounded queue — the reference's own leading tax — and stop with it unaddressed while satisfying the stated rule exactly.

F003: applied to a target with none of those runtime properties, the five categories may have no referents at all, and the gate fires before any work begins. That is not hypothetical for this campaign: this skill is scheduled to be pointed at this repository, a set of prose bundles, and the description selects it for that job on a literal reading.

Behind all three sits the same shape: **the procedure's only stopping rule is written in terms of an artifact nothing produces, over a category set narrower than the work, in vocabulary that may not resolve against the targets the description admits.** F008 is the same shape one step earlier — step 4 compares "slices" and step 5 filters "serious candidates", and no step produces either — so the indeterminacy step 6 inherits was already present at step 4.

The fourth P1, F004, is the same class in the sibling skill and is the cheapest to fix: `test-proof-debt-audit`'s mandatory report fields omit the disposition, so a fully compliant report never states which of the six the audit chose. The audit's own result is the one thing its output contract does not require.

That is the merge blocker, and it is worth being precise about what it is not. These are not missing features. Both skills are well-written prose with real content — ten of the eleven reconciled candidates are load-bearing rules that a deletion-sensitivity pass confirmed, and the reference contains lenses (`structural-antipatterns.md:107-112`, `:116-124`) that are genuinely sharp. The blocker is that **the one rule deciding when an audit is finished cannot decide it**, and a report emitted under that rule reads as coverage-checked whether or not any coverage occurred.

**C12 applies to the remediation, and to this campaign's own next step.** `architecture-premise-audit` is an instrument this campaign is scheduled to execute at the project boundary. The instrument and the doctrine it measures must not share an iteration: run it as written, unfixed, and let its output be the evidence for or against F003. An `architecture-premise-audit` repaired first and then run would demonstrate nothing about whether the shipped step 6 constrains an audit of this repository — which is exactly the argument S3b made about `beo_audit.py`, applied here to a skill this seat itself is about to invoke.

## Next Receive Prompt

The mandated sentence, reproduced verbatim:

> Use $ultra-review-receive to verify docs/ultrareview/26-09-06-s4-audit-skills-round-1.md and implement confirmed owner-clean fixes.

**This sentence is not an authorization.** It is the closing line the ultra-review skill mandates and generates (`create_ultra_review_report.py:102`). In this campaign `ultra-review-receive` runs in verification-only mode and applies no fix: Phase A writes files, not gates. No delivery, merge, push or deploy is authorized by this report. Whether Phase B opens — and whether any fix above is applied — is the Human's decision, taken after Phase A has ranked the confirmed findings across all slices.
