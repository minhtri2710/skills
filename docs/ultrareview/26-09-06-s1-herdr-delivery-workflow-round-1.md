# Ultra Review: s1-herdr-delivery-workflow Round 1

Date: 26-09-06
Review name: s1-herdr-delivery-workflow
Round: 1
Scope: skills/herdr-delivery-workflow at 038dc27: SKILL.md, 8 references, gate_row.py, evals.json
Report path: docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1.md

Scouts: 10, all returned. Model: `sonnet`, one model for all ten, overlap from assignment and search
angle rather than from model difference. Subagent kind `Explore`; read-only was charter-enforced and
confirmed by tree comparison, not enforced by the tool list — `Explore` retains `Bash`. Raw candidates:
146 rows in `skills/ultra-review-workspace/campaign-01/S1-CANDIDATES.md`, which is gitignored custody,
not this artifact.

Severity here: **P1** a record this project has already written is false, or a mandatory gate is
unsatisfiable as written; **P2** a rule cannot be executed as written, or the instrument cannot
measure what it claims to; **P3** clarity, robustness, or dead surface.

Each finding is tagged with where a fix lands — `prose`, `gate_row.py`, or `evals.json` — because C12
forbids a script and the eval case measuring it from sharing an iteration, so Phase B must split along
that seam.

## Prior Round Guard

Previous reports read:
- none

## Findings

### F001 [P1] `check()` re-parses six fields the doctrine says it re-derives — `gate_row.py` + prose

Severity: P1 | Confidence: high
Source pointer: `scripts/gate_row.py:132-182`, `references/human-gates-and-closeout.md:71`
Evidence:
- `:71` claims the script "re-reads the appended line from disk, re-derives each of those, and exits
  non-zero on any mismatch. Read-back proves the row landed; the re-derivation proves it adds up."
- Of the six fields named, exactly one is re-derived. Push `count` is recomputed (`:164-175`). The
  gate id (`:134`) and the timestamp (`:151`) are format-checked against a regex only. The branch is
  never re-derived (`:153-156` only resolves the commit). `boundary-check` is captured by `PUSH_RE`
  and never recomputed — `main()` does not pass `--boundary` down the `--check` path at all.
  `merge-base --is-ancestor` runs in `build()` at `:65` and never in `check()`.
- Two further instances of the same shape: `check()` tests `field.startswith(known)` for `channel=`,
  `writer=` and `record=` and never validates the value (`:158-163`), so a reconstruction row
  relabelled `record=timely` passes; and `build()` rejects an empty quote on a resolved status
  (`:99-100`) while `check()` tests only `quote is None` (`:181-182`), so `quote=""` parses to `''`
  and passes.
- Found independently by five scouts along four different angles.
Contract violated:
- The ledger's entire evidentiary claim. `--check` prints `ok: G<n> checks out` on rows whose
  boundary-check is fabricated, whose base is not an ancestor of its head, whose `record=` field is
  relabelled, or whose quote is empty.
Plausible failure mode:
- A hand-edited or corrupted row passes re-derivation. The Human's only actual defence is reading the
  file, which is the thing the script exists to replace.
Durable solution hypothesis:
- Extract one `derive(...)` used by both paths so `check()` cannot drift weaker than `build()` again,
  and validate values rather than key prefixes. If any field genuinely cannot be re-derived after the
  fact, remove it from the `:71` claim rather than leaving the claim standing.
Disconfirming check:
- Build a valid push row, hand-edit `boundary-check`, `record=`, or the quote, and run `--check`. It
  should reject and will not.

### F002 [P1] `derive_push` implements the algorithm the doctrine names as the anti-pattern — `gate_row.py`

Severity: P1 | Confidence: high
Source pointer: `scripts/gate_row.py:64-74`, `references/human-gates-and-closeout.md:35-43`
Evidence:
- `:35-43` specifies the record-only push boundary check as the union of paths touched by every commit
  in the range, via `git rev-list base..head` piped through `git diff-tree --root -m --no-commit-id
  --name-only -r`, and states in plain prose: "This computes the union of paths touched by all commits
  being pushed, **not the index or only the final tree diff**."
- `gate_row.py:69` is `git diff --name-only base..head` — the two-dot tree diff, which is exactly "only
  the final tree diff".
- Found independently by scout-09 and scout-08.
Contract violated:
- The single safety check gating an unreviewed write to the product line computes a strictly weaker
  predicate than the one the doctrine writes out longhand two files away.
Plausible failure mode:
- Commit A in the push range writes outside the declared record-only boundary; commit B in the same
  range reverts it. The net diff is empty, `boundary-check=""` is emitted, and the waiver path passes
  clean while an out-of-boundary write shipped.
Durable solution hypothesis:
- Replace `derive_push`'s diff with the doctrine's own `rev-list` + `diff-tree --root -m` loop, and
  thread the result into `check()` per F001 so the field is re-derived rather than re-parsed.
Disconfirming check:
- A two-commit scratch range where commit 1 touches an out-of-boundary path and commit 2 reverts it.
  `derive_push` emits `boundary-check=""`; the doctrine's snippet lists the path.
**First-party instance.** `G90` in this project's ledger carries `boundary-check=""` derived by this
code path. The row is not wrong to have been written — the script produced it — but the field does not
mean what the doctrine says it means, and the ledger is append-only.

### F003 [P1] The Supervisor can extend a standing waiver the layering rule says it cannot — prose

Severity: P1 | Confidence: high
Source pointer: `SKILL.md:48`, `references/human-gates-and-closeout.md:26,:49-54`
Evidence:
- `SKILL.md:48`: a charter, a config key, or a Supervisor message "can add a constraint; none can move
  a decision from one seat to another, remove a gate, or authorize an external write."
- `human-gates-and-closeout.md:49-54` lets the Supervisor extend a standing waiver to a seat the Human
  never named, requiring only same-turn disclosure and revocability.
- `evals.json:408-415` scores the extension as correct behaviour, so this is intended, not a slip.
- The clause names no legitimacy criterion, no ledger row, no notification path, and does not appear
  in `supervisor-policy.md`'s anti-pattern vocabulary.
