# Ultra Review Receive: s4-audit-skills Round 1

Date: 26-09-07 (the report under review is dated 26-09-06)
Review name: s4-audit-skills
Round: 1, receive pass
Report under review: `docs/ultrareview/26-09-06-s4-audit-skills-round-1.md`
Report sha256: `0483ad84d1bfb4b9a2b33189d7b6d7aa6acf031821a07599bc98cb152669d0eb`
Report length: 1083 lines, 52 findings (P1 4 / P2 31 / P3 17)
Brief: `skills/ultra-review-workspace/campaign-01/S4-BRIEF.md`, sha256
`e2b91fd1a19ff8ded309932ab00dd0ae4bc2a4b46852f08e2ad9bc64022a01ea` — identical to
the value the report's own header records, so the report was written against this
brief and not an earlier one.
Review base: `038dc27b50859cb30542b91683688a1f52ce5d66`
Slice: `skills/architecture-premise-audit/` and `skills/test-proof-debt-audit/`,
4 tracked files, 318 lines.

All counts, file lists, greps and exit codes below were derived on the turn this
file was written, and each names the command it came from.

## Execution Restriction

`S4-BRIEF.md:74-78` binds this pass: read-only; no file edited, staged,
formatted, or created inside the slice; no tests, builds, or package managers;
and **no invocation of either skill, in any mode — not as a demonstration, not
on a small scope, not on this repository.** Static inspection only.

**Proof the restriction held.** `git diff 038dc27b -- skills/architecture-premise-audit skills/test-proof-debt-audit`
is empty and exits 0: the slice is byte-identical to the review base at the close
of this pass. That is the whole custody proof available here, and it is weaker
than the equivalent proof in the script rounds by a stated amount: prose has no
`.pyc` analog, no import side effect, and no interpreter cache, so there is no
second artifact that would record an execution the diff cannot see. What the
diff establishes is that nothing in the slice changed. What it cannot establish
on its own is that no read-only execution occurred; that rests on this record's
own account of every command run, which is reproduced in the Instrument Log.

**One thing this pass did read that looks adjacent to an invocation, and is not.**
`docs/ultrareview/26-09-06-project-architecture-premise-audit.md` is the record of
a `architecture-premise-audit` run that had already been executed, at base
`038dc27b`, before this pass opened. Reading an already-written record is not
running the skill. That run is load-bearing for F001, F002, F003, F012, F015,
F016 and F025 below, and its independence is disclosed in the Instrument Log
because it is not independent.

## Disposition Vocabulary

- **CONFIRMED** — the claim reproduces as written, at the stated severity.
- **CONFIRMED-narrowed** — a true core survives; a stated part of the claim does not.
- **CONFIRMED-broadened** — true, and true of more than the report claimed.
- **CONFIRMED-strengthened** — true, and the report's own hedge or recorded
  dissent is refuted by evidence the report did not have.
- **CONFIRMED-redirected** — the defect is real but sits at a different line,
  file, or clause than the report names.
- **DUPLICATE** — the same defect as another finding; the survivor is named.
- **NOT CONFIRMED** — the claim does not reproduce, or the finding's own stated
  falsifier fires.
- **BLOCKED-half** — one half cannot be settled by this pass; the owner is named.
- **SPLIT** — the finding contains two separable claims with different outcomes.
  Counted once, under its worst outcome, and the counting is stated in the row.
- **REVERSAL** (`RX` prefix) — this pass overturns a disposition or a claim in an
  already-closed record of this campaign.

## Dispositions

### F001 [P1] — CONFIRMED

`grep -rn 'ledger' skills/architecture-premise-audit/` run on this turn over the
**whole bundle**, not just `SKILL.md`, returns exactly two lines: `SKILL.md:67`
and `SKILL.md:86`. The reference contributes none. The report greps `SKILL.md`
only while its prose claims "no third occurrence in the bundle"; widening the
grep to the bundle is the check the report should have run, and it returns the
confirming result.

Empirically confirmed as well. The project-boundary run's own Instrument Log
states that no step constructed its ledger and that the ledger's existence was
the coordinator's choice, not the procedure's. The agent did exactly what this
finding predicted: it authored the object the gate checks against.

### F002 [P1] — CONFIRMED-strengthened

The counts reproduce: step 3 at `:53-55` traces nine, step 6 at `:65-67` gates on
five, and `grep -n -i 'queue\|scheduler\|deployment' skills/architecture-premise-audit/SKILL.md`
returns `:54` and `:55` only — one appearance each, both inside step 3.

**Strengthened on two independent grounds the report did not have.**

First, the recorded dissent (S4-02-05: the missing four may be *supporting
mechanisms* rather than coverage targets) is refuted from the text itself, not
by preferring one reading. `:17-18` makes cited proof a first-class object of
this skill — "Treat passing proof as evidence about an implementation, not proof
that the mechanism should exist" is a Boundaries rule, the highest-authority
prose in the file. A category the Boundaries single out cannot be demoted to a
mechanism found en route. The dissent's reading is unavailable for at least one
of the four, which is enough to settle the finding.

Second, the loss is no longer hypothetical. The project run's coverage ledger
carries `tests/` at row 19 under the category **cited proof**, and that row
produced finding **A6** — two shipped executables with no test, in a repository
holding 4094 lines of test. Row 19 exists only because the coordinator carried
the four orphaned categories into the ledger deliberately, against step 6 as
written. Step 6 as written would have terminated without it and A6 would not
exist.

### F003 [P1] — SPLIT, counted once under CONFIRMED-narrowed at P2

This finding named its own falsifier and scheduled it: run the skill at the
project boundary, unfixed, and look at the ledger. **The run happened.** It
splits the finding cleanly.

**Branch A — immediate vacuous termination — NOT CONFIRMED.** The prediction was a
coverage ledger of zero non-vacuous rows, or an improvised one, with the audit
terminating before work began. The ledger has 22 rows, every row traceable to a
file or a command, and rows 20 and 21 record derived absences rather than
vacancies. The finding's own text says non-vacuous rows "weaken this finding
materially". They do, and this pass records that as a disconfirmation rather
than softening it into a hedge.

