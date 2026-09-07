# Project Premise Audit — beo-skills at the project boundary

Run: `architecture-premise-audit`, once, at the whole-project boundary, on this
repository, at HEAD `038dc27b50859cb30542b91683688a1f52ce5d66`.

**The skill was executed as written and unfixed.** S4 F001, F002 and F003 are
open P1 findings against this skill's own procedure, and S4 F003's disconfirming
check is this run's coverage ledger. Fixing the skill first would have made the
run prove nothing about the shipped text. Everything the shipped procedure could
not supply is recorded in the Instrument Log at the end, which is *not* one of
the skill's required output sections and is marked as an addition.

Deliverable path assumption, stated because nothing named one: the campaign
convention is `docs/ultrareview/`, so this file lands there under a slug that
cannot be confused with a round report. `ultra-review/SKILL.md:52`'s one-report
rule governs an ultra-review run; this is not one, so that rule is not in force
here.

Read-only. No file outside this report was created, modified, or deleted.

---

## Verdict

`REPAIR_FIRST`

One finding is an architecture defect by the skill's own test — A1: no forcing
requirement for the premise, and relocating the claim simplifies authority rather
than losing one. A2 is an owner defect of the same weight: the machinery on both
sides is sound and the missing thing is one authoritative sentence. Either alone
carries `REPAIR_FIRST`; neither is a redirect: the skill catalog archetype is right for eight of the
nine units, the `br`-backed delivery contract is right for the ninth, and the
`beo` bundle's individual mechanisms are, one at a time, well-owned. What is
wrong is the layer above them — what enforces the control plane, and which of
two control planes governs. Both are repairable inside the current archetype.

---

## Expected atlas versus observed map

**Product category.** A distribution of agent skill bundles: Markdown contracts
an LLM agent loads, plus the references, registries, and helper scripts those
contracts name. The production consumer is an LLM agent in a session; the
production entry point is the agent reading a `SKILL.md`; the durable effect is
whatever that agent then writes in some *other* repository. Distribution is a
file copy into `~/.claude/skills` (`skills-lock.json` is gitignored at
`.gitignore:4` and tracks nothing here).

**Expected responsibilities for that category.** A selection surface per unit; a
body an agent can execute without ambiguity; a reference layer for detail that
does not fit the body; deterministic helpers for the steps prose cannot make an
agent do reliably; a proof layer over those helpers; and — where two units could
be selected for the same request — a precedence rule. Scaling variable: number
of skill units against the agent's context window and its ability to pick the
right one. Adversarial variable: an agent that self-attests rather than runs.

**Observed, all derived on this turn from `git ls-files` and `wc -l`.**

| surface | tracked | lines |
|---|---|---|
| skill units (`SKILL.md`) | 17 | — |
| top-level skill dirs (`beo` plus 8 standalone) | 9 | — |
| `beo` prose (`skills/beo/**/*.md`) | 22 | 1659 |
| `beo` Python | 17 | 5968 |
| `beo` registry JSON | 9 | 1212 |
| `herdr-delivery-workflow` prose | 9 | 1145 |
| `herdr-delivery-workflow` Python (`gate_row.py`) | 1 | 229 |
| tests, whole repo | 9 | 4094 |
| tests, `beo` only (excludes `tests/test_gate_row.py`, 144) | 8 | 3950 |
| tracked files, whole repo | 89 | — |

The shape that matters is not the ratio. It is that **11130 lines of `beo`
Python, registry, and test exist to enforce a contract stated in 1659 lines of
`beo` prose, and every one of those enforcement lines runs only if the agent
being constrained chooses to run it.** The 11130 is 5968 + 1212 + 3950, derived
on this turn; the test term is `git ls-files 'tests/*.py' | grep -v gate_row |
xargs cat | wc -l`, excluding the 144-line `test_gate_row.py`, which belongs to
`herdr-delivery-workflow`. There is no CI (`git ls-files | grep
"^\.github"` → 0; no `.github` on disk), no hook, and no external invoker in the
tracked tree. `br` is the one genuinely external authority, and the kernel is
explicit that it owns only lifecycle, claim, and closure (`kernel.md:22`,
`kernel.md:30`).

