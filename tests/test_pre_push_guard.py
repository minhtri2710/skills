#!/usr/bin/env python3
"""Unit tests for the review-coverage and push-authority pre-push guard."""
from __future__ import annotations

import contextlib
import io
import shlex
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
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

    def row(self, *args: str) -> int:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            return gate_row.main(["--ledger", str(self.ledger), "--repo", str(self.repo), *args])

    def standing(self, scope: str = "origin:main", expiry: str = "until-revoked") -> str:
        """Record a push-scoped standing delegation and return its id."""
        self.assertEqual(self.row(
            "--kind", "standing-delegation", "--status", "recorded:standing-delegation",
            "--who", "lead", "--scope", "pushes", "--conditions", "review PASS",
            "--expiry", expiry, "--push-scope", scope,
            "--words", "human", "--note", "standing push grant", "--quote", "push when green",
        ), 0)
        return self.last_id()

    def grant(self, spec: str) -> str:
        """Record a one-shot push-grant and return its id."""
        self.assertEqual(self.row(
            "--kind", "push-grant", "--status", "open", "--writer", "supervisor",
            "--channel", "supervisor-relay:typed", "--grant", spec,
            "--words", "human", "--note", "one-shot push grant", "--quote", "push this",
        ), 0)
        return self.last_id()

    def last_id(self) -> str:
        return gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))[-1].split(" | ")[0]

    def ref_line(self, remote_base: str, local_tip: str, ref: str = "refs/heads/main") -> str:
        return f"{ref} {local_tip} {ref} {remote_base}\n"

    def invoke(self, stdin: str = "", hook_argv: tuple[str, ...] = ()) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with patch.object(pre_push_guard.sys, "stdin", io.StringIO(stdin)):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = pre_push_guard.main(
                    ["--repo", str(self.repo), "--ledger", str(self.ledger), *hook_argv]
                )
        return code, out.getvalue(), err.getvalue()

    def test_covered_range_via_manual_mode_is_allowed(self):
        self.advance("c1")
        self.assertEqual(self.review(self.base), 0)
        self.standing()
        code, out, err = self.invoke()  # empty stdin -> base derived from origin/main
        self.assertEqual(code, 0)
        self.assertIn("covered", out)
        self.assertEqual(err, "")

    def test_empty_non_tty_stdin_uses_origin_fallback_without_isatty(self):
        self.advance("c1")
        self.assertEqual(self.review(self.base), 0)
        self.standing()

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
        self.standing()
        code, _, err = self.invoke(self.ref_line(self.base, c1))
        self.assertEqual(code, 1)
        self.assertIn("not covered", err)

    def test_tiled_stack_of_two_reviewed_deliveries_is_allowed(self):
        c1 = self.advance("c1")
        self.assertEqual(self.review(self.base), 0)   # F-F: base..c1
        c2 = self.advance("c2")
        self.assertEqual(self.review(c1), 0)          # F-G: c1..c2
        self.standing()
        code, out, err = self.invoke(self.ref_line(self.base, c2))
        self.assertEqual(code, 0, err)
        self.assertIn("covered", out)

    def test_uncovered_intermediate_in_the_stack_is_refused(self):
        c1 = self.advance("c1")
        self.assertEqual(self.review(self.base), 0)   # only base..c1 reviewed
        c2 = self.advance("c2")                        # c2 rides unreviewed
        self.standing()
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
        self.standing()
        code, _, err = self.invoke(self.ref_line(self.base, c1))
        self.assertEqual(code, 1)
        self.assertIn("not covered", err)

    def test_new_ref_with_zero_remote_base_is_refused(self):
        c1 = self.advance("c1")
        self.assertEqual(self.review(self.base), 0)
        self.standing()
        code, _, err = self.invoke(self.ref_line(ZERO, c1))
        self.assertEqual(code, 1)
        self.assertIn("no remote base", err)

    def test_new_ref_with_zero_remote_base_is_admitted_on_empty_remote(self):
        self.set_empty_origin()
        c1 = self.advance("c1")
        self.assertEqual(self.review(ZERO), 0)
        self.standing()
        code, out, err = self.invoke(self.ref_line(ZERO, c1))
        self.assertEqual(code, 0, err)
        self.assertIn("covered", out)

    def test_pairs_none_absent_branch_on_empty_remote_is_admitted(self):
        self.set_empty_origin()
        self.git("checkout", "-qb", "feature")
        self.advance("feature commit")
        self.assertEqual(self.review(ZERO), 0)
        self.standing("origin:feature")
        code, out, err = self.invoke()
        self.assertEqual(code, 0, err)
        self.assertIn("covered", out)

    def test_pairs_none_absent_branch_on_populated_remote_is_refused(self):
        self.git("checkout", "-qb", "feature")
        self.standing("origin:feature")
        code, _, err = self.invoke()
        self.assertEqual(code, 1)
        self.assertIn("ref refs/heads/feature has no remote base", err)

    def test_ledger_is_read_under_a_shared_lock(self):
        self.advance("c1")
        self.assertEqual(self.review(self.base), 0)
        self.standing()
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

    def test_a_deletion_needs_a_one_shot_grant_naming_it(self):
        line = f"(delete) {ZERO} refs/heads/dead {self.base}\n"
        self.standing("origin:dead")
        code, _, err = self.invoke(line)
        self.assertEqual(code, 1)
        self.assertIn("never covers a deletion", err)
        self.assertIn("one-shot kind=push-grant naming op delete", err)
        self.grant(f"origin refs/heads/dead delete {self.base}..{ZERO}")
        code, out, err = self.invoke(line)
        self.assertEqual(code, 0, err)
        self.assertIn("1 pushed ref", out)

    def test_git_hook_argv_is_admitted_on_a_covered_range(self):
        c1 = self.advance("c1")
        self.assertEqual(self.review(self.base), 0)
        self.standing()
        code, out, err = self.invoke(self.ref_line(self.base, c1), ("origin", str(self.origin)))
        self.assertEqual(code, 0, err)
        self.assertIn("covered", out)

    def test_hook_remote_decides_first_publication_not_origin(self):
        other = self.tmp / "other.git"
        subprocess.run(["git", "init", "-q", "--bare", str(other)], check=True)
        self.git("remote", "add", "other", str(other))
        c1 = self.advance("c1")
        self.assertEqual(self.review(ZERO), 0)
        self.standing("other:main,origin:main")
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

        c1 = self.rev("HEAD")
        self.assertEqual(self.review(self.base), 0)
        refused = push()
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("no push authority", refused.stderr)
        self.assertIn("no grant row", refused.stderr)
        self.grant(f"origin refs/heads/main push {self.base}..{c1}")
        admitted = push()
        self.assertEqual(admitted.returncode, 0, admitted.stderr)
        self.assertIn("a Human grant", admitted.stdout + admitted.stderr)

    # --- push authority -------------------------------------------------

    def test_covered_push_without_a_grant_is_refused(self):
        c1 = self.advance("c1")
        self.assertEqual(self.review(self.base), 0)
        code, out, err = self.invoke(self.ref_line(self.base, c1))
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn("no push authority", err)
        self.assertIn("no grant row in the ledger", err)

    def test_one_shot_grant_admits_exactly_its_range_remote_and_branch(self):
        c1 = self.advance("c1")
        self.assertEqual(self.review(self.base), 0)
        c2 = self.advance("c2")
        self.assertEqual(self.review(c1), 0)
        self.grant(f"origin refs/heads/main push {self.base}..{c1}")
        self.assertEqual(self.invoke(self.ref_line(self.base, c1))[0], 0)
        code, _, err = self.invoke(self.ref_line(self.base, c2))
        self.assertEqual(code, 1)
        self.assertIn(f"grant scope is range {self.base}..{c1}", err)
        code, _, err = self.invoke(self.ref_line(self.base, c1, "refs/heads/dev"))
        self.assertEqual(code, 1)
        self.assertIn("grant scope is origin refs/heads/main push", err)
        other = self.tmp / "other.git"
        subprocess.run(["git", "init", "-q", "--bare", str(other)], check=True)
        code, _, err = self.invoke(self.ref_line(self.base, c1), ("other", str(other)))
        self.assertEqual(code, 1)
        self.assertIn("grant scope is origin refs/heads/main push", err)

    def test_a_pushed_range_inside_the_granted_range_is_admitted(self):
        c1 = self.advance("c1")
        c2 = self.advance("c2")
        self.assertEqual(self.review(self.base), 0)
        self.grant(f"origin refs/heads/main push {self.base}..{c2}")
        code, out, err = self.invoke(self.ref_line(c1, c2))
        self.assertEqual(code, 0, err)

    def test_a_consumed_grant_authorizes_nothing(self):
        c1 = self.advance("c1")
        self.assertEqual(self.review(self.base), 0)
        gid = self.grant(f"origin refs/heads/main push {self.base}..{c1}")
        self.git("push", "-q", "origin", "main")
        self.assertEqual(self.row(
            "--kind", "push", "--status", "resolved:instruction", "--push-base", self.base,
            "--boundary", ".", "--resolves", gid,
            "--words", "human", "--note", "pushed under grant", "--quote", "push this",
        ), 0)
        code, _, err = self.invoke(self.ref_line(self.base, c1))
        self.assertEqual(code, 1)
        self.assertIn(f"{gid} grant is consumed", err)
        c2 = self.advance("c2")
        self.assertEqual(self.review(c1), 0)
        code, _, err = self.invoke(self.ref_line(c1, c2))
        self.assertEqual(code, 1)
        self.assertIn(f"{gid} grant scope is range", err)

    def test_standing_grant_in_force_admits_and_expired_refuses(self):
        c1 = self.advance("c1")
        self.assertEqual(self.review(self.base), 0)
        gid = self.standing(expiry="2001-01-01T00:00:00Z")
        code, _, err = self.invoke(self.ref_line(self.base, c1))
        self.assertEqual(code, 1)
        self.assertIn(f"{gid} standing delegation expiry 2001-01-01T00:00:00Z has passed", err)
        self.standing(expiry="2999-01-01T00:00:00Z")
        self.assertEqual(self.invoke(self.ref_line(self.base, c1))[0], 0)

    def test_expiry_is_compared_against_the_passed_clock(self):
        c1 = self.advance("c1")
        self.standing(expiry="2030-06-01T12:00:00Z")
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))

        def at(instant: str) -> None:
            gate_row.require_push_authority(
                rows, self.repo, "origin", "refs/heads/main", self.base, c1,
                datetime.strptime(instant, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc))

        at("2030-06-01T11:59:59Z")
        with self.assertRaisesRegex(gate_row.RowError, "has passed"):
            at("2030-06-01T12:00:00Z")

    def test_revoked_standing_grant_refuses(self):
        c1 = self.advance("c1")
        self.assertEqual(self.review(self.base), 0)
        gid = self.standing()
        self.assertEqual(self.invoke(self.ref_line(self.base, c1))[0], 0)
        self.assertEqual(self.row(
            "--kind", "revocation", "--status", "resolved:instruction", "--resolves", gid,
            "--words", "human", "--note", "delegation revoked", "--quote", "stop pushing",
        ), 0)
        code, _, err = self.invoke(self.ref_line(self.base, c1))
        self.assertEqual(code, 1)
        self.assertIn(f"{gid} standing delegation is revoked", err)

    def test_standing_grant_scope_names_remote_and_branch(self):
        c1 = self.advance("c1")
        self.assertEqual(self.review(self.base), 0)
        gid = self.standing("origin:dev")
        code, _, err = self.invoke(self.ref_line(self.base, c1))
        self.assertEqual(code, 1)
        self.assertIn(f"{gid} standing delegation scope is push-scope=origin:dev", err)

    def test_standing_grant_never_covers_a_force_push(self):
        c1 = self.advance("c1")
        self.git("checkout", "-qb", "side", self.base)
        d1 = self.advance("d1")
        self.assertEqual(self.review(self.base), 0)
        self.standing()
        code, _, err = self.invoke(self.ref_line(c1, d1))
        self.assertEqual(code, 1)
        self.assertIn("never covers a force push", err)
        self.assertIn("naming op force", err)
        self.grant(f"origin refs/heads/main force {c1}..{d1}")
        code, _, err = self.invoke(self.ref_line(c1, d1))
        self.assertEqual(code, 0, err)

    def test_standing_grant_never_covers_a_tag(self):
        c1 = self.advance("c1")
        self.assertEqual(self.review(self.base), 0)
        self.standing()
        code, _, err = self.invoke(self.ref_line(self.base, c1, "refs/tags/v1"))
        self.assertEqual(code, 1)
        self.assertIn("never covers a tag push", err)

    def test_a_free_text_standing_row_authorizes_no_push(self):
        c1 = self.advance("c1")
        self.assertEqual(self.review(self.base), 0)
        self.assertEqual(self.row(
            "--kind", "standing-delegation", "--status", "recorded:standing-delegation",
            "--who", "lead", "--scope", "push when green", "--conditions", "review PASS",
            "--expiry", "the Human's next substantive instruction",
            "--words", "human", "--note", "free-text delegation", "--quote", "push when green",
        ), 0)
        gid = self.last_id()
        code, _, err = self.invoke(self.ref_line(self.base, c1))
        self.assertEqual(code, 1)
        self.assertIn(f"{gid} standing delegation has no push-scope", err)


