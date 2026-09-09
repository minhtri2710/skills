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

    def append_review(self) -> int:
        return gate_row.main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "review", "--status", "recorded:review",
            "--words", "seat", "--note", "review passed", "--quote", "PASS",
        ])

    def invoke(self) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = pre_push_guard.main(["--repo", str(self.repo), "--ledger", str(self.ledger)])
        return code, out.getvalue(), err.getvalue()

    def test_head_with_gate_row_written_review_is_allowed(self):
        self.assertEqual(self.append_review(), 0)
        code, out, err = self.invoke()
        self.assertEqual(code, 0)
        self.assertIn("passing review row", out)
        self.assertEqual(err, "")

    def test_head_with_no_review_row_is_refused(self):
        code, _, err = self.invoke()
        self.assertEqual(code, 1)
        self.assertIn("review PASS row", err)


if __name__ == "__main__":
    unittest.main()
