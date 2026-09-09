#!/usr/bin/env python3
"""Tests for selective mailbox reads."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import mailbox  # noqa: E402


SAMPLE = """---
## lead-beo-skills -> supervisor | 2026-09-10T00:05Z | first
one
---
## lead-beo-skills -> supervisor | 2026-09-10T00:10Z | second
two
---
## lead-beo-skills -> supervisor | 2026-09-10T00:15Z | third
three
"""


class MailboxTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir="/private/tmp")
        self.path = Path(self.tmp.name) / "mailbox.md"
        self.path.write_text(SAMPLE, encoding="utf-8")
        self.addCleanup(self.tmp.cleanup)

    def test_since_excludes_boundary_and_returns_whole_entry(self):
        self.assertEqual(
            mailbox.select_entries(self.path.read_text(encoding="utf-8"), since="2026-09-10T00:10Z"),
            [
                "## lead-beo-skills -> supervisor | 2026-09-10T00:15Z | third\nthree",
            ],
        )

    def test_last_returns_whole_entries(self):
        self.assertEqual(
            mailbox.select_entries(self.path.read_text(encoding="utf-8"), last=2),
            [
                "## lead-beo-skills -> supervisor | 2026-09-10T00:10Z | second\ntwo",
                "## lead-beo-skills -> supervisor | 2026-09-10T00:15Z | third\nthree",
            ],
        )

    def test_headers_returns_only_header_lines(self):
        self.assertEqual(
            mailbox.select_entries(self.path.read_text(encoding="utf-8"), headers=True),
            [
                "## lead-beo-skills -> supervisor | 2026-09-10T00:05Z | first",
                "## lead-beo-skills -> supervisor | 2026-09-10T00:10Z | second",
                "## lead-beo-skills -> supervisor | 2026-09-10T00:15Z | third",
            ],
        )

    def test_no_selector_returns_all_entries(self):
        self.assertEqual(
            mailbox.select_entries(self.path.read_text(encoding="utf-8")),
            [
                "## lead-beo-skills -> supervisor | 2026-09-10T00:05Z | first\none",
                "## lead-beo-skills -> supervisor | 2026-09-10T00:10Z | second\ntwo",
                "## lead-beo-skills -> supervisor | 2026-09-10T00:15Z | third\nthree",
            ],
        )

    def test_since_and_last_are_mutually_exclusive(self):
        with self.assertRaisesRegex(ValueError, "since and last are mutually exclusive"):
            mailbox.select_entries(
                self.path.read_text(encoding="utf-8"),
                since="2026-09-10T00:10Z",
                last=1,
            )

    def test_main_headers_since_returns_selected_headers(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = mailbox.main(
                [
                    "--file",
                    str(self.path),
                    "--headers",
                    "--since",
                    "2026-09-10T00:05Z",
                ]
            )
        self.assertEqual(result, 0)
        self.assertEqual(
            stdout.getvalue(),
            "## lead-beo-skills -> supervisor | 2026-09-10T00:10Z | second\n"
            "## lead-beo-skills -> supervisor | 2026-09-10T00:15Z | third\n",
        )
        self.assertEqual(stderr.getvalue(), "")

    def test_main_requires_a_selector(self):
        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            result = mailbox.main(["--file", str(self.path)])
        self.assertEqual(result, 1)
        self.assertEqual(stdout.getvalue(), "")
        self.assertIn("mailbox: at least one of", stderr.getvalue())


if __name__ == "__main__":
    unittest.main()
