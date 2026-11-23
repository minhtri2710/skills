# Delivery sequence

The [workflow contract](../SKILL.md) defines the tiers, shared rules, and dangerous acts
used in these steps; [Supervisor and Lead](supervisor-and-lead.md) defines the upward
events and Advisor consults.

## 1. Place it

The project's one Lead runs each delivery the Supervisor hands it (relaying
the Human's request per "Human words" in Every agent), one branch per delivery. A
delivery whose input holds more than five independent findings splits into deliveries of
at most five. The Supervisor creates each Lead with that project's `workspaceId`, never
its own, and its prompt names the Advisor's id where its grants name one, which the Lead
writes into the record's `handoff.md`. The Lead starts, in parallel, every queued
delivery that no pending answer holds and whose written paths are disjoint from those in
flight; one that overlaps waits for the merge it overlaps.

The first delivery in flight
runs in the project's existing workspace and creates no workspace worktree; each
further one runs on its own branch in its own `--new-workspace worktree` workspace,
outside the Lead's cwd: there an Engineer writes the work even when it does not split,
every shell command the Lead needs (a commit, a git read, a checksum, creating a lane
snapshot of the delivery's SHA and running a lane in it, where the snapshot path sits
outside the Lead's cwd and every workspace, created with literal paths and no `cd`, and
a lane runs from a script or with the runner's own directory flag, for example `git -C`
or `make -C`, never after a typed `cd`) is run by that Engineer exactly as the Lead
names it, a lane as a tracked background task, with the output, SHA, and lane output
path reported back, and the Lead reads files there with its file-read tools only, since
a Lead shell command naming that path raises a dialog.

Before it goes in flight, the Lead names the host ports, databases, compose projects, and container names each
delivery's checks use, and checks that share any of them run one delivery at a time.
Every Engineer of a delivery works on that delivery's branch and checkout, never on a
branch, worktree, or PR of its own; commits, exact-SHA review, merges, and close-out
stay per delivery.

The project's record is `~/.paseo/reports/<project>/`; its
`handoff.md` holds state, standing rules, open dangerous acts, and next work, and names
the record's `grants.md`; the Lead updates it before each event. Another workflow's
state directory is data, never the record. Done when the workspace id and branch are
named in the project's record, and the delivery's written paths, docs and generated
mirrors included (derived from each user-visible change in the design: the file that
documents it, who writes it, and any generated file that follows from it), are in the
record and compared with those of every delivery in flight before it starts and again
whenever its owned paths widen, where an overlap found holds the later-started
delivery's overlapping work until the earlier one merges, as at start.

## 2. Staff it

The Lead partitions by default: one Engineer per disjoint path set, all
running in parallel; overlapping work is one Engineer, not two. A shared interface,
schema, or generated file belongs to one Engineer; the Lead routes every change to it
through that owner and relays each such change to every Engineer whose paths use it. Once
a delivery has staffed an Engineer, every source change in it goes to an Engineer,
whatever its size. Only when the work does not split, the delivery has not staffed an
Engineer, and its plan says none will be, does the Lead write it itself (not in a
worktree workspace, where an Engineer writes it, as step 1 says), under owned paths and a
report, as an Engineer would; the plan records why before the first edit.