Second shape: **two delivery control planes, and neither names the other.**
`grep -ri` for `beo` across every tracked `herdr-delivery-workflow` file returns
0; `grep -ri herdr` across every tracked `skills/beo/**` file returns 0. Three
files in the repository mention both — `AGENTS.md`, `README.md`, and
`tests/test_gate_row.py` — and only one of them says anything about the
relationship: `AGENTS.md:4`, "These instructions govern only the BEO skill system
under `skills/beo/`; they do not govern unrelated skills in this repository, such
as `herdr-delivery-workflow`." That is a disclaimer, not a precedence rule.

---

## Coverage ledger

One row per discovered ingress, authoritative state family, durable effect,
expensive operation, and external output. The skill's step 6 names five
categories; step 3 names nine. The four step-3 categories with no step-6 home
(queues, schedulers, deployment boundaries, cited proof) are carried here anyway
and marked — that gap is S4 F002, and honouring only step 6 would have let this
audit terminate without them.

| # | item | category | represented in |
|---|---|---|---|
| 1 | agent loads a `SKILL.md` | ingress | A1, A2 |
| 2 | agent runs a named helper from a `SKILL.md` | ingress | A1 |
| 3 | `.beads/artifacts/<id>/TICKET.json` | authoritative state | justified (A1 counterargument) |
| 4 | `.beads/artifacts/<id>/state.json` | authoritative state | justified |
| 5 | `.beads/artifacts/<id>/runtime-events.jsonl` | authoritative state | A4 |
| 6 | `.beads/beo-reservations.jsonl` + `.lock` (fcntl) | authoritative state | A5 |
| 7 | Beads DB via `br` CLI | authoritative state | excluded — external tool, product repos |
| 8 | git worktree `beo/<id>/<actor>/<ts>` | durable effect | A5 |
| 9 | worktree merge into main on `verdict_accept` | durable effect | A5 |
| 10 | product-file mutation under `scope.files.allow` | durable effect | A1 |
| 11 | `skills/beo/beo-author/proposals/pending/prop-*.md` | durable effect | **A3** |
| 12 | `<vault>/beo-learnings/*.md` (qmd/Obsidian) | durable effect | excluded — advisory memory, kernel §8 |
| 13 | Herdr gate ledger row via `gate_row.py` | durable effect | A2 |
| 14 | `beo_verify.py` running ticket verify commands | expensive op | justified |
| 15 | `beo_audit.py` C1–C9 drift scan (837 lines) | expensive op | PROBABLY_JUSTIFIED |
| 16 | `beo_score_trace.py` / `beo_score_context.py` | expensive op | **A4** |
| 17 | `check_skill_bundle.py` | expensive op | PROBABLY_JUSTIFIED |
| 18 | skill distribution: `cp -R` to `~/.claude/skills` | external output | A2 |
| 19 | `tests/` (4094 lines, 9 files) | cited proof | **A6** |
| 20 | queues | step-3 category | none exist; nothing found |
| 21 | schedulers | step-3 category | none exist; nothing found |
| 22 | deployment boundaries | step-3 category | item 18 is the only one |

**Exclusions, each with its reason.** `.beads/` in product repos — authoritative
state owned by `br`, outside this checkout, and no instance exists here (`ls -d
.beads` → absent). Obsidian vault — advisory memory that the kernel forbids from
granting authority. On disk but not part of the product, each with the rule that
excludes it, from `git check-ignore -v`: `.agents` and `.pi` (user global
`~/.gitignore:92`, `:97`), `.claude` (`~/.gitignore:87`), `.backpass`
(`.git/info/exclude:7`), `skills-lock.json` (`.gitignore:4`). Not ignored by any
rule but not tracked either, and therefore not product: `.crew`, `.pytest_cache`,
`.venv`, `docs/`, `scratchpad/`. Porcelain is 8 lines on this turn, consistent
with that split.

`references/structural-antipatterns.md` was **not** loaded. Its condition is
"realtime multiplayer, MMO, or another system with a suspected structural
misfit" (`architecture-premise-audit/SKILL.md:26-27`); this is a document
distribution, no realtime or multiplayer surface exists, and loading a
game-networking lens catalog here would have supplied vocabulary rather than
evidence. That decision is itself an instance of S4 F010 — the load condition's
third clause is circular — and is recorded in the Instrument Log.

---

## Ranked findings

### A1 [architecture defect] The control plane's determinism is enforced only by the agent it constrains, and nothing outside the agent runs it

