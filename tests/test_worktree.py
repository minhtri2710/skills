#!/usr/bin/env python3
"""Unit tests for beo_worktree.py.

Tests cover path-safety, branch-name sanitization, and git orchestration
in isolated temporary repositories.
"""
from __future__ import annotations

import contextlib
import importlib
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

REFERENCE_ROOT = Path(__file__).resolve().parents[1] / "skills" / "beo" / "beo-reference"
SCRIPTS = REFERENCE_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))

import beo_worktree


class WorktreePathTest(unittest.TestCase):
    def test_accepts_valid_issue_id(self):
        """A typical Beads issue id like 'br-123' must produce a path under WORKTREE_BASE."""
        import beo_worktree
        path = beo_worktree.worktree_path("br-123")
        self.assertEqual(path.name, "br-123")
        self.assertEqual(path.parent, beo_worktree.WORKTREE_BASE)

    def test_rejects_path_traversal(self):
        """An issue_id containing '..' must be rejected with ValueError."""
        import beo_worktree
        with self.assertRaises(ValueError):
            beo_worktree.worktree_path("../etc/passwd")

    def test_rejects_absolute_path(self):
        """An issue_id starting with '/' must be rejected."""
        import beo_worktree
        with self.assertRaises(ValueError):
            beo_worktree.worktree_path("/etc/passwd")

    def test_rejects_shell_metacharacters(self):
        """An issue_id with shell metacharacters must be rejected."""
        import beo_worktree
        for bad in ("br;rm", "br$foo", "br|bar", "br`x`", "br&y"):
            with self.subTest(bad=bad):
                with self.assertRaises(ValueError):
                    beo_worktree.worktree_path(bad)

    def test_rejects_empty_issue_id(self):
        """An empty issue_id must be rejected."""
        import beo_worktree
        with self.assertRaises(ValueError):
            beo_worktree.worktree_path("")

    def test_accepts_long_issue_id_within_limit(self):
        """An issue_id up to 121 chars (regex allows 1 + 120) must be accepted."""
        import beo_worktree
        long_id = "br-" + "a" * 117  # 120 chars total
        path = beo_worktree.worktree_path(long_id)
        self.assertEqual(path.name, long_id)

    def test_rejects_oversize_issue_id(self):
        """An issue_id beyond 121 chars must be rejected to bound disk usage."""
        import beo_worktree
        oversize = "br-" + "a" * 200
        with self.assertRaises(ValueError):
            beo_worktree.worktree_path(oversize)


class WorktreeBranchTest(unittest.TestCase):
    def test_produces_expected_branch_shape(self):
        """The branch must follow the documented convention beo/<issue>/<actor>/<timestamp>."""
        import beo_worktree
        branch = beo_worktree.worktree_branch("br-123", "alice", "20260616T120000Z")
        self.assertEqual(branch, "beo/br-123/alice/20260616T120000Z")

    def test_sanitizes_path_metacharacters_in_actor(self):
        """Path-meaningful chars in the actor are replaced; safe chars (._-) survive."""
        import beo_worktree
        branch = beo_worktree.worktree_branch("br-1", "a/b.c", "20260616T120000Z")
        # `/` becomes `-`. `.` is in SAFE_BRANCH_CHAR and survives, but the
        # post-sanitize check rejects actors that start with `.`. The full
        # sanitization result is `a-b.c`, then the starts-with-dot check
        # is not triggered because the actor starts with `a`, not `.`.
        self.assertEqual(branch, "beo/br-1/a-b.c/20260616T120000Z")

    def test_sanitizes_shell_metacharacters_in_actor(self):
        """Shell metacharacters in the actor must be replaced, not echoed to a branch name."""
        import beo_worktree
        branch = beo_worktree.worktree_branch("br-1", "a;b$c", "20260616T120000Z")
        for forbidden in (";", "$", "&", "|", "`", "(", ")", "<", ">", "*", "?", "[", "]", "\\", "'", '"', " "):
            self.assertNotIn(forbidden, branch)

    def test_strips_leading_and_trailing_dashes_from_actor(self):
        """Leading/trailing dashes from sanitization must be stripped for clean branch shape."""
        import beo_worktree
        branch = beo_worktree.worktree_branch("br-1", "///", "20260616T120000Z")
        # The actor is all stripped, falls back to "unknown"
        self.assertEqual(branch, "beo/br-1/unknown/20260616T120000Z")

    def test_uses_unknown_for_empty_actor(self):
        """An actor that sanitizes to empty must fall back to 'unknown'."""
        import beo_worktree
        branch = beo_worktree.worktree_branch("br-1", "///", "20260616T120000Z")
        self.assertIn("/unknown/", branch)

    def test_rejects_actor_starting_with_dot(self):
        """A git branch component must not start with '.'; the function must raise."""
        import beo_worktree
        # The sanitization preserves '.' (it's in SAFE_BRANCH_CHAR), so the
        # post-sanitize starts-with-dot check must catch this and raise.
        with self.assertRaises(ValueError):
            beo_worktree.worktree_branch("br-1", ".foo", "20260616T120000Z")
        with self.assertRaises(ValueError):
            beo_worktree.worktree_branch("br-1", "..hidden", "20260616T120000Z")

    def test_rejects_actor_ending_with_lock(self):
        """A git ref must not end with '.lock'; the function must raise."""
        import beo_worktree
        with self.assertRaises(ValueError):
            beo_worktree.worktree_branch("br-1", "evil.lock", "20260616T120000Z")

    def test_rejects_actor_with_double_dot(self):
        """A git branch component must not contain '..' anywhere.

        Dots survive sanitization (they are in SAFE_BRANCH_CHAR), so an actor
        of 'a..b' reaches the post-sanitize '..' guard and must raise.
        """
        import beo_worktree
        with self.assertRaises(ValueError):
            beo_worktree.worktree_branch("br-1", "a..b", "20260616T120000Z")

    def test_propagates_issue_id_validation(self):
        """An unsafe issue_id must be rejected by worktree_branch too."""
        import beo_worktree
        with self.assertRaises(ValueError):
            beo_worktree.worktree_branch("../evil", "alice", "20260616T120000Z")


