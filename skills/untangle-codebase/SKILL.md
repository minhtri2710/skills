---
name: untangle-codebase
description: Restructure the production code of a named area, or of the repository, so that a changed requirement lands in one place, keeping behaviour. Use only when the user explicitly invokes untangle-codebase. Do not use to judge tests, clear stale docs and debris, shape one module, or question the system's archetype.
disable-model-invocation: true
---

# Untangle Codebase

A structural refactor that keeps behaviour, on the area the user names, else
the repository. One question measures structure, for findings and proposed
fixes alike, the change question: when a requirement changes, does the code
that has to change sit in one place, and is nothing else forced to change with
it? One log file holds baseline, findings, decisions and behaviour differences,
and carries the work across a context reset. When the survey will not fit one
context, chart the effort with effort-charting (`planning` skill) and run this skill per area.

## 1. Baseline

Run the checks the repository already uses to show behaviour and write their
result at the top of the log, failures that predate the work included, so a
later failure can be told from an old one. Name beside it the parts of the
scope no check exercises (with only a build and a linter, that is all of it).
Leave uncommitted work outside the refactor as found. Done when the baseline
result and those blind parts head the log.

## 2. Survey, read-only

Log each finding with file and line and one sentence: which change would go
wrong, and how. The three kinds below are what the change question returns for
the edit sites, the places edited for one requirement change. Take them in
this order, since what the first removes need not be read for the others.

1. Idle code: no change to a requirement would ever lead anyone to edit it.
   The deletion test of deep-module-design (`design` skill) confirms it.
2. Unlinked edit sites: for one requirement change, starting at one site and
   following what the code references does not arrive at the rest, as when one
   module writes a format that another reads and no definition is shared.
3. Unearned edit site: edited or re-verified only for what it is attached to,
   its own requirement unchanged (reporting code that follows storage layout).

A special case is code that would be deleted, by itself, if one situation
stopped occurring. Log each, and ask in step 3 what the system would have to
be for that situation to be an ordinary case; never repair one singly.

A tool's report (unused code, a cycle, a duplicate) is a lead until you have
checked the ways code is reached that a static tool misses: dynamic loading, a
framework's conventions, generated consumers, use from outside the repository.
Code the repository holds but does not author (generated, vendored, an applied
migration) is surveyed at what produces it, not where it lies. Change history
shows what changes together. Done when a full pass adds no finding.

## 3. Redesign

Regroup the log by decision: the fewest that remove the findings. Design for
today's requirements, not as a patch on the present shape; one decision that
dissolves several findings beats one repair each. Test each decision with the
change question. Show the regrouped log to the user and wait for the go,
unless the invocation already asked for the changes; even then, put to the
user before step 4 any decision that changes behaviour others can observe (a
public interface, stored data, a wire format). A survey with nothing worth a
decision ends the skill here, a valid result. Done when every finding ends
under exactly one decision or under a line saying why it stays.

## 4. Cut

One decision at a time, each as one complete change: new shape, every caller
updated, old path deleted in the same change (no adapter between, unless the
user asked for a period in which both live), then the baseline checks. In a
blind part they prove nothing: first write a check to run before and after, or
put the cut to the user with the gap named. A caller in a file with uncommitted
work outside the refactor makes that decision wait and be reported; never cut
over that file or leave the caller on the old path. Once cut, each special
case under the decision is gone or stays in the log with the need that keeps
it. A behaviour difference a cut causes or uncovers goes in the log and the
report; bugs are not hunted. Done, per decision, when the baseline checks give
the baseline result.

## 5. Recheck

A fresh reader with the result but not the log (a subagent, else a new session)
repeats the survey; findings go back to step 3 until none is worth fixing.

## Done when all four hold

- the baseline checks give the baseline result, bar differences the log names,
  and every cut in a blind part had its own check, run before and after, or
  was put to the user with the gap named;
- every finding is under a decision that was cut or under a line saying why it
  stays, and each special case that remains has its need in the log;
- the last survey by a fresh reader returned nothing worth fixing;
- for the three kinds of change the area's history shows it gets most often,
  the edit sites in the result are one place, or the log says why not.

The final report gives these four with evidence, the decisions taken, the
findings left with reasons, and what was put to the user. Do not commit, push,
or open a pull request unless asked.

## Neighbours

- Tests to judge for proof value or redundancy: test-proof-debt-audit (`verification` skill). Here
  they are the baseline; change one only where a cut changes its interface.
- Stale docs, plans, scripts, or debris: repo-refresh, which removes what is no
  longer true around production code; this restructures that code.
- One named module or seam to design: deep-module-design (`design` skill).
- A doubt the system is the right kind of system: architecture-premise-audit (`design` skill).