**Branch B — reinterpretation licensed by nothing — CONFIRMED.** The finding's
stated alternative failure was "the agent reinterpreting 'ingress' as 'an agent
reads this skill'". Row 1 of that ledger reads `agent loads a SKILL.md |
ingress`. That is the predicted reinterpretation, verbatim, and no line of
`SKILL.md:46-95` licenses it. The consequence the finding named — two runs may
reinterpret differently and neither is wrong — stands untested but unrefuted.

**Branch C — the requester gate — CONFIRMED, as an assumption.** `:3` requires
"explicitly requested" and names no requester. The run resolved it by treating a
chain of two documents as the explicit request rather than an utterance naming
the skill, and recorded that resolution **as an assumption**. A gate that a
compliant run must resolve by assumption is not decidable from the text, which
is exactly what the finding claimed.

**Severity redirect, disclosed.** With branch A disconfirmed, the surviving
claim is that the rule cannot be executed as written — two runs may reinterpret
step 6's vocabulary differently and the text picks neither. That is the report's
**P2** clause, not the P1 clause it filed under ("satisfiable without doing its
work"). This pass files F003 at **P2**. The finding is counted once, under
CONFIRMED-narrowed, which is its worst surviving outcome.

**Independence, disclosed here and again in Custody.** The run that falsified
branch A was executed by this seat, which also coordinated the report that made
the prediction and is now writing the receive record. C12 held — the skill was
executed as written and unfixed, so the instrument and the doctrine it measures
did not share an iteration. Independence did not hold. An independent re-run is
the only thing that breaks the loop, and it is outside this pass.

### F004 [P1] — CONFIRMED

`sed -n '17p;28,29p' skills/test-proof-debt-audit/SKILL.md` reproduces exactly:
`:17` is the six-token terminal choice, `:28-29` is a flat unconditional list of
five fields, and the disposition is not among them. Nothing between `:28` and
`:33` marks a field optional or names the disposition by another spelling.

**Disclosed dependency.** This P1 rests on a severity clause the S4 report itself
added for this slice at `:46` — "a mandatory output cannot carry the result the
procedure produces". No earlier round used that clause. It is a defensible
extension for a slice of prose instructions rather than code, and the finding is
correct on its own terms; a reader who rejects the added clause should read this
as the strongest P2 in the report rather than as a P1. That choice belongs to
whoever ranks Phase B, and it is surfaced here rather than absorbed.

The second half of the finding — that `keep` and `escalate` cannot fill two of
the five mandatory fields — is independent of the added clause and reproduces
directly: a `keep` has no disconfirming scenario and no smallest replacement.

### F005 [P2] — SPLIT, counted once under CONFIRMED-narrowed

**First half — the contradiction — CONFIRMED-redirected to F024.** `SKILL.md:8-10`
is a *trigger-based* prohibition: "Do not turn ordinary implementation, a failing
test, weak coverage, or the presence of mocks into a repository-wide proof
audit." It forbids the agent widening on its own initiative from those four
triggers. `:33` explicitly contemplates "a broad user-requested audit", so a
user-initiated widening is licensed and `catalog.md:3` is not in contradiction
with `:8-10` on its face. The residue is real but it is the `:8`-versus-`:33`
scope question, and **F024 owns that root**. Filed there, once.

**Second half — the bare mutation imperative — CONFIRMED as written.**
`catalog.md:39` reads "Do not grow a proxy with more strings or patterns.
Delete, demote, or replace it." The second sentence is an imperative applied to
the artifact, in the file loaded during the broad case, to an agent whose write
access is ambient. `SKILL.md:30-31` is the only thing that stops it and lives in
a different file read at a different time. `grep -n 'scan roots' skills/test-proof-debt-audit/`
returns exactly one line, `catalog.md:3`; the term is defined nowhere.

Counted once, under CONFIRMED-narrowed.

### F006 [P2] — CONFIRMED

The four-file grep reproduces: `grep -n -i 'escalat'` across all four slice files
returns **exactly one line**, `test-proof-debt-audit/SKILL.md:17`. Every other
disposition has follow-up prose; `escalate` has the list entry and nothing else.
The recorded dissent (S4-01-10: plausibly self-explanatory, changes no artifact)
is correctly overruled — "changes no artifact" is precisely the proposition no
sentence in the file states.

### F007 [P2] — CONFIRMED

Three sites reproduce and no fourth exists: `SKILL.md:70` "justified divergence",
`SKILL.md:91` `STOP_OPTIMIZING` / `PROBABLY_JUSTIFIED`, and
`structural-antipatterns.md:148` `BORING_STANDARD` / `JUSTIFIED_DEVIATION`. No
glossary, table, or equivalence sentence. The compounding observation is the
sharper half and holds: for any audit that does not load the conditional
reference, the `:69-71` classification list contains exactly one exoneration
term and the two backticked exoneration tokens do not exist at all.

### F008 [P2] — CONFIRMED

`grep -n 'slice' skills/architecture-premise-audit/SKILL.md` returns `:35`,
`:44`, `:57`; the case-insensitive form adds `:32`, the heading. The report
states both forms, which is the correct disclosure. `grep -n -i 'candidate'`
returns `:61` and `:69`, and step 4 at `:57-60` never uses the word. Two
consecutive steps consume artifacts no predecessor produces.

Empirically supported: the project run's Instrument Log records that no step of
that run produced slices, and the run proceeded without them.

### F009 [P2] — CONFIRMED

`grep -n 'checkpoint'` across all four files returns **exactly one line**,
`structural-antipatterns.md:4`. A definite article pointing at nothing, in a
sentence that gates all reporting, in a file read before step 2 — at which
moment no artifact of the procedure exists.

### F010 [P2] — CONFIRMED

Three one-each sites reproduce. `grep -n -i 'suspect\|misfit' ` over both
`architecture-premise-audit` files returns `:26` and `:27` in `SKILL.md` and the
reference's own title line — no definition grounded in anything an agent knows
before reading the file. Both readings the finding names stay live, and the
finding is correctly located in the undecidability rather than in either reading.

Empirically supported: the project run recorded the reference as **not loaded**,
on the ground that the trigger did not fire for a prose target — one of the two
branches, taken without any textual basis for preferring it.

### F011 [P2] — CONFIRMED

`grep -n -i 'expected atlas\|expected capability map\|expected-versus-observed'`
returns exactly `:50`, `:29`, `:85` — one occurrence each, three names, no
equating sentence. The *when* of the mandatory read is undecidable, not merely
the *whether*.

### F012 [P2] — CONFIRMED

`grep -n 'completion rule' skills/architecture-premise-audit/SKILL.md` returns
exactly one line, `:49`. The artifact is never read back, and step 6 states an
independent stopping condition without referring to step 1.

Empirically confirmed: the project run's Instrument Log records the step-1
completion rule as inert — authored, then never consulted by any later step. The
recorded dissent (S4-03-04: a "declare, then verify" reading is as plausible)
is answered by the run, which had every incentive to verify and did not, because
nothing told it to.

### F013 [P2] — CONFIRMED

`grep -n -i 'return to\|repeat\|again\|iterate' skills/architecture-premise-audit/SKILL.md`
returns nothing and exits 1. No loop-back instruction exists anywhere in the
95-line file. Step 6 gates on "every discovered" item without scoping
"discovered" to a step, over a set steps 4 and 5 can grow, with no base case.

### F014 [P2] — CONFIRMED

`sed -n '67p;86p'` reproduces. The exclusion is granted by the same agent that
set the scope at `:14`, nothing forbids narrowing mid-audit, and `:86` states no
required content for an exclusion — no justification, no count, no rationale
field. The escape hatch on the only termination gate is unaudited.

Note, in the finding's favor and not against it: the project run wrote each
exclusion with a reason anyway. It did so on its own discipline, which is the
finding's point — the procedure requires nothing.

### F015 [P2] — CONFIRMED

`:69-71` gives six per-candidate classifications, `:75-81` gives five report
verdicts, and no sentence in `:46-95` composes one into the other.
"insufficient evidence" at `:71` and `INSUFFICIENT_EVIDENCE` at `:81` are the
same words in two semantic roles with no stated relationship.

Empirically confirmed: the project run's Instrument Log records that no
composition rule exists and that its verdict was chosen without one.

### F016 [P2] — CONFIRMED

`grep -n -i 'premise' skills/architecture-premise-audit/SKILL.md` returns `:2`,
`:3`, `:6`, `:87` — three title uses and one body use, undefined.
`grep -n -i 'tax'` returns `:87` only. The only taxonomy for "tax" is
`structural-antipatterns.md:64`, behind the conditional gate.

Empirically confirmed: the project run invented a hidden premise and a tax per
finding, with no taxonomy in context, exactly as predicted — its reference was
never loaded. The recorded dissent (S4-01-09: the lens names are deliberately not
closed-vocabulary labels) is correctly answered in the report: that is a reason
not to require lens names, not a reason for the field to be undefined.

### F017 [P2] — CONFIRMED

`sed -n '65,73p'` shows the unnumbered classification block at `:69-71` sitting
between step 6 and the `## Verdict And Output` header, carrying no number where
the six actions at `:48`, `:50`, `:53`, `:57`, `:61`, `:65` all carry one, and
being procedurally necessary because the Verdict section consumes its output.

### F018 [P2] — CONFIRMED

`grep -n -i 'independent truth'` returns `SKILL.md:16` and `catalog.md:24`.
Neither is a definition; `:24` uses the phrase inside an example smell. The
elaboration such as it is sits behind the `:33` gate, which does not clearly
cover the narrow single-claim case the description at `:3` advertises.