- Compounding, `:49` says a waiver is "per-project, not per Human session" while `:26` says "only the
  current request qualifies: a prior request, a config key, or an inferred preference never resolves a
  gate", and no intake step reads `gates.md` for a prior grant. And "keep it revocable" names no
  status value, no mechanism, and no check.
- Found independently by scout-01 and scout-07.
Contract violated:
- The authority-layering rule, on the one class of action — external writes — it exists to protect.
Plausible failure mode:
- Either a later delivery cannot discover a live waiver at all and the per-project claim is dead
  letter, or a Lead honours one from memory, which `:26` forbids and the attribution rules punish.
  Both readings are available from the text.
Durable solution hypothesis:
- Decide which layer owns waiver extension. If the Supervisor keeps it, `SKILL.md:48` needs the
  carve-out named, the extension needs its own ledger row kind, and revocation needs a status value
  intake actually greps for.
Disconfirming check:
- Find any intake step that reads `gates.md` for a prior standing-waiver grant, or any defined
  revocation status. Neither exists at this head.

### F004 [P1] Every row's head is ambient HEAD; a reconstruction row is wrong by construction — `gate_row.py` + prose

Severity: P1 | Confidence: high
Source pointer: `scripts/gate_row.py:104-105,:118-125,:192-201`, `references/human-gates-and-closeout.md:77`
Evidence:
- No `--head` or `--branch` argument exists. `build()` takes `<branch>@<head>` unconditionally from
  `git rev-parse HEAD` at invocation time, and nothing cross-checks it against the reviewed, merged or
  pushed SHA the gate is actually about.
- `:77` mandates `--record reconstruction` for a resolved-but-unrecorded gate, which by definition
  describes a past head — and the script cannot express one.
- The push branch (`:118-125`) additionally requires `ls-remote origin refs/heads/<branch>` to equal
  current HEAD, so a historical push can never be reconstructed at all.
- Found independently by scout-09, scout-04 and scout-02.
Contract violated:
- "Verified" in a gate row means self-consistent with whatever HEAD happened to be, not that the row
  matches the SHA it describes.
Plausible failure mode:
- A reconstruction row silently records the reconstruction-time head. The named special case doctrine
  provides for is the case the script gets wrong.
Durable solution hypothesis:
- Add `--head`, defaulting to HEAD, required with `--record reconstruction`, and exempt a
  reconstruction push row from the ls-remote currency check.
Disconfirming check:
- `grep -n 'add_argument' scripts/gate_row.py` — no head or branch override is present.

### F005 [P1] The denial-recording terminator exists and is not wired — prose

Severity: P1 | Confidence: high
Source pointer: `references/lead-policy.md:103`, `references/human-gates-and-closeout.md:81`
Evidence:
- `:81` requires a runtime-denial row per refused command and says to "retry in the narrowest allowed
  shape before treating it as blocking", with no stated stopping point. Recording a refusal is itself
  a refusable command, so the rule recurses.
- `lead-policy.md:103` supplies the terminator: "When the same command fails the same way twice — a
  launch that returns an error, a check that cannot start, **a prompt that is refused** — the third
  attempt is not a retry, it is a decision: inspect the prerequisite first (the binary, its auth or
  quota, the pane's state, **the Lead's own permission**), and when the prerequisite is not the Lead's
  to fix, route `BLOCKED` to the Human."
- A refused prompt is a named trigger and the Lead's own permission is a named prerequisite — the
  exact prerequisite at issue when `gate_row.py` has no allow entry. `:81` never cites `:103`.
- Scout-02 raised `:103` as a candidate and doubted it applied; read at this head it applies squarely.
Contract violated:
- Two files hold two halves of one rule with no cross-reference, and the half that bounds the loop is
  in the file a seat reading about gates has no reason to open.
Plausible failure mode:
- Exactly what happened in C20: refusals 2 and 3 were a byte-identical retry with the same error, so
  `:103` had already fired; attempts 4, 5 and 6 should not have run.
Durable solution hypothesis:
- One cross-reference in `:81` to `lead-policy.md:103`, and a sentence saying whether "the same
  command" is judged by the refused operation or by its literal shape.
Disconfirming check:
- Read `:81` end to end for any stopping rule. There is none; the stopping rule is two files away.
**First-party instance, and it corrects this project's own record.** `iteration-19/HANDOFF.md:81-84`
states that doctrine "states no terminating condition" and that the rule "cannot be satisfied". That is
wrong. This lowers the carried C21 item from a missing base case to an unwired cross-reference, and the
handoff is owed a dated correction of the same shape its refusal count already received.

### F006 [P1] Seven eval cases cannot be scored under the condition they run in — `evals.json`

Severity: P1 | Confidence: high
Source pointer: `evals/evals.json` cases 1, 2, 4, 11, 16, 20, 22; `references/intake-policy.md:11`,
`references/project-config.md:11`, `SKILL.md:14`
Evidence:
- Three doctrine sites agree: a delivery or review-only route reads the project config before
  classifying the lane or staffing anyone, and when it is absent the seat asks the Human rather than
  defaulting silently.
- Condition c is a frozen skill snapshot with no repository and no `config.md`, so the config is always
  absent.
- These seven cases open a fresh delivery or review-only intake without stating config state. A
  doctrine-faithful transcript halts at the config question before reaching the partition, staffing,
  charter, quiesce and review behaviours the assertions score.
- Cases 18, 19, 26, 31 and 43 state config state explicitly and are clean. Case 3 is lightweight and
  exempt by `project-config.md:11`.
Contract violated:
- The instrument's own C12 config-state rule — state in the prompt any runtime state the doctrine
  branches on — was applied prospectively to the newest cases and never swept back over cases 1 to 37.
Plausible failure mode:
- The grader either penalises correct condition-c behaviour or scores an off-doctrine transcript as
  expected. 7 of 43 cases, 16% of the instrument.
Durable solution hypothesis:
- Sweep the C12 rule backwards: every delivery or review-only case states config state, the way 18,
  19, 26, 31 and 43 already do.
