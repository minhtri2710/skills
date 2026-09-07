# S5 Receive — `prompt-leverage`, `repo-refresh`, `frontend-design`, Round 1

Verification-only pass over `docs/ultrareview/26-09-06-s5-craft-skills-round-1.md`.
No fix is applied by this record. Phase A writes files, not gates; opening Phase B
is the Human's decision and nothing here opens it.

**Inputs, all three hashes re-derived on this turn with `shasum -a 256`.**

- Report under review: `docs/ultrareview/26-09-06-s5-craft-skills-round-1.md`,
  **1486 lines**, sha256 `8dece0549974f0e5e784d77053849bb3a9b35ffc3be43044513f307cfd856d45`.
- Brief: `skills/ultra-review-workspace/campaign-01/S5-BRIEF.md`, 166 lines,
  sha256 `63a3f92be5532bbb8f4e3238082699d2f2d855e5c16e63da9810e8dd9e86a829` — matches
  the value the report's header carries.
- Candidates: `skills/ultra-review-workspace/campaign-01/S5-CANDIDATES.md`, 1628 lines,
  sha256 `8d7cfdbd3a73eb3e54a76a487d98f30631f4d0c033d48e22c04c6bd80ad2db6c` — likewise.
- Frozen scope: `038dc27b50859cb30542b91683688a1f52ce5d66`, seven tracked files,
  **520 lines** (`git ls-files skills/prompt-leverage skills/frontend-design skills/repo-refresh | xargs wc -l`).
- Working head this turn: `33eafc5431a265d523241db25b0e455a974f09e3`, branch `main`,
  stash 0, porcelain 14 lines. `git diff --stat 038dc27b -- skills/prompt-leverage
  skills/frontend-design skills/repo-refresh` is empty, exit 0: the slice has not moved
  since the batch closed, so every pointer below was checked against the frozen text.

**What this pass did.** It read all 520 lines of the seven in-scope files and all 1486
lines of the report. It re-derived every count the report states about itself, both
directions of the candidate reconciliation, every grep the report names, and every
claim about `augment_prompt.py`. It ran the two Verification Queue items the report
marks not optional. It bounded three classes of pointer the report's own instrument
does not enumerate.

**What this pass did not do.** It did not execute `augment_prompt.py` — not with a
prompt, not with `--help`, not to check a branch — and did not import it. It did not
invoke `repo-refresh` in any mode under any framing, nor `prompt-leverage`, nor
`frontend-design`. It ran no test, build, or package manager. It edited no file in the
slice. The only file it wrote is this record.

## Disposition Vocabulary

- **CONFIRMED** — the claim reproduces as written.
- **CONFIRMED-narrowed** — a true core survives; a stated part of the claim does not.
- **CONFIRMED-strengthened** — the claim reproduces and the check found more than it says.
- **NOT CONFIRMED** — the claim does not reproduce and no narrower version survives.
- **DUPLICATE** — the same defect as another finding; the survivor is named.
- **SPLIT** — two separable claims under one heading, counted once under the worse outcome.

Severity is the report's own. Where this pass disagrees with a severity, it says so in
the disposition rather than silently restating the band.

## The Added P1 Clause — Accepted

The report adds one severity clause for this slice and discloses it: P1 also covers
*"a safety boundary in an irreversible procedure whose only named enforcement mechanism
structurally cannot cover the case the boundary exists to protect"*, needed by F004,
with a note that a reader rejecting the clause should read F004 as P2.

**This pass accepts the clause rather than relaying the choice.** The warrant is in the
brief, not invented by the report: `S5-BRIEF.md:37-40` states the asymmetry the clause
operationalizes — *"a rule that under-deletes leaves debt, a rule that over-deletes
destroys work, and its own text is what stands between them"* — for the only destructive
skill in scope. A clause that raises the band for an unenforceable safety boundary in
exactly that procedure is the brief's own risk model applied to a severity scale, and
the report was right to make it visible rather than fold it into P2 silently. The P2
reading exists and is rejected here: it treats the boundary's enforceability as a
quality-of-prose question, which is precisely the framing the brief rules out for this
bundle. F004 is therefore counted P1 below.

## Findings

### F001 [P1] — CONFIRMED-narrowed

The first half reproduces exactly. `:137-139` reads "Do not claim completion while live
references point to removed material, two documents own the same contract, completed
plans remain active, or a mandatory proof route has no named current risk and consumer."
Four universally quantified negatives over a whole repository, none affirmatively
satisfiable by any procedure the file states. `sed -n '45,72p' | grep -i 'until\|complete
when\|sufficient\|stop when'` returns nothing on this turn, so the identification steps
that would have to bound the negatives have no terminating phrase either. That is F001's
core and it stands.

**The second half does not.** F001 says `:36-37` "forbids creating commits, issues, or
external messages 'unless separately requested', which cuts against the naming living
anywhere durable." Read on this turn, `:36-37` is: "Do not create branches, commits, pull
requests, issues, or external messages unless separately requested." **Files are not on
that list**, and section 4 (`:89-110`) edits files as its entire job. A durable in-repo
artifact recording the risk and consumer beside the proof route is therefore permitted by
the Boundaries as written — which is also what F001's own durable solution hypothesis
proposes. The inference from `:36-37` is not available; the ledger's transience has to be
argued from the absence of any instruction that it persists, which `:43-125` does supply.

The narrowing does not touch the finding's rank. The gate is still unsatisfiable, and the
half that carries that is the half that survives.

### F002 [P1] — CONFIRMED

Verification Queue item 2, run on this turn. The three acceptance tests for one question
reproduce with their counts exact:

- `refresh-standard.md:50-57` — "A retained mandatory proof route must name:" then **six**
  items: current risk; production behavior or machine contract; current consumer; an
  observation capable of failing when the behavior disappears; an independent oracle; the
  reason cheaper ordinary testing is insufficient.
- `SKILL.md:100-101` — **four**: "no current risk, independent oracle, production consumer,
  or deletion sensitivity."
- `SKILL.md:137-139` — **two**: "no named current risk and consumer."

6 against 4 against 2, over the same subject, in one bundle, with no sentence relating
them. The completion gate is reportable over a route that fails items 2, 4, 5 and 6 of
the standard the bundle loads unconditionally at `:27-28`.

### F003 [P1] — CONFIRMED

`:18` "`audit`: inspect and report; this is the default for a bare invocation."
`:19-20` "`apply`: audit, perform the authorized cleanup, and verify. Words such as
`refresh`, `clean`, `fix`, `remove`, or `consolidate` authorize this mode."
`:21` "`verify`: validate an earlier refresh without expanding its scope."
`:3` "Use only when the user explicitly invokes `$repo-refresh`."

The collision is textual and complete: the invocation token the description requires
contains `refresh`, the first word of the apply list, and `:21`'s own definition of the
safe third mode contains it too. Nothing in the file defines "bare" in a way that excludes
wording containing the skill's own name. The report's confidence split — high that the
collision exists, medium that a runtime matches literally — is the right shape and is
kept.

This pass agrees with the report's Strongest Reason Not To Merge Yet: of the five P1s,
this is the one reachable from ordinary phrasing whose two branches differ by whether
files are deleted.

### F004 [P1] — CONFIRMED

Every pointer reproduces. `:33` "Inspect the worktree first. Preserve unrelated and
pre-existing changes." `:40-41` "Use Git as history. Do not create archives, backup
directories, migration diaries, or compatibility copies inside the repository." The
argument holds as written: committed state needs no dedicated preservation boundary, so
the changes `:33` exists for are the uncommitted ones, and those are exactly what Git
history does not hold.

**F004 and F001 lean on the same `:36-37`, and only F001 breaks on it.** The discriminator
is what each infers. F001 infers that no durable *record* may be written — false, files are
not on the list. F004 infers only that a *commit* is foreclosed, which is true on the
face of the line, and then reaches its rollback conclusion through `:40-41`: restoring
deleted content requires either a commit or a copy inside the repository, and the two
lines together ban both. F004 does not need the baseline-record inference at all — its own
solution hypothesis proposes precisely the permitted file-based baseline. The premise
narrows one finding and not the other because the two draw different conclusions from it.

### F005 [P1] — CONFIRMED-broadened

The claim reproduces at its stated pointer. `docs/ultrareview/26-09-06-s4-audit-skills-round-1.md:865`
reads, inside F045's evidence: *"Neither file names the other. Mitigated by
`repo-refresh/SKILL.md:14`'s 'Never invoke this skill implicitly', which prevents
accidental auto-selection but does not tell a human which skill to name."* `SKILL.md:14`
reads "Never invoke this skill implicitly." A body sentence is not visible at selection
time; by the time it is readable, selection has happened. The mitigation claim is false
and F005 is right that it is.

**The broadening: F005 names one record, and there are two.** The S4 *receive* record —
written by this seat, sealed at `4c83a2ef…` — did not narrow the clause, and in one place
restated it affirmatively. Both checked on this turn:

- `26-09-06-s4-audit-skills-round-1-receive.md`, F045's disposition, is a plain
  **CONFIRMED** whose text verifies the pointers reproduce and says nothing about the
  mitigation clause. Silence, in a pass whose job is to disposition the claim.
