#!/usr/bin/env python3
"""Unit tests for tracked skill deployment acceptance."""
from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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

        def tamper_second(repo, head, source_root, install_dir, paths, skill_prefix):
            original_install(repo, head, source_root, install_dir, paths, skill_prefix)
            if skill_prefix == "skills/second-skill":
                (install_dir / "SKILL.md").write_text("tampered\n")

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
