#!/usr/bin/env python3
from __future__ import annotations

import contextlib
import io
import json
import os
import stat
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import support
import security_check


def setUpModule() -> None:
    support.never_run("git", "gitleaks", "trivy", "semgrep", "bandit", "cargo-audit")


class InteractiveInput(io.StringIO):
    def isatty(self) -> bool:
        return True


class SecurityCheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.root = Path(self._tmp.name)
        self.bin = self.root / "bin"
        self.bin.mkdir()
        self.old_cwd = Path.cwd()
        self.old_path = os.environ.get("PATH", "")
        os.chdir(self.root)
        os.environ["PATH"] = str(self.bin) + os.pathsep + self.old_path

    def tearDown(self) -> None:
        os.chdir(self.old_cwd)
        os.environ["PATH"] = self.old_path
        self._tmp.cleanup()

    def write_fake(self, name: str, body: str) -> None:
        path = self.bin / name
        path.write_text("#!/bin/sh\nset -eu\n" + body, encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)

    def write_config(self, checks: list[dict[str, object]], fail_on: list[str] | None = None) -> Path:
        path = self.root / "config.json"
        path.write_text(
            json.dumps({"fail_on": ["HIGH"] if fail_on is None else fail_on, "checks": checks}),
            encoding="utf-8",
        )
        return path

    def one_check(
        self,
        name: str = "gitleaks",
        category: str = "secrets",
        command: list[str] | None = None,
        **extra: object,
    ) -> dict[str, object]:
        check: dict[str, object] = {
            "name": name,
            "category": category,
            "required": True,
            "command": command or [name],
        }
        check.update(extra)
        return check

    def report_paths(self, stem: str = "report") -> tuple[Path, Path]:
        return self.root / (stem + ".json"), self.root / (stem + ".md")

    def run_with_reports(self, config: Path, *args: str) -> tuple[int, str, str, dict[str, object]]:
        output, markdown = self.report_paths()
        code, stdout, stderr = support.run_main(
            security_check.main,
            ["--config", str(config), "--output", str(output), "--markdown", str(markdown), *args],
        )
        payload = json.loads(output.read_text(encoding="utf-8"))
        return code, stdout, stderr, payload

    def init_git(self) -> None:
        support.temp_git_repo(self.root)

    def stage(self, relative: str, content: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        support.git(self.root, "add", relative)

    def clean_fakes(self) -> None:
        self.write_fake(
            "gitleaks",
            "report=\"\"\n"
            "while [ \"$#\" -gt 0 ]; do\n"
            "  if [ \"$1\" = \"--report-path\" ]; then report=$2; shift 2; else shift; fi\n"
            "done\n"
            "if [ -n \"$report\" ]; then printf '%s\\n' '[]' > \"$report\"; else printf '%s\\n' '[]'; fi\n",
        )
        self.write_fake("trivy", "printf '%s\\n' '{\"Results\":[]}'\n")
        self.write_fake("semgrep", "printf '%s\\n' '{\"results\":[]}'\n")

    def test_fail_on_rejects_empty_unknown_and_non_string_values(self) -> None:
        for fail_on in ([], ["HIHG"], [1], ["HIGH", "UNKNOWN"]):
            with self.subTest(fail_on=fail_on):
                config = self.write_config([self.one_check()], fail_on=fail_on)  # type: ignore[arg-type]
                output, markdown = self.report_paths("invalid-fail-on")
                code, stdout, stderr = support.run_main(
                    security_check.main,
                    ["--config", str(config), "--output", str(output), "--markdown", str(markdown)],
                )
                self.assertEqual(code, 2)
                self.assertEqual(stdout, "")
                self.assertEqual(
                    stderr,
                    "Configuration error: fail_on must be a non-empty list of known severities\n",
                )
                self.assertFalse(output.exists())
                self.assertFalse(markdown.exists())

    def test_explicit_missing_config_exits_two(self) -> None:
        output, markdown = self.report_paths()
        missing = self.root / "missing.json"
        code, stdout, stderr = support.run_main(
            security_check.main,
            ["--config", str(missing), "--output", str(output), "--markdown", str(markdown)],
        )
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "Configuration error: configuration file not found: " + str(missing) + "\n")
        self.assertFalse(output.exists())
        self.assertFalse(markdown.exists())

    def test_categories_are_sorted_and_none_when_empty(self) -> None:
        self.write_fake(
            "semgrep",
            "printf '%s\\n' '{\"results\":[{\"path\":\"src/app.py\",\"extra\":{\"severity\":\"INFO\"}}]}'\n",
        )
        self.write_fake("gitleaks", "printf '%s\\n' '[{\"Description\":\"Synthetic\"}]'\n")
        config = self.write_config(
            [self.one_check(name="semgrep", category="static"), self.one_check()], fail_on=["CRITICAL"]
        )
        _, stdout, _, _ = self.run_with_reports(config)
        self.assertIn("Categories: secrets=1, static=1\n", stdout)

        self.clean_fakes()
        config = self.write_config([self.one_check()])
        _, stdout, _, _ = self.run_with_reports(config)
        self.assertIn("Categories: none\n", stdout)

    def test_staged_scope_triggers_and_trip_all_paths(self) -> None:
        self.clean_fakes()
        self.init_git()
        config = self.write_config([
            self.one_check(),
            self.one_check(name="trivy", category="dependencies"),
            self.one_check(name="semgrep", category="static"),
        ])
        cases = {
            "README.md": {"gitleaks"},
            "package-lock.json": {"gitleaks", "trivy"},
            "src/app.py": {"gitleaks", "semgrep"},
            ".github/workflows/check.yml": {"gitleaks", "trivy", "semgrep"},
            "docker/Dockerfile.dev": {"gitleaks", "trivy", "semgrep"},
        }
        for path, expected_to_run in cases.items():
            with self.subTest(path=path):
                self.stage(path, "synthetic\n")
                _, _, _, payload = self.run_with_reports(config, "--staged-only")
                support.git(self.root, "rm", "-q", "--cached", path)
                ran = {check["name"] for check in payload["checks"] if not check["skipped"]}
                self.assertEqual(ran, expected_to_run)

    def test_all_and_staged_only_are_mutually_exclusive(self) -> None:
        with self.assertRaises(SystemExit) as exclusive_exit:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                security_check.main(["--all", "--staged-only"])
        self.assertEqual(exclusive_exit.exception.code, 2)

    def test_staged_only_without_staged_file_exits_two(self) -> None:
        self.init_git()
        code, stdout, stderr = support.run_main(security_check.main, ["--staged-only"])
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("--staged-only requires", stderr)

    def test_always_on_secret_scope_with_staged_documentation(self) -> None:
        self.clean_fakes()
        self.init_git()
        self.stage("docs/example.md", "synthetic-token-like-value-for-testing-only\n")
        output, markdown = self.report_paths()
        code, stdout, stderr = support.run_main(
            security_check.main, ["--staged-only", "--output", str(output), "--markdown", str(markdown)]
        )
        payload = json.loads(output.read_text(encoding="utf-8"))
        self.assertEqual(stderr, "")
        self.assertEqual(code, 0)
        self.assertEqual(payload["scope"]["mode"], "staged")
        checks = {check["name"]: check for check in payload["checks"]}
        self.assertEqual(checks["gitleaks"]["status"], "Assessed")
        self.assertTrue(checks["gitleaks"]["matched_paths"])
        self.assertTrue(checks["trivy"]["skipped"])
        self.assertTrue(checks["semgrep"]["skipped"])

    def test_missing_executable_is_not_assessed_and_allow_missing_is_partial(self) -> None:
        config = self.write_config(
            [self.one_check(command=["missing-synthetic-scanner"])],
        )
        code, _, stderr, payload = self.run_with_reports(config)
        self.assertEqual(code, 2)
        self.assertIn("assessment incomplete", stderr)
        self.assertEqual(payload["checks"][0]["status"], "Not-Assessed")
        self.assertEqual(payload["checks"][0]["findings"][0]["assessment"], "Not-Assessed")

        code, _, stderr, payload = self.run_with_reports(config, "--allow-missing-tools")
        self.assertEqual(code, 0)
        self.assertIn("report is partial", stderr)
        self.assertEqual(payload["summary"]["not_assessed"], 1)
        self.assertEqual(payload["checks"][0]["status"], "Not-Assessed")

    def test_missing_executable_record_names_its_command(self) -> None:
        config = self.write_config([self.one_check(command=["missing-synthetic-scanner", "--flag"])])
        _, _, _, payload = self.run_with_reports(config)
        self.assertEqual(payload["checks"][0]["command_name"], "missing-synthetic-scanner")

    def test_malformed_config_exits_two_before_any_scanner_runs(self) -> None:
        marker = self.root / "gitleaks-ran"
        self.write_fake("gitleaks", "touch " + str(marker) + "\nprintf '%s\\n' '[]'\n")
        self.write_fake("semgrep", "printf '%s\\n' '{\"results\":[]}'\n")
        first = self.one_check()
        second = self.one_check(name="semgrep", category="static")
        cases = {
            "expected_returncodes must be a list of integers": ({"expected_returncodes": ["0"]}, {}),
            "trip_all_paths must be a list of globs": ({}, {"trip_all_paths": "security/**"}),
            "check trigger paths must be a list of globs": ({"triggers": {"paths": "**/*.py"}}, {}),
        }
        for message, (second_extra, top_level) in cases.items():
            with self.subTest(message=message):
                marker.unlink(missing_ok=True)
                config = self.write_config([first, {**second, **second_extra}])
                config.write_text(
                    json.dumps({**json.loads(config.read_text(encoding="utf-8")), **top_level}),
                    encoding="utf-8",
                )
                output, markdown = self.report_paths("malformed")
                code, stdout, stderr = support.run_main(
                    security_check.main,
                    ["--config", str(config), "--output", str(output), "--markdown", str(markdown), "--all"],
                )
                self.assertEqual(code, 2)
                self.assertEqual(stdout, "")
                self.assertEqual(stderr, "Configuration error: " + message + "\n")
                self.assertFalse(marker.exists())
                self.assertFalse(output.exists())

    def test_malformed_output_and_timeout_are_not_green(self) -> None:
        self.write_fake("gitleaks", "printf '%s\\n' 'RAW-SCANNER-OUTPUT'\n")
        config = self.write_config([self.one_check()])
        code, _, _, payload = self.run_with_reports(config)
        self.assertEqual(code, 2)
        self.assertEqual(payload["checks"][0]["status"], "Not-Assessed")
        self.assertNotIn("RAW-SCANNER-OUTPUT", json.dumps(payload))

        self.write_fake("gitleaks", "sleep 2\n")
        config = self.write_config([self.one_check(timeout_seconds=1)])
        code, _, _, payload = self.run_with_reports(config)
        self.assertEqual(code, 2)
        self.assertIn("timed out", payload["checks"][0]["tool_error"])
        self.assertEqual(payload["checks"][0]["status"], "Not-Assessed")

    def test_report_containment_and_category_counts(self) -> None:
        self.write_fake(
            "gitleaks",
            "printf '%s\\n' '[{\"Description\":\"Synthetic secret-like finding\",\"File\":\"docs/example.md\"}]'\n",
        )
        self.write_fake(
            "semgrep",
            "printf '%s\\n' '{\"results\":[{\"path\":\"src/app.py\",\"extra\":{\"severity\":\"WARNING\",\"message\":\"Synthetic static finding\"}}]}'\n",
        )
        config = self.write_config(
            [
                self.one_check(),
                self.one_check(name="semgrep", category="static"),
            ],
            fail_on=["CRITICAL"],
        )
        before = {path.relative_to(self.root) for path in self.root.rglob("*") if path.is_file()}
        output, markdown = self.report_paths()
        code, stdout, _, payload = self.run_with_reports(config)
        after = {path.relative_to(self.root) for path in self.root.rglob("*") if path.is_file()}
        self.assertEqual(code, 0)
        self.assertEqual(after - before, {output.relative_to(self.root), markdown.relative_to(self.root)})
        self.assertIn("Categories: secrets=1, static=1", stdout)
        self.assertIn("- Categories: secrets=1, static=1", markdown.read_text(encoding="utf-8"))
        self.assertEqual(payload["summary"]["category_counts"], {"secrets": 1, "static": 1})

    def test_all_runs_every_configured_check_for_staged_docs(self) -> None:
        self.clean_fakes()
        self.init_git()
        self.stage("docs/example.md", "synthetic-token-like-value-for-testing-only\n")
        config = self.write_config(
            [
                self.one_check(),
                self.one_check(name="trivy", category="dependencies"),
                self.one_check(name="semgrep", category="static"),
            ]
        )
        code, _, _, payload = self.run_with_reports(config, "--all")
        self.assertEqual(code, 0)
        self.assertEqual(payload["scope"]["mode"], "full")
        self.assertEqual(payload["summary"]["checks_run"], 3)
        self.assertTrue(all(check["status"] == "Assessed" for check in payload["checks"]))

    def test_scanner_severities_map_to_report_severities(self) -> None:
        def emit(body: str) -> str:
            return "printf '%s\\n' '" + body + "'\n"

        self.write_fake("gitleaks", emit('[{"Description":"Synthetic secret-like finding","File":"docs/example.md"}]'))
        self.write_fake("trivy", emit(
            '{"Results":[{"Target":"package-lock.json","Vulnerabilities":'
            '[{"VulnerabilityID":"SYNTHETIC-1","PkgName":"fixture","Severity":"CRITICAL"}]}]}'
        ))
        self.write_fake("semgrep", emit(
            '{"results":[{"path":"a.py","extra":{"severity":"ERROR","message":"error rule"}},'
            '{"path":"b.py","extra":{"severity":"WARNING","message":"warning rule"}},'
            '{"path":"c.py","extra":{"severity":"INFO","message":"info rule"}}]}'
        ))
        self.write_fake("bandit", emit('{"results":[{"filename":"a.py","issue_severity":"MEDIUM","issue_text":"bandit rule"}]}'))
        self.write_fake("cargo-audit", emit(
            '{"vulnerabilities":{"list":[{"advisory":{"id":"SYNTHETIC-RUST-1","severity":"low"},"package":{"name":"fixture"}}]}}'
        ))
        config = self.write_config(
            [
                self.one_check(),
                self.one_check(name="trivy", category="dependencies"),
                self.one_check(name="semgrep", category="static"),
                self.one_check(name="bandit", category="static"),
                self.one_check(name="cargo-audit", category="dependencies"),
            ],
            fail_on=["CRITICAL"],
        )
        _, _, _, payload = self.run_with_reports(config)
        severities = {item["title"]: item["severity"] for item in payload["findings"]}
        self.assertEqual(severities, {
            "Synthetic secret-like finding": "HIGH",
            "SYNTHETIC-1 in fixture": "CRITICAL",
            "error rule": "HIGH",
            "warning rule": "MEDIUM",
            "info rule": "INFO",
            "bandit rule": "MEDIUM",
            "SYNTHETIC-RUST-1 in fixture": "LOW",
        })

    def test_fail_on_hit_exits_one_and_below_threshold_exits_zero(self) -> None:
        self.write_fake(
            "gitleaks",
            "printf '%s\\n' '[{\"Description\":\"Synthetic secret-like finding\"}]'\n",
        )
        config = self.write_config([self.one_check()], fail_on=["HIGH"])
        code, _, _, _ = self.run_with_reports(config)
        self.assertEqual(code, 1)

        config = self.write_config([self.one_check()], fail_on=["CRITICAL"])
        code, _, _, _ = self.run_with_reports(config)
        self.assertEqual(code, 0)

    def test_force_is_refused_non_interactively_and_yes_bypasses_only_findings(self) -> None:
        self.write_fake(
            "gitleaks",
            "printf '%s\\n' '[{\"Description\":\"Synthetic secret-like finding\"}]'\n",
        )
        config = self.write_config([self.one_check()])
        with patch.object(security_check.sys, "stdin", io.StringIO()):
            code, _, stderr, payload = self.run_with_reports(config, "--force")
        self.assertEqual(code, 1)
        self.assertIn("Refusing --force", stderr)
        self.assertEqual(payload["bypass"]["status"], "denied")

        with patch.object(security_check.sys, "stdin", InteractiveInput()), patch(
            "builtins.input", return_value="YES"
        ):
            code, _, _, payload = self.run_with_reports(config, "--force")
        self.assertEqual(code, 0)
        self.assertEqual(payload["bypass"]["status"], "BYPASSED")
        self.assertEqual(payload["bypass"]["accepted"], True)


if __name__ == "__main__":
    unittest.main()
