#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import io
import json
import os
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock

import support

HOOKS = support.ROOT / "hooks"
GLOB_DELETE = HOOKS / "block-glob-delete.py"
SESSION_TMPDIR = HOOKS / "session-tmpdir.py"
SYSTEM_PYTHON = Path("/usr/bin/python3")
SESSION_ID = "0b6c1f5e-aaaa-bbbb-cccc-123456789abc"

# (command, expected refusal id, or None when the hook allows it)
ROWS = [
    ("rm -r /tmp/tmp*", "glob"),
    ("rm -rf /tmp/*", "glob"),
    ("rm /tmp/x?", "glob"),
    ("rm -r /tmp/[ab]*", "glob"),
    ("rm -r /tmp/{a,b}", "brace"),
    ("rm -r /tmp/{1..3}", "brace"),
    ('rm -r "/tmp/tmp*"', None),
    ("rm -r '/tmp/*'", None),
    ('rm "app/[id]/page.tsx"', None),
    ("rm -r \\*", None),
    ('rm -r "/tmp/"*', "glob"),
    ('rm -r "$S"/*', "glob"),
    ("rm -- /tmp/*", "glob"),
    ("rm *.pyc", "glob"),
    ("rm -r /tmp", "shared-tmp"),
    ("rm -r /tmp/", "shared-tmp"),
    ("rm -r /tmp/.", "shared-tmp"),
    ("rm -r //tmp", "shared-tmp"),
    ("rm -r /tmp/a/..", "shared-tmp"),
    ("rm -r /private/tmp/", "shared-tmp"),
    ("rm -r /var/tmp", "shared-tmp"),
    ("rm -r /", "shared-tmp"),
    ("rm -r /tmp/gdg.Ab12Cd", None),
    ("rm -r /tmp/gdg.Ab12Cd/sub", None),
    ('rm -r "$S"', None),
    ("rm -r $S", "expansion"),
    ("rm -r ${S}", "expansion"),
    ("rm -r $(ls)", "expansion"),
    ("rm -r `ls`", "expansion"),
    ("rm -- -x", None),
    ("rm -f a b", None),
    ("mv /tmp/* x", "glob"),
    ("mv /tmp x", "shared-tmp"),
    ("mv -t dest /tmp", "shared-tmp"),
    ("mv a /tmp/", None),
    ("mv a /tmp/x 2>/dev/null", None),
    ("mv -t /tmp a b", None),
    ("rmdir /tmp/*", "glob"),
    ("find /tmp -name 'x*' -delete", "find"),
    ("find /private/tmp/ -delete", "find"),
    ("find /tmp -name x -exec rm {} +", "find"),
    ("find /tmp/* -delete", "find"),
    ("find -name x -delete", "find"),
    ("find /tmp/gdg.Ab12Cd -name '*.log' -delete", None),
    ("find . -name '*.pyc' -delete", None),
    ("find . -name '*.pyc' -exec rm {} +", None),
    ("find /tmp -name x -print", None),
    ("ls /tmp | xargs rm", "xargs"),
    ("printf '%s\\n' /tmp/a | xargs -0 -n1 rm -f", "xargs"),
    ("ls | xargs sh -c 'rm \"$@\"' _", "xargs"),
    ("ls | xargs echo", None),
    ("git rm '*.txt'", None),
    ("git rm *.txt", None),
    ("cd x && rm a*", "glob"),
    ("true; rm -rf /tmp/*", "glob"),
    ("false || rm /tmp/z*", "glob"),
    ("echo hi | tee f\nrm /tmp/z*", "glob"),
    ("(rm /tmp/*)", "glob"),
    ("{ rm /tmp/*; }", "glob"),
    ("if true; then rm /tmp/*; fi", "glob"),
    ("echo \"$(rm /tmp/*)\"", "glob"),
    ("echo `rm /tmp/*`", "glob"),
    ("bash -c 'rm -r /tmp/*'", "glob"),
    ('sh -lc "rm /tmp/x?"', "glob"),
    ("eval 'rm /tmp/*'", "glob"),
    ("bash -c 'bash -c \"rm /tmp/*\"'", "glob"),
    ("sudo rm /tmp/*", "glob"),
    ("\\rm /tmp/*", "glob"),
    ("/bin/rm /tmp/*", "glob"),
    ("env A=1 rm /tmp/*", "glob"),
    ("env -u A rm /tmp/*", "glob"),
    ("command rm /tmp/*", "glob"),
    ("A=1 rm /tmp/*", "glob"),
    ("cat <<'EOF' > n.md\nrm *\nrm -r /tmp\nEOF", None),
    ("cat <<-EOF\n\trm *\n\tEOF\nls", None),
    ("cat <<EOF\nrm *\nEOF\nrm /tmp/*", "glob"),
    ("bash <<EOF\nrm /tmp/*\nEOF", "glob"),
    ('echo "ps exit $?"', None),
    ('git commit -m "rm /tmp/*"', None),
    ("grep -n 'rm *' f", None),
    ("echo hi # x; rm /tmp/*", None),
    ("ls /tmp", None),
    ("rm \"unterminated", "unparsable"),
    ("echo $(rm /tmp/x", "unparsable"),
    # a heredoc inside $(...) is data to the scan, whatever quotes and parentheses its body holds
    ("git commit -m \"$(cat <<'EOF'\nfix: don't crash on empty input\n\nCo-Authored-By: X <x@y>\nEOF\n)\"", None),
    ("gh pr create --title t --body \"$(cat <<'EOF'\n## Summary\n- it's done (mostly\nEOF\n)\"", None),
    ("git commit -m \"$(cat <<'EOF'\n1) first\n2) second\nEOF\n)\" && rm /tmp/z*", "glob"),
    ("echo $(cat <<'EOF'\nrm -rf /tmp/*\nEOF\n)", None),
    ("echo $((1<<2))", None),
    # shell options that take an argument sit before -c
    ("bash -euo pipefail -c 'rm -rf /tmp/*'", "glob"),
    ("bash -o pipefail -c 'rm -rf /tmp/*'", "glob"),
    ("bash -O extglob -c 'rm -rf /tmp/*'", "glob"),
    ("sh +o errexit -c 'rm -rf /tmp/*'", "glob"),
    ("bash --norc -c 'rm -rf /tmp/*'", "glob"),
    ("bash -euo pipefail -c 'rm -r /tmp/gdg.Ab12Cd'", None),
    ("bash script.sh 'rm -rf /tmp/*'", None),
    # wrappers with their own options and arguments
    ("timeout 5 rm -rf /tmp/*", "glob"),
    ("timeout -s KILL 5 rm -rf /tmp/*", "glob"),
    ("timeout --foreground 60 bash -c 'rm -rf /tmp/tmp*'", "glob"),
    ("time -p rm /tmp/*", "glob"),
    ("stdbuf -o0 rm /tmp/*", "glob"),
    ("ionice -c3 rm /tmp/*", "glob"),
    ("caffeinate -t 5 rm /tmp/*", "glob"),
    ("timeout 5 rm -r /tmp/gdg.Ab12Cd", None),
    # a shell script run by find -exec is judged like one run by xargs
    ("find /tmp -name 'tmp*' -exec sh -c 'rm -r \"$0\"' {} \\;", "find"),
    ("find /tmp -exec bash -c 'rm -rf \"$@\"' _ {} +", "find"),
    ("find /tmp/gdg.Ab12Cd -exec sh -c 'rm \"$0\"' {} \\;", None),
    ("find /tmp/gdg.Ab12Cd -exec sh -c 'rm -r /tmp/*' {} \\;", "glob"),
    ("find /tmp -exec sh -c 'echo \"$0\"' {} \\;", None),
    # text a shell runs: a here-string, and a substitution in an unquoted heredoc body
    ("bash <<< 'rm -rf /tmp/*'", "glob"),
    ("cat <<< 'rm /tmp/*'", None),
    ("cat <<EOF\n$(rm -rf /tmp/*)\nEOF", "glob"),
    ("cat <<EOF\n`rm -rf /tmp/*`\nEOF", "glob"),
    ("cat <<'EOF'\n$(rm -rf /tmp/*)\nEOF", None),
    # `-` or `--` ends the shell's options; the -c text is the word after it
    ("bash -c -- 'rm -rf /tmp/*'", "glob"),
    ("bash -c - 'rm -rf /tmp/*'", "glob"),
    ("bash -ec -- 'rm -rf /tmp/*'", "glob"),
    ("bash -c -- 'echo ok'", None),
    ("bash -- script.sh 'rm -rf /tmp/*'", None),
    # a case pattern's `)` does not end the substitution around it
    ('echo "$(case $v in a) rm -rf /tmp/*;; esac)"', "glob"),
    ('echo "$(case $v in (a|b) true;; c) rm -rf /tmp/*;; esac)"', "glob"),
    ('echo "$(case $v in @(a|b)) rm -rf /tmp/*;; esac)"', "glob"),
    ('echo "$(case $v in a) true;& b) rm -rf /tmp/*;; esac)"', "glob"),
    ('echo "$(case $v in a) case $w in b) true;; esac;; c) rm -rf /tmp/*;; esac)"', "glob"),
    ('echo "$(case $v in a) true;; esac)" && rm /tmp/z*', "glob"),
    ('echo "$(case $v in a) echo hi;; b) ls;; esac)"', None),
    ('echo "$(case $v in a) rm -r /tmp/gdg.Ab12Cd;; esac)"', None),
    ('echo "$(echo case in)"', None),
    # `<<` inside an arithmetic command is a shift, not a heredoc
    ("(( x = 1 << 2 ))\nrm -rf /tmp/*", "glob"),
    ("if (( x << 1 )); then rm /tmp/*; fi", "glob"),
    ("for (( i = 1 << 2; i < 9; i++ ))\ndo rm /tmp/*; done", "glob"),
    ("(( x <<= 2 ))\necho ok", None),
    ("(( x = 1 << 2 ))\ncat <<EOF\nrm /tmp/*\nEOF", None),
    ("(( x = 1 << 2 ))\ncat <<EOF\nrm /tmp/*\nEOF\nrm /tmp/z*", "glob"),
    ("((cat <<EOF\nrm *\nEOF\n))\nrm /tmp/z*", "glob"),
    # xargs options that take a separate argument
    ("ls /tmp | xargs -J % rm %", "xargs"),
    ("ls /tmp | xargs --delimiter '\\n' rm", "xargs"),
    ("ls /tmp | xargs --max-args 1 echo", None),
    # ANSI-C quoting
    ("echo $'it\\'s'", None),
    ("rm $'/tmp/*'", None),
]


