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

    def test_bold_engineer_disposition_is_ok(self):
        charter = self.engineer_charter().replace(
            "Disposition: Engineer\n", "**Disposition:** Engineer.\n"
        )
        code, output, error = self.run_lint(charter, self.staffing_record())
        self.assertEqual(code, 0)
        self.assertIn("OK:", output)
        self.assertEqual(error, "")

    def test_malformed_bold_disposition_is_named(self):
        charter = self.engineer_charter().replace(
            "Disposition: Engineer\n", "**Disposition:** Builder.\n"
        )
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

    def test_report_block_without_send_failed_is_named(self):
        charter = self.engineer_charter().replace("SEND-FAILED", "send failed")
        code, _, error = self.run_lint(charter)
        self.assertNotEqual(code, 0)
        self.assertIn("SEND-FAILED", error)

    def test_full_hardened_report_block_is_ok(self):
        code, output, error = self.run_lint(self.engineer_charter(), self.staffing_record())
        self.assertEqual(code, 0)
        self.assertIn("OK:", output)
        self.assertEqual(error, "")

    def test_engineer_without_staffing_record_is_named(self):
        code, _, error = self.run_lint(self.engineer_charter())
        self.assertEqual(code, 1)
        self.assertIn("staffing record is required", error)
        self.assertIn("Engineer/Reviewer", error)

    def test_reviewer_with_filled_staffing_record_is_ok(self):
        code, output, error = self.run_lint(self.reviewer_charter(), self.staffing_record())
        self.assertEqual(code, 0)
        self.assertIn("OK:", output)
        self.assertEqual(error, "")

    def test_reviewer_placeholder_is_named(self):
        staffing = self.staffing_record().replace(
            "REVIEWER: rev kind=agy model=m", "REVIEWER: <name> kind=<kind> model=m"
        )
        code, _, error = self.run_lint(self.reviewer_charter(), staffing)
        self.assertEqual(code, 1)
        self.assertIn("REVIEWER", error)
        self.assertIn("placeholder", error)

    def test_engineer_ignores_placeholder_in_other_seat(self):
        staffing = self.staffing_record().replace(
            "REVIEWER: rev kind=agy model=m", "REVIEWER: <name> kind=<kind> model=m"
        )
        code, output, error = self.run_lint(self.engineer_charter(), staffing)
        self.assertEqual(code, 0)
        self.assertIn("OK:", output)
        self.assertEqual(error, "")

    def test_architect_staffing_remains_optional(self):
        charter = self.engineer_charter().replace("Disposition: Engineer", "Disposition: Architect")
        code, output, error = self.run_lint(charter)
        self.assertEqual(code, 0)
        self.assertIn("OK:", output)
        self.assertEqual(error, "")

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
            "Write the finished report/verdict to report-eng-lint.md with the editor/write tool (never via the shell), then print it as the pane's final output.\n"
            "At send time, compose a prompt with the verdict/outcome line, a bounded summary (~200 words max), and full report at report-eng-lint.md; send ONLY that composed prompt with the EXACT command herdr agent prompt lead-beo-skills \"<composed prompt>\" and NO other flags. Do not send the report file contents. THIS SEND IS MANDATORY.\n"
            "If the command exits non-zero: retry it ONCE with exactly the same form; if it still fails, append a line SEND-FAILED to the end of the report file and run herdr notification show \"eng-lint: report send failed\" --body \"report-eng-lint.md\" --sound request, then stop.\n"
        )

    @staticmethod
    def reviewer_charter() -> str:
        return (
            "Disposition: Reviewer\n"
            "Reviewed head: 0123456789abcdef0123456789abcdef01234567\n"
            "Write the finished report/verdict to report-eng-lint.md with the editor/write tool (never via the shell), then print it as the pane's final output.\n"
            "At send time, compose a prompt with the verdict/outcome line, a bounded summary (~200 words max), and full report at report-eng-lint.md; send ONLY that composed prompt with the EXACT command herdr agent prompt lead-beo-skills \"<composed prompt>\" and NO other flags. Do not send the report file contents. THIS SEND IS MANDATORY.\n"
            "If the command exits non-zero: retry it ONCE with exactly the same form; if it still fails, append a line SEND-FAILED to the end of the report file and run herdr notification show \"eng-lint: report send failed\" --body \"report-eng-lint.md\" --sound request, then stop.\n"
        )

    @staticmethod
    def staffing_record() -> str:
        return (
            "ENGINEER: eng kind=pi model=m posture=none dialog=denied skills=none extensions=none\n"
            "REVIEWER: rev kind=agy model=m posture=prompting dialog=residual skills=none extensions=none\n"
        )


if __name__ == "__main__":
    unittest.main()