Each Engineer's prompt names its owned paths, its delivery's branch and checkout, and its
reporting target; the prompt also relays what the Human said per "Human words" in Every
agent; a brief for any seat (a Reviewer's included) that bans a form of command also
says beside the ban what the seat does instead, taken from this skill where the skill
says it (example: a ban on naming a file in a shell command says how the seat finds
references to that file, such as the file-search tool, or that it does not search for
them); a brief for a delivery that adapts an idea from a third-party source states the
idea in wording, clause order and list order of its own, not the source's; the Lead
compares the brief with the source lines for each of the three before staffing, and the
prompt tells the writer not to follow the source's sentence or list; the prompt also has
the Engineer list, before editing, every reader and writer of each field, function, or
input rule it changes (specs and tests included, inside its owned paths or not), found
by searching the whole repository for the bare name and call shape, scripts with
embedded code included, never for one qualified spelling, and, when the change adds an
input (examples: a flag, a field, a route, a message kind), the existing code that
first reads that input (its parser, router or decoder), and reach each one or name why
not.

Replace a Lead only after its `handoff.md` is current; for a Lead that cannot
write it, the new Lead writes it from the old Lead's `paseo logs` before other work.
The new Lead first checks that record against each delivery's tree and writes each
mismatch into it, and reads `grants.md` unchanged.

The plan names the fast lane, each acceptance lane with the paths it reads, and the project's
refusal and acceptance table, or none; the plan also names each act of the delivery on
the "Dangerous acts" list, its merge included, or says there is none; when a grant or
a brief exempts one call from a
rule the delivery adds, the plan lists every caller, direct or through another function,
of the function that implements the exempted call, and the table gives each caller a
row, exempt or refused; when the delivery changes a path with a stated target not shown
met before it, in a way that can move the measure, the plan also names the fixtures,
and the measure is recorded before and after the change on those same fixtures. Any
choice between two or more designs or approaches takes Advisor consult point 1 first.
When the plan names a lane of a kind
that step 5 points to a reference for, read that reference first. A tool a lane runs or
downloads (a pinned binary or other artifact) is checked against a recorded checksum
and lives in a repo-local gitignored directory or a persistent cache, never `/tmp`,
which a reboot clears. Done when every writer's owned paths are disjoint and written
down.

## 3. Implement

Engineers write inside owned paths; before reporting, each runs the plan's
fast lane with the same race or sanitizer flags as the acceptance lanes (for example a race
detector) and every static check they run on its owned paths (examples: a typecheck, a
lint), so a data race or a static fault is caught before hand-in, and checks its change
against the refusal and acceptance table the plan names, each such caller's row included,
quoting both in its report.

The report also carries: step 2's reader and writer list, each one reached or named with why not; for a
change that tightens or loosens an input rule, adds an input, or turns a refusal into a
hold, an accept, or a silent drop (a broad catch around a refusal counts), or the
reverse, a table of inputs the old code accepted and the new code refuses and the
reverse, each row marked intended or defect (a refusal turned into a silent drop is
always a defect), with a row for each way an added input can be absent or ill-formed
where the code that first reads it reads it (for a flag: missing, empty, or followed by
another token); each containment or refusal guard in a function it changed, with the
line that shows the guard still holds or the brief item that removes it; for each test
it deletes or rewrites, each behaviour that test pinned and the surviving test that pins
it; and every deviation from its brief as a named item, which the Lead accepts or sends
back.

Done when every Engineer has reported, none is running, and the Lead has checked
each reported change against the diff and, before a statement in a report about what
calls, reads, or depends on the changed code enters a commit message, a PR body, or the
record as fact, that statement against the code.

## 4. Commit

Only the Lead commits (in a worktree workspace, through its Engineer as step
1 says), on the delivery's quiet tree: `git status --porcelain` shows only this commit's
paths. Done when the commit SHA is named.

## 5. Review

At the commit, the Lead starts (in a worktree workspace, through its Engineer
as step 1 says) the plan's acceptance lanes and end-to-end runs on a detached snapshot of
that SHA (a worktree or archive; a scratch copy comes from `git archive <sha>`, never
`cp -R` or rsync, and no agent runs a writing git command in a snapshot or a copy; a
suite that reads the git index or history runs on a worktree, since an archive copy has
no `.git`), never the live checkout, and in parallel staffs a Reviewer there, as a
different agent instance from every writer. Engineers may keep
editing the branch checkout meanwhile: a new commit gets its own lanes and review,
and those running report on their own SHA.

The Reviewer reviews the diff while
the lanes run, runs no lane, generator, or formatter (a generator is a write; to check a
generated file it asks the Lead to compare it, which the Lead does as a lane on the
snapshot that runs the generator there and shows any diff, never in the live checkout),
writes its report file with its file-write tool before it reports (each Reviewer prompt,
the delta re-review's included, names that file's path literally), and reports `PASS` /
`FAIL` / `BLOCKED` only after reading every lane's output file, quoting what it saw
there, never the Lead's line about the lane; the Lead sends it each file's path as its
lane ends and writes into the record's `handoff.md`, in UTC, the start and wall-clock
bound of each lane that runs as a tracked background task and its end when it ends,
and a Reviewer waiting on one is not stalled.

A lane's output shows, before and after it,
the SHA it ran at and, for a worktree snapshot, an empty `git status --porcelain` there.
The output also shows, at both points, the load averages (`uptime`) of the host it ran
on, and a Reviewer puts a failure or a slow run down to host load only by quoting those
averages.

A lane's script itself checks every precondition the lane relies on (examples: a control
that must show a refusal, a profile that must be written, a directory that must exist),
and a failed check stops the lane before the launch that precondition guards, since a
precondition set up outside the script is lost when the script is copied.

