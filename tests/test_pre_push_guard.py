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

    def test_new_tag_with_zero_remote_base_is_refused_on_populated_remote(self):
        c1 = self.advance("c1")
        self.assertEqual(self.review(self.base), 0)
        self.grant(f"origin refs/tags/v1 push {ZERO}..{c1}")
        code, _, err = self.invoke(self.ref_line(ZERO, c1, "refs/tags/v1"))
        self.assertEqual(code, 1)
        self.assertIn("no remote base", err)

    def test_new_branch_on_populated_remote_publishes_its_set_beyond_the_tracking_refs(self):
        c1 = self.advance("c1")
        line = self.ref_line(ZERO, c1, "refs/heads/feature")
        self.standing("origin:feature")
        code, _, err = self.invoke(line)
        self.assertEqual(code, 1)
        self.assertIn(f"refusing push of {self.base}..{c1}", err)
        self.assertEqual(self.review(self.base), 0)
        code, out, err = self.invoke(line)
        self.assertEqual(code, 0, err)
        self.assertIn("covered", out)

    def test_new_branch_with_two_boundary_commits_is_refused(self):
        self.git("checkout", "-qb", "side")
        side = self.advance("s1")
        self.git("push", "-q", "origin", "side")
        self.git("checkout", "-q", "main")
        self.advance("a1")
        self.git("merge", "-q", "--no-edit", "-X", "ours", "side")
        tip = self.rev("HEAD")
        self.assertEqual(self.review(ZERO), 0)
        self.standing("origin:feature")
        code, _, err = self.invoke(self.ref_line(ZERO, tip, "refs/heads/feature"))
        self.assertEqual(code, 1)
        self.assertIn("2 boundary commits", err)
        self.assertIn(self.base, err)
        self.assertIn(side, err)

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
        self.assertIn("publishes no commit outside the tips origin holds", err)

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
        self.grant(f"other refs/tags/v1 push {ZERO}..{c1}")
        self.grant(f"origin refs/tags/v1 push {ZERO}..{c1}")
        line = self.ref_line(ZERO, c1, "refs/tags/v1")
        code, out, err = self.invoke(line, ("other", str(other)))
        self.assertEqual(code, 0, err)
        self.assertIn("covered", out)
        code, _, err = self.invoke(line, ("origin", str(self.origin)))
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

    def test_real_git_push_of_a_new_branch_through_a_forwarding_hook_wrapper(self):
        hook = self.repo / ".git" / "hooks" / "pre-push"
        hook.write_text(
            "#!/bin/sh\n"
            f'exec "{sys.executable}" "{SCRIPTS / "pre_push_guard.py"}" '
            f'--ledger "{self.ledger}" --repo "{self.repo}" "$@"\n'
        )
        hook.chmod(0o755)
        self.git("checkout", "-qb", "feature")
        f1 = self.advance("f1")

        def push() -> subprocess.CompletedProcess:
            return subprocess.run(["git", "-C", str(self.repo), "push", "origin", "feature"],
                                  capture_output=True, text=True)

        refused = push()
        self.assertNotEqual(refused.returncode, 0)
        self.assertIn("no push authority", refused.stderr)
        self.grant(f"origin refs/heads/feature push {self.base}..{f1}")
        uncovered = push()
        self.assertNotEqual(uncovered.returncode, 0)
        self.assertIn(f"refusing push of {self.base}..{f1}", uncovered.stderr)
        self.assertIn("not covered", uncovered.stderr)
        self.assertEqual(self.review(self.base), 0)
        admitted = push()
        self.assertEqual(admitted.returncode, 0, admitted.stderr)
        self.assertEqual(self.rev("refs/remotes/origin/feature"), f1)

    def hook_wrapper(self) -> None:
        hook = self.repo / ".git" / "hooks" / "pre-push"
        hook.write_text(
            "#!/bin/sh\n"
            f'exec "{sys.executable}" "{SCRIPTS / "pre_push_guard.py"}" '
            f'--ledger "{self.ledger}" --repo "{self.repo}" "$@"\n'
        )
        hook.chmod(0o755)

    def test_real_git_push_of_a_new_branch_ignores_a_stale_tracking_ref(self):
        self.git("checkout", "-qb", "old")
        x = self.advance("x")
        self.git("push", "-q", "origin", "old")
        subprocess.run(["git", "-C", str(self.origin), "branch", "-D", "old"],
                       check=True, capture_output=True)
        self.assertEqual(self.rev("refs/remotes/origin/old"), x)  # unpruned, stale
        self.git("checkout", "-qb", "feature")
        f = self.advance("f")
        self.assertEqual(self.review(x), 0)
        self.grant(f"origin refs/heads/feature push {x}..{f}")
        self.hook_wrapper()
        pushed = subprocess.run(["git", "-C", str(self.repo), "push", "origin", "feature"],
                                capture_output=True, text=True)
        self.assertNotEqual(pushed.returncode, 0)
        self.assertIn(f"refusing push of {self.base}..{f}", pushed.stderr)
        branches = subprocess.run(["git", "-C", str(self.origin), "branch", "--contains", x],
                                  capture_output=True, text=True).stdout
        self.assertEqual(branches.strip(), "")

    def test_a_remote_tip_missing_locally_refuses_a_new_branch_naming_it(self):
        other = self.tmp / "other-clone"
        subprocess.run(["git", "clone", "-q", str(self.origin), str(other)], check=True)
        for args in (("config", "user.email", "t@example.invalid"), ("config", "user.name", "t"),
                     ("commit", "-q", "--allow-empty", "-m", "elsewhere"), ("push", "-q", "origin", "HEAD:side")):
            subprocess.run(["git", "-C", str(other), *args], check=True, capture_output=True)
        unseen = subprocess.run(["git", "-C", str(other), "rev-parse", "HEAD"],
                                check=True, capture_output=True, text=True).stdout.strip()
        self.git("checkout", "-qb", "feature")
        f = self.advance("f")
        self.assertEqual(self.review(self.base), 0)
        self.grant(f"origin refs/heads/feature push {self.base}..{f}")
        code, _, err = self.invoke(self.ref_line(ZERO, f, "refs/heads/feature"))
        self.assertEqual(code, 1)
        self.assertIn(f"origin holds {unseen} (refs/heads/side), which is not a local object", err)

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

    def digest(self, *pairs: tuple[Path, Path], extra: tuple[str, ...] = ()) -> tuple[int, str]:
        code, out, _ = self.run_guard(*pairs, extra=extra)
        return code, out

    def run_guard(self, *pairs: tuple[Path, Path], extra: tuple[str, ...] = ()) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        argv = [arg for ledger, repo in pairs for arg in ("--digest", str(ledger), str(repo))]
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = pre_push_guard.main([*argv, *extra])
        return code, out.getvalue(), err.getvalue()

    def items(self, out: str) -> str:
        return next(line for line in out.splitlines() if line.startswith("items: ")).removeprefix("items: ")

    def grant(self, *pairs: tuple[Path, Path], selection: str = "all", quote: str = "push it",
              items: str | None = None) -> tuple[int, str, str]:
        if items is None:
            items = self.items(self.digest(*pairs)[1])
        return self.run_guard(*pairs, extra=("--grant", selection, "--items", items, "--quote", quote))

    def grant_rows(self, ledger: Path) -> list[str]:
        return [row for row in gate_row.ledger_rows(ledger.read_text(encoding="utf-8"))
                if gate_row.row_evidence(row)[0] == "push-grant"]

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
        self.assertNotIn("\n  2. ", out.split("Question:")[1])

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
        self.git(quiet_repo, "push", "-q", "origin", "main")
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

    def test_grant_mode_writes_a_row_the_guard_accepts(self):
        ledger, repo, base = self.project("alpha")
        tip = self.advance(repo, "a1")
        self.review(ledger, repo, base)
        self.push_gate(ledger, repo)
        code, out, _ = self.grant((ledger, repo))
        self.assertEqual(code, 0)
        grant = gate_row.ledger_rows(ledger.read_text(encoding="utf-8"))[-1].split(" | ")[0]
        self.assertEqual(out, f"item 1: wrote {grant} to {ledger}\n")
        self.assertEqual(self.row(ledger, repo, "--check"), grant)
        self.assertEqual(pre_push_guard.check(ledger, repo, "origin", [("refs/heads/main", base, tip)]), [tip])
        _, again = self.digest((ledger, repo))
        self.assertIn(f"authority: granted by {grant}", again)

    def test_digest_prints_an_items_hash_and_no_grant_command(self):
        ledger, repo, base = self.project("alpha")
        self.advance(repo, "a1")
        self.review(ledger, repo, base)
        self.push_gate(ledger, repo)
        _, out = self.digest((ledger, repo))
        self.assertRegex(out, r"\nitems: [0-9a-f]{64}\n$")
        self.assertFalse([line for line in out.splitlines() if line.lstrip().startswith("grant:")])
        self.assertNotIn("<HUMAN-WORDS>", out)

    def two_branches(self) -> tuple[Path, Path, str, str, str]:
        ledger, repo, base = self.project("alpha")
        one = self.branch(ledger, repo, "one", base)
        two = self.branch(ledger, repo, "two", base)
        return ledger, repo, base, one, two

    def test_grant_all_writes_one_supervisor_row_per_item(self):
        ledger, repo, base, one, two = self.two_branches()
        code, out, _ = self.grant((ledger, repo))
        self.assertEqual(code, 0)
        rows = self.grant_rows(ledger)
        self.assertEqual(len(rows), 2)
        for row, name, tip in zip(rows, ("one", "two"), (one, two)):
            self.assertIn(f"| grant=origin refs/heads/{name} push {base}..{tip} |", row)
            self.assertIn("| status=open |", row)
            self.assertIn("| writer=supervisor |", row)
            self.assertIn("| channel=supervisor-relay:typed |", row)
            self.assertIn("| words=human |", row)
            self.assertIn(f"| note=Human grants push of {name} {base[:7]}..{tip[:7]} |", row)
            self.assertTrue(row.endswith(' | quote="push it"'))
        self.assertEqual(out.splitlines(), [f"item {n}: wrote {row.split(' | ')[0]} to {ledger}"
                                            for n, row in zip((1, 2), rows)])

    def test_grant_of_one_number_writes_only_that_item(self):
        ledger, repo, base, _, two = self.two_branches()
        code, _, _ = self.grant((ledger, repo), selection="2")
        self.assertEqual(code, 0)
        rows = self.grant_rows(ledger)
        self.assertEqual(len(rows), 1)
        self.assertIn(f"| grant=origin refs/heads/two push {base}..{two} |", rows[0])
        self.assertEqual(pre_push_guard.check(ledger, repo, "origin", [("refs/heads/two", base, two)]), [two])

    def assert_refused_without_write(self, pairs, needle: str, **kwargs) -> None:
        before = [ledger.read_bytes() for ledger, _ in pairs]
        code, out, err = self.grant(*pairs, **kwargs)
        self.assertEqual(code, 1)
        self.assertEqual(out, "")
        self.assertIn(needle, err)
        self.assertEqual([ledger.read_bytes() for ledger, _ in pairs], before)

    def test_grant_refuses_a_stale_items_hash_after_a_new_commit(self):
        ledger, repo, base = self.project("alpha")
        self.advance(repo, "a1")
        self.review(ledger, repo, base)
        self.push_gate(ledger, repo)
        stale = self.items(self.digest((ledger, repo))[1])
        mid = self.git(repo, "rev-parse", "HEAD")
        self.advance(repo, "a2")
        self.review(ledger, repo, mid)
        self.push_gate(ledger, repo)
        self.assert_refused_without_write([(ledger, repo)], "--items does not match", items=stale)

    def test_grant_refuses_a_not_ready_or_unknown_number_and_an_empty_quote(self):
        ledger, repo, base = self.project("alpha")
        self.branch(ledger, repo, "ready", base)
        self.branch(ledger, repo, "unreviewed", base, review=False)
        _, out = self.digest((ledger, repo))
        self.assertIn("NOT READY", out)
        self.assertNotIn("\n  2. ", out)
        for selection in ("2", "1,2", "0", "x"):
            self.assert_refused_without_write([(ledger, repo)], "--grant", selection=selection)
        for quote in ("", "  ", "two\nlines"):
            self.assert_refused_without_write([(ledger, repo)], "--quote", quote=quote)

    def test_grant_quote_with_shell_metacharacters_is_recorded_verbatim(self):
        ledger, repo, base = self.project("alpha")
        self.advance(repo, "a1")
        self.review(ledger, repo, base)
        self.push_gate(ledger, repo)
        marker = self.tmp / "executed"
        quote = f"it's ok $(touch {marker}) `touch {marker}` push"
        code, _, _ = self.grant((ledger, repo), quote=quote)
        self.assertEqual(code, 0)
        self.assertTrue(self.grant_rows(ledger)[0].endswith(f' | quote="{quote}"'))
        self.assertFalse(marker.exists())

    def test_a_failing_later_row_names_the_rows_already_written(self):
        ledger, repo, base, _, _ = self.two_branches()
        items = self.items(self.digest((ledger, repo))[1])
        real = gate_row.main
        calls = []

        def second_fails(argv):
            calls.append(argv)
            return real(argv) if len(calls) == 1 else (print("gate_row: boom", file=sys.stderr) or 1)

        with patch.object(pre_push_guard.gate_row, "main", second_fails):
            code, out, err = self.grant((ledger, repo), items=items)
        first = self.grant_rows(ledger)
        self.assertEqual(code, 1)
        self.assertEqual(len(first), 1)
        written = first[0].split(" | ")[0]
        self.assertIn(f"item 2: gate_row: boom; rows written before it: {written}", err)
        self.assertEqual(out, f"item 1: wrote {written} to {ledger}\n")

    def test_grant_flags_require_digest_and_each_other(self):
        ledger, repo, _ = self.project("alpha")
        for argv, needle in (
            (["--ledger", str(ledger), "--grant", "all"], "--grant, --items and --quote require --digest"),
            (["--digest", str(ledger), str(repo), "--grant", "all", "--quote", "q"],
             "--grant requires --items and --quote"),
            (["--digest", str(ledger), str(repo), "--items", "x"], "--items and --quote require --grant"),
        ):
            err = io.StringIO()
            with contextlib.redirect_stderr(err), self.assertRaises(SystemExit):
                pre_push_guard.main(argv)
            self.assertIn(needle, err.getvalue())

    def test_covered_new_branch_is_labeled_and_offered(self):
        ledger, repo, base = self.project("alpha")
        self.git(repo, "checkout", "-qb", "feature")
        tip = self.advance(repo, "f1")
        self.review(ledger, repo, base)
        self.push_gate(ledger, repo)
        code, out = self.digest((ledger, repo))
        self.assertEqual(code, 0)
        self.assertIn(f"range: new branch {base}..{tip} (1 commits)", out)
        self.assertEqual(self.grant((ledger, repo))[0], 0)
        self.assertIn(f"| grant=origin refs/heads/feature push {base}..{tip} |", self.grant_rows(ledger)[0])
        self.assertIn(f"  1. alpha feature new branch {base[:7]}..{tip[:7]} (1 commits)", out)
        self.assertNotIn("UNGATED", out)

    def test_checkout_ahead_of_upstream_without_open_gate_is_ungated_and_not_offered(self):
        ledger, repo, base = self.project("alpha")
        self.git(repo, "branch", "-q", "--set-upstream-to=origin/main")
        self.advance(repo, "a1")
        tip = self.advance(repo, "a2")
        self.review(ledger, repo, base)
        code, out = self.digest((ledger, repo))
        self.assertEqual(code, 0)
        self.assertIn(f"UNGATED: branch main, 2 commits, range {base}..{tip}", out)
        self.assertIn("no open push-gate: the Lead has not gated this work", out)
        self.assertIn("Question: none", out)

    def test_commits_past_an_open_gate_tip_are_ungated_alone_and_the_gate_still_offered(self):
        ledger, repo, base = self.project("alpha")
        self.git(repo, "branch", "-q", "--set-upstream-to=origin/main")
        gated = self.advance(repo, "a1")
        self.review(ledger, repo, base)
        self.push_gate(ledger, repo)
        head = self.advance(repo, "a2")
        code, out = self.digest((ledger, repo))
        self.assertEqual(code, 0)
        self.assertIn(f"range: {base}..{gated} (1 commits)", out)
        self.assertIn(f"UNGATED: branch main, 1 commits, range {gated}..{head}", out)
        self.assertIn(f"  1. alpha main {base[:7]}..{gated[:7]} (1 commits)", out)

    def branch(self, ledger: Path, repo: Path, name: str, start: str, review: bool = True) -> str:
        """A new branch from start with one commit, optionally reviewed, under an open push gate."""
        self.git(repo, "checkout", "-qb", name, start)
        tip = self.advance(repo, name)
        if review:
            self.review(ledger, repo, start)
        self.push_gate(ledger, repo)
        return tip

    def test_independent_new_branches_are_two_items(self):
        ledger, repo, base = self.project("alpha")
        one = self.branch(ledger, repo, "one", base)
        two = self.branch(ledger, repo, "two", base)
        code, out = self.digest((ledger, repo))
        self.assertEqual(code, 0)
        self.assertIn(f"range: new branch {base}..{one} (1 commits)", out)
        self.assertIn(f"range: new branch {base}..{two} (1 commits)", out)
        self.assertIn(f"  1. alpha one new branch {base[:7]}..{one[:7]} (1 commits)\n", out)
        self.assertIn(f"  2. alpha two new branch {base[:7]}..{two[:7]} (1 commits)\n", out)
        self.assertNotIn("stacked", out)

    def test_stacked_new_branch_names_its_dependency_and_starts_at_its_tip(self):
        ledger, repo, base = self.project("alpha")
        low = self.branch(ledger, repo, "low", base)
        high = self.branch(ledger, repo, "high", low)
        code, out = self.digest((ledger, repo))
        self.assertEqual(code, 0)
        self.assertIn("  stacked on low (item 1): push after it\n", out)
        self.assertIn(f"range: new branch {low}..{high} (1 commits)", out)
        self.assertEqual(self.grant((ledger, repo), selection="2")[0], 0)
        self.assertIn(f"| grant=origin refs/heads/high push {low}..{high} |", self.grant_rows(ledger)[0])
        self.assertIn(f"  1. alpha low new branch {base[:7]}..{low[:7]} (1 commits)\n", out)
        self.assertIn(f"  2. alpha high new branch {low[:7]}..{high[:7]} (1 commits), "
                      "stacked on low (item 1): push after it\n", out)

    def test_branch_stacked_on_a_not_ready_branch_is_not_offered_and_others_are(self):
        ledger, repo, base = self.project("alpha")
        low = self.branch(ledger, repo, "low", base, review=False)
        self.branch(ledger, repo, "high", low)
        other = self.branch(ledger, repo, "other", base)
        code, out = self.digest((ledger, repo))
        self.assertEqual(code, 0)
        low_block, high_block = out.split("branch: high")
        self.assertIn("NOT READY: refusing push", low_block)
        self.assertIn("stacked on low (NOT READY): push after it", high_block)
        self.assertIn("NOT READY: a branch it is stacked on is not offered", high_block)
        question = out.split("Question:")[1]
        self.assertIn(f"  1. alpha other new branch {base[:7]}..{other[:7]} (1 commits)\n", question)
        self.assertNotIn("\n  2. ", question)

    def test_real_pushes_in_item_order_with_recorded_grants_pass_the_guard(self):
        ledger, repo, base = self.project("alpha")
        low = self.branch(ledger, repo, "low", base)
        self.branch(ledger, repo, "high", low)
        hook = repo / ".git" / "hooks" / "pre-push"
        hook.write_text(f"#!/bin/sh\nexec {shlex.quote(sys.executable)} "
                        f"{shlex.quote(str(SCRIPTS / 'pre_push_guard.py'))} --ledger {shlex.quote(str(ledger))} "
                        f"--repo {shlex.quote(str(repo))} \"$@\"\n")
        hook.chmod(0o755)
        push = ["git", "-C", str(repo), "push", "-q", "origin"]
        self.assertNotEqual(subprocess.run([*push, "low"], capture_output=True).returncode, 0)
        self.assertEqual(self.grant((ledger, repo))[0], 0)
        self.assertEqual(len(self.grant_rows(ledger)), 2)
        for name in ("low", "high"):
            subprocess.run([*push, name], check=True, capture_output=True)