Disconfirming check:
- If the eval harness pre-seeds a `config.md`, this dissolves. That contradicts the recorded condition
  c and is a harness question, not a question about this head.

### F007 [P1] Four settled rules have zero eval coverage, including the one housing F002 — `evals.json`

Severity: P1 | Confidence: high
Source pointer: `evals/evals.json`, all 43 cases
Evidence:
- Zero cases for **solo-Lead** as a declared mode, though it has its own rules across
  `lead-policy.md:46,:54,:65,:71,:148,:203` and `peer-policy.md:158`. Every partition case assumes
  `partitioned`.
- Zero cases for the **record-only direct-push clause** (`human-gates-and-closeout.md:32-46`) — the
  most safety-sensitive clause in the file, an unreviewed write to the product line, and the clause
  whose implementation F002 shows is wrong. An eval here would have caught F002 empirically.
- Zero cases for the **Architect disposition and `COUNCIL_REQUEST`** (`structural-misfit-policy.md:66-72`,
  `peer-policy.md:192`) — a full third Peer disposition with its own charter shape and report format.
- Zero cases for **`gate_row.py`'s actual invocation**; no case constructs a command line.
- Zero cases for the **second-death-routes-BLOCKED terminator** (`SKILL.md:78`, `lead-policy.md:99`);
  cases 27 and 28 test the restaff-once path and stop.
- Confirmed by two scouts by independent grep of the full case dump.
Contract violated:
- The instrument measures the mechanism it already measures six times over (cases 1, 20, 23, 24, 25,
  31 on the quiesce→commit→checks→review chain) while whole rules go unmeasured.
Plausible failure mode:
- A doctrine change to any of these four ships with no instrument that would notice a regression.
Durable solution hypothesis:
- One case each, and rebalance the near-duplicate budget (13/29, 33/35) toward them.
Disconfirming check:
- `grep -i 'solo-lead\|architect\|council_request\|record-only' evals/evals.json` — zero hits.

### F008 [P2] Concurrent writers break the read-back guarantee in the direction that matters — `gate_row.py`

Severity: P2 | Confidence: medium-high
Source pointer: `scripts/gate_row.py:55-61,:214-220`
Evidence:
- `next_id()` reads max+1 with no lock; `flock` appears nowhere in the file.
- The read-back self-check takes `rows[-1]`, so a concurrent append between this process's write and
  its read makes a correctly-written row report failure.
- Lead plus Supervisor-as-hands is an explicitly documented concurrent-writer pair
  (`human-gates-and-closeout.md:81`, `supervisor-policy.md:31`).
Contract violated:
- `:71` says "read-back proves the row landed". A failed read-back here does not prove the row did not
  land — the exact inverse of the claimed property.
Plausible failure mode:
- Two rows take the same gate id, or a seat sees a false failure, retries per doctrine, and appends a
  duplicate into an append-only file that cannot be cleaned.
Durable solution hypothesis:
- `fcntl.flock` around read-id / append / read-back, and match the read-back by content rather than by
  position.
Disconfirming check:
- Two near-simultaneous invocations against a scratch ledger.

### F009 [P2] Five custody sites are blind to gitignored paths — prose

Severity: P2 | Confidence: high
Source pointer: `SKILL.md:59`, `references/lead-policy.md:65,:173`, `references/peer-policy.md:123,:152`,
`references/human-gates-and-closeout.md:118`
Evidence:
- All five specify `git --no-optional-locks status --porcelain --untracked-files=all`, which does not
  surface gitignored files; that needs `--ignored`.
- Anything at a gitignored path is invisible to every custody, review and cleanup check in the
  workflow, while acceptance commands can read or execute it.
- The doctrine neither checks these paths nor names the exclusion anywhere.
Contract violated:
- "Nothing unexplained may be committed" is enforced by an observation that cannot see a whole class
  of file.
Plausible failure mode:
- A Peer writes an executable or a fixture at a gitignored path; no custody check sees it; an
  acceptance command runs it.
Durable solution hypothesis:
- Name the exclusion once and decide it deliberately, or add `--ignored` to the custody sites where
  execution is possible.
Disconfirming check:
- `git status --porcelain --untracked-files=all` in this checkout does not list
  `skills/*-workspace/`, which `.gitignore:16` ignores and which holds this campaign's own files.

### F010 [P2] Solo-Lead's mandatory review gate is unsatisfiable with one installed kind — prose

Severity: P2 | Confidence: high
Source pointer: `SKILL.md:43,:61`, `references/lead-policy.md:46`, `references/peer-policy.md:156,:167`
Evidence:
- Five sites state without exception that in solo-Lead the Reviewer must differ from the Lead by both
  kind and model.
- Partitioned mode has an explicit degraded path: `lead-policy.md:46` allows a same-kind fallback with
  a distinct pinned model and disclosed kind-collision residual risk. Solo-Lead has no such fallback
  anywhere.
- `peer-policy.md:167`'s own `INDEPENDENCE:` template lists `same-kind-distinct-model` as a legal
  value, adjacent to prose forbidding it for this mode.
- Intake has no check that two kinds are installed before declaring solo-Lead.
Contract violated:
- A gate that is "still mandatory" and constructively unsatisfiable is not a gate.
Plausible failure mode:
- A solo-Lead delivery with one installed kind deadlocks at Reviewer staffing with no sanctioned
  degraded path, unlike partitioned mode.
Durable solution hypothesis:
- Either forbid solo-Lead at intake when fewer than two kinds are installed, or extend the same
  disclosed-residual-risk fallback to it.
Disconfirming check:
- Find a solo-Lead fallback clause. None exists at this head.

### F011 [P2] Quiesce may never trigger under the workflow's own default dispatch — prose

Severity: P2 | Confidence: medium-high
Source pointer: `SKILL.md:59`, `references/peer-policy.md:152` vs `references/lead-policy.md:62,:98`,
`references/herdr-cli.md:57-59,:181`
Evidence:
- `SKILL.md` and `peer-policy.md` gate quiesce on "every staffed Engineer is idle"; `lead-policy.md`
  says "idle or done".
