#!/usr/bin/env python3
"""Unit tests for beo_worktree.py — pure-function paths only.

Tests cover the path-safety and branch-name sanitization logic that
runs before any git invocation. The git-orchestrating functions
(cmd_create, cmd_merge, cmd_cleanup, cmd_status) require a real
git repo and are out of scope for unit tests; they are exercised
end-to-end by beo-validate in strict mode.
"""
from __future__ import annotations

import importlib
import os
import re
import sys
import unittest
from unittest import mock
from pathlib import Path

REFERENCE_ROOT = Path(__file__).resolve().parents[1] / "skills" / "beo" / "beo-reference"
SCRIPTS = REFERENCE_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


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
        with mock.patch.dict(os.environ, {"BEO_WORKTREE_BASE": "/var/tmp/custom"}):
            importlib.reload(beo_worktree)
            base = beo_worktree.WORKTREE_BASE
            self.assertEqual(base, Path("/var/tmp/custom"))


if __name__ == "__main__":
    unittest.main()
