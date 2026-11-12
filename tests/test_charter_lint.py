"""Unit tests for the dispatch-time charter and staffing lint."""
from __future__ import annotations

import contextlib
import hashlib
import io
import os
import shutil
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

import support
import backend
import charter_lint
import gitops
from backends import herdr
from fake_backend import FakeBackend

SCRIPTS = support.ADW / "scripts"
LEAD = "lead-beo-skills"
REPORT = "/state/demo/runs/r1/report-eng-lint.md"


def setUpModule() -> None:
    support.never_run("git", sys.executable)


class CharterLintTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._repo_tmp = tempfile.TemporaryDirectory(dir=os.path.realpath("/tmp"))
        cls.repo = Path(cls._repo_tmp.name)
        cls.addClassCleanup(cls._repo_tmp.cleanup)
        support.temp_git_repo(cls.repo)
        for message in ("base", "mid", "head"):
            support.git(cls.repo, "commit", "-q", "--allow-empty", "-m", message)
        cls.base, cls.mid, cls.head = support.git(cls.repo, "rev-parse", "HEAD~2", "HEAD~1", "HEAD").split()

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=os.path.realpath("/tmp"))
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        (self.bin / "git").symlink_to(shutil.which("git"))

    def lint_main(self, argv: list[str], seats: backend.Backend | None = None) -> int:
        opened = unittest.mock.patch.object(
            charter_lint.backend, "open_backend", return_value=seats or FakeBackend()
        )
        with opened:
            return charter_lint.main(argv)

    def run_lint(
        self,
        charter: str,
        staffing: str | None = None,
        seats: backend.Backend | None = None,
        fence_tool: bool = True,
    ) -> tuple[int, str, str]:
        fence = self.bin / "sandbox-exec"
        fence.unlink(missing_ok=True)
        if fence_tool:
            fence.write_text("#!/bin/sh\n", encoding="utf-8")
            fence.chmod(0o755)
        charter_path = self.tmp / "charter.md"
        charter_path.write_text(charter, encoding="utf-8")
        argv = ["--charter", str(charter_path), "--lead", LEAD, "--repo", str(self.repo)]
        if staffing is not None:
            staffing_path = self.tmp / "staffing.txt"
            staffing_path.write_text(staffing, encoding="utf-8")
            argv.extend(["--staffing", str(staffing_path)])

        stdout = io.StringIO()
        stderr = io.StringIO()
        with unittest.mock.patch.dict(os.environ, {"PATH": str(self.bin)}), \
                contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = self.lint_main(argv, seats)
        return code, stdout.getvalue(), stderr.getvalue()

    def test_ok_line_contains_sha256_of_each_linted_file(self):
        charter = self.engineer_charter()
        staffing = self.staffing_record()
        code, output, error = self.run_lint(charter, staffing)
        self.assertEqual(code, 0)
        self.assertEqual(
            output,
            "OK: charter sha256=" + hashlib.sha256(charter.encode("utf-8")).hexdigest()
            + "; staffing record sha256="
            + hashlib.sha256(staffing.encode("utf-8")).hexdigest()
            + "; dispatch requirements linted\n",
        )
        self.assertEqual(error, "")

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

    def test_each_disposition_without_takeover_guard_is_named(self):
        charters = {
            "Engineer": self.engineer_charter(),
            "Reviewer": self.reviewer_charter(),
            "Architect": self.engineer_charter().replace("Disposition: Engineer", "Disposition: Architect"),
        }
        for disposition, charter in charters.items():
            with self.subTest(disposition=disposition):
                code, _, error = self.run_lint(
                    charter.replace(self.takeover_guard_sentence(), ""), self.staffing_record()
                )
                self.assertEqual(code, 1)
                self.assertEqual(
                    error,
                    "charter_lint: missing takeover guard: Never stop, remove, or take over a "
                    "container, process, or port\n",
                )

    def test_takeover_guard_match_ignores_case_and_spacing(self):
        charter = self.engineer_charter().replace(
            "Never stop, remove, or take over a container, process, or port",
            "NEVER stop,  remove, or take over\na container, process, or port",
        )
        code, output, error = self.run_lint(charter, self.staffing_record())
        self.assertEqual(code, 0)
        self.assertIn("OK:", output)
        self.assertEqual(error, "")

    def test_pattern_kill_guard_match_ignores_case_and_spacing(self):
        charter = self.engineer_charter().replace(
            "Never kill a process by pattern", "NEVER kill  a process\nby pattern"
        )
        code, output, error = self.run_lint(charter, self.staffing_record())
        self.assertEqual(code, 0)
        self.assertIn("OK:", output)
        self.assertEqual(error, "")

    def test_reviewer_without_time_limit_clause_is_named(self):
        charter = self.reviewer_charter().replace(
            self.time_limit_sentence(),
            "Acceptance: past the time limit: a stalled review ends as `BLOCKED (time limit)`.\n",
        )
        code, _, error = self.run_lint(charter, self.staffing_record())
        self.assertEqual(code, 1)
        self.assertIn("missing time limit: BLOCKED (time limit)", error)

    def test_engineer_reviewer_and_architect_without_staffing_record_are_named(self):
        charters = {
            "Engineer": self.engineer_charter(),
            "Reviewer": self.reviewer_charter(),
            "Architect": self.engineer_charter().replace("Disposition: Engineer", "Disposition: Architect"),
        }
        for disposition, charter in charters.items():
            with self.subTest(disposition=disposition):
                code, _, error = self.run_lint(charter)
                self.assertEqual(code, 1)
                self.assertIn(
                    "staffing record is required for an Engineer/Reviewer/Architect disposition", error
                )

    def test_fenced_seat_docker_residual_depends_on_charter_allowance(self):
        charter = self.reviewer_charter() + "The charter allows containers, using docker compose up.\n"
        missing = self.run_lint(charter, self.staffing_record())
        self.assertEqual(missing[0], 1)
        self.assertIn(
            "charter_lint: REVIEWER fenced seat missing residual docker-daemon writes\n",
            missing[2],
        )

        residual = self.staffing_record().replace(
            self.fence_evidence(),
            self.fence_evidence()
            + " residual docker-daemon writes (the Docker daemon runs outside sandbox-exec), "
            "bounded by: charter",
        )
        self.assertEqual(self.run_lint(charter, residual)[0], 0)

        engineer_charter = (
            self.engineer_charter() + "The charter allows containers, using docker compose up.\n"
        )
        self.assertEqual(self.run_lint(engineer_charter, self.staffing_record())[0], 0)

        prohibited = self.reviewer_charter() + "No docker/psql/build/e2e.\n"
        self.assertEqual(self.run_lint(prohibited, self.staffing_record())[0], 0)

        doctrinal = (
            "The fence does not bound the Docker daemon: a fenced charter that allows "
            "containers pins the exact docker commands.\n"
        )
        self.assertEqual(self.run_lint(self.reviewer_charter() + doctrinal, self.staffing_record())[0], 1)

    def test_reviewer_placeholder_is_named(self):
        staffing = self.staffing_record().replace(
            "REVIEWER: rev kind=pi model=m", "REVIEWER: <name> kind=<kind> model=m"
        )
        code, _, error = self.run_lint(self.reviewer_charter(), staffing)
        self.assertEqual(code, 1)
        self.assertIn("REVIEWER", error)
        self.assertIn("placeholder", error)

    def test_engineer_ignores_placeholder_in_other_seat(self):
        staffing = self.staffing_record().replace(
            "REVIEWER: rev kind=pi model=m", "REVIEWER: <name> kind=<kind> model=m"
        )
        code, output, error = self.run_lint(self.engineer_charter(), staffing)
        self.assertEqual(code, 0)
        self.assertIn("OK:", output)
        self.assertEqual(error, "")

    def test_reviewer_without_fence_is_refused(self):
        staffing = self.staffing_record().replace(
            " " + self.fence_evidence(), "", 1
        )
        code, _, error = self.run_lint(self.reviewer_charter(), staffing)
        self.assertEqual(code, 1)
        self.assertIn("REVIEWER seat missing fence=", error)

    def test_reviewer_bare_fence_none_is_refused(self):
        for token in ("fence=none", "fence=none:"):
            with self.subTest(token=token):
                staffing = self.staffing_record().replace(
                    self.fence_evidence(), token, 1
                )
                code, _, error = self.run_lint(self.reviewer_charter(), staffing)
                self.assertEqual(code, 1)
                self.assertIn("REVIEWER fence=none requires a reason in parentheses", error)

    def test_reviewer_fence_none_when_required_is_refused(self):
        staffing = self.staffing_record().replace(
            self.fence_evidence(), "fence=none(no OS fence available)", 1
        )
        code, _, error = self.run_lint(self.reviewer_charter(), staffing)
        self.assertEqual(code, 1)
        self.assertIn("REVIEWER fence=none is not allowed", error)

    def test_reviewer_fence_none_with_a_reason_is_accepted_without_sandbox_exec(self):
        staffing = self.staffing_record().replace(
            self.fence_evidence(), "fence=none(no OS fence available)", 1
        )
        code, output, error = self.run_lint(self.reviewer_charter(), staffing, fence_tool=False)
        self.assertEqual((code, error), (0, ""))
        self.assertIn("OK:", output)

    def test_reviewer_balanced_parentheses_in_fence_evidence_are_accepted(self):
        staffing = self.staffing_record().replace(
            self.fence_evidence(),
            "fence=sandbox-exec(fence.sb; probe touch (x2) -> Operation not permitted, no file) "
            "posture=none(extra (parentheses))",
            1,
        )
        code, output, error = self.run_lint(self.reviewer_charter(), staffing)
        self.assertEqual(code, 0)
        self.assertIn("OK:", output)
        self.assertEqual(error, "")

        base_accepted_unbalanced = self.staffing_record().replace(
            self.fence_evidence(),
            "fence=sandbox-exec(fence.sb; probe touch -> Operation not permitted (oops)",
            1,
        )
        code, output, error = self.run_lint(self.reviewer_charter(), base_accepted_unbalanced)
        self.assertEqual(code, 0)
        self.assertIn("OK:", output)
        self.assertEqual(error, "")

    def test_reviewer_missing_fence_profile_or_probe_is_refused(self):
        cases = (
            "fence=sandbox-exec(missing.sb; probe touch /checkout/.fence-probe "
            "-> Operation not permitted, no file)",
            "fence=sandbox-exec(fence.sb)",
            "fence=sandbox-exec(fence.sb; probe not run)",
            "fence=sandbox-exec(fence.sb; probe touch /checkout/.fence-probe -> Permission denied)",
        )
        for evidence in cases:
            with self.subTest(evidence=evidence):
                staffing = self.staffing_record().replace(self.fence_evidence(), evidence, 1)
                code, _, error = self.run_lint(self.reviewer_charter(), staffing)
                self.assertEqual(code, 1)
                self.assertIn("must record an existing .sb file and a probe result", error)

    def test_architect_seat_is_checked(self):
        charter = self.engineer_charter().replace("Disposition: Engineer", "Disposition: Architect")
        architect_record = self.staffing_record().replace("REVIEWER:", "ARCHITECT:", 1)
        code, output, error = self.run_lint(charter, architect_record)
        self.assertEqual(code, 0)
        self.assertIn("OK:", output)
        self.assertEqual(error, "")

        incomplete = architect_record.replace(
            "ARCHITECT: rev kind=pi model=m posture=prompting dialog=denied ",
            "ARCHITECT: rev kind=pi model=m posture=prompting ",
        )
        code, _, error = self.run_lint(charter, incomplete)
        self.assertEqual(code, 1)
        self.assertIn("ARCHITECT seat missing dialog=", error)

    def test_staffing_missing_each_required_key_is_named(self):
        complete = self.staffing_record()
        for key in (
            "posture=", "dialog=", "dialog-tools=", "dialog-deny=", "dialog-source=",
            "skills=", "extensions=",
        ):
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

    def test_staffing_rejects_dialog_deny_that_does_not_match_recorded_tools(self):
        staffing = self.staffing_record().replace("dialog-deny=*question*", "dialog-deny=ask_question", 1)
        code, _, error = self.run_lint(self.engineer_charter(), staffing)
        self.assertEqual(code, 1)
        self.assertIn("ENGINEER dialog-deny does not cover ask_user_question", error)

    def test_dialog_absent_requires_no_tools_and_no_deny(self):
        staffing = self.staffing_record().replace(
            "dialog=denied dialog-tools=ask_user_question,ask_question dialog-deny=*question*",
            "dialog=absent dialog-tools=none dialog-deny=none",
            1,
        )
        self.assertEqual(self.run_lint(self.engineer_charter(), staffing)[0], 0)
        invalid = staffing.replace("dialog-tools=none", "dialog-tools=ask_user_question", 1)
        code, _, error = self.run_lint(self.engineer_charter(), invalid)
        self.assertEqual(code, 1)
        self.assertIn("dialog=absent requires dialog-tools=none and dialog-deny=none", error)

    def test_staffing_rejects_unknown_dialog_values(self):
        for dialog in ("ask_user_question", "ask_question"):
            with self.subTest(dialog=dialog):
                staffing = self.staffing_record().replace("dialog=denied", f"dialog={dialog}", 1)
                code, _, error = self.run_lint(self.engineer_charter(), staffing)
                self.assertEqual(code, 1)
                self.assertIn(f"ENGINEER seat cannot have dialog={dialog}", error)

    def test_lowercase_seat_line_after_prose_is_still_checked(self):
        staffing = "Staffed 2026-09-24.\nengineer: eng kind=pi model=m posture=none\n"
        code, _, error = self.run_lint(self.engineer_charter(), staffing)
        self.assertEqual(code, 1)
        self.assertIn("ENGINEER seat missing dialog=", error)

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
                    code = self.lint_main([*argv, "--lead", LEAD, "--repo", str(self.repo)])
                self.assertEqual(code, 1)
                self.assertEqual(stdout.getvalue(), "")
                self.assertIn(f"charter_lint: {label}", stderr.getvalue())
                self.assertIn(missing, stderr.getvalue())

    def test_charter_lead_and_repo_are_required_arguments(self):
        charter_path = self.tmp / "charter.md"
        charter_path.write_text(self.engineer_charter(), encoding="utf-8")
        given = {"--charter": str(charter_path), "--lead": LEAD, "--repo": str(self.repo)}
        for omitted in given:
            argv = [part for flag, value in given.items() if flag != omitted for part in (flag, value)]
            with self.subTest(argv=argv), contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit) as raised:
                    self.lint_main(argv)
                self.assertEqual(raised.exception.code, 2)

    def test_a_charter_is_read_as_utf8_whatever_the_locale(self):
        charter = self.tmp / "charter.md"
        charter.write_text(self.engineer_charter() + "café\n", encoding="utf-8")
        staffing = self.tmp / "staffing.txt"
        staffing.write_text(self.staffing_record(), encoding="utf-8")
        proc = support.run_in_locale(
            "C",
            "import sys; sys.path[:0] = sys.argv[1:3]; import backend, charter_lint; "
            "from fake_backend import FakeBackend; backend.open_backend = lambda environ, explicit=None: FakeBackend(); "
            "sys.exit(charter_lint.main(sys.argv[3:]))", str(SCRIPTS), str(Path(__file__).parent), "--charter", str(charter),
            "--lead", LEAD, "--staffing", str(staffing), "--repo", str(self.repo),
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)

    def test_range_endpoints_staffed_heads_and_their_splices_must_resolve(self):
        base, head, null = self.base, self.head, gitops.NULL_OID
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
            code = self.lint_main([
                "--charter", str(charter_path), "--lead", LEAD, "--repo", str(self.tmp),
            ])
        self.assertEqual(code, 1)
        self.assertIn(f"charter_lint: could not read repo {self.tmp}: ", stderr.getvalue())
        stderr = io.StringIO()
        missing_git = FileNotFoundError(2, "No such file or directory", "git")
        with unittest.mock.patch.object(gitops.subprocess, "Popen", side_effect=missing_git), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
            code = self.lint_main([
                "--charter", str(charter_path), "--lead", LEAD, "--repo", str(self.repo),
            ])
        self.assertEqual(code, 1)
        self.assertIn(f"charter_lint: could not read repo {self.repo}: could not run git: ", stderr.getvalue())

    def test_repair_re_review_range_must_hold_a_commit_its_prior_fail_review_names(self):
        base, mid, head = self.base, self.mid, self.head
        gloss = "(`none`, or the prior FAIL report, its head and the finding ids)"
        failed = f"Prior review: report-review-{mid[:12]}.md FAIL (F1)\n"
        narrowed = f"Reviewed unit: the range {mid}..{head}\n"
        rewritten = support.git(self.repo, "commit-tree", f"{head}^{{tree}}", "-p", mid, "-m", "rewritten")
        rewritten_child = support.git(
            self.repo, "commit-tree", f"{head}^{{tree}}", "-p", rewritten, "-m", "rewritten child"
        )
        side = support.git(self.repo, "commit-tree", f"{head}^{{tree}}", "-m", "side root")
        side_child = support.git(self.repo, "commit-tree", f"{head}^{{tree}}", "-p", side, "-m", "side child")
        merged = support.git(self.repo, "commit-tree", f"{head}^{{tree}}", "-p", mid, "-p", side, "-m", "merge")
        keep_base = (
            "must keep the slice base: no commit named on the Prior review line lies inside it below its head, "
            "or was rewritten with the range starting at or below where the head diverged from it"
        )
        cases = (
            ("base kept", f"Reviewed unit: the range {base}..{head}\n"
             f"Prior review: report-review-{mid[:12]}.md FAIL (F1); slice base {base[:8]}\n", None),
            ("narrowed to the prior head", narrowed + failed,
             f"repair re-review range {mid}..{head} {keep_base}"),
            ("narrowed, naming the new head too", narrowed
             + f"Prior review: report-review-{mid[:12]}.md FAIL (F1); repair head {head[:7]}\n",
             f"repair re-review range {mid}..{head} {keep_base}"),
            ("rewritten sibling with divergence base kept",
             f"Reviewed unit: the range {mid}..{rewritten}\n"
             + f"Prior review: report-review-{head[:12]}.md FAIL (F1)\n", None),
            ("rewritten sibling with base narrowed above divergence",
             f"Reviewed unit: the range {rewritten}..{rewritten_child}\n"
             + f"Prior review: report-review-{head[:12]}.md FAIL (F1)\n",
             f"repair re-review range {rewritten}..{rewritten_child} {keep_base}"),
            ("head is ancestor of named commit",
             f"Reviewed unit: the range {base}..{mid}\n"
             + f"Prior review: report-review-{head[:12]}.md FAIL (F1)\n",
             f"repair re-review range {base}..{mid} {keep_base}"),
            ("a short head is no Reviewed unit range",
             f"Reviewed unit: the range {base}..{mid[:12]}\n"
             + f"Prior review: report-review-{head[:12]}.md FAIL (F1)\n",
             "repair re-review has no Reviewed unit range"),
            ("an upper-case head reads as the lower-case one",
             f"Reviewed unit: the range {base}..{mid.upper()}\n"
             + f"Prior review: report-review-{head[:12]}.md FAIL (F1)\n",
             f"repair re-review range {base}..{mid} {keep_base}"),
            ("no prior review", narrowed + f"Prior review: none {gloss}\n", None),
            ("prior FAIL named mid-line in prose", f"Scope note. Prior reviews: report-review-{mid[:12]}.md FAIL\n",
             None),
            ("FAIL naming no commit", narrowed + "Prior review: report-review-deadbeefcafe.md FAIL\n",
             "repair re-review Prior review names a FAIL but no commit in --repo"),
            ("no Reviewed unit range", failed, "repair re-review has no Reviewed unit range"),
            ("divergence on a merged side branch below the base",
             f"Reviewed unit: the range {base}..{merged}\n"
             + f"Prior review: report-review-{side_child[:12]}.md FAIL (F1)\n",
             f"repair re-review range {base}..{merged} {keep_base}"),
            ("root range kept", f"Reviewed unit: the range {gitops.NULL_OID}..{head}\n" + failed, None),
            ("rewritten sibling of a root range",
             f"Reviewed unit: the range {gitops.NULL_OID}..{rewritten}\n"
             + f"Prior review: report-review-{head[:12]}.md FAIL (F1)\n", None),
            ("unresolvable range", f"Reviewed unit: the range {head}..{base}\n" + f"Prior review: report-review-{mid[:12]}.md FAIL (F1)\n",
             f"repair re-review range {head}..{base} does not resolve in {self.repo}"),
        )
        for label, charter_lines, problem in cases:
            with self.subTest(label):
                code, _, error = self.run_lint(
                    self.reviewer_charter() + charter_lines, self.staffing_record()
                )
                expected = (0, "") if problem is None else (1, f"charter_lint: {problem}\n")
                self.assertEqual((code, error), expected)

    def test_the_charter_must_hold_the_send_block_the_backend_renders(self):
        rendered = FakeBackend().send_block(LEAD, REPORT).text
        wrong_lead = FakeBackend().send_block("lead-other", REPORT).text
        problem = f"charter_lint: missing report-by-prompt block, as fake renders it:\n{rendered}\n"
        for label, block in (
            ("absent", ""),
            ("another lead", wrong_lead),
            ("one byte changed", rendered.replace("FAKE-SEND", "FAKE-SENT")),
        ):
            with self.subTest(label):
                code, _, error = self.run_lint(self.engineer_charter().replace(rendered, block), self.staffing_record())
                self.assertEqual((code, error), (1, problem))

    def test_the_send_block_is_whatever_the_opened_backend_renders(self):
        block = herdr.Adapter({}).send_block(LEAD, REPORT)
        charter = self.engineer_charter().replace(FakeBackend().send_block(LEAD, REPORT).text, block.text)
        self.assertEqual(self.run_lint(charter, self.staffing_record(), herdr.Adapter({}))[::2], (0, ""))
        without_notice = charter.replace(block.failure_notice, "")
        code, _, error = self.run_lint(without_notice, self.staffing_record(), herdr.Adapter({}))
        self.assertEqual(code, 1)
        self.assertIn("as herdr renders it", error)
        code, _, error = self.run_lint(charter, self.staffing_record())
        self.assertEqual(code, 1)
        self.assertIn("as fake renders it", error)

    def test_a_charter_without_an_absolute_report_path_is_named(self):
        charter = self.engineer_charter().replace(FakeBackend().send_block(LEAD, REPORT).text, "").replace(REPORT, "report-eng-lint.md")
        code, _, error = self.run_lint(charter, self.staffing_record())
        self.assertEqual(code, 1)
        self.assertEqual(error, "charter_lint: missing report-by-prompt block: absolute <run-dir>/report-<peer>.md path\n")

    def test_a_send_block_the_backend_cannot_render_is_named(self):
        seats = FakeBackend()
        seats.script("send_block", ValueError("not a seat handle: 'x y'"))
        code, _, error = self.run_lint(self.engineer_charter(), self.staffing_record(), seats)
        self.assertEqual((code, error), (1, "charter_lint: report-by-prompt block cannot be rendered: not a seat handle: 'x y'\n"))

    def test_the_backend_flag_reaches_detect_as_explicit(self):
        charter_path = self.tmp / "charter.md"
        charter_path.write_text(self.engineer_charter(), encoding="utf-8")
        stderr = io.StringIO()
        with unittest.mock.patch.object(backend, "detect", side_effect=backend.DetectionError("stop")) as detect, \
                contextlib.redirect_stderr(stderr):
            code = charter_lint.main([
                "--charter", str(charter_path), "--lead", LEAD, "--repo", str(self.repo), "--backend", "herdr@w1:p1",
            ])
        self.assertEqual((code, stderr.getvalue()), (1, "charter_lint: stop\n"))
        self.assertEqual(detect.call_args.args[1], backend.Explicit("herdr", "w1:p1"))

    def test_a_backend_that_cannot_open_fails_closed(self):
        charter_path = self.tmp / "charter.md"
        charter_path.write_text(self.engineer_charter(), encoding="utf-8")
        stderr = io.StringIO()
        with unittest.mock.patch.object(
            charter_lint.backend, "open_backend", side_effect=backend.BackendUnavailable("tool unavailable")
        ), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
            code = charter_lint.main(["--charter", str(charter_path), "--lead", LEAD, "--repo", str(self.repo)])
        self.assertEqual((code, stderr.getvalue()), (1, "charter_lint: tool unavailable\n"))

    @staticmethod
    def engineer_charter() -> str:
        return (
            "Disposition: Engineer\n"
            "Owned paths: tests/test_charter_lint.py\n"
            + CharterLintTest.kill_guard_sentence()
            + CharterLintTest.takeover_guard_sentence()
            + "Write the finished report/verdict to report-eng-lint.md with the editor/write tool (never via the shell), then print it as the pane's final output.\n"
            + CharterLintTest.send_block_text()
        )

    @staticmethod
    def send_block_text(block: str | None = None) -> str:
        block = FakeBackend().send_block(LEAD, REPORT).text if block is None else block
        return (
            f"At send time, compose a prompt with the verdict/outcome line, a bounded summary (~200 words max), and full report at {REPORT}; "
            f"send it with exactly this block and NO other flags:\n{block}\n"
            "If the send exits non-zero: retry it ONCE; if it still fails, append a line SEND-FAILED to the end of the report file, then stop.\n"
        )

    @staticmethod
    def live_wake_guard_sentence() -> str:
        return (
            "No-mutation: the review changes no external state, so Never run `mailbox.py --wake` "
            "against a real seat: it prompts the seat recorded for the role it names.\n"
        )

    @staticmethod
    def kill_guard_sentence() -> str:
        return (
            "Never kill a process by pattern (`pkill -f`, `killall`, `pgrep ... | xargs kill`); "
            "stop only a process whose pid or task id you started yourself.\n"
        )

    @staticmethod
    def takeover_guard_sentence() -> str:
        return (
            "Never stop, remove, or take over a container, process, or port another agent, issue, "
            "or project started; report the collision to the Lead.\n"
        )

    @staticmethod
    def time_limit_sentence() -> str:
        return "Time limit: three hours after the latest Lead prompt with no verdict, send `BLOCKED (time limit)`.\n"

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
            + cls.takeover_guard_sentence()
            + cls.ocr_step_sentence()
            + "Review order: first the diff and your own findings; only then read the implementation reports.\n"
            + cls.time_limit_sentence()
            + "Write the finished report/verdict to report-eng-lint.md with the editor/write tool (never via the shell), then print it as the pane's final output.\n"
            + CharterLintTest.send_block_text()
        )

    def staffing_record(self) -> str:
        profile = self.tmp / "fence.sb"
        profile.write_text("(version 1)\n", encoding="utf-8")
        fence = self.fence_evidence()
        return (
            "ENGINEER: eng kind=pi model=m posture=none dialog=denied dialog-tools=ask_user_question,ask_question dialog-deny=*question* dialog-source=pi-1.0.4-active-tool-inventory skills=none extensions=none\n"
            f"REVIEWER: rev kind=pi model=m posture=prompting dialog=denied dialog-tools=ask_user_question,ask_question dialog-deny=*question* dialog-source=pi-1.0.4-active-tool-inventory skills=none extensions=none "
            f"{fence}\n"
        )

    def fence_evidence(self) -> str:
        return (
            f"fence=sandbox-exec(fence.sb; probe touch {self.tmp}/.fence-probe "
            "-> Operation not permitted, no file)"
        )


if __name__ == "__main__":
    unittest.main()