**Production evidence.** Every gate in the `beo` control plane is reached by an
agent reading a skill card and choosing to run a command. `beo-validate/SKILL.md`
names `beo_reservation.py` and `beo_worktree.py`; `beo-execute/SKILL.md` names
`beo_run.py` and `beo_worktree.py`; `beo-review/SKILL.md` names `beo_check.py`,
`beo_verify.py` and `beo_worktree.py`. No hook, no CI, no wrapper process, and no
`br` extension invokes any of them: `git ls-files | grep "^\.github"` returns 0,
and no `.github` exists on disk. `br` is external and owns claim and closure
(`kernel.md:22`, `:30`) — the BEO-specific gates (approval hash binding, dirty
prestate, scope containment, reservations, worktree lifecycle) are not.

**Hidden premise.** That an LLM operator which can be trusted to run
`beo_check.py` honestly and report its exit code honestly needs `beo_check.py`.
If the agent is trustworthy the determinism is redundant; if it is not, the
determinism is bypassable by not running it, and nothing detects that. The
machinery is built for an adversarial-or-unreliable operator and deployed on the
honour system.

**Tax.** 5968 lines of Python and 1212 lines of registry that must be kept
consistent with 1659 lines of prose, plus 3950 lines of `beo` test holding that
Python in place, plus `beo_audit.py`'s C1–C9 drift checks (837 lines) whose entire job
is detecting when the two halves have diverged. The drift-detection subsystem is
a direct cost of the size, and the size is a direct cost of the premise.

**Amplification route.** Every new rule must be stated twice — once in prose for
the agent and once in Python or registry for the gate — and then a third time in
a test, and then reconciled by C1–C9. One doctrine change costs four edits and a
scan. S4 F001 found the same shape one level down: a mandatory gate satisfiable
without doing its work. At project scale, the whole control plane is that gate.

**Counterargument, the strongest available.** Prose cannot stop an agent from
self-attesting. A deterministic hash-bound approval that the agent *does* run
produces evidence a later reviewer can recompute, and an approval the agent
skipped leaves `state.json` without a `PASS_EXECUTE`, which the *next* phase
reads. So the machinery is not enforcement-at-the-moment but
auditability-after-the-fact, and auditability survives an agent that skips a
step, because the missing artifact is the signal. This is a real defence and it
covers `beo_check`, `beo_approval`, `beo_verify`, `beo_state`, and the dirty
prestate rule. It does not cover the premise that these are *invariants* — the
kernel calls them "Hard Invariants" (`kernel.md:20`) and hard invariants that an
actor can decline to evaluate are conventions.

**Falsifier.** Any tracked invoker outside the agent's own choice — a git hook, a
CI workflow, a `br` plugin, a wrapper that runs `beo_check.py` before a commit —
falsifies this finding as stated. So does a stated design position, anywhere in
`skills/beo/`, that the control plane is auditability rather than enforcement;
`grep -rn -i "advisory" skills/beo/beo-reference/references/`, run on this turn,
returns 15 lines, and the word attaches to optional or reporting machinery in
every one but a single case: qmd/Obsidian memory, `br` labels, the `bv`
boundary, the two scoring helpers, the context-budget ceilings, support-subroutine
output, and the proposal generator. The exception is `kernel.md:163`,
"`beo-plan.decomposition_recorded_contract` is advisory" — one named contract,
declared advisory against the surrounding rule that per-skill
`artifact_write_authorities` and `must_not` "remain binding" (`kernel.md:164`).
That one exception is the closest the bundle comes to the position, and it
scopes itself to a single contract rather than to the control plane.

---

### A2 [owner defect] Two delivery control planes govern the same job with opposite premises, and no artifact says which applies

**Production evidence.** `beo` and `herdr-delivery-workflow` both own: human
gates, approval, scope containment, review verdict, and closure. Derived on this
turn by counting files containing each term: human gate 9/8, approval 14/7, scope
13/9, review 18/9, verdict 15/6, claim 15/8 (beo prose / herdr prose). They take
**structural divergence** in two places — one an outright contradiction, one a
duplicated solution neither plane names:

- *Isolation.* `kernel.md:75`, "Worktree isolation is an optional strict-mode
  feature for full filesystem isolation" — 393 lines of `beo_worktree.py` plus
  563 lines of test, with a merge path into main. Against
  `herdr-delivery-workflow/references/lead-policy.md:30`, "Do not create a second
  working tree for isolation, concurrency, or review; `herdr worktree` is out of
  scope", repeated at `herdr-cli.md:67`.