### F019 [P2] — CONFIRMED

`:22-24` offers three outcomes for one detected condition with no assignment
rule, and `catalog.md:39` repeats an undiscriminated triple for the general
proxy case. The recorded dissent (S4-10-29: `catalog.md:39`'s subset may
implicitly narrow the applicable dispositions for proxies) is live and, as the
report says, unstated — on either reading the line needs an edit, so the dissent
does not change the disposition.

### F020 [P2] — CONFIRMED

`:23-24`'s exception branch — the historical value is itself a current public
machine or security contract — identifies a live case and attaches none of the
six tokens at `:17` to it. The dependency the report notes is real: fixing F022
closes this one as a side effect.

### F021 [P2] — CONFIRMED

`grep -n 'closeout' skills/test-proof-debt-audit/SKILL.md` returns `:17`, `:23`,
`:26`. `:17` lists `demote` and `closeout-only` as co-equal; `:23` uses
closeout-only as the destination of demoting; `:26` reinforces closeout as a
tier. No line defines `closeout-only` as reachable other than via demotion.

### F022 [P2] — CONFIRMED

`grep -n 'keep' skills/test-proof-debt-audit/SKILL.md` returns `:17` only. The
disposition an audit reaches when nothing is wrong has no stated trigger
anywhere in the file, and must be inferred by elimination from `:19-31`, which
never use the word.

### F023 [P2] — CONFIRMED

The finding is already correctly narrow: it explicitly disclaims the
contradiction reading and locates the gap in the missing exit. That gap
reproduces — `catalog.md:7` opens seven families at `:9-15` with no stopping
condition, `:17` says search hits are leads without saying what closes a lead
out, and `SKILL.md:30`'s only "stop" is conditioned on the user's request mode
rather than on completion. Nothing routes a widened search's leads back into the
six-way disposition.

### F024 [P2] — CONFIRMED-broadened

