#!/usr/bin/env python3
"""Unit tests for gate_row.py (C19 — the ledger row is derived, not typed)."""
from __future__ import annotations

import contextlib
import hashlib
import io
import os
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest import mock
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import gate_row  # noqa: E402


def make_repo(tmp: Path) -> Path:
    repo = tmp / "repo"
    repo.mkdir()
    run = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True,
                                    capture_output=True, text=True, stdin=subprocess.DEVNULL)
    run("init", "-q", "-b", "main")
    run("config", "user.email", "t@example.invalid")
    run("config", "user.name", "t")
    for n in range(3):
        (repo / f"f{n}.txt").write_text(f"{n}\n")
        run("add", "-A")
        run("commit", "-qm", f"c{n}")
    return repo


class GateRowTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=os.path.realpath("/tmp"))
        self.tmp = Path(self._tmp.name)
        self.repo = make_repo(self.tmp)
        self.ledger = self.tmp / "gates.md"
        self.ledger.write_text("# Gate ledger — test\n\n")
        self.addCleanup(self._tmp.cleanup)

    def run_main(self, argv: list[str]) -> int:
        """Run the CLI with its stdout and stderr captured, so a test run stays readable.

        stderr is kept on `self.err`: a refusal that exits 1 for the wrong reason
        is still a passing exit code, so the message is part of the assertion.
        """
        self.err = io.StringIO()
        self.out = io.StringIO()
        with contextlib.redirect_stdout(self.out), contextlib.redirect_stderr(self.err):
            return gate_row.main(argv)

    def append(self, *extra: str) -> int:
        return self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "merge", "--status", "resolved:human",
            "--words", "human", "--note", "merged the reviewed head", "--quote", "merge it", *extra,
        ])

    def append_repair_grant(self, finding: str = "F-1", quote: str = "repair grant") -> int:
        return self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "repair-grant", "--status", "recorded:granted",
            "--finding", finding, "--words", "selected", "--note", "repair grant",
            "--quote", quote,
        ])

    def append_review_pass(self, base: str | None = None) -> int:
        return self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "review", "--status", "recorded:review-pass",
            "--review-base", base or self.rev("HEAD~2"),
            "--words", "seat", "--note", "review passed", "--quote", "PASS",
        ])

    def append_review_fail(self, base: str | None = None) -> int:
        return self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "review", "--status", "recorded:review-fail",
            "--review-base", base or self.rev("HEAD~2"),
            "--words", "seat", "--note", "review failed", "--quote", "FAIL",
        ])

    def append_correction(self, target: str, *extra: str) -> int:
        return self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "correction", "--status", "recorded:correction",
            "--void", target, "--words", "seat", "--note", "verdict corrected",
            "--quote", "correction recorded", *extra,
        ])

    def append_local_ops(self, *extra: str) -> int:
        return self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "local-ops", "--status", "recorded:local-ops",
            "--op", "git status --short", "--after", f"main@{self.rev('HEAD')}",
            "--words", "seat", "--note", "ran the named local operation",
            "--quote", "git status --short", *extra,
        ])

    def append_standing_delegation(self, *extra: str) -> int:
        return self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "standing-delegation", "--status", "recorded:standing-delegation",
            "--who", "lead-beo-skills", "--scope", "scripts only",
            "--conditions", "after review", "--expiry", "until the Human's next message",
            "--words", "human", "--note", "delegation recorded",
            "--quote", "I grant this delegation | verbatim", *extra,
        ])

    def append_handoff(self, *extra: str) -> int:
        return self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "handoff", "--status", "recorded:handoff",
            "--words", "seat", "--note", "delivery accepted at reviewed head",
            "--quote", "accepted", *extra,
        ])

    def git(self, *args: str) -> str:
        return subprocess.run(["git", "-C", str(self.repo), *args],
                              capture_output=True, text=True, check=True, stdin=subprocess.DEVNULL).stdout.strip()

    def rev(self, ref: str) -> str:
        return subprocess.run(["git", "-C", str(self.repo), "rev-parse", ref],
                              capture_output=True, text=True, check=True, stdin=subprocess.DEVNULL).stdout.strip()

    def last_row(self) -> str:
        return [l for l in self.ledger.read_text().splitlines()
                if gate_row.ID_RE.match(l)][-1]

    def test_relative_ledger_is_refused_and_writes_nothing(self):
        import os
        scratch = self.tmp / "cwd"
        scratch.mkdir()
        prev = os.getcwd()
        os.chdir(scratch)
        try:
            rc = self.run_main([
                "--ledger", "gates.md", "--repo", str(self.repo),
                "--kind", "merge", "--status", "resolved:human",
                "--words", "human", "--note", "n", "--quote", "q",
            ])
        finally:
            os.chdir(prev)
        self.assertEqual(rc, 1)
        self.assertIn("not absolute", self.err.getvalue())
        self.assertFalse((scratch / "gates.md").exists())

    def fixture_row(self, gid: str, status: str, words: str = "human",
                    quote: str = "fixture", resolves: str | None = None,
                    note: str = "fixture", kind: str = "merge") -> str:
        target = f" | resolves={resolves}" if resolves else ""
        return (f"{gid} | 2026-09-06T00:00:00Z | kind={kind} | "
                f"main@{self.rev('HEAD')} | status={status} | record=timely"
                f"{target} | words={words} | note={note} | quote=\"{quote}\"")

    def chained(self, rows: list[str]) -> list[str]:
        out = rows[:1]
        for row in rows[1:]:
            out.append(row.replace(" | words=", f" | prev_hash={gate_row.row_hash(out[-1])} | words=", 1))
        return out

    def open_gates(self) -> list[str]:
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--open-gates",
        ]), 0, self.err.getvalue())
        return self.out.getvalue().splitlines()

    def test_words_is_required_for_append(self):
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "merge", "--status", "resolved:human",
            "--note", "merged the reviewed head", "--quote", "merge it",
        ]), 1)
        self.assertIn("--words is required", self.err.getvalue())
        self.assertEqual(self.ledger.read_text(), "# Gate ledger — test\n\n")

    def test_dialog_channel_requires_selected_words_on_append_and_check(self):
        before = self.ledger.read_text()
        self.assertEqual(self.append(
            "--status", "open", "--channel", "supervisor-relay:dialog",
            "--words", "human", "--quote", "human",
        ), 1)
        self.assertIn("channel=supervisor-relay:dialog", self.err.getvalue())
        self.assertIn("words=selected", self.err.getvalue())
        self.assertEqual(self.ledger.read_text(), before)

        self.assertEqual(self.append(
            "--status", "open", "--channel", "supervisor-relay:dialog",
            "--words", "selected", "--quote", "selected",
        ), 0)
        row = self.last_row().replace(
            "words=selected", "words=human"
        ).replace('quote="selected"', 'quote="human"')
        self.ledger.write_text(row + "\n", encoding="utf-8")
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 1)
        self.assertIn("channel=supervisor-relay:dialog", self.err.getvalue())
        self.assertIn("words=selected", self.err.getvalue())

    def test_typed_human_and_dialog_selected_rows_are_accepted(self):
        self.assertEqual(self.append(
            "--status", "open", "--channel", "supervisor-relay:dialog",
            "--words", "selected", "--quote", "selected",
        ), 0)
        self.assertEqual(self.append(
            "--status", "open", "--channel", "supervisor-relay:typed",
            "--words", "human", "--quote", "human",
        ), 0)
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 0)

    def test_seat_permission_denial_requires_system_words_shape_on_append_and_check(self):
        before = self.ledger.read_text()
        self.assertEqual(self.append(
            "--kind", "merge-gate", "--status", "open",
            "--words", "human", "--quote", "human",
            "--note", "blocked:seat-permission",
        ), 1)
        self.assertIn("blocked:seat-permission", self.err.getvalue())
        self.assertIn("words=none", self.err.getvalue())
        self.assertEqual(self.ledger.read_text(), before)

        self.assertEqual(self.append(
            "--kind", "merge-gate", "--status", "open",
            "--words", "none", "--quote", "",
            "--note", "blocked:seat-permission",
        ), 0)
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 0)

        valid = self.fixture_row(
            "G1", "open", words="none", quote="", note="blocked:seat-permission",
            kind="merge-gate",
        )
        self.ledger.write_text(valid + "\n", encoding="utf-8")
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 0)

        invalid = self.fixture_row(
            "G1", "open", words="seat", quote="classifier denial",
            note="blocked:seat-permission", kind="merge-gate",
        )
        self.ledger.write_text(invalid + "\n", encoding="utf-8")
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 1)
        self.assertIn("blocked:seat-permission", self.err.getvalue())
        self.assertIn("words=none", self.err.getvalue())

    def test_open_human_gate_requires_opt_in_mailbox_attention(self):
        row = self.fixture_row("G1", "open", words="none", quote="", kind="merge")
        self.ledger.write_text(row + "\n", encoding="utf-8")
        mailbox = self.tmp / "supervisor-mailbox.md"

        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 0)
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
            "--mailbox", str(mailbox),
        ]), 1)
        self.assertIn("could not be read", self.err.getvalue())

        head = self.rev("HEAD")
        mailbox.write_text(
            "## lead-beo-skills -> supervisor | 2026-09-13T00:00:00Z | "
            f"ATTENTION project human gate G1 | HEAD {head}\n",
            encoding="utf-8",
        )
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
            "--mailbox", str(mailbox),
        ]), 0)

        mailbox.write_text(
            "## lead-beo-skills -> supervisor | 2026-09-13T00:00:00Z | "
            f"ATTENTION project human gate {head} | HEAD {head}\n",
            encoding="utf-8",
        )
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
            "--mailbox", str(mailbox),
        ]), 0)

        mailbox.write_text(
            "## lead-beo-skills -> supervisor | 2026-09-13T00:00:00Z | "
            f"ATTENTION project human gate G10 | HEAD {head}\n",
            encoding="utf-8",
        )
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
            "--mailbox", str(mailbox),
        ]), 1)
        self.assertIn("G1", self.err.getvalue())

        for shape, entry in (
            ("answer header", f"## lead-beo-skills -> supervisor | 2026-09-13T00:00:00Z | human gate G1 | HEAD {head}"),
            ("minute timestamp", f"## lead-beo-skills -> supervisor | 2026-09-13T00:00Z | ATTENTION project human gate G1 | HEAD {head}"),
            ("another seat", f"## lead-beo-skills -> lead-other | 2026-09-13T00:00:00Z | ATTENTION project human gate G1 | HEAD {head}"),
            ("body line", f"ATTENTION project human gate G1 | HEAD {head}"),
        ):
            with self.subTest(shape):
                mailbox.write_text(entry + "\n", encoding="utf-8")
                self.assertEqual(self.run_main([
                    "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
                    "--mailbox", str(mailbox),
                ]), 1)
                self.assertIn("no matching ATTENTION entry", self.err.getvalue())

    def test_backdated_last_row_fails_check_with_timestamp_regression(self):
        self.assertEqual(self.append(), 0)
        existing_rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        args = SimpleNamespace(
            kind="merge", status="resolved:test", channel="", writer="", record="timely", head="",
            push_base="", review_base="", boundary=[], resolves=[], words="human", note="backdated",
            quote="backdated", quote_file="",
        )
        with mock.patch.object(gate_row, "datetime") as clock:
            clock.now.return_value = datetime(2000, 1, 1, tzinfo=timezone.utc)
            backdated = gate_row.build(args, self.repo, gate_row.LedgerState.of(existing_rows))
        self.ledger.write_text(
            self.ledger.read_text(encoding="utf-8") + backdated + "\n", encoding="utf-8"
        )
        self.assertEqual(self.run_main(
            ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]), 1)
        self.assertIn("timestamp regression", self.err.getvalue())
        self.assertIn("2000-01-01T00:00:00Z", self.err.getvalue())

    def test_repair_cap_rejects_repeated_finding_since_boundary(self):
        self.assertEqual(self.append_repair_grant("F-1"), 0)
        self.assertEqual(self.append_repair_grant("F-2"), 0)
        self.assertEqual(self.append_repair_grant("F-1"), 1)
        self.assertIn("repair cap", self.err.getvalue())
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        duplicate = self.last_row().replace("G2", "G3").replace("finding=F-2", "finding=F-1")
        duplicate = duplicate.replace(
            f"prev_hash={hashlib.sha256(rows[0].encode('utf-8')).hexdigest()}",
            f"prev_hash={hashlib.sha256(rows[1].encode('utf-8')).hexdigest()}",
        )
        self.ledger.write_text(self.ledger.read_text(encoding="utf-8") + duplicate + "\n", encoding="utf-8")
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 1)
        self.assertIn("repair cap", self.err.getvalue())

    def test_progress_boundary_resets_repair_grant_cap(self):
        self.assertEqual(self.append_repair_grant("F-1"), 0)
        self.assertEqual(self.append_review_pass(), 0)
        self.assertEqual(self.append_repair_grant("F-1"), 0)
        self.assertEqual(self.append_repair_grant("F-2"), 0)
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 0)

    def test_non_boundary_row_does_not_reset_repair_grant_cap(self):
        self.assertEqual(self.append_repair_grant("F-1"), 0)
        self.assertEqual(self.append_review_fail(), 0)
        self.assertEqual(self.append_repair_grant("F-2"), 0)
        self.assertEqual(self.append_repair_grant("F-1"), 1)
        self.assertIn("repair cap", self.err.getvalue())

    def test_distinct_findings_are_progress_and_are_allowed(self):
        self.assertEqual(self.append_repair_grant("F-1", "round 3"), 0)
        self.assertEqual(self.append_repair_grant("F-2", "round 4"), 0)
        self.assertEqual(self.append_repair_grant("F-3", "third grant"), 0)
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 0)
        self.assertIn("finding=F-3", self.last_row())

    def test_repair_grant_requires_finding_identity(self):
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "repair-grant", "--status", "recorded:granted",
            "--words", "selected", "--note", "repair grant", "--quote", "grant",
        ]), 1)
        self.assertIn("requires finding= field", self.err.getvalue())

    def test_local_ops_append_readback_rederive_and_check(self):
        self.assertEqual(self.append(), 0)
        self.assertEqual(self.append_local_ops(), 0)
        row = self.last_row()
        self.assertIn("kind=local-ops", row)
        self.assertIn("status=recorded:local-ops", row)
        self.assertIn("op=git status --short", row)
        self.assertIn(f"after=main@{self.rev('HEAD')}", row)
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 0)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        self.ledger.write_text(
            "# Gate ledger — test\n\n" + "\n".join([
                rows[0], row.replace(" | op=git status --short", "")
            ]) + "\n", encoding="utf-8"
        )
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 1)
        self.assertIn("requires op= field", self.err.getvalue())

    def test_local_ops_requires_its_structured_fields(self):
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "local-ops", "--status", "recorded:local-ops",
            "--after", f"main@{self.rev('HEAD')}", "--words", "seat",
            "--note", "ran the named local operation", "--quote", "git status --short",
        ]), 1)
        self.assertIn("requires op= field", self.err.getvalue())

    def test_standing_delegation_append_readback_rederive_and_check(self):
        self.assertEqual(self.append_standing_delegation(), 0)
        self.assertEqual(self.append_standing_delegation(), 0)
        row = self.last_row()
        self.assertIn("kind=standing-delegation", row)
        for field in ("who=lead-beo-skills", "scope=scripts only",
                      "conditions=after review", "expiry=until the Human's next message"):
            self.assertIn(field, row)
        self.assertTrue(row.endswith('quote="I grant this delegation | verbatim"'))
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 0)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        self.ledger.write_text(
            "# Gate ledger — test\n\n" + "\n".join([
                rows[0], rows[1].replace(" | expiry=until the Human's next message", "")
            ]) + "\n", encoding="utf-8"
        )
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 1)
        self.assertIn("requires expiry= field", self.err.getvalue())

    def test_standing_delegation_requires_its_structured_fields(self):
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "standing-delegation", "--status", "recorded:standing-delegation",
            "--who", "lead-beo-skills", "--scope", "scripts only",
            "--conditions", "after review", "--words", "human",
            "--note", "delegation recorded", "--quote", "I grant this delegation",
        ]), 1)
        self.assertIn("requires expiry= field", self.err.getvalue())

    def test_standing_delegation_accepts_a_dialog_selected_option_quote(self):
        self.assertEqual(self.append_standing_delegation(
            "--channel", "supervisor-relay:dialog", "--words", "selected",
            "--quote", "Yes, delegate it",
        ), 0, self.err.getvalue())
        row = self.last_row()
        self.assertIn("words=selected", row)
        self.assertIn("channel=supervisor-relay:dialog", row)
        self.assertEqual(self.check_last(), 0, self.err.getvalue())

    def test_under_names_an_in_force_delegation_and_records_the_seats_words(self):
        merge = ["--ledger", str(self.ledger), "--repo", str(self.repo), "--kind", "merge",
                 "--status", "resolved:standing-delegation", "--note", "merged under delegation",
                 "--quote", "merged PR#1 at the reviewed head"]
        self.assertEqual(self.append_standing_delegation(), 0, self.err.getvalue())
        self.assertEqual(self.run_main([*merge, "--under", "G1"]), 0, self.err.getvalue())
        self.assertIn("| under=G1 | prev_hash=", self.last_row())
        self.assertIn('words=seat | note=merged under delegation | quote="merged PR#1', self.last_row())
        self.assertEqual(self.check_last(), 0, self.err.getvalue())
        self.assertEqual(self.append_standing_delegation("--expiry", "2020-01-01T00:00:00Z"), 0)
        self.assertEqual(self.append_standing_delegation("--resolves", "G1"), 0, self.err.getvalue())
        for extra, message in (
            (["--under", "G2"], "under=G2 is not an earlier kind=standing-delegation row"),
            (["--under", "G3"], "under=G3 refused: the delegation expired at 2020-01-01T00:00:00Z"),
            (["--under", "G1"], "under=G1 refused: the delegation is revoked"),
            (["--under", "G4", "--words", "human"], "requires words=seat"),
        ):
            with self.subTest(extra=extra):
                before = self.ledger.read_bytes()
                self.assertEqual(self.run_main([*merge, *extra]), 1)
                self.assertIn(message, self.err.getvalue())
                self.assertEqual(self.ledger.read_bytes(), before)

    def test_standing_delegation_rejects_words_outside_human_and_selected(self):
        before = self.ledger.read_bytes()
        self.assertEqual(self.append_standing_delegation("--words", "seat"), 1)
        self.assertIn("requires words=human or words=selected", self.err.getvalue())
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_check_refuses_a_standing_delegation_written_with_seat_words(self):
        self.assertEqual(self.append_standing_delegation(), 0, self.err.getvalue())
        row = self.last_row().replace("words=human", "words=seat")
        self.ledger.write_text(row + "\n", encoding="utf-8")
        self.assertEqual(self.check_last(), 1)
        self.assertIn("requires words=human or words=selected", self.err.getvalue())

    def test_dialog_selected_standing_delegation_refuses_an_empty_quote_on_append(self):
        before = self.ledger.read_bytes()
        self.assertEqual(self.append_standing_delegation(
            "--channel", "supervisor-relay:dialog", "--words", "selected", "--quote", "",
        ), 1)
        self.assertIn("words=none iff quote= is empty", self.err.getvalue())
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_dialog_selected_standing_delegation_tamper_is_refused_on_check(self):
        self.assertEqual(self.append_standing_delegation(
            "--channel", "supervisor-relay:dialog", "--words", "selected",
            "--quote", "Yes, delegate it",
        ), 0, self.err.getvalue())
        selected = self.last_row()
        for tampered, message in (
            (selected.replace('quote="Yes, delegate it"', 'quote=""'), "words=none iff quote= is empty"),
            (selected.replace("words=selected", "words=human"),
             "channel=supervisor-relay:dialog requires words=selected"),
        ):
            with self.subTest(message=message):
                self.ledger.write_text(tampered + "\n", encoding="utf-8")
                self.assertEqual(self.check_last(), 1)
                self.assertIn(message, self.err.getvalue())

    def test_validation_checks_each_row_once_against_the_state_its_predecessors_leave(self):
        rows = self.chained([self.fixture_row(f"G{n}", "resolved:human") for n in range(1, 6)])
        seen: list[int] = []
        real_check = gate_row.check

        def spy(row, repo, state=None):
            seen.append(len(state.rows))
            return real_check(row, repo, state)

        with mock.patch.object(gate_row, "check", side_effect=spy):
            state = gate_row.validate_ledger(rows, self.repo)
        self.assertEqual(seen, [0, 1, 2, 3, 4])
        self.assertEqual(state.rows, rows)

    def test_validation_asks_git_once_for_a_head_shared_by_every_row(self):
        rows = self.chained([self.fixture_row(f"G{n}", "resolved:human") for n in range(1, 31)])
        with mock.patch.object(gate_row.subprocess, "run", wraps=gate_row.subprocess.run) as run:
            gate_row.validate_ledger(rows, self.repo)
        self.assertEqual(run.call_count, 1)

    def test_validation_resolves_every_distinct_head_in_one_cat_file_batch(self):
        for n in range(30):
            subprocess.run(["git", "-C", str(self.repo), "commit", "--allow-empty", "-qm", f"e{n}"],
                           check=True, capture_output=True, stdin=subprocess.DEVNULL)
        heads = [self.rev(f"HEAD~{n}") for n in range(30)]
        rows = self.chained([
            self.fixture_row(f"G{n}", "resolved:human").replace(f"main@{self.rev('HEAD')}", f"main@{head}")
            for n, head in enumerate(heads, 1)
        ])
        with mock.patch.object(gate_row.subprocess, "run", wraps=gate_row.subprocess.run) as run:
            gate_row.validate_ledger(rows, self.repo)
        git_verbs = [call.args[0][3] for call in run.call_args_list]
        self.assertEqual(git_verbs.count("cat-file"), 1)
        self.assertEqual(git_verbs.count("rev-parse"), 0)

    def test_a_push_range_reads_its_commits_through_one_diff_tree_call(self):
        with mock.patch.object(gate_row.subprocess, "run", wraps=gate_row.subprocess.run) as run:
            gate_row.derive_push(self.repo, self.rev("HEAD~2"), self.rev("HEAD"), ["."])
        git_verbs = [call.args[0][3] for call in run.call_args_list]
        self.assertEqual(git_verbs.count("diff-tree"), 1)

    def check_last(self) -> int:
        return self.run_main(["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"])

    def test_strict_ledger_check_rejects_pre_void_correction_under_current_contract(self):
        rows = [
            self.fixture_row("G1", "resolved:done", kind="merge"),
            self.fixture_row("G2", "recorded:correction", kind="correction"),
            self.fixture_row("G3", "recorded:handoff", kind="handoff"),
        ]
        self.ledger.write_text(
            "# Gate ledger — disposable historical-contract fixture\n\n"
            + "\n".join(self.chained(rows)) + "\n",
            encoding="utf-8",
        )
        code = self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ])
        self.assertEqual(code, 1)
        self.assertEqual(
            self.err.getvalue(),
            "gate_row: kind=correction requires exactly one void= field after resolves=\n",
        )

    def test_a_standing_delegation_is_revoked_once_by_a_resolving_row(self):
        self.assertEqual(self.append_standing_delegation(), 0)
        self.assertEqual(self.append("--resolves", "G1"), 0, self.err.getvalue())
        self.assertEqual(self.check_last(), 0, self.err.getvalue())
        self.assertEqual(self.append("--resolves", "G1"), 1)
        self.assertIn("already-revoked", self.err.getvalue())

    def test_handoff_append_readback_rederive_and_check(self):
        self.assertEqual(self.append_handoff(), 0)
        row = self.last_row()
        self.assertIn("kind=handoff", row)
        self.assertIn("status=recorded:handoff", row)
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 0)
        self.ledger.write_text(
            row.replace("status=recorded:handoff", "status=recorded:done") + "\n",
            encoding="utf-8",
        )
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 1)
        self.assertIn("kind=handoff requires status=recorded:handoff", self.err.getvalue())

    def test_handoff_requires_its_status(self):
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "handoff", "--status", "recorded:done",
            "--words", "seat", "--note", "delivery accepted", "--quote", "accepted",
        ]), 1)
        self.assertIn("kind=handoff requires status=recorded:handoff", self.err.getvalue())

    def test_quote_file_becomes_quote_and_round_trips(self):
        quote_file = self.tmp / "refused-command.txt"
        quote = "runtime denied command | --flag"
        quote_file.write_text(quote, encoding="utf-8")
        argv = [
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "merge", "--status", "resolved:human",
            "--words", "human", "--note", "merged the reviewed head",
            "--quote-file", str(quote_file),
        ]
        self.assertEqual(self.run_main(argv), 0)
        self.assertTrue(self.last_row().endswith(f'quote="{quote}"'))
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 0)

    def test_quote_file_strips_one_trailing_newline(self):
        quote_file = self.tmp / "refused-command.txt"
        quote_file.write_text("runtime denied command\n", encoding="utf-8")
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "merge", "--status", "resolved:human",
            "--words", "human", "--note", "merged the reviewed head",
            "--quote-file", str(quote_file),
        ]), 0)
        self.assertTrue(self.last_row().endswith('quote="runtime denied command"'))

    def test_quote_and_quote_file_are_mutually_exclusive(self):
        quote_file = self.tmp / "refused-command.txt"
        quote_file.write_text("file quote", encoding="utf-8")
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "merge", "--status", "resolved:human",
            "--words", "human", "--note", "merged the reviewed head",
            "--quote", "argument quote", "--quote-file", str(quote_file),
        ]), 1)
        self.assertIn("--quote", self.err.getvalue())
        self.assertIn("--quote-file", self.err.getvalue())

    def test_empty_quote_file_requires_words_none(self):
        quote_file = self.tmp / "empty.txt"
        quote_file.write_text("", encoding="utf-8")
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "merge", "--status", "resolved:human",
            "--words", "human", "--note", "merged the reviewed head",
            "--quote-file", str(quote_file),
        ]), 1)
        self.assertIn("words=none", self.err.getvalue())

    def test_empty_quote_file_with_none_and_open_lands(self):
        quote_file = self.tmp / "empty.txt"
        quote_file.write_text("", encoding="utf-8")
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "merge", "--status", "open", "--words", "none",
            "--note", "awaiting review", "--quote-file", str(quote_file),
        ]), 0)
        self.assertIn("status=open", self.last_row())
        self.assertTrue(self.last_row().endswith('quote=""'))

    def test_open_gates_refuses_quote_file_as_an_append_argument(self):
        missing = self.tmp / "not-read.txt"
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--open-gates", "--quote-file", str(missing),
        ]), 1)
        self.assertIn("--open-gates cannot be combined with append arguments", self.err.getvalue())
        self.assertNotIn("could not be read", self.err.getvalue())

    def test_resolves_refuses_never_open_and_already_closed_ids_and_accepts_open_id(self):
        self.assertEqual(self.append("--resolves", "G404"), 1)
        self.assertIn("G404", self.err.getvalue())
        self.assertIn("never-open", self.err.getvalue())

        self.assertEqual(self.append("--status", "open", "--words", "none", "--quote", ""), 0)
        self.assertEqual(self.append("--resolves", "G1"), 0)
        self.assertIn("resolves=G1", self.last_row())
        self.assertEqual(self.append("--resolves", "G1"), 1)
        self.assertIn("G1", self.err.getvalue())
        self.assertIn("already-closed", self.err.getvalue())
        legacy = self.fixture_row("G1", "resolved:done")
        self.ledger.write_text(legacy + "\n", encoding="utf-8")
        self.assertEqual(self.open_gates(), [])

        self.assertEqual(self.append_review_pass(), 0)
        review_id = self.last_row().split(" | ")[0]
        self.assertEqual(self.append_correction(review_id), 0, self.err.getvalue())
        self.assertIn(f" | void={review_id} | ", self.last_row())
        self.assertEqual(self.check_last(), 0, self.err.getvalue())
        self.assertEqual(self.append_correction(review_id), 1)
        self.assertIn("already voided", self.err.getvalue())
        self.assertEqual(self.append_correction("G404"), 1)
        self.assertIn("not an earlier row of this ledger", self.err.getvalue())
        self.ledger.write_text(self.fixture_row("G1", "open", kind="merge") + "\n",
                               encoding="utf-8")
        self.assertEqual(self.append_correction("G1"), 1)
        self.assertIn("target must be a kind=review", self.err.getvalue())

        for args, reason in (
            (("--kind", "correction", "--status", "recorded:wrong", "--void", review_id),
             "requires status=recorded:correction"),
            (("--kind", "correction", "--status", "recorded:correction"), "requires --void"),
            (("--kind", "correction", "--status", "recorded:correction",
              "--void", review_id, "--void", review_id), "exactly one --void"),
            (("--void", review_id), "only meaningful on kind=correction"),
        ):
            self.assertEqual(self.append(*args), 1)
            self.assertIn(reason, self.err.getvalue())

        prior = self.fixture_row("G1", "open", kind="merge")
        bad_rows = [
            (self.fixture_row("G2", "recorded:correction", kind="merge").replace(
                " | words=", " | void=G1 | words=", 1), "only on a kind=correction"),
            (self.fixture_row("G2", "recorded:wrong", kind="correction").replace(
                " | words=", " | void=G1 | words=", 1), "requires status=recorded:correction"),
            (self.fixture_row("G2", "recorded:correction", kind="correction"), "requires exactly one void="),
            (self.fixture_row("G2", "recorded:correction", kind="correction").replace(
                " | words=", " | void=G1 | words=", 1), "target must be a kind=review"),
            (self.fixture_row("G2", "recorded:correction", kind="correction").replace(
                " | words=", " | void=G404 | words=", 1), "not an earlier row of this ledger"),
            (self.fixture_row("G2", "recorded:correction", kind="correction").replace(
                " | words=", " | void=G1 | void=G1 | words=", 1), "more than one void="),
        ]
        for row, reason in bad_rows:
            row = row.replace(" | words=", f" | prev_hash={gate_row.row_hash(prior)} | words=", 1)
            with self.subTest(reason=reason), self.assertRaisesRegex(gate_row.RowError, re.escape(reason)):
                gate_row.check(row, self.repo, gate_row.LedgerState.of([prior]))

        failed_review = self.fixture_row("G1", "recorded:review-fail", kind="review")
        voided_failed_review = self.fixture_row(
            "G2", "recorded:correction", kind="correction"
        ).replace(" | words=", " | void=G1 | words=", 1)
        voided_failed_review = voided_failed_review.replace(
            " | words=", f" | prev_hash={gate_row.row_hash(failed_review)} | words=", 1
        )
        with self.assertRaisesRegex(
            gate_row.RowError, "target must be a kind=review status=recorded:review-pass"
        ):
            gate_row.check(voided_failed_review, self.repo, gate_row.LedgerState.of([failed_review]))

        review = self.fixture_row("G1", "recorded:review-pass", kind="review")
        first = self.fixture_row("G2", "recorded:correction", kind="correction").replace(
            " | words=", " | void=G1 | words=", 1
        ).replace(" | words=", f" | prev_hash={gate_row.row_hash(review)} | words=", 1)
        repeated = self.fixture_row("G3", "recorded:correction", kind="correction").replace(
            " | words=", " | void=G1 | words=", 1
        ).replace(" | words=", f" | prev_hash={gate_row.row_hash(first)} | words=", 1)
        with self.assertRaisesRegex(gate_row.RowError, "already voided"):
            gate_row.check(repeated, self.repo, gate_row.LedgerState.of([review, first]))

    def test_open_gate_mode_uses_last_rows_and_structured_resolves_only(self):
        rows = [
            self.fixture_row("G26", "open", "none", ""),
            self.fixture_row("G27", "open", "none", "", note="prose says resolves=G27"),
            self.fixture_row("G28", "open", "none", ""),
            self.fixture_row("G29", "resolved:done", resolves="G28"),
            self.fixture_row("G30", "open", "none", ""),
            self.fixture_row("G31", "resolved:done"),
        ]
        self.ledger.write_text("# fixture\n" + "\n".join(self.chained(rows)) + "\n")
        self.assertEqual(self.open_gates(), ["G26", "G27", "G30"])

    def test_words_values_require_the_matching_quote_presence(self):
        self.assertEqual(self.append("--status", "open", "--words", "none", "--quote", ""), 0)
        for words in ("seat", "human", "selected"):
            self.assertEqual(self.append("--words", words, "--quote", words), 0)
        self.assertEqual(self.append("--words", "none", "--quote", "not empty"), 1)
        self.assertIn("words=none", self.err.getvalue())
        self.assertEqual(self.append("--words", "seat", "--quote", ""), 1)
        self.assertIn("words=none", self.err.getvalue())

    def test_a_count_that_does_not_match_the_range_is_rejected(self):
        base, head = self.rev("HEAD~2"), self.rev("HEAD")
        row = (f'G2 | 2026-09-06T00:00:00Z | kind=push | main@{head} | '
               f'status=resolved:human | record=timely | '
               f'push={base}..{head} count=7 boundary="f1.txt f2.txt" '
               f'boundary-check="" | words=human | note=n | quote="q"')
        prior = self.fixture_row("G1", "recorded:review-pass", kind="review")
        with self.assertRaises(gate_row.RowError) as ctx:
            gate_row.check(self.chained([prior, row])[1], self.repo, gate_row.LedgerState.of([prior]))
        self.assertIn("carries 2 commits", str(ctx.exception))

    def test_a_failed_check_never_writes_a_row(self):
        before = self.ledger.read_bytes()
        with mock.patch.object(gate_row, "check", side_effect=gate_row.RowError("synthetic check failure")):
            self.assertEqual(self.append(), 1)
        self.assertIn("synthetic check failure", self.err.getvalue())
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_explicit_head_requires_full_sha_and_reconstruction_for_a_past_head(self):
        current = self.rev("HEAD")
        past = self.rev("HEAD~1")
        self.assertEqual(self.append("--head", f"main@{past}"), 1)
        self.assertIn("--record reconstruction", self.err.getvalue())
        self.assertEqual(self.append("--head", f"main@{past[:7]}"), 1)
        self.assertIn("full 40-hex", self.err.getvalue())
        self.assertEqual(self.append(
            "--head", f"main@{past}", "--record", "reconstruction",
        ), 0)
        self.assertIn(f"main@{past}", self.last_row())
        self.assertNotIn(current, self.last_row().split(" | ")[3])

        (self.repo / "later.txt").write_text("later\n")
        self.git("add", "later.txt")
        self.git("commit", "-qm", "later review time")
        self.assertEqual(self.append(
            "--kind", "review", "--status", "recorded:review-pass",
            "--review-base", self.rev("HEAD~3"), "--head", f"main@{past}",
            "--words", "seat", "--note", "replacement review", "--quote", "PASS",
        ), 0, self.err.getvalue())
        self.assertIn(f"main@{past}", self.last_row().split(" | ")[3])
        self.assertIn("record=timely", self.last_row())
        self.assertEqual(self.check_last(), 0, self.err.getvalue())
        self.assertEqual(self.append(
            "--kind", "review", "--status", "recorded:review-pass",
            "--review-base", self.rev("HEAD~3"), "--head", f"main@{past}",
            "--record", "reconstruction", "--words", "seat",
            "--note", "reconstructed replacement review", "--quote", "PASS",
        ), 0, self.err.getvalue())
        self.assertIn("record=reconstruction", self.last_row())
        self.assertEqual(self.check_last(), 0, self.err.getvalue())
        for row in (("--kind", "deploy-gate", "--status", "open", "--words", "none", "--quote", ""),
                    ("--kind", "handoff", "--status", "recorded:handoff", "--words", "seat",
                     "--quote", "STATUS: accepted")):
            self.assertEqual(self.append(*row, "--head", f"main@{past}"), 0, self.err.getvalue())
            self.assertIn(f"main@{past}", self.last_row().split(" | ")[3])
            self.assertIn("record=timely", self.last_row())
            self.assertEqual(self.check_last(), 0, self.err.getvalue())

        self.add_remote(past)
        push = ("--kind", "push", "--push-base", self.rev("HEAD~3"), "--boundary", ".")
        self.assertEqual(self.append(*push, "--head", f"main@{past}"), 0, self.err.getvalue())
        self.assertIn(f"main@{past}", self.last_row().split(" | ")[3])
        self.assertIn("record=timely", self.last_row())
        self.assertEqual(self.check_last(), 0, self.err.getvalue())
        side = self.git("commit-tree", f"{past}^{{tree}}", "-p", past, "-m", "side")
        self.assertEqual(self.append(*push, "--head", f"main@{side}"), 1)
        self.assertIn("--record reconstruction", self.err.getvalue())

    def test_zero_base_review_includes_the_root_commit(self):
        zero = "0" * 40
        self.assertEqual(self.append_review_pass(zero), 0)
        self.assertIn(f"review={zero}..{self.rev('HEAD')} count=3", self.last_row())
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 0)

    def test_zero_base_push_requires_whole_history_review_coverage(self):
        zero = "0" * 40
        self.add_remote("HEAD")
        before = self.ledger.read_bytes()
        self.assertEqual(self.append(
            "--kind", "push", "--push-base", zero, "--boundary", ".",
        ), 1)
        self.assertIn("not covered by any review PASS range", self.err.getvalue())
        self.assertEqual(self.ledger.read_bytes(), before)
        self.assertEqual(self.append_review_pass(zero), 0)
        self.assertEqual(self.append(
            "--kind", "push", "--push-base", zero, "--boundary", ".",
        ), 0)
        self.assertIn(f"push={zero}..{self.rev('HEAD')} count=3", self.last_row())

    def test_first_publication_to_an_empty_remote_can_be_recorded_with_zero_base(self):
        zero = "0" * 40
        self.add_empty_remote()
        self.assertEqual(self.append_review_pass(zero), 0)
        subprocess.run(["git", "-C", str(self.repo), "push", "-q", "origin", "main"],
                       check=True, capture_output=True, stdin=subprocess.DEVNULL)
        self.assertEqual(self.append(
            "--kind", "push", "--push-base", zero, "--boundary", ".",
        ), 0)

    def test_a_past_head_is_landed_when_a_newer_remote_tip_is_on_top(self):
        zero = "0" * 40
        past = self.rev("HEAD")
        self.assertEqual(self.append_review_pass(zero), 0)
        self.add_remote("HEAD")
        (self.repo / "later.txt").write_text("later\n")
        self.git("add", "later.txt")
        self.git("commit", "-qm", "later remote commit")
        subprocess.run(["git", "-C", str(self.repo), "push", "-q", "origin", "main"],
                       check=True, capture_output=True, stdin=subprocess.DEVNULL)
        self.assertEqual(self.append(
            "--kind", "push", "--push-base", zero, "--boundary", ".",
            "--head", f"main@{past}", "--record", "reconstruction",
        ), 0)
        self.assertIn(f"main@{past}", self.last_row())

    def test_a_remote_tip_not_present_locally_is_refused_with_fetch_action(self):
        zero = "0" * 40
        self.assertEqual(self.append_review_pass(zero), 0)
        self.add_remote("HEAD")
        other = self.tmp / "other"
        subprocess.run(["git", "clone", "-q", str(self.tmp / "origin.git"), str(other)],
                       check=True, capture_output=True, stdin=subprocess.DEVNULL)
        subprocess.run(["git", "-C", str(other), "config", "user.email", "t@example.invalid"],
                       check=True, stdin=subprocess.DEVNULL)
        subprocess.run(["git", "-C", str(other), "config", "user.name", "t"], check=True, stdin=subprocess.DEVNULL)
        (other / "unknown.txt").write_text("unknown\n")
        subprocess.run(["git", "-C", str(other), "add", "unknown.txt"], check=True, stdin=subprocess.DEVNULL)
        subprocess.run(["git", "-C", str(other), "commit", "-qm", "unknown remote commit"], check=True, stdin=subprocess.DEVNULL)
        subprocess.run(["git", "-C", str(other), "push", "-q", "origin", "main"],
                       check=True, capture_output=True, stdin=subprocess.DEVNULL)
        before = self.ledger.read_bytes()
        self.assertEqual(self.append(
            "--kind", "push", "--push-base", zero, "--boundary", ".",
        ), 1)
        self.assertIn("git fetch", self.err.getvalue())
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_a_push_row_with_wrong_local_id_is_refused_by_check(self):
        self.assertEqual(self.append(), 0)
        self.assertEqual(self.append(), 0)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        prior = rows[:-1]
        row = rows[-1].replace("G2", "G9", 1)
        with self.assertRaisesRegex(gate_row.RowError, "next local id G2"):
            gate_row.check(row, self.repo, gate_row.LedgerState.of(prior))

    def test_a_delimiter_in_note_is_refused(self):
        for note in ("a | b", 'a " b'):
            with self.subTest(note=note):
                self.assertEqual(self.append("--note", note), 1)
                self.assertIn("note= refuses", self.err.getvalue())
        self.assertEqual(self.append("--note", "a b"), 0, self.err.getvalue())
        text = self.ledger.read_text(encoding="utf-8")
        self.ledger.write_text(text.replace(" | note=a b | ", ' | note=a " b | '), encoding="utf-8")
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 1)
        self.assertIn("note= refuses", self.err.getvalue())

    def test_a_pipe_in_quote_is_kept_verbatim(self):
        human = "à cho các lead revert lại model từ abc-tunnel về cliproxy gpt luna|zai/glm 5.3 flash đi"
        self.assertEqual(self.append("--quote", human), 0)
        self.assertTrue(self.last_row().endswith(f'quote="{human}"'))
        self.assertEqual(self.run_main(
            ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]), 0)

    def test_quote_marker_text_is_kept_verbatim(self):
        human = 'literal | quote=" text'
        self.assertEqual(self.append("--quote", human), 0)
        self.assertTrue(self.last_row().endswith(f'quote="{human}"'))
        self.assertEqual(self.run_main(
            ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]), 0)

    def test_narrative_over_the_cap_is_refused(self):
        self.assertEqual(self.append("--note", "x" * (gate_row.NOTE_MAX + 1)), 1)

    def test_an_undocumented_key_is_refused(self):
        head = self.rev("HEAD")
        row = (f'G9 | 2026-09-06T00:00:00Z | kind=push | main@{head} | '
               f'status=resolved:human | authority=G64 | project=beo-skills | '
               f'record=timely | words=human | note=n | quote="q"')
        with self.assertRaises(gate_row.RowError) as ctx:
            gate_row.check(row, self.repo)
        self.assertIn("not in the row schema", str(ctx.exception))

    def add_empty_remote(self) -> None:
        bare = self.tmp / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True, stdin=subprocess.DEVNULL)
        subprocess.run(["git", "-C", str(self.repo), "remote", "add", "origin", str(bare)],
                       check=True, stdin=subprocess.DEVNULL)

    def add_remote(self, ref: str) -> None:
        bare = self.tmp / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)], check=True, stdin=subprocess.DEVNULL)
        subprocess.run(["git", "-C", str(self.repo), "remote", "add", "origin", str(bare)],
                       check=True, stdin=subprocess.DEVNULL)
        subprocess.run(["git", "-C", str(self.repo), "push", "-q", "origin",
                        f"{self.rev(ref)}:refs/heads/main"], check=True, capture_output=True, stdin=subprocess.DEVNULL)

    def test_a_landed_push_derives_its_own_count_and_boundary(self):
        self.assertEqual(self.append_review_pass(), 0)
        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", self.rev("HEAD~2"),
                                     "--boundary", "f1.txt", "--boundary", "f2.txt"), 0)
        row = self.last_row()
        self.assertIn("count=2", row)
        self.assertIn('boundary="f1.txt f2.txt"', row)
        self.assertIn('boundary-check=""', row)
        self.assertRegex(row, r"push=[0-9a-f]{7,40}\.\.[0-9a-f]{7,40} count=\d+ "
                              r'boundary="[^"]+" boundary-check="[^"]*"')

    def test_a_path_outside_the_boundary_is_named(self):
        self.assertEqual(self.append_review_pass(), 0)
        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", self.rev("HEAD~2"),
                                     "--boundary", "f1.txt"), 0)
        row = self.last_row()
        self.assertIn('boundary="f1.txt"', row)
        self.assertIn('boundary-check="f2.txt"', row)

    def test_a_path_added_and_deleted_inside_the_range_is_still_named(self):
        base = self.rev("HEAD")
        (self.repo / "src").mkdir()
        (self.repo / "src" / "out-of-boundary.py").write_text("x\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "add outside the boundary")
        self.git("rm", "-q", "src/out-of-boundary.py")
        self.git("commit", "-qm", "delete it again")

        net = self.git("diff", "--name-only", f"{base}..HEAD")
        self.assertEqual(net, "", "the net tree diff must be empty, or this case proves nothing")

        self.assertEqual(self.append_review_pass(), 0)
        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", base,
                                     "--boundary", "docs"), 0)
        row = self.last_row()
        self.assertIn("count=2", row)
        self.assertIn('boundary-check="src/out-of-boundary.py"', row)

    def test_a_boundary_flag_holding_several_joined_paths_is_refused(self):
        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", self.rev("HEAD~2"),
                                     "--boundary", "f1.txt f2.txt"), 1)

    def test_a_changed_path_holding_a_space_is_refused(self):
        base = self.rev("HEAD")
        (self.repo / "two words.txt").write_text("x\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "a path with a space")
        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", base,
                                     "--boundary", "docs"), 1)

    def valid_push_row(self) -> tuple[str, list[str]]:
        boundary = ["f1.txt", "f2.txt"]
        self.assertEqual(self.append_review_pass(), 0)
        self.add_remote("HEAD")
        self.assertEqual(self.append(
            "--kind", "push", "--push-base", self.rev("HEAD~2"),
            "--channel", "supervisor-relay:typed", "--writer", "lead-beo-skills",
            *[a for b in boundary for a in ("--boundary", b)]), 0)
        return self.last_row(), boundary

    def test_every_tamper_the_receive_record_found_passing_is_now_refused(self):
        row, boundary = self.valid_push_row()
        prior_rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))[:-1]
        tampers = {
            "boundary-check": (
                'boundary-check=""', 'boundary-check="src/fabricated.py"',
                "outside the declared boundary",
            ),
            "boundary": (
                'boundary="f1.txt f2.txt"', 'boundary="f1.txt"',
                'boundary-check=""',
            ),
            "record": ("record=timely", "record=bogus", "not one of"),
            "quote": ('quote="merge it"', 'quote=""', "words=none iff quote= is empty"),
            "head": (
                f"main@{self.rev('HEAD')}", f"main@{'0' * 40}",
                "git rev-parse --verify",
            ),
            "channel": ("channel=supervisor-relay:typed", "channel=bogus:bogus", "valid channel"),
            "writer": ("writer=lead-beo-skills", "writer=NOT_A_SEAT", "valid writer"),
            "push-kind": ("kind=push", "kind=merge", "push= is only on a kind=push row"),
        }
        for name, (before, after, message) in tampers.items():
            with self.subTest(name):
                tampered = row.replace(before, after)
                self.assertNotEqual(tampered, row, "the tamper did not change the row")
                with self.assertRaisesRegex(gate_row.RowError, re.escape(message)):
                    gate_row.check(tampered, self.repo, gate_row.LedgerState.of(prior_rows))

    def test_check_derives_a_push_row_with_no_boundary_flag(self):
        self.valid_push_row()
        self.assertEqual(self.run_main(
            ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]), 0)

    def test_a_push_row_requires_a_preceding_review_pass_on_append_and_check(self):
        self.add_remote("HEAD")
        base = self.rev("HEAD~2")
        self.assertEqual(self.append("--kind", "push", "--push-base", base,
                                     "--boundary", "f1.txt"), 1)
        self.assertIn("not covered by any review PASS range", self.err.getvalue())
        self.assertEqual(len(gate_row.ledger_rows(self.ledger.read_text())), 0)

        self.assertEqual(self.append_review_pass(), 0)
        self.assertEqual(self.append("--kind", "push", "--push-base", base,
                                     "--boundary", "f1.txt"), 0)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        review = rows[0].replace("status=recorded:review-pass", "status=recorded:review-fail")
        row = self.last_row().replace(
            f"prev_hash={hashlib.sha256(rows[0].encode('utf-8')).hexdigest()}",
            f"prev_hash={hashlib.sha256(review.encode('utf-8')).hexdigest()}",
        )
        self.ledger.write_text(
            "# Gate ledger — test\n\n" + review + "\n" + row + "\n", encoding="utf-8"
        )
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 1)
        self.assertIn("not covered by any review PASS range", self.err.getvalue())

    def test_a_push_row_with_no_declared_boundary_never_reaches_the_ledger(self):
        self.assertEqual(self.append_review_pass(), 0)
        self.add_remote("HEAD")
        before = self.ledger.read_text()
        self.assertEqual(self.append("--kind", "push",
                                     "--push-base", self.rev("HEAD~2")), 1)
        self.assertIn("a push row needs --boundary", self.err.getvalue())
        self.assertEqual(self.ledger.read_text(), before, "the refused row landed anyway")

    def test_a_review_row_needs_a_review_base(self):
        before = self.ledger.read_text()
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "review", "--status", "recorded:review-pass",
            "--words", "seat", "--note", "review", "--quote", "PASS",
        ]), 1)
        self.assertIn("a review row needs --review-base", self.err.getvalue())
        self.assertEqual(self.ledger.read_text(), before, "the refused row landed anyway")

    def test_a_review_row_with_a_wrong_count_is_refused_by_check(self):
        self.assertEqual(self.append_review_pass(), 0)
        tampered = self.last_row().replace("count=2", "count=5")
        self.ledger.write_text("# Gate ledger — test\n\n" + tampered + "\n", encoding="utf-8")
        self.assertEqual(self.run_main(
            ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]), 1)
        self.assertIn("carries 2 commits", self.err.getvalue())

    def test_a_review_row_with_no_review_block_is_refused_by_check(self):
        self.assertEqual(self.append_review_pass(), 0)
        stripped = " | ".join(
            p for p in self.last_row().split(" | ") if not p.startswith("review=")
        )
        self.ledger.write_text("# Gate ledger — test\n\n" + stripped + "\n", encoding="utf-8")
        self.assertEqual(self.run_main(
            ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]), 1)
        self.assertIn("carries no review block", self.err.getvalue())

    def test_review_base_on_a_non_review_row_is_refused_rather_than_dropped(self):
        before = self.ledger.read_text()
        self.assertEqual(self.append("--review-base", self.rev("HEAD~2")), 1)
        self.assertIn("--review-base is only meaningful on a review row", self.err.getvalue())
        self.assertEqual(self.ledger.read_text(), before, "the refused row landed anyway")

    def test_a_row_declaring_an_empty_boundary_is_refused(self):
        row, _ = self.valid_push_row()
        empty = row.replace('boundary="f1.txt f2.txt"', 'boundary=""')
        self.assertNotEqual(empty, row)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        with self.assertRaises(gate_row.RowError) as ctx:
            gate_row.check(empty, self.repo, gate_row.LedgerState.of(rows[:-1]))
        self.assertIn("empty boundary", str(ctx.exception))

    def test_a_dot_boundary_covers_the_whole_repository(self):
        self.assertEqual(self.append_review_pass(), 0)
        """`.` prefixes no repo-relative path, so it used to invert its own meaning.

        Declaring the whole tree produced the whole changed set as *outside* it —
        the over-claiming shape, from the one declaration that means the opposite.
        """
        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", self.rev("HEAD~2"),
                                     "--boundary", "."), 0)
        row = self.last_row()
        self.assertIn('boundary="."', row)
        self.assertIn('boundary-check=""', row)

    def test_a_row_outlives_the_branch_that_named_it(self):
        self.git("checkout", "-q", "-b", "topic")
        self.assertEqual(self.append(), 0)
        row = self.last_row()
        self.assertIn("topic@", row)
        self.git("checkout", "-q", "main")
        self.git("branch", "-D", "topic")
        gate_row.check(row, self.repo)
        gate_row.check(row.replace("topic@", "nonexistent-branch@"), self.repo)
        push_row, _ = self.valid_push_row()
        prior_rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))[:-1]
        gate_row.check(push_row.replace("main@", "nonexistent-branch@"), self.repo, gate_row.LedgerState.of(prior_rows))

    def test_a_push_row_without_push_base_never_reaches_the_ledger(self):
        self.assertEqual(self.append_review_pass(), 0)
        self.add_remote("HEAD")
        before = self.ledger.read_text()
        self.assertEqual(self.append("--kind", "push", "--boundary", "f1.txt"), 1)
        self.assertIn("a push row needs --push-base", self.err.getvalue())
        self.assertEqual(self.ledger.read_text(), before, "the refused row landed anyway")

    def test_a_kind_push_row_with_no_push_block_is_refused_by_check(self):
        row, _ = self.valid_push_row()
        blockless = re.sub(r" \| push=[^|]+", " ", row)
        self.assertNotIn("push=", blockless)
        self.assertIn("kind=push", blockless)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        self.ledger.write_text(
            "# Gate ledger — test\n\n" + "\n".join([rows[0], blockless]) + "\n",
            encoding="utf-8",
        )
        self.assertEqual(self.run_main(
            ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]), 1)
        self.assertIn("carries no push block", self.err.getvalue())

    def test_push_base_on_a_non_push_row_is_refused_rather_than_dropped(self):
        self.assertEqual(self.append_review_pass(), 0)
        self.add_remote("HEAD")
        before = self.ledger.read_text()
        self.assertEqual(self.append("--push-base", self.rev("HEAD~2"),
                                     "--boundary", "f1.txt"), 1)
        self.assertIn("only meaningful on a push row", self.err.getvalue())
        self.assertEqual(self.ledger.read_text(), before, "the refused row landed anyway")

    def test_boundary_on_a_non_push_row_is_refused_rather_than_dropped(self):
        before = self.ledger.read_text()
        self.assertEqual(self.append("--boundary", "f1.txt"), 1)
        self.assertIn("--boundary is only meaningful on a push row", self.err.getvalue())
        self.assertEqual(self.ledger.read_text(), before, "the refused row landed anyway")

    def test_chain_byte_definition_excludes_the_predecessor_newline(self):
        self.assertEqual(self.append(), 0)
        predecessor = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))[0]
        self.assertEqual(self.append(), 0)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        expected = hashlib.sha256(predecessor.encode("utf-8")).hexdigest()
        with_newline = hashlib.sha256((predecessor + "\n").encode("utf-8")).hexdigest()
        self.assertNotEqual(expected, with_newline)
        self.assertRegex(rows[1], rf"(?:^| \\| )prev_hash={expected}(?: \\| |$)")
        self.assertNotIn(f"prev_hash={with_newline}", rows[1])

    def test_deploy_targets_select_latest_applicable_completed_row(self):
        skill_root = self.repo / "skills" / "example"
        skill_root.mkdir(parents=True)
        (skill_root / "SKILL.md").write_text("test skill\n", encoding="utf-8")
        self.git("add", "skills/example")
        self.git("commit", "-qm", "add skill")
        first_head = self.rev("HEAD")
        args = [
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "deploy", "--status", "resolved:deploy", "--skill", "example",
            "--words", "seat", "--note", "deployed", "--quote", "ok",
        ]
        self.assertEqual(self.run_main(args), 0, self.err.getvalue())
        first_row = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))[-1]
        self.assertIn("skills=example", first_row)
        (skill_root / "SKILL.md").write_text("newer skill\n", encoding="utf-8")
        self.git("add", "skills/example")
        self.git("commit", "-qm", "update skill")
        second_head = self.rev("HEAD")
        self.assertEqual(self.run_main(args), 0, self.err.getvalue())
        selected = gate_row.select_deployed_head(self.ledger, "example", self.repo)
        self.assertEqual(selected[:2], ("main", second_head))
        self.assertEqual(selected[2], gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))[-1])
        self.assertNotEqual(first_head, second_head)
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--deployed-head", "missing",
        ]), 1)
        self.assertIn("no completed target-bearing deploy row", self.err.getvalue())

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            self.assertEqual(gate_row.main([
                "--ledger", str(self.ledger), "--repo", str(self.repo),
                "--deployed-head", "example",
            ]), 0)
        branch_head, source_row = output.getvalue().splitlines()
        self.assertEqual(branch_head, f"main@{second_head}")
        self.assertEqual(source_row, selected[2])

    def test_binary_deploy_without_skill_is_chained_but_not_a_recovery_target(self):
        skill_root = self.repo / "skills" / "example"
        skill_root.mkdir(parents=True)
        (skill_root / "SKILL.md").write_text("test skill\n", encoding="utf-8")
        self.git("add", "skills/example")
        self.git("commit", "-qm", "add skill")

        def cli(*args: str) -> subprocess.CompletedProcess[str]:
            return subprocess.run(
                [sys.executable, str(SCRIPTS / "gate_row.py"),
                 "--ledger", str(self.ledger), "--repo", str(self.repo), *args],
                capture_output=True, text=True, stdin=subprocess.DEVNULL, check=False,
            )

        common = ("--kind", "deploy", "--words", "seat", "--note", "installed binary",
                  "--quote", "ok")
        before = self.ledger.read_bytes()
        for extra, error in (
            (("--status", "open"), "kind=deploy requires a completed deploy status"),
            (("--status", "resolved:deploy", "--skill", "example", "--skill", "example"),
             "kind=deploy --skill names a skill more than once"),
            (("--status", "resolved:deploy", "--skill", "../example"),
             "kind=deploy --skill names a malformed top-level skill"),
        ):
            with self.subTest(extra=extra):
                rejected = cli(*common, *extra)
                self.assertEqual(rejected.returncode, 1)
                self.assertIn(error, rejected.stderr)
                self.assertEqual(self.ledger.read_bytes(), before)

        deployed = cli(*common, "--status", "resolved:deploy")
        self.assertEqual(deployed.returncode, 0, deployed.stderr)
        first_row = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))[0]
        self.assertNotIn("skills=", first_row)

        chained = cli(
            "--kind", "merge", "--status", "resolved:human", "--words", "human",
            "--note", "continue ledger", "--quote", "merge",
        )
        self.assertEqual(chained.returncode, 0, chained.stderr)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 2)
        self.assertIn(f"prev_hash={gate_row.row_hash(rows[0])}", rows[1])

        checked = cli("--check")
        self.assertEqual(checked.returncode, 0, checked.stderr)
        self.assertEqual(checked.stdout, "ok: G2 checks out\n")

        recovery = cli("--deployed-head", "example")
        self.assertEqual(recovery.returncode, 1)
        self.assertIn("no completed target-bearing deploy row", recovery.stderr)

    def test_fresh_ledger_g1_to_g2_forms_an_intact_chain(self):
        self.assertEqual(self.append(), 0)
        self.assertEqual(self.append(), 0)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        self.assertEqual([row.split(" | ")[0] for row in rows], ["G1", "G2"])
        self.assertNotIn("prev_hash=", rows[0])
        self.assertIn(
            f"prev_hash={hashlib.sha256(rows[0].encode('utf-8')).hexdigest()}",
            rows[1],
        )
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 0)

    def test_a_second_row_without_prev_hash_is_refused_on_every_load(self):
        self.assertEqual(self.append(), 0)
        self.assertEqual(self.append(), 0)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        stripped = "# Gate ledger — test\n\n" + "\n".join([rows[0], rows[1].replace(
            " | prev_hash=" + gate_row.row_hash(rows[0]), ""
        )]) + "\n"
        self.ledger.write_text(stripped, encoding="utf-8")
        for mode in (["--check"], ["--open-gates"], []):
            with self.subTest(mode=mode):
                argv = ["--ledger", str(self.ledger), "--repo", str(self.repo), *mode]
                if not mode:
                    self.assertEqual(self.append(), 1)
                else:
                    self.assertEqual(self.run_main(argv), 1)
                self.assertIn("row 'G2' is missing prev_hash=", self.err.getvalue())
                self.assertEqual(self.ledger.read_text(encoding="utf-8"), stripped)

    def test_a_first_row_carrying_prev_hash_is_refused_on_load(self):
        self.assertEqual(self.append(), 0)
        self.assertEqual(self.append(), 0)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        self.ledger.write_text("# Gate ledger — test\n\n" + rows[1] + "\n", encoding="utf-8")
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 1)
        self.assertIn("row 'G2' carries prev_hash= without a predecessor", self.err.getvalue())

    def assert_chain_tamper_rejected(self, rows: list[str]) -> None:
        self.ledger.write_text(
            "# Gate ledger — test\n\n" + "\n".join(rows) + "\n", encoding="utf-8"
        )
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 1)
        self.assertIn("prev_hash", self.err.getvalue())

    def test_mid_chain_edit_is_rejected_by_the_cli_loader(self):
        for _ in range(3):
            self.assertEqual(self.append(), 0)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        edited = rows[1].replace("note=merged the reviewed head", "note=edited historical row")
        self.assert_chain_tamper_rejected([rows[0], edited, rows[2]])

    def test_mid_chain_deletion_is_rejected_by_the_cli_loader(self):
        for _ in range(3):
            self.assertEqual(self.append(), 0)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        self.assert_chain_tamper_rejected([rows[0], rows[2]])

    def test_mid_chain_reorder_is_rejected_by_the_cli_loader(self):
        for _ in range(3):
            self.assertEqual(self.append(), 0)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        self.assert_chain_tamper_rejected([rows[0], rows[2], rows[1]])

    def test_stripped_post_adoption_prev_hash_is_rejected_by_the_cli_loader(self):
        for _ in range(3):
            self.assertEqual(self.append(), 0)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        stripped = rows[2].replace(
            " | prev_hash=" + hashlib.sha256(rows[1].encode("utf-8")).hexdigest(), ""
        )
        self.assert_chain_tamper_rejected([rows[0], rows[1], stripped])

    def test_a_row_over_claiming_the_whole_changed_set_is_refused(self):
        row, boundary = self.valid_push_row()
        p = re.search(r'boundary-check="([^"]*)"', row)
        self.assertEqual(p.group(1), "", "the control row declares no breach")
        base = self.rev("HEAD~2")
        changed = sorted({
            path
            for commit in self.git("rev-list", f"{base}..HEAD").splitlines()
            for path in self.git("diff-tree", "--root", "-m", "--no-commit-id",
                                 "--name-only", "-r", commit).splitlines()
            if path
        })
        self.assertTrue(set(boundary) & set(changed), "the range touches the boundary")
        over = row.replace('boundary-check=""', f'boundary-check="{" ".join(changed)}"')
        self.assertNotEqual(over, row)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        self.ledger.write_text(
            "# Gate ledger — test\n\n" + "\n".join([rows[0], over]) + "\n",
            encoding="utf-8",
        )
        argv = ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]
        self.assertEqual(self.run_main(argv), 1)
        self.assertIn("outside the declared boundary", self.err.getvalue())

    def test_ledger_is_a_required_argument(self):
        with self.assertRaises(SystemExit) as ctx:
            self.run_main(["--repo", str(self.repo), "--check"])
        self.assertEqual(ctx.exception.code, 2)

    def test_repo_defaults_to_the_working_directory(self):
        with contextlib.chdir(self.repo):
            self.assertEqual(self.run_main([
                "--ledger", str(self.ledger), "--kind", "merge", "--status", "resolved:human",
                "--words", "human", "--note", "merged the reviewed head", "--quote", "merge it",
            ]), 0, self.err.getvalue())
        self.assertIn(f" | main@{self.rev('HEAD')} | ", self.last_row())

    def test_append_requires_kind_status_and_note(self):
        before = self.ledger.read_bytes()
        base = ["--ledger", str(self.ledger), "--repo", str(self.repo), "--words", "human", "--quote", "q"]
        for extra, message in (
            (["--kind", "merge", "--note", "n"], "--kind and --status are required"),
            (["--kind", "merge", "--status", "open"], "note= is required"),
        ):
            with self.subTest(extra):
                self.assertEqual(self.run_main(base + extra), 1)
                self.assertIn(message, self.err.getvalue())
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_a_ledger_without_a_trailing_newline_gets_one_before_the_row(self):
        self.ledger.write_text("# Gate ledger — test", encoding="utf-8")
        self.assertEqual(self.append(), 0, self.err.getvalue())
        self.assertEqual(self.ledger.read_text(encoding="utf-8"),
                         f"# Gate ledger — test\n{self.last_row()}\n")

    def test_check_prints_the_id_it_checked(self):
        self.assertEqual(self.append(), 0)
        written = self.last_row()
        self.assertEqual(self.check_last(), 0)
        self.assertEqual(self.out.getvalue(), "ok: G1 checks out\n")
        self.assertEqual(self.last_row(), written)

    def test_a_row_is_stamped_in_utc_whatever_the_local_zone(self):
        import os
        import time
        self.addCleanup(time.tzset)
        with mock.patch.dict(os.environ, {"TZ": "Etc/GMT-7"}):
            time.tzset()
            self.assertEqual(self.append(), 0, self.err.getvalue())
        stamp = datetime.strptime(self.last_row().split(" | ")[1], "%Y-%m-%dT%H:%M:%SZ")
        drift = abs(stamp.replace(tzinfo=timezone.utc) - datetime.now(timezone.utc))
        self.assertLess(drift.total_seconds(), 600)

    def test_a_note_of_exactly_the_cap_lands_and_checks_out(self):
        self.assertEqual(self.append("--note", "n" * gate_row.NOTE_MAX), 0, self.err.getvalue())
        self.assertEqual(self.check_last(), 0, self.err.getvalue())

    def test_quote_file_strips_one_trailing_crlf(self):
        path = self.tmp / "quote.txt"
        path.write_bytes(b"merge it\r\n")
        self.assertEqual(self.append("--quote", "", "--quote-file", str(path)), 0, self.err.getvalue())
        self.assertIn(' | quote="merge it"', self.last_row())
        self.assertTrue(self.last_row().endswith('"merge it"'))

    def test_every_special_flag_is_refused_on_a_kind_it_does_not_belong_to(self):
        before = self.ledger.read_bytes()
        for flag in ("--op", "--after", "--who", "--scope", "--conditions", "--expiry", "--finding"):
            with self.subTest(flag):
                self.assertEqual(self.append(flag, "x"), 1)
                self.assertIn(f"{flag} is only meaningful", self.err.getvalue())
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_a_structured_field_refuses_the_row_delimiters(self):
        before = self.ledger.read_bytes()
        for op in ("git|status", 'git "status"', "git\nstatus"):
            with self.subTest(op=op):
                self.assertEqual(self.append_local_ops("--op", op), 1)
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_one_resolves_flag_can_close_several_gates(self):
        self.assertEqual(self.append("--status", "open"), 0, self.err.getvalue())
        self.assertEqual(self.append("--status", "open"), 0, self.err.getvalue())
        self.assertEqual(self.append("--resolves", "G1,G2"), 0, self.err.getvalue())
        self.assertIn(" | resolves=G1,G2 | ", self.last_row())
        self.assertEqual(self.open_gates(), [])

    def test_only_a_progress_boundary_resets_the_repair_cap(self):
        self.add_remote("HEAD")
        cases = (
            ("merge resolved", True, lambda: self.append()),
            ("repair-cap-gate", True, lambda: self.append("--kind", "repair-cap-gate", "--status", "open")),
            ("push", True, lambda: self.append(
                "--kind", "push", "--push-base", self.rev("HEAD~2"), "--boundary", ".")),
            ("merge open", False, lambda: self.append("--status", "open")),
            ("resolved non-merge", False, lambda: self.append("--kind", "deploy-gate")),
        )
        for name, resets, boundary in cases:
            with self.subTest(name):
                self.ledger.write_text("# Gate ledger — test\n\n")
                self.assertEqual(self.append_review_pass(), 0, self.err.getvalue())
                self.assertEqual(self.append_repair_grant(), 0, self.err.getvalue())
                self.assertEqual(boundary(), 0, self.err.getvalue())
                self.assertEqual(self.append_repair_grant(), 0 if resets else 1, self.err.getvalue())

    def test_the_landed_check_reads_origins_copy_of_the_rows_branch(self):
        self.assertEqual(self.append_review_pass(), 0, self.err.getvalue())
        self.add_remote("HEAD")
        subprocess.run(["git", "-C", str(self.repo), "push", "-q", "origin",
                        f"{self.rev('HEAD~1')}:refs/heads/aaa"], check=True, capture_output=True, stdin=subprocess.DEVNULL)
        subprocess.run(["git", "--git-dir", str(self.tmp / "origin.git"), "symbolic-ref", "HEAD",
                        "refs/heads/aaa"], check=True, stdin=subprocess.DEVNULL)
        self.assertEqual(self.append(
            "--kind", "push", "--push-base", self.rev("HEAD~2"), "--boundary", "."), 0, self.err.getvalue())

    def test_a_head_that_is_not_under_the_remote_tip_has_not_landed(self):
        self.assertEqual(self.append_review_pass(), 0, self.err.getvalue())
        self.add_remote("HEAD~1")
        before = self.ledger.read_bytes()
        self.assertEqual(self.append(
            "--kind", "push", "--push-base", self.rev("HEAD~2"), "--boundary", "."), 1)
        self.assertIn("has not landed", self.err.getvalue())
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_boundary_alone_on_a_review_row_is_refused(self):
        before = self.ledger.read_bytes()
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "review", "--status", "recorded:review-pass", "--review-base", self.rev("HEAD~2"),
            "--boundary", "f1.txt", "--words", "seat", "--note", "review passed", "--quote", "PASS",
        ]), 1)
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_two_paths_outside_the_boundary_round_trip(self):
        self.assertEqual(self.append_review_pass(), 0, self.err.getvalue())
        self.add_remote("HEAD")
        self.assertEqual(self.append(
            "--kind", "push", "--push-base", self.rev("HEAD~2"), "--boundary", "docs"), 0, self.err.getvalue())
        self.assertIn('boundary-check="f1.txt f2.txt"', self.last_row())
        self.assertEqual(self.check_last(), 0, self.err.getvalue())

    def test_the_touched_set_counts_the_root_commit_merges_and_both_rename_sides(self):
        self.assertEqual(gate_row.derive_push(self.repo, "0" * 40, self.rev("HEAD"), ["f1.txt", "f2.txt"]),
                         ("3", ["f0.txt"]))
        base = self.rev("HEAD")
        self.git("checkout", "-qb", "side")
        (self.repo / "side.txt").write_text("s\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "side")
        self.git("checkout", "-q", "main")
        self.git("mv", "f0.txt", "kept.txt")
        self.git("commit", "-qm", "rename")
        self.git("merge", "-q", "--no-ff", "--no-commit", "side")
        (self.repo / "evil.txt").write_text("e\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "merge with a change of its own")
        _, outside = gate_row.derive_push(self.repo, base, self.rev("HEAD"), ["side.txt", "kept.txt"])
        self.assertEqual(outside, ["evil.txt", "f0.txt"])

    def test_a_directory_boundary_covers_its_files_with_or_without_a_slash(self):
        base = self.rev("HEAD")
        (self.repo / "docs").mkdir()
        (self.repo / "docs" / "a.md").write_text("a\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "docs")
        for boundary in ("docs", "docs/"):
            with self.subTest(boundary):
                self.assertEqual(gate_row.derive_push(self.repo, base, self.rev("HEAD"), [boundary]), ("1", []))

    def test_a_boundary_ending_in_a_letter_does_not_cover_its_siblings(self):
        base = self.rev("HEAD")
        (self.repo / "lib").mkdir()
        (self.repo / "lib" / "core.py").write_text("c\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "lib")
        self.assertEqual(gate_row.derive_push(self.repo, base, self.rev("HEAD"), ["lib/X"]),
                         ("1", ["lib/core.py"]))

    def test_a_boundary_holding_whitespace_is_refused(self):
        with self.assertRaises(gate_row.RowError):
            gate_row.derive_push(self.repo, self.rev("HEAD~1"), self.rev("HEAD"), ["a b"])

    def test_cutover_genesis_rows_are_accepted_and_next_g_id_continues(self):
        head = self.rev("HEAD")
        fixtures = (
            ("G608", "2026-09-23T06:17:11Z", "main", "lead-beo-skills",
             "31c7e7ed3e4fa153dc53c991c7205ee58f0bc6390b333dbb9cd2ade4435ed143"),
            ("G485", "2026-09-23T06:18:53Z", "main", "lead-apexinvest-payload",
             "24c2a4747b9e8a32c9079d45f3e1d18b54b9d4b1250dd56248cf72130939f2ec"),
            ("G210", "2026-09-23T07:14:38Z", "fix/rereview-forks", "lead-munsu",
             "e14cfdb9c9d12eec9d53e3ec5cc493a85e5b3ee201e4f5f83b0e42ab02e46854"),
        )
        for gid, timestamp, branch, writer, archive in fixtures:
            with self.subTest(gid):
                genesis = (
                    f'{gid} | {timestamp} | kind=cutover | {branch}@{head} | '
                    f'status=recorded:cutover | writer={writer} | record=timely | '
                    f'archive={archive} | words=seat | note=genesis fixture | quote="cutover"'
                )
                self.ledger.write_text("# Gate ledger — test\n\n" + genesis + "\n", encoding="utf-8")
                self.assertEqual(self.run_main([
                    "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
                ]), 0, self.err.getvalue())
                self.assertIn(f"ok: {gid} checks out", self.out.getvalue())
                self.assertEqual(self.run_main([
                    "--ledger", str(self.ledger), "--repo", str(self.repo),
                    "--kind", "merge", "--status", "resolved:human",
                    "--words", "human", "--note", "continue genesis chain", "--quote", "continue",
                ]), 0, self.err.getvalue())
                second = self.last_row()
                self.assertTrue(second.startswith(f"G{int(gid[1:]) + 1} | "))
                self.assertIn(f"prev_hash={gate_row.row_hash(genesis)}", second)
                self.assertEqual(self.run_main([
                    "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
                ]), 0, self.err.getvalue())
                self.assertEqual(self.run_main([
                    "--ledger", str(self.ledger), "--repo", str(self.repo),
                    "--kind", "push-gate", "--status", "open", "--words", "none",
                    "--note", "carried open gate",
                ]), 0, self.err.getvalue())
                carried = self.last_row()
                self.assertTrue(carried.startswith(f"G{int(gid[1:]) + 2} | "))
                self.assertIn(f"prev_hash={gate_row.row_hash(second)}", carried)
                self.assertEqual(self.open_gates(), [f"G{int(gid[1:]) + 2}"])

        gid, timestamp, branch, writer, archive = fixtures[0]
        genesis = (
            f'{gid} | {timestamp} | kind=cutover | {branch}@{head} | '
            f'status=recorded:cutover | writer={writer} | record=timely | '
            f'archive={archive} | words=seat | note=genesis fixture | quote="cutover"'
        )
        for malformed in (
            genesis.replace("status=recorded:cutover", "status=recorded:handoff"),
            genesis.replace(f"archive={archive}", f"archive={'A' * 64}"),
            genesis.replace(f"archive={archive} | ", ""),
            genesis.replace("kind=cutover", "kind=merge"),
            genesis.replace(gid, "decision-abc", 1),
            genesis.replace(gid, "G0", 1),
        ):
            self.ledger.write_text("# Gate ledger — test\n\n" + malformed + "\n", encoding="utf-8")
            self.assertEqual(self.run_main([
                "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
            ]), 1)

        later_cutover = genesis.replace(gid, f"G{int(gid[1:]) + 1}", 1).replace(
            f"archive={archive}", f"prev_hash={gate_row.row_hash(genesis)} | archive={archive}"
        )
        rows = [genesis, later_cutover]
        self.ledger.write_text("# Gate ledger — test\n\n" + "\n".join(rows) + "\n", encoding="utf-8")
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 1)
        self.assertIn("kind=cutover is only valid as the first row", self.err.getvalue())

        broken = genesis.replace(f"archive={archive}", f"archive={'A' * 64}")
        re_chained = (
            f'G{int(gid[1:]) + 1} | {timestamp} | kind=merge | {branch}@{head} | '
            f'status=resolved:human | writer={writer} | record=timely | '
            f'prev_hash={gate_row.row_hash(broken)} | words=human | note=re-chained | quote="continue"'
        )
        rows = [broken, re_chained]
        self.ledger.write_text("# Gate ledger — test\n\n" + "\n".join(rows) + "\n", encoding="utf-8")
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 1)
        self.assertIn("is not a 64-character lowercase hex archive=", self.err.getvalue())

        self.ledger.write_text("# Gate ledger — test\n\n" + genesis + "\n", encoding="utf-8")
        before = self.ledger.read_bytes()
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "cutover", "--status", "recorded:cutover",
            "--words", "seat", "--note", "no cutover append", "--quote", "cutover",
        ]), 1)
        self.assertIn("valid only as a stored first-row genesis", self.err.getvalue())
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_check_refuses_a_non_first_row_without_prev_hash_by_position(self):
        self.assertEqual(self.append(), 0)
        self.assertEqual(self.append(), 0)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        stripped = rows[1].replace(" | prev_hash=" + gate_row.row_hash(rows[0]), "")
        with self.assertRaisesRegex(gate_row.RowError, "is missing prev_hash=; every row after the first"):
            gate_row.verify_chain([rows[0], stripped])

    def test_a_prev_hash_mismatch_names_the_expected_hash(self):
        self.assertEqual(self.append_local_ops(), 0, self.err.getvalue())
        self.assertEqual(self.append_local_ops(), 0, self.err.getvalue())
        first, second = [l for l in self.ledger.read_text().splitlines() if gate_row.ID_RE.match(l)]
        bad = second.replace(f"prev_hash={gate_row.row_hash(first)}", "prev_hash=" + "0" * 64)
        with self.assertRaises(gate_row.RowError) as caught:
            gate_row.verify_chain([first, bad])
        self.assertEqual(str(caught.exception),
                         f"prev_hash mismatch at row {second.split(' | ')[0]!r}: "
                         f"expected {gate_row.row_hash(first)}, got {'0' * 64}")

    def test_archive_field_on_another_kind_is_refused_by_check(self):
        self.assertEqual(self.append(), 0)
        self.assertEqual(self.append(), 0)
        first, row = gate_row.ledger_rows(self.ledger.read_text())
        forged = row.replace(" | words=", f" | archive={'a' * 64} | words=")
        with self.assertRaisesRegex(gate_row.RowError, "words= is missing or out of order"):
            gate_row.check(forged, self.repo, gate_row.LedgerState.of([first]))

    def test_an_archive_value_carrying_a_second_equals_is_refused(self):
        head = self.rev("HEAD")
        genesis = (
            f"G1 | 2026-09-06T00:00:00Z | kind=cutover | main@{head} | "
            "status=recorded:cutover | writer=lead-beo-skills | record=timely | "
            f"archive={'a' * 64} | words=seat | note=genesis fixture | quote=\"cutover\""
        )
        field = f"archive={'a' * 64}"
        for forged in (f"{field}=x", f"archive=x={'a' * 64}"):
            with self.subTest(forged), self.assertRaises(gate_row.RowError):
                gate_row.check(genesis.replace(field, forged), self.repo)

    def test_an_id_token_not_followed_by_the_field_delimiter_is_refused(self):
        row = self.fixture_row("G1", "open", "none", "").replace("G1 | ", "G1 |x | ", 1)
        self.ledger.write_text(row + "\n", encoding="utf-8")
        self.assertEqual(self.check_last(), 1)
        self.assertIn("row does not start with a G id", self.err.getvalue())

    def test_a_row_ending_before_a_required_field_is_refused_naming_it(self):
        head = f"main@{self.rev('HEAD')}"
        for middle, needle in (
            ("kind=merge | {head} | status=open", "record="),
            ("kind=repair-grant | {head} | status=recorded:granted | record=timely", "finding="),
            ("kind=cutover | {head} | status=recorded:cutover | record=timely", "archive="),
        ):
            with self.subTest(needle):
                row = f'G1 | 2026-09-06T00:00:00Z | {middle.format(head=head)} | quote=""'
                self.ledger.write_text(row + "\n", encoding="utf-8")
                self.assertEqual(self.check_last(), 1)
                self.assertIn(needle, self.err.getvalue())

    def test_local_ops_values_are_read_up_to_the_first_equals(self):
        self.assertEqual(self.append_local_ops("--op", "export X="), 0, self.err.getvalue())
        self.git("branch", "a=")
        self.assertEqual(self.append_local_ops("--after", f"a=@{self.rev('HEAD')}"), 0, self.err.getvalue())

    def test_resolving_a_standing_delegation_still_checks_the_next_target(self):
        self.assertEqual(self.append_standing_delegation(), 0, self.err.getvalue())
        self.assertEqual(self.append("--resolves", "G1,G9"), 1)
        self.assertIn(
            "resolves=G9 refused: never-open; supersede by citing its id in note=",
            self.err.getvalue(),
        )

    def test_a_gate_whose_latest_own_row_is_closed_cannot_be_resolved(self):
        rows = [
            self.fixture_row("G1", "open", "none", ""),
            self.fixture_row("G2", "resolved:done", resolves="G1"),
        ]
        self.ledger.write_text("# fixture\n" + "\n".join(self.chained(rows)) + "\n")
        self.assertEqual(self.append("--resolves", "G1"), 1)
        self.assertIn("resolves=G1 refused: already-closed", self.err.getvalue())

    def test_a_later_row_can_resolve_an_open_gate_or_standing_delegation(self):
        self.assertEqual(self.append(
            "--status", "open", "--words", "none", "--quote", "",
        ), 0, self.err.getvalue())
        self.assertEqual(self.append("--resolves", "G1"), 0, self.err.getvalue())
        self.assertEqual(self.append_standing_delegation(), 0, self.err.getvalue())
        self.assertEqual(self.append("--resolves", "G3"), 0, self.err.getvalue())

    def test_a_prior_repair_grant_finding_is_read_whole(self):
        row = self.fixture_row("G1", "recorded:granted", kind="repair-grant").replace(
            " | words=", " | finding=a=b | words=", 1)
        self.ledger.write_text(row + "\n", encoding="utf-8")
        self.assertEqual(self.append_repair_grant("c"), 1)
        self.assertIn("finding='a=b' is not an identity token", self.err.getvalue())

    def test_append_rejects_a_malformed_historical_review_status(self):
        for status in ("recorded:review-pass=x", "x=recorded:review-pass"):
            with self.subTest(status):
                rows = [
                    self.fixture_row("G1", "recorded:granted", kind="repair-grant").replace(
                        " | words=", " | finding=F-1 | words=", 1),
                    self.fixture_row("G2", status, kind="review"),
                ]
                self.ledger.write_text("# fixture\n" + "\n".join(self.chained(rows)) + "\n")
                self.assertEqual(self.append_repair_grant("F-1"), 1)
                self.assertIn("is not a valid status=", self.err.getvalue())

    def test_read_only_modes_do_not_create_a_missing_ledger(self):
        missing = self.tmp / "missing" / "gates.md"
        missing.parent.mkdir()
        for mode in ("--check", "--open-gates"):
            with self.subTest(mode):
                self.assertEqual(self.run_main(["--ledger", str(missing), "--repo", str(self.repo), mode]), 1)
                self.assertFalse(missing.exists())

    def test_an_unknown_record_or_words_value_is_a_usage_error(self):
        for flag in ("--record", "--words"):
            with self.subTest(flag), self.assertRaises(SystemExit) as caught:
                self.append(flag, "bogus")
            self.assertEqual(caught.exception.code, 2)

    def test_an_outside_path_holding_a_row_delimiter_is_refused(self):
        for name in ("pipe|name.txt", 'quote"name.txt'):
            with self.subTest(name):
                base = self.rev("HEAD")
                (self.repo / name).write_text("x\n")
                self.git("add", "-A")
                self.git("commit", "-qm", "delimiter path")
                with self.assertRaises(gate_row.RowError):
                    gate_row.derive_push(self.repo, base, self.rev("HEAD"), ["docs"])

    def test_mailbox_attention_is_required_only_of_an_open_human_gate(self):
        mailbox = self.tmp / "supervisor-mailbox.md"
        mailbox.write_text("", encoding="utf-8")
        argv = ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check", "--mailbox", str(mailbox)]
        self.assertEqual(self.append(), 0, self.err.getvalue())
        self.assertEqual(self.run_main(argv), 0, self.err.getvalue())
        self.assertEqual(self.append("--kind", "note", "--status", "open"), 0, self.err.getvalue())
        self.assertEqual(self.run_main(argv), 0, self.err.getvalue())

    def test_mailbox_attention_is_found_below_other_lines(self):
        self.assertEqual(self.append("--status", "open"), 0, self.err.getvalue())
        mailbox = self.tmp / "supervisor-mailbox.md"
        mailbox.write_text(
            "# Supervisor mailbox\n\n"
            "## lead-beo-skills -> supervisor | 2026-09-13T00:00:00Z | "
            f"ATTENTION project human gate G1 | HEAD {self.rev('HEAD')}\n",
            encoding="utf-8",
        )
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check", "--mailbox", str(mailbox),
        ]), 0, self.err.getvalue())

    def test_a_field_value_carrying_a_second_equals_is_refused_by_check(self):
        self.assertEqual(self.append("--status", "open", "--channel", "supervisor-relay:typed",
                                     "--writer", "lead-beo-skills"), 0, self.err.getvalue())
        self.assertEqual(self.append("--resolves", "G1"), 0, self.err.getvalue())
        self.assertEqual(self.append_repair_grant(), 0, self.err.getvalue())
        self.assertEqual(self.append_local_ops(), 0, self.err.getvalue())
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        names = {"channel", "writer", "record", "status", "resolves", "finding", "after", "prev_hash", "words"}
        for index, row in enumerate(rows):
            for field in row.split(" | ")[1:-1]:
                name, _, value = field.partition("=")
                if name not in names:
                    continue
                # A branch name may hold "=", so after=x=<branch>@<sha> is a valid after=.
                prefixed = () if name == "after" else (f"{name}=x={value}",)
                for forged in (f"{field}=x", *prefixed):
                    with self.subTest(forged):
                        tampered = row.replace(f" | {field} | ", f" | {forged} | ", 1)
                        self.assertNotEqual(tampered, row)
                        if name == "prev_hash":
                            with self.assertRaises(gate_row.RowError):
                                gate_row.verify_chain([*rows[:index], tampered])
                        else:
                            with self.assertRaises(gate_row.RowError):
                                gate_row.check(tampered, self.repo, gate_row.LedgerState.of(rows[:index]))

    def test_a_truncated_row_is_a_row_error_not_a_crash(self):
        head = self.rev("HEAD")
        record = " | record=timely"

        def row(kind: str, status: str, tail: str) -> str:
            return f'G1 | 2026-09-06T00:00:00Z | kind={kind} | main@{head} | status={status}{tail} | quote=""'

        rows = [
            row("merge", "open", ""),
            row("merge", "open", " | channel=supervisor-relay:typed"),
            row("merge", "open", " | writer=lead-beo-skills"),
            row("merge", "open", record),
            row("merge", "open", record + " | words=none"),
            row("local-ops", gate_row.LOCAL_OPS_STATUS, record),
            row("repair-grant", "recorded:granted", record),
            row("cutover", gate_row.CUTOVER_STATUS, record),
            row("standing-delegation", gate_row.STANDING_DELEGATION_STATUS,
                record + " | who=w | scope=s | conditions=c | expiry=e"),
        ]
        for text in rows:
            with self.subTest(text), self.assertRaises(gate_row.RowError):
                gate_row.check(text, self.repo, gate_row.LedgerState.of([]))
        cutover = row("cutover", gate_row.CUTOVER_STATUS,
                      f"{record} | archive={'a' * 64} | words=none | note=n")
        with self.assertRaises(gate_row.RowError):
            gate_row.check(cutover, self.repo)

    def test_check_refuses_hand_edits_the_writer_never_emits(self):
        self.assertEqual(self.append(), 0, self.err.getvalue())
        push, _ = self.valid_push_row()
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        merge, review = rows[0], rows[1]
        head, mid = self.rev("HEAD"), self.rev("HEAD~1")
        tampers = [
            (merge, "status=resolved:human", "status=Done"),
            (merge, "kind=merge", "kind=Merge"),
            (merge, "note=merged the reviewed head", "writer=lead-beo-skills"),
            (merge, "note=merged the reviewed head", "note=merged|the reviewed head"),
            (merge, "note=merged the reviewed head", 'note=merged "the" reviewed head'),
            (merge, 'quote="merge it"', 'quote="merge it'),
            (merge, 'quote="merge it"', 'quote=merge it"'),
            (review, f"main@{head}", f"main@{mid}"),
            (push, f"main@{head}", f"main@{mid}"),
        ]
        for row, before, after in tampers:
            with self.subTest(after):
                tampered = row.replace(before, after, 1)
                self.assertNotEqual(tampered, row)
                with self.assertRaises(gate_row.RowError):
                    gate_row.check(tampered, self.repo, gate_row.LedgerState.of(rows[:rows.index(row)]))

    def test_an_unknown_commit_is_refused_naming_git_rev_parse_verify(self):
        bad = "1" * 40
        appends = {
            "--after": lambda: self.append_local_ops("--after", f"main@{bad}"),
            "--head": lambda: self.append("--head", f"main@{bad}", "--record", "reconstruction"),
        }
        for name, append in appends.items():
            with self.subTest(name):
                self.assertEqual(append(), 1)
                self.assertIn(f"git rev-parse --verify {bad}^{{commit}} failed: fatal: Needed a single revision",
                              self.err.getvalue())

    def test_an_empty_special_field_value_is_refused_by_check(self):
        self.assertEqual(self.append_local_ops(), 0, self.err.getvalue())
        self.ledger.write_text(self.last_row().replace("op=git status --short", "op=") + "\n", encoding="utf-8")
        self.assertEqual(self.check_last(), 1)
        self.assertIn("op= is required", self.err.getvalue())

    def test_a_field_without_an_equals_sign_is_refused_naming_it(self):
        self.assertEqual(self.append_local_ops(), 0, self.err.getvalue())
        row = self.last_row()
        for edited, message in (
            (row.replace(" | words=", " | junk | words="), "field 'junk' is not in the row schema"),
            (row.replace(" | quote=", " | op=x | quote="), "field 'op' is out of order or duplicated"),
        ):
            with self.subTest(message):
                self.err.truncate(0)
                self.err.seek(0)
                self.ledger.write_text(edited + "\n", encoding="utf-8")
                self.assertEqual(self.check_last(), 1)
                self.assertIn(message, self.err.getvalue())

    def test_a_row_in_a_linked_worktree_records_that_worktrees_branch_and_head(self):
        worktree = self.tmp / "wt"
        self.git("worktree", "add", "-q", "-b", "side", str(worktree))
        (worktree / "s.txt").write_text("s\n")
        subprocess.run(["git", "-C", str(worktree), "add", "s.txt"], check=True, stdin=subprocess.DEVNULL)
        subprocess.run(["git", "-C", str(worktree), "commit", "-qm", "s1"], check=True, stdin=subprocess.DEVNULL)
        side = subprocess.run(["git", "-C", str(worktree), "rev-parse", "HEAD"],
                              capture_output=True, text=True, check=True, stdin=subprocess.DEVNULL).stdout.strip()
        self.repo = worktree
        self.assertEqual(self.append_local_ops(), 0, self.err.getvalue())
        self.assertIn(f" | side@{side} | ", self.last_row())

    def test_a_row_on_a_detached_head_records_the_branch_as_HEAD(self):
        self.git("checkout", "-q", "--detach")
        self.assertEqual(self.append_local_ops(), 0, self.err.getvalue())
        self.assertIn(f" | HEAD@{self.rev('HEAD')} | ", self.last_row())

    def test_check_refuses_an_empty_field(self):
        self.assertEqual(self.append_local_ops(), 0, self.err.getvalue())
        self.ledger.write_text(self.last_row().replace(" | words=", " |  | words=") + "\n", encoding="utf-8")
        before = self.ledger.read_bytes()
        self.assertEqual(self.check_last(), 1)
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_open_gates_refuses_a_ledger_row_with_an_invalid_status_or_prev_hash(self):
        for old, new in (("status=recorded:local-ops", "status=BAD"), (None, "prev_hash=zz")):
            with self.subTest(new):
                self.ledger.write_text("# Gate ledger — test\n\n")
                self.assertEqual(self.append_local_ops(), 0, self.err.getvalue())
                self.assertEqual(self.append_local_ops(), 0, self.err.getvalue())
                first, second = [l for l in self.ledger.read_text().splitlines() if gate_row.ID_RE.match(l)]
                old = old or f"prev_hash={gate_row.row_hash(first)}"
                self.ledger.write_text(f"# Gate ledger — test\n\n{first}\n{second.replace(old, new)}\n",
                                       encoding="utf-8")
                before = self.ledger.read_bytes()
                self.assertEqual(self.run_main(["--ledger", str(self.ledger), "--open-gates"]), 1)
                self.assertEqual(self.ledger.read_bytes(), before)

    def run_in_locale(self, locale: str, *argv: str) -> subprocess.CompletedProcess:
        env = {k: v for k, v in os.environ.items() if k not in ("PYTHONUTF8", "PYTHONIOENCODING", "LANG")}
        return subprocess.run([sys.executable, "-c", "import sys; sys.path.insert(0, sys.argv[1]); import gate_row; "
                               "sys.exit(gate_row.main(sys.argv[2:]))", str(SCRIPTS), *argv],
                              capture_output=True, env={**env, "LC_ALL": locale}, stdin=subprocess.DEVNULL)

    def test_a_quote_file_is_read_as_utf8_whatever_the_locale(self):
        quote = self.tmp / "quote.txt"
        quote.write_text("café\n", encoding="utf-8")
        proc = self.run_in_locale("en_US.ISO8859-1", "--ledger", str(self.ledger), "--repo", str(self.repo),
                                  "--kind", "merge", "--status", "resolved:human", "--words", "human",
                                  "--note", "merged", "--quote-file", str(quote))
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn('quote="café"'.encode("latin-1"), proc.stdout)

    def test_a_mailbox_is_read_as_utf8_whatever_the_locale(self):
        self.ledger.write_text("# Gate ledger\n\n", encoding="utf-8")
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "push-gate", "--status", "open", "--words", "none", "--note", "push gate",
        ]), 0, self.err.getvalue())
        mailbox = self.tmp / "mailbox.md"
        mailbox.write_text(f"## lead -> supervisor | 2026-09-25T01:02:03Z | ATTENTION G1 café | HEAD {self.rev('HEAD')}\n",
                           encoding="utf-8")
        proc = self.run_in_locale("en_US.US-ASCII", "--ledger", str(self.ledger), "--repo", str(self.repo),
                                  "--check", "--mailbox", str(mailbox))
        self.assertEqual(proc.returncode, 0, proc.stderr)


    def test_every_line_separator_in_quote_quote_file_or_note_is_refused_and_writes_nothing(self):
        quote_file = self.tmp / "quote.txt"
        before = self.ledger.read_bytes()
        for sep in (*gate_row.LINE_BREAKS, "\r\n"):
            quote_file.write_bytes(f"a{sep}b".encode("utf-8"))
            for name, extra in (
                ("quote", ("--quote", f"a{sep}b")),
                ("quote", ("--quote", "", "--quote-file", str(quote_file))),
                ("note", ("--note", f"a{sep}b")),
            ):
                with self.subTest(sep=sep, args=extra[::2]):
                    self.assertEqual(self.append(*extra), 1)
                    self.assertIn(f"{name}= is one line", self.err.getvalue())
                    self.assertEqual(self.ledger.read_bytes(), before)
        self.assertEqual(self.append(), 0, self.err.getvalue())
        self.assertEqual(self.check_last(), 0, self.err.getvalue())

    def test_a_quote_file_ending_in_a_lone_cr_is_refused(self):
        # newline="" keeps the CR; a universal-newline read would turn it into
        # the one trailing newline the strip removes and admit the row.
        quote_file = self.tmp / "quote.txt"
        quote_file.write_bytes(b"merge it\r")
        before = self.ledger.read_bytes()
        self.assertEqual(self.append("--quote", "", "--quote-file", str(quote_file)), 1)
        self.assertIn("quote= is one line; it holds line separator '\\r'", self.err.getvalue())
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_every_ledger_read_refuses_a_chained_row_holding_a_line_separator_by_field(self):
        cases = (
            ("note=", self.fixture_row("G2", "open", words="none", quote="", note="a\x0cb")),
            ("quote=", self.fixture_row("G2", "resolved:x", quote="a\u2029b")),
            ("words=", self.fixture_row("G2", "open", words="none\x85", quote="")),
        )
        for label, row in cases:
            with self.subTest(label):
                rows = self.chained([self.fixture_row("G1", "open", words="none", quote=""), row])
                self.ledger.write_text("\n".join(rows) + "\n", encoding="utf-8")
                for mode in ("--check", "--open-gates"):
                    self.assertEqual(self.run_main(
                        ["--ledger", str(self.ledger), "--repo", str(self.repo), mode]), 1)
                    self.assertIn(f"row 'G2' {label} is one line", self.err.getvalue())

    def test_a_malformed_ledger_is_refused_cleanly_by_every_read(self):
        first = self.fixture_row("G1", "open", words="none", quote="")
        second = self.fixture_row("G2", "open", words="none", quote="")
        cases = (
            ("empty field", self.chained([first, second.replace(" | record=", " |  | record=")]),
             "row 'G2' field 6 is empty or holds |"),
            ("field holding |", self.chained([first, second.replace(" | record=", " | | record=")]),
             "row 'G2' field 6 is empty or holds |"),
            ("short predecessor", self.chained(['G1 | quote=""', second]),
             "row 'G1' has 1 fields before quote=, expected at least 5"),
            ("invalid single status", [first.replace("status=open", "status=bogus")],
             "field 'status=bogus' is not a valid status="),
            ("invalid single prev_hash", [first, second.replace(" | words=", " | prev_hash=zz | words=")],
             "field 'prev_hash=zz' is not a 64-character lowercase hex prev_hash="),
            *(
                (f"{bad} id row", self.chained([first, second.replace("G2 | ", f"{bad} | ", 1)]),
                 "row has no G id")
                for bad in ("S3", "G-1", "G1x")
            ),
        )
        for name, rows, message in cases:
            self.ledger.write_text("\n".join(rows) + "\n", encoding="utf-8")
            for mode in ("--check", "--open-gates"):
                with self.subTest(name, mode=mode):
                    self.assertEqual(self.run_main(
                        ["--ledger", str(self.ledger), "--repo", str(self.repo), mode]), 1)
                    self.assertIn(message, self.err.getvalue())
        self.ledger.write_bytes(first.encode("utf-8") + b"\n" + b"G2 | caf\xe9\n")
        for argv in (["--check"], ["--open-gates"], [*self.append_args()]):
            with self.subTest("non-UTF-8", argv=argv[:1]):
                self.assertEqual(self.run_main(["--ledger", str(self.ledger), "--repo", str(self.repo), *argv]), 1)
                self.assertIn("ledger is not UTF-8", self.err.getvalue())

    def append_args(self) -> list[str]:
        return ["--kind", "merge", "--status", "open", "--words", "none", "--note", "n"]


if __name__ == "__main__":
    unittest.main()
