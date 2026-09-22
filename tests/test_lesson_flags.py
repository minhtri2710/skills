#!/usr/bin/env python3
"""Tests for the advisory lesson staleness report."""
from __future__ import annotations

import io
import tempfile
import unittest
from contextlib import redirect_stdout
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
import sys

sys.path.insert(0, str(SCRIPTS))

import lesson_flags  # noqa: E402


class LessonFlagsTest(unittest.TestCase):
    def setUp(self):
        self.tempdir = tempfile.TemporaryDirectory()
        self.root = Path(self.tempdir.name)
        self.patch_root = mock.patch.object(lesson_flags, "PROJECTS_ROOT", str(self.root))
        self.patch_root.start()

    def tearDown(self):
        self.patch_root.stop()
        self.tempdir.cleanup()

    def write_record(self, name, status, last_used, superseded_by=None):
        path = self.root / "demo/runs/coordination/lessons" / f"{name}.md"
        path.parent.mkdir(parents=True, exist_ok=True)
        extra = f"superseded_by: {superseded_by}\n" if superseded_by is not None else ""
        path.write_text(
            "<!-- Store: lesson records. -->\n"
            "---\n"
            f"id: {name}\n"
            f"added: {last_used}\n"
            "source_run: runs/issue\n"
            "approved_by: human\n"
            f"status: {status}\n"
            f"last_used: {last_used}\n"
            f"{extra}"
            "---\n\nA lesson.\n",
            encoding="utf-8",
        )
        return path

    def run_flags(self, argv):
        output = io.StringIO()
        with redirect_stdout(output):
            code = lesson_flags.main(argv)
        return code, output.getvalue()

    def test_stale_records_are_flagged_and_fresh_records_are_not(self):
        old = (datetime.now(timezone.utc) - timedelta(days=120)).date().isoformat()
        fresh = (datetime.now(timezone.utc) - timedelta(days=5)).date().isoformat()
        self.write_record("old-active", "active", old)
        self.write_record("old-failure", "failure-mode", old)
        self.write_record("fresh-rejected", "rejected", fresh)
        store = self.root / "demo/runs/coordination/lessons"
        before = {path: path.read_bytes() for path in store.glob("*.md")}

        code, output = self.run_flags(["--project", "demo", "--days", "90"])

        self.assertEqual(code, 0)
        self.assertIn("[active]", output)
        self.assertIn("old-active.md", output)
        self.assertIn("[failure-mode]", output)
        self.assertIn("old-failure.md", output)
        self.assertNotIn("fresh-rejected.md", output)
        self.assertEqual(before, {path: path.read_bytes() for path in store.glob("*.md")})

    def test_superseded_record_with_landing_ref_is_classified(self):
        old = (datetime.now(timezone.utc) - timedelta(days=120)).date().isoformat()
        path = self.write_record(
            "old-superseded", "superseded", old, superseded_by="abc1234 (push G349)"
        )
        fields, last_used = lesson_flags.record_fields(str(path))
        self.assertEqual(fields["status"], "superseded")
        self.assertEqual(last_used.isoformat(), old)

        code, output = self.run_flags(["--project", "demo", "--days", "90"])

        self.assertEqual(code, 0)
        self.assertIn("[superseded]", output)
        self.assertIn("old-superseded.md", output)

    def test_fresh_superseded_record_is_flagged_regardless_of_staleness(self):
        # A superseded lesson is replaced doctrine: it surfaces as a retire
        # candidate even when last_used is recent, while a fresh non-superseded
        # record does not.
        fresh = (datetime.now(timezone.utc) - timedelta(days=3)).date().isoformat()
        self.write_record(
            "fresh-superseded", "superseded", fresh, superseded_by="abc1234 (push G349)"
        )
        self.write_record("fresh-active", "active", fresh)

        code, output = self.run_flags(["--project", "demo", "--days", "90"])

        self.assertEqual(code, 0)
        self.assertIn("[superseded]", output)
        self.assertIn("fresh-superseded.md", output)
        self.assertNotIn("fresh-active.md", output)

    def test_superseded_without_landing_ref_is_unclassified(self):
        old = (datetime.now(timezone.utc) - timedelta(days=120)).date().isoformat()
        path = self.write_record("bare-superseded", "superseded", old)
        with self.assertRaises(lesson_flags.LessonParseError):
            lesson_flags.record_fields(str(path))

    def test_superseded_by_on_non_superseded_status_is_unclassified(self):
        old = (datetime.now(timezone.utc) - timedelta(days=120)).date().isoformat()
        path = self.write_record(
            "active-with-ref", "active", old, superseded_by="abc1234"
        )
        with self.assertRaises(lesson_flags.LessonParseError):
            lesson_flags.record_fields(str(path))

    def test_malformed_lessons_are_reported_and_make_exit_nonzero(self):
        malformed = self.root / "demo/runs/coordination/lessons/broken.md"
        malformed.parent.mkdir(parents=True, exist_ok=True)
        malformed.write_text(
            "---\n"
            "id: broken\n"
            "added: 2020-01-01\n"
            "source_run: runs/issue\n"
            "approved_by: human\n"
            "status: active\n"
            "---\n\nBroken lesson.\n",
            encoding="utf-8",
        )

        code, output = self.run_flags(["--project", "demo"])

        self.assertEqual(code, 1)
        self.assertIn(f"malformed: {malformed}: missing field: last_used", output)
        self.assertNotIn("Nothing to flag", output)

    def test_missing_lessons_directory_exits_cleanly(self):
        code, output = self.run_flags(["--project", "demo"])

        self.assertEqual(code, 0)
        self.assertIn("Nothing to flag", output)


if __name__ == "__main__":
    unittest.main()