if __name__ == "__main__":
    unittest.main()


class PushDigestTest(unittest.TestCase):
    """--digest: every project's open push gates as one range, read-only, one question."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir="/private/tmp")
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)

    def project(self, name: str) -> tuple[Path, Path, str]:
        """A repo pushed to a bare origin, with an empty ledger at <name>/gates.md."""
        root = self.tmp / name
        repo = root / "repo"
        repo.mkdir(parents=True)
        origin = root / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
        for args in (("init", "-q", "-b", "main"), ("config", "user.email", "t@example.invalid"),
                     ("config", "user.name", "t"), ("remote", "add", "origin", str(origin))):
            self.git(repo, *args)
        base = self.advance(repo, "base")
        self.git(repo, "push", "-q", "origin", "main")
        ledger = root / "gates.md"
        ledger.write_text("# Gate ledger — test\n\n")
        return ledger, repo, base

    def git(self, repo: Path, *args: str) -> str:
        return subprocess.run(["git", "-C", str(repo), *args], check=True,
                              capture_output=True, text=True).stdout.strip()

    def advance(self, repo: Path, msg: str) -> str:
        (repo / "file.txt").write_text(f"{msg}\n")
        self.git(repo, "add", "file.txt")
        self.git(repo, "commit", "-qm", msg)
        return self.git(repo, "rev-parse", "HEAD")

    def row(self, ledger: Path, repo: Path, *args: str) -> str:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(gate_row.main(["--ledger", str(ledger), "--repo", str(repo), *args]), 0)
        return gate_row.ledger_rows(ledger.read_text(encoding="utf-8"))[-1].split(" | ")[0]

    def review(self, ledger: Path, repo: Path, base: str) -> str:
        return self.row(ledger, repo, "--kind", "review", "--status", "recorded:review-pass",
                        "--review-base", base, "--words", "seat", "--note", "review", "--quote", "PASS")

    def push_gate(self, ledger: Path, repo: Path) -> str:
        return self.row(ledger, repo, "--kind", "push-gate", "--status", "open",
                        "--words", "none", "--note", "push awaits the Human")

    def digest(self, *pairs: tuple[Path, Path]) -> tuple[int, str]:
        out = io.StringIO()
        argv = [arg for ledger, repo in pairs for arg in ("--digest", str(ledger), str(repo))]
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = pre_push_guard.main(argv)
        return code, out.getvalue()

    def test_ready_and_uncovered_projects_only_ready_is_offered(self):
        ready, ready_repo, ready_base = self.project("alpha")
        tip = self.advance(ready_repo, "a1")
        review = self.review(ready, ready_repo, ready_base)
        gate = self.push_gate(ready, ready_repo)
        bare, bare_repo, bare_base = self.project("beta")
        self.advance(bare_repo, "b1")
        self.push_gate(bare, bare_repo)
        code, out = self.digest((ready, ready_repo), (bare, bare_repo))
        self.assertEqual(code, 0)
        alpha, beta = out.split("== beta")
        self.assertIn(f"gates: {gate}", alpha)
        self.assertIn(f"range: {ready_base}..{tip} (1 commits)", alpha)
        self.assertIn(f"review rows: {review}; coverage ok", alpha)
        self.assertIn("authority: needs push-grant", alpha)
        self.assertIn("NOT READY: refusing push", beta)
        self.assertIn("not covered by any review PASS range", beta)
        self.assertIn(f"  1. alpha main {ready_base[:7]}..{tip[:7]} (1 commits)", out)
        self.assertNotIn("2.", out.split("Question:")[1])

    def test_stacked_open_gates_collapse_to_one_range(self):
        ledger, repo, base = self.project("alpha")
        self.advance(repo, "c1")
        self.review(ledger, repo, base)
        first = self.push_gate(ledger, repo)
        mid = self.git(repo, "rev-parse", "HEAD")
        tip = self.advance(repo, "c2")
        self.review(ledger, repo, mid)
        second = self.push_gate(ledger, repo)
        code, out = self.digest((ledger, repo))
        self.assertEqual(code, 0)
        self.assertIn(f"gates: {first} {second}", out)
        self.assertIn(f"range: {base}..{tip} (2 commits)", out)
        self.assertEqual(out.count("== "), 1)
        self.assertEqual(out.count("  1. "), 1)

    def test_project_without_open_push_gate_is_omitted(self):
        ledger, repo, _ = self.project("alpha")
        quiet, quiet_repo, quiet_base = self.project("quiet")
        self.advance(quiet_repo, "q1")
        self.review(quiet, quiet_repo, quiet_base)
        code, out = self.digest((ledger, repo), (quiet, quiet_repo))
        self.assertEqual(code, 0)
        self.assertNotIn("==", out)
        self.assertIn("Question: none", out)

    def test_read_error_in_one_project_reports_the_other_and_exits_nonzero(self):
        ledger, repo, base = self.project("alpha")
        self.advance(repo, "a1")
        self.review(ledger, repo, base)
        self.push_gate(ledger, repo)
        missing = self.tmp / "gone" / "gates.md"
        code, out = self.digest((missing, repo), (ledger, repo))
        self.assertEqual(code, 1)
        self.assertIn("== gone", out)
        self.assertIn("ERROR:", out)
        self.assertIn("  1. alpha main", out)

    def test_digest_writes_no_ledger_byte(self):
        ledger, repo, base = self.project("alpha")
        self.advance(repo, "a1")
        self.review(ledger, repo, base)
        self.push_gate(ledger, repo)
        other, other_repo, _ = self.project("beta")
        self.advance(other_repo, "b1")
        self.push_gate(other, other_repo)
        before = (ledger.read_bytes(), other.read_bytes())
        self.digest((ledger, repo), (other, other_repo))
        self.assertEqual((ledger.read_bytes(), other.read_bytes()), before)

    def test_printed_grant_command_writes_a_row_the_guard_accepts(self):
        ledger, repo, base = self.project("alpha")
        tip = self.advance(repo, "a1")
        self.review(ledger, repo, base)
        self.push_gate(ledger, repo)
        _, out = self.digest((ledger, repo))
        command = next(line for line in out.splitlines() if line.startswith("  grant: "))
        argv = shlex.split(command.removeprefix("  grant: ").replace("<HUMAN-WORDS>", "push it"))
        self.assertEqual(Path(argv[1]).resolve(), (SCRIPTS / "gate_row.py").resolve())
        subprocess.run([sys.executable, *argv[1:]], check=True, capture_output=True)
        grant = gate_row.ledger_rows(ledger.read_text(encoding="utf-8"))[-1].split(" | ")[0]
        self.assertEqual(pre_push_guard.check(ledger, repo, "origin", [("refs/heads/main", base, tip)]), [tip])
        _, again = self.digest((ledger, repo))
        self.assertIn(f"authority: granted by {grant}", again)
        self.assertNotIn("grant: ", again.replace("granted by", ""))
