#!/usr/bin/env python3
from __future__ import annotations

import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

import support

TEMPLATE = support.ROOT / "skills" / "human-step-wizard" / "scripts" / "wizard-template.sh"


def setUpModule() -> None:
    support.never_run("bash")


def library() -> str:
    text = TEMPLATE.read_text()
    marker = text.index("# STAGES:")
    return text[:marker]


class WizardTemplateTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.dir = Path(self._tmp.name)
        self.lib = self.dir / "lib.sh"
        self.lib.write_text(library())

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def run_bash(self, body: str, stdin: str = "", path: str = "/usr/bin:/bin") -> subprocess.CompletedProcess[str]:
        script = f"source {self.lib}\n{body}\n"
        return subprocess.run(
            [shutil.which("bash", path="/usr/bin:/bin") or "bash", "-c", script], cwd=self.dir, input=stdin, capture_output=True, text=True, env={"PATH": path, "ENV_FILE": ".env"}
        )

    def test_library_parses(self) -> None:
        self.assertEqual(subprocess.run(["bash", "-n", str(TEMPLATE)], capture_output=True, stdin=subprocess.DEVNULL).returncode, 0)

    def test_write_env_upserts_without_duplicating(self) -> None:
        result = self.run_bash('write_env API_KEY first\nwrite_env OTHER x\nwrite_env API_KEY second')
        self.assertEqual(result.returncode, 0, result.stderr)
        lines = (self.dir / ".env").read_text().splitlines()
        self.assertEqual(lines.count('API_KEY="second"'), 1)
        self.assertNotIn('API_KEY="first"', lines)
        self.assertIn('OTHER="x"', lines)

    def test_write_env_values_round_trip_through_source_and_ask(self) -> None:
        value = 'a b "c" $d `e` \\f #g'
        result = self.run_bash(
            'write_env K "$1"\n( source "$ENV_FILE"; printf "|%s|" "$K" )\nask K "Paste:"\nprintf "|%s|" "$K"'.replace('"$1"', "'" + value + "'"),
            stdin="\n",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.count(f"|{value}|"), 2, result.stdout)

    def test_ask_strips_one_layer_of_quotes_from_saved_values(self) -> None:
        (self.dir / ".env").write_text("A=\"abc\"\nB='def'\n")
        result = self.run_bash('ask A "a:"\nask B "b:"\nprintf "|%s|%s|" "$A" "$B"', stdin="\n\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("|abc|def|", result.stdout)

    def test_write_env_read_error_keeps_the_file_and_fails(self) -> None:
        if os.geteuid() == 0:
            self.skipTest("root reads any file")
        env = self.dir / ".env"
        env.write_text("A=1\nB=2\n")
        env.chmod(0)
        try:
            result = self.run_bash("write_env C 3")
        finally:
            env.chmod(0o600)
        self.assertNotEqual(result.returncode, 0)
        self.assertEqual(env.read_text(), "A=1\nB=2\n")
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), [".env", "lib.sh"])

    def test_write_env_keeps_the_callers_exit_trap(self) -> None:
        mv_fails = self.fake_bin("mv", "exit 1\n")
        for name, path in (("returns normally", "/usr/bin:/bin"), ("exits mid-write", f"{mv_fails}:/usr/bin:/bin")):
            with self.subTest(name):
                result = self.run_bash("trap 'echo caller-exit' EXIT\nwrite_env K v", path=path)
                self.assertEqual(result.stdout.count("caller-exit"), 1, result.stdout)
                self.assertEqual(list(self.dir.glob(".env.*")), [])

    def test_write_env_stages_its_temp_file_beside_the_env_file(self) -> None:
        bin_dir = self.fake_bin("mktemp", 'echo "$*" > "$PWD/mktemp.args"\nexec /usr/bin/mktemp "$@"\n')
        result = self.run_bash("write_env K v", path=f"{bin_dir}:/usr/bin:/bin")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertTrue((self.dir / "mktemp.args").read_text().startswith(".env."))
        self.assertEqual(sorted(p.name for p in self.dir.iterdir()), [".env", "fake-bin", "lib.sh", "mktemp.args"])

    def test_ask_keeps_existing_value_on_empty_input(self) -> None:
        (self.dir / ".env").write_text("TOKEN=kept\n")
        result = self.run_bash('ask TOKEN "Paste:"\nprintf "%s" "$TOKEN"', stdin="\n")
        self.assertEqual(result.stdout.strip().rsplit(" ", 1)[-1], "kept")

    def test_ask_typed_input_overrides_saved_value(self) -> None:
        (self.dir / ".env").write_text("TOKEN=old\n")
        result = self.run_bash('ask TOKEN "Paste:"\nprintf "|%s|" "$TOKEN"', stdin="fresh\n")
        self.assertIn("|fresh|", result.stdout)
        self.assertNotIn("|old|", result.stdout)

    def test_ask_refuses_empty_required_input_and_reasks(self) -> None:
        result = self.run_bash('ask TOKEN "Paste:"\nprintf "|%s|" "$TOKEN"', stdin="\nfresh\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("|fresh|", result.stdout)

    def test_ask_eof_without_value_names_key_and_fails(self) -> None:
        result = self.run_bash('ask TOKEN "Paste:"', stdin="")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("TOKEN", result.stderr)

    def test_set_secret_records_skip_when_gh_is_absent(self) -> None:
        result = self.run_bash('set_secret NAME value\nprintf "%s" "${SKIPPED[0]}"')
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("GitHub secret NAME", result.stdout)
        self.assertNotIn("value", result.stdout.split("GitHub secret NAME")[-1])

    def fake_bin(self, name: str, script: str) -> str:
        bin_dir = self.dir / "fake-bin"
        bin_dir.mkdir(exist_ok=True)
        tool = bin_dir / name
        tool.write_text("#!/bin/sh\n" + script)
        tool.chmod(0o755)
        return str(bin_dir)

    def test_set_secret_skip_carries_the_gh_error(self) -> None:
        bin_dir = self.fake_bin("gh", 'if [ "$1" = auth ]; then exit 0; fi\ncat >/dev/null\necho "HTTP 403: no permission" >&2\nexit 1\n')
        result = self.run_bash('set_secret NAME value\nprintf "%s" "${SKIPPED[0]}"', path=f"{bin_dir}:/usr/bin:/bin")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("HTTP 403", result.stdout)
        self.assertNotIn("gh not ready", result.stdout)

    def test_open_url_trusts_explorer_exe_despite_its_exit_code(self) -> None:
        bin_dir = self.fake_bin("explorer.exe", "exit 1\n")
        result = self.run_bash('open_url "https://example.test/keys"', path=bin_dir)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn("visit it manually", result.stdout)

    def test_open_url_warns_when_no_opener_exists(self) -> None:
        empty_bin = self.dir / "no-opener"
        empty_bin.mkdir()
        result = self.run_bash('open_url "https://example.test/keys"', path=str(empty_bin))
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("visit it manually: https://example.test/keys", result.stdout)

    def test_banner_counts_the_stage_lines_of_its_script(self) -> None:
        script = self.dir / "wizard.sh"
        script.write_text(library() + 'banner "Demo"\nstage "One"\nstage "Two"\n')
        result = subprocess.run(
            [shutil.which("bash", path="/usr/bin:/bin") or "bash", str(script)], cwd=self.dir, input="\n", capture_output=True, text=True, env={"PATH": "/usr/bin:/bin"}
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("2 stages", result.stdout)
        self.assertIn("Stage 2/2", result.stdout)


if __name__ == "__main__":
    unittest.main()
