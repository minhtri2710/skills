#!/usr/bin/env python3
"""Unit tests for deploy pruning and exact install verification."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import deploy_skill  # noqa: E402


class DeployPruneTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir="/private/tmp")
        self.tmp = Path(self._tmp.name)
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.invalid")
        self.git("config", "user.name", "t")
        self.source = self.repo / "skills" / "herdr-delivery-workflow"
        self.source.mkdir(parents=True)
        (self.source / "SKILL.md").write_text("tracked skill\n")
        (self.source / "policy.md").write_text("tracked policy\n")
        self.git("add", "skills")
        self.git("commit", "-qm", "skill")
        self.install = self.tmp / "installed"
        self.head = deploy_skill.git(self.repo, "rev-parse", "HEAD")
        self.paths = deploy_skill.tracked_files(
            self.repo, self.head, "skills/herdr-delivery-workflow"
        )
        prefix = "skills/herdr-delivery-workflow/"
        self.tracked_relative = {Path(path[len(prefix):]) for path in self.paths}
        self.addCleanup(self._tmp.cleanup)

    def git(self, *args: str) -> None:
        subprocess.run(
            ["git", "-C", str(self.repo), *args],
            check=True,
            capture_output=True,
            text=True,
        )

    def deploy(self) -> None:
        deploy_skill.install_files(
            self.repo,
            self.head,
            self.source,
            self.install,
            self.paths,
            "skills/herdr-delivery-workflow",
        )
        deploy_skill.verify_install(
            self.repo,
            self.head,
            self.install,
            self.paths,
            "skills/herdr-delivery-workflow",
        )

    def test_stale_file_is_pruned(self):
        self.install.mkdir()
        stale = self.install / "obsolete" / "old-policy.md"
        stale.parent.mkdir()
        stale.write_text("deleted from the tracked tree\n")

        self.deploy()

        self.assertFalse(stale.exists())
        self.assertFalse(stale.parent.exists())
        self.assertEqual(
            {path.relative_to(self.install) for path in self.install.rglob("*") if path.is_file()},
            self.tracked_relative,
        )

    def test_symlinked_parent_is_supported(self):
        real_parent = self.tmp / "real"
        real_parent.mkdir()
        linked_parent = self.tmp / "link"
        linked_parent.symlink_to(real_parent, target_is_directory=True)
        install = linked_parent / "skill"

        deploy_skill.install_files(
            self.repo,
            self.head,
            self.source,
            install,
            self.paths,
            "skills/herdr-delivery-workflow",
        )
        deploy_skill.verify_install(
            self.repo,
            self.head,
            install,
            self.paths,
            "skills/herdr-delivery-workflow",
        )

        self.assertEqual(
            {path.relative_to(install) for path in install.rglob("*") if path.is_file()},
            self.tracked_relative,
        )

    def test_in_tree_symlink_is_unlinked_without_touching_target(self):
        outside = self.tmp / "outside"
        outside.mkdir()
        sentinel = outside / "sentinel"
        sentinel.write_text("must survive\n")
        self.install.mkdir()
        escape = self.install / "obsolete"
        escape.symlink_to(outside, target_is_directory=True)

        self.deploy()

        self.assertFalse(escape.exists())
        self.assertEqual(sentinel.read_text(), "must survive\n")

    def test_tracked_named_symlink_is_replaced_without_touching_target(self):
        outside = self.tmp / "outside"
        outside.mkdir()
        sentinel = outside / "sentinel"
        sentinel.write_text("must survive\n")
        self.install.mkdir()
        (self.install / "SKILL.md").symlink_to(sentinel)

        self.deploy()

        self.assertFalse((self.install / "SKILL.md").is_symlink())
        self.assertEqual(sentinel.read_text(), "must survive\n")
        self.assertEqual((self.install / "SKILL.md").read_text(), "tracked skill\n")

    def test_verify_rejects_forced_stale_file(self):
        self.deploy()
        stale = self.install / "old-policy.md"
        stale.write_text("deleted from the tracked tree\n")

        with self.assertRaises(deploy_skill.DeployError):
            deploy_skill.verify_install(
                self.repo,
                self.head,
                self.install,
                self.paths,
                "skills/herdr-delivery-workflow",
            )

    def test_pycache_is_preserved_and_ignored(self):
        self.deploy()
        cache = self.install / "__pycache__"
        cache.mkdir()
        artifact = cache / "deploy.cpython-314.pyc"
        artifact.write_bytes(b"runtime artifact")

        deploy_skill.install_files(
            self.repo,
            self.head,
            self.source,
            self.install,
            self.paths,
            "skills/herdr-delivery-workflow",
        )
        deploy_skill.verify_install(
            self.repo,
            self.head,
            self.install,
            self.paths,
            "skills/herdr-delivery-workflow",
        )

        self.assertEqual(artifact.read_bytes(), b"runtime artifact")

    def test_deploy_is_idempotent(self):
        self.deploy()
        before = {
            path.relative_to(self.install): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in self.install.rglob("*")
            if path.is_file()
        }

        self.deploy()
        after = {
            path.relative_to(self.install): (path.read_bytes(), path.stat().st_mtime_ns)
            for path in self.install.rglob("*")
            if path.is_file()
        }

        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
