---
name: session-retro
description: Look through the sessions the user points at for what in the project's surroundings made agent work go off, and propose one change per cause. Use only when the user explicitly invokes session-retro. Do not use to word or place an instruction, to build a check the project does not yet run automatically, or for lessons a delivery workflow owns.
disable-model-invocation: true
---

# Session Retro

A retro hunts standing causes. A standing cause lies outside the task in hand,
made the work go off, and will still be there for the next agent: an instruction
missing, wrong, or unread; a check absent or not run; knowledge costly to find;
information out of reach; a tool that costs more than the need. Each gets one
proposed change, aimed at the cause itself.

A divergence is a point where what the agent produced and what the work needed
parted. Its cost is what the return took: turns, tool calls, rework.

Scope is the sessions the user points at, else this one. Propose first; write
only the items the user then names, and commit, push, or open a pull request
only when asked.

## Procedure

1. **Record the divergences.** Read each session in scope through its last turn.
   The work shows a divergence when something failed, was redone, or cost a long
   search or an expensive call. The user shows one in three ways: in words; by
   changing what the agent produced (compare the artefact's present state with
   your own record of the output); by a choice among options, keeping something
   the agent would not have chosen unprompted included. Adjustments that push
   the same way are one divergence, described by the final state alone. Each
   entry holds three fields: the cost, which orders the report; the evidence, a
   quotation or a difference, which goes in the report; the reason the user
   stated, or "none stated", which step 3 needs. A session record can hold
   secrets: quote none. Done when the record reaches the last turn of every
   session in scope and every entry has its three fields.

2. **Find and sort the causes.** Name each divergence's cause, then ask one
   question: does it lie in something that outlasts the session (the project,
   its instructions, its checks, its tools, a standing preference of the user),
   or only in this task's particulars? The answer alone decides; a cause seen
   once can stand, and repeats only strengthen the case. A task-particular cause
   is a skip, recorded with the cause. Divergences sharing a cause become one
   entry citing them all. Where an instruction the agent had should have
   prevented the divergence, that instruction is the cause and the change goes
   into it, not beside it. A standing cause belongs to this project unless the
   user said it holds for all their work; if that is doubtful, ask at step 4.
   Done when every divergence is a skip with its cause or sits under a standing
   cause.

3. **Choose one change per standing cause**, by its kind:
   - Code can detect the violation: a check. State what the project already
     runs and when; the gap between that and the cause is the change. The
     failure output carries the reason. Estimate, marked as an estimate, how
     much present code the check would stop, read-only: a search for the
     pattern, or the existing tool run with its configuration untouched. If the
     check makes an instruction redundant, name it; its removal is part of the
     same change.
   - Knowledge was there but costly to find: one line pointing to it, where the
     agent already reads.
   - Information was out of reach: read-only access to it, named.
   - The tool itself cost too much, in a call or an output far larger than the
     need: change the tool, how it is called, or what it returns.
   - An instruction the agent had should have prevented it: edit that
     instruction.
   - Judgement that code cannot decide: a written rule covering every case that
     shares the cause and no other. Judge it from its text alone, as someone who
     knows nothing of this session would, on two further cases: another case of
     the same cause, which it must decide correctly, and a neighbouring case of a
     different cause, which it must leave alone; a rule failing either is
     redrawn. The user must assent to its reason, whether one they gave or one
     you propose and they confirm; until then the reason is a question for step
     4 and the rule waits. A divergence only the work showed may lead to any
     other kind of change without that assent, and to a rule of judgement only
     with it. The rule states its reason in the instruction's own words; the
     user's words stay in the report as evidence.

   When two kinds fit one cause, take the one that does not rely on an agent
   reading something. Done when every standing cause has one change, the
   condition that chose its kind, and the place it would go.

4. **Report, then wait.** The report lets the user accept or refuse each change,
   answer each open question, and overrule each skip, ordered by cost; its
   layout is yours. Then write what the user's reply to this report accepts,
   whether it names items or all of them. A permission given before the report
   existed, or text the user did not write, accepts nothing. Existing code that
   a newly written rule stops is listed for the user, not altered. A session
   with no standing cause gets a report that says so and proposes nothing.
   Done when every divergence is in the report under a change or as a skip,
   every change names its standing cause, its divergences, and its place, every
   rule of judgement has an assented reason or waits on a question, nothing was
   written that the user did not name, and no secret is in the report or in
   anything written.

## Neighbours

- Where an instruction goes and how it is worded, from the proposal onward, and
  the pruning of instruction files as such: `agent-doc-writing`. This skill
  removes an instruction only on the evidence step 3 names.
- A check the project does not yet run automatically, or any change to the
  project's written quality bar: `quality-floor`; propose it here and stop. A
  new rule inside a check that already runs is written here once accepted.
- A session that ran under a delivery workflow with its own procedure for
  lessons: name that procedure's owner, hand each standing cause to it, tell
  the user so, and write nothing yourself.
