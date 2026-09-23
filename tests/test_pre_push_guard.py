#!/usr/bin/env python3
"""Unit tests for the review-coverage pre-push guard."""
from __future__ import annotations

import contextlib
import io
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import gate_row  # noqa: E402
import pre_push_guard  # noqa: E402

ZERO = "0" * 40


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
        self.git("commit", "-qm", "base")
        # A bare origin the guard's manual mode and the pushed range resolve against.
        self.origin = self.tmp / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", str(self.origin)], check=True)
        self.git("remote", "add", "origin", str(self.origin))
        self.git("push", "-q", "origin", "main")
        self.base = self.rev("HEAD")
        self.ledger = self.tmp / "gates.md"
        self.ledger.write_text("# Gate ledger — test\n\n")
        self.addCleanup(self._tmp.cleanup)

    def git(self, *args: str) -> None:
        subprocess.run(["git", "-C", str(self.repo), *args], check=True,
                       capture_output=True, text=True)

    def rev(self, ref: str) -> str:
        return subprocess.run(
            ["git", "-C", str(self.repo), "rev-parse", ref],
            check=True, capture_output=True, text=True,
        ).stdout.strip()

    def advance(self, msg: str) -> str:
        (self.repo / "file.txt").write_text(f"{msg}\n")
        self.git("add", "file.txt")
        self.git("commit", "-qm", msg)
        return self.rev("HEAD")

    def set_empty_origin(self) -> None:
        empty = self.tmp / "empty-origin.git"
        subprocess.run(["git", "init", "-q", "--bare", str(empty)], check=True)
        self.git("remote", "set-url", "origin", str(empty))

    def review(self, base: str, status: str = "recorded:review-pass", quote: str = "PASS") -> int:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return gate_row.main([
                "--ledger", str(self.ledger), "--repo", str(self.repo),
                "--kind", "review", "--status", status, "--review-base", base,
                "--words", "seat", "--note", "review recorded", "--quote", quote,
            ])

    def ref_line(self, remote_base: str, local_tip: str) -> str:
        return f"refs/heads/main {local_tip} refs/heads/main {remote_base}\n"

    def invoke(self, stdin: str = "", hook_argv: tuple[str, ...] = ()) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with patch.object(pre_push_guard.sys, "stdin", io.StringIO(stdin)):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = pre_push_guard.main(
                    ["--repo", str(self.repo), "--ledger", str(self.ledger), *hook_argv]
                )
        return code, out.getvalue(), err.getvalue()

    def test_covered_range_via_manual_mode_is_allowed(self):
        c1 = self.advance("c1")
        self.assertEqual(self.review(self.base), 0)
        del c1
        code, out, err = self.invoke()  # empty stdin -> base derived from origin/main
        self.assertEqual(code, 0)
        self.assertIn("covered", out)
        self.assertEqual(err, "")

    def test_empty_non_tty_stdin_uses_origin_fallback_without_isatty(self):
        self.advance("c1")
        self.assertEqual(self.review(self.base), 0)

        class EmptyNonTTY:
            def read(self):
                return ""

            def isatty(self):
                raise AssertionError("the guard must use empty stdin, not isatty")

        out, err = io.StringIO(), io.StringIO()
        with patch.object(pre_push_guard.sys, "stdin", EmptyNonTTY()):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = pre_push_guard.main([
                    "--repo", str(self.repo), "--ledger", str(self.ledger),
                ])
        self.assertEqual(code, 0)
        self.assertIn("covered", out.getvalue())
        self.assertEqual(err.getvalue(), "")

    def test_failed_review_leaves_the_range_uncovered(self):
        c1 = self.advance("c1")
        self.assertEqual(self.review(self.base, "recorded:review-fail", "FAIL: 2 findings"), 0)
        code, _, err = self.invoke(self.ref_line(self.base, c1))
        self.assertEqual(code, 1)
        self.assertIn("not covered", err)

    def test_tiled_stack_of_two_reviewed_deliveries_is_allowed(self):
        c1 = self.advance("c1")
        self.assertEqual(self.review(self.base), 0)   # F-F: base..c1
        c2 = self.advance("c2")
        self.assertEqual(self.review(c1), 0)          # F-G: c1..c2
        code, out, err = self.invoke(self.ref_line(self.base, c2))
        self.assertEqual(code, 0, err)
        self.assertIn("covered", out)

    def test_uncovered_intermediate_in_the_stack_is_refused(self):
        c1 = self.advance("c1")
        self.assertEqual(self.review(self.base), 0)   # only base..c1 reviewed
        c2 = self.advance("c2")                        # c2 rides unreviewed
        code, _, err = self.invoke(self.ref_line(self.base, c2))
        self.assertEqual(code, 1)
        self.assertIn(c2, err)
        self.assertIn("not covered", err)

    def test_tampered_chain_is_reported_as_guard_error(self):
        self.advance("c1")
        for _ in range(3):
            self.assertEqual(self.review(self.base), 0)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        tampered = rows[1].replace("note=review recorded", "note=edited historical row")
        self.ledger.write_text(
            "# Gate ledger — test\n\n" + "\n".join([rows[0], tampered, rows[2]]) + "\n",
            encoding="utf-8",
        )
        code, out, err = self.invoke()
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("pre_push_guard:", err)
        self.assertIn("prev_hash", err)
        self.assertNotIn("Traceback", err)

    def test_range_with_no_review_row_is_refused(self):
        c1 = self.advance("c1")
        code, _, err = self.invoke(self.ref_line(self.base, c1))
        self.assertEqual(code, 1)
        self.assertIn("not covered", err)

    def test_new_ref_with_zero_remote_base_is_refused(self):
        c1 = self.advance("c1")
        self.assertEqual(self.review(self.base), 0)
        code, _, err = self.invoke(self.ref_line(ZERO, c1))
        self.assertEqual(code, 1)
        self.assertIn("no remote base", err)

    def test_new_ref_with_zero_remote_base_is_admitted_on_empty_remote(self):
        self.set_empty_origin()
        c1 = self.advance("c1")
        self.assertEqual(self.review(ZERO), 0)
        code, out, err = self.invoke(self.ref_line(ZERO, c1))
        self.assertEqual(code, 0, err)
        self.assertIn("covered", out)

    def test_pairs_none_absent_branch_on_empty_remote_is_admitted(self):
        self.set_empty_origin()
        self.git("checkout", "-qb", "feature")
        self.advance("feature commit")
        self.assertEqual(self.review(ZERO), 0)
        code, out, err = self.invoke()
        self.assertEqual(code, 0, err)
        self.assertIn("covered", out)

    def test_pairs_none_absent_branch_on_populated_remote_is_refused(self):
        self.git("checkout", "-qb", "feature")
        code, _, err = self.invoke()
        self.assertEqual(code, 1)
        self.assertIn("ref origin/feature has no remote base", err)

    def test_ledger_is_read_under_a_shared_lock(self):
        self.advance("c1")
        self.assertEqual(self.review(self.base), 0)
        with patch.object(
            pre_push_guard.gate_row,
            "locked_ledger",
            wraps=pre_push_guard.gate_row.locked_ledger,
        ) as locked:
            code, out, err = self.invoke()
        self.assertEqual(code, 0, err)
        self.assertIn("covered", out)
        self.assertEqual(err, "")
        locked.assert_called_once_with(self.ledger, exclusive=False)

    def test_a_branch_deletion_pushes_no_range_and_is_admitted(self):
        code, out, err = self.invoke(f"(delete) {ZERO} refs/heads/dead {self.base}\n")
        self.assertEqual(code, 0, err)
        self.assertIn("0 pushed range", out)

    def test_git_hook_argv_is_admitted_on_a_covered_range(self):
        c1 = self.advance("c1")
        self.assertEqual(self.review(self.base), 0)
        code, out, err = self.invoke(self.ref_line(self.base, c1), ("origin", str(self.origin)))
        self.assertEqual(code, 0, err)
        self.assertIn("covered", out)

    def test_hook_remote_decides_first_publication_not_origin(self):
        other = self.tmp / "other.git"
        subprocess.run(["git", "init", "-q", "--bare", str(other)], check=True)
        self.git("remote", "add", "other", str(other))
        c1 = self.advance("c1")
        self.assertEqual(self.review(ZERO), 0)
        code, out, err = self.invoke(self.ref_line(ZERO, c1), ("other", str(other)))
        self.assertEqual(code, 0, err)
        self.assertIn("covered", out)
        code, _, err = self.invoke(self.ref_line(ZERO, c1), ("origin", str(self.origin)))
        self.assertEqual(code, 1)
        self.assertIn("no remote base", err)

    def test_a_third_positional_is_refused(self):
        with self.assertRaises(SystemExit) as exc:
            self.invoke("", ("origin", str(self.origin), "extra"))
        self.assertEqual(exc.exception.code, 2)

    def test_real_git_push_through_a_forwarding_hook_wrapper(self):
        hook = self.repo / ".git" / "hooks" / "pre-push"
        hook.write_text(
            "#!/bin/sh\n"
            f'exec "{sys.executable}" "{SCRIPTS / "pre_push_guard.py"}" '
            f'--ledger "{self.ledger}" --repo "{self.repo}" "$@"\n'
        )
        hook.chmod(0o755)
        self.advance("c1")

        def push() -> subprocess.CompletedProcess:
            return subprocess.run(["git", "-C", str(self.repo), "push", "origin", "main"],
                                  capture_output=True, text=True)

        refused = push()
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("not covered", refused.stderr)
        self.assertEqual(self.review(self.base), 0)
        admitted = push()
        self.assertEqual(admitted.returncode, 0, admitted.stderr)
        self.assertIn("fully covered", admitted.stdout + admitted.stderr)


if __name__ == "__main__":
    unittest.main()
