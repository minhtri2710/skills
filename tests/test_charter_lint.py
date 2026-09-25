"""Unit tests for the dispatch-time charter and staffing lint."""
from __future__ import annotations

import contextlib
import importlib.util
import io
import os
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import charter_lint  # noqa: E402
import jev  # noqa: E402


class CharterLintTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._repo_tmp = tempfile.TemporaryDirectory(dir="/private/tmp")
        cls.repo = Path(cls._repo_tmp.name)
        cls.addClassCleanup(cls._repo_tmp.cleanup)
        git = ["git", "-C", str(cls.repo), "-c", "user.name=t", "-c", "user.email=t@example.com"]
        subprocess.run([*git, "init", "-q"], check=True)
        for message in ("base", "head"):
            subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", message], check=True)
        cls.base, cls.head = subprocess.run(
            [*git, "rev-parse", "HEAD~1", "HEAD"], check=True, capture_output=True, text=True
        ).stdout.split()

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir="/private/tmp")
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def run_lint(
        self,
        charter: str,
        staffing: str | None = None,
        jev_enabled: bool = False,
    ) -> tuple[int, str, str]:
        charter_path = self.tmp / "charter.md"
        charter_path.write_text(charter, encoding="utf-8")
        argv = ["--charter", str(charter_path), "--lead", "lead-beo-skills", "--repo", str(self.repo)]
        if jev_enabled:
            argv.append("--jev")
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

    def test_reviewer_without_live_wake_guard_is_named(self):
        charter = self.reviewer_charter().replace(self.live_wake_guard_sentence(), "")
        code, _, error = self.run_lint(charter, self.staffing_record())
        self.assertEqual(code, 1)
        self.assertIn(
            "missing live-wake guard: Never run `mailbox.py --wake` against a real seat", error
        )

    def test_reviewer_with_live_wake_guard_passes(self):
        code, output, error = self.run_lint(self.reviewer_charter(), self.staffing_record())
        self.assertEqual(code, 0)
        self.assertIn("OK:", output)
        self.assertEqual(error, "")

    def test_engineer_without_live_wake_guard_still_passes(self):
        code, output, error = self.run_lint(self.engineer_charter(), self.staffing_record())
        self.assertEqual(code, 0)
        self.assertIn("OK:", output)
        self.assertNotIn("live-wake", error)

    def test_live_wake_guard_match_ignores_case_and_backticks(self):
        charter = self.reviewer_charter().replace(
            "Never run `mailbox.py --wake` against a real seat",
            "never run mailbox.py  --wake  against a REAL seat",
        )
        code, output, error = self.run_lint(charter, self.staffing_record())
        self.assertEqual(code, 0)
        self.assertIn("OK:", output)
        self.assertEqual(error, "")

    def test_each_disposition_without_pattern_kill_guard_is_named(self):
        charters = {
            "Engineer": self.engineer_charter(),
            "Reviewer": self.reviewer_charter(),
            "Architect": self.engineer_charter().replace("Disposition: Engineer", "Disposition: Architect"),
        }
        for disposition, charter in charters.items():
            with self.subTest(disposition=disposition):
                code, _, error = self.run_lint(
                    charter.replace(self.kill_guard_sentence(), ""), self.staffing_record()
                )
                self.assertEqual(code, 1)
                self.assertIn("missing pattern-kill guard: Never kill a process by pattern", error)

    def test_pattern_kill_guard_match_ignores_case_and_spacing(self):
        charter = self.engineer_charter().replace(
            "Never kill a process by pattern", "NEVER kill  a process\nby pattern"
        )
        code, output, error = self.run_lint(charter, self.staffing_record())
        self.assertEqual(code, 0)
        self.assertIn("OK:", output)
        self.assertEqual(error, "")

    def test_reviewer_without_either_ocr_delegate_command_is_named(self):
        for command in ("ocr delegate preview", "ocr delegate rule"):
            with self.subTest(command=command):
                charter = self.reviewer_charter().replace(command, "ocr")
                code, _, error = self.run_lint(charter, self.staffing_record())
                self.assertEqual(code, 1)
                self.assertIn(
                    "missing OCR delegate step: ocr delegate preview and ocr delegate rule", error
                )

    def test_engineer_without_ocr_delegate_step_still_passes(self):
        code, output, error = self.run_lint(self.engineer_charter(), self.staffing_record())
        self.assertEqual(code, 0)
        self.assertIn("OK:", output)
        self.assertNotIn("OCR", error)

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

    def test_default_lint_does_not_call_jev(self):
        with unittest.mock.patch.object(jev, "triage_charter") as triage:
            code, output, error = self.run_lint(self.engineer_charter(), self.staffing_record())
        self.assertEqual(code, 0)
        self.assertIn("OK:", output)
        self.assertNotIn("Jev advisory", output)
        self.assertEqual(error, "")
        triage.assert_not_called()

    def test_jev_is_opt_in_advisory_and_cannot_change_lint_result(self):
        with unittest.mock.patch.object(
            jev,
            "triage_charter",
            return_value=jev.UnavailableResult(
                status="unavailable", finding={}, reason="missing_api_key"
            ),
        ) as triage:
            clean = self.run_lint(self.engineer_charter(), self.staffing_record(), jev_enabled=True)
            broken = self.run_lint(
                self.engineer_charter().replace("Disposition: Engineer\n", ""),
                jev_enabled=True,
            )
        self.assertEqual(clean[0], 0)
        self.assertEqual(broken[0], 1)
        self.assertIn("Jev advisory: unavailable (missing_api_key)", clean[1])
        self.assertIn("Jev advisory: unavailable (missing_api_key)", broken[1])
        self.assertIn("Disposition", broken[2])
        self.assertEqual(triage.call_count, 2)

    def test_available_jev_advisory_is_bounded_and_does_not_authorize(self):
        judgment = jev.CharterAdvisoryResult(
            status="available",
            source_state={"disposition": "Engineer", "body": "body"},
            coherence=jev.NoulJudgment(label="incoherent", probability=0.1),
            raw_answers={"noul": {"type": "noul", "noul": 0.1}},
        )
        with unittest.mock.patch.object(
            jev, "triage_charter", return_value=judgment
        ) as triage:
            code, output, error = self.run_lint(
                self.engineer_charter(), self.staffing_record(), jev_enabled=True
            )
        self.assertEqual(code, 0)
        self.assertEqual(error, "")
        self.assertEqual(output.count("Jev advisory:"), 1)
        self.assertIn("Jev advisory: incoherent", output)
        self.assertIn("OK:", output)
        triage.assert_called_once()

    def test_lint_without_jev_runs_when_jev_is_unimportable(self):
        # jev needs python >= 3.10; a fresh charter_lint must load and lint
        # without it, and only --jev may import it.
        spec = importlib.util.spec_from_file_location(
            "charter_lint_without_jev", SCRIPTS / "charter_lint.py"
        )
        module = importlib.util.module_from_spec(spec)
        charter_path = self.tmp / "charter.md"
        charter_path.write_text(self.engineer_charter(), encoding="utf-8")
        staffing_path = self.tmp / "staffing.txt"
        staffing_path.write_text(self.staffing_record(), encoding="utf-8")
        stdout = io.StringIO()
        with unittest.mock.patch.dict(sys.modules, {"jev": None, spec.name: module}):
            spec.loader.exec_module(module)
            with contextlib.redirect_stdout(stdout):
                code = module.main([
                    "--charter", str(charter_path),
                    "--lead", "lead-beo-skills",
                    "--staffing", str(staffing_path),
                    "--repo", str(self.repo),
                ])
            with self.assertRaises(ImportError):
                module.main([
                    "--charter", str(charter_path),
                    "--lead", "lead-beo-skills",
                    "--staffing", str(staffing_path),
                    "--repo", str(self.repo),
                    "--jev",
                ])
        self.assertEqual(code, 0)
        self.assertIn("OK:", stdout.getvalue())

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

    def test_lowercase_seat_line_after_prose_is_still_checked(self):
        staffing = "Staffed 2026-09-24.\nengineer: eng kind=pi model=m posture=none\n"
        code, _, error = self.run_lint(self.engineer_charter(), staffing)
        self.assertEqual(code, 1)
        self.assertIn("ENGINEER seat missing dialog=", error)

    def test_reviewer_without_staffing_record_is_named(self):
        code, _, error = self.run_lint(self.reviewer_charter())
        self.assertEqual(code, 1)
        self.assertIn("staffing record is required", error)

    def test_unreadable_charter_or_staffing_exits_1_on_stderr(self):
        charter_path = self.tmp / "charter.md"
        charter_path.write_text(self.engineer_charter(), encoding="utf-8")
        missing = str(self.tmp / "missing.md")
        for argv, label in (
            (["--charter", missing], "could not read charter "),
            (["--charter", str(charter_path), "--staffing", missing],
             "could not read staffing record "),
        ):
            with self.subTest(label=label):
                stdout, stderr = io.StringIO(), io.StringIO()
                with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                    code = charter_lint.main(
                        [*argv, "--lead", "lead-beo-skills", "--repo", str(self.repo)]
                    )
                self.assertEqual(code, 1)
                self.assertEqual(stdout.getvalue(), "")
                self.assertIn(f"charter_lint: {label}", stderr.getvalue())
                self.assertIn(missing, stderr.getvalue())

    def test_charter_lead_and_repo_are_required_arguments(self):
        charter_path = self.tmp / "charter.md"
        charter_path.write_text(self.engineer_charter(), encoding="utf-8")
        given = {"--charter": str(charter_path), "--lead": "lead-beo-skills", "--repo": str(self.repo)}
        for omitted in given:
            argv = [part for flag, value in given.items() if flag != omitted for part in (flag, value)]
            with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    charter_lint.main(argv)
                self.assertEqual(raised.exception.code, 2)

    def test_a_charter_is_read_as_utf8_whatever_the_locale(self):
        charter = self.tmp / "charter.md"
        charter.write_text(self.engineer_charter() + "café\n", encoding="utf-8")
        staffing = self.tmp / "staffing.txt"
        staffing.write_text(self.staffing_record(), encoding="utf-8")
        env = {k: v for k, v in os.environ.items() if k not in ("PYTHONUTF8", "PYTHONIOENCODING", "LANG")}
        proc = subprocess.run(
            [sys.executable, "-c", "import sys; sys.path.insert(0, sys.argv[1]); import charter_lint; "
             "sys.exit(charter_lint.main(sys.argv[2:]))", str(SCRIPTS), "--charter", str(charter),
             "--lead", "lead-beo-skills", "--staffing", str(staffing), "--repo", str(self.repo)],
            capture_output=True, text=True, env={**env, "LC_ALL": "en_US.US-ASCII"},
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_range_endpoints_staffed_heads_and_their_splices_must_resolve(self):
        base, head, null = self.base, self.head, "0" * 40
        spliced_base = base[:12] + head[12:]
        spliced_echo = head[:7] + ("0" if head[7] != "0" else "1") + base[8:]
        null_prefixed_pin = "0" * 7 + "d" * 33
        cases = (
            ("resolved range", f"Reviewed unit: the range {base}..{head}\n", "", None),
            ("first-push null base", f"Reviewed unit: the range {null}..{head}\n", "", None),
            ("external pin", f"Range {base}..{head}; upstream pin gitea @ {'d' * 40}\n", "", None),
            ("null base anchors no splice", f"Range {null}..{head}; pin @ {null_prefixed_pin}\n", "", None),
            ("spliced range base", f"Reviewed unit: the range {spliced_base}..{head}\n", "",
             f"unresolved SHA {spliced_base} in charter"),
            ("spliced head echo", f"Range {base}...{head}; verdict line REVIEW {spliced_echo}\n", "",
             f"unresolved SHA {spliced_echo} in charter"),
            ("unresolved staffed head", "", f"HEAD: main@{'e' * 40}\n",
             f"unresolved SHA {'e' * 40} in staffing record"),
            ("unresolved staffed head=", "", f"Restaffed at head={'f' * 40}\n",
             f"unresolved SHA {'f' * 40} in staffing record"),
        )
        for label, charter_line, staffing_line, problem in cases:
            with self.subTest(label):
                code, output, error = self.run_lint(
                    self.reviewer_charter() + charter_line, self.staffing_record() + staffing_line
                )
                if problem is None:
                    self.assertEqual((code, error), (0, ""))
                else:
                    self.assertEqual(code, 1)
                    self.assertEqual(error, f"charter_lint: {problem}: not an object in {self.repo}\n")
        charter_path = self.tmp / "charter.md"
        charter_path.write_text(self.engineer_charter(), encoding="utf-8")
        stderr = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
            code = charter_lint.main([
                "--charter", str(charter_path), "--lead", "lead-beo-skills", "--repo", str(self.tmp),
            ])
        self.assertEqual(code, 1)
        self.assertIn(f"charter_lint: could not read repo {self.tmp}: ", stderr.getvalue())
        stderr = io.StringIO()
        missing_git = FileNotFoundError(2, "No such file or directory", "git")
        with unittest.mock.patch.object(charter_lint.subprocess, "run", side_effect=missing_git), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
            code = charter_lint.main([
                "--charter", str(charter_path), "--lead", "lead-beo-skills", "--repo", str(self.repo),
            ])
        self.assertEqual(code, 1)
        self.assertIn("charter_lint: could not run git: ", stderr.getvalue())

    def test_jev_receives_the_declared_disposition_and_full_charter(self):
        unavailable = jev.UnavailableResult(status="unavailable", finding={}, reason="x")
        no_disposition = self.engineer_charter().replace("Disposition: Engineer\n", "")
        with unittest.mock.patch.object(
            jev, "triage_charter", return_value=unavailable
        ) as triage:
            self.run_lint(self.engineer_charter(), self.staffing_record(), jev_enabled=True)
            self.run_lint(no_disposition, jev_enabled=True)
        self.assertEqual(
            triage.call_args_list,
            [
                unittest.mock.call("Engineer", self.engineer_charter()),
                unittest.mock.call(None, no_disposition),
            ],
        )

    @staticmethod
    def engineer_charter() -> str:
        return (
            "Disposition: Engineer\n"
            "Owned paths: tests/test_charter_lint.py\n"
            + CharterLintTest.kill_guard_sentence()
            + "Write the finished report/verdict to report-eng-lint.md with the editor/write tool (never via the shell), then print it as the pane's final output.\n"
            "At send time, compose a prompt with the verdict/outcome line, a bounded summary (~200 words max), and full report at report-eng-lint.md; send ONLY that composed prompt with the EXACT command herdr agent prompt lead-beo-skills \"<composed prompt>\" and NO other flags. Do not send the report file contents. THIS SEND IS MANDATORY.\n"
            "If the command exits non-zero: retry it ONCE with exactly the same form; if it still fails, append a line SEND-FAILED to the end of the report file and run herdr notification show \"eng-lint: report send failed\" --body \"report-eng-lint.md\" --sound request, then stop.\n"
        )

    @staticmethod
    def live_wake_guard_sentence() -> str:
        return (
            "No-mutation: the review changes no external state, so Never run `mailbox.py --wake` "
            "against a real seat; exercise wake only with a patched subprocess or a nonexistent "
            "seat name (expect `agent_not_found`).\n"
        )

    @staticmethod
    def kill_guard_sentence() -> str:
        return (
            "Never kill a process by pattern (`pkill -f`, `killall`, `pgrep ... | xargs kill`); "
            "stop only a process whose pid or task id you started yourself.\n"
        )

    @staticmethod
    def ocr_step_sentence() -> str:
        return (
            "Run `ocr delegate preview --format json --repo /repo --from base --to head`, then "
            "`ocr delegate rule --format json --repo /repo <reviewable paths>`, and report the OCR coverage block.\n"
        )

    @classmethod
    def reviewer_charter(cls) -> str:
        return (
            "Disposition: Reviewer\n"
            f"Reviewed head: {cls.head}\n"
            + cls.live_wake_guard_sentence()
            + cls.kill_guard_sentence()
            + cls.ocr_step_sentence()
            + "Review order: first the diff and your own findings; only then read the implementation reports.\n"
            + "Write the finished report/verdict to report-eng-lint.md with the editor/write tool (never via the shell), then print it as the pane's final output.\n"
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