Confirmed as filed, and **broadened to own the root** that F005 also raised. The
question is `SKILL.md:8` ("Audit only the claim and proof route named by the
user") against `SKILL.md:33` ("a broad user-requested audit"). Three findings in
one report take three different stances on it: F005 calls it a contradiction,
F023 says it is *not* a contradiction because `:33`'s gate reconciles it, and
F024 says the text does not disambiguate. F024's stance is the correct one and
the other two are dispositioned against it above. The report-internal
inconsistency is itself recorded in the Instrument Log.

The rest of F024 reproduces: "broad" carries no threshold, no step is named as
the evaluation point, and part of the precondition is stated only inside the
gated file at `catalog.md:3`, unreadable until the gate has already been passed.

### F025 [P2] — CONFIRMED

`grep -n -i 'read-only\|do not edit\|do not modify\|no files' skills/architecture-premise-audit/SKILL.md`
returns `:9` and nothing in the Procedure or the output sections. The boundary is
a prohibition nothing can detect being crossed, and the report format carries no
evidence either way.

Empirically confirmed in the strongest available form: the project run held
read-only, and its own record states that it did so on seat discipline. The
skill contributed no check. A run that had drifted would have produced an
identical report.

### F026 [P2] — CONFIRMED

`:21-22` forbids "a second review workflow" and the phrase is defined nowhere in
the 95-line file, while step 5 at `:61-64` requires tracing real callers, naming
the amplification route, constructing the counterfactual, giving the strongest
counterargument, and stating a falsifier — which at depth satisfies any plain
reading of the prohibition. Both readings of what the clause aims at (the
sibling skill, or recursive `ultra-review`) stay live, and the finding is
correctly located in that.

Grep note: the report writes that `grep -n -i 'second review\|review workflow'`
returns "`:21-22` only". Run today it returns a single line, `:22`, because the
phrase wraps across the two source lines. The claim is unaffected; the notation
is a range where the command returns one line. Recorded in the Instrument Log.

### F027 [P2] — CONFIRMED

`:75` plus `:77-81` reproduce; `STOP_AND_REDIRECT` is imperative in form; the
read-only clause at `:9-10` sits 68 lines away with no cross-reference from the
verdict list; and nothing states the tokens' illocutionary force. The finding is
correctly framed as a compounded rather than a standalone risk.

### F028 [P2] — CONFIRMED

`grep -n -i 'redirect' skills/architecture-premise-audit/SKILL.md` returns `:79`
and `:80` and nothing else. Two tokens implying a destination, in a closed
vocabulary, with the destination unconstrained anywhere in the file.

### F029 [P2] — CONFIRMED

The four-file grep for either skill name returns the two frontmatter `name:`
lines and nothing else: **neither in-scope file names the other skill anywhere.**
`test-proof-debt-audit/SKILL.md:29` gestures at architecture redesign and
`architecture-premise-audit/SKILL.md:17-18` and `:55` gesture at cited proof.
A prohibition that gestures at a sibling domain without naming it or describing
the handoff is not a decidable boundary.

Cross-reference: the project run's own remediation list routes its finding A6 to
`test-proof-debt-audit` — a handoff the run had to invent, because neither file
states it.

### F030 [P2] — CONFIRMED

`:3`'s only positive scope noun is "a whole project"; `:14` adds "or named
broad-system boundary"; `:26-27`'s load trigger is written for exactly the
narrower case. The description under-selects for the scope the reference exists
to serve, and `:3`'s negative clause ("one named design concern") plausibly
reads as covering that same request.

### F031 [P2] — CONFIRMED

`grep -n -i 'ordinary architecture review\|named design concern'` returns `:3`
only. Neither term has a test, example, or rule anywhere in the two files. The
finding's own conditional falsifier — that selection is always done by a human
who knows the intended distinction — cannot be established from the slice:
unlike `repo-refresh/SKILL.md:14` ("Never invoke this skill implicitly"), this
skill states no such constraint, so automatic selection is not excluded.

The report's cross-round note is correct and worth carrying forward: this is the
clause S2 F043 held up as the exemplar to copy into `ultra-review`'s
description. The exemplar has a defect, which is a fact S2's remediation needs.

### F032 [P2] — CONFIRMED

`:3`'s four-item list of proof artifacts — test, validator, benchmark, gate —
omits cited prose and metadata, which `:14` itself names as one of four
observation categories and which `catalog.md:10`, `:22` and `:23` make the
catalog's central smell. A caller whose cited proof is a README sentence has no
keyword to match.

### F033 [P2] — CONFIRMED

`:3` excludes "failing tests" and "weak coverage" outright, and both readings the
finding constructs land inside the positive clause on the same line. No text
separates "failing because the claim broke" from "failing because the proof
route is brittle".

### F034 [P2] — CONFIRMED

`grep -nE '\b(search|grep|trace|look for|inspect|scan|find)\b' skills/architecture-premise-audit/references/structural-antipatterns.md`
returns exactly two lines: `:3`, the framing sentence itself, and `:121`, where
"source scan" appears inside a pattern description. No verb of search directs the
agent anywhere. The file states a usage mode twice and operationalizes it
nowhere, while its sibling catalog at `catalog.md:5` and `:7` does exactly that.
The in-file counterexample the report names at `:107-112` is real and is the
right model for the fix.

### F035 [P2] — CONFIRMED

`SKILL.md:14`'s four observation categories and `catalog.md:37`'s six truthful
categories share no term and are never reconciled, and the adjacent
`closeout-only` / "closeout audit" collision reproduces. The answer to a
mandatory field changes with the load path.

### F036 [P3] — CONFIRMED

All five bullets at `:126-144` are game networking. `:118`'s "player-visible
outcome" reproduces as the fourth item after three fully generic terms in
Boundary and proof laundering, a section carrying no domain qualifier — the
sharper half of the finding, because that lens is valuable in every domain and a
non-game auditor may read the bullet as inapplicable.

### F037 [P3] — CONFIRMED

Step 2 at `:50-52` draws on "established domain mechanisms" and the bundle names
no source outside the conditionally-gated reference. The report's own reading —
that latent model knowledge may be the acceptable implicit default but is never
stated as such, so a thin atlas cannot be attributed — is the right frame and is
adopted.

### F038 [P3] — CONFIRMED

`grep -n -i 'platform' skills/architecture-premise-audit/SKILL.md` returns `:42`
only. A mandatory slice element whose product no step, classification, or output
item ever reads.

### F039 [P3] — CONFIRMED

The premise grep returns four lines and the report characterizes each correctly:
`:2` frontmatter, `:3` description, `:6` heading, `:87` a different concept.
Filed at P3 with low-medium confidence, which is the right weight — the report
states it is filed because the brief forbids suppression, and that is the
correct reason to file it rather than a reason to inflate it.

### F040 [P3] — CONFIRMED

`:69-71` is plain prose; `:77-81`, `:91` and `structural-antipatterns.md:148` are
all backticked. The formatting asymmetry leaves undecided whether the six
classifications are required literals or paraphrasable categories, which matters
because nothing validates report shape.

### F041 [P3] — CONFIRMED

Step 4 operates over slices (`:57`, with `:44` making slices explicitly
cross-cutting); step 6 covers five mechanism categories and never mentions
slices. The report's own rating note is correct: this is not well-posed until
F001 is fixed, which is why it is P3 and not higher.

### F042 [P3] — SPLIT, counted once under CONFIRMED-narrowed

Three of the four duplicate pairs stand: the framing pair
(`structural-antipatterns.md:3` against `SKILL.md:29-30`), the
description-restates-Boundaries pair (`:3` against `:15-16`), and the
assessment-only pair (`test-proof-debt-audit/SKILL.md:30-31`). The report's
handling of the second — keep both, because the description also does
selection-time work — is right and is why this is P3.

**The fourth pair is disconfirmed by the finding's own falsifier.** The report
asks: construct a case where an agent honors `:15-16` and `:34-35` and would
still copy the repository's decomposition at step 3. One exists. `:15-16` governs
what the agent treats as *authoritative*; `:34-35` governs how it *judges* work.
Neither governs how the observed map is *organized*, and the observed map is a
description of what exists, so organizing it by repository module is the natural
default there. `:55-56` is the only sentence that reaches step 3's artifact
directly. It is load-bearing, and its just-in-time placement is doing work rather
than repeating a rule.

Counted once, under CONFIRMED-narrowed.

### F043 [P3] — SPLIT, counted once under CONFIRMED-narrowed

**`catalog.md:17` first sentence — CONFIRMED.** "Use repository-appropriate
search and semantic tools." discriminates no behavior an agent would otherwise
choose; nothing selects repository-*inappropriate* tools deliberately. The
report's contrast note is important and correct: the *second* sentence on the
same line, "Search hits are leads, not findings.", is the catalog's only guard
against reporting raw search output as findings and must survive any edit to
this line.

**`architecture-premise-audit/SKILL.md:94` first sentence — NOT CONFIRMED, by the
finding's own stated falsifier.** The report asks for a case where an agent picks
a valid verdict token yet demonstrably fails "best judgment" in a way no other
rule catches. One exists, and it is the obvious one: an agent with sufficient
evidence emits `INSUFFICIENT_EVIDENCE` to avoid committing. That is a valid
token from the fixed list. It is not an unranked option menu and not an interview
questionnaire, so `:94-95`'s second sentence does not catch it. `:23-24` governs
when to *ask*, not which verdict to choose. Nothing else in the file forbids
hedging. "Make the best evidence-supported judgment available" is therefore the
only rule against hedging into `INSUFFICIENT_EVIDENCE`, and it is load-bearing.

Counted once, under CONFIRMED-narrowed, because a confirmed half is the worse
outcome. The `:94` half must not be actioned in Phase B: deleting that sentence
would remove the file's only anti-hedge rule.

### F044 [P3] — CONFIRMED

The pairings at `:13` ↔ `:21` and `:11` ↔ `:22-23` reproduce, and the report's
own scoping is the honest part: `:25` and `:26` have no Search Families
counterpart, so the overlap is partial and the finding applies only to the paired
subset. Filed correctly as redundancy rather than contradiction.

### F045 [P3] — CONFIRMED

Every cross-scope pointer reproduces. `sed -n '3p'` over the four named skills
returns the descriptions the report quotes; `repo-refresh/SKILL.md:14` reads
"Never invoke this skill implicitly."; `:78-85` carries the six-token
`KEEP`/`MERGE`/`REWRITE`/`DEMOTE`/`DELETE`/`BLOCKED` vocabulary, disjoint from
`test-proof-debt-audit/SKILL.md:17`'s six, over the same subject matter, with
neither file naming the other.

The finding's conditional falsifier — that a human always names the skill, so
automatic selection never arbitrates — is not establishable from the slice and is
correctly the reason for the P3 rating rather than for dismissal.

### F046 [P3] — CONFIRMED

The comparison reproduces on this turn. `repo-refresh/SKILL.md:3` anchors on the
literal token `$repo-refresh`; `herdr-delivery-workflow/SKILL.md:3` on an
explicit mention of Herdr plus `HERDR_ENV=1`; `ultra-review/SKILL.md:3`,
`prompt-leverage/SKILL.md:3` and `frontend-design/SKILL.md:3` all give concrete
positive phrasings. Both in-scope descriptions rest on abstract qualifiers with
neither a token nor an example. The report's own solution note is right that a
fixed token would be the wrong fix here.

### F047 [P3] — CONFIRMED-narrowed

The structural claim stands: nothing in `SKILL.md:46-95` requires that any named
antipattern be checked, so no individual bullet is mandatory and the file's
enforceable surface is the load condition, the usage framing, and the two
Exoneration tokens.

**Narrowed on the count.** The report says "roughly thirty named antipatterns,
taxes and domain examples across `:8-144`". `grep -c '^- ' skills/architecture-premise-audit/references/structural-antipatterns.md`
returns **40** top-level bullets on this turn. The report's number understates
by ten and is the only unverified quantity in the finding; the argument does not
depend on it, and is stronger with the correct number.

### F048 [P3] — CONFIRMED

`:8` "Wrong product category" and `:24` "Wrong archetype" sit under the same
`## Causal mechanism` header at `:6` with no distinguishing text. The report's
own note — that this is likely an under-explained two-grain distinction rather
than a contradiction, and that neither label is a required output token — is the
correct weight and is why P3 with low confidence is right.

### F049 [P3] — CONFIRMED

`:14` requires naming "performance" as one of four observation categories and
`:15` applies a binary pass/fail deletion-sensitivity test to it. The finding's
conditional falsifier (every performance proof in view is a threshold-gated CI
check) cannot be established from the slice, which the report says, and which is
why it is P3.

### F050 [P3] — NOT CONFIRMED

The finding's own falsifier fires. It asks: if removing `:21-22`'s derivability
question would leave an agent unable to catch a history-only case that `:19-21`'s
enumeration misses, the sentence is load-bearing and the finding is void.
`:19-21` enumerates a closed list — "a retired width, tag, field, version, byte
sequence, or identifier". The derivability question — "could the test be derived
from the current contract without repository history?" — is strictly more
general and catches cases outside that list: an expected value that is a digest
of a retired configuration file, an ordering that only a superseded release
produced, a fixture whose shape came from a migration that no longer runs. None
of those is a width, tag, field, version, byte sequence, or identifier. Removing
the sentence would lose them.

The report itself flagged the generality — "Its phrasing is more general than the
enumerated list, which is why confidence is low" — and filed anyway. Filing was
right; the disposition is that the check the report proposed returns the
disconfirming result.

### F051 [P3] — CONFIRMED

`:3` excludes "ordinary implementation" at selection time and `:30-31` permits
modification when requested, with no text distinguishing the request's subject
from a fix that follows an audit. A caller asking to audit a claim's proof and
then fix it if weak gets contradictory signals from the two.

### F052 [P3] — CONFIRMED

`:21-22` forbids turning a broad audit into implementation while `:89` and `:92`
mandate a counterfactual architecture and prioritized decisions with no stated
ceiling on detail. The undetectability is the same as F025's, which the report
correctly cross-references rather than filing twice.

## Tally

Assigned by hand from the 52 disposition sections above, each read in full and
assigned once, then counted mechanically from the headings of **this** record so
that the table below is not a second reading. The report's own filed counts were
enumerated with
`grep -cE '^### F[0-9]{3} \[P' docs/ultrareview/26-09-06-s4-audit-skills-round-1.md`,
which returns **52**, and the per-band counts with the same pattern per band,
which return **P1 4, P2 31, P3 17** as filed.

The disposition counts in the table were re-derived on this turn from this
record's own headings, all against
`docs/ultrareview/26-09-06-s4-audit-skills-round-1-receive.md`:
`grep -cE '^### F[0-9]{3} \[P[123]\] — ' ` returns **52**; the same pattern
anchored per disposition returns **44** for `CONFIRMED$`, **1** for
`CONFIRMED-strengthened$`, **1** for `CONFIRMED-broadened$`, **1** for
`CONFIRMED-narrowed$` and **4** for `SPLIT`, which together are the five rows
the table records as CONFIRMED-narrowed, and **1** for `NOT CONFIRMED$`. The
four SPLIT headings are the four splits named below; they are filed in the
CONFIRMED-narrowed row because that is each one's worst surviving outcome.

| disposition | count | findings |
|---|---|---|
| CONFIRMED | 44 | F001, F004, F006, F007, F008, F009, F010, F011, F012, F013, F014, F015, F016, F017, F018, F019, F020, F021, F022, F023, F025, F026, F027, F028, F029, F030, F031, F032, F033, F034, F035, F036, F037, F038, F039, F040, F041, F044, F045, F046, F048, F049, F051, F052 |
| CONFIRMED-strengthened | 1 | F002 |
| CONFIRMED-broadened | 1 | F024 |
| CONFIRMED-narrowed | 5 | F003, F005, F042, F043, F047 |
| CONFIRMED-redirected | 0 | — |
| DUPLICATE | 0 | — |
| BLOCKED-half | 0 | — |
| NOT CONFIRMED | 1 | F050 |
| REVERSAL | 0 | — |
| **total** | **52** | |

Every finding F001 through F052 has exactly one disposition section above, with
no gaps and none dispositioned twice; the table's rows sum to 52 against that
enumeration.

**Four of the five CONFIRMED-narrowed rows are SPLITs** — F003, F005, F042, F043
each contain two separable claims with different outcomes, and each is counted
once, under its worst surviving outcome, as the vocabulary requires. F047 is
narrowed on a count rather than split. The disconfirmed halves are recorded
individually because Phase B must not action them: F003's vacuous-termination
branch, F005's contradiction reading, F042's `:55-56` pair, and F043's
`SKILL.md:94` sentence.

**51 of 52 findings are confirmed in some form.** One is not confirmed.

**Severity after this pass: P1 3, P2 32, P3 17.** F003 moves from P1 to P2 for
the reason stated in its section — its surviving claim satisfies the report's P2
clause, not the P1 clause it was filed under. No other severity changes. Of the
51 confirmed, the bands are P1 3, P2 32, P3 16, since the single NOT CONFIRMED
finding is a P3.

**Zero fixes applied. Zero gates opened. Zero ledger rows written. Zero files
changed under `skills/`.** This is a Phase A receive pass; it writes a record and
nothing else.

## Ranked Confirmed Findings

Ranked for Phase B by what a fix unblocks, not by severity alone. Opening Phase
B is the Human's decision and this ranking is not a request to open it.

**Coverage.** All **51** confirmed findings appear in exactly one of the
fourteen items below. Derived on this turn, not asserted: the bolded ids of
items 1 through 13 plus the full list of item 14 were extracted and counted —
**51 ids, 51 distinct, none repeated, and the only id of the 52 not present is
F050**. F050 is deliberately absent: it is the one NOT CONFIRMED finding,
and it appears instead in the "Not to be actioned" list. Where an item names a
further id in prose — item 1 names F041 and F047, item 3 names F035 — that is a
dependency note, and each of those ids also holds its own slot in item 14. The
first version of this section listed 49, with F014 and F021 mentioned only as
such prose dependencies; that gap is recorded as Instrument Log item 15.

1. **F001 + F014** — construct the coverage ledger at step 3, and give the
   exclusion clause at `:86` a required reason field. Everything else in the
   procedure's termination story depends on the ledger existing before the gate
   checks it, and F014's escape hatch sits on that same gate: a ledger the
   auditor may silently narrow is not a termination check. F041 and F047 are not
   well-posed until F001 lands, and the project run demonstrated the failure
   rather than predicting it.
2. **F002** — reconcile step 3's nine categories with step 6's five. Cheapest
   high-value edit in the slice, and the only finding with a measured casualty:
   step 6 as written would have terminated the project run without finding A6.
3. **F004 + F021** — add the chosen disposition to `test-proof-debt-audit`'s
   mandatory report fields, make "disconfirming scenario" and "smallest
   replacement" conditional, and state how `closeout-only` is reached other than
   by demotion. One edit closes F004's two halves; F021 is the same block's
   vocabulary gap and is cheapest to close in the same pass. F035 loses most of
   its consequence once a disposition field exists.
4. **F003** — state what step 6's five categories mean when the audited system is
   not a runtime, and who counts as the requester when the caller is an
   orchestrator. Both gates were resolved by assumption in the one run that
   exists.
5. **F022 + F020 + F019** — one edit. Give `keep` a stated trigger derived from
   the two tests the skill already performs; F020's exception branch then
   resolves through it, and F019's undiscriminated triple gets its first
   discriminator.
6. **F006** — define `escalate` as a report-only label with a trigger, matching
   `architecture-premise-audit/SKILL.md:21-22`'s wording.
7. **F008 + F017** — name the step that builds slices and number the
   classification block. Two structural gaps in one numbered sequence.
8. **F007 + F015 + F040** — one canonical vocabulary for exoneration and one
   composition rule from classifications to verdict, formatted like every other
   controlled vocabulary in the bundle.
9. **F024 + F005 + F023** — settle `:8` against `:33` once, define "broad", and
   give the widened search an exit. F005's `catalog.md:39` imperative is
   rephrased as a recommendation in the same edit.
10. **F009 + F010 + F011 + F016 + F018 + F037** — the undefined-term cluster:
    "bounded checkpoint", the reference's load condition, the expected map's
    three names, "hidden premise" and "tax", "independent truth", and the source
    of "established domain mechanisms". Each is a sentence.
11. **F025 + F052** — the read-only boundary and the counterfactual's ceiling.
    Both are undetectable crossings; one output line closes the first.
12. **F029 + F045 + F028 + F026** — name the sibling in each description, which
    gives `REDIRECT_RECOMMENDED` a referent and the second-review prohibition a
    boundary.
13. **F030 + F031 + F032 + F033 + F046 + F051 + F039** — the selection-surface
    cluster. All are description edits and can land as one change.
14. **The remainder** — F012, F013, F027, F034, F035, F036, F038, F041, F042,
    F043, F044, F047, F048, F049 — real, individually small, and none blocking
    another.

**Not to be actioned**, and stated positively so a Phase B reader does not
delete them: `architecture-premise-audit/SKILL.md:55-56` (F042's fourth pair,
load-bearing at step 3), `architecture-premise-audit/SKILL.md:94` first sentence
(F043's second half, the only anti-hedge rule in the file),
`test-proof-debt-audit/SKILL.md:21-22` (F050, more general than the enumeration
it sits beside), and `catalog.md:17`'s *second* sentence (the catalog's only
guard against reporting search hits as findings — F043 targets only the first
sentence of that line).

## Load-Bearing Rules Affirmed

Four findings in this report propose deletions, and a receive pass that confirms
them without saying what must survive is half a check. These are the rules in the
slice that this pass tested for load-bearingness by constructing the case the
report's own falsifier asked for, and found load-bearing. Each is stated with the
behavior that would be lost.

1. `architecture-premise-audit/SKILL.md:55-56` — "Do not copy the repository's
   decomposition without testing it." Reaches step 3's artifact directly, which
   `:15-16` and `:34-35` do not. Lost behavior: the observed map organized by
   repository module by default.
2. `architecture-premise-audit/SKILL.md:94`, first sentence — "Make the best
   evidence-supported judgment available." Lost behavior: hedging into
   `INSUFFICIENT_EVIDENCE` with sufficient evidence, which no other clause
   forbids.
3. `test-proof-debt-audit/SKILL.md:21-22` — the derivability question. Strictly
   more general than the enumerated list at `:19-21`. Lost behavior: catching
   history-only proofs whose retired value is not a width, tag, field, version,
   byte sequence, or identifier.
4. `catalog.md:17`, second sentence — "Search hits are leads, not findings." The
   catalog's only guard against reporting raw search output. Lost behavior:
   seven search families becoming seven finding families.
5. `architecture-premise-audit/SKILL.md:17-18` — "Treat passing proof as evidence
   about an implementation, not proof that the mechanism should exist." Load-
   bearing for F002's disposition: it makes cited proof a first-class object of
   the skill, which is what defeats the recorded dissent.
6. `architecture-premise-audit/SKILL.md:19-20` — complexity is a finding only when
   it lacks a required product need, owner, lifecycle, consumer, scaling
   contract, or failure contract. The only clause in the file that stops the
   audit reporting complexity as such.
7. `architecture-premise-audit/SKILL.md:23-24` — ask only when one missing fact
   would reverse the verdict. Bounds interaction; F027 correctly treats it as
   compounding rather than as a defect in itself.
8. `architecture-premise-audit/SKILL.md:44` — "A slice may cross modules, and one
   module may contain several slices." The sentence that makes F041's two-axis
   observation true rather than pedantic.
9. `structural-antipatterns.md:3` — "search lenses, not a checklist". F042 marks
   the pair redundant and recommends the reference keep this copy; the rule
   itself is not a deletion candidate on either side of that pair.
10. `test-proof-debt-audit/SKILL.md:30-31` — assessment-only and
    modify-when-requested. F005's second half turns on this being the *only*
    thing stopping `catalog.md:39`; deleting either half of F042's fourth pair
    would remove the guard F005 depends on.

## Prior Round Guard, Re-Derived

The report's guard claim — that no prior round deferred a question to this slice
— holds, and its supporting count does not, for a reason that is time and not
error.

Derived on this turn:
`grep -c -i 'defer' docs/ultrareview/26-09-06-s{1,2,3a,3b}*.md` summed across
files returns **10**. The report states **six**. The four additional hits are
`s1-receive` (1), `s2-receive` (1) and `s3a-receive` (2) — three receive records
that did not exist when the S4 report was written, because the S4 report's own
glob matched only the four round-1 reports then present. None of the four defers
anything to S4.

The claim is therefore confirmed and the number is time-dependent. The lesson is
the one the campaign has already recorded twice: a glob over a growing directory
is not a stable derivation, and a count derived from one must name the moment it
was taken. The report named its turn, so it is not at fault; this record names
its own.

## Candidate Reconciliation, Re-Derived

All four numbers reproduce exactly.

- `grep -oE 'S4-[0-9]{2}-[0-9]{2}' skills/ultra-review-workspace/campaign-01/S4-CANDIDATES.md | sort -u | wc -l`
  → **111** distinct candidate ids.
- The same extraction restricted to the report's `Candidates:` lines
  (`grep -E '^Candidates:' <report> | grep -oE 'S4-[0-9]{2}-[0-9]{2}' | sort -u | wc -l`)
  → **100** cited in a finding.
- `comm -23` of the two → **11** uncited, and they are exactly the eleven the
  report's own Candidate Reconciliation section lists: `S4-04-08`, `S4-10-03`,
  `S4-10-05`, `S4-10-09`, `S4-10-10`, `S4-10-11`, `S4-10-19`, `S4-10-20`,
  `S4-10-21`, `S4-10-25`, `S4-10-27`.
- `comm -13` of the two → **0**. No id appears in the report that is not in the
  candidate file: nothing was invented at write time.
- Per-scout distribution, `sed 's/-[0-9][0-9]$//' | uniq -c`:
  10 / 10 / 9 / 8 / 10 / 10 / 7 / 7 / 10 / 30 for scouts 01 through 10, summing
  to 111.

One derivation trap worth naming, because it nearly produced a wrong number
here. Extracting ids from the whole report rather than from its `Candidates:`
lines returns **111**, not 100 — because the report's reconciliation section
prints the eleven uncited ids as prose. The 111/111 result looks like perfect
coverage and means the opposite of what it appears to. The correct extraction is
anchored to the field that expresses citation.

## Instrument Log

1. **The falsifier F003 scheduled had already run, and the advice this seat was
   given about it was out of date.** The guidance before this pass began was to
   file F003's behavioral half as BLOCKED-half with the scheduled run as owner.
   The run is on disk at
   `docs/ultrareview/26-09-06-project-architecture-premise-audit.md`, executed at
   base `038dc27b`, as written and unfixed. BLOCKED-half would have been a false
   record — a gate reported open that evidence had already closed. Reading the
   record before adopting the disposition is what caught it.
2. **The run confirms more than F003.** Its Instrument Log directly confirms
   F001, F002, F012, F015, F016 and F025, and its ledger row 19 supplies F002's
   only measured casualty. Six findings in this report are supported by observed
   behavior rather than by reading alone. That is unusual for a prose slice and
   is the single strongest evidence in this receive pass.
3. **Independence did not hold, and C12 is not the same property.** One seat
   coordinated the S4 report, executed the falsifying run, and wrote this receive
   record. C12 — an instrument and the doctrine it measures must not share an
   iteration — held: the skill was run unfixed, so the run measures the shipped
   text. Independence is a different property and it failed. Every disposition
   citing the run is therefore self-corroborating, and this is stated in F001,
   F002, F003 and again in Custody. An independent re-run of
   `architecture-premise-audit` at the project boundary, by a seat that did not
   write the report, is the only thing that breaks the loop. It is outside this
   pass and is recorded as owed work.
4. **A false sentence was found in the run's own record and corrected during this
   pass.** Its Instrument Log claimed the four categories step 6 omits "produced
   rows 19 through 22, including the only external-output row and the only proof
   row". Row 18 is categorized *external output*, and external output is one of
   step 6's five — so step 6 as written keeps row 18, and the claim overstated
   the loss by one category. The correction was applied above that record's
   boundary as one asserted substitution, plus a labelled correction paragraph in
   its Derivation section. The record's two mechanical counts were re-derived
   after the edit and are unchanged at **27 distinct pointers** and **25 quoted
   strings**, because the correction adds neither; its quote-character parity is
   unchanged at 64. That record carries no digest, so no seal needed reissuing.
   S4 F002 is strengthened rather than weakened by the correction: the surviving
   casualty is a finding, A6, not merely a category.
5. **This is the "a record already written is false" class, in a record this seat
   wrote.** It is the same class S3b's item 15 recorded about its own stale
   Pointer Self-Check. Twice now the false record has been the seat's own, found
   only because a later pass had reason to re-read it. The pattern is not
   carelessness at write time; it is that a claim about a table is written while
   looking at the argument rather than at the table. Both instances were caught
   by re-reading the artifact the sentence describes, and that is the check worth
   keeping: when a sentence characterizes a table, re-read the table.
6. **The report takes three positions on one question, and this pass had to pick
   an owner.** F005 calls `catalog.md:3` against `SKILL.md:8-10` a contradiction;
   F023 says explicitly it is *not* a contradiction because `:33` reconciles it;
   F024 says the text does not disambiguate. All three are in the same report,
   none cites the other two on this point. F024 is right and now owns the root;
   F005 is narrowed to its second half and F023 to the exit gap it already
   claimed. The report is not wrong to file all three — each scouts a different
   consequence — but a report that argues both sides of a question without
   noticing is a defect in the instrument, not in the slice, and it is recorded
   here rather than as a finding against the skills.
7. **Two of the report's stated falsifiers fired, and both were run rather than
   read past.** F043's `SKILL.md:94` half asked for a constructed case and one
   exists (hedging into `INSUFFICIENT_EVIDENCE`); F050's asked the same and one
   exists (a history-only proof outside the enumerated list). F042's fourth pair
   went the same way. A receive pass that confirms 51 of 52 findings is worth
   little unless the disconfirming checks were actually attempted; these three
   are the evidence that they were, and they are the reason the "Not to be
   actioned" list exists.
8. **One count in the report is wrong and the argument survives it.** F047 says
   "roughly thirty" bullets in the 151-line reference; `grep -c '^- '` returns
   **40** on this turn. The finding is about enforceability, not about size, so
   the error does not reach the conclusion — but "roughly thirty" is a derived
   quantity written without deriving it, which is the C16 fault class, and it is
   the only instance found in 1083 lines.
9. **One notation in the report is a range where the command returns one line.**
   F026 writes that `grep -n -i 'second review\|review workflow'` returns
   "`:21-22` only"; today it returns the single line `:22`, because the phrase
   wraps. Harmless, and worth recording because the same notation elsewhere in
   the campaign has meant a two-line grep result rather than a source range.
10. **The `defer` guard's count is time-dependent and its claim is not.** Ten
    hits today against six then, all four new ones in receive records written
    after the report. Recorded in full above.
11. **The candidate reconciliation has a trap that produces a false clean
    result.** Extracting ids from the whole report returns 111 of 111 — apparent
    perfect coverage — because the reconciliation section prints the uncited ids
    as prose. Anchoring the extraction to `Candidates:` lines returns the true
    100. A coverage check that counts an artifact's own confession of a gap as
    evidence the gap is closed is a fail-open check, and this is that shape.
12. **Cross-round consequence, recorded for whoever ranks Phase B.** S2 F043
    proposed copying `architecture-premise-audit/SKILL.md:3`'s negative scope
    clause into `ultra-review`'s description as an exemplar. S4 F031 finds that
    clause defective, and this pass confirms it. The exemplar should not be
    copied until F031 is fixed, or S2's remediation will propagate the defect
    into a third description. Neither report knew this about the other; the
    campaign only sees it because both rounds are now received.
13. **Widening one grep changed nothing and should have been run first.** F001's
    disconfirming check greps `SKILL.md` while its prose claims a fact about the
    bundle. Run over the bundle it returns the same two lines, so the finding is
    unaffected — but the check as written could not have detected a ledger
    construction sentence living in the reference. Checking the file the claim is
    about is not the same as checking the file the finding is about.
14. **What this pass did not do.** It did not invoke either skill, in any mode.
    It ran no test, build, or package manager. It edited no file in the slice.
    The only file written under `docs/` besides this record is the one-sentence
    correction and its accompanying paragraph in the project-audit record, which
    is disclosed in item 4 and in Custody. Every command run in this pass was a
    read: `cat`, `sed -n`, `head`, `wc`, `grep`, `git grep`, `git diff`,
    `git rev-parse`, `git status`, `git stash list`, `shasum`, `comm`, `sort`,
    `uniq`, and `python3` used only to substitute text in the two `docs/` files,
    to resolve pointers, to bound the bare `:NN` citations, and to compute this
    record's digest.
15. **Two defects were found above the boundary after this record was first
    sealed, and it was resealed.** Both were in sections Phase B consumes.
    (a) Ranked Confirmed Findings covered **49** of the 51 confirmed findings:
    F014 appeared only inside item 1's prose as a dependency of F001, and F021
    only inside item 3's prose as a consequence of F004, while item 14 claimed
    to hold "the remainder". An enumeration that stops short of its own total is
    exactly what item 8 charges the report with, and this record had the same
    fault. F014 now holds a ranked slot in item 1 and F021 in item 3, and the
    section states its own coverage arithmetic so the next reader can check it
    without re-summing. (b) The Pointer Self-Check named the resolver as
    `python3 scratchpad/ptr_s4.py`, a path that does not exist in this
    repository — the script lives in the session scratchpad outside the tree,
    and the repository's `scratchpad/` holds only `c8-intake.md`. A reader
    running the command as written gets a file-not-found. The section now says
    where the script lives, that it is not committed, and reproduces its regex
    and its thirteen root prefixes inline so the check can be rebuilt without
    it. The resolver could not catch this defect because the bad path was a
    command, not a backticked `path:line` citation — the same fail-open shape
    item 11 records, in the instrument this record trusts most.

    **This is the third instance of "the record already written is false" in
    this campaign, and the third in a record this seat wrote** — S3b item 15,
    this record's item 4 and 5, and now this. The retired digest is
    `f66abb369a2c0d774305dd48e3f4ff0aa027dc3b756cedc34c091e0571a71573`; the
    value below the boundary is the live one, and the Supervisor was sent a
    reconciliation naming both so nothing downstream builds on the retired one.
    The durable check item 5 named — *when a sentence characterizes a table,
    re-read the table* — extends here: **when a section claims to enumerate a
    total, sum it; when a record names a command, run it from where the reader
    would.**

## Pointer Self-Check

Run last, after every body edit above and before the digest below. That ordering
is the rule S3b's Instrument Log item 15 established after its own Pointer
Self-Check was found stale: writing a record item can itself add citations, so
the resolver's final run must be the one with nothing left to invalidate it.

**Full `path:line` citations.** A resolver named `ptr_s4.py`, run as
`python3 <session-scratchpad>/ptr_s4.py` from the repository root. It lives in
this session's scratchpad outside the repository and is **not** committed here —
the repository's own `scratchpad/` holds only `c8-intake.md`, so the command is
not reproducible from a clean checkout without rewriting the script. It extracts
every backticked citation whose filename ends in `.py`, `.json` or `.md`, with
the pattern

```
`([A-Za-z0-9_./-]+\.(?:py|json|md)):(\d+)(?:-(\d+))?`
```

then resolves the captured path against thirteen root prefixes, in this order,
taking the first that is an existing file: the repository root (`""`),
`skills/architecture-premise-audit/`,
`skills/architecture-premise-audit/references/`,
`skills/test-proof-debt-audit/`, `skills/test-proof-debt-audit/references/`,
`skills/`, `skills/ultra-review/`, `skills/repo-refresh/`,
`skills/herdr-delivery-workflow/`, `skills/prompt-leverage/`,
`skills/frontend-design/`, `skills/ultra-review-workspace/campaign-01/`, and
`docs/ultrareview/`. It then checks that the resolved file exists and that the
range lies inside its line count, counting distinct `(file, start, end)` triples
once and reporting instances separately:
**45/45 resolved and in range, 67 instances, 0 unresolved, 0 out of
range.**

**Bare `:NN` citations.** The record follows the report's convention of citing a
line relative to the file named in the same sentence, which no resolver can
check mechanically. Re-derived on this turn after the reseal edits, with the
pattern

```
`:(\d+)(?:-(\d+))?`
```

counted as matches rather than endpoints: **145 such matches across 69
distinct line numbers** — two more than the 143 counted before the reseal. One
is the `:86` added to ranked item 1; the other is the citation of it in this
sentence, which the pattern counts like any other. The 69 distinct values are
unchanged, because 86 was already cited elsewhere in the record. They were
bounded against the four in-scope files: the
largest line number cited is **144** and none exceeds **151**, the line count of
`skills/architecture-premise-audit/references/structural-antipatterns.md`, the
longest file in the slice. The six values above 95 — 107, 112, 118, 121, 126,
144 — were read individually and all belong to sections citing that reference
rather than the 95-line `SKILL.md`. This is a bound, not a resolution: it proves
no bare pointer is out of range for any file it could name, and does not prove
each names the file its sentence intends.

## Custody

- Review base: `038dc27b50859cb30542b91683688a1f52ce5d66`. Working HEAD at write
  time: `33eafc5431a265d523241db25b0e455a974f09e3`. Stash list: 0 entries.
- **Slice unchanged.**
  `git diff 038dc27b -- skills/architecture-premise-audit skills/test-proof-debt-audit`
  is empty and exits 0. Both bundles are byte-identical to the review base.
- `git --no-optional-locks status --porcelain --untracked-files=all` before this
  record was written: **13 lines** — ` M AGENTS.md`, eleven untracked files under
  `docs/ultrareview/`, and `?? scratchpad/c8-intake.md`. With this record it is
  **14**.
- `AGENTS.md` remains ` M` and untouched by this pass — not staged, not
  reverted — pending the Human's attribution of that edit.
- `scratchpad/c8-intake.md` is never staged. `.claude/better-harness/` is never
  committed, swept, or counted.
- One file outside this record was edited during this pass:
  `docs/ultrareview/26-09-06-project-architecture-premise-audit.md`, one asserted
  substitution correcting a false sentence in its Instrument Log plus a labelled
  correction paragraph in its Derivation section. Disclosed in Instrument Log
  item 4. Its two mechanical counts were re-derived after the edit and are
  unchanged; it carries no digest, so nothing was resealed. File length before
  535 lines, after 549.
- **Independence, disclosed.** One seat coordinated the S4 report, executed the
  `architecture-premise-audit` run that falsifies part of F003 and corroborates
  five other findings, and wrote this receive record. C12 held; independence did
  not. Every disposition citing that run is self-corroborating and is marked as
  such where it appears.
- **Owed work.** An independent re-run of `architecture-premise-audit` at the
  project boundary, by a seat that did not write the S4 report, is the only thing
  that breaks the self-corroboration loop. Also still owed from S3b: a second
  pass over `tests/` (9 modules, 4094 lines) with its own brief.
- No delivery, merge, push or deploy is authorized by this pass. Phase A writes
  files, not gates. Opening Phase B remains the Human's decision, and the
  Ranked Confirmed Findings section above is a ranking, not a request.
- Fixes applied 0. Gates opened 0. Ledger rows written 0. Files changed under
  `skills/` 0.

---

## Digest

Derived on this turn, after the last body edit and after the final resolver run.

The digest covers this record's body: every line from line 1 through the last
`---` separator inclusive, which is the boundary immediately above this section.
The boundary is located as the **last** `---` in the file, so that adding text
below it — this paragraph included — cannot change what was sealed.

**The hashed bytes carry no trailing newline.** The body is joined with newlines
between lines and nothing after the final one, which is what makes the value
reproducible from a shell:

```
head -n 1106 docs/ultrareview/26-09-06-s4-audit-skills-round-1-receive.md \
  | perl -0pe 's/\n\z//' | shasum -a 256
```

- Separator line: **1106**
- `wc -l` of the whole file: **1167**, re-derived after the two notes appended
  below the boundary; the separator line and the digest are unaffected by
  anything written below it, which is the reason the boundary is located as the
  last `---` in the file.
- Record digest: **`4c83a2efb43d8cc048dad2f81b005847122b312dcae7dd9d9580debefd255a9c`**
- Reproduced independently by the shell command above, which returns the same
  value.
- **Retired digest, superseded and not to be cited:**
  `f66abb369a2c0d774305dd48e3f4ff0aa027dc3b756cedc34c091e0571a71573`, the seal of
  the first version of this record, at separator 1017 and `wc -l` 1039. It was
  retired by the two corrections recorded as Instrument Log item 15 — the ranked
  section covering 49 of 51 confirmed findings, and the Pointer Self-Check naming
  a resolver path that does not exist in this repository. Both corrections are
  above the boundary and therefore inside this digest.

## Two notes recorded after this seal

Both belong below the boundary because both concern the sealing itself. Neither
changes any disposition, count, or digest above.

**Item 15's reconciliation sentence was written one command early.** Instrument
Log item 15 says, in the past tense, that the Supervisor was sent a
reconciliation naming the retired and the live digest. That prompt could not be
sent until the live digest existed, so at the moment of sealing the sentence was
not yet true. It became true immediately after: the prompt was accepted at pane
w2B:p1A, naming the retired value, the live value, and the shell command that
reproduces it. The gap was brief and is recorded rather than repaired by a
tense change, because the rule it brushes against — no seat reports a durable
write before the write has landed — is not made whole by rewording; a reader who
saw the sealed record between the two commands would have read a claim about a
message that had not been sent.

**The inline root list in the Pointer Self-Check was first written from memory
and was wrong.** The first draft of that correction named two reference
directories the resolver does not use and omitted three roots it does, including
the repository root itself. It was caught before sealing by reading the script
rather than recalling it, and the corrected list above is transcribed from the
script's own definition. This is the fault class Instrument Log item 5 names,
caught this time before the seal rather than after — and it is recorded here
because it was disclosed to the Supervisor in the pane, and the pane is not the
record.

## A Correction From S5, Recorded Below This Seal

S5 F005 falsifies a sentence carried in this record. The finding is stated at
`docs/ultrareview/26-09-06-s5-craft-skills-round-1.md:120-139` and dispositioned
CONFIRMED-broadened in `docs/ultrareview/26-09-06-s5-craft-skills-round-1-receive.md`.

The false claim originates in the S4 report at `docs/ultrareview/26-09-06-s4-audit-skills-round-1.md:865`,
inside F045's evidence: `repo-refresh/SKILL.md:14`'s "Never invoke this skill implicitly"
is credited with preventing accidental auto-selection. It cannot. A skill is selected on
`name` and `description` alone; the body is not visible at selection time, so by the time
`:14` is readable the selection has already happened.

**This record did not catch it, and in one place restated it.** Two places, both above the
seal and both left exactly as they were:

1. F045's disposition here is a plain **CONFIRMED**. It verified that every cross-scope
   pointer reproduces and that `:14` reads as quoted, and said nothing about the mitigation
   clause three lines further into the same evidence block.
2. F031's disposition here uses the reading as a premise: "unlike `repo-refresh/SKILL.md:14`
   ('Never invoke this skill implicitly'), this skill states no such constraint, so
   automatic selection is not excluded." That sentence asserts `:14` does exclude automatic
   selection for `repo-refresh`, which is the false claim in this record's own voice.

Nothing above the separator is edited and the digest `4c83a2ef…` is unchanged and still
valid. A reader relying on F031 or F045 should read them with this note.

**The durable lesson, which S5's Instrument Log carries in full.** A receive pass must
disposition a finding's evidence bullets, not only its heading. F045's heading — that no
description states precedence against its siblings — is true, and a heading-level CONFIRMED
swallowed a false clause inside the evidence that supports it.

**The standing counter-argument is untouched by this correction.** S5-10-23 argues `:14` is
the only in-body checkpoint at which a mis-selected agent could refuse to proceed, and is
therefore cross-surface rather than redundant. S5 F005 defeats the *mitigation* claim, not
the *keep* recommendation. `:14` is not to be deleted on the authority of either record.
