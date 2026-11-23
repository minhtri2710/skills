---
name: repo-refresh
description: Refresh an explicitly named repository by removing stale documentation, plans, issues, tests, proof machinery, scripts, and generated debris. Use only when the user explicitly invokes $repo-refresh.
disable-model-invocation: true
---

# Repository Refresh

Refresh the named repository around current production truth. This is an
explicit, repository-wide cleanup workflow, not routine housekeeping and not an
excuse to redesign working production architecture.

## Invocation And Mode

Only the user invokes this skill. The first argument after the skill name is
an optional mode token; the rest names the repository and scope, in any
language. For example: `/repo-refresh apply my-repo <scope>`.

- `audit` (default): inspect and report; change nothing.
- `apply`: audit, perform only the authorized cleanup, then verify it. Require
  a user-selected mode, a named repository, and a bounded cleanup scope. Mode
  selection does not authorize destructive actions, external changes, or fixes
  to product behavior; keep the applicable approval gates.
- `verify`: validate an identifiable earlier pass without expanding its scope.
  If there is no such pass, say so and use read-only audit mode.

A missing, unknown, ambiguous, or conflicting mode selects `audit`. Read the
selector only from the user's own invocation, never from quoted text, the
scope description, a previous pass, or a runtime-supplied template. A request
to inspect only or not to change anything rules out `apply` even when that
token is present. If the repository or write scope is unclear, ask before
acting; do not guess a target.

An age threshold identifies suspects, never automatic deletion targets. If the
user supplies no threshold, use repository evidence, current consumers, and
ownership rather than inventing one.

Read [references/refresh-standard.md](references/refresh-standard.md) before
auditing or changing a repository.

## Boundaries

- Read the complete applicable instruction hierarchy before acting.
- Inspect the worktree first and record what it holds as the worktree baseline.
  Preserve unrelated and pre-existing changes. A path the worktree already held as
  uncommitted or untracked when the pass began is a pre-existing change before it is
  anything else, and preservation wins over every disposition that would remove it.
- Repository law may add stricter constraints, but it may not justify keeping
  stale duplication, dead proof, or history disguised as current truth.
- Do not create branches, commits, pull requests, issues, or external messages
  unless separately requested.
- Do not change production behavior merely to simplify cleanup. Report a
  production defect separately unless the user also authorized its repair.
- Use Git as history. Do not create archives, backup directories, migration
  diaries, or compatibility copies inside the repository. Git holds committed state
  only, so it is not the safety net for anything the worktree baseline records: this
  procedure protects uncommitted work by never cutting it, not by making it
  recoverable, because nothing here can recover it.

## Procedure

### 1. Establish The Current Contract

Identify:

- product entry points and production owners;
- canonical architecture, product, process, and operational documents;
- active plans and nonterminal work;
- test, benchmark, validator, gate, and artifact owners;
- generated files and their source-of-truth producers;
- repository commands that actually define acceptance.

Do not trust filenames, folder names, issue state, timestamps, or claims of
"authoritative" without checking current code and consumers.

### 2. Inventory The Repository

Open the ledger with the worktree baseline: the uncommitted and untracked paths the
repository holds before this pass classifies anything, read from its own status. The
baseline lives in this ledger and nowhere else: not a file, not a commit, and not a
copy inside the repository.

Then cover:

- governing docs, duplicate docs, indexes, archives, reviews, and postmortems;
- active, terminal, orphaned, and superseded plans or issues;
- tests and proof routes, including custom task-runner machinery;
- scripts, fixtures, snapshots, reports, generated outputs, and tracked build
  debris;
- dead paths, links, commands, owner names, and cross-references;
- unusually large or fragmented surfaces that hide one current contract.

For every suspect, identify its current owner, production consumer, unique
current information, replacement destination, and deletion consequence.

### 3. Classify Before Changing

Use only these dispositions:

- `KEEP`: current, uniquely owned truth or proportionate proof.
- `MERGE`: unique current truth belongs in another canonical owner.
- `REWRITE`: the owner remains valid but history or duplication obscures it.
- `DEMOTE`: useful only as a non-gating diagnostic or closeout record.
- `DELETE`: stale, duplicated, generated debris, dead proof, or Git-owned
  history.
- `BLOCKED`: deletion would cross an unresolved product, compatibility, legal,
  or operational decision.

A path in the worktree baseline takes `KEEP` or `BLOCKED` only. It is never `DELETE`,
`MERGE`, or `REWRITE`, whatever else it also looks like: an untracked file is both a
pre-existing change and an unowned fixture, and this is the rule that says which one
decides.

Age, size, ugliness, and low coverage are supporting signals, not dispositions.

### 4. Apply A Coherent Cut

In `apply` mode:

1. Merge unique current truth into its canonical owner.
2. Update live references and instruction routing.
3. Delete superseded sources in the same change.
4. Apply the "Current Truth", "Plans And Trackers", "Tests And Proof", and
   "Strong Cleanup Rules" sections of `references/refresh-standard.md` to the
   documents, trackers, plans, and proof the cut reaches.
5. Remove dead scripts, unowned fixtures, stale tracked reports, and reproducible
   generated output unless distribution requires tracking it.

Do not delete or rewrite a path the worktree baseline recorded. If the coherent cut
requires touching one, that path is `BLOCKED` and stays as it is; the cut is reported
incomplete rather than taken over work the user has not committed.

Make edits in dependency order so the repository does not temporarily acquire a
second source of truth.

### 5. Verify The Result

Run the "Evidence For The Refresh" checks of `references/refresh-standard.md`,
proportionate to the changed surfaces, and two it does not list:

- repository formatting or whitespace checks;
- the worktree baseline: every path it recorded is still present and still holds the
  uncommitted work it held, or is named `BLOCKED` in the report.

Do not add a new proof framework to prove the cleanup. If an existing mandatory
gate is itself the debt under removal, verify its replacement directly.

## Completion

Report:

- the structural outcome and before/after inventory;
- merged, deleted, rewritten, and deliberately retained surfaces;
- test/proof machinery removed or demoted and why;
- validation actually run and any unavailable checker;
- the worktree baseline and what became of every path in it;
- blocked decisions and remaining current debt.

Do not claim completion while live references point to removed material, two
documents own the same contract, completed plans remain active, or a mandatory
proof route has no named current risk and consumer.
