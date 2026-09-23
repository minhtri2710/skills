#!/usr/bin/env python3
"""Unit tests for gate_row.py (C19 — the ledger row is derived, not typed)."""
from __future__ import annotations

import contextlib
import hashlib
import io
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
                                    capture_output=True, text=True)
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
        self._tmp = tempfile.TemporaryDirectory(dir="/private/tmp")
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
            "--kind", "merge", "--status", "resolved:standing-waiver",
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
                              capture_output=True, text=True, check=True).stdout.strip()

    def rev(self, ref: str) -> str:
        return subprocess.run(["git", "-C", str(self.repo), "rev-parse", ref],
                              capture_output=True, text=True, check=True).stdout.strip()

    def last_row(self) -> str:
        return [l for l in self.ledger.read_text().splitlines()
                if gate_row.ID_RE.match(l)][-1]

    def test_relative_ledger_is_refused_and_writes_nothing(self):
        # A2 lesson: a bare relative --ledger against a reset cwd treats a
        # nonexistent repo-local gates.md as empty and silently births a stray
        # G1. Refuse a non-absolute ledger path before touching the filesystem.
        import os
        scratch = self.tmp / "cwd"
        scratch.mkdir()
        prev = os.getcwd()
        os.chdir(scratch)
        try:
            rc = self.run_main([
                "--ledger", "gates.md", "--repo", str(self.repo),
                "--kind", "merge", "--status", "resolved:standing-waiver",
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
        """Give fixture rows the ledger's chain: each row after the first hashes its predecessor."""
        out = rows[:1]
        for row in rows[1:]:
            out.append(row.replace(" | words=", f" | prev_hash={gate_row.row_hash(out[-1])} | words=", 1))
        return out

    def open_gates(self) -> list[str]:
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--open-gates",
        ]), 0)
        return self.out.getvalue().splitlines()

    def test_words_is_required_for_append(self):
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "merge", "--status", "resolved:standing-waiver",
            "--note", "merged the reviewed head", "--quote", "merge it",
        ]), 1)
        self.assertIn("--words is required", self.err.getvalue())
        self.assertEqual(self.ledger.read_text(), "# Gate ledger — test\n\n")

    def test_round_trip(self):
        """A row the script writes is a row --check accepts, unchanged."""
        self.assertEqual(self.append(), 0)
        written = self.last_row()
        self.assertEqual(self.run_main(
            ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]), 0)
        self.assertEqual(self.last_row(), written)

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

    def test_monotonic_ledger_passes_check(self):
        self.assertEqual(self.append(), 0)
        self.assertEqual(self.append(), 0)
        self.assertEqual(self.run_main(
            ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]), 0)

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
            backdated = gate_row.build(args, self.repo, existing_rows)
        self.ledger.write_text(
            self.ledger.read_text(encoding="utf-8") + backdated + "\n", encoding="utf-8"
        )
        self.assertEqual(self.run_main(
            ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]), 1)
        self.assertIn("timestamp regression", self.err.getvalue())
        self.assertIn("2000-01-01T00:00:00Z", self.err.getvalue())

    def test_repair_cap_allows_one_repair_grant_and_check_passes(self):
        self.assertEqual(self.append_repair_grant(), 0)
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 0)

    def test_repair_cap_allows_two_repair_grants_since_boundary(self):
        self.assertEqual(self.append_repair_grant("F-1"), 0)
        self.assertEqual(self.append_repair_grant("F-2"), 0)
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 0)

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
        """Distinct finding identities mean each repair grant made progress."""
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

    def test_standing_delegation_rejects_non_human_words(self):
        before = self.ledger.read_bytes()
        self.assertEqual(self.append_standing_delegation("--words", "selected"), 1)
        self.assertIn("requires words=human", self.err.getvalue())
        self.assertEqual(self.ledger.read_bytes(), before)

    def check_last(self) -> int:
        return self.run_main(["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"])

    def append_push_grant(self, spec: str, *extra: str) -> int:
        return self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "push-grant", "--status", "open", "--writer", "supervisor",
            "--channel", "supervisor-relay:typed", "--grant", spec,
            "--words", "human", "--note", "one-shot push grant", "--quote", "push it", *extra,
        ])

    def test_push_scope_delegation_round_trips_with_a_machine_expiry(self):
        for expiry in ("until-revoked", "2030-01-01T00:00:00Z"):
            self.assertEqual(self.append_standing_delegation(
                "--expiry", expiry, "--push-scope", "origin:main,upstream:release/1"), 0, self.err.getvalue())
            row = self.last_row()
            self.assertIn(f"expiry={expiry} | push-scope=origin:main,upstream:release/1 | ", row)
            self.assertEqual(self.check_last(), 0, self.err.getvalue())

    def test_push_scope_refuses_a_free_text_expiry_and_a_malformed_scope(self):
        before = self.ledger.read_bytes()
        self.assertEqual(self.append_standing_delegation("--push-scope", "origin:main"), 1)
        self.assertIn("not an ISO-8601 UTC timestamp or until-revoked", self.err.getvalue())
        self.assertEqual(self.append_standing_delegation(
            "--expiry", "until-revoked", "--push-scope", "main"), 1)
        self.assertIn("is not <remote>:<branch>", self.err.getvalue())
        self.assertEqual(self.ledger.read_bytes(), before)
        self.assertEqual(self.append("--push-scope", "origin:main"), 1)
        self.assertIn("--push-scope is only meaningful", self.err.getvalue())

    def test_push_grant_round_trips_and_refuses_bad_shapes(self):
        base, head = self.rev("HEAD~1"), self.rev("HEAD")
        zero = "0" * 40
        self.assertEqual(self.append_push_grant(f"origin refs/heads/main push {base}..{head}"), 0,
                         self.err.getvalue())
        self.assertIn(f"grant=origin refs/heads/main push {base}..{head} | ", self.last_row())
        self.assertEqual(self.check_last(), 0, self.err.getvalue())
        self.assertEqual(self.append_push_grant(f"origin refs/heads/dead delete {base}..{zero}"), 0,
                         self.err.getvalue())
        self.assertEqual(self.check_last(), 0, self.err.getvalue())
        before = self.ledger.read_bytes()
        for spec, message in (
            (f"origin refs/heads/main push {head}..{base}", "is-ancestor"),
            (f"origin refs/heads/main push {base[:12]}..{head}", "is not <remote>"),
            (f"origin main push {base}..{head}", "is not <remote>"),
            (f"origin refs/heads/main delete {base}..{head}", "zero tip"),
            (f"origin refs/heads/main push {base}..{zero}", "op delete"),
        ):
            self.assertEqual(self.append_push_grant(spec), 1, spec)
            self.assertIn(message, self.err.getvalue())
        spec = f"origin refs/heads/main push {base}..{head}"
        self.assertEqual(self.append_push_grant(spec, "--words", "seat"), 1)
        self.assertIn("requires words=human or words=selected", self.err.getvalue())
        self.assertEqual(self.append_push_grant(spec, "--status", "resolved:instruction"), 1)
        self.assertIn("requires status=open", self.err.getvalue())
        self.assertEqual(self.append("--grant", spec), 1)
        self.assertIn("--grant is only meaningful", self.err.getvalue())
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_a_push_row_must_consume_the_open_grant_its_push_landed_under(self):
        """apexinvest-payload G511/G512: the grant named the pushed range, the push row
        resolved only the push gate, and G511 stayed open."""
        self.assertEqual(self.append_review_pass(), 0, self.err.getvalue())
        self.add_remote("HEAD")
        base, head = self.rev("HEAD~2"), self.rev("HEAD")
        self.assertEqual(self.append_push_grant(f"origin refs/heads/main push {base}..{head}"), 0,
                         self.err.getvalue())
        grant_id = self.last_row().split(" | ")[0]
        before = self.ledger.read_bytes()
        self.assertEqual(self.append("--kind", "push", "--push-base", base, "--boundary", "."), 1)
        self.assertIn(f"open grant {grant_id}", self.err.getvalue())
        self.assertIn(f"--resolves {grant_id}", self.err.getvalue())
        self.assertEqual(self.ledger.read_bytes(), before)
        self.assertEqual(self.append("--kind", "push", "--push-base", base, "--boundary", ".",
                                     "--resolves", grant_id), 0, self.err.getvalue())
        self.assertEqual(self.check_last(), 0, self.err.getvalue())
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        self.ledger.write_text("# Gate ledger — test\n\n" + "\n".join(
            rows[:-1] + [rows[-1].replace(f" | resolves={grant_id}", "")]) + "\n", encoding="utf-8")
        self.assertEqual(self.check_last(), 1)
        self.assertIn(f"open grant {grant_id}", self.err.getvalue())

    def test_a_push_row_ignores_grants_for_another_branch_or_range(self):
        self.assertEqual(self.append_review_pass(), 0, self.err.getvalue())
        self.add_remote("HEAD")
        base, mid, head = self.rev("HEAD~2"), self.rev("HEAD~1"), self.rev("HEAD")
        self.assertEqual(self.append_push_grant(f"origin refs/heads/other push {base}..{head}"), 0)
        self.assertEqual(self.append_push_grant(f"upstream refs/heads/main push {base}..{head}"), 0)
        self.assertEqual(self.append_push_grant(f"origin refs/heads/main push {base}..{mid}"), 0)
        self.assertEqual(self.append("--kind", "push", "--push-base", base, "--boundary", "."), 0,
                         self.err.getvalue())
        self.assertEqual(self.check_last(), 0, self.err.getvalue())

    def test_a_standing_delegation_is_revoked_once_by_a_resolving_row(self):
        self.assertEqual(self.append_standing_delegation(
            "--expiry", "until-revoked", "--push-scope", "origin:main"), 0)
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
            "--kind", "merge", "--status", "resolved:standing-waiver",
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
            "--kind", "merge", "--status", "resolved:standing-waiver",
            "--words", "human", "--note", "merged the reviewed head",
            "--quote-file", str(quote_file),
        ]), 0)
        self.assertTrue(self.last_row().endswith('quote="runtime denied command"'))

    def test_quote_file_refuses_an_interior_newline(self):
        quote_file = self.tmp / "refused-command.txt"
        quote_file.write_text("first\nsecond\n", encoding="utf-8")
        before = self.ledger.read_text()
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "merge", "--status", "resolved:standing-waiver",
            "--words", "human", "--note", "merged the reviewed head",
            "--quote-file", str(quote_file),
        ]), 1)
        self.assertIn("quote= is one line", self.err.getvalue())
        self.assertEqual(self.ledger.read_text(), before)

    def test_quote_and_quote_file_are_mutually_exclusive(self):
        quote_file = self.tmp / "refused-command.txt"
        quote_file.write_text("file quote", encoding="utf-8")
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "merge", "--status", "resolved:standing-waiver",
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
            "--kind", "merge", "--status", "resolved:standing-waiver",
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

    def test_ids_are_consecutive_and_read_from_the_file(self):
        self.assertEqual(self.append(), 0)
        self.assertEqual(self.append(), 0)
        ids = [l.split(" | ")[0] for l in self.ledger.read_text().splitlines()
               if gate_row.ID_RE.match(l)]
        self.assertEqual(ids, ["G1", "G2"])

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

    def test_open_gate_mode_uses_last_rows_and_structured_resolves_only(self):
        rows = [
            self.fixture_row("G26", "open", "none", ""),
            self.fixture_row("G26", "open", "none", ""),
            self.fixture_row("G26", "resolved:done"),
            self.fixture_row("G27", "open", "none", "", note="prose says resolves=G27"),
            self.fixture_row("G28", "open", "none", ""),
            self.fixture_row("G29", "resolved:done", resolves="G28"),
            self.fixture_row("G30", "open", "none", ""),
        ]
        self.ledger.write_text("# fixture\n" + "\n".join(self.chained(rows)) + "\n")
        self.assertEqual(self.open_gates(), ["G27", "G30"])

    def test_words_values_require_the_matching_quote_presence(self):
        self.assertEqual(self.append("--status", "open", "--words", "none", "--quote", ""), 0)
        for words in ("seat", "human", "selected"):
            self.assertEqual(self.append("--words", words, "--quote", words), 0)
        self.assertEqual(self.append("--words", "none", "--quote", "not empty"), 1)
        self.assertIn("words=none", self.err.getvalue())
        self.assertEqual(self.append("--words", "seat", "--quote", ""), 1)
        self.assertIn("words=none", self.err.getvalue())

    def test_slug_ids_are_resolved_by_first_field(self):
        self.ledger.write_text(self.fixture_row("decision-abc", "open", "none", "") + "\n")
        self.assertEqual(self.append("--resolves", "decision-abc"), 0)
        self.assertIn("resolves=decision-abc", self.last_row())
        self.assertEqual(self.open_gates(), [])

    def test_a_count_that_does_not_match_the_range_is_rejected(self):
        """The recount rule as code: parts that do not sum fail --check."""
        base, head = self.rev("HEAD~2"), self.rev("HEAD")
        row = (f'G2 | 2026-09-06T00:00:00Z | kind=push | main@{head} | '
               f'status=resolved:standing-waiver | record=timely | '
               f'push={base}..{head} count=7 boundary="f1.txt f2.txt" '
               f'boundary-check="" | words=human | note=n | quote="q"')
        prior = self.fixture_row("G1", "recorded:review-pass", kind="review")
        with self.assertRaises(gate_row.RowError) as ctx:
            gate_row.check(self.chained([prior, row])[1], self.repo, [prior])
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
                       check=True, capture_output=True)
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
                       check=True, capture_output=True)
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
                       check=True, capture_output=True)
        subprocess.run(["git", "-C", str(other), "config", "user.email", "t@example.invalid"],
                       check=True)
        subprocess.run(["git", "-C", str(other), "config", "user.name", "t"], check=True)
        (other / "unknown.txt").write_text("unknown\n")
        subprocess.run(["git", "-C", str(other), "add", "unknown.txt"], check=True)
        subprocess.run(["git", "-C", str(other), "commit", "-qm", "unknown remote commit"], check=True)
        subprocess.run(["git", "-C", str(other), "push", "-q", "origin", "main"],
                       check=True, capture_output=True)
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
            gate_row.check(row, self.repo, prior)

    def test_a_push_block_on_a_non_push_row_is_refused_by_check(self):
        head = self.rev("HEAD")
        row = (f'G2 | 2026-09-06T00:00:00Z | kind=merge | main@{head} | '
               f'status=resolved:done | record=timely | '
               f'push={self.rev("HEAD~1")}..{head} count=1 boundary="." '
               f'boundary-check="" | words=human | note=n | quote="q"')
        with self.assertRaisesRegex(gate_row.RowError, "push= is only on a kind=push row"):
            gate_row.check(row, self.repo, [self.fixture_row("G1", "resolved:done")])

    def test_a_pipe_in_note_is_refused(self):
        """note= is the seat's own words, so it fails closed on the delimiter."""
        self.assertEqual(self.append("--note", "a | b"), 1)

    def test_a_pipe_in_quote_is_kept_verbatim(self):
        """G33: the Human typed a literal | inside their own words (G52)."""
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
        """The drifted shape this project actually wrote must not pass."""
        head = self.rev("HEAD")
        row = (f'G9 | 2026-09-06T00:00:00Z | kind=push | main@{head} | '
               f'status=resolved:standing-waiver | authority=G64 | project=beo-skills | '
               f'record=timely | words=human | note=n | quote="q"')
        with self.assertRaises(gate_row.RowError) as ctx:
            gate_row.check(row, self.repo)
        self.assertIn("not in the row schema", str(ctx.exception))

    def add_empty_remote(self) -> None:
        """An empty bare origin, for a first publication test."""
        bare = self.tmp / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "remote", "add", "origin", str(bare)],
                       check=True)

    def add_remote(self, ref: str) -> None:
        """A bare origin holding `ref`, so ls-remote answers for real."""
        bare = self.tmp / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "remote", "add", "origin", str(bare)],
                       check=True)
        subprocess.run(["git", "-C", str(self.repo), "push", "-q", "origin",
                        f"{self.rev(ref)}:refs/heads/main"], check=True, capture_output=True)

    def test_a_push_row_whose_push_has_not_landed_is_refused(self):
        """origin is a commit behind, so the row would claim a push that did not happen."""
        self.assertEqual(self.append_review_pass(), 0)
        self.add_remote("HEAD~1")
        base = self.rev("HEAD~2")
        self.assertEqual(self.append("--kind", "push", "--push-base", base), 1)

    def test_a_landed_push_derives_its_own_count_and_boundary(self):
        self.assertEqual(self.append_review_pass(), 0)
        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", self.rev("HEAD~2"),
                                     "--boundary", "f1.txt", "--boundary", "f2.txt"), 0)
        row = self.last_row()
        self.assertIn("count=2", row)
        self.assertIn('boundary="f1.txt f2.txt"', row)
        self.assertIn('boundary-check=""', row)

    def test_a_path_outside_the_boundary_is_named(self):
        self.assertEqual(self.append_review_pass(), 0)
        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", self.rev("HEAD~2"),
                                     "--boundary", "f1.txt"), 0)
        row = self.last_row()
        self.assertIn('boundary="f1.txt"', row)
        self.assertIn('boundary-check="f2.txt"', row)

    def test_a_path_added_and_deleted_inside_the_range_is_still_named(self):
        """S1 F002's own reproduction. The two end trees agree; the union does not.

        This is the one input where a net `diff --name-only <base>..<head>` and the
        doctrine's `rev-list | diff-tree` union disagree, and it disagrees in the
        direction that lets an out-of-boundary write through clean.
        """
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
        """The shape three ledgers actually wrote: one --boundary holding a joined list.

        `--boundary` is `action="append"`, one flag per path, so a joined value is a
        single string no path can equal or sit under. Every changed path then reads
        as outside the boundary and the row is indistinguishable from one that
        declared no boundary at all — which is why it fails closed here instead.
        """
        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", self.rev("HEAD~2"),
                                     "--boundary", "f1.txt f2.txt"), 1)

    def test_a_changed_path_holding_a_space_is_refused(self):
        """boundary-check joins paths with spaces, so such a path cannot be read back."""
        base = self.rev("HEAD")
        (self.repo / "two words.txt").write_text("x\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "a path with a space")
        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", base,
                                     "--boundary", "docs"), 1)

    def valid_push_row(self) -> tuple[str, list[str]]:
        """One push row the script built itself, with the boundary it was built against."""
        boundary = ["f1.txt", "f2.txt"]
        self.assertEqual(self.append_review_pass(), 0)
        self.add_remote("HEAD")
        self.assertEqual(self.append(
            "--kind", "push", "--push-base", self.rev("HEAD~2"),
            "--channel", "supervisor-relay:typed", "--writer", "lead-beo-skills",
            *[a for b in boundary for a in ("--boundary", b)]), 0)
        return self.last_row(), boundary

    def test_the_control_row_still_checks_out(self):
        """The matrix below only means something if the unmodified row passes."""
        row, boundary = self.valid_push_row()
        prior_rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))[:-1]
        gate_row.check(row, self.repo, prior_rows)

    def test_every_tamper_the_receive_record_found_passing_is_now_refused(self):
        """S1 F001's six-of-six matrix: one field hand-edited at a time, re-checked."""
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
                    gate_row.check(tampered, self.repo, prior_rows)

    def test_check_derives_a_push_row_with_no_boundary_flag(self):
        """The point of the slice: every input the check needs is in the row.

        Before the boundary was carried in the block, this exact invocation was
        refused — the caller had to re-supply the declared paths from memory,
        which is a derived field taking an underived input.
        """
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
        """The append-only file does not get a row the same command then rejects.

        The refusal moved from after the write to before it: `build` needs the
        boundary to derive the block at all, so a missing one fails while the
        ledger is still untouched.
        """
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

    def test_a_review_row_round_trips_its_range(self):
        self.assertEqual(self.append_review_pass(), 0)
        self.assertRegex(self.last_row(), r"review=[0-9a-f]{7,40}\.\.[0-9a-f]{7,40} count=2")
        self.assertEqual(self.run_main(
            ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]), 0)

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
        """`build` cannot write one, so only a hand-edited row carries it."""
        row, _ = self.valid_push_row()
        empty = row.replace('boundary="f1.txt f2.txt"', 'boundary=""')
        self.assertNotEqual(empty, row)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        with self.assertRaises(gate_row.RowError) as ctx:
            gate_row.check(empty, self.repo, rows[:-1])
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
        """G104 and G109: a merge deletes the branch, the row stays checkable.

        The head is verified as an object, so the row is re-derivable from the
        checkout for as long as the commit is reachable.
        """
        self.git("checkout", "-q", "-b", "topic")
        self.assertEqual(self.append(), 0)
        row = self.last_row()
        self.assertIn("topic@", row)
        self.git("checkout", "-q", "main")
        self.git("branch", "-D", "topic")
        gate_row.check(row, self.repo)

    def test_the_branch_label_is_no_longer_verified_and_that_is_the_trade(self):
        """Stated as a test so the loss is on the record, not discovered later.

        A row names the branch its head sat on. That is history, not a fact any
        command re-derives: once the branch is deleted or moved, nothing in the
        repository says what a commit was on. Verifying it against live refs
        made the same row pass today and fail tomorrow, which is the failure
        `test_a_row_outlives_the_branch_that_named_it` records. The head SHA
        carries the verification instead, and the label is read as prose.
        """
        row, _ = self.valid_push_row()
        relabelled = row.replace("main@", "nonexistent-branch@")
        self.assertNotEqual(relabelled, row)
        prior_rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))[:-1]
        gate_row.check(relabelled, self.repo, prior_rows)
        with self.assertRaises(gate_row.RowError):
            gate_row.check(row.replace(f"main@{self.rev('HEAD')}", f"main@{'0' * 40}"),
                           self.repo)

    def test_a_kind_push_row_carries_all_four_push_fields_or_no_row_exists(self):
        """The acceptance criterion stated on row CONTENT, not on --check's verdict.

        `--check` is the instrument that could not see this defect: on the parent
        it printed a byte-identical `ok` for a verified push row and for a
        vacuous one, so a criterion phrased as "--check passes" is satisfied by
        exactly the row the slice exists to prevent. Phrased on content, it is
        not: either the row holds the range, the count, the declared boundary and
        the boundary-check, or the append was refused and no row exists at all.
        """
        self.assertEqual(self.append_review_pass(), 0)
        self.add_remote("HEAD")
        before = self.ledger.read_text()

        # Arm A: kind=push with no --push-base. No row may exist.
        self.assertEqual(self.append("--kind", "push", "--boundary", "f1.txt"), 1)
        self.assertEqual(self.ledger.read_text(), before)

        # Arm B: the same row supplied properly. Every field present, by content.
        self.assertEqual(self.append(
            "--kind", "push", "--push-base", self.rev("HEAD~2"),
            "--boundary", "f1.txt", "--boundary", "f2.txt"), 0)
        row = self.last_row()
        self.assertIn("kind=push", row)
        for field in ("push=", "count=", 'boundary="', 'boundary-check="'):
            self.assertIn(field, row, f"a kind=push row must carry {field}")
        self.assertRegex(row, r"push=[0-9a-f]{7,40}\.\.[0-9a-f]{7,40} count=\d+ "
                              r'boundary="[^"]+" boundary-check="[^"]*"')

    def test_a_push_row_without_push_base_never_reaches_the_ledger(self):
        """The live defect B7 hit: kind and block were controlled independently.

        The parent gated the whole block on `--push-base`, so this exact
        invocation appended `kind=push` with no range, no count, no boundary and
        no boundary-check, skipped the `ls-remote` proof that the push landed,
        and silently dropped the `--boundary` that was passed. The row asserted a
        push and carried nothing that could contradict it.
        """
        self.assertEqual(self.append_review_pass(), 0)
        self.add_remote("HEAD")
        before = self.ledger.read_text()
        self.assertEqual(self.append("--kind", "push", "--boundary", "f1.txt"), 1)
        self.assertIn("a push row needs --push-base", self.err.getvalue())
        self.assertEqual(self.ledger.read_text(), before, "the refused row landed anyway")

    def test_a_kind_push_row_with_no_push_block_is_refused_by_check(self):
        """The other half: the checker confirmed such a row instead of failing it.

        `check` validated a push block only where one was present, so a
        `kind=push` row without one was checked against nothing and returned
        `ok`. Both halves are needed — repairing `build` alone still passes every
        row already written that way.
        """
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
        """An argument accepted and silently ignored is the same defect mirrored.

        The parent emitted a push block on any row given `--push-base`, whatever
        its kind. Tying the block to the kind closes that direction too, and says
        so instead of quietly doing nothing.
        """
        self.assertEqual(self.append_review_pass(), 0)
        self.add_remote("HEAD")
        before = self.ledger.read_text()
        self.assertEqual(self.append("--push-base", self.rev("HEAD~2"),
                                     "--boundary", "f1.txt"), 1)
        self.assertIn("only meaningful on a push row", self.err.getvalue())
        self.assertEqual(self.ledger.read_text(), before, "the refused row landed anyway")

    def test_boundary_on_a_non_push_row_is_refused_rather_than_dropped(self):
        """The other half of the mirror, and the defect this slice itself left.

        The first pass refused `--push-base` on a non-push row and left
        `--boundary` accepted and silently discarded — the same class the slice
        exists to close, reintroduced one line away from the fix. Both arguments
        only mean anything inside a push block, so both are refused when there is
        no block to put them in.
        """
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

    def test_check_refuses_a_non_first_row_without_prev_hash_by_position(self):
        self.assertEqual(self.append(), 0)
        self.assertEqual(self.append(), 0)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        stripped = rows[1].replace(" | prev_hash=" + gate_row.row_hash(rows[0]), "")
        with self.assertRaisesRegex(gate_row.RowError, "prev_hash= is missing; every row after the first"):
            gate_row.check(stripped, self.repo, [rows[0]], self.ledger)

    def test_intact_chain_is_verified_on_check_and_open_gate_read(self):
        for _ in range(3):
            self.assertEqual(self.append(), 0)
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 0)
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--open-gates",
        ]), 0)
        self.assertEqual(self.out.getvalue(), "")

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
        """The shape six rows across two ledgers already carry.

        `--boundary` is `action="append"`, one flag per path; a seat that passes
        all its paths joined in a single flag declares one string no path can
        match, so every path lands outside and the row records the entire
        changed set. That row asserts a breach that did not happen, and against
        an empty boundary the derivation reproduces it exactly.
        """
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


