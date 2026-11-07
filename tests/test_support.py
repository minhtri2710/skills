"""The shared test plumbing: script dirs, the never-run guard, isolated temp git repos, run_main."""
from __future__ import annotations

import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import support


class ScriptDirsTest(unittest.TestCase):
    def test_two_scripts_with_one_module_name_refuse_to_load(self) -> None:
        with tempfile.TemporaryDirectory() as tmp, mock.patch.object(sys, "path", list(sys.path)):
            for skill in ("one", "two"):
                scripts = Path(tmp) / "skills" / skill / "scripts"
                scripts.mkdir(parents=True)
                (scripts / "shared.py").write_text("", encoding="utf-8")
            with self.assertRaisesRegex(ImportError, "shared"):
                support.insert_script_dirs(Path(tmp))


class GuardTest(unittest.TestCase):
    def test_run_and_popen_refuse_a_command_that_is_not_listed(self) -> None:
        with support.guarded(sys.executable):
            for call in (subprocess.run, subprocess.Popen):
                with self.subTest(call=call.__name__), self.assertRaisesRegex(AssertionError, "tests run only"):
                    call(["not-allowed"])

    def test_a_listed_command_runs_through_run_and_popen_by_path_or_by_name(self) -> None:
        for listed in (sys.executable, os.path.basename(sys.executable)):
            with self.subTest(listed=listed), support.guarded(listed):
                done = subprocess.run(
                    [sys.executable, "-c", "print(1)"], capture_output=True, text=True, encoding="utf-8"
                )
                with subprocess.Popen([sys.executable, "-c", "pass"]) as proc:
                    proc.wait()
                self.assertEqual((done.stdout, proc.returncode), ("1\n", 0))


class TempGitRepoTest(unittest.TestCase):
    def test_a_commit_ignores_the_users_global_git_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            user_config = Path(tmp) / "gitconfig"
            user_config.write_text(
                "[commit]\n\tgpgsign = true\n[gpg]\n\tprogram = /nonexistent/gpg\n", encoding="utf-8"
            )
            with mock.patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": str(user_config), "HOME": tmp}):
                repo = support.temp_git_repo(Path(tmp) / "repo")
                support.git(repo, "commit", "--allow-empty", "-q", "-m", "one")
            log = support.git(repo, "log", "--format=%an <%ae>")
        self.assertEqual(log, "test <test@example.invalid>")

    def test_git_run_by_a_script_under_the_guard_ignores_the_users_global_git_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            repo = support.temp_git_repo(Path(tmp) / "repo")
            user_config = Path(tmp) / "gitconfig"
            user_config.write_text(
                "[commit]\n\tgpgsign = true\n[gpg]\n\tprogram = /nonexistent/gpg\n", encoding="utf-8"
            )
            with mock.patch.dict(os.environ, {"GIT_CONFIG_GLOBAL": str(user_config), "HOME": tmp}), \
                    support.guarded("git"):
                subprocess.run(
                    ["git", "-C", str(repo), "commit", "--allow-empty", "-q", "-m", "one"],
                    check=True, capture_output=True, stdin=subprocess.DEVNULL,
                )


class RunInLocaleTest(unittest.TestCase):
    REPORT = "import codecs, sys; print(sys.flags.utf8_mode, codecs.lookup(sys.stdout.encoding).name)"

    def test_a_missing_locale_and_the_c_locale_leave_the_child_in_ascii_not_utf8_mode(self) -> None:
        for locale in ("C", "xx_XX.NOPE"):
            with self.subTest(locale=locale):
                proc = support.run_in_locale(locale, self.REPORT)
                self.assertEqual((proc.returncode, proc.stdout), (0, b"0 ascii\n"), proc.stderr)

    def test_the_child_ignores_the_callers_utf8_and_io_encoding_settings(self) -> None:
        with mock.patch.dict(os.environ, {"PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8"}):
            proc = support.run_in_locale("C", self.REPORT)
        self.assertEqual((proc.returncode, proc.stdout), (0, b"0 ascii\n"), proc.stderr)

    def test_the_child_gets_the_code_then_the_arguments_and_its_output_is_bytes(self) -> None:
        proc = support.run_in_locale("C", "import sys; print(sys.argv[1:]); sys.exit(3)", "a", "b")
        self.assertEqual((proc.returncode, proc.stdout), (3, b"['a', 'b']\n"))


class RunMainTest(unittest.TestCase):
    def test_returns_the_code_and_what_main_wrote_and_read(self) -> None:
        def main(argv: list[str]) -> int:
            print(argv, sys.stdin.read())
            print("bad", file=sys.stderr)
            return 3

        self.assertEqual(support.run_main(main, ["a"], stdin="in"), (3, "['a'] in\n", "bad\n"))


if __name__ == "__main__":
    unittest.main()