- *Concurrency.* Both planes solve path-partitioned concurrency, by different
  machinery, and neither one's answer is visible from the other. `beo` gives
  each actor a lockfile: `beo_reservation.py` takes an `fcntl` lock on
  `.beads/beo-reservations.lock`, and `kernel.md:66` calls reservations
  "BEO-local strict-mode path ownership evidence" — ownership evidence only
  earns its cost when other actors exist. `kernel.md:22`, "Work on exactly one
  claimed atomic issue at a time", bounds each actor to one issue; it does not
  forbid the others, so the lock is not a contradiction. `herdr` answers the
  same question with Lead-owned disjoint path scopes and no lock at all
  (`herdr-delivery-workflow/SKILL.md` partitioned mode). Two mechanisms for one
  problem in one checkout, and no tracked file says which one an actor is
  under.

**Hidden premise.** That the repository is a flat catalog of independent skills —
`README.md:3`, "Agent Skills bundle … standalone skills live beside it under
`skills/`". A catalog has no place to record that two entries answer the same
request differently, and this one does not: no tracked file states precedence,
and `AGENTS.md:4` explicitly declines to govern anything outside `skills/beo/`,
which leaves all eight standalone skills with no repo-level governing document.

**Tax.** An agent selecting a delivery skill for a real request has two complete,
internally coherent, mutually silent answers and no discriminator. The cost is
paid entirely at selection time and is invisible in either bundle.

**Amplification route.** Every doctrine improvement to one plane widens the gap
without anything registering that it did. S4 F045 found the description-level
version of this for the two audit skills — "Neither description states precedence
against the three sibling skills whose descriptions match the same requests" The
same defect at bundle scale is this finding, and it is larger because the two
delivery planes disagree about facts, not just overlap in scope.

**Counterargument.** They may be genuinely different jobs: `beo` governs delivery
*inside a product repo* against a Beads issue; `herdr-delivery-workflow` governs
*an agent fleet* in a terminal multiplexer. On that reading the "opposite
positions" are each correct for their own context and the silence is clean
separation. This is plausible and is why the finding is an owner defect and not
an architecture defect — the machinery is fine, the missing thing is one
authoritative statement of the boundary. But the reading is not written anywhere,
and an agent cannot act on a reading the repository does not contain.

**Falsifier.** Any tracked artifact stating when to select which, or a project
config, root `AGENTS.md` section, or `README.md` paragraph assigning each plane a
context. `grep -rn -i herdr skills/beo` → 0 and `grep -rn -i beo
skills/herdr-delivery-workflow` → 0 are the confirming results.

---

### A3 [owner defect] `beo_propose.py` writes into `beo-author`'s own tree and `beo-author`'s contract never reads it

**Production evidence.** `beo_propose.py:5-7` and `:28` write `prop-<sha1>.md`
into `skills/beo/beo-author/proposals/pending/`. `beo-author/SKILL.md` — the
owner of that tree — never mentions `beo_propose.py`, `proposals/`, or
`prop-*.md`; its step 5 covers only `beo_audit.py --check-manifest` scans. The
only tracked reader of that path in the whole repository is
`tests/test_propose.py`. The directory does not exist in the tree.

**Tax.** 213 lines producing an artifact with no consumer, plus 276 lines of test
holding it in place, plus a second proposal vocabulary competing with the wired
one.

**Amplification route.** There are now two proposal channels with different
artifacts. The other one — `harness-proposal.json` — is fully wired: schema,
`pipeline.json:16` and `:25`, `phase-contracts.json`, `state.schema.json:77`,
both callers (`beo-execute/SKILL.md:24-25`, `beo-review/SKILL.md:35-36`), and the
`beo-author` gate at `beo-author/SKILL.md:26-31`. A reader who finds `prop-*.md` reasonably
assumes the same wiring exists.

**Counterargument.** `beo_propose.py` is listed under "Optional" in
`degraded-tools.md:19`, so it may be deliberately human-facing: a human runs it
and reads the Markdown. That is coherent. It is not stated, and "optional" in
that table describes degradation of an automated path, not a human audience.

**Falsifier.** Any tracked prose naming `proposals/pending` or `prop-*.md` as
something a skill or a person reads.