class CutoverTest(unittest.TestCase):
    """A fresh ledger born from its archived predecessor by one kind=cutover row."""

    run_main = GateRowTest.run_main
    append = GateRowTest.append
    append_handoff = GateRowTest.append_handoff
    last_row = GateRowTest.last_row

    def setUp(self):
        GateRowTest.setUp(self)
        self.assertEqual(self.append(), 0)
        self.assertEqual(self.append_handoff(), 0)
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "push-gate", "--status", "open", "--words", "none",
            "--note", "push gate awaiting the Human",
        ]), 0)
        self.archive = self.tmp / gate_row.LEGACY_LEDGER
        self.ledger.rename(self.archive)
        self.ledger.write_text("# Gate ledger — test\n\n")

    def cutover(self, *extra: str) -> int:
        return self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "cutover", "--status", "recorded:cutover",
            "--words", "seat", "--note", "ledger cut over", "--quote", "cutover", *extra,
        ])

    def check_main(self) -> int:
        return self.run_main(["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"])

    def test_cutover_continues_ids_and_binds_the_archive_bytes(self):
        archive_bytes = self.archive.read_bytes()
        self.assertEqual(self.cutover(), 0)
        row = self.last_row()
        self.assertTrue(row.startswith("G4 | "))
        self.assertIn(f"archive={hashlib.sha256(archive_bytes).hexdigest()}", row)
        self.assertIn("status=recorded:cutover", row)
        self.assertNotIn("prev_hash=", row)
        self.assertEqual(self.archive.read_bytes(), archive_bytes)
        self.assertEqual(self.check_main(), 0)

    def test_next_row_chains_to_the_cutover_and_open_gates_carry_over(self):
        self.assertEqual(self.cutover(), 0)
        cutover_row = self.last_row()
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "push-gate", "--status", "open", "--words", "none",
            "--note", "carried open gate G3",
        ]), 0)
        row = self.last_row()
        self.assertTrue(row.startswith("G5 | "))
        self.assertIn(f"prev_hash={gate_row.row_hash(cutover_row)}", row)
        self.assertEqual(self.check_main(), 0)
        self.assertEqual(self.run_main(["--ledger", str(self.ledger), "--open-gates"]), 0)
        self.assertEqual(self.out.getvalue(), "G5\n")

    def test_check_fails_when_the_archive_is_missing_edited_or_truncated(self):
        self.assertEqual(self.cutover(), 0)
        original = self.archive.read_bytes()
        self.archive.write_bytes(original.replace(b"merged the reviewed head", b"merged the reviewed HEAD"))
        self.assertEqual(self.check_main(), 1)
        self.assertIn("archive= mismatch", self.err.getvalue())
        self.archive.write_bytes(original.replace(b"Gate ledger", b"Gate Ledger"))
        self.assertEqual(self.check_main(), 1)
        self.assertIn("archive= mismatch", self.err.getvalue())
        self.archive.write_bytes(original + b"trailing prose\n")
        self.assertEqual(self.check_main(), 1)
        self.assertIn("archive= mismatch", self.err.getvalue())
        rows = gate_row.ledger_rows(original.decode("utf-8"))
        self.archive.write_text("# Gate ledger — test\n\n" + "\n".join(rows[:-1]) + "\n")
        self.assertEqual(self.check_main(), 1)
        self.assertIn("cutover id G4 is not the archive's next local id G3", self.err.getvalue())
        self.archive.unlink()
        self.assertEqual(self.check_main(), 1)
        self.assertIn("no gates.legacy.md with at least one row", self.err.getvalue())

    def test_a_non_cutover_first_row_beside_an_archive_is_refused(self):
        before = self.ledger.read_bytes()
        self.assertEqual(self.append(), 1)
        self.assertIn("kind=merge refused as the first row beside a non-empty gates.legacy.md",
                      self.err.getvalue())
        self.assertEqual(self.ledger.read_bytes(), before)
        stray = self.ledger.read_text() + self.archive.read_text().splitlines()[2] + "\n"
        self.ledger.write_text(stray)
        self.assertEqual(self.check_main(), 1)
        self.assertIn("would restart ids at G1", self.err.getvalue())

    def test_cutover_on_a_non_empty_ledger_is_refused(self):
        self.assertEqual(self.cutover(), 0)
        before = self.ledger.read_bytes()
        self.assertEqual(self.cutover(), 1)
        self.assertIn("kind=cutover refused: the ledger already holds rows", self.err.getvalue())
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_cutover_without_an_archive_is_refused(self):
        for archive_text in (None, "# Gate ledger — test\n\n"):
            self.archive.unlink(missing_ok=True)
            if archive_text is not None:
                self.archive.write_text(archive_text)
            before = self.ledger.read_bytes()
            self.assertEqual(self.cutover(), 1)
            self.assertIn("kind=cutover refused: no gates.legacy.md", self.err.getvalue())
            self.assertEqual(self.ledger.read_bytes(), before)

    def test_cutover_binds_a_real_shape_unchained_archive_by_bytes(self):
        rows = gate_row.ledger_rows(self.archive.read_text(encoding="utf-8"))
        unchained = [row.split(" | prev_hash=")[0] + " | words=" + row.split(" | words=", 1)[1]
                     for row in rows]
        self.assertTrue(all("prev_hash=" not in row for row in unchained))
        self.archive.write_text("# Gate ledger — test\n\n" + "\n".join(unchained) + "\n", encoding="utf-8")
        with self.assertRaisesRegex(gate_row.RowError, "row 'G2' is missing prev_hash="):
            gate_row.ledger_rows(self.archive.read_text(encoding="utf-8"))
        archive_bytes = self.archive.read_bytes()
        self.assertEqual(self.cutover(), 0)
        row = self.last_row()
        self.assertTrue(row.startswith("G4 | "))
        self.assertIn(f"archive={hashlib.sha256(archive_bytes).hexdigest()}", row)
        self.assertEqual(self.check_main(), 0)
        self.archive.write_bytes(archive_bytes.replace(b"merged the reviewed head", b"merged the reviewed HEAD", 1))
        self.assertEqual(self.check_main(), 1)
        self.assertIn("archive= mismatch", self.err.getvalue())

    def test_cutover_requires_its_status(self):
        before = self.ledger.read_bytes()
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "cutover", "--status", "recorded:handoff",
            "--words", "seat", "--note", "ledger cut over", "--quote", "cutover",
        ]), 1)
        self.assertIn("kind=cutover requires status=recorded:cutover", self.err.getvalue())
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_archive_field_on_another_kind_is_refused_by_check(self):
        self.assertEqual(self.cutover(), 0)
        self.assertEqual(self.append(), 0)
        cutover_row, row = gate_row.ledger_rows(self.ledger.read_text())
        archive = [f for f in cutover_row.split(" | ") if f.startswith("archive=")][0]
        forged = row.replace(" | words=", f" | {archive} | words=")
        with self.assertRaisesRegex(gate_row.RowError, "words= is missing or out of order"):
            gate_row.check(forged, self.repo, [cutover_row], self.ledger)


if __name__ == "__main__":
    unittest.main()