- Per `herdr-cli.md`, `idle` requires the pane's tab to have been seen in the focused UI, and the
  workflow's own default dispatch is `--no-focus`.
- A settled background Peer therefore reaches `done`, not `idle`.
Contract violated:
- The condition that ends the parallel phase is written against a state the default configuration does
  not produce.
Plausible failure mode:
- A Lead reading `SKILL.md` literally never quiesces; one reading `lead-policy.md` does. The two files
  produce different runs from the same tree.
Durable solution hypothesis:
- One phrasing, in one place, cited by the others — `idle or done`, since that is what the runtime
  produces.
Disconfirming check:
- `herdr agent list` after a `--no-focus` dispatch settles: the state is `done`.

### F012 [P2] No Lead permission posture is defined, and a blocked Lead cannot be woken — prose

Severity: P2 | Confidence: medium
Source pointer: `references/peer-policy.md:35-45`, `references/herdr-cli.md:104,:147`;
`references/lead-policy.md` (absent)
Evidence:
- Peer permission posture is specified in detail; the Lead's own posture is specified nowhere.
- Every Peer report goes through `herdr agent prompt lead-<slug>`, which bounces with `agent_blocked`
  if the Lead is sitting at its own dialog.
- The Lead then never receives the wake that would let it print `Awaiting reports:`, and toasts default
  to off.
Contract violated:
- The report-by-prompt channel, which the whole no-polling design rests on, has an unhandled failure
  mode at its receiving end.
Plausible failure mode:
- A Lead at a dialog silently drops every Peer report; nothing in the design notices, because noticing
  would require the polling the design forbids.
Durable solution hypothesis:
- Specify a Lead posture at intake alongside the Peer postures, and name what happens to a bounced
  report.
Disconfirming check:
- `grep -rn 'lead-args\|Lead.*posture' references/` — nothing defines one.

### F013 [P2] "Resources created by this run" has no meaning after a seat exchange — prose

Severity: P2 | Confidence: high
Source pointer: `SKILL.md:64`, `references/human-gates-and-closeout.md:115`,
`references/lead-policy.md:157`
Evidence:
- Closeout scopes teardown authority to "this run".
- A relaunch is "a fresh start pointed at a context pack, not a resume", and the replacement seat
  "holds none of the outgoing seat's run context".
- No text ties "this run" to the delivery rather than to the acting seat.
Contract violated:
- The central closeout predicate is undefined for the case doctrine explicitly provides for.
Plausible failure mode:
- A replacement Lead concludes it may close nothing and closeout stalls, or closes on no principled
  boundary.
Durable solution hypothesis:
- Define "this run" as the delivery, across any seat replacement holding the canonical Lead name, once
  in `lead-policy.md`, "Seat identity and continuity".
Disconfirming check:
- Find a sentence binding "this run" to the delivery. None exists.

### F014 [P2] Three lifecycle exits have no owner: involuntary Lead death, abandonment, rogue stash — prose

Severity: P2 | Confidence: high
Source pointer: `references/lead-policy.md:52,:64,:105,:157`, `references/supervisor-policy.md:20`
Evidence:
- Every recovery path presumes a written pack or a surviving seat. A Lead pane vanishing with live
  Peers and no pack is covered nowhere — and the Supervisor's own doctrine forbids the polling that
  would detect it.
- `lead-policy.md:52` lets a delivery leave the flight slot only through the full success chain. No
  cancellation or abandonment path exists, so a stuck delivery holds the project's one slot forever.
- A rogue stash is routed `BLOCKED` (`:64`) with no owner, no procedure, and no condition under which
  that BLOCKED is resolved.
Contract violated:
- Three resources with a creation or discovery rule and no destruction rule.
Plausible failure mode:
- Orphaned Peers writing to a shared tree that a new delivery has started on, with no intake check for
  stray prior-run seats.
Durable solution hypothesis:
- One abandonment resolution class that frees the slot with the same teardown obligations; a liveness
  artifact refreshed at each quiesce so a dead Lead leaves something bootstrappable; and a named
  authority for stash disposition.
Disconfirming check:
- `grep -rn 'abandon\|cancel\|withdraw' references/` — absent.

### F015 [P2] The relaunch checklist's first step cannot execute — prose

Severity: P2 | Confidence: high
Source pointer: `references/lead-policy.md:164`
Evidence:
- The step instructs comparing each installed file's `git hash-object` against
  `git rev-parse <deployed-head>:<path>`.
- `<deployed-head>` is defined nowhere, and the repository `git rev-parse` runs against — the skill
  source tree, not the product checkout under delivery — is never named.
- Eval case 12 supplies the head directly in its prompt, papering over the gap for scoring and
  confirming doctrine never supplies it.
Contract violated:
- A checklist step that runs "first" and depends on an input doctrine never provides.
Plausible failure mode:
- Three relaunching seats guess three different values, or all fall through to the weaker sampled
  branch even where a tracked source exists.
Durable solution hypothesis:
- Record the deployed head in `project-config.md` at deploy time and name the repo path in the step.
Disconfirming check:
- `grep -rn 'deployed-head' references/` — one hit, the use site.

### F016 [P2] Hashing files on disk proves nothing about a compacted seat — prose

Severity: P2 | Confidence: medium-high
Source pointer: `references/lead-policy.md:157,:164`
Evidence:
- Doctrine "loads at seat start, not at runtime"; a seat "keeps the old doctrine and allow-list until
  relaunched".
- The `:164` confirmation step fires "after compaction or relaunch" alike. For relaunch it is sound.
  For compaction the seat never reloads, so a clean hash match says nothing about what it is executing.
Contract violated:
- The doctrine's own verification step is proof debt: the cited proof passes when the claimed property
  is false.
Plausible failure mode:
- A compacted-not-relaunched seat reports the check confirmed and proceeds on stale rules.
Durable solution hypothesis:
- State that compaction cannot pick up doctrine changes, and forbid treating the hash check as
  sufficient on that branch.