---

### A4 [quarantined scaffold] Two scorers emit a number nothing consumes

**Production evidence.** `beo_score_trace.py` (339) and `beo_score_context.py`
(267) emit a 0–3 score as an optional `score` runtime event.
`context-budget.md:6` says the budget table "does not enforce —
`beo_score_context.py` is the read-side check that flags drift", and `:71`
describes the score. No skill card branches on a score. `beo-author/SKILL.md:53`
says beo-author "may invoke a scorer and re-emit under its own name", which
routes the number nowhere. `degraded-tools.md:18`: "Skip score events; no
functional impact."

**Classification.** Quarantined scaffold, not architecture defect: the bundle
states plainly that removing them changes nothing, and its own degradation table
says so. The defect is that 606 lines of shipped code carry that status
silently rather than being marked as measurement instruments for a future
decision. Proof is asymmetric too: `git ls-files 'tests/*.py' | xargs grep -l
'score_trace\|score_context'` returns `test_score_trace.py` (381 lines) plus two
incidental hits (`test_audit.py`, `test_imports.py`); no test file is dedicated to
`beo_score_context.py`.

**Falsifier.** Any skill card or registry rule that reads a `score` and changes a
route.

---

### A5 [justified divergence] Strict-mode reservation and worktree machinery is fully owned, and its concurrency premise belongs to A2

Recorded because the line counts invite the opposite conclusion.
`beo_reservation.py` (488) and `beo_worktree.py` (393) are named in
`beo-validate/SKILL.md:15-16` and `:30`, `beo-execute/SKILL.md:15` and `:21-22`,
and `beo-review/SKILL.md:12` and `:30-33`, with a complete lifecycle: create
before `PASS_EXECUTE`, resolve at execute, merge or clean up at every terminal
route. `kernel.md` §6 and §7 own the policy. These are not orphans, and the
library modules that look unreferenced in prose — `beo_io`, `beo_paths`,
`beo_state`, `beo_ticket`, `beo_approval`, none of which has a `__main__` — are
imported by the entrypoints, verified this turn by grepping the import graph. The
`fcntl` lock is coherent with the kernel rather than against it: one issue per
actor does not mean one actor. What is unowned is that a second plane in the same
checkout partitions paths without any lock, and that is A2's, not theirs.

---

### A6 [implementation drift] Two shipped executables have no test, in a repo with 4094 lines of test

**Production evidence.** `augment_prompt.py` (110) is named in
`prompt-leverage/SKILL.md`; `create_ultra_review_report.py` (203) is named in
`ultra-review/SKILL.md`. `git ls-files 'tests/*.py' | xargs grep -l
'augment_prompt\|create_ultra_review_report'` → 0 files. Eight of nine test files
cover `beo_*`; the ninth covers `gate_row`.

**Classification.** Implementation drift, low. Flagged rather than argued: the
skill that owns this question is `test-proof-debt-audit`, and running it here
would be the "second review workflow" `architecture-premise-audit/SKILL.md:21-22`
forbids. This finding is the handoff, not the audit.

---

## Counterfactual architecture

**For A1.** Two coherent routes; the repository has neither, which is the point.

*Route 1 — name it auditability.* State in `kernel.md` that the control plane
produces recomputable evidence rather than enforcing invariants, rename "Hard
Invariants" to what they are, and add to `beo-review` one step that recomputes
the prior phases' predicates from artifacts rather than trusting the recorded
result. **Machinery removed:** none. **Machinery relocated:** the enforcement
claim moves from the gate to the review step, where a different actor evaluates
it. This is the cheaper route and it is honest about the deployment.

*Route 2 — add one external invoker.* A single pre-commit hook or `br`-side check
that runs `beo_check.py` against the current issue. **Machinery removed:** none.
**Machinery added:** one invoker, plus the operational cost of a hook that can be
skipped with `--no-verify`, which reintroduces the problem one level out. Weaker
than Route 1 for that reason.

**For A2.** One tracked artifact — a `## Delivery` section in the root
`README.md`, or a repo-level `AGENTS.md` section that does not disclaim the
standalone skills — stating which plane governs which context and that the
worktree and concurrency positions are context-specific, not contradictory.
**Machinery removed:** none. **Authority simplified:** an agent gains a
discriminator it currently has to invent.

