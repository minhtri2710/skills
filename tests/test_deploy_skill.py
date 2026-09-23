#!/usr/bin/env python3
"""Unit tests for tracked skill deployment acceptance."""
from __future__ import annotations

import io
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import deploy_skill  # noqa: E402
import gate_row  # noqa: E402


class DeploySkillTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir="/private/tmp")
        self.tmp = Path(self._tmp.name)
        self.repo = self.tmp / "repo"
        self.repo.mkdir()
        self.git("init", "-q", "-b", "main")
        self.git("config", "user.email", "t@example.invalid")
        self.git("config", "user.name", "t")
        self.skills = self.repo / "skills"
        self.source = self.skills / "herdr-delivery-workflow"
        self.source.mkdir(parents=True)
        (self.source / "SKILL.md").write_text("tracked skill\n")
        self.git("add", "skills")
        self.git("commit", "-qm", "skill")
        self.install = self.tmp / "installed"
        self._stdout_patch = patch.object(sys, "stdout", io.StringIO())
        self._stderr_patch = patch.object(sys, "stderr", io.StringIO())
        self._stdout_patch.start()
        self._stderr_patch.start()
        self.addCleanup(self._stderr_patch.stop)
        self.addCleanup(self._stdout_patch.stop)
        self.addCleanup(self._tmp.cleanup)

    def git(self, *args: str) -> None:
        subprocess.run(["git", "-C", str(self.repo), *args], check=True,
                       capture_output=True, text=True)

    def deploy_args(self, ledger: Path) -> list[str]:
        return [
            "--repo", str(self.repo),
            "--install-dir", str(self.install),
            "--ledger", str(ledger),
            "--status", "resolved:deploy",
            "--words", "seat", "--note", "installed the skill", "--quote", "done",
        ]

    def snapshot(self) -> dict:
        return {
            path.relative_to(self.tmp): (
                path.is_dir(),
                None if path.is_dir() or path.is_symlink() else path.read_bytes(),
                stat.S_IMODE(path.lstat().st_mode),
            )
            for path in self.tmp.rglob("*")
            if self.repo not in path.parents and path != self.repo
        }

    def two_skill_install(self) -> None:
        (self.source / "policy.md").write_text("policy v1\n")
        second = self.skills / "second-skill"
        second.mkdir()
        (second / "SKILL.md").write_text("second v1\n")
        (second / "run.sh").write_text("#!/bin/sh\n")
        (second / "run.sh").chmod(0o755)
        self.git("add", "skills")
        self.git("commit", "-qm", "v1")
        self.assertEqual(deploy_skill.main(self.deploy_args(self.tmp / "v1-gates.md")), 0)
        cache = self.install / "herdr-delivery-workflow" / "__pycache__"
        cache.mkdir()
        (cache / "x.pyc").write_bytes(b"cache")
        (self.install / "herdr-delivery-workflow" / "policy.md").chmod(0o600)
        (self.source / "SKILL.md").write_text("tracked skill v2\n")
        (self.source / "policy.md").unlink()
        (self.source / "added.md").write_text("added v2\n")
        (second / "SKILL.md").write_text("second v2\n")
        (second / "run.sh").unlink()
        self.git("add", "-A", "skills")
        self.git("commit", "-qm", "v2")

    def failing_on_call(self, target, name: str, failing_call: int):
        original = getattr(target, name)
        calls = []

        def fail(*args, **kwargs):
            calls.append(args)
            if len(calls) == failing_call:
                raise OSError(28, "injected failure")
            return original(*args, **kwargs)

        return patch.object(target, name, fail)

    def assert_failed_deploy_left_install_unchanged(self, target, name: str, failing_call: int):
        self.two_skill_install()
        before = self.snapshot()
        ledger = self.tmp / "gates.md"

        with self.failing_on_call(target, name, failing_call):
            result = deploy_skill.main(self.deploy_args(ledger))

        self.assertEqual(result, 1)
        self.assertFalse(ledger.exists())
        self.assertEqual(self.snapshot(), before)

    def test_staging_failure_in_first_skill_leaves_live_trees_unchanged(self):
        self.assert_failed_deploy_left_install_unchanged(Path, "write_bytes", 2)

    def test_staging_failure_in_second_skill_leaves_first_skill_unchanged(self):
        self.assert_failed_deploy_left_install_unchanged(Path, "write_bytes", 3)

    def test_chmod_failure_leaves_live_trees_unchanged(self):
        self.assert_failed_deploy_left_install_unchanged(deploy_skill.os, "chmod", 1)

    def test_swap_failure_in_second_skill_restores_both_skills(self):
        # Rename calls: live->old and new->live for the first skill, then live->old for the second.
        self.assert_failed_deploy_left_install_unchanged(deploy_skill.os, "rename", 4)

    def test_backup_rename_failure_in_second_skill_restores_first_skill(self):
        self.assert_failed_deploy_left_install_unchanged(deploy_skill.os, "rename", 3)

    def test_rollback_failure_names_the_kept_previous_install(self):
        self.two_skill_install()
        original = os.rename
        calls = []

        def fail(src, dst):
            calls.append(src)
            if len(calls) in {2, 3}:
                raise OSError(5, "injected failure")
            return original(src, dst)

        with patch.object(deploy_skill.os, "rename", fail):
            with self.assertRaises(deploy_skill.DeployError) as raised:
                deploy_skill.install_files(self.install, [("herdr-delivery-workflow", [
                    (Path("SKILL.md"), b"new\n", 0o644)])])

        kept = str(raised.exception).split("kept under ", 1)[1].split(":", 1)[0]
        self.assertEqual(
            (Path(kept) / "old" / "0" / "SKILL.md").read_text(), "tracked skill\n"
        )

    def test_dirty_worktree_installs_head_blob(self):
        (self.source / "SKILL.md").write_text("dirty working tree\n")

        result = deploy_skill.main(self.deploy_args(self.tmp / "gates.md"))

        self.assertEqual(result, 0)
        installed = self.install / "herdr-delivery-workflow" / "SKILL.md"
        self.assertEqual(installed.read_text(), "tracked skill\n")
        head = deploy_skill.git(self.repo, "rev-parse", "HEAD")
        paths = deploy_skill.tracked_files(self.repo, head, "skills/herdr-delivery-workflow")
        deploy_skill.verify_install(
            self.repo, head, installed.parent, paths, "skills/herdr-delivery-workflow"
        )

    def test_executable_mode_comes_from_head_tree(self):
        script = self.source / "run.sh"
        script.write_text("#!/bin/sh\nexit 0\n")
        script.chmod(0o755)
        self.git("add", "skills")
        self.git("commit", "-qm", "add executable")
        script.chmod(0o644)

        result = deploy_skill.main(self.deploy_args(self.tmp / "gates.md"))

        self.assertEqual(result, 0)
        installed = self.install / "herdr-delivery-workflow" / "run.sh"
        self.assertEqual(stat.S_IMODE(installed.stat().st_mode), 0o755)

    def test_resolution_failure_leaves_earlier_install_byte_identical(self):
        initial_ledger = self.tmp / "initial-gates.md"
        self.assertEqual(deploy_skill.main(self.deploy_args(initial_ledger)), 0)
        stale = self.install / "herdr-delivery-workflow" / "obsolete.txt"
        stale.write_text("must remain when resolution fails\n")
        before = {
            path.relative_to(self.install): (path.read_bytes(), stat.S_IMODE(path.stat().st_mode))
            for path in self.install.rglob("*")
            if path.is_file()
        }

        second = self.skills / "second-skill"
        second.mkdir()
        (second / "SKILL.md").symlink_to(self.source / "SKILL.md")
        self.git("add", "skills")
        self.git("commit", "-qm", "add unsupported second skill")

        result = deploy_skill.main(
            self.deploy_args(self.tmp / "gates.md")
            + ["--skill", "herdr-delivery-workflow", "--skill", "second-skill"]
        )

        self.assertEqual(result, 1)
        after = {
            path.relative_to(self.install): (path.read_bytes(), stat.S_IMODE(path.stat().st_mode))
            for path in self.install.rglob("*")
            if path.is_file()
        }
        self.assertEqual(after, before)

    def test_symlink_mode_is_refused_before_install(self):
        second = self.skills / "second-skill"
        second.mkdir()
        (second / "SKILL.md").symlink_to(self.source / "SKILL.md")
        self.git("add", "skills")
        self.git("commit", "-qm", "add symlink")
        head = deploy_skill.git(self.repo, "rev-parse", "HEAD")
        paths = deploy_skill.tracked_files(self.repo, head, "skills/second-skill")

        with self.assertRaises(deploy_skill.DeployError):
            deploy_skill.resolved_files(self.repo, head, paths, "skills/second-skill")
        self.assertFalse(self.install.exists())

    def test_tampered_installed_file_fails_hash_comparison(self):
        self.install.mkdir()
        installed = self.install / "SKILL.md"
        installed.write_text("tampered\n")
        head = deploy_skill.git(self.repo, "rev-parse", "HEAD")
        paths = deploy_skill.tracked_files(self.repo, head, "skills/herdr-delivery-workflow")
        with self.assertRaises(deploy_skill.DeployError):
            deploy_skill.verify_install(
                self.repo, head, self.install, paths, "skills/herdr-delivery-workflow"
            )

    def test_symlinked_install_root_is_supported_by_cli(self):
        real_root = self.tmp / ".agents" / "skills"
        real_root.mkdir(parents=True)
        linked_root = self.tmp / ".claude" / "skills"
        linked_root.parent.mkdir()
        linked_root.symlink_to(real_root, target_is_directory=True)

        args = self.deploy_args(self.tmp / "gates.md")
        args[args.index("--install-dir") + 1] = str(linked_root)
        result = deploy_skill.main(args)

        self.assertEqual(result, 0)
        self.assertTrue((real_root / "herdr-delivery-workflow" / "SKILL.md").is_file())

    def test_cli_default_install_dir_uses_canonical_home(self):
        ledger = self.tmp / "gates.md"
        args = self.deploy_args(ledger)
        install_index = args.index("--install-dir")
        del args[install_index:install_index + 2]

        with patch.object(deploy_skill.Path, "home", return_value=self.tmp):
            result = deploy_skill.main(args)

        self.assertEqual(result, 0)
        self.assertTrue(
            (self.tmp / ".agents" / "skills" / "herdr-delivery-workflow" / "SKILL.md").is_file()
        )
        self.assertFalse(self.install.exists())

    def test_default_deploy_selects_all_tracked_skills(self):
        second = self.skills / "second-skill"
        second.mkdir()
        (second / "SKILL.md").write_text("second skill\n")
        self.git("add", "skills")
        self.git("commit", "-qm", "add second skill")

        ledger = self.tmp / "gates.md"
        result = deploy_skill.main(self.deploy_args(ledger))

        self.assertEqual(result, 0)
        self.assertEqual(
            deploy_skill.tracked_skills(self.repo, deploy_skill.git(self.repo, "rev-parse", "HEAD")),
            ["herdr-delivery-workflow", "second-skill"],
        )
        self.assertEqual(
            {path.name for path in self.install.iterdir()},
            {"herdr-delivery-workflow", "second-skill"},
        )
        self.assertEqual(len(gate_row.ledger_rows(ledger.read_text())), 1)

    def test_explicit_selection_is_validated_and_limited(self):
        second = self.skills / "second-skill"
        second.mkdir()
        (second / "SKILL.md").write_text("second skill\n")
        self.git("add", "skills")
        self.git("commit", "-qm", "add second skill")

        result = deploy_skill.main(self.deploy_args(self.tmp / "gates.md") + ["--skill", "second-skill"])

        self.assertEqual(result, 0)
        self.assertTrue((self.install / "second-skill" / "SKILL.md").is_file())
        self.assertFalse((self.install / "herdr-delivery-workflow").exists())
        with self.assertRaises(deploy_skill.DeployError):
            deploy_skill.selected_skills(self.repo, deploy_skill.git(self.repo, "rev-parse", "HEAD"), ["../outside"])

    def test_repo_only_dirs_excluded_and_pruned(self):
        # Track the plugin manifest and eval suite under the skill prefix.
        (self.source / ".claude-plugin").mkdir()
        (self.source / ".claude-plugin" / "plugin.json").write_text('{"name": "x"}\n')
        (self.source / "plugin-eval" / "id5").mkdir(parents=True)
        (self.source / "plugin-eval" / "id5" / "prompt.md").write_text("case\n")
        self.git("add", "skills")
        self.git("commit", "-qm", "add repo-only dirs")

        # Pre-existing stale install of an excluded file must be pruned.
        installed = self.install / "herdr-delivery-workflow"
        installed.mkdir(parents=True)
        (installed / ".claude-plugin").mkdir()
        (installed / ".claude-plugin" / "plugin.json").write_text('{"name": "stale"}\n')

        result = deploy_skill.main(self.deploy_args(self.tmp / "gates.md"))

        self.assertEqual(result, 0)
        self.assertTrue((installed / "SKILL.md").is_file())
        self.assertFalse((installed / ".claude-plugin" / "plugin.json").exists())
        self.assertFalse((installed / "plugin-eval").exists())

    def test_tampered_selected_tree_appends_no_deploy_row(self):
        ledger = self.tmp / "gates.md"
        original_install = deploy_skill.install_files

        def tamper_second(install_root, skills):
            original_install(install_root, skills)
            (install_root / "second-skill" / "SKILL.md").write_text("tampered\n")

        second = self.skills / "second-skill"
        second.mkdir()
        (second / "SKILL.md").write_text("second skill\n")
        self.git("add", "skills")
        self.git("commit", "-qm", "add second skill")

        old = deploy_skill.install_files
        deploy_skill.install_files = tamper_second
        try:
            result = deploy_skill.main(self.deploy_args(ledger))
        finally:
            deploy_skill.install_files = old

        self.assertEqual(result, 1)
        self.assertFalse(ledger.exists())

    def test_deploy_resolves_open_gate_in_same_invocation(self):
        gate_row_script = SCRIPTS / "gate_row.py"
        append = [
            sys.executable,
            str(gate_row_script),
            "--repo", str(self.repo),
            "--ledger", str(self.tmp / "gates.md"),
        ]
        open_gate = subprocess.run(
            append + [
                "--kind", "deploy-gate", "--status", "open",
                "--words", "none", "--note", "deploy permission pending", "--quote", "",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(open_gate.returncode, 0, open_gate.stderr)
        self.assertIn("G1", open_gate.stdout)

        result = deploy_skill.main(self.deploy_args(self.tmp / "gates.md") + ["--resolves", "G1"])

        self.assertEqual(result, 0)
        rows = gate_row.ledger_rows((self.tmp / "gates.md").read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 2)
        self.assertIn("resolves=G1", rows[-1])
        open_gates = subprocess.run(
            append + ["--open-gates"],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(open_gates.returncode, 0, open_gates.stderr)
        self.assertEqual(open_gates.stdout, "")


if __name__ == "__main__":
    unittest.main()