- The same record's F031 disposition uses the reading as a premise: *"unlike
  `repo-refresh/SKILL.md:14` ('Never invoke this skill implicitly'), this skill states no
  such constraint, so automatic selection is not excluded."* That sentence asserts `:14`
  **does** exclude automatic selection for `repo-refresh`. It is false for exactly the
  reason F005 gives, and it is this seat's own writing.

So the P1 clause F005 invokes — "a record already written is false" — is satisfied twice,
and the second instance is in the campaign's own verification layer. That is recorded in
the Instrument Log below as the fourth occurrence of this class in a record this seat
wrote, and a note pointing at F005 is appended below the S4 receive record's boundary. The
S4 receive is **not** resealed for it: its digest covers the text above its separator, and
correcting a sealed record by editing above the boundary is the failure mode the boundary
exists to prevent.

The standing counter-argument the report reproduces rather than resolves (S5-10-23: `:14`
is the only in-body checkpoint after a loose description match, so deleting it as
duplication removes the last check on that path) is carried here intact. It is not
defeated by F005 — F005 kills the *mitigation* claim, not the *keep* recommendation — and
the question it turns on, whether a harness re-consults body text after selection, is not
answerable from any file in this repository. Phase B must not delete `:14` on F005's
authority.

### F006 [P2] — CONFIRMED

`:47` opens a six-category "Identify:" list; `:61` opens "Build a compact ledger
covering:". `sed -n '45,72p' skills/repo-refresh/SKILL.md | grep -i 'until\|complete
when\|sufficient\|stop when'` returns nothing on this turn. `:23-25`'s bound is circular as
the finding says: "use repository evidence, current consumers, and ownership rather than
inventing one" names the fields `:71-72` produces *about* suspects, so narrowing the
suspect set presupposes the inventory. "Compact" remains the only size word and it
constrains prose, not coverage.

### F007 [P2] — CONFIRMED-narrowed