A lane is green at a SHA when its output shows it passing there, or at an earlier SHA
whose diff to this one touches no path the lane reads. A lane is not green at a SHA
while any run of it there failed and that failure has no diagnosis in the record: an
intermittent failure, or one the change did not cause, is diagnosed from the failing
run's own logs, a green rerun alone closes nothing, the fix for one the change did not
cause is split into a delivery of its own, and the failing run's output goes to the
Reviewer with the rest. The Reviewer checks and states these conditions in its verdict,
and a lane that fails them runs again. A `PASS` needs every lane green at its SHA. A
figure measured at an earlier head is stated with that head; it is given as a later
head's only when the diff between the two touches no path the measurement reads, else
the later head's figure comes from a new measurement. A Reviewer whose review spans more
files than one context holds reports a table naming who read each file (itself or a
named read-only subagent); a `PASS` without it is no `PASS`. A lane that reads a path
solely as a build input, checks terminal output meant for a human, runs on a second
host, or launches an installed program the project does not pin that can update itself
(an install) or call out on its own (a network call): read [review lanes](review-lanes.md)
before planning, running, carrying, or reviewing it.

A delete, move, or overwrite in the change whose path comes from stored state is a `FAIL`
until it has a containment guard in the same delivery, never an accepted risk. A new test
the change does not need, or one that duplicates an existing proof, is a finding; a stub
that breaks the stub rule in "Extend before adding" (Every agent) is a `FAIL`.

