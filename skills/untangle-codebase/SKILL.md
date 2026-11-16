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
context, chart the effort with effort-charting and run this skill per area.

## 1. Baseline

Run the checks the repository already uses to show behaviour and write their
result at the top of the log, failures that predate the work included, so a
later failure can be told from an old one. Leave uncommitted work outside the
refactor as found. Done when the baseline result heads the log.

## 2. Survey, read-only

Log each finding with file and line and one sentence: which change would go
wrong, and how. Survey in this order, since what the first class removes need
not be read for the others:

1. Idle code: code with no reason of its own to change. Deleting it loses
   nothing (deep-module-design's deletion test), it varies along an axis that
   has only had one value, or nothing reaches it.
2. A tie the code does not show: two places one change must touch together,
   with nothing in the code saying so (a repeated rule; state passed through
   something shared and unnamed; an order of calls a caller has to know).
3. A tie the change does not need: places bound together that change for
   different reasons (a caller that knows what the interface should hide; a
   dependency pointing from steadier code to more volatile code).

Also log every special case: code that serves one situation and does not
follow from how the system works, whatever its form; if the situation went
away, this code and nothing else would go. It is a requirement the design has
no place for: evidence for step 3, never repaired on its own.

A tool's report (unused code, a cycle, a duplicate) is a lead. A finding enters
the log as fact only after you check the ways code is reached that a static
tool misses: dynamic loading, a framework's conventions, generated consumers,
use from outside the repository. Change history is evidence for what changes
together and how often. Done when a full pass over the scope adds no finding.

## 3. Redesign

Group the findings under the fewest design decisions that remove them, each
written above the findings it answers. Design for today's requirements, not as
a patch on the present shape; one decision that dissolves several findings
beats one repair each. Test each decision with the change question. Show the
grouped log to the user and wait for the go, unless the invocation already
asked for the changes; even then, put to the user before step 4 any decision
that changes behaviour others can observe (a public interface, stored data, a
wire format). A survey with nothing worth a decision ends the skill here, a
valid result: make no change to have something to show. Done when every
finding sits under a decision or a line saying why it stays.

## 4. Cut

One decision at a time, each as one complete change: new shape, every caller
updated, old path deleted in the same change (no adapter between, unless the
user asked for a period in which both live), then the baseline checks. A
special case the redesign makes unnecessary goes with it; one still needed
stays, with its requirement named in the log. Bugs are not hunted; a behaviour
difference a cut causes or uncovers goes in the log and the report. Done,
per decision, when the baseline checks give the baseline result.

## 5. Recheck

A reader with fresh context and without the log (a subagent, where the harness
has one) repeats the survey on the result; its findings go back to step 3,
until a survey returns nothing you can defend fixing.

## Done

The whole skill is done when:
- the baseline checks give the baseline result, bar differences the log names;
- each special case left in scope has its requirement named in the log;
- you can name the one place a usual change to the area lands;
- no dependency points from steadier code to more volatile code;
- the last fresh survey returned nothing worth fixing.

The final report gives these five with evidence, the decisions taken, the
findings left with reasons, and what was put to the user. Do not commit, push,
or open a pull request unless asked.

## Neighbours

- Tests to judge for proof value or redundancy: test-proof-debt-audit. Here
  they are the baseline; change one only where a cut changes its interface.
- Stale docs, plans, scripts, or debris: repo-refresh, which removes what is no
  longer true around production code; this restructures that code.
- One named module or seam to design: deep-module-design.
- A doubt the system is the right kind of system: architecture-premise-audit.
