# Behavior-Preserving Port

Judge the port from the callers' side only. An **observation** is one thing a
caller of the original can tell: a value it gets back, a state it finds changed,
something written or sent, a failure it can tell apart from another failure and the
data that failure carries, the arrangement of what comes out. Every observation
holds in the target; nothing else of the original has a claim on the target.

The list of observations is the port's one working record. Each entry carries where
its expected value comes from, the check that pins it in the target, and its state:
held, kept fault, or dropped. A dropped entry names its ground: the input lies
outside the answers of step 1; it is a trait of the original's platform that cannot
exist in the target; or the user's word. Only the third needs asking, so every drop
that fits neither of the first two is put to the user.

## 1. Bound the port

Settle three questions before listing any observation, asking the user wherever the
code does not answer:

- which callers move to the target, and which stay where they are;
- whether the port replaces the original in the repository being changed, or is a
  second version for another consumer or of code that lives elsewhere;
- which inputs the system receives at all; where neither the code nor the user
  knows, every input counts as received.

Ends when the three answers are written at the head of the record.

## 2. List the observations

Start from the callers, since they decide what can be told; for callers that stay,
list here what they can tell through the crossing between the two platforms. To
find the observations no signature shows, ask each entry point five questions:

- what input does it accept, and what does it reject?
- when do two inputs or two values count as the same?
- what range do its values hold, and what happens at the ends?
- how is its output arranged where the input leaves that open?
- what does it depend on outside its arguments: clock, locale, files, settings,
  earlier calls?

Something the original does is the platform's, not an observation, when no caller
of the target would notice it gone. The way a failure is delivered is the
platform's; which failures can be told apart, and what each carries, are
observations. A platform trait a caller of the original could notice and that will
be gone is an entry in state dropped, for the report. Where you cannot tell whether
a caller relies on something, ask.

Ends when every entry point has been put the five questions and every entry has a
state.

## 3. Source each expected value

Give each entry its expected value and name the source: a check of the original
(each assertion and each table case is a unit; a test's name is not), a run of the
original, or, where the original cannot be run, a reading of the code, a
specification, or the user's word, marked as such.

Ends when every entry has a source; count the entries resting on reading for the
report.

## 4. Signatures, checks, body

In this order. Design the target's signatures from the entries, so that checks can
be written against them. Write one check per entry (a row of a table counts), all
before the body: the behaviour is observed, not imagined, so the checks cannot lock
in a guess. Then write the body until the checks pass.

- Nothing enters the target that neither an entry nor a caller in the target needs.
- Use the target's means of switching off its own checking only where the target
  meets foreign code.
- For an input outside the answers of step 1, the target does what is natural to
  it, and the entry is dropped on that ground.
- Design and check the crossing for callers that stay like any other signature.

Ends when every entry not dropped has a passing check and each signature traces to
entries.

## 5. Changes to what the original does

Until every entry holds, a difference between the two cannot be sorted into port
error or improvement. So:

- A change that alters no entry (speed, for one) may be made; name it in the report.
- A change that alters an entry waits until every entry holds, is then its own
  change, and is the user's decision. A decision the request already gave ("and fix
  that bug while you are at it") stands and needs no second ask, but its change
  still waits until step 6 has ended.
- A fault you see in the original becomes an entry in state kept fault, naming the
  callers that rely on it. A kept fault that loses data or weakens security is put
  to the user before the port is called done.

Ends when every fault seen has its entry and each grave one has the user's answer.

## 6. Compare and read

Where you can run the original, run both on inputs drawn from the entries, a few
per entry, and compare the outputs; a comparison not run is reported as not run.
Then read the result once as a reader fluent in the target would: remove anything
that reader would flag as a habit of the original's platform, or justify it by an
entry; where the target is much larger than its original, read it for parts no
entry needs. Give every difference the comparison shows a destination before this
step ends: a port error, fixed; an entry that was missing, added with a state; or a
kept fault under step 5.

Ends when you ran the comparison and sorted every difference, or reported it not
run; the reading has no open item; and the target's build and static checks ran
with no error.

## 7. Switch

Only when step 1 says the port replaces the original here. Callers that move use
the target. Callers that stay reach it through the crossing, which by now has its
entries and passing checks and is the one live path; this step only cuts over.
Delete the original's body, and every one of its own checks, in the same change
unless the user asked for a period with both; then body and checks stay together.
A check with no counterpart in the target goes too, and the report says why: its
entry was dropped, or the checks were left out on the user's word. When step 1 says
the port does not replace the original here, make no switch and no delete; a delete
is put to the user.

After the cut, search the repository being changed for every reference that led to
the original: a call, an entry in a build manifest, a packaging list or a job
definition, a generated file checked in. Judge each hit by where it leads, since
the crossing may live under the original's name. Give each reference found one
destination: it now leads to the target or its crossing (for a generated file,
change what generates it), or the report names it as not settled, as for a name
built at run time or a string the search cannot resolve. Then run the target's
build and static checks again; a file that exists only after a build shows up here.

Ends in one of three ways: you made the cut, gave every reference the search found
its destination, and ran the build and static checks again with no error; the
user's words for keeping both are quoted; or step 1 answered that the port does
not replace the original here.

## Leaving a part out

When the user tells you to go on without a part (the record, the checks before the
body, the comparison), say what you then cannot vouch for. The user's instruction
decides; the report names the part as left out on the user's word. A part left out
this way counts as ended.

## Borders

- Use `source-grounded-implementation` when the target's idiom or API for the exact
  installed version is in question.
- Use `test-first-seams` (`verification` skill) for new behaviour once every entry holds.
- Use `bug-diagnosis` (`diagnosis` skill) when a kept fault chosen for fixing has no evident cause.
- Use `performance-verification` (`diagnosis` skill) when speed is the reason for a change.
- Use `pr-body` (`docs` skill) when a pull request description is being written.

## Done and report

Done means steps 1 to 7 have each ended or been left out on the user's word, and
each fix the user decided is made.

Give the report in the answer, with no new file, grouped by what the user must
decide: the answers of step 1; the record in compact form, one line per entry or
group of like entries, giving where the expected value came from and the check that
pins it, so a reader can audit that each check of the original has its counterpart;
dropped entries, each with its ground; kept faults with their callers; changes that
altered no entry; entries whose expected value rests on reading; what was compared
and what was not run; what the search after the cut did not settle, the code of
callers outside the repository included, which was not searched.
