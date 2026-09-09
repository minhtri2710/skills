#!/usr/bin/env python3
"""Unit tests for the review-only pre-push guard."""
from __future__ import annotations

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import gate_row  # noqa: E402
import pre_push_guard  # noqa: E402


class PrePushGuardTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir="/private/tmp")
        self.tmp = Path(self._tmp.name)
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.invalid")
        self.git("config", "user.name", "t")
        (self.repo / "file.txt").write_text("content\n")
        self.git("add", "file.txt")
        self.git("commit", "-qm", "initial")
        self.ledger = self.tmp / "gates.md"
        self.ledger.write_text("# Gate ledger — test\n\n")
        self.addCleanup(self._tmp.cleanup)

    def git(self, *args: str) -> None:
        subprocess.run(["git", "-C", str(self.repo), *args], check=True,
                       capture_output=True, text=True)

    def append_review(self, status: str = "recorded:review-pass", quote: str = "PASS") -> int:
        return gate_row.main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "review", "--status", status,
            "--words", "seat", "--note", "review passed", "--quote", quote,
        ])

    def invoke(self, stdin: str = "") -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with patch.object(pre_push_guard.sys, "stdin", io.StringIO(stdin)):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = pre_push_guard.main(["--repo", str(self.repo), "--ledger", str(self.ledger)])
        return code, out.getvalue(), err.getvalue()

    def test_head_with_gate_row_written_review_pass_is_allowed(self):
        self.assertEqual(self.append_review(), 0)
        code, out, err = self.invoke()
        self.assertEqual(code, 0)
        self.assertIn("passing review row", out)
        self.assertEqual(err, "")

    def test_head_with_failed_review_is_refused(self):
        self.assertEqual(self.append_review("recorded:review-fail", "FAIL: 2 findings"), 0)
        code, _, err = self.invoke()
        self.assertEqual(code, 1)
        self.assertIn("review PASS row", err)

    def test_unreviewed_pushed_sha_is_refused_even_when_head_was_reviewed(self):
        self.assertEqual(self.append_review(), 0)
        reviewed_sha = subprocess.run(
            ["git", "-C", str(self.repo), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()

        (self.repo / "file.txt").write_text("changed\n")
        self.git("add", "file.txt")
        self.git("commit", "-qm", "second")
        pushed_sha = subprocess.run(
            ["git", "-C", str(self.repo), "rev-parse", "HEAD"],
            check=True, capture_output=True, text=True,
        ).stdout.strip()
        self.git("reset", "--hard", reviewed_sha)

        ref_line = f"refs/heads/main {pushed_sha} refs/heads/main {reviewed_sha}\n"
        code, _, err = self.invoke(ref_line)
        self.assertEqual(code, 1)
        self.assertIn(pushed_sha, err)

    def test_head_with_no_review_row_is_refused(self):
        code, _, err = self.invoke()
        self.assertEqual(code, 1)
        self.assertIn("review PASS row", err)


if __name__ == "__main__":
    unittest.main()