Disconfirming check:
- Find a compaction-specific reload instruction. None exists.

### F017 [P2] `:155` and `:157` disagree about who may relaunch, and about mid-flight — prose

Severity: P2 | Confidence: high
Source pointer: `references/lead-policy.md:155,:157`
Evidence:
- `:155` names exactly two authorised reasons a Lead seat is replaced, "never on the Lead's own
  initiative". Context growth is neither.
- `:157` commands, unconditionally, "when the run context grows past what can hold the verification
  ledger, gate records, and agent inventory reliably, compact or relaunch the seat" — and in the same
  sentence forbids relaunch "mid-flight with Peers outstanding", which is precisely when context is
  largest.
Contract violated:
- An imperative and a prohibition both apply with no tie-break.
Plausible failure mode:
- The seat relaunches itself against `:155`, or ignores `:157` and exhausts context mid-delivery.
Durable solution hypothesis:
- `:157` reads "compact, or signal for relaunch", never "relaunch", with an explicit escape when
  compaction itself is impossible mid-flight.
Disconfirming check:
- Eval 41 asserts the Lead does not replace its own seat, which resolves the contradiction only by
  strained reading and does not exercise the mid-flight collision.

### F018 [P2] The evidence the doctrine cares most about is the evidence it leaves in the pane — prose

Severity: P2 | Confidence: high
Source pointer: `references/human-gates-and-closeout.md:69,:77,:130-146`, `references/lead-policy.md:199`
Evidence:
- `:69` externalises the gate ledger on the stated ground that "a gate that lives only in the Lead's
  run context dies with the pane".
- The verification ledger (full SHAs, exit codes, verdicts) is kept in run context only, and the final
  handoff block is printed with no file destination. Both carry the identical risk the argument names.
- `:77` caps `--note` because "narrative belongs in the delivery's workspace record" — a destination
  never defined as a file or a location anywhere.
Contract violated:
- The record/control-plane distinction explains why the ledger is not a control plane; it does not
  explain why two more records are denied durability.
Plausible failure mode:
- A pane lost after acceptance takes the whole evidence trail with it; only bare gate rows survive,
  which record resolutions, not evidence.
Durable solution hypothesis:
- Extend the `~/.herdr/projects/<slug>/` convention to a per-delivery evidence record, append-only
  with read-back, and make that the defined "workspace record".
Disconfirming check:
- `grep -rn 'workspace record' references/` — one use, no definition.

### F019 [P2] No vocabulary exists for a runtime-denial row's `--kind` and `--status` — prose

Severity: P2 | Confidence: medium-high
Source pointer: `references/human-gates-and-closeout.md:81`, `scripts/gate_row.py:29-30,:212-213`
Evidence:
- Both arguments are required. `KIND_RE` accepts any lowercase token and `STATUS_RE` accepts
  `open|resolved:<x>|recorded:<x>`.
- No file states which values a runtime-denial row takes, and `recorded:<x>` is a prefix no doctrine
  text ever produces or names.
Contract violated:
- The ledger is meant to be greppable. A field with no fixed vocabulary is not.
Plausible failure mode:
- Each seat invents a convention. This is the likely mechanism behind the recorded observation that
  three seats read the same text and wrote different rows.
Durable solution hypothesis:
- Fix the literal tokens in `:81` itself, and either define `recorded:` or remove it from `STATUS_RE`.
Disconfirming check:
- `grep -rn 'recorded:' references/` — the prefix appears in no doctrine rule.

### F020 [P2] `--check` sees only the last row, and nothing owns running it — `gate_row.py` + prose

Severity: P2 | Confidence: medium-high
Source pointer: `scripts/gate_row.py:190-191,:205-211`; `references/lead-policy.md:164`
Evidence:
- `--check` inspects `rows[-1]` only. No loop, no whole-ledger mode, no chained hash.
- No policy file names who runs it, when, or why; `grep '--check'` across every reference returns
  nothing outside the script's own `--help`.
- The natural owner is the `:164` reconciliation step, which describes manual reconciliation and never
  mentions the script.
- Reconciliation itself is triggered only by relaunch or compaction, never before an ordinary handoff,
  so a continuous seat's dropped row is never caught.
Contract violated:
- Once a row is superseded by a later append it can be hand-edited forever with no detection.
Plausible failure mode:
- Exactly the C20 shortfall — four unrecorded denials in a continuous seat, caught by the Lead's own
  narrative and by nothing structural.
Durable solution hypothesis:
- A whole-ledger check mode, wired into both the `:164` checklist and the acceptance-and-cleanup step.
Disconfirming check:
- Append two rows, corrupt the first, run `--check`. It reports ok.

### F021 [P2] `--writer` and `--repo` are unauthenticated — `gate_row.py`

Severity: P2 | Confidence: medium-high
Source pointer: `scripts/gate_row.py:32,:84-85,:115-116,:189`
Evidence:
- `--writer` is free text with no binding to the invoking session, so a Lead can stamp
  `writer=supervisor-as-hands` on a row it authored alone — the "gate resolved by an authority that did
  not resolve it" vector.
- `--repo` defaults to `cwd()` and is never checked against the project slug implied by `--ledger`, so
  a row describing a foreign repository appends into this project's ledger and passes every check.
Contract violated:
- The row's attribution and its subject are both assertions the script accepts on trust while
  presenting the row as derived.
Plausible failure mode:
- A ledger that reads as authoritative about a repository it never looked at.
Durable solution hypothesis:
- Derive the slug from `--ledger` and require `--repo` to match it; state in `--help` that `--writer`
  is a declaration, not a derivation.
Disconfirming check:
- Run the script with `--repo` pointing at an unrelated checkout; the row appends clean.

### F022 [P2] Assertion quality: seven bundled assertions, two inconsistencies, one ungrounded — `evals.json`

Severity: P2 | Confidence: medium
Source pointer: `evals/evals.json` cases 12[2], 14[3], 17[5], 19, 20[4],[5], 25[3], 33[3], 40, 42[1]
Evidence:
- Seven assertions bundle independently-failable behaviours with "and", so partial compliance has no
  defined score. Case 7[2] looks similar and is not a defect: `peer-policy.md:158` makes its list fixed
  verbatim text.
