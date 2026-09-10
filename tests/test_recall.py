#!/usr/bin/env python3
"""Tests for the in-memory record recall helper."""
from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
import sys

sys.path.insert(0, str(SCRIPTS))

import recall  # noqa: E402


class RecallTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.patch_root = mock.patch.object(recall, "PROJECTS_ROOT", str(self.root))
        self.patch_root.start()

    def tearDown(self):
        self.patch_root.stop()
        self.tempdir.cleanup()

    def write(self, relative, text):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")

    def run_recall(self, argv):
        output = io.StringIO()
        with redirect_stdout(output):
            code = recall.main(argv)
        return code, output.getvalue()

    def test_diacritic_free_vietnamese_query_finds_folded_text(self):
        self.write("notes/vietnam.md", "Mùa hè tạo một mốc xanh cho bản đồ.\n")

        code, output = self.run_recall(["mua he", "moc xanh"])

        self.assertEqual(code, 0)
        self.assertTrue(output.startswith("notes/vietnam.md:1  "))

    def test_rrf_fuses_two_variants(self):
        self.write("target.md", "amber circuit beacon\n")
        self.write("single.md", "amber amber amber amber\n")

        code, output = self.run_recall(["amber", "beacon"])

        self.assertEqual(code, 0)
        self.assertEqual(output.splitlines()[0].split(":", 1)[0], "target.md")

    def test_get_prints_exact_requested_span(self):
        self.write("span.md", "first\nsecond\nthird\nfourth\n")

        code, output = self.run_recall(["--get", "span.md:2:2"])

        self.assertEqual(code, 0)
        self.assertEqual(output, "second\nthird\n")

    def test_index_bonus_breaks_equal_relevance(self):
        self.write("body.md", "alpha alpha alpha beta\n")
        self.write("runs/INDEX.md", "alpha beta beta beta\n")

        code, output = self.run_recall(["alpha", "beta"])

        self.assertEqual(code, 0)
        self.assertEqual(output.splitlines()[0].split(":", 1)[0], "runs/INDEX.md")

    def test_invalid_selectors_exit_nonzero(self):
        for argv in ([], ["one"], ["--get", "bad"]):
            with self.subTest(argv=argv), self.assertRaises(SystemExit) as raised:
                with redirect_stderr(io.StringIO()):
                    recall.main(argv)
            self.assertNotEqual(raised.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