Before each Reviewer prompt, the delta re-review's included, the Lead stores each writer's
report (an Engineer's, or its own when it wrote the work), each round's in its own file,
in the record; each Reviewer prompt names those files and asks for step 3's report items
(the Review-only route has no writer report, so it names and asks for none); the
Reviewer checks them against the diff and judges each brief deviation: a lost guard, or
a behaviour left with no test pinning it, is a `FAIL`; a change in accepted or refused
inputs that the table omits or marks defect is a finding, and a refusal turned into a
silent drop is at least Medium however its row is marked.

A `FAIL` lists every finding at its SHA and goes back to the owning writer; the fix is
committed on top of the failed SHA, with no amend, rebase, squash, or force-push before
merge, and the same Reviewer re-reviews `git diff <failed SHA> <new SHA>`, its prompt
naming both SHAs and a new report file, which never overwrites the earlier round's.
Paseo deliberately keeps the same Reviewer for this delta review; the
one-instance-per-head rule of agent-delivery-workflow governs that skill's seats only.
Where a fix rewrites a sentence of a rule or a contract, its writer and the delta's
Reviewer compare the new sentence with its base text on the product line as well as with
the finding, and name each case the base covered that the new text no longer does.
Only the lanes that fail the carry rule at the new SHA run again.

Every finding carries a severity (High, Medium, Low, or Info), and only High and Medium block; a Low or Info
finding reported with a `PASS` does not reopen the review, and the head goes on to
step 6. A Low that is a correctness or user-visible defect goes into the next queued
delivery touching its area, else into the record's next work; style, wording, and doc
Lows join the next delivery that touches the same file, or wait for the next trial or
usage pass (a round of running the product to find defects). This delivery's record and
the receiving delivery's plan name each such finding. A delivery that only fixes Lows
opens no further delivery for a Low its review finds, unless that Low is a correctness
defect. A second `FAIL` round with a Medium or higher finding, and dropping a finding,
review claim or bug as "does not hold", each take Advisor consult points 2 and 3 first.
Done when a `PASS` names the SHA it covers.

## 6. Merge

The Lead pushes the delivery's branch, opens or updates its PR, and
squash-merges it once a `PASS` names that PR's head or a head with the same tree, CI is
green on that head where the project runs CI, where the merge is on the "Dangerous
acts" list, that merge's answer, asked after the `PASS`, has arrived, and the head
contains the product line's
current head, shown by `git merge-base --is-ancestor <product line head> <PR head>`, read
after a fetch right before each merge and again for every other open head after each
merge of its own, its exit status written to the record (a forge accepting the merge is
no proof), or is a stacked head meeting its proof (below);
otherwise it merges the product line into the branch (a figure measured before the
merge: step 5), never rebasing a pushed branch, and the new head is reviewed again
unless its tree equals the reviewed head's. Where CI cannot run for a recorded reason,
a Human condition in `grants.md` that names its
replacement checks and its removal condition stands in for green CI, and the record,
the `closed-out` event, and any `dangerous` request for the merge name the CI state.

A branch holding more than one commit has its squash merge given its subject and body
explicitly by the Lead: a PR body is the squash message only for a one-commit branch or
a forge set that way. Where the project requires a commit trailer, the squash message
carries it: the PR body ends with it before the merge (where the PR body is the
message), or the merge is given its message explicitly. After a merge given an explicit
message, and after every merge where the project requires a trailer, the Lead reads the
squash commit's message on the product line; a required trailer missing there is an
`incident`, never a fix-up push.

Stacked heads (each head stacked on the previous one):
read [stacked merges](stacked-merges.md) before reviewing or merging them. A dangerous edit to
declarative runtime config (a compose file, manifest, or unit file) is written only once
approved, and applied in that same window. Done when the merged head is named and each
dangerous act is reported with its answer, or as pending with the work it holds.

## 7. Close out

Each delivery closes on its own: check that each merge it made in a stack
squashed to a tree equal to its head's; archive each agent it created, an agent with a
report file no earlier than when that file exists and its status shows no turn
running (this sets the earliest moment only: in a worktree delivery its Engineer removes
the worktree and snapshots before it is archived, as below), then the workspace it
created; a child of theirs that must keep running is detached first, and the
workspace holding it stays with its worktree, recorded as still open. Remove its
worktree and any leftover directory (in a worktree workspace, by its Engineer before
that Engineer is archived, as step 1 says).

If the delivery used `--new-workspace local --cwd <path>`, `paseo project delete` the
project whose `paseo project ls` path equals `<path>`, never the main checkout's, nor one
holding a kept workspace: deleting a project deletes all its workspaces.

Then write to the project's record what changed, what was removed, tests run with their output, the net
test-line change with one line of reason, what is still open, and the times of its start,
first Engineer report, `PASS`, and merge, each written in UTC to the record when it
happens, and
send `closed-out`. Every SHA, head, installed version, and branch state in `closed-out`
is read from the remote, the checkout, and the installed copy after its act completes,
never drafted ahead of it.

In that same turn the Lead starts every queued delivery step 1
admits; with none in flight, it ends a turn only on an empty queue or with every queued
delivery held by a pending answer. A Lead that ends a turn with queued work that no
pending answer holds (example: a path overlap with a delivery in flight) keeps one
recurring self-prompt (a heartbeat, not the Heartbeat tier), each wake one turn that
re-reads `handoff.md`, starts what step 1 admits, and ends; it deletes the heartbeat
once no such work is queued. A Lead whose every queued delivery is held by a pending
answer keeps none, since the answer arrives as a prompt.

After each trial or usage pass
(step 5), the Lead runs the `test-proof-debt-audit` branch of the `verification` skill on the fastest-growing suites
and deletes redundant tests in a delivery of its own, through the normal review. Done
when `paseo ls`, `paseo workspace ls`, `paseo project ls`, and `git worktree list` show
nothing a delivery of this project created that no delivery in flight owns or the
record names as still open, and every queued delivery step 1 admits has started and the
self-prompt heartbeat is armed or absent as this step sets; report an archive only
after `paseo ls`, not the workspace state, no longer shows its id.