**For A3.** Either wire `prop-*.md` into `beo-author/SKILL.md` step 5 as a second
triage input, or state in `degraded-tools.md` that the output is human-facing.
**Machinery removed:** nothing yet — Phase A writes findings, not fixes.

---

## STOP_OPTIMIZING

- **The 5968-line Python surface as such.** It is not too large for what it does;
  A1 is about what makes it run, not how much of it there is. Shrinking it
  without settling A1 loses evidence and fixes nothing.
- **`beo_audit.py` C1–C9 (837 lines).** It is the consistency check the two-sided
  doctrine requires and it works. It is a symptom of A1's tax, not a candidate.
- **Merging delivery owners or `beo-setup`.** Settled 2026-09-03 at Tier 4;
  re-proposing it is out of scope here.

## PROBABLY_JUSTIFIED

- `check_skill_bundle.py` (350) — schema integrity for the bundles, one job, one
  owner, named in `degraded-tools.md` and the root `README.md`.
- `gate_row.py` (229) — derives every field of a ledger row from git rather than
  from a seat's memory. Its forcing requirement is exactly the failure mode this
  campaign keeps finding, and it is tested.
- The `harness-proposal.json` channel — wired end to end across schema, pipeline,
  phase contracts, state schema, both callers, and the author gate.
- `beo_verify.py`, `beo_check.py`, `beo_approval.py`, `beo_state.py` — load
  bearing under A1's counterargument even if A1 stands.

---

## Prioritized decisions

1. **Settle A1's framing.** Enforcement or auditability. Everything else in the
   `beo` bundle is downstream of that answer, and both routes above cost less
   than continuing to carry the ambiguity. Human decision.
2. **Write the A2 boundary statement.** One paragraph, one file. It is the
   cheapest finding here and the one an agent hits first.
3. **Disposition A3 and A4** — wire or declare. Small, mechanical, no premise
   attached.
4. **Route A6 to `test-proof-debt-audit`** if that skill is run in this campaign.

**Fitness scenarios.** *Nothing changes:* the repository keeps working, because
its actual operator is careful; the cost stays a slow doctrine-drift tax and one
selection ambiguity that surfaces the first time a new agent picks the wrong
delivery plane. *A1 resolved as auditability:* the bundle stops claiming
enforcement it cannot perform, and `beo-review` becomes the place the claim is
made good. *A1 resolved as enforcement:* one hook, and the `--no-verify` gap has
to be answered.

---

## Instrument Log (addition, not a required output section)

This run is S4 F003's disconfirming check. The check S4 named, verbatim: "does
its coverage ledger contain non-vacuous rows, and how did it resolve 'explicitly
requested' for an orchestrator-initiated invocation? Non-vacuous rows weaken this
finding materially. A zero-row or improvised ledger confirms it."

**Result: partially disconfirming.** The ledger above has 22 rows, each
traceable to a file or a command: 20 name an artifact or a command, and rows 20
and 21 record that no queue and no scheduler exist, which is a derived absence
rather than a vacancy. But every row's *category* was
supplied by step 3's nine-item list, not by step 6's five, and the four
categories step 6 omits — queues, schedulers, deployment boundaries, cited proof
— produced rows 19 through 22, including the only proof row. Row 18, the
distribution row, is categorized *external output*, which is one of step 6's own
five, so step 6 as written would have kept it; the casualties are row 19, whose
cited-proof category produced finding A6, and rows 20 through 22, whose derived
absences exist only because step 3 named those three categories. **Had this
audit terminated on step 6 as written, it would have been coverage-complete
without ever representing proof, and A6 would not exist.** That
confirms S4 F002 directly. S4 F001 is also confirmed: no step constructed this
ledger, and its existence is the coordinator's choice, not the procedure's.

Other instrument observations, recorded as found and not fixed:

- **"Explicitly requested" (S4 F003).** Resolved as: the Human's 17:40 relay
  authorized reviewing every skill in the project with ultra-review "và các skill
  liên quan", and the campaign plan schedules this run at the project boundary.
  That is a chain of two documents, not an utterance naming this skill. The
  shipped text supplies no test for the chain, so the resolution is an assumption
  and is stated as one.
- **Step 1's completion rule (S4 F012).** Authored as "every discovered ingress,
  state family, durable effect, expensive operation and external output has a
  ledger row or a stated exclusion" — which is step 6's fixed rule restated,
  because nothing downstream reads a different one. The step-1 artifact was
  therefore inert, exactly as F012 predicts.
