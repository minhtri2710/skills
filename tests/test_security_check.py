#!/usr/bin/env python3
"""Tests for the local security-check runner."""
from __future__ import annotations

import contextlib
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

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "security-setup" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import security_check  # noqa: E402


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

    def run_main(self, *args: str) -> tuple[int, str, str]:
        stdout, stderr = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
            code = security_check.main(list(args))
        return code, stdout.getvalue(), stderr.getvalue()

    def run_with_reports(self, config: Path, *args: str) -> tuple[int, str, str, dict[str, object]]:
        output, markdown = self.report_paths()
        code, stdout, stderr = self.run_main(
            "--config", str(config), "--output", str(output), "--markdown", str(markdown), *args
        )
        payload = json.loads(output.read_text(encoding="utf-8"))
        return code, stdout, stderr, payload

    def init_git(self) -> None:
        subprocess.run(["git", "init", "-q", "-b", "main"], cwd=self.root, check=True)

    def stage(self, relative: str, content: str) -> None:
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        subprocess.run(["git", "add", relative], cwd=self.root, check=True)

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

    def test_default_config_validates(self) -> None:
        security_check.validate_config(security_check.DEFAULT_CONFIG)
        self.assertEqual(security_check.load_config(None), security_check.DEFAULT_CONFIG)

    def test_fail_on_rejects_empty_unknown_and_non_string_values(self) -> None:
        for fail_on in ([], ["HIHG"], [1], ["HIGH", "UNKNOWN"]):
            with self.subTest(fail_on=fail_on):
                config = self.write_config([self.one_check()], fail_on=fail_on)  # type: ignore[arg-type]
                output, markdown = self.report_paths("invalid-fail-on")
                code, stdout, stderr = self.run_main(
                    "--config", str(config),
                    "--output", str(output),
                    "--markdown", str(markdown),
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
        code, stdout, stderr = self.run_main(
            "--config", str(missing),
            "--output", str(output),
            "--markdown", str(markdown),
        )
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertEqual(stderr, "Configuration error: configuration file not found: " + str(missing) + "\n")
        self.assertFalse(output.exists())
        self.assertFalse(markdown.exists())

    def test_category_formatter_is_sorted_and_has_none_case(self) -> None:
        self.assertEqual(security_check.format_categories({}), "none")
        self.assertEqual(
            security_check.format_categories({"static": 2, "secrets": 1}),
            "secrets=1, static=2",
        )

    def test_scope_triggers_and_trip_all_paths(self) -> None:
        _, docs = security_check.evaluate_scope(security_check.DEFAULT_CONFIG, ["README.md"])
        self.assertTrue(docs["gitleaks"]["run"])
        self.assertFalse(docs["trivy"]["run"])
        self.assertFalse(docs["semgrep"]["run"])

        _, lockfile = security_check.evaluate_scope(security_check.DEFAULT_CONFIG, ["package-lock.json"])
        self.assertTrue(lockfile["trivy"]["run"])
        self.assertFalse(lockfile["semgrep"]["run"])

        _, source = security_check.evaluate_scope(security_check.DEFAULT_CONFIG, ["src/app.py"])
        self.assertTrue(source["semgrep"]["run"])

        _, workflow = security_check.evaluate_scope(
            security_check.DEFAULT_CONFIG, [".github/workflows/check.yml"]
        )
        self.assertTrue(all(decision["run"] for decision in workflow.values()))

        _, full = security_check.evaluate_scope(security_check.DEFAULT_CONFIG, None)
        self.assertTrue(all(decision["run"] for decision in full.values()))

    def test_cli_help_unknown_option_and_mutually_exclusive_scope(self) -> None:
        with self.assertRaises(SystemExit) as help_exit:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                security_check.main(["--help"])
        self.assertEqual(help_exit.exception.code, 0)

        with self.assertRaises(SystemExit) as unknown_exit:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                security_check.main(["--not-an-option"])
        self.assertEqual(unknown_exit.exception.code, 2)

        with self.assertRaises(SystemExit) as exclusive_exit:
            with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                security_check.main(["--all", "--staged-only"])
        self.assertEqual(exclusive_exit.exception.code, 2)

    def test_staged_only_without_staged_file_exits_two(self) -> None:
        self.init_git()
        code, stdout, stderr = self.run_main("--staged-only")
        self.assertEqual(code, 2)
        self.assertEqual(stdout, "")
        self.assertIn("--staged-only requires", stderr)

    def test_always_on_secret_scope_with_staged_documentation(self) -> None:
        self.clean_fakes()
        self.init_git()
        self.stage("docs/example.md", "synthetic-token-like-value-for-testing-only\n")
        output, markdown = self.report_paths()
        code, stdout, stderr = self.run_main(
            "--staged-only", "--output", str(output), "--markdown", str(markdown)
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
        self.assertNotIn("RAW-SCANNER-OUTPUT", output.read_text(encoding="utf-8"))

    def test_all_runs_every_configured_check(self) -> None:
        self.clean_fakes()
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

    def test_parsers_map_scanner_severities(self) -> None:
        gitleaks = security_check.parse_gitleaks(
            [{"Description": "Synthetic secret-like finding", "File": "docs/example.md"}],
            "secrets",
            "gitleaks",
        )
        self.assertEqual(gitleaks[0]["severity"], "HIGH")

        trivy = security_check.parse_trivy(
            {"Results": [{"Target": "package-lock.json", "Vulnerabilities": [
                {"VulnerabilityID": "SYNTHETIC-1", "PkgName": "fixture", "Severity": "CRITICAL"}
            ]}]},
            "dependencies",
            "trivy",
        )
        self.assertEqual(trivy[0]["severity"], "CRITICAL")

        semgrep = security_check.parse_semgrep(
            {"results": [{"path": "src/app.py", "extra": {"severity": "ERROR"}}]},
            "static",
            "semgrep",
        )
        self.assertEqual(semgrep[0]["severity"], "HIGH")

        bandit = security_check.parse_bandit(
            {"results": [{"filename": "src/app.py", "issue_severity": "WARNING"}]},
            "static",
            "bandit",
        )
        self.assertEqual(bandit[0]["severity"], "MEDIUM")

        cargo = security_check.parse_cargo_audit(
            {"vulnerabilities": {"list": [{
                "advisory": {"id": "SYNTHETIC-RUST-1", "severity": "low"},
                "package": {"name": "fixture"},
            }]}},
            "dependencies",
            "cargo-audit",
        )
        self.assertEqual(cargo[0]["severity"], "LOW")

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