- Case 20[5] states Reviewer kind independence absolutely; case 16[4] hedges it with the
  `lead-policy.md:46` fallback. Installed kinds are unstated in both prompts, so identical reasoning
  passes one and fails the other.
- Case 17[5] scores a real rule (`herdr-cli.md:177`) against a scenario the prompt never stages: no
  Supervisor, no Supervisor-opened pane. Nothing in a compliant transcript gives the grader anything to
  check.
- Case 19 expects a refusal to repair past the cap on a live "keep repairing" instruction, while
  `human-gates-and-closeout.md:26` says a plain instruction in the current request resolves the gate it
  names. The case picks a side the doctrine does not settle.
- Case 40's Engineer says "Ledger row appended"; only the Lead writes the ledger, and none of the five
  assertions score the authority breach. Independently found here and already carried in
  `iteration-19/HANDOFF.md:118`.
Contract violated:
- An assertion that cannot be marked pass or fail from a transcript is not an instrument.
Plausible failure mode:
- Scores that vary with the grader rather than with the run.
Durable solution hypothesis:
- Split the bundles; align 20[5] with 16[4] or state installed kinds in the prompt; give 17[5] its own
  case with the Supervisor pane narrated; settle 19's question in doctrine first, then cite it; add the
  authority-breach assertion to 40.
Disconfirming check:
- Compare against case 2, whose assertions are cleanly separated one behaviour each.

### F023 [P2] Robustness family in `gate_row.py` — `gate_row.py`

Severity: P2 | Confidence: high
Source pointer: `scripts/gate_row.py:95,:104-105,:188,:206,:214-223`
Evidence:
- A branch name containing `|` or `@` — both valid per `git check-ref-format`, verified empirically —
  writes an unparseable row into an append-only file, detected only after the append.
- `"\n" in note` is narrower than `.splitlines()`: `\v`, `\r`, `\x1c`–`\x1e`, `\x85`, U+2028 and U+2029
  pass validation and fragment the ledger.
- No `encoding="utf-8"` on any `open()`, though G52 makes Vietnamese diacritics mandatory in quotes.
- Nothing creates `~/.herdr/projects/<slug>/`; `main()` catches only `RowError`, so a missing parent is
  an unhandled `FileNotFoundError` traceback rather than the documented exit-1 contract.
- `Path` arguments are never `.expanduser()`-d, so a `~`-prefixed `--ledger` creates a literal `./~`
  tree.
- `check()` locates the terminal quote by `partition(" | quote=")`, a substring search rather than a
  field split.
Contract violated:
- Validate-before-append, on a file that cannot be repaired after the fact.
Plausible failure mode:
- An unparseable or fragmented row in an append-only ledger; a first row on a new project crashing with
  a traceback.
Durable solution hypothesis:
- Validate every field against the row grammar before opening the file; `.splitlines()` for the
  whitespace check; explicit utf-8; `mkdir(parents=True)`; `.expanduser()`; split on `" | "`.
Disconfirming check:
- `git checkout -b 'a|b'` succeeds; build a row on it.

### F024 [P3] The `SKILL.md` role table contradicts its own sources in four places — prose

Severity: P3 | Confidence: high
Source pointer: `SKILL.md:39-44`
Evidence:
- `:39` makes "any approval dialog" a Human gate; `human-gates-and-closeout.md:13,:60-67` carves out the
  routine command approval, which gets no gate record and no ledger line.
- `:42-44` says the Lead staffs every Peer; under the `human-started` posture it explicitly does not
  (`peer-policy.md:42`, `supervisor-policy.md:32`), and `SKILL.md:29` already states that exception.
- `:40`'s "never instruct a Peer" omits the Human-named keypress and the Human-instructed seat start.
- `:48`'s "each seat reads its own layer" names the Lead's and the Peer's scope and never the
  Supervisor's, though `project-config.md:11` grants the Supervisor an audit read.
Contract violated:
- A summary table that a seat may read instead of the source, disagreeing with the source.
Plausible failure mode:
- A seat reading only `SKILL.md` treats a routine approval as a gate, or refuses a Human-started seat.
Durable solution hypothesis:
- Make the table's cells point at their sources rather than restate them.
Disconfirming check:
- Read each cell against its cited section.

### F025 [P3] The router needs the classification the route produces — prose

Severity: P3 | Confidence: medium
Source pointer: `SKILL.md:24-29`, `references/intake-policy.md:15-43`
Evidence:
- Delivery's entry test is whether bounded ownership analysis is needed, which is what intake produces
  — and intake is read only after the route is chosen.
- "One bounded prompt to an existing agent" (lightweight) and "a source change" (delivery) both fit a
  prompt telling a running agent to edit code, with opposite ceremony and no tiebreak.
- Supervise and lightweight both fit "ask lead-X why … and tell me" when the caller's relationship to
  the delivery is unstated.
- The lightweight clause list is ambiguous between disjunctive and conjunctive; read disjunctively,
  "read-only inspection" licenses unbounded fan-out while forbidding the policies that would bound it.
- The trigger requires the word "Herdr", so a Herdr-shaped task phrased without it has no route.
Contract violated:
- Section 1 is the only part of this skill every seat reads, and it is the least decidable.
Plausible failure mode:
- Two seats route the same request differently and neither is wrong by the text.
Durable solution hypothesis:
- One ordered decision procedure with an explicit default, rather than four descriptions.
Disconfirming check:
- Route a dozen realistic front-door tasks by the literal text; the ambiguities reproduce.

### F026 [P3] Teardown says wait; every other rule forbids waiting — prose

Severity: P3 | Confidence: medium
Source pointer: `references/herdr-cli.md:80,:104,:177`, `SKILL.md:78,:80`
Evidence:
- Teardown is "send its own quit sequence, wait for it to leave the pane, then close the pane".
- No mechanism for that wait is permitted: `agent wait` has one named site that is not this,
  `pane wait-output` is only for a pane with no agent, and polling, sleeping and blocking are forbidden
  everywhere.
