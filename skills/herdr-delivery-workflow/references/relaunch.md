# Relaunch recovery

A Lead or Supervisor seat recovering from compaction or relaunch reads this before acting.

For predecessor retirement and unsent feedback prompts, follow `supervisor.md`, "Handoff".

Run this checklist in order:

1. Before parity, identify the skill publisher's repo and deployment ledger from relaunch evidence, separately from the consuming project's repo and gate ledger. Run `scripts/gate_row.py --deployed-head <skill> --ledger <publisher-ledger> --repo <publisher-repo>`; full-chain validation prints `<branch>@<full SHA>` and the deploy row. Record inputs and outputs; use that SHA as `deployed_head`. Missing publisher evidence is actionable unproven: stop and name it to the Human. Never use consumer inputs, infer or universally discover an owner, or fall back to checkout `HEAD`, prose, older row, or sample.
2. Compare installed files with that head: enumerate `git ls-tree`, hash files with `git hash-object`, compare `git rev-parse "${deployed_head}:<path>"` (braced for zsh). Later steps use that text.
3. If the relaunch names a NEXT item or next scope, quote that line verbatim from a named staffing/backlog NEXT section or `scripts/slices_ready.py` output, include that source file path in the Lead's pane and the run's workspace record, and confirm it with `scripts/relaunch_entry_check.py --verify --block-file <next-item-block> --source-file <named-source>`; the quote must carry its gate ids and must never be reconstructed from memory.
4. Run `scripts/relaunch_entry_check.py --count --repo <publisher-repo> --ledger <publisher-ledger> --skill <skill> --skill-path <repo-relative-path> --installed-path <installed-path>`. It checks chain, latest target row, parity; refusal stops without fallback.
5. Reconcile pushes, merges, and PR mutations in the consumer repo/ledger with `scripts/gate_row.py --repo <consumer-repo> --ledger <consumer-ledger>`; reconstruct events with `--record reconstruction --head <branch>@<exact full 40-hex SHA>` and source. Only `deploy_skill.py` records deploys after install verification. First-publication ranges: `lead.md`, "Review and push coverage". Check after each row.
6. Unconditionally record `scripts/gate_row.py`'s resolved path and a real `gate_row.py --check` on the consumer ledger, naming the row, even if no rows were reconstructed. A failed check means the row is absent or invalid; redo it through `scripts/gate_row.py`, never by hand.
7. Re-establish current branch, full `HEAD`, porcelain, and stash list.
8. For a Supervisor seat, read the newly appended mailbox entries as `supervisor.md`, "What the Supervisor sees", sets, from the recorded `last-read` mark.
9. Reconcile live Peers and owed reports with `scripts/roster.py`, then run its `--drift` check against the project config for every staffed Peer (`herdr-cli.md`, "Start and drive an agent"); carry each `DRIFT` or `UNVERIFIABLE` line, or refusal, into the step-10 record.
10. Last, print the reconciled `HEAD`, branch, open gates, and owed reports, with the facts steps 3, 6, and 9 produced, in the Lead's pane and write them to the run's workspace record. Append no mailbox entry. For the cause or content of an older decision, beyond the state reconciled above, follow `herdr-cli.md`, “Recall past records”, not run directories. If the seat cannot continue safely, report `BLOCKED` to the Human with preserved custody evidence, not a fresh delivery. Otherwise a Lead does not stop here: the NEXT step 3 confirmed opens in this turn, or the turn ends as `lead.md`, “Awaited work” says.