class NowUtcTest(unittest.TestCase):
    def test_returns_compact_utc_timestamp(self):
        """now_utc() must return a string in compact UTC form YYYYMMDDTHHMMSSZ."""
        import beo_worktree
        ts = beo_worktree.now_utc()
        self.assertRegex(ts, r"^\d{8}T\d{6}Z$")

    def test_now_utc_is_stable_length(self):
        """All timestamps must be the same length for use in branch names."""
        import beo_worktree
        ts1 = beo_worktree.now_utc()
        ts2 = beo_worktree.now_utc()
        self.assertEqual(len(ts1), len(ts2))
        self.assertEqual(len(ts1), 16)  # YYYYMMDDTHHMMSSZ


class WorktreeBaseTest(unittest.TestCase):
    def test_worktree_base_uses_env_override(self):
        """BEO_WORKTREE_BASE must override the default /tmp/beo-worktrees path."""
        import beo_worktree
        self.addCleanup(importlib.reload, beo_worktree)
        with mock.patch.dict(os.environ, {"BEO_WORKTREE_BASE": "/var/tmp/custom"}):
            importlib.reload(beo_worktree)
            base = beo_worktree.WORKTREE_BASE
            self.assertEqual(base, Path("/var/tmp/custom"))


class GitRepoTestCase(unittest.TestCase):
    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmpdir.cleanup)
        self.root = Path(self.tmpdir.name) / "repo"
        self.root.mkdir()
        self.git("init", "-q", cwd=self.root)
        self.git("config", "user.email", "test@example.com", cwd=self.root)
        self.git("config", "user.name", "Test User", cwd=self.root)
        (self.root / "README.md").write_text("initial\n", encoding="utf-8")
        self.git("add", "README.md", cwd=self.root)
        self.git("commit", "-m", "initial", cwd=self.root)

        self.base = Path(self.tmpdir.name) / "worktrees"
        patcher = mock.patch.object(beo_worktree, "WORKTREE_BASE", self.base)
        patcher.start()
        self.addCleanup(patcher.stop)

    def invoke(self, fn, *args) -> tuple[int, dict]:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            rc = fn(*args)
        return rc, json.loads(output.getvalue())

    def run_exit(self, fn, *args) -> dict:
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with self.assertRaises(SystemExit) as raised:
                fn(*args)
        self.assertEqual(raised.exception.code, 1)
        return json.loads(output.getvalue())

    def git(self, *args, cwd=None):
        return subprocess.run(
            ["git", *args],
            cwd=cwd,
            check=True,
            capture_output=True,
            text=True,
        )

    def commit_in(self, path, filename, content, message):
        path = Path(path)
        (path / filename).write_text(content, encoding="utf-8")
        self.git("-C", path, "add", filename)
        self.git("-C", path, "commit", "-m", message)

    def test_create_success(self):
        original_branch = self.git(
            "rev-parse", "--abbrev-ref", "HEAD", cwd=self.root
        ).stdout.strip()
        root_head = self.git("rev-parse", "HEAD", cwd=self.root).stdout.strip()

        rc, result = self.invoke(beo_worktree.cmd_create, self.root, "br-1", "alice")

        self.assertEqual(rc, 0)
        self.assertEqual(result["status"], "success")
        self.assertRegex(result["branch"], r"^beo/br-1/alice/\d{8}T\d{6}Z$")
        worktree = Path(result["worktree_path"])
        self.assertTrue(worktree.is_dir())
        self.assertEqual(
            worktree.resolve(), beo_worktree.worktree_path("br-1").resolve()
        )
        self.assertEqual(result["head_ref"], root_head)
        self.assertEqual(
            self.git("rev-parse", "--abbrev-ref", "HEAD", cwd=self.root).stdout.strip(),
            original_branch,
        )

    def test_create_handles_beads_symlink_and_absence(self):
        rc, absent = self.invoke(beo_worktree.cmd_create, self.root, "br-2", "alice")
        self.assertEqual(rc, 0)
        self.assertEqual(absent["status"], "success")
        self.assertFalse(
            beo_worktree.worktree_path("br-2").resolve().joinpath(".beads").exists()
        )
        self.invoke(beo_worktree.cmd_cleanup, self.root, "br-2", "test")

        main_beads = self.root / ".beads"
        main_beads.mkdir()
        rc, result = self.invoke(beo_worktree.cmd_create, self.root, "br-1", "alice")

        self.assertEqual(rc, 0)
        self.assertEqual(result["status"], "success")
        worktree_beads = Path(result["worktree_path"]) / ".beads"
        self.assertTrue(worktree_beads.is_symlink())
        self.assertEqual(worktree_beads.resolve(), main_beads.resolve())

    def test_create_refuses_dirty_tree(self):
        (self.root / "untracked.txt").write_text("dirty\n", encoding="utf-8")

        result = self.run_exit(
            beo_worktree.cmd_create, self.root, "br-1", "alice"
        )

        self.assertEqual(result["status"], "failed")

    def test_create_is_idempotent(self):
        first_rc, first = self.invoke(
            beo_worktree.cmd_create, self.root, "br-1", "alice"
        )
        second_rc, second = self.invoke(
            beo_worktree.cmd_create, self.root, "br-1", "alice"
        )

        self.assertEqual(first_rc, 0)
        self.assertEqual(first["status"], "success")
        self.assertEqual(second_rc, 0)
        self.assertEqual(second["status"], "exists")
        self.assertEqual(second["branch"], first["branch"])

    def test_create_reuses_branch_for_stale_worktree(self):
        _, first = self.invoke(beo_worktree.cmd_create, self.root, "br-1", "alice")
        shutil.rmtree(Path(first["worktree_path"]))

        rc, result = self.invoke(beo_worktree.cmd_create, self.root, "br-1", "alice")

        self.assertEqual(rc, 0)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["branch"], first["branch"])

    def test_status_reports_not_found_active_and_stale(self):
        rc, result = self.invoke(beo_worktree.cmd_status, self.root, "br-1")
        self.assertEqual(rc, 0)
        self.assertEqual(result["status"], "not_found")

        _, created = self.invoke(beo_worktree.cmd_create, self.root, "br-1", "alice")
        rc, result = self.invoke(beo_worktree.cmd_status, self.root, "br-1")
        self.assertEqual(rc, 0)
        self.assertEqual(result["status"], "active")
        self.assertEqual(result["branch"], created["branch"])
        self.assertEqual(
            Path(result["worktree_path"]).resolve(),
            beo_worktree.worktree_path("br-1").resolve(),
        )
        self.assertIsNotNone(result["latest_commit"])

        shutil.rmtree(Path(created["worktree_path"]))
        rc, result = self.invoke(beo_worktree.cmd_status, self.root, "br-1")
        self.assertEqual(rc, 0)
        self.assertEqual(result["status"], "stale")
        self.assertEqual(result["branch"], created["branch"])

    def test_merge_reports_not_found_for_missing_and_unregistered_paths(self):
        rc, result = self.invoke(beo_worktree.cmd_merge, self.root, "br-1")
        self.assertEqual(rc, 1)
        self.assertEqual(result["status"], "not_found")

        worktree = beo_worktree.worktree_path("br-1")
        worktree.mkdir(parents=True)
        rc, result = self.invoke(beo_worktree.cmd_merge, self.root, "br-1")
        self.assertEqual(rc, 1)
        self.assertEqual(result["status"], "not_found")

    def test_merge_reports_no_changes_after_create(self):
        _, created = self.invoke(beo_worktree.cmd_create, self.root, "br-1", "alice")

        rc, result = self.invoke(beo_worktree.cmd_merge, self.root, "br-1")

        self.assertEqual(rc, 0)
        self.assertEqual(result["status"], "no_changes")
        self.assertEqual(result["branch"], created["branch"])

    def test_merge_success_creates_no_ff_merge(self):
        _, created = self.invoke(beo_worktree.cmd_create, self.root, "br-1", "alice")
        self.commit_in(
            created["worktree_path"], "merged.txt", "from worktree\n", "worktree change"
        )

        rc, result = self.invoke(beo_worktree.cmd_merge, self.root, "br-1")

        self.assertEqual(rc, 0)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["branch"], created["branch"])
        self.assertTrue((self.root / "merged.txt").is_file())
        parents = self.git("log", "-1", "--pretty=%P", cwd=self.root).stdout.strip().split()
        self.assertEqual(len(parents), 2)
        self.assertEqual(
            self.git("status", "--porcelain", cwd=self.root).stdout.strip(), ""
        )

    def test_merge_conflict_is_aborted(self):
        _, created = self.invoke(beo_worktree.cmd_create, self.root, "br-1", "alice")
        self.commit_in(
            created["worktree_path"], "conflict.txt", "A\n", "worktree conflict"
        )
        self.commit_in(self.root, "conflict.txt", "B\n", "root conflict")

        rc, result = self.invoke(beo_worktree.cmd_merge, self.root, "br-1")

        self.assertEqual(rc, 1)
        self.assertEqual(result["status"], "failed")
        self.assertIn("aborted", result["error"])
        self.assertEqual(
            self.git("status", "--porcelain", cwd=self.root).stdout.strip(), ""
        )
        self.assertFalse((self.root / ".git" / "MERGE_HEAD").exists())

    def test_cleanup_removes_worktree_and_branch(self):
        _, created = self.invoke(beo_worktree.cmd_create, self.root, "br-1", "alice")
        worktree = Path(created["worktree_path"])

        rc, result = self.invoke(beo_worktree.cmd_cleanup, self.root, "br-1", "done")

        self.assertEqual(rc, 0)
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["branch"], created["branch"])
        self.assertFalse(worktree.exists())
        branch_check = subprocess.run(
            ["git", "rev-parse", "--verify", "--quiet", created["branch"]],
            cwd=self.root,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(branch_check.returncode, 0)
        worktree_list = self.git(
            "worktree", "list", "--porcelain", cwd=self.root
        ).stdout
        self.assertNotIn(str(worktree.resolve()), worktree_list)

    def test_cleanup_unlinks_symlinked_path_without_touching_target(self):
        target = Path(self.tmpdir.name) / "target"
        target.mkdir()
        (target / "keep.txt").write_text("keep\n", encoding="utf-8")
        link = beo_worktree.worktree_path("br-1")
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(target, target_is_directory=True)

        rc, result = self.invoke(
            beo_worktree.cmd_cleanup, self.root, "br-1", "stale-link"
        )

        self.assertEqual(rc, 0, result)
        self.assertEqual(result["status"], "success")
        self.assertNotIn("branch", result)
        self.assertNotIn("errors", result)
        self.assertFalse(link.is_symlink())
        self.assertFalse(link.exists())
        self.assertTrue(target.is_dir())
        self.assertTrue((target / "keep.txt").is_file())

    def test_cleanup_nothing_to_clean_echoes_reason(self):
        rc, result = self.invoke(
            beo_worktree.cmd_cleanup, self.root, "br-1", "aborted by reviewer"
        )

        self.assertEqual(rc, 0)
        self.assertEqual(result["status"], "success")
        self.assertNotIn("branch", result)
        self.assertEqual(result["reason"], "aborted by reviewer")

    def test_ensure_beads_symlink_rejects_regular_file(self):
        (self.root / ".beads").write_text("not a directory\n", encoding="utf-8")

        with self.assertRaisesRegex(RuntimeError, "not a directory"):
            beo_worktree.ensure_beads_symlink(
                self.root, Path(self.tmpdir.name) / "worktree"
            )

    def test_ensure_beads_symlink_rejects_real_directory(self):
        (self.root / ".beads").mkdir()
        worktree = Path(self.tmpdir.name) / "worktree"
        worktree.mkdir()
        (worktree / ".beads").mkdir()

        with self.assertRaisesRegex(RuntimeError, "real directory"):
            beo_worktree.ensure_beads_symlink(self.root, worktree)

    def test_ensure_beads_symlink_keeps_correct_existing_symlink(self):
        main_beads = self.root / ".beads"
        main_beads.mkdir()
        worktree = Path(self.tmpdir.name) / "worktree"
        worktree.mkdir()
        worktree_beads = worktree / ".beads"
        worktree_beads.symlink_to(main_beads, target_is_directory=True)

        beo_worktree.ensure_beads_symlink(self.root, worktree)

        self.assertTrue(worktree_beads.is_symlink())
        self.assertEqual(worktree_beads.resolve(), main_beads.resolve())

    def test_find_existing_worktree_matches_only_registered_path_and_branch(self):
        matching = str(beo_worktree.worktree_path("br-1").resolve())
        porcelain = "\n".join(
            [
                "worktree /tmp/unrelated",
                "HEAD 1111111111111111111111111111111111111111",
                "branch refs/heads/other",
                "",
                "worktree /tmp/detached",
                "HEAD 2222222222222222222222222222222222222222",
                "detached",
                "",
                f"worktree {matching}",
                "HEAD 3333333333333333333333333333333333333333",
                "branch refs/heads/beo/br-1/alice/x",
            ]
        )
        with mock.patch.object(
            beo_worktree,
            "run_git",
            return_value=types.SimpleNamespace(stdout=porcelain),
        ):
            self.assertEqual(
                beo_worktree.find_existing_worktree(self.root, "br-1"),
                "beo/br-1/alice/x",
            )

        matching_detached = "\n".join(
            [
                f"worktree {matching}",
                "HEAD 3333333333333333333333333333333333333333",
                "detached",
            ]
        )
        with mock.patch.object(
            beo_worktree,
            "run_git",
            return_value=types.SimpleNamespace(stdout=matching_detached),
        ):
            self.assertIsNone(
                beo_worktree.find_existing_worktree(self.root, "br-1")
            )

        with mock.patch.object(
            beo_worktree,
            "run_git",
            return_value=types.SimpleNamespace(stdout="worktree /tmp/other\nHEAD dead\n"),
        ):
            self.assertIsNone(
                beo_worktree.find_existing_worktree(self.root, "br-1")
            )

    def test_main_dispatches_commands_and_handles_failures(self):
        rc, result = self.invoke(
            beo_worktree.main,
            ["--root", str(self.root), "status", "--issue", "br-1"],
        )
        self.assertEqual(rc, 0)
        self.assertEqual(result["status"], "not_found")

        rc, result = self.invoke(
            beo_worktree.main,
            ["--root", str(self.root), "create", "--issue", "br-1", "--actor", "alice"],
        )
        self.assertEqual(rc, 0)
        self.assertEqual(result["status"], "success")

        rc, result = self.invoke(
            beo_worktree.main,
            ["--root", str(self.root), "status", "--issue", "../evil"],
        )
        self.assertEqual(rc, 1)
        self.assertEqual(result["status"], "failed")

        (self.root / "dirty.txt").write_text("dirty\n", encoding="utf-8")
        result = self.run_exit(
            beo_worktree.main,
            ["--root", str(self.root), "create", "--issue", "br-2", "--actor", "alice"],
        )
        self.assertEqual(result["status"], "failed")

    def test_subprocess_status_uses_environment_worktree_base(self):
        env = os.environ.copy()
        env["BEO_WORKTREE_BASE"] = str(self.base)
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPTS / "beo_worktree.py"),
                "--root",
                str(self.root),
                "status",
                "--issue",
                "br-1",
            ],
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(json.loads(completed.stdout)["status"], "not_found")


if __name__ == "__main__":
    unittest.main()
