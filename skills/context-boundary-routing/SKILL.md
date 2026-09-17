---
name: context-boundary-routing
description: At a phase boundary, choose between continuing in this context, clearing it, handing off, delegating to subagents, or compacting, and pick the delegation shape when subagents are the answer. Use when a phase of work has just ended (a design settled, an implementation landed, a review returned), when the context is filling, or before spawning agents for a task. Do not use mid-phase; there the only options are continue or split the remaining work.
---

# Context Boundary Routing

A phase ends when the work reaches an "ok, that's done" point: grilling finished,
the implementation landed, QA returned. The gap after it is the only place this
decision belongs. Mid-phase there is nothing to decide; compacting there loses the
thread.

Every move except continuing turns a primary source (the session as it happened)
into a secondary one (a summary of it). The summary has less noise and more room,
and it is lossy in ways the next phase cannot detect, so pay that cost only when
staying costs more.

## The tree, in order; first yes wins

1. **Continue.** Yes when the next phase needs this one as a primary source (an
   implementation wants the design reasoning verbatim, not a digest of it), or
   when enough room remains for the next phase to fit. Continue costs nothing and
   loses nothing, so rule it out before anything else.
2. **Clear.** Yes when everything here — the exploration, the decisions, the dead
   ends — is disposable to what comes next. Cheapest move on the board, and the
   old session stays resumable. Clearing a relevant context is one-way: the
   *why* behind what was built does not come back from reading the diff.
3. **Hand off.** Only when something has to travel: a different harness, a
   different repository or directory, another person, or a side task found
   mid-phase that must not derail this one. The handoff document points at
   artifacts (spec, plan, diff, records) instead of duplicating them, names the
   skills the next agent should load, and is redacted.
4. **Delegate.** Yes when the remaining task is scoped tightly enough to run
   with nobody steering, so a subagent takes it and this session stays intact.
   An automated review of a finished diff is the standard case.
5. **Compact.** Relevant context, same harness, same directory, and the user has
   to stay in the loop. This is where the tree lands often, and it is the
   default, not the first reach: pass it what the next phase needs
   (`/compact we are going to QA the export path`) so the summary keeps it.

## Delegation shape

When step 4 wins, pick the shape and refuse the others.

- **One agent, one perspective, one artifact** is the baseline every other shape
  is compared against.
- **Parallel fan-out with a merge in this context** is justified when the
  sub-tasks share no mutable state or ordering, each produces a different *kind*
  of finding rather than the same finding from another angle, and the merge fits
  in the room this session has left. Skip the fan-out when the change is at
  most two files and under fifty lines and touches no auth, payments, data
  access, or configuration; otherwise fan out even if the diff looks small.
- **Research isolation** sends an agent to read what would otherwise flood this
  context and returns a digest much smaller than what it read.

Four shapes are refused: an agent whose whole job is deciding which agent to
call; an agent that invokes another agent; a sequential orchestrator that
paraphrases each step to the next, paying a lossy summary per hop; and trees
deeper than one level. Depth is at most one, and the merge happens here, where
the primary source still is.

## Brief the agent as a peer

The brief is the only context the agent will have: the goal, what is already
ruled out, the files worth reading, and an explicit scope. If the brief cannot be
written clearly, the task is not understood well enough to hand off, and the
answer was continue.