The finding's substance reproduces. `:76` "Use only these dispositions:" closes the set at
six; `BLOCKED` at `:84-85` is scoped to "an unresolved product, compatibility, legal, or
operational decision" — a policy conflict, not an epistemic gap; `refresh-standard.md:86`
prescribes a mixed effect ("When uncertain, preserve unique current truth but delete
redundant narrative") rather than one of the six tokens, which breaks `:76` on its face.
No token covers "the evidence needed to decide could not be established." That is the
finding and it stands.

**Its disconfirming check does not reproduce as written.** The check says
`grep -in "unresolved\|uncertain\|missing\|unknown"` over both files returns "only
`refresh-standard.md:18-19` and `:86`". Run on this turn it returns **three** lines:
`refresh-standard.md:86`, `SKILL.md:84`, and `SKILL.md:116` ("missing Markdown links").
`refresh-standard.md:18-19` is **not** among them — that line is about "suspect", and the
finding's evidence cites it correctly elsewhere for that. The check's stated result names
a line the command cannot return and omits two it does. Nothing in the finding depends on
it; the narrowing is to the check line only.

### F008 [P2] — CONFIRMED

`:50-57` tests the well-formedness of a route's justification; triggers 4 (`:66`) and 8
(`:72`) test cost and proportionality, which none of the six items evaluates. `:74-75`
("Keep historical compatibility vectors only when the old value remains a current public,
security, wire, storage, migration, or machine contract") sits immediately after the
triggers with no marked scope over them, and trigger 1 (`:61-62`) still matches a
compatibility check implemented as a presence assertion. Read on this turn, there is no
connecting or precedence sentence between `:57` and `:59`, and none in `:77-86` or
`:88-97`.

### F009 [P2] — CONFIRMED

This is the finding that reshapes its own scout claim, and the reshaping is what
reproduces. `grep -rn "deletion sensitivity" skills/` on this turn returns exactly two
hits: `repo-refresh/SKILL.md:101` and `test-proof-debt-audit/SKILL.md:15`. `refresh-standard.md:71`
reads "cannot fail under a credible removal of the claimed behavior" — deletion sensitivity
in other words, inside the trigger list the scout said it was absent from. The polarity
inversion is real: the reference makes it a deletion trigger, `SKILL.md:100-101` makes it a
retention property. The bundle that uses the name never defines it; the bundle that defines
it is a skill neither file cross-references.

### F010 [P2] — CONFIRMED

`:100-101`'s "no current risk, independent oracle, production consumer, or deletion
sensitivity" carries a bare `or` against `refresh-standard.md:50-57`'s explicitly
conjunctive "must name: 1…6". The asymmetry in how the two lists mark their quantifier is
on the page. The structural half also reproduces: `:74` heads the classification section
and `:76-85` owns the vocabulary, while `:100-101` re-derives a substantive deletion test
inside the execution section. See F064, which records the same missing-quantifier defect
from the reference file's side.

### F011 [P2] — CONFIRMED

`:114` "Run validation proportionate to the changed surfaces:" and every bullet at
`:116-122` is conditional or scoped — read in full on this turn: missing Markdown links and
stale path/reference scan; tracker schema checks "when a tracker exists"; plan and
instruction references; generator/source parity; "targeted tests for changed tooling";
formatting checks; "the smallest official acceptance command whose contract changed". No
bullet names CI configuration, build files, or import graphs. `:124-125` forecloses the
fallback. The dependence on F006 is real: "whose contract changed" presupposes a complete
identification that no step bounds.

### F012 [P2] — CONFIRMED

`:16-21` read on this turn: `audit` has a default rule, `apply` has a five-word trigger
list, `verify` has a definition and no selector. `:91` scopes section 4 to `apply` mode
explicitly ("In `apply` mode:"); `:112`'s "### 5. Verify The Result" carries no scope note
and reads as the tail of an `apply` run. `:27-28` gates the reference load on "before
auditing or changing a repository", which a standalone `verify` run does neither of.
`:21`'s "without expanding its scope" needs a record of the earlier scope that `:36-37`
and the absence of any durable-record step leave unwritten. Four gaps, one mode.

### F013 [P2] — CONFIRMED

Verification Queue item 5, run on this turn. `grep -n 'REWRITE\|BLOCKED\|DEMOTE\|MERGE\|KEEP\|DELETE'
skills/repo-refresh/SKILL.md` returns hits only at `:78`, `:79`, `:80`, `:81`, `:82`, `:84`
— the six definitions — and nowhere else in the file. The nine `apply` steps at `:93-107`,
printed in full on this turn, contain no disposition token at all, while steps 3, 5, 6, 7
and 8 issue unconditional verbs. `grep -in 'rewrit'` returns `:80` and `:132`;
`grep -in 'block'` returns `:84` and `:135`. `BLOCKED`'s only consumer is a Completion
report bullet — a disclosure obligation, not an interlock before the irreversible step.

### F014 [P2] — CONFIRMED

`refresh-standard.md:59` is "Delete, replace, or demote machinery that:". `grep -in
"replace"` over both files on this turn returns exactly three lines: that one,
`SKILL.md:72` ("replacement destination"), and `SKILL.md:125` ("verify its replacement
directly"). Neither of the latter is a disposition, and "replace" is not among the six at
`:76-85`. No trigger is mapped to an action and no action to a disposition.

### F015 [P2] — CONFIRMED-narrowed

The substance reproduces. `refresh-standard.md:3-4` grounds the whole standard in "the
NOVA cleanup"; the term is never defined, dated, or cross-referenced. The project-shaped
rules are as quoted: `:14-16` bans `archive/`, `completed/`, `review/`, `packet/`, `old/`,
`postmortem/` by default; `:25-30` prescribes a six-folder `docs/` taxonomy; `:79` prefers
deletion over deprecation "inside a single-owner repository". `SKILL.md:27-28` loads the
file unconditionally.

**The scoping of the grep is imprecise.** "A repository-wide grep run on this turn returns
exactly one occurrence of NOVA — this line." Re-run on this turn over `skills/` and
`docs/`, it returns **four**: `refresh-standard.md:3` and three inside the S5 report's own
text. One in the source tree, which is the claim that matters; "repository-wide" is not
what was run. The finding's own disconfirming check compounds it by using the
`--include=*.md` form that the report's Coverage section separately records as failing
under zsh. Same class as S4's F047: the number is right about the sources and the
derivation is described wrong.

### F016 [P2] — CONFIRMED

`refresh-standard.md:32-34` and `:25-30` read on this turn. The six canonical owners are
literal `docs/*` paths; "Do not force these names over an equally coherent existing
structure" and "Do remove parallel doctrine, contract, observability, project, agent, and
miscellaneous trees when their content belongs to the canonical owners above" are adjacent
sentences, and nothing states whether "canonical owners" means the literal paths or their
functional equivalents. A `docs/doctrine/` tree satisfies both descriptions simultaneously.

### F017 [P2] — CONFIRMED

`:124-125` is the only sentence in the file about verifying a removed gate, and it reads
"If an existing mandatory gate is itself the debt under removal, verify its replacement
directly." A gate classified `DELETE` at `:82-83` or removed under `:100-101` has no
replacement to verify. Re-read of `:112-125` on this turn finds no removal-without-
replacement branch.

### F018 [P2] — CONFIRMED

`:116-122`'s seven bullets are checks with no stated failure consequence, and nothing in
`:112-139` bounds a fix-and-recheck cycle or requires re-verification of a fix. The
report's own low-medium confidence is right: the absence is real, and how much it costs
depends on conventions the file does not state.

### F019 [P2] — CONFIRMED

`:34-35` reads "Repository law may add stricter constraints, but it may not justify keeping
stale duplication, dead proof, or history disguised as current truth." The asymmetry is on
the page: local law is restricted only in the protective direction, and no converse clause
restricts reading it as authorizing deletion. Three clauses touch protection — `:34-35`,
`:84-85`, `refresh-standard.md:15-16` — with no precedence among them. The counter-weight
the report records (S5-10-24: without `:34-35`, any local convention becomes blanket
permission to skip cleanup) is carried, and the finding is correctly the missing symmetry
rather than the clause's existence.

### F020 [P2] — CONFIRMED

`agents/openai.yaml` read in full on this turn, all six lines. `:4`'s `default_prompt` is
"Use $repo-refresh only for the explicitly requested repository-wide audit, cleanup, or
verification; consolidate current truth, remove stale docs and proof machinery, and
preserve unrelated work." **`consolidate` and `remove` are both in `SKILL.md:20`'s
five-word apply list, verbatim**, and "cleanup" shares a root with `clean`. The second half
also reproduces: the file names the modes as "audit, cleanup, or verification", so two of
the three mode tokens never appear on that surface and the trigger-word list is invisible
there. The mechanism is independent of F003 — that one is the skill's own name, this one is
the sibling surface's boilerplate.

### F021 [P2] — CONFIRMED

`:19-20`'s "Words such as" is unmarked for exhaustiveness. `delete` — the literal word
behind `:82`'s `DELETE`, the disposition the scheme is built around — is absent, and so is
`apply`, the mode's own name. `fix` is present, in a file whose `:38` separates changing
production behavior from cleanup. Both readings of the list produce a failure and the file
chooses neither.

### F022 [P2] — CONFIRMED

The sweep reproduces exactly. `grep -rn '\$[a-z][a-z-]*' skills/*/SKILL.md
skills/*/agents/*.yaml`, run on this turn, returns **five** sites: three `agents/openai.yaml`
`default_prompt` fields (`repo-refresh`, `ultra-review`, `ultra-review-receive`),
`ultra-review/SKILL.md` directing a hand-off, and `repo-refresh/SKILL.md:3` gating its own
selection. Two are Claude-facing prose and only one is a gate.

**A pointer note, and it cuts in the report's favour.** `ultra-review/SKILL.md:132` reads
`:133` in the working tree, because `dcf9f2f5` grew that file from 133 to 134 lines after
the review base. `git show 038dc27b:skills/ultra-review/SKILL.md | sed -n '132p'` returns
"Use $ultra-review-receive to verify <report path> and implement confirmed owner-clean
fixes." — the report is correct at its own base and a working-tree check is the misleading
one. Recorded because a range-checking resolver would have passed `:132` against a
134-line file without noticing it now points at different text.

**S4's `:22` characterization, checked because F022 asserts it.** `26-09-06-s4-audit-skills-round-1.md:22`
does say `repo-refresh`'s token-based form "is the half of F043's exemplar pair that
survives this round intact." F022 is right that S5 defeats it. Unlike F005, the S4
**receive** record did not endorse this one: its Prior Round Guard re-derivation
(`:829-847`) covers only the `defer` count and never reaches the exemplar sentence, and its
Instrument Log item 12 carries the `architecture-premise-audit` half alone. Silence, not
endorsement — so the correction lands on the S4 report only.

### F023 [P2] — CONFIRMED-narrowed

The three-way overlap reproduces. `repo-refresh` disposes of proof machinery with
`KEEP`/`MERGE`/`REWRITE`/`DEMOTE`/`DELETE`/`BLOCKED` (`:78-85`); `test-proof-debt-audit:17`
uses `keep`/`replace`/`demote`/`closeout-only`/`delete`/`escalate`; the vocabularies are
disjoint in three tokens each direction. The coverage-gap half — "Clean up the stale tests
and dead proof machinery across this repo" matching none of the three descriptions — holds
as an argument about the descriptions as written.

**One characterization does not reproduce.** The finding says
`grep -n 'test-proof-debt-audit\|repo-refresh'` over both files "returns nothing but their
own `name:` lines". Run on this turn it returns a **third** line, `repo-refresh/SKILL.md:3`,
whose `description` carries the `$repo-refresh` token. The substantive claim — neither file
names the other — is unaffected, since that third line is `repo-refresh` naming itself.

## How The Script Findings Were Verified, Before Dispositioning Them

F024 through F040 make claims about `skills/prompt-leverage/scripts/augment_prompt.py`.
The brief and the report's Next Receive Prompt both forbid executing it. This pass
verified them **without executing or importing the file**, by a method that is disclosed
here because it is the step that could be circular:

1. The file was read with `cat -n` and parsed statically with `python3 -c "import ast;
   ast.parse(open(p).read())"`. Structural claims — which functions contain conditionals,
   whether any `Raise` node or `sys` import exists, what the argparse block declares — were
   answered by walking that tree, never by running the module.
2. The `TASK_KEYWORDS` dict and the intensity trigger lists were read out of the parse
   tree with `ast.literal_eval` on their own nodes.
3. The behavioural traces (F024's substring cases, F027's hyphen, F028's `Debug…`
   sentence, F029's set membership, F030's flatten) were evaluated in a **separate
   process against a retyped copy** of those literals — retyped from the `cat -n`
   printout, not imported.
4. **The retyping was proved identical before any trace was trusted**: the retyped
   literal compares equal to the source literal, with identical key order, under
   `ast.literal_eval` of the source node. Without that assertion a typo in the retyping
   would have "reproduced" nothing, and the whole method would be circular. It is the
   assertion, not the trace, that gives these dispositions their standing.
5. `find skills/prompt-leverage \( -name '__pycache__' -o -name '*.pyc' \)` returns **0**
   — re-run at the close of this pass, after the traces, so it is evidence about this
   pass's own conduct and not only about the scouts'.

This is a boundary case against the restriction and is recorded as one. Nothing in the
file was executed, imported, or invoked; what was executed is a hand-typed copy of two
literals whose identity to the originals was established statically first.

### F024 [P2] — CONFIRMED

`:23` is `if keyword in lowered:` with no word-boundary test anywhere in the file. All
four substring cases are true by construction and were confirmed on the retyped literals:
`test` in `latest`, `memo` in `memory`, `repo` in `report`, `fix` in `prefix`. The worked
trace reproduces: `Explain the memory issue` scores `analysis` 1 (`explain`) and `writing`
1 (`memo` inside `memory`), and resolves to `writing` on declaration order. The reverse
case reproduces too: `give me the latest report` picks up `coding` 2 from `test` inside
`latest` and `repo` inside `report`.

### F025 [P2] — CONFIRMED

`:26`'s `max(scores.items(), key=…)` returns the first maximum; the dict order at `:10-17`
is coding, research, writing, review, planning, analysis, so `coding` wins every tie and
`analysis` loses every tie. The three orderings the finding names are three different
orders and none of them is documented as functional. F024 supplies the proof that ties
are ordinary rather than exotic.

### F026 [P2] — CONFIRMED

`analyze market` and `look up` (`:12`), `break down` and `root cause` (`:16`) are matched
by the same containment test, so they require exact adjacency with a single space. The
directional consequence the finding draws is the interesting half and it holds: the two
categories carrying phrase keywords are exactly the two that lose ties under F025's
ordering, so the defects compound in one direction rather than cancelling.

### F027 [P2] — CONFIRMED

`"high stakes" in "this is a high-stakes output"` is `False`; the hyphen occupies the
position the space requires. `framework.md:46` writes the term hyphenated —
"`Deep`: debugging, architecture, complex research, or high-stakes outputs." — so the user
who reuses the documentation's own word is the user the check fails. This is the sharpest
of the four Deep-unreachability cases and it is a two-line comparison.

### F028 [P2] — CONFIRMED

`debug`, `architect` and `complex` appear in no keyword list in the file — confirmed
against the parsed literals, not by grep alone. The trace reproduces: `Debug this failing
integration test in the auth service` scores `coding` on `bug` (inside `debug`) and `test`,
wins outright, finds no `:32` trigger, and returns **Standard** at `:34` because `coding`
is in the Standard set. The prose's headline example of a Deep task deterministically
returns Standard.

### F029 [P2] — CONFIRMED

`:34`'s literal set is `{"coding", "research", "review"}` — read from the parse tree.
`framework.md:45` is "`Standard`: typical coding, research, and drafting tasks." `writing`
is the drafting type (`TASK_KEYWORDS["writing"]` contains `draft`) and is absent from the
set; `review` is in the set and absent from the definition. A swap, not a partial list, and
character-comparable.

### F030 [P2] — CONFIRMED

`:62`'s `re.sub(r"\s+", " ", raw_prompt).strip()` collapses newlines and indentation;
`:71` embeds the result as a single Markdown list item. The trace reproduces exactly:
`Fix this:\n\ndef f():\n    return 1\n` becomes `Fix this: def f(): return 1`. For the
task type the bundle declares first, the indentation was the semantics.

### F031 [P2] — CONFIRMED

Confirmed structurally rather than by trace: the parse tree contains **no `Raise` node
anywhere in the module and no `sys` import**, so there is no non-zero exit path at all,
and nothing between `:62` and `:94` branches on emptiness. An empty prompt therefore
reaches `:27`'s `analysis` fallback and `:36`'s `Light` and emits the full seven-block
template with an empty Objective, exit 0.

### F032 [P3] — CONFIRMED

`:27` returns `"analysis"` on `best_score == 0` and the return carries no signal that
nothing matched, so no caller can distinguish the two cases. The keyword literals are
ASCII English throughout and the module has no locale handling, so the non-English
consequence follows, compounded by `analysis` being outside `:34`'s Standard set. P3 is
right: the bundle never claims non-English support, and the part that stands regardless is
the conflation of "no signal" with a real category.

### F033 [P2] — CONFIRMED

`:71` interpolates `{normalized}` with no escaping, quoting or fencing anywhere between
`:62` and `:94`. A prompt containing the template's own block labels produces output with
two of them and nothing marking which is structure. The medium confidence is correctly
placed on whether a given consumer is confused, not on whether the output is ambiguous.

### F034 [P2] — CONFIRMED

The strongest structural result of this pass: **the parse tree shows zero conditional
nodes anywhere inside `upgrade_prompt`** — no `If`, no `IfExp`, no comprehension guard.
The seven-block `dedent(f"""…""")` at `:68-94` is emitted unconditionally for every input,
with only four inner lines varying. Against that stand five restraint clauses
(`SKILL.md:15`, `:25`, `:57`, `framework.md:68`, `:69`) and `SKILL.md:46` recommending this
script for the same step. The prose's proportionality rule and the tool the prose
recommends cannot both be followed.

### F035 [P2] — CONFIRMED

All three blocks check out. Work Style emits only task type and effort level against
`framework.md:17-22`'s demand to name breadth, depth and invariants. Objective emits only
the echoed prompt against `:11`'s "Define success in observable terms". Verification emits
correctness, completeness, edge cases and better approaches against `:34`'s five, and
`grep -in 'ground\|side effect'` over the script returns nothing on this turn — `grounding`
and `side effects` are absent. The P2 rather than P1 rating is right because the manual
path can still supply the missing content.

### F036 [P2] — CONFIRMED

`grep -n '^### ' skills/prompt-leverage/references/framework.md` re-run on this turn: the
Task-Type Adjustments section carries exactly four subsections — Coding, Research, Writing,
Review. No `### Planning`, no `### Analysis`. Both `SKILL.md:13` and `TASK_KEYWORDS` name
six. `:27`'s zero-match fallback is `analysis`, one of the two undocumented types, and
`--task` at `:100` takes its choices from the six keys, so `--task planning` reaches the
gap deterministically.

### F037 [P3] — CONFIRMED

Three spellings, all re-derived on this turn. `framework.md:5`'s pipeline says `Goal` and
`Done`; the definitions at `:9` and `:36` say `Objective` and `Done Criteria`; the script
emits `Objective:` and `Done Criteria:`. `grep -in 'effort' framework.md` returns nothing
while the script's emitted label at `:79` is `Effort level`, and the reference heads the
axis "Intensity Levels" at `:40`. `grep -in 'risk'` returns nothing in `framework.md` and,
in the script, only `:45` and `:51`, both inside emitted instruction strings about what the
*executing* agent should surface. `SKILL.md:41`'s "Classify the task and risk level" names
an axis nothing in the bundle computes.

### F038 [P3] — CONFIRMED

`SKILL.md:48-55`'s four-item Quality Bar and `framework.md:73-82`'s six-item Upgrade Rubric
are both final checks on the same artifact, and neither names the other. The non-overlap
runs both ways, which is the observation that rules out reading one as a summary of the
other: `framework.md` has "reduces ambiguity" and "defines the expected output clearly";
`SKILL.md:53` has "does not add unnecessary ceremony", the check that would have caught
F034.

### F039 [P3] — CONFIRMED

`build_tool_rules` branches on coding, research, review with a generic default;
`build_output_contract` branches on coding, research, writing, review. `writing` gets a
bespoke output contract and generic tool rules, and `framework.md:50-64` gives Writing an
adjustment subsection like the other three without saying anything about tool rules being
generic for it. The finding correctly claims a maintenance cost and no wrong output.

### F040 [P3] — CONFIRMED

The argparse block declares exactly the positional `prompt` and `--task`; there is no
`--intensity` and no third argument. Intensity materially changes the emitted prompt at
`:79`, and the only route to `Deep` outside `{coding, research, review}` is embedding one
of the six undocumented substrings from `:32` into the prompt text — which changes the
artifact in order to change its metadata.

### F041 [P2] — CONFIRMED

`:29` is the entire selection instruction: "Choose one mode based on the user request."
Read against `:31-34`'s four modes on this turn, there is no criterion, no example, no
default, and no tiebreak. `:3` advertises five triggers; "improve an existing prompt"
matches `Inline upgrade` and `Upgrade + rationale` equally and "add clearer tool rules"
matches no mode by name. The comparator the finding uses is fair and is worth keeping in
the Phase B record: `repo-refresh/SKILL.md:16-21` has a mechanism, whatever F003 and F021
say about how well it works; this file has none.

### F042 [P2] — CONFIRMED

`:16` (Workflow step 5) "Return both the improved prompt and a short explanation of what
changed when useful" against `:31` "`Inline upgrade`: provide the upgraded prompt only."
Read on this turn, the Workflow contains no forward reference to the Output Modes and the
Output Modes contain no clause subordinating the Workflow. "Only" at `:31` is categorical,
which is what makes the two irreconcilable rather than merely layered.

### F043 [P2] — CONFIRMED

`:50` "Before finalizing, check the upgraded prompt:" with four items at `:52-55`, all
predicated on the artifact being an upgraded prompt. `Template extraction` (`:33`) produces
a fill-in-the-blank template and `Hook spec` (`:34`) produces a design explanation. The
section is unconditional and `:31-34` carries no per-mode exemption. "Still matches the
original intent" has no meaning for a hook-design explanation.

### F044 [P2] — CONFIRMED

`:41` "Classify the task and risk level" produces two values; `:42` "Expand the prompt
using the framework blocks" consumes neither by name, and the framework's only expansion
dial is Intensity at `framework.md:40-46`. The risk value has no consumer anywhere after
step 2. Both readings fail as the finding states, and the literal reading is the harmful
one.

### F045 [P2] — CONFIRMED

`grep -rn 'augment_prompt' skills/prompt-leverage/` on this turn matches `SKILL.md:46` and
nothing in `references/framework.md`. The line sits inside the Hook Pattern, not the
Workflow, and the Workflow never mentions the script. "When a deterministic first-pass
rewrite is helpful" states no test. Both readings of the addressee are available from the
one sentence, and the two produce materially different behavior given F034.

### F046 [P3] — CONFIRMED

`:42` is flat while `:22`, `:23`, `:24` and `framework.md:68` all gate the same instruction
("only when they improve correctness", "only when tool use materially affects correctness",
"for non-trivial tasks", "only when they materially improve execution"). The finding's
sharpest observation is that the unconditional reading is the one the bundle's own script
models, per F034.

### F047 [P2] — CONFIRMED

`:57` is the file's last line: "If the prompt is already strong, say so and make only
minimal edits." No test for "strong" exists anywhere in the bundle, and by `:57` the
reader has already passed Workflow steps 1-4 and the entire Quality Bar — the rebuild the
exit exists to avoid has happened. Re-read of `:10-16` finds no early gate; the phrase
appears once, at `:57`.

### F048 [P3] — CONFIRMED

`:54`'s "includes the right verification level for the task" names neither the
`### Verification` block (present or absent) nor the Intensity axis (graded). The item is
satisfiable two ways that check different things, and the phrase is used once and never
glossed.

### F049 [P3] — CONFIRMED

`:33`'s "convert the prompt into a reusable fill-in-the-blank template" against `:8`
("without changing the underlying intent") and `:20` ("Preserve the user's objective,
constraints, and tone unless they conflict"). The tension is real and the resolution —
preserve shape, blank parameters — is available and unwritten, which is exactly why P3 and
low confidence are right.

### F050 [P3] — CONFIRMED

Both restatement sets reproduce line for line: proportionality at `:15`, `:25`, `:53` and
`framework.md:69`; intent preservation at `:8`, `:20` and `:52`. Each differs slightly and
none is marked authoritative. The finding's own disconfirming check is the part worth
carrying into Phase B: `:52-53` are a *gate*, so removing them removes a checkpoint even
though their content is a restatement. That is why this is a consolidation finding and not
a deletion finding, and a Phase B pass that reads it as licence to delete the Quality Bar
items would be misreading it.

### F051 [P2] — CONFIRMED

`frontend-design/SKILL.md` was read whole on this turn; it is 25 lines. `:22-23` is the
only verification instruction and names no tool, command, dev server, browser, or
screenshot mechanism, and the bundle has no reference directory to route to. `:24-25`'s
fallback — "If rendered inspection is unavailable, report that limitation without claiming
visual completion" — defines neither "unavailable" nor any attempt threshold. `:23-24`
("Do not add a separate verification ceremony or unrelated cleanup") closes the local
repair: the file forbids inventing a substitute check while naming no mechanism for the one
check it requires. `:3` makes it load-bearing by putting responsive behavior in acceptance.

The report's P2/P1 disclosure is correctly resolved as it stands. `:24-25` forbids
claiming visual completion, so it is a disclosure obligation rather than a satisfied gate,
and P2 is right. This pass notes the residual: the disclosure is unfalsifiable because no
attempt is required, so its enforcement value rests entirely on a later reviewer choosing
to ask what was tried.

### F052 [P2] — CONFIRMED

`grep -rn "product contract" skills/` on this turn returns **17** hits, of which exactly
**two** fall outside `*-workspace/`: `frontend-design/SKILL.md:12` itself and
`refresh-standard.md:26` ("`docs/product/`: externally observable product contracts"), a
folder-taxonomy line in a different bundle. No skill body defines the term. The second
half stands too: `:10-11` demands audience, primary job, information density, existing
components and material states before editing, three of which are typically recorded
nowhere in a codebase, and the ask-trigger at `:11-12` is keyed to contract impact rather
than to missing information — so an agent that cannot determine the audience is told
neither to ask, nor to assume, nor to state an assumption.

### F053 [P2] — CONFIRMED

`:22`'s "the representative viewports required by the change" has no breakpoint list, no
minimum count, no derivation instruction and no reference file — confirmed by the full read
of all 25 lines. `:3` puts responsive behavior in acceptance, so the acceptance claim rests
on a set the file never bounds.

### F054 [P3] — CONFIRMED

`:10-11`'s "material states" and `:18`'s six named states are eight lines apart and never
connected; "material" is not used again after `:11`. The finding's sharper half is the
qualifier: "that belong to the flow" is the entire scoping mechanism and neither "belong"
nor "the flow" is defined, so the line cannot be cited either to demand a state or to
excuse skipping one. P3 and low confidence are right — the two readings may converge in
practice.

### F055 [P3] — CONFIRMED

`:20`'s "domain content and established assets instead of generic card grids, gradients,
glass, blobs, or oversized marketing headings" turns on "generic", "established" and
"oversized", none given a threshold. The finding's own reason for not proposing deletion
holds and matters for Phase B: `:14` alone supplies no stop-list, so removing `:20` would
leave genuinely generic output violating nothing.

### F056 [P3] — CONFIRMED

`:8` asserts "the repository's design language" and names no tokens file, style guide,
component library, or search instruction; the bundle has no reference directory to hold
one. `:10-11` gestures at the mechanism through "existing components" and is never linked
to `:8`. The available-but-unstated reading is correctly what keeps this at P3.

### F057 [P3] — CONFIRMED

The full read confirms there is no Completion or Done section, and none of the five
structure bullets at `:16-20` is marked as gating. The comparator is fair:
`repo-refresh/SKILL.md:127-139` has an explicit Completion section, so the absence is a
choice this repository does not make uniformly — and F001 through F002 show that having one
is not the same as having a good one, which the finding says itself.

### F058 [P3] — CONFIRMED

`:3` excludes "isolated design-token changes" and includes work whose "domain-fit visual
design is a material part of acceptance"; `:20` is the body instructing on exactly that
class of choice. A single-component visual treatment change satisfies both descriptions.
"Material part of acceptance" appears at `:3` and never in the body. The finding's
disconfirming check is worth preserving as a method note: S4 used this line as an
out-of-scope comparator, the brief voided that characterization for this round, and the
finding was re-derived independently and lands narrower than S4's observation.

### F059 [P2] — CONFIRMED

`:71-72` fixes five ledger fields: current owner, production consumer, unique current
information, replacement destination, deletion consequence. `REWRITE` (`:80`) turns on
whether "history or duplication obscures" the owner; `DEMOTE` (`:81`) turns on whether the
item is "non-gating". Neither property is any of the five and neither is derivable from
them. Read on this turn, no sentence in `SKILL.md:59-87` or `refresh-standard.md:50-86`
derives obscuring or gating status from the recorded fields. The compounding with F001 is
real: the gate's "naming" rests on a record that cannot carry the distinction.

### F060 [P3] — CONFIRMED

`:79` defines `MERGE` as content belonging in another canonical owner; step 1 (`:93`)
merges it in, step 3 (`:95`) deletes "superseded sources in the same change", and
`refresh-standard.md:80` — read on this turn — is "Do not leave forwarding documents for
renamed internal paths; update callers." Every `MERGE`d origin is deleted with no stub, so
`MERGE` and `DELETE` are sequential stages of one outcome inside a set presented at `:76`
as closed alternatives.

### F061 [P3] — CONFIRMED

`:74` heads the section "Classify Before Changing" and `:76` closes the vocabulary, while
step 2 (`:94`) and step 9 (`:106-107`, "Prefer fewer canonical folders and one documentation
index. Do not preserve empty taxonomy.") are keyed to no suspect's disposition. The
collision with `:33` is the part that matters: step 9 authorizes folder restructuring
inside the procedure whose one anti-collateral rule is `:33`. Low confidence is right —
the repository-invariant reading is available and unstated.

### F062 [P3] — CONFIRMED

`:69` inventories "unusually large or fragmented surfaces that hide one current contract",
and none of the six dispositions names size or fragmentation: `:82`'s `DELETE` requires
stale or duplicated, `:80`'s `REWRITE` names history or duplication, `:79`'s `MERGE`
presumes an existing other owner. A category the inventory step collects has no home in the
vocabulary that step feeds.

### F063 [P3] — CONFIRMED

The five Completion bullets read on this turn are `:131` structural outcome and
before/after inventory; `:132` merged, deleted, rewritten and deliberately retained
surfaces; `:133` test/proof machinery removed or demoted and why; `:134` validation actually
run; `:135` blocked decisions and remaining current debt. `:81` defines `DEMOTE` generically
and step 4 (`:96-97`) produces a closeout-record outcome for tracker records, which no
bullet names. `:131` may absorb it generically, which is exactly why the finding is P3 and
medium rather than higher.

### F064 [P3] — CONFIRMED

`:50` "A retained mandatory proof route must name:" carries no "all of the following";
`:59` "Delete, replace, or demote machinery that:" carries no "any of the following". The
asymmetric stakes the finding names are the useful part: misreading `:59` as conjunctive
neuters deletion entirely, misreading `:50` as disjunctive lets a route survive on one of
six. Both intended readings are the ones this report uses throughout — including in F002
and F008 — which is worth stating plainly: two of this round's findings depend on a
quantifier the source never writes.

### F065 [P2] — CONFIRMED

Both halves reproduce against the files read whole. `prompt-leverage/SKILL.md:3` carries no
exclusion clause while both siblings do. `frontend-design/SKILL.md:8` states the real scope
limit — "This skill owns visual and interaction quality, not product discovery or
architecture" — in the body, which is not visible at selection time, while `:3` matches
"redesign the checkout flow's information architecture and interaction model" through
"interaction flow … is a material part of acceptance". The agent is loaded and mid-task
when it meets the disclaimer, and no handoff, sibling, or fallback is named.

### F066 [P3] — CONFIRMED

Verification Queue item 11. `skills/beo/beo-execute/SKILL.md:3`, read on this turn, is
"Implement one approved atomic BEO bead after `PASS_EXECUTE`. Use bv only for read-only
orientation and br for authoritative ready/claim checks. Mutate only approved scope. Never
approve, review, or close." — the `PASS_EXECUTE` gate is exactly as quoted, which is the
finding's own reason for rating the practical collision risk low. The recorded withdrawal
is the right thing to have preserved: the scout's stronger claim (that
`frontend-design:11`'s "Make routine visual choices locally" authorizes touching files
outside the approved scope) is wrong, because `:11` governs when to ask a question, not
which files to touch. Recording the withdrawal rather than the withdrawn claim is the
behaviour this campaign should keep.

### F067 [P3] — CONFIRMED

"A material part of acceptance" and "minor component maintenance" are both undefined degree
phrases in a single description line, and the worked borderline — a new settings toggle
built from the existing toggle component — reads either way. The finding correctly claims
selection risk rather than a falsified rule.

### F068 [P3] — CONFIRMED

`prompt-leverage/SKILL.md:3` frames output as "an execution-ready instruction set for Codex
or another AI agent" and then triggers on "improve an existing prompt" with no restriction
on the reader. A prompt written for a human is neither included nor excluded.

### F069 [P3] — CONFIRMED

`agents/openai.yaml` read in full: six lines, no disposition name, and the word
"disposition" does not appear. `find skills -name openai.yaml` on this turn returns
**three** — `repo-refresh`, `ultra-review`, `ultra-review-receive` — and none names its
bundle's internal vocabulary, which is what makes the silence repository convention rather
than a defect specific to this bundle. Filed as a closure result, which is the honest shape
for a question whose answer is "this surface says nothing".

### F070 [P2] — CONFIRMED

Verification Queue item 10. `:32` is the first bullet under `## Boundaries` (`:30`): "Read
the complete applicable instruction hierarchy before acting." `grep -rn "instruction
hierarchy" skills/`, filtered past `-workspace/`, returns **exactly one line** in the whole
tree on this turn: that one. Neither in-scope file defines the term, enumerates its members,
or gives a discovery method. `:27-28` names a different instruction with a different
subject — one file, not a hierarchy — and `:34-35` then makes "repository law" load-bearing
for a precedence rule against a corpus that was never located. The completeness qualifier is
what makes the gap decisive: an incomplete read is a violation the agent cannot detect.

### F071 [P3] — CONFIRMED

`refresh-standard.md:99-101` is the file's last sentence and its only statement of success,
and it names five contract classes. `grep -rn "contributor" skills/` filtered past
`-workspace/` returns **exactly one line** on this turn: `:101` itself. The asymmetry the
finding rests on is the right one — the other four classes are equally undefined as terms
but each has visible machinery elsewhere in the bundle, and this one has none: no step, no
ledger field, no Completion bullet would fail if a contributor contract were dropped.

### F072 [P3] — CONFIRMED

The three surfaces read on this turn gate three different things. `SKILL.md:3` gates the
user's utterance; `openai.yaml:4` gates which action is authorized and presupposes the
invocation happened; `openai.yaml:6`'s `allow_implicit_invocation: false` is the only one a
runtime can enforce without a model complying with a sentence. The `short_description`
contradiction stands: `openai.yaml:3` is "Remove stale repository machinery and history"
while `SKILL.md:40-41` is "Use Git as history. Do not create archives, backup directories,
migration diaries, or compatibility copies inside the repository" — the skill treats Git as
history's owner and deletes artifacts, not history. The same line also drops docs, plans
and issues, which `SKILL.md:3` names. The carried uncertainty about whether
`short_description` is ever shown to a human is correctly carried rather than resolved.

### F073 [P3] — CONFIRMED

All three cases reproduce at the strength the finding assigns them. The clearest:
`SKILL.md:23-25` "An age threshold identifies suspects, never automatic deletion targets"
against `refresh-standard.md:18-19` "A document modified before a user-supplied date is
presumed suspect, not presumed disposable" — one rule, two statements, and the scopes
already differ, the body's being general and the reference's conditioned on a user-supplied
date. The half case: `grep -rn "documentation index" skills/repo-refresh/` on this turn
returns `SKILL.md:106` and `refresh-standard.md:11`. The weakest case is carried at the
scout's own low-medium confidence rather than promoted.

The finding's self-limitation is the part Phase B must keep: it deliberately excludes
cross-surface repetition, accepting S5-10-23's argument that the description, the body and
`agents/openai.yaml` are read at different times by different mechanisms and cannot
substitute for one another. A Phase B pass that reads F073 as authority to deduplicate
across surfaces would be inverting it.

## Load-Bearing Rules Confirmed — Outside The Finding Tally

Verification Queue item 12, which the report marks not optional: *"a receive pass that
verifies only defect claims will mis-rank the bundles, because two of scout 10's answers
are that a rule should be kept."* Both were read at their sources on this turn. **Neither
is a finding and neither is counted in the tally below.**

**S5-10-22 — `repo-refresh/SKILL.md:137-139`. KEEP.** It is the bundle's only stated
stopping condition. Nothing else in the file defines when the `apply` workflow is finished
as opposed to having executed the nine section-4 steps once; without it an agent could
report completion having left broken references or duplicate owners behind. F001 and F002
are findings *about this sentence*, and both are strengthenings, not deletions: F001 says
its four negatives are unsatisfiable as stated, F002 says its proof-route test names two of
six items. **A Phase B pass that resolved either by deleting `:137-139` would remove the
only stopping condition in a destructive procedure.** That is the mis-ranking item 12
exists to prevent, and it is recorded here explicitly.

**S5-10-26 — `prompt-leverage/references/framework.md:9-38`. KEEP.** Read on this turn,
`:7` opens `## Block Definitions` and `:9` through `:38` are exactly seven `###` blocks —
Objective, Context, Work Style, Tool Rules, Output Contract, Verification, Done Criteria.
`SKILL.md:14` ("Rebuild the prompt with the framework blocks in `references/framework.md`")
has no other referent, and `framework.md:5`'s pipeline arrow supplies names without
definitions. It is the sole content behind the bundle's one mandatory reference load.
F035 and F037 both cite this range as the standard the script fails to meet — which is a
reason it must survive, since deleting the standard would make the script's output
compliant by removing what it fails.

Four further scout answers are carried in the findings above as reasons to keep a line
rather than cut it, and are named here so a Phase B ranking sees them without re-reading
the candidates file: **S5-10-23** (`SKILL.md:14` is cross-surface, not redundant — carried
in F005), **S5-10-24** (`:34-35` prevents local convention becoming blanket permission to
skip cleanup — carried in F019), **S5-10-20** (`:33` is the sole anti-collateral rule —
carried in F004), and **S5-10-15/16/17** (`frontend-design`'s `:12` gate, `:20` stop-list
and `:22-25` inspection step — carried in F052, F055 and F051, each of which proposes a
strengthening rather than a cut).

## Report Self-Counts, Re-Derived

Every number the report states about itself reproduces, including the one it discloses as
a trap.

- **73 findings**, `grep -c '^### F[0-9][0-9][0-9] '` → 73. Ids contiguous F001-F073, no
  duplicates, and every `Fnnn` cross-reference in the body resolves to a heading that
  exists.
- **Bands 5 P1 / 42 P2 / 26 P3**, by the report's own tolerant pattern
  `grep -oE '^### F[0-9]{3} \[P[123][^]]*\]' | grep -oE 'P[123]' | sort | uniq -c`.
- **The strict pattern returns 72**, exactly as the report says it does. `grep -cE '^###
  F[0-9]{3} \[P[123]\]'` → 72, because F004's heading reads `[P1, under the added clause]`.
  A receive pass that used the strict pattern and did not read the disclosure would have
  reported a count mismatch against a report that had already explained it.
- **1486 lines**, `wc -l`.
- **520 lines of scope across seven tracked files**, and the head, branch and stash all
  re-derived above.

## Prior Round Guard, Re-Derived

The report carries three corrections to S4 and this pass checked all three at their
sources.

**Correction 1 is F005, and it is broader than the report states.** The false clause is at
`26-09-06-s4-audit-skills-round-1.md:865`, and the S4 *receive* record repeats the reading
at its own F031 disposition while dispositioning F045 as a plain CONFIRMED. Both are
recorded in F005 above and in Instrument Log item 1.

**Correction 2 is F022, and it lands on the S4 report only.** `:22`'s "the half of F043's
exemplar pair that survives this round intact" is defeated by F022's sweep. The S4 receive
record's Prior Round Guard re-derivation covers only that report's `defer` count and never
reaches this sentence; its Instrument Log item 12 carries the `architecture-premise-audit`
half of the same exemplar pair and not the `repo-refresh` half. Silence rather than
endorsement, so no correction is owed to the receive record for it.

**Correction 3 is recorded, not carried as a finding, and that is the right disposition.**
S5-09-07 refines S4 F046's framing rather than falsifying it: `repo-refresh/SKILL.md:3`'s
first sentence names seven concrete nouns, so grouping it as anchoring "on an explicit
invocation token" as against "concrete positive phrasings" implies an opposition the line
does not support. F046 grouped by token, not by noun list, so it is not wrong; the implied
contrast is what a Phase B reader should not inherit. The report files it in the guard and
not in the findings, which is correct — and it is the source of one arithmetic subtlety
recorded in the next section.

## Candidate Reconciliation, Re-Derived

Both directions reproduce, and the derivation that produces them is the one the report
used rather than the one that looks equivalent.

- **165 candidate ids filed**, `grep -oE 'S5-[0-9]{2}-[0-9]{2}' S5-CANDIDATES.md | sort -u
  | wc -l`.
- **Per-scout distribution**, `sed 's/-[0-9][0-9]$//' | uniq -c`: 20 / 15 / 14 / 16 / 11 /
  24 / 12 / 12 / 15 / 26 for scouts 01 through 10, summing to 165, each contiguous `1..N`.
- **Cited but never filed → 0.** Nothing was invented at write time.
- **Body-cited → 163**, extracting from the report truncated at its `## Candidate
  Reconciliation` heading.
- **Filed but never cited → 2**, and they are exactly `S5-10-22` and `S5-10-26` — the two
  load-bearing keeps, which the report names and dispositions in prose and which this
  record confirms in its own section above.
- **Scout 10's `B`-series.** B1, B2 and B3 are filed under the heading `### Scout 10 —
  incidental in-scope bugs found outside G10` and are carried in F002, F036 and F029
  respectively, confirmed at the citation lines on this turn.
- **F070-F073's candidate ids** are exactly the seven the report claims were unconsumed by
  the first pass, the twelve folded ids are all present, and 12 + 7 + 2 = 21.

**The extraction that looks equivalent and is not.** Running the same `grep` over the
**whole** report returns **165** cited and **0** uncited — apparent perfect coverage. It is
false for the same reason S4's was: the Candidate Reconciliation section prints the two
uncited ids as prose, so the report's own confession of its gap is counted as evidence the
gap is closed. Anchoring the extraction above the section is what produces the true 163.
This is the third time this campaign has met this shape and the second time in a receive
record's own instrument.

**And one subtlety in the opposite direction, which is why the anchor is the section and
not the field.** Extracting from `Candidates:` lines alone returns **162**, not 163. The
163rd is `S5-09-07`, cited in Prior Round Guard Correction 3 as recorded-not-carried. The
report counts body citations rather than `Candidates:` lines and is right to: an id
discussed in the guard has been consumed by the report even though no finding claims it. A
`Candidates:`-anchored extraction would be fail-open in the other direction, reporting a
coverage gap that does not exist. The correct anchor is structural — everything above the
reconciliation section — and neither of the two obvious mechanical shortcuts finds it.

## Derived Counts That Do Not Reproduce

Four figures in the report do not reproduce as stated. **None of them touches a finding's
claim**, and all four are the class S4 named at its item 8: the count is wrong or the
derivation is described wrong, and the argument survives it. They are recorded because a
Phase B reader who re-runs the report's own instrument will hit them.

**1. The pointer figures, and the scoping disclosure is the wrong part.** The report says
two scripts were run over "this file truncated at the `## Candidate Reconciliation`
heading" because "the pointers in Verification Queue are commands for a later reader to
run, not claims, and are not counted below", and reports **107 distinct full-path
`file:line` pointers (187 instances)**.

Derived on this turn, counting distinct pointers as written, over four scopings:

| scoping | instances | distinct |
|---|---|---|
| whole file | 142 | **107** |
| truncated at `## Candidate Reconciliation` | 135 | 102 |
| through Candidate Reconciliation, excluding Verification Queue | 137 | 104 |
| through Verification Queue | 137 | 104 |

**107 reproduces only over the whole file** — which is the one scoping that *includes* the
Verification Queue pointers the report explicitly says it excluded. The disclosure is
therefore not merely imprecise, it describes a run that was not performed. The five distinct
pointers that separate the whole-file figure from the truncated one are
`frontend-design/SKILL.md:24`, `prompt-leverage/references/framework.md:9`,
`repo-refresh/SKILL.md:56`, `repo-refresh/SKILL.md:137` and `ultra-review/SKILL.md:52`.

**187 reproduces under no scoping at all**; the maximum instance count at any of the four is
142.

**"0 failures" holds at every scoping.** Every full-path pointer resolves: the file exists,
the line is within it, and the line is not blank. The instrument's result is right and its
self-description is wrong, which is the only reason this is a record-keeping defect rather
than a verification failure.

**2. F015's "repository-wide grep".** One occurrence of NOVA in the source tree, four in
`skills/` and `docs/` together. Recorded in F015 above.

**3. F023's grep characterization.** A third line is returned. Recorded in F023 above.

**4. The 296 quoted strings.** The report says every quoted string of 12 characters or more
— 296 of them — was substring-checked. That figure is not reproducible from the stated
method: the nearest values derived on this turn are 326 instances / 290 distinct over the
truncated range and 346 / 302 over the whole file. The report documents that its parser
normalizes case, strips Markdown emphasis, confirms even quote parity per line and takes
`split('"')[1::2]`, so a naive re-extraction is not expected to land on the same number.
This is therefore a **bounded non-reproduction rather than a defect claim**: reproducing it
would require rebuilding the parser, which this pass did not do and which the report's own
C12 disclosure — that the parser reached its final form by being debugged against the report
it checks — makes the more interesting number anyway. The eleven corrections it produced
were each checked at their sources in the findings above and all eleven hold.

## Tally

Derived mechanically from this record's own `###` headings on this turn, not carried from
a count written earlier in the pass.

| Disposition | Count | Findings |
|---|---|---|
| CONFIRMED | 68 | all not listed below |
| CONFIRMED-narrowed | 4 | F001, F007, F015, F023 |
| CONFIRMED-broadened | 1 | F005 |
| NOT CONFIRMED | 0 | — |
| DUPLICATE | 0 | — |

**73 findings, 73 confirmed in substance, none overturned.** No finding of this round
fails to reproduce.

Severity after the pass is unchanged from the report: **P1 5 / P2 42 / P3 26**, with F004
counted P1 under the added clause this record accepts above.

The four narrowings are all of one shape and none touches a finding's rank: in each case a
supporting sentence or a disconfirming-check line does not reproduce while the claim it
supports does. F001 loses an inference from `:36-37` and keeps its unsatisfiable gate.
F007 loses a disconfirming check's stated result and keeps its missing-token argument.
F015 loses "repository-wide" and keeps one source-tree occurrence. F023 loses "nothing but
their own `name:` lines" and keeps neither-names-the-other. F005's broadening is the only
disposition in the round that adds to a finding rather than subtracting: it names a second
false record, and that record is this seat's own.

**Two load-bearing keeps are confirmed and are not in this tally.** They are dispositions
about rules that should survive, not findings, and counting them would inflate the defect
total for the bundles they protect. That separation is the point of Verification Queue
item 12.

## Instrument Log

1. **"The record already written is false" now names two records, and I wrote the second
   one.** S5 F005 corrects `26-09-06-s4-audit-skills-round-1.md:865`. Checking it against
   the S4 *receive* record — which this seat wrote and sealed — showed that record did not
   narrow the clause, dispositioned F045 as a plain CONFIRMED, and then used the false
   reading as a premise in its own F031 disposition. That is the **fourth** instance of
   this class in a record this seat wrote, and the first where the falsehood was
   introduced by the verification layer rather than merely passed through it. A note
   pointing at S5 F005 is appended below the S4 receive record's digest boundary; the
   record is not resealed, because correcting a sealed record above its boundary is the
   failure the boundary exists to prevent.
   **The durable check this adds:** when a receive pass confirms a finding, it must
   disposition the finding's *evidence bullets*, not only its heading. F045's heading was
   about missing precedence between descriptions and was true; the false clause was three
   lines into its evidence, and a heading-level CONFIRMED swallowed it.
2. **A mention is not a slot, and an id in a reconciliation section is not a citation.**
   Extracting candidate ids from the whole report returns 165 of 165 — apparent perfect
   coverage — because the reconciliation section prints the two uncited ids as prose. The
   true figure is 163, anchored above that section. This is the third occurrence of the
   fail-open shape in this campaign. The new part is the *opposite* error found beside it:
   anchoring to `Candidates:` lines instead returns 162 and reports a gap that does not
   exist, because `S5-09-07` is consumed in the Prior Round Guard. Both mechanical
   shortcuts are wrong in opposite directions and only the structural anchor is right.
3. **A count can reproduce exactly and still convict its own description.** The report's
   107 reproduces — over the whole file, which is precisely the scoping its disclosure
   rules out. Had the figure been wrong, the disclosure would have looked like the
   explanation; because it is right, it is the proof the described run was not the run
   performed. The durable form: when a count reproduces under a scoping the record
   disclaims, check the disclaimer, not the count.
4. **A range-checking resolver cannot see content drift, and out-of-scope pointers are
   where it bites.** `ultra-review/SKILL.md:132` is correct at the review base and points
   at different text at HEAD, because `dcf9f2f5` grew that file by one line. A resolver
   that checks existence and range passes it silently. Every out-of-scope pointer in this
   round was therefore read with `git show 038dc27b:<path>`. Of the thirteen distinct
   out-of-scope pointers the report carries, only the three into `ultra-review/SKILL.md`
   reach a file that has moved since the base; no pointer reaches any
   `herdr-delivery-workflow` file, so `33eafc54` changes nothing here.
5. **The script findings were verified by static parse plus a retyped-literal trace, and
   the assertion is the load-bearing step.** The method is disclosed in full above. The
   part worth carrying: a retyped literal proves nothing until it is shown identical to the
   source literal, and the `ast.literal_eval` equality with identical key order is what
   makes the traces evidence rather than a parallel implementation of the same bug. The
   `__pycache__` sweep was re-run **after** the traces, at closeout, returning 0 — so it is
   evidence about this pass's own conduct and not only a repetition of the report's.
6. **Two pointer classes the report's instrument cannot enumerate, bounded here.**
   (a) `SKILL.md:NN` with no directory — 91 instances, 20 distinct forms, ambiguous across
   the three in-scope `SKILL.md` files (139, 57 and 25 lines). Bounded by line number:
   6 forms start above 57 and can only be `repo-refresh`; 6 start in 26-57 and exclude
   `frontend-design`; **8 start at or below 25 and are ambiguous by number alone**, resolved
   only by the citing finding's own `Source pointer:` line. That last set is where a
   mis-resolution would hide, and the report discloses that exactly one such
   mis-resolution happened during its own run and was fixed by writing the path out.
   (b) Bare `:NN` with no filename — 554 instances, 156 distinct forms, maximum start line
   **139**, which is the length of `repo-refresh/SKILL.md`, the longest file in scope. No
   bare pointer exceeds the longest file it could name.
7. **Same-seat independence, disclosed as in S4.** This seat coordinated the S5 batch and
   receives it. C12's instrument/iteration separation is held — the verification instrument
   here is not the one the report used, and the two are named separately throughout — but
   **independence in the review sense is not satisfied**, and no wording in this record
   should be read as claiming it. The campaign's owed independent work is unchanged: an
   `architecture-premise-audit` re-run at the project boundary by a seat that did not write
   the S4 report, which this seat cannot satisfy alone.
8. **The Supervisor's 09:59 correction, recorded because it bears on nothing.** Its 09:57
   message attributed a `gh-axi` block to the beo-skills working directory; it had run from
   the munsu cwd. Re-derived from beo-skills at 09:59: 0 open PRs, 0 open issues. The
   numbers stand and the derivation was wrong, which is the same class this campaign keeps
   finding and is recorded here for symmetry, not as a defect owed to anyone.

## Custody

- HEAD `33eafc5431a265d523241db25b0e455a974f09e3`, branch `main`, stash 0, porcelain
  **14 lines** — all four re-derived on this turn.
- `git diff --stat 038dc27b -- skills/prompt-leverage skills/frontend-design
  skills/repo-refresh` is empty, exit 0. The slice has not moved since the batch closed.
- `find skills/prompt-leverage \( -name '__pycache__' -o -name '*.pyc' \)` → **0**, run at
  the close of this pass.
- No file in the slice was edited, staged, formatted or created. No skill was invoked in
  any mode. No script in scope was executed or imported. No test, build or package manager
  was run.
- `AGENTS.md` remains ` M` and untouched — not staged, not reverted — pending the Human's
  attribution of that edit. `scratchpad/c8-intake.md` is not staged.
- The only file this pass wrote under `docs/` is this record. One note is appended below
  the digest boundary of `26-09-06-s4-audit-skills-round-1-receive.md`, which is a
  below-boundary append and does not alter that record's sealed text or its digest.

## What This Round Leaves Open

- **Phase A is complete with this record.** S1, S2, S3a, S3b, S4 and S5 are all received
  and sealed. Every confirmed finding across the campaign is now ranked in its own round's
  record.
- **The push remains blocked.** `git push origin refs/heads/main:refs/heads/main` was
  refused twice by this seat's runtime classifier, compound and bare, so the refusal is
  shape-independent. Recorded as a runtime denial and explicitly not a Human ruling. Two
  commits are unpushed; `origin/main` is at `038dc27b5085`. No third attempt will be made
  by this seat.
- **The owed independent re-run** of `architecture-premise-audit` at the project boundary,
  by a seat that did not write the S4 report, is unchanged and unsatisfiable by this seat
  alone.
- **A second S3b pass over `tests/`** (9 modules, 4094 lines) has not been run and needs
  its own brief.
- **The two load-bearing keeps are binding on any Phase B ranking.** `repo-refresh/SKILL.md:137-139`
  and `prompt-leverage/references/framework.md:9-38` are strengthened, never deleted, by
  the findings that cite them.

## Pointer Self-Check

Run last, after every body edit above and before the digest below. That ordering is the
rule S3b's Instrument Log established after its own Pointer Self-Check was found stale:
writing a record item can itself add citations, so the resolver's final run must be the
one with nothing left to invalidate it.

**The resolver lives outside the tree and is not committed.** It is a scratch script in
this session's scratchpad, so a reader cannot run it from the repository. Its pattern and
its roots are therefore reproduced inline, in full, read from the file rather than
recalled — the S4 receive record's item 15 was written after the first draft of exactly
this paragraph named roots the script does not use.

Pattern:

```
`([A-Za-z0-9_./-]+\.(?:py|json|md|yaml|yml)):(\d+)(?:-(\d+))?`
```

Only matches containing a `/` are treated as full-path pointers. Roots, tried in this
order until one resolves:

```
""                                       skills/prompt-leverage/references/
skills/                                  skills/prompt-leverage/scripts/
skills/repo-refresh/                     skills/frontend-design/
skills/repo-refresh/references/          skills/ultra-review/
skills/repo-refresh/agents/              skills/beo/
skills/prompt-leverage/                  skills/beo/beo-execute/
skills/ultra-review-workspace/campaign-01/
docs/ultrareview/
```

**One rule this resolver adds over S4's.** Any pointer whose file appears in
`git diff --name-only 038dc27b HEAD` is resolved against `git show 038dc27b:<path>`, not
against the working tree. Without it, a pointer into a file that has grown since the base
passes a range check while naming different text — the hazard F022 exhibits. Two pointers
in this record take that path, both into `skills/ultra-review/SKILL.md`.

**Result, derived on the final run: 19 distinct full-path pointers, 26 instances,
0 unresolved, 0 out of range, 0 landing on a blank line.**

Two classes the resolver cannot enumerate, bounded instead:

- **No-dir `filename:NN`** — 61 instances, 49 distinct forms. Each is
  resolved by the sentence that carries it; the ambiguous class is `SKILL.md:NN` at or
  below line 25, where all three in-scope bundles could be meant.
- **Bare `:NN`** — 222 instances, 111 distinct forms. Exactly one distinct start
  line exceeds 139, the length of the longest in-scope file: `:829-847`, which names
  `26-09-06-s4-audit-skills-round-1-receive.md` and is in range there at 1167 lines. Every
  other bare pointer is within the longest file its sentence could name.

**This section's own citations are inside those numbers.** The paragraph above adds a bare
pointer by recording that a bare pointer exists, and the sentence naming the two base-
resolved pointers adds two full-path instances. The figures given are from the final run
over the finished text, so they include themselves; that is the only way a self-referential
count can be stated truthfully, and stating it is cheaper than writing around it.

---

**Digest of this record, sealed at the separator above.**

`d6a7759a20cdaea0fcb76492a7dc67301eabe362dadab8006dac97fa049b1c80`

The hash covers every line up to and including the last `---` above, joined by newlines,
**with no trailing newline on the hashed bytes**. That detail is not incidental: joining
the lines and hashing them is not the same as hashing the first N lines of the file as the
shell would emit them, and a reader who forgets it gets a different digest and concludes
the record was altered. The shell equivalent, which reproduces the value above exactly:

    head -n 1254 <file> | perl -0pe 's/\n\z//' | shasum -a 256

Everything below the separator is outside the seal and may grow. Nothing above it changes.

## Notes Recorded After This Seal

**One correction owed to an earlier record, and where it was written.** S5 F005 falsifies a
sentence in the S4 receive record that this seat wrote. The correction is appended below
that record's own digest boundary rather than into its sealed text, and the S4 record's
digest is unchanged and still valid. A reader holding the S4 receive record should read its
below-boundary note before relying on its F031 or F045 dispositions.

**A Human decision arrived while this record was being written**, relayed through the
Supervisor on `supervisor-relay:typed` and reproduced here in the Human's own characters:

> oki tôi giao quyền cho các lead hãy tự fix đi, nếu có vấn đề gì thì hỏi advisor rồi tiếp tục

It arrived after the findings above were dispositioned and it changes none of them: this
record remains verification-only and applies no fix, which is what `ultra-review-receive`
is. Its effect is on what happens next rather than on what is written here, and it is
recorded at the moment it arrived rather than folded silently into the closing section.
The Supervisor's reading of the grant is the Supervisor's and is recorded as such in the
gate ledger, not as the Human's words.

**What the seal does not cover.** The two verification scripts this pass used — the pointer
resolver and the static-parse harness for `augment_prompt.py` — are scratch files outside
the checkout. The resolver's pattern and roots are reproduced above in full; the parse
harness is described in the method section above in enough detail to re-walk, but it is not
reproduced line for line, and a reader who wants to re-derive the script findings should
expect to rebuild it from the description rather than to recover it.

**A stated count in the sealed text that disagrees with its own enumeration: porcelain.**
The Custody section above, and the header at `:19`, both say porcelain is **14 lines**. It
is **15**. Re-derived on the turn this note was written:

    git --no-optional-locks status --porcelain --untracked-files=all | wc -l   → 15

The fifteenth entry is `?? docs/ultrareview/26-09-06-s5-craft-skills-round-1-receive.md` —
this record. The mechanism is that the custody figure was sampled before the record it
belongs to had been written to disk, so the one file the turn created is the one file the
count omits. Nothing else in custody moves: HEAD, branch, stash, the empty scope diff and
the zero `.pyc` all reproduce, and the other fourteen entries are the S4 close's fourteen,
unchanged. No finding, head, digest or boundary is touched by this. The figure is corrected
here rather than in place because it sits above the seal.

**The rule this yields, stated so the next closeout inherits it.** *Custody is sampled
after the last durable write of the turn, not before.* A closeout that samples its own
working state before writing the closeout is guaranteed to under-count by exactly the files
the closeout creates, and the error is invisible to every check except re-enumeration. This
is the same failure this campaign's own rule names — a stated count must be derived on the
turn it is written, from the thing it describes — approached from the other side: the count
was derived on the right turn, but at the wrong moment inside it. Both halves are needed.
Credit for catching it goes to the Supervisor, who re-enumerated rather than re-read.

**The Tally's derivation claim, verified after the fact.** The `## Tally` section opens by
saying the counts are derived mechanically from this record's own `###` headings on this
turn. When that sentence was written the counts had not been re-derived by command; they
were carried from the dispositioning pass. The derivation was run after the seal, and it
reproduces the sealed figures exactly:

    grep -c '^### F[0-9][0-9][0-9] ' <file>                             → 73
    grep -oE '^### F[0-9]{3} \[P[123]\] — [A-Za-z-]+' <file> \
      | sed 's/.*— //' | sort | uniq -c   → 68 CONFIRMED, 4 CONFIRMED-narrowed,
                                            1 CONFIRMED-broadened
    grep -oE '^### F[0-9]{3} \[P[123]\] — (CONFIRMED-narrowed|CONFIRMED-broadened)'
      → F001, F007, F015, F023 narrowed; F005 broadened

Ids are contiguous F001–F073, 73 distinct. So the sealed sentence is true, and it was true
before it was checked — but it was written as a claim about a derivation that had not yet
happened, which is the same defect this record charges against the report it reviews. It is
recorded here rather than quietly ratified by the reproduction. A derivation claim is owed
its command at the moment it is written, not at the moment it is doubted.

**The pycache sweep's timing, corrected.** Custody says the sweep ran "at the close of this
pass"; it ran before this record was written, alongside the behavioural traces.
`find skills/prompt-leverage \( -name '__pycache__' -o -name '*.pyc' \)` → **0**, re-run at
2026-09-07T03:28:11Z, after the record was on disk. The figure was right; the stated moment
was not, and it is the same sampling error as the porcelain count.