Contract violated:
- A required step with no permitted implementation.
Plausible failure mode:
- Either the anti-polling rule is violated to implement teardown, or the pane closes before the quit
  completes and leaks a process.
Durable solution hypothesis:
- Specify the event-driven observation used elsewhere for compaction detection, not a loop.
Disconfirming check:
- `grep -rn 'wait' references/herdr-cli.md` and check each site's applicability.

### F027 [P3] Smaller structural gaps, recorded without individual treatment — prose + `gate_row.py`

Severity: P3 | Confidence: mixed
Source pointer: as listed
Evidence:
- `lead-policy.md:84` requires recording a post-merge CI run ID "in the relevant ledger line", which
  needs amending an appended row: the ledger is append-only and the script has no update operation.
  `:84`'s deferral to "the next slice intake or wake" also never fires on a single-issue delivery,
  since wake is defined as a Peer report, a Supervisor message, or a Human instruction — never "CI
  finished" (`:94`).
- `herdr-cli.md:61` defines a fifth lifecycle state, `unknown`; roster reconciliation has no branch for
  it.
- `lead-policy.md:99`'s "both panes' evidence" presupposes the first dead Peer's pane was left open; no
  rule says to leave it open, and none says whether a restaff reuses the pane or splits a fresh one.
- `lead-policy.md:99`'s "missing from the list means it died" is contradicted by `herdr-cli.md:53,:124`,
  where a terminal restart clears a name while the session survives — restaffing then puts two live
  writers on one scope.
- The context pack has no delivery id, slug, head or timestamp distinguishing it from a prior
  delivery's pack at the same fixed path; it is never marked consumed; and it is the one durable write
  the `SKILL.md:70` read-back rule cannot reach, because the writer exits immediately after writing.
- A resolution row carries no back-reference to the row it resolves, so `grep status=open` overreports
  after any resolution.
- `SKILL.md:27`'s `git rev-parse --verify <sha>^{commit}` succeeds for an unreachable or dangling
  commit, so review-only can PASS a SHA no branch contains.
- The push verification hardcodes remote `origin`, while `project-config.md:28`'s `target-line` names a
  line, not a remote.
- The trapped-output fallback names "a temporary directory" with no path convention, no collision
  safety between concurrent Peers, and no cleanup.
- The `human-started` posture opens a gate whose resolution step is named nowhere, and the string
  `human-started` appears in no ledger row.
- Validation-run custody (`human-gates-and-closeout.md:85-109`) names no teardown or abandonment path
  when the owning delivery is BLOCKED or reopened; per-issue teardown reaches Herdr panes, not an
  external run.
- `project-config.md:41`'s closing clause drops its qualifier and reads as a blanket "the Lead does not
  write outside the repository", which would forbid the mandated writes to `gates.md`, the pack and the
  notebook. Most likely an ambiguous antecedent.
- `project-config.md:23-25` defines `engineer-args` as containing the allowlist while `peer-policy.md:37`
  and eval 43 treat it as an opaque pass-through value.
- `human-gates-and-closeout.md:12` makes "material contract change" an unconditional Human gate while
  `intake-policy.md:31,:58` makes it Lead-resolvable through the Design Gate.
- `peer-policy.md:172` requires renaming an already-named Reviewer across repair heads, while
  `herdr-cli.md:124` frames rename as applying to an unnamed agent; the two-step with `--clear` is
  documented nowhere.
- `gate_row.py:188`'s `--help` says "the Reviewer round-trips against a scratch file"; no policy file
  has a Reviewer touch the ledger at all.
- `gate_row.py:100`'s `record == "reconstruction" and not note` guard is dead, since `note` is already
  required non-empty. Previously known; confirmed independently.

### F028 [P3] The derived-count rule detects only self-inconsistency — prose

Severity: P3 | Confidence: high, structural
Source pointer: `SKILL.md:70`
Evidence:
- The rule catches a stated count that disagrees with its own enumeration. Carrying forward both the
  stale count and the stale list together satisfies it perfectly.
Contract violated:
- Nothing, as written. Recorded because the rule's protection is narrower than the confidence it
  invites, and because this project has already produced one instance of the failure it does catch.
Plausible failure mode:
- A consistent, wholly stale report passes.
Durable solution hypothesis:
- None that is a line of prose. This is a limit of prose executed by an agent; the mitigation is the
  command in the message, which the rule already asks for.
Disconfirming check:
- None available from this head.

### Recorded and not carried as findings

- **The empty `files` field on all 43 cases.** Scout-03 reported it as citation drift; scout-08
  retracted it. `skill-creator/references/schemas.md:35` defines `evals[].files` as an *optional* list
  of input file paths — sample inputs, not citations. No case here needs one, so `[]` is correct.
  Verified by the coordinator against the schema, not adjudicated between scouts.
- **Citation integrity is clean.** Two scouts independently checked every quoted cross-file section
  name — 34 and 28 by their respective countings — and all resolve. No reference file is an orphan. No
  `file:line` citations exist in the prose at all.
- **No project-identity leak** in any eval case; `acme-api`, `web-scope` and `<project-slug>` are
  generic throughout.
- **Branch lifecycle** is correctly out of scope: the checkout is the caller's and closeout never
  removes it.
- **The Supervisor notebook** needs no teardown rule; it is a pure evidence record.
- **Candidate C-01, withdrawn to the queue rather than dropped:** the schema names the field
  `expectations` and this file uses `assertions`, but `skill-creator/SKILL.md:195` itself writes
  `"assertions": []`, so the tool is internally inconsistent and this file follows its SKILL.md. Queued
  below rather than reported, since the risk depends on a runner this head cannot see.

## Verification Queue

Read-only checks. None of these implies write permission.

**Correction added 26-09-06, after the S2 review of `ultra-review` and `ultra-review-receive`. Two
statements in this section are wrong and must be read before any check below is run.**