def run_hook(command: str, cwd: str | None = None, python: str = sys.executable) -> subprocess.CompletedProcess[str]:
    payload = {"tool_name": "Bash", "tool_input": {"command": command}}
    if cwd is not None:
        payload["cwd"] = cwd
    return run_script(GLOB_DELETE, json.dumps(payload), python=python)


def run_script(script: Path, stdin: str, *args: str, env: dict[str, str] | None = None,
               python: str = sys.executable) -> subprocess.CompletedProcess[str]:
    return subprocess.run([python, "-I", str(script), *args], input=stdin, capture_output=True, text=True,
                          env=env if env is not None else {"PATH": "/usr/bin:/bin"}, timeout=30)


def setUpModule() -> None:
    support.never_run(sys.executable, str(SYSTEM_PYTHON))


class BlockGlobDeleteTest(unittest.TestCase):
    def assert_verdict(self, result: subprocess.CompletedProcess[str], refusal: str | None, command: str) -> None:
        if refusal is None:
            self.assertEqual((result.returncode, result.stderr), (0, ""), command)
        else:
            self.assertEqual(result.returncode, 2, command)
            self.assertIn(f"block-glob-delete ({refusal})", result.stderr, command)

    def test_refusal_table(self) -> None:
        for command, refusal in ROWS:
            with self.subTest(command=command):
                self.assert_verdict(run_hook(command), refusal, command)

    def test_relative_target_is_resolved_against_cwd(self) -> None:
        self.assert_verdict(run_hook("rm -r .", cwd="/tmp"), "shared-tmp", "rm -r . in /tmp")
        self.assert_verdict(run_hook("rm -r ..", cwd="/tmp/gdg.Ab12Cd"), "shared-tmp", "rm -r .. in /tmp/x")
        self.assert_verdict(run_hook("rm -r sub", cwd="/tmp/gdg.Ab12Cd"), None, "rm -r sub in /tmp/x")

    def test_unreadable_input_is_blocked(self) -> None:
        for stdin in ("not json", "", "[]", '{"tool_input":{"command":3}}'):
            with self.subTest(stdin=stdin):
                self.assertEqual(run_script(GLOB_DELETE, stdin).returncode, 2)

    def test_missing_command_is_allowed(self) -> None:
        self.assertEqual(run_script(GLOB_DELETE, '{"tool_input":{}}').returncode, 0)

    @unittest.skipUnless(SYSTEM_PYTHON.exists(), "no /usr/bin/python3: the interpreter the hook is wired to")
    def test_runs_under_the_system_interpreter(self) -> None:
        self.assert_verdict(run_hook("rm -r /tmp/tmp*", python=str(SYSTEM_PYTHON)), "glob", "system python")
        self.assert_verdict(run_hook("rm -r /tmp/gdg.Ab12Cd", python=str(SYSTEM_PYTHON)), None, "system python")


