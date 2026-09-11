"""Unit tests for the dispatch-time charter and staffing lint."""
from __future__ import annotations

import contextlib
import io
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import charter_lint  # noqa: E402


class CharterLintTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir="/private/tmp")
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def run_lint(self, charter: str, staffing: str | None = None) -> tuple[int, str, str]:
        charter_path = self.tmp / "charter.md"
        charter_path.write_text(charter, encoding="utf-8")
        argv = ["--charter", str(charter_path), "--lead", "lead-beo-skills"]
        if staffing is not None:
            staffing_path = self.tmp / "staffing.txt"
            staffing_path.write_text(staffing, encoding="utf-8")
            argv.extend(["--staffing", str(staffing_path)])

        stdout = io.StringIO()
        stderr = io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = charter_lint.main(argv)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_well_formed_engineer_and_staffing_record_is_ok(self):
        code, output, error = self.run_lint(self.engineer_charter(), self.staffing_record())
        self.assertEqual(code, 0)
        self.assertIn("OK:", output)
        self.assertEqual(error, "")

    def test_missing_disposition_is_named(self):
        charter = self.engineer_charter().replace("Disposition: Engineer\n", "")
        code, _, error = self.run_lint(charter)
        self.assertNotEqual(code, 0)
        self.assertIn("Disposition", error)

    def test_engineer_without_owned_paths_is_named(self):
        charter = self.engineer_charter().replace("Owned paths: tests/test_charter_lint.py\n", "")
        code, _, error = self.run_lint(charter)
        self.assertNotEqual(code, 0)
        self.assertIn("owned paths", error)

    def test_reviewer_without_exact_head_is_named(self):
        charter = self.engineer_charter().replace("Disposition: Engineer", "Disposition: Reviewer")
        charter = charter.replace("Owned paths: tests/test_charter_lint.py\n", "Reviewed head: pending\n")
        code, _, error = self.run_lint(charter)
        self.assertNotEqual(code, 0)
        self.assertIn("exact-head", error)

    def test_missing_prompt_command_is_named(self):
        charter = self.engineer_charter().replace("herdr agent prompt lead-beo-skills", "send the report")
        code, _, error = self.run_lint(charter)
        self.assertNotEqual(code, 0)
        self.assertIn("herdr agent prompt lead-beo-skills", error)

    def test_missing_report_path_is_named(self):
        charter = self.engineer_charter().replace("report-eng-lint.md", "evidence.md")
        code, _, error = self.run_lint(charter)
        self.assertNotEqual(code, 0)
        self.assertIn("report-*.md", error)

    def test_staffing_missing_each_required_key_is_named(self):
        complete = self.staffing_record()
        for key in ("posture=", "dialog=", "skills=", "extensions="):
            with self.subTest(key=key):
                engineer_line = next(
                    line for line in complete.splitlines() if line.startswith("ENGINEER:")
                )
                field = next(field for field in engineer_line.split() if field.startswith(key))
                incomplete = complete.replace(field, "", 1)
                code, _, error = self.run_lint(self.engineer_charter(), incomplete)
                self.assertNotEqual(code, 0)
                self.assertIn(key, error)
                self.assertIn("ENGINEER", error)

    @staticmethod
    def engineer_charter() -> str:
        return (
            "Disposition: Engineer\n"
            "Owned paths: tests/test_charter_lint.py\n"
            "Write report-eng-lint.md and send with herdr agent prompt lead-beo-skills ...\n"
        )

    @staticmethod
    def staffing_record() -> str:
        return (
            "ENGINEER: eng kind=pi model=m posture=none dialog=denied skills=none extensions=none\n"
            "REVIEWER: rev kind=agy model=m posture=prompting dialog=residual skills=none extensions=none\n"
        )


if __name__ == "__main__":
    unittest.main()