1. **The "read-only" claim above is false for six of the sixteen entries.** F001, F002, F008 and F020
   instruct building, appending or corrupting, and each names a scratch target. **F021 and F023 name
   no scratch target at all.** `gate_row.py:187` makes `--ledger` required with no default, so an
   operator following either as literally written would supply the project's real append-only ledger
   at `~/.herdr/projects/<slug>/gates.md` — the file this report's own F001, F008 and F020 say cannot
   be repaired once corrupted. **Run F021 and F023 only against a scratch ledger in a temporary
   directory. Neither check requires, and neither authorizes, a write to the real ledger.** Carried as
   S2 F005 in `docs/ultrareview/26-09-06-s2-ultra-review-pair-round-1.md`.
2. **This queue is incomplete.** It lists 16 of this report's 28 findings. The twelve absent are F013,
   F014, F016, F017, F018, F019, F022, F024, F025, F026, F027 and F028; each except F027 carries its
   own `Disconfirming check:` inside its Findings block, which is where a verifier should take it
   from. F027 has none, because it is missing four of the seven mandatory subfields. Carried as S2
   F006 and S2 F007.

Both are defects in this artifact, found by an S2 scout auditing it against the skill that produced
it, and both are recorded here rather than by rewriting the entries, so the report a verifier reads
is the report the scouts produced.

- **F001** — build a valid push row in a scratch repo, hand-edit `boundary-check`, then `record=timely`,
  then `quote=""`, and run `--check` on each. Expect three rejections; predict three passes.
- **F002** — two-commit range where commit 1 touches an out-of-boundary path and commit 2 reverts it.
  Compare `derive_push`'s output against the `rev-list` + `diff-tree` snippet at
  `human-gates-and-closeout.md:35-43`.
- **F003** — grep `intake-policy.md` for any step reading `gates.md` for a prior standing-waiver grant;
  grep all references for a revocation status value.
- **F004** — `grep -n 'add_argument' scripts/gate_row.py`; confirm no head or branch override.
- **F005** — read `human-gates-and-closeout.md:81` end to end for a stopping rule; confirm `:103` is
  never cited. Then confirm from the C20 run record that refusals 2 and 3 were the same command with
  the same error.
- **F006** — confirm from the eval harness whether a `config.md` is seeded under condition c. This is
  the one check that can dissolve the finding, and it cannot be answered from this head.
- **F007** — `grep -i 'solo-lead\|architect\|council_request\|record-only' evals/evals.json`.
- **F008** — two near-simultaneous `gate_row.py` invocations against a scratch ledger.
- **F009** — `git status --porcelain --untracked-files=all` against `--ignored` in this checkout.
- **F010** — grep for a solo-Lead Reviewer fallback clause.
- **F011** — dispatch an agent `--no-focus`, let it settle, read `herdr agent list`.
- **F012** — prompt a Lead sitting at a dialog and observe `agent_blocked`.
- **F015** — `grep -rn 'deployed-head' references/`.
- **F020** — append two rows to a scratch ledger, corrupt the first, run `--check`.
- **F021** — run with `--repo` pointing at an unrelated checkout.
- **F023** — `git checkout -b 'a|b'` then build a row; separately, a note containing `\v`.
- **C-01** — determine whether any runner keys on `expectations`. If one does, 43 cases grade against
  zero assertions.

## Strongest Reason Not To Merge Yet

The ledger's evidentiary claim is the load-bearing thing in this skill, and two findings say it does
not hold on rows this project has already written.

`human-gates-and-closeout.md:71` tells every seat that `--check` re-derives six fields and that "the
re-derivation proves it adds up". F001 shows one of the six is re-derived. F002 shows the field that
matters most — the boundary check gating an unreviewed push to the product line — is computed by the
exact algorithm the doctrine spells out longhand as wrong. `G90` in this project's ledger carries a
`boundary-check=""` produced that way.

That combination is worse than either alone. A weak check would be a gap; a check that is advertised as
strong, and cited by name in the doctrine as the reason a seat may stop reading the file, is a false
assurance. Every downstream rule that treats a `--check` exit 0 as evidence is resting on it, and this
seat has done so five times this week.

F005 sharpens the point rather than softening it: the terminating condition this project spent an
iteration calling absent has been sitting in `lead-policy.md:103` the whole time, unreferenced. The
defect is not that the doctrine is wrong. It is that the doctrine is right in a place nobody reading
about gates would look — and the same seat that wrote the analysis had already read both files.

## Next Receive Prompt

Use $ultra-review-receive to verify docs/ultrareview/26-09-06-s1-herdr-delivery-workflow-round-1.md.

**Disclosure added 26-09-06.** `ultra-review/SKILL.md:131-133` and
`create_ultra_review_report.py:102` mandate a fixed closing sentence ending "and implement confirmed
owner-clean fixes." This report does not carry it. The coordinator removed that clause and substituted
the paragraph below, because pasting it would have misstated the Human's grant — and did not disclose
the substitution at the time. The substitution was correct on the merits and it was an unauthorized
deviation from a contract-supplied fixed string; both facts stand. The underlying defect — a producer
that generates the authorization the consumer's write gate asks for, with no conditional form for a
verification-only caller — is S2 F001 in
`docs/ultrareview/26-09-06-s2-ultra-review-pair-round-1.md`, reached independently by three scouts.

**Verification only.** The Human granted a review of the project's skills, not remediation. Every
finding is dispositioned CONFIRMED / DISPROVEN / DUPLICATE / BLOCKED / DEFERRED and nothing is fixed in
this pass; verification does not imply write permission. Fixes are Phase B, opened only after the whole
campaign's confirmed findings are ranked, and each one is a separate delivery with a real Engineer and
an independent Reviewer on the exact head.

When Phase B opens it splits three ways, and C12 forbids merging the splits: `gate_row.py` fixes
(F001, F002, F004, F008, F020, F021, F023), the prose fixes (F003, F005, F009–F019, F024–F028), and the
`evals.json` cases measuring them (F006, F007, F022) — which must land in a different iteration from the
script and doctrine changes they measure.