def load_session_tmpdir() -> types.ModuleType:
    spec = importlib.util.spec_from_file_location("session_tmpdir", SESSION_TMPDIR)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class SessionTmpdirTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name).resolve() / "T"
        self.root.mkdir()
        self.env_file = Path(self._tmp.name) / "env"
        self.env = {"PATH": "/usr/bin:/bin", "TMPDIR": str(self.root) + "/", "CLAUDE_ENV_FILE": str(self.env_file)}
        self.session = self.root / f"claude-{SESSION_ID}"

    def hook(self, phase: str, session_id: str = SESSION_ID, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return run_script(SESSION_TMPDIR, json.dumps({"session_id": session_id}), phase, env=env or self.env)

    def test_start_creates_a_private_directory_and_exports_it_once(self) -> None:
        self.assertEqual(self.hook("start").returncode, 0)
        self.assertEqual(self.hook("start").returncode, 0)
        self.assertEqual(self.session.stat().st_mode & 0o777, 0o700)
        self.assertEqual(self.env_file.read_text(), f"export TMPDIR={self.session}/\n")

    def test_start_refuses_a_bad_id_a_missing_env_file_and_a_foreign_entry(self) -> None:
        self.assertEqual(self.hook("start", session_id="../../x").returncode, 2)
        self.assertEqual(self.hook("start", session_id="short").returncode, 2)
        self.assertEqual(self.hook("start", env={k: v for k, v in self.env.items() if k != "CLAUDE_ENV_FILE"}).returncode, 2)
        self.session.symlink_to(self.root)
        self.assertEqual(self.hook("start").returncode, 2)
        self.assertFalse(self.env_file.exists())

    def test_end_removes_exactly_the_session_directory(self) -> None:
        self.hook("start")
        (self.session / "scratch").write_text("x")
        other = self.root / "claude-other-session-id"
        other.mkdir()
        self.assertEqual(self.hook("end").returncode, 0)
        self.assertFalse(self.session.exists())
        self.assertTrue(other.is_dir())
        self.assertEqual(self.hook("end").returncode, 0)

    def test_end_finds_the_directory_when_the_hook_already_sees_the_session_tmpdir(self) -> None:
        self.hook("start")
        env = {**self.env, "TMPDIR": str(self.session) + "/"}
        self.assertEqual(self.hook("end", env=env).returncode, 0)
        self.assertFalse(self.session.exists())

    def test_end_leaves_a_symlink_and_its_target_alone(self) -> None:
        target = self.root / "precious"
        target.mkdir()
        (target / "keep").write_text("x")
        self.session.symlink_to(target)
        self.assertEqual(self.hook("end").returncode, 1)
        self.assertTrue((target / "keep").is_file())
        self.assertTrue(self.session.is_symlink())

    def test_end_leaves_a_directory_another_user_owns(self) -> None:
        self.hook("start")
        module = load_session_tmpdir()
        with mock.patch.dict(os.environ, {"TMPDIR": str(self.root)}), \
                mock.patch.object(module.os, "getuid", return_value=os.getuid() + 1), \
                mock.patch.object(sys, "stdin", io.StringIO(json.dumps({"session_id": SESSION_ID}))), \
                self.assertRaises(SystemExit) as raised:
            module.end()
        self.assertEqual(raised.exception.code, 1)
        self.assertTrue(self.session.is_dir())


if __name__ == "__main__":
    unittest.main()
