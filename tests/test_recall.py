#!/usr/bin/env python3
"""Tests for the in-memory record recall helper."""
from __future__ import annotations

import io
import os
import tempfile
import unittest
from datetime import datetime, timezone
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

    def test_stamp_updates_returned_lessons_but_not_other_records(self):
        old = "2020-01-01"
        self.write(
            "demo/runs/coordination/lessons/lesson.md",
            "---\nid: lesson\nadded: 2020-01-01\nsource_run: runs/issue\napproved_by: human\nstatus: active\nlast_used: "
            + old
            + "\n---\n\nA lesson.\n",
        )
        self.write("demo/notes.md", "lesson guidance\n")
        lesson = self.root / "demo/runs/coordination/lessons/lesson.md"
        other = self.root / "demo/notes.md"
        before_other = other.read_bytes()

        code, output = self.run_recall(["--project", "demo", "--stamp", "lesson", "guidance"])

        self.assertEqual(code, 0)
        self.assertIn("demo/runs/coordination/lessons/lesson.md", output)
        self.assertIn("last_used: " + datetime.now(timezone.utc).date().isoformat(), lesson.read_text())
        self.assertEqual(other.read_bytes(), before_other)

    def test_query_without_stamp_does_not_modify_records(self):
        self.write(
            "demo/runs/coordination/lessons/lesson.md",
            "---\nid: lesson\nadded: 2020-01-01\nsource_run: runs/issue\napproved_by: human\nstatus: active\nlast_used: 2020-01-01\n---\n\nlesson guidance\n",
        )
        lesson = self.root / "demo/runs/coordination/lessons/lesson.md"
        before = lesson.read_bytes()
        before_mtime = os.stat(lesson).st_mtime_ns

        code, output = self.run_recall(["--project", "demo", "lesson", "guidance"])

        self.assertEqual(code, 0)
        self.assertTrue(output)
        self.assertEqual(lesson.read_bytes(), before)
        self.assertEqual(os.stat(lesson).st_mtime_ns, before_mtime)

    def test_stamp_skips_missing_last_used_and_prints_results(self):
        self.write(
            "demo/runs/coordination/lessons/missing.md",
            "---\nid: missing\nadded: 2020-01-01\nsource_run: runs/issue\napproved_by: human\nstatus: active\n---\n\nmissing lesson\n",
        )

        code, output = self.run_recall(["--project", "demo", "--stamp", "missing", "lesson"])

        self.assertEqual(code, 0)
        self.assertIn("demo/runs/coordination/lessons/missing.md", output)

    def test_stamp_writes_each_returned_file_once(self):
        self.write(
            "demo/runs/coordination/lessons/lesson.md",
            "---\nid: lesson\nadded: 2020-01-01\nsource_run: runs/issue\napproved_by: human\nstatus: active\nlast_used: 2020-01-01\n---\n\nlesson lesson lesson guidance\n",
        )
        lesson = self.root / "demo/runs/coordination/lessons/lesson.md"
        with mock.patch.object(recall, "stamp_lesson", wraps=recall.stamp_lesson) as stamp:
            code, output = self.run_recall(["--project", "demo", "--stamp", "lesson", "guidance"])

        self.assertEqual(code, 0)
        self.assertTrue(output)
        self.assertEqual(stamp.call_count, 1)
        self.assertEqual(stamp.call_args.args[0], os.path.realpath(lesson))

    def test_invalid_selectors_exit_nonzero(self):
        for argv in ([], ["one"], ["--get", "bad"]):
            with self.subTest(argv=argv), self.assertRaises(SystemExit) as raised:
                with redirect_stderr(io.StringIO()):
                    recall.main(argv)
            self.assertNotEqual(raised.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
