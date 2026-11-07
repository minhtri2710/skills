#!/usr/bin/env python3
"""Unit tests for tracked skill deployment acceptance."""
from __future__ import annotations

import io
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import support
import deploy_skill
import gate_row

SCRIPTS = support.ADW / "scripts"


def setUpModule() -> None:
    support.never_run("git", "skills", sys.executable)


FAKE_SKILLS = f'''#!{sys.executable}
import json
import os
import shutil
import sys
from pathlib import Path

record = {{
    "argv": sys.argv[1:],
    "do_not_track": os.environ.get("DO_NOT_TRACK"),
    "source": sys.argv[2],
    "stdin_isatty": sys.stdin.isatty(),
}}
log_path = Path(os.environ["SKILLS_LOG"])
records = json.loads(log_path.read_text(encoding="utf-8")) if log_path.exists() else []
records.append(record)
log_path.write_text(json.dumps(records), encoding="utf-8")
if int(os.environ.get("SKILLS_EXIT", "0")):
    raise SystemExit(int(os.environ["SKILLS_EXIT"]))
source = Path(sys.argv[2])
target = Path.home() / ".agents" / "skills" / source.name
if target.exists():
    shutil.rmtree(target)
shutil.copytree(source, target)
if os.environ.get("SKILLS_TAMPER"):
    (target / "SKILL.md").write_text("tampered\\n", encoding="utf-8")
'''


class DeploySkillTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=os.path.realpath("/tmp"))
        self.tmp = Path(self._tmp.name)
        self.repo = support.temp_git_repo(self.tmp / "repo")
        self.skills = self.repo / "skills"
        self.source = self.skills / "agent-delivery-workflow"
        self.source.mkdir(parents=True)
        (self.source / "SKILL.md").write_text(
            "---\nname: agent-delivery-workflow\ndescription: test skill\n---\ntracked skill\n",
            encoding="utf-8",
        )
        support.git(self.repo, "add", "skills")
        support.git(self.repo, "commit", "-qm", "skill")
        self.origin(self.head())
        self.home = self.tmp / "home"
        self.home.mkdir()
        self.bin = self.tmp / "bin"
        self.bin.mkdir()
        self.fake_cli = self.bin / "skills"
        self.fake_cli.write_text(FAKE_SKILLS, encoding="utf-8")
        self.fake_cli.chmod(0o755)
        self.cli_log = self.tmp / "skills-call.json"
        self._stdout_patch = patch.object(sys, "stdout", io.StringIO())
        self._stderr_patch = patch.object(sys, "stderr", io.StringIO())
        self._stdout_patch.start()
        self._stderr_patch.start()
        self.addCleanup(self._stderr_patch.stop)
        self.addCleanup(self._stdout_patch.stop)
        self.addCleanup(self._tmp.cleanup)

    def head(self) -> str:
        return support.git(self.repo, "rev-parse", "HEAD")

    def origin(self, head: str | None) -> None:
        if head is None:
            support.git(self.repo, "update-ref", "-d", "refs/remotes/origin/main")
        else:
            support.git(self.repo, "update-ref", "refs/remotes/origin/main", head)

    def deploy_args(self, ledger: Path, head: str = "HEAD") -> list[str]:
        return [
            "--repo", str(self.repo), "--head", head,
            "--ledger", str(ledger),
            "--status", "resolved:deploy",
            "--words", "seat", "--note", "installed the skill", "--quote", "done",
        ]

    def run_deploy(self, args: list[str], **extra_env: str) -> int:
        environment = {
            "HOME": str(self.home),
            "PATH": f"{self.bin}{os.pathsep}{os.environ['PATH']}",
            "SKILLS_LOG": str(self.cli_log),
            **extra_env,
        }
        with patch.dict(os.environ, environment):
            return deploy_skill.main(args)

    def assert_install_matches_head(self, skill: str, head: str) -> None:
        root = self.home / ".agents" / "skills" / skill
        prefix = f"skills/{skill}/"
        entries = deploy_skill.tracked_files(self.repo, head, prefix)
        self.assertEqual(
            {path.relative_to(root).as_posix() for path in root.rglob("*") if path.is_file()},
            {path[len(prefix):] for path, _mode, _object_id in entries},
        )
        for path, mode, object_id in entries:
            installed = root / path[len(prefix):]
            self.assertEqual(support.git(self.repo, "hash-object", str(installed)), object_id)
            self.assertEqual(object_id, support.git(self.repo, "rev-parse", f"{head}:{path}"))
            self.assertEqual(stat.S_IMODE(installed.stat().st_mode), mode)

    def test_local_staged_cli_gets_fixed_argv_and_head_contents(self):
        (self.source / "runtime.py").write_text("tracked runtime\n", encoding="utf-8")
        support.git(self.repo, "add", "skills")
        support.git(self.repo, "commit", "-qm", "runtime file")
        head = self.head()
        self.origin(head)
        ledger = self.tmp / "gates.md"

        result = self.run_deploy(self.deploy_args(ledger))

        self.assertEqual(result, 0)
        self.assert_install_matches_head("agent-delivery-workflow", head)
        calls = json.loads(self.cli_log.read_text(encoding="utf-8"))
        self.assertEqual(len(calls), 1)
        call = calls[0]
        self.assertEqual(call["argv"], [
            "add", call["source"], "-g", "-a", "cline", "-s",
            "agent-delivery-workflow", "-y", "--copy",
        ])
        self.assertEqual(call["do_not_track"], "1")
        self.assertFalse(call["stdin_isatty"])
        self.assertIn("deploy-skill-", call["source"])
        self.assertFalse(Path(call["source"]).exists())
        self.assertTrue((self.home / ".agents" / "skills" / "agent-delivery-workflow").is_dir())
        rows = gate_row.ledger_rows(ledger.read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 1)
        self.assertIn("skills=agent-delivery-workflow", rows[0])

    def human_deploy_args(self, ledger: Path, *extra: str) -> list[str]:
        return [
            "--repo", str(self.repo), "--ledger", str(ledger), "--status", "resolved:human",
            "--words", "human", "--note", "installed the skill", *extra,
        ]

    def test_human_words_deploy_passes_the_brief_and_stores_no_quote(self):
        self.origin(self.head())
        ledger = self.tmp / "gates.md"
        brief = "Deploy the merged head. In scope: this skill only."

        self.assertEqual(self.run_deploy(self.human_deploy_args(ledger, "--brief", brief)), 0)

        row = gate_row.ledger_rows(ledger.read_text(encoding="utf-8"))[0]
        self.assertIn(f" | words=human | brief={brief} | note=installed the skill | ", row)
        self.assertTrue(row.endswith(' | quote=""'))

    def test_human_words_deploy_without_a_brief_or_with_a_quote_appends_no_row(self):
        self.origin(self.head())
        ledger = self.tmp / "gates.md"
        for extra, message in (
            ((), "brief= is required"),
            (("--brief", "Deploy the merged head.", "--quote", "said"), "stores no Human text"),
        ):
            with self.subTest(extra=extra):
                self.assertEqual(self.run_deploy(self.human_deploy_args(ledger, *extra)), 1)
                self.assertIn(message, sys.stderr.getvalue())
                self.assertFalse(ledger.exists())
                self.assertFalse(self.cli_log.exists(), "refused row must not invoke skills")
                self.assertFalse((self.home / ".agents").exists())

    def test_dirty_worktree_installs_head_blob_and_mode(self):
        (self.source / "run.sh").write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
        (self.source / "run.sh").chmod(0o755)
        support.git(self.repo, "add", "skills")
        support.git(self.repo, "commit", "-qm", "executable script")
        head = self.head()
        self.origin(head)
        (self.source / "SKILL.md").write_text("dirty working tree\n", encoding="utf-8")

        result = self.run_deploy(self.deploy_args(self.tmp / "gates.md"))

        self.assertEqual(result, 0)
        installed = self.home / ".agents" / "skills" / "agent-delivery-workflow"
        self.assertTrue((installed / "SKILL.md").read_text(encoding="utf-8").endswith("tracked skill\n"))
        self.assertEqual(stat.S_IMODE((installed / "run.sh").stat().st_mode), 0o755)
        self.assert_install_matches_head("agent-delivery-workflow", head)

    def test_unsupported_git_mode_is_refused_before_any_cli_write(self):
        second = self.skills / "second-skill"
        second.mkdir()
        (second / "SKILL.md").symlink_to(self.source / "SKILL.md")
        support.git(self.repo, "add", "skills")
        support.git(self.repo, "commit", "-qm", "add symlink")
        head = self.head()
        self.origin(head)

        result = self.run_deploy(
            self.deploy_args(self.tmp / "gates.md") + ["--skill", "second-skill"]
        )

        self.assertEqual(result, 1)
        self.assertFalse(self.cli_log.exists())
        self.assertFalse((self.home / ".agents").exists())
        self.assertFalse((self.tmp / "gates.md").exists())

    def test_verify_rejects_tampering_and_appends_no_row(self):
        ledger = self.tmp / "gates.md"

        result = self.run_deploy(self.deploy_args(ledger), SKILLS_TAMPER="1")

        self.assertEqual(result, 1)
        self.assertIn("installed hash mismatch", sys.stderr.getvalue())
        self.assertFalse(ledger.exists())

    def test_append_refused_after_install_says_installed_and_no_row(self):
        ledger = self.tmp / "gates.md"
        for error in (gate_row.RowError("ledger moved"), OSError("ledger moved")):
            with self.subTest(error=type(error).__name__):
                sys.stderr.truncate(0)
                sys.stderr.seek(0)
                with patch.object(gate_row, "append_row", side_effect=error):
                    result = self.run_deploy(self.deploy_args(ledger))

                self.assertEqual(result, 1)
                message = sys.stderr.getvalue()
                for token in ("installed agent-delivery-workflow", "no deploy row was recorded", "ledger moved"):
                    self.assertIn(token, message)
                self.assertTrue((self.home / ".agents" / "skills" / "agent-delivery-workflow").is_dir())
                self.assertFalse(ledger.exists())

    def test_cli_absent_refuses_before_staging_or_writing(self):
        ledger = self.tmp / "gates.md"
        with patch.object(deploy_skill.shutil, "which", return_value=None), patch.object(
            deploy_skill.tempfile, "TemporaryDirectory", side_effect=AssertionError("staging started")
        ):
            result = deploy_skill.main(self.deploy_args(ledger))

        self.assertEqual(result, 1)
        self.assertIn("skills CLI was not found", sys.stderr.getvalue())
        self.assertFalse(ledger.exists())
        self.assertFalse((self.home / ".agents").exists())

    def test_relative_ledger_is_refused_before_staging_or_installing(self):
        with patch.object(
            deploy_skill.tempfile, "TemporaryDirectory", side_effect=AssertionError("staging started")
        ):
            result = self.run_deploy(self.deploy_args(Path("gates.md")))

        self.assertEqual(result, 1)
        self.assertIn("not absolute", sys.stderr.getvalue())
        self.assertFalse((self.home / ".agents").exists())

    def test_nonzero_cli_exit_refuses_without_row_and_cleans_staging(self):
        ledger = self.tmp / "gates.md"

        result = self.run_deploy(self.deploy_args(ledger), SKILLS_EXIT="7")

        self.assertEqual(result, 1)
        self.assertIn("skills add failed", sys.stderr.getvalue())
        calls = json.loads(self.cli_log.read_text(encoding="utf-8"))
        self.assertEqual(len(calls), 1)
        self.assertFalse(Path(calls[0]["source"]).exists())
        self.assertFalse(ledger.exists())
        self.assertFalse((self.home / ".agents").exists())

    def test_selection_is_validated_and_limits_installs(self):
        second = self.skills / "second-skill"
        second.mkdir()
        (second / "SKILL.md").write_text(
            "---\nname: second-skill\ndescription: second test skill\n---\nsecond\n",
            encoding="utf-8",
        )
        support.git(self.repo, "add", "skills")
        support.git(self.repo, "commit", "-qm", "add second skill")
        self.origin(self.head())

        result = self.run_deploy(
            self.deploy_args(self.tmp / "gates.md") + ["--skill", "second-skill"]
        )

        self.assertEqual(result, 0)
        root = self.home / ".agents" / "skills"
        self.assertTrue((root / "second-skill" / "SKILL.md").is_file())
        self.assertFalse((root / "agent-delivery-workflow").exists())
        with self.assertRaises(deploy_skill.DeployError):
            deploy_skill.selected_skills(self.repo, self.head(), ["../outside"])

    def test_default_selection_installs_all_tracked_skills(self):
        second = self.skills / "second-skill"
        second.mkdir()
        (second / "SKILL.md").write_text(
            "---\nname: second-skill\ndescription: second test skill\n---\nsecond\n",
            encoding="utf-8",
        )
        support.git(self.repo, "add", "skills")
        support.git(self.repo, "commit", "-qm", "add second skill")
        self.origin(self.head())
        ledger = self.tmp / "gates.md"

        result = self.run_deploy(self.deploy_args(ledger))

        self.assertEqual(result, 0)
        self.assertEqual(
            {path.name for path in (self.home / ".agents" / "skills").iterdir()},
            {"agent-delivery-workflow", "second-skill"},
        )
        calls = json.loads(self.cli_log.read_text(encoding="utf-8"))
        self.assertEqual(len(calls), 2)
        self.assertEqual({Path(call["source"]).name for call in calls}, {
            "agent-delivery-workflow", "second-skill",
        })
        self.assertTrue(all(call["do_not_track"] == "1" for call in calls))
        for call in calls:
            self.assertEqual(call["argv"][call["argv"].index("-s") + 1], Path(call["source"]).name)
        self.assertEqual(len(gate_row.ledger_rows(ledger.read_text(encoding="utf-8"))), 1)

    def test_verify_rejects_extra_files_and_ignores_pycache(self):
        head = self.head()
        prefix = "skills/agent-delivery-workflow/"
        entries = deploy_skill.tracked_files(self.repo, head, prefix)
        install = self.tmp / "install"
        install.mkdir()
        (install / "SKILL.md").write_bytes((self.source / "SKILL.md").read_bytes())
        cache = install / "__pycache__"
        cache.mkdir()
        (cache / "artifact.pyc").write_bytes(b"runtime artifact")

        deploy_skill.verify_install(self.repo, install, entries, prefix)
        (install / "extra.txt").write_text("not tracked\n", encoding="utf-8")
        with self.assertRaises(deploy_skill.DeployError):
            deploy_skill.verify_install(self.repo, install, entries, prefix)

    def test_verify_rejects_a_symlinked_subdirectory(self):
        prefix = "skills/agent-delivery-workflow/"
        entries = deploy_skill.tracked_files(self.repo, self.head(), prefix)
        install = self.tmp / "install"
        install.mkdir()
        (install / "SKILL.md").write_bytes((self.source / "SKILL.md").read_bytes())
        deploy_skill.verify_install(self.repo, install, entries, prefix)
        outside = self.tmp / "outside"
        outside.mkdir()
        (install / "linked").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(deploy_skill.DeployError, "not tracked"):
            deploy_skill.verify_install(self.repo, install, entries, prefix)

    def test_head_equal_to_or_ancestor_of_origin_main_is_admitted(self):
        ancestor = self.head()
        ancestor_content = (self.source / "SKILL.md").read_bytes()
        (self.source / "SKILL.md").write_text(
            "---\nname: agent-delivery-workflow\ndescription: test skill\n---\nnew tracked skill\n",
            encoding="utf-8",
        )
        support.git(self.repo, "add", "skills")
        support.git(self.repo, "commit", "-qm", "new skill content")
        descendant = self.head()
        self.origin(descendant)

        installed = self.home / ".agents/skills/agent-delivery-workflow/SKILL.md"
        below = self.run_deploy(self.deploy_args(self.tmp / "below-gates.md", ancestor))
        self.assertEqual(below, 0)
        self.assertEqual(installed.read_bytes(), ancestor_content)
        equal = self.run_deploy(self.deploy_args(self.tmp / "equal-gates.md", descendant))
        self.assertEqual(equal, 0)
        self.assertIn("new tracked skill", installed.read_text())

    def test_head_outside_origin_main_and_missing_origin_ref_are_refused(self):
        accepted = self.head()
        support.git(self.repo, "checkout", "-qb", "offline", accepted)
        (self.source / "SKILL.md").write_text(
            "---\nname: agent-delivery-workflow\ndescription: test skill\n---\noffline content\n",
            encoding="utf-8",
        )
        support.git(self.repo, "add", "skills")
        support.git(self.repo, "commit", "-qm", "offline head")
        offline = self.head()
        support.git(self.repo, "checkout", "-q", "main")
        ledger = self.tmp / "gates.md"

        refused = self.run_deploy(self.deploy_args(ledger, offline))
        self.assertEqual(refused, 1)
        self.assertFalse(self.cli_log.exists(), "refused head must not invoke skills")
        self.assertFalse((self.home / ".agents" / "skills").exists())
        self.assertFalse(ledger.exists())
        self.assertIn("not contained in refs/remotes/origin/main", sys.stderr.getvalue())

        self.origin(None)
        missing = self.run_deploy(self.deploy_args(ledger, accepted))
        self.assertEqual(missing, 1)
        self.assertIn("required admission ref refs/remotes/origin/main is missing", sys.stderr.getvalue())
        self.assertFalse(self.cli_log.exists(), "missing origin ref must not invoke skills")
        self.assertFalse((self.home / ".agents" / "skills").exists())
        self.assertFalse(ledger.exists())

    def test_deploy_resolves_open_gate_in_same_invocation(self):
        gate_row_script = SCRIPTS / "gate_row.py"
        append = [
            sys.executable, str(gate_row_script),
            "--repo", str(self.repo), "--ledger", str(self.tmp / "gates.md"),
        ]
        open_gate = subprocess.run(
            append + [
                "--kind", "deploy-gate", "--status", "open",
                "--words", "none", "--note", "deploy permission pending", "--quote", "",
            ],
            check=False,
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
        )
        self.assertEqual(open_gate.returncode, 0, open_gate.stderr)
        self.assertIn("G1", open_gate.stdout)

        result = self.run_deploy(
            self.deploy_args(self.tmp / "gates.md") + ["--resolves", "G1"]
        )

        self.assertEqual(result, 0)
        rows = gate_row.ledger_rows((self.tmp / "gates.md").read_text(encoding="utf-8"))
        self.assertEqual(len(rows), 2)
        self.assertIn("resolves=G1", rows[-1])
        open_gates = subprocess.run(
            append + ["--open-gates"],
            check=False,
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
        )
        self.assertEqual(open_gates.returncode, 0, open_gates.stderr)
        self.assertEqual(open_gates.stdout, "")


if __name__ == "__main__":
    unittest.main()