- **Step 4's slices (S4 F008, F041).** No step produced slices. The comparison ran
  over ledger rows instead, and the promotion from "compared" to "serious
  candidate" was a coordinator judgment with no rule behind it.
- **"Hidden premise" and "tax" (S4 F016).** Both fields are filled above for A1
  and A2. Neither term is defined anywhere in the bundle; the content is invented
  per field. A second run would produce different shapes for the same findings.
- **The reference's load condition (S4 F010).** Not loaded, for the reason given
  in the coverage section. The condition's third clause — "another system with a
  suspected structural misfit" — is satisfied by any project this skill would ever
  be pointed at, so the decision not to load was made on domain fit rather than on
  the stated condition.
- **Six classifications, five verdicts, no composition rule (S4 F015).** Derived
  on this turn from the six finding headings: one architecture defect, two owner
  defects, one quarantined scaffold, one justified divergence, one implementation
  drift. The mapping to `REPAIR_FIRST`
  was chosen by the discriminator stated at the top of Verdict; the skill supplies
  none.
- **Read-only boundary (S4 F025).** Held. Nothing outside this file was written,
  and the campaign's Phase A boundary — findings, not fixes — held independently.

---

## Derivation

Every count above was derived on the turn this file was written.

**Pointer verification, mechanical, same discipline as the campaign's rounds.**
Two scripts were run over this file on this turn, and re-run after the revisions
below. The first resolved every `` `path:line` `` pointer against `git ls-files`
and checked that the file exists and the line is non-blank: **27 distinct
pointers, 32 instances, 0 failures**, after one bare pointer naming only
`SKILL.md` with the line range 26-31 was written out as
`beo-author/SKILL.md:26-31` — the same ambiguity S5 F024 records.

The second extracted every quoted string of 12 characters or more at document
level, splitting the whole file on the double-quote character and taking the odd
elements, and tested containment against the normalized text of every tracked
file plus the S4 report: **25 strings, 0 unmatched**. Two parity notes, because
both would otherwise read as failures. The file has 64 double-quote characters,
even parity, and every pair's span was measured to confirm the pairing is real
rather than shifted: no span is implausibly long. But quotes wrap across lines
here, so a per-line parity check is meaningless on this file and reports 32
false odd lines. The document-level split is the only correct form.

**One correction applied 2026-09-07, during the S4 receive pass, above the
boundary.** The Instrument Log sentence above claimed the four categories step 6
omits produced the only external-output row. That was false: row 18 is
categorized *external output*, which is one of step 6's five, so step 6 as
written keeps it. The claim overstated the loss by one category. S4 F002 still
stands and is strengthened rather than weakened, because the surviving casualty
is the cited-proof row that produced finding A6 — a finding, not a category. The
correction adds no pointer and no quoted string, so the two counts above hold
unchanged; both were re-derived after the edit.

One genuine misquote was found and fixed on the earlier run: a period appended
to the S4 F045 heading. Five further unmatched strings from that run were
adjudicated rather than changed, and the normalizer now absorbs them: one marked
elision of `README.md:3` (`…`); one rendering of S4's nested double quotes as
single quotes, confirmed present in S4 in its double-quote form by `grep -c`;
the Human's own words *"và các skill liên quan"*, which are in no tracked file
by nature; and two quotations of this report's own prose.

- Tracked files 89, skill units 17, top-level skill dirs 9: `git ls-files`.
- All line counts: `git ls-files <glob> | xargs cat | wc -l`.
- Cross-plane silence: `grep -rn -i` in both directions over `git ls-files`
  output for each bundle, 0 and 0; three files naming both, found by a per-file
  loop over `git ls-files`.
- Vocabulary overlap: `grep -ril <term>` over each bundle's tracked `.md` files.
- Exclusion rules: `git check-ignore -v` per path.
- Import graph and `__main__` presence: `grep -n` over
  `skills/beo/beo-reference/scripts/*.py`.
- Custody at write time: HEAD `038dc27b50859cb30542b91683688a1f52ce5d66`, stash
  0, porcelain 8 lines before this file was written and 9 with it, `.beads`
  absent, no `.github`.

No delivery, merge, push or deploy is authorized by this run. Phase A writes
files, not gates.
