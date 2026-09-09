#!/usr/bin/env python3
"""Unit tests for the review-and-push pre-push guard."""
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
        self.addCleanup(self._tmp.cleanup)

    def git(self, *args: str) -> None:
        subprocess.run(["git", "-C", str(self.repo), *args], check=True,
                       capture_output=True, text=True)

    def head(self) -> str:
        return subprocess.run(["git", "-C", str(self.repo), "rev-parse", "HEAD"],
                              check=True, capture_output=True, text=True).stdout.strip()

    def rows(self, *rows: str) -> None:
        head = self.head()
        self.ledger.write_text("\n".join(
            row.replace("<head>", head) for row in rows
        ) + "\n")

    def invoke(self) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = pre_push_guard.main(["--repo", str(self.repo), "--ledger", str(self.ledger)])
        return code, out.getvalue(), err.getvalue()

    def test_head_with_review_and_push_rows_is_allowed(self):
        self.rows(
            'G1 | 2026-01-01T00:00:00Z | kind=review | main@<head> | '
            'status=recorded:review | record=timely | words=none | note=review | quote=""',
            'G2 | 2026-01-01T00:00:00Z | kind=push | main@<head> | '
            'status=resolved:standing-waiver | record=timely | words=none | note=push | quote=""',
        )
        code, _, _ = self.invoke()
        self.assertEqual(code, 0)

    def test_head_with_neither_row_is_refused(self):
        self.rows(
            'G1 | 2026-01-01T00:00:00Z | kind=merge | main@<head> | '
            'status=resolved:standing-waiver | record=timely | words=none | note=merge | quote=""',
        )
        code, _, err = self.invoke()
        self.assertNotEqual(code, 0)
        self.assertIn("review PASS row", err)
        self.assertIn("push row", err)

    def test_head_with_only_one_required_row_is_refused(self):
        self.rows(
            'G1 | 2026-01-01T00:00:00Z | kind=review | main@<head> | '
            'status=resolved:review | record=timely | words=none | note=review | quote=""',
        )
        code, _, err = self.invoke()
        self.assertNotEqual(code, 0)
        self.assertIn("push row", err)


if __name__ == "__main__":
    unittest.main()
