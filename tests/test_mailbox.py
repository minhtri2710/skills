#!/usr/bin/env python3
"""Tests for selective mailbox reads."""
from __future__ import annotations

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


if __name__ == "__main__":
    unittest.main()
