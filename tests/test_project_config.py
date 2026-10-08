#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "herdr-delivery-workflow"
SCRIPT = SKILL / "scripts" / "project_config.py"
sys.path.insert(0, str(SKILL / "scripts"))

import project_config  # noqa: E402

_FULL = {
    "lead-kind": "pi",
    "lead-args": ["--model", "lead-model"],
    "launch-profiles": {"pi": {"seat-argv": ["--name", "{seat}"], "peer-argv": ["--settings", "{settings_file}"], "peer-settings-json": {"lead": "{lead}"}}},
    "engineer-kind": "claude",
    "engineer-args": ["--model", "m1", "--permission-mode", "auto", ""],
    "reviewer-kind": "claude",
    "reviewer-args": ["--model", "m1"],
    "engineer-fallback": "pi",
    "reviewer-fallback": "pi",
    "engineer-fallback-args": ["--approve"],
    "reviewer-fallback-args": [],
    "checks-light": ["python -m unittest"],
    "checks-heavy": ["python -m unittest discover"],
    "ci": {"trigger": "push", "workflows": [".github/workflows/ci.yml"]},
    "local-ops": ["make dev"],
    "lane-defaults": {"docs/": "tiny", "src/": "high-risk"},
    "target-line": "main",
    "always-gate": ["push"],
    "worker-cap": 3,
    "provenance": {"file": ["why"], "worker-cap": ["why"]},
}


class ProjectConfigTests(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory()
        self.addCleanup(directory.cleanup)
        self.path = Path(directory.name) / "config.json"

    def _write(self, content) -> Path:
        self.path.write_text(
            content if isinstance(content, str) else json.dumps(content), encoding="utf-8"
        )
        return self.path

    def test_accepts_a_config_with_every_key(self):
        self.assertEqual(project_config.load(self._write(_FULL)), _FULL)

    def test_refuses_each_class_naming_the_path_and_the_key(self):
        cases = [
            ({key: value for key, value in _FULL.items() if key != "lead-args"}, "lead-kind and lead-args must be configured together"),
            ({key: value for key, value in _FULL.items() if key != "engineer-fallback-args"}, "engineer-fallback and engineer-fallback-args must be configured together"),
            ({key: value for key, value in _FULL.items() if key != "reviewer-fallback"}, "reviewer-fallback and reviewer-fallback-args must be configured together"),
            ({**_FULL, "engineer-arg": []}, "engineer-arg: unknown key"),
            ({**_FULL, "launch-profiles": {"pi": {"unknown-key": []}}}, "launch-profiles.pi.unknown-key: unknown key"),
            ({**_FULL, "launch-profiles": {"pi": {"seat-argv": ["{unknown}"]}}}, "unknown placeholder"),
            ({**_FULL, "launch-profiles": {"pi": {"runtime-state-dir": "/tmp/{unknown}"}}}, "unknown placeholder"),
            ({**_FULL, "launch-profiles": {"pi": {"runtime-state-dir": "relative"}}}, "must be an absolute path"),
            ({**_FULL, "engineer-args": "--model m1"}, "engineer-args: must be an array of strings"),
            ({**_FULL, "engineer-kind": ""}, "engineer-kind: must be a non-empty string"),
            ({**_FULL, "lane-defaults": {"src/": "tiny", "docs/": "urgent"}}, "lane-defaults.docs/: must map to one of"),
            ({**_FULL, "target-line": 5}, "target-line: must be a non-empty string"),
            ({**_FULL, "engineer-args": ["--model", 1]}, "engineer-args: must be an array of strings"),
            ({**_FULL, "checks-light": ["ok", ""]}, "checks-light: must be an array of non-empty strings"),
            ({**_FULL, "ci": ["trigger", "workflows"]},"ci: must be an object with exactly"),
            ({**_FULL, "ci": {**_FULL["ci"], "extra": 1}}, "ci: must be an object with exactly"),
            ({**_FULL, "ci": {"trigger": "always", "workflows": ["ci.yml"]}}, "ci.trigger: must be one of"),
            ({**_FULL, "ci": {"trigger": "pr"}}, "ci: must be an object with exactly"),
            ({**_FULL, "ci": {"trigger": "pr", "workflows": []}}, "ci: workflows must be empty exactly when trigger is none"),
            ({**_FULL, "ci": {"trigger": "pr", "workflows": ["ci.yml", ""]}}, "ci.workflows: must be an array of non-empty strings"),
            ({**_FULL, "lane-defaults": []}, "lane-defaults: must be an object"),
            ({**_FULL, "lane-defaults": {"src/": "tiny", "": "tiny"}}, "lane-defaults.: must map to one of"),
            ({**_FULL, "provenance": []}, "provenance: must be an object"),
            ({**_FULL, "provenance": {"engineer-kind": ["ok"], "file": "why"}}, "provenance.file: must be an array of strings"),
            ({**_FULL, "worker-cap": "3"}, "worker-cap: must be an integer >= 1"),
            ({**_FULL, "worker-cap": True}, "worker-cap: must be an integer >= 1"),
            ({**_FULL, "worker-cap": 0}, "worker-cap: must be an integer >= 1"),
            ({**_FULL, "ci": {"trigger": "none", "workflows": ["ci.yml"]}}, "ci: workflows must be empty"),
            ({**_FULL, "provenance": {"file": ["ok"], "engineer-arg": ["x"]}}, "provenance.engineer-arg: unknown key"),
            ({**_FULL, "provenance": {"file": ["ok"], "provenance": ["x"]}}, "provenance.provenance: unknown key"),
            ('{"worker-cap": 1, "worker-cap": 2}', "duplicate key 'worker-cap'"),
            ('{"ci": {"trigger": "pr", "trigger": "pr"}}', "duplicate key 'trigger'"),
            ("[]", "top level must be an object"),
            ("{", "Expecting property name"),
            ("[" * 1000000 + "]" * 1000000, "nested too deeply"),
        ]
        for content, message in cases:
            with self.subTest(message=message):
                with self.assertRaises(ValueError) as caught:
                    project_config.load(self._write(content))
                self.assertTrue(
                    str(caught.exception).startswith(f"{self.path}: "), str(caught.exception)
                )
                self.assertIn(message, str(caught.exception))
        with self.assertRaises(ValueError) as caught:
            project_config.load(self.path.with_name("absent.json"))
        self.assertIn("absent.json", str(caught.exception))

    def _check(self, path: Path) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(SCRIPT), "--check", str(path)],
            capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL,
        )

    def test_check_prints_ok_or_one_refusal_line(self):
        ok = self._check(self._write(_FULL))
        self.assertEqual((ok.returncode, ok.stdout, ok.stderr), (0, f"ok: {self.path}\n", ""))
        refused = self._check(self._write({"no\npe": 1}))
        self.assertEqual(
            (refused.returncode, refused.stdout, refused.stderr),
            (1, "", f"{self.path}: no pe: unknown key\n"),
        )

    def test_expansion_uses_literal_closed_placeholders_and_fixed_role_fields(self):
        config = {
            "lead-kind": "pi", "lead-args": ["--model", "lead"],
            "reviewer-kind": "pi", "reviewer-args": ["--model", "reviewer"],
            "engineer-kind": "pi", "engineer-args": ["--approve"],
            "launch-profiles": {"pi": {
                "seat-argv": ["--name", "{seat}", "--exclude-tools", "ask_question"],
                "peer-argv": ["--settings", "{settings_file}"],
                "peer-settings-json": {"seat": "{seat}", "run": "{run_dir}"},
                "runtime-state-dir": "/tmp/state",
            }},
        }
        result = project_config.expand_launch(
            config, role="reviewer", kind="pi", role_args=["--model", "reviewer"],
            seat="rev", lead="lead", run_dir="/run", installed_skill_dir="/skill",
            settings_file="/run/settings.json",
        )
        self.assertEqual(result, {
            "argv": ["--model", "reviewer", "--name", "rev", "--exclude-tools", "ask_question", "--settings", "/run/settings.json"],
            "settings_file": "/run/settings.json",
            "settings_json": {"seat": "rev", "run": "/run"},
            "runtime_state_dir": "/tmp/state",
        })
        with self.assertRaisesRegex(ValueError, "must come from config"):
            project_config.expand_launch(
                config, role="reviewer", kind="pi", role_args=["--model", "wrong"],
                seat="rev", lead="lead", run_dir="/run", installed_skill_dir="/skill",
                settings_file="/run/settings.json",
            )
        engineer = project_config.expand_launch(
            config, role="engineer", kind="pi", role_args=["--approve"],
            seat="eng", lead="lead", run_dir="/run", installed_skill_dir="/skill",
            settings_file="/run/settings.json",
        )
        self.assertIsNone(engineer["runtime_state_dir"])
        architect = project_config.expand_launch(
            config, role="architect", kind="pi", role_args=["--model", "reviewer"],
            seat="arch", lead="lead", run_dir="/run", installed_skill_dir="/skill",
            settings_file="/run/settings.json",
        )
        self.assertEqual(architect["runtime_state_dir"], "/tmp/state")
        lead = project_config.expand_launch(
            config, role="lead", kind="pi", role_args=["--model", "lead"], seat="lead", lead="lead",
            run_dir="/run", installed_skill_dir="/skill", settings_file="/run/settings.json",
        )
        self.assertIsNone(lead["runtime_state_dir"])

    def test_expand_refuses_missing_primary_role_args(self):
        for role in ("engineer", "reviewer"):
            with self.subTest(role=role):
                config = {
                    f"{role}-kind": "pi",
                    "launch-profiles": {"pi": {"seat-argv": [], "peer-argv": []}},
                }
                with self.assertRaisesRegex(ValueError, f"{role} role args are missing"):
                    project_config.expand_launch(
                        config, role=role, kind="pi", role_args=[], seat="peer", lead="lead",
                        run_dir="/run", installed_skill_dir="/skill", settings_file="/run/settings.json",
                    )

    def test_expand_allows_configured_fallback_when_primary_args_are_absent_for_same_kind(self):
        config = {
            "engineer-kind": "pi", "engineer-fallback": "pi",
            "engineer-fallback-args": ["--model", "fallback"],
            "launch-profiles": {"pi": {"seat-argv": [], "peer-argv": []}},
        }
        result = project_config.expand_launch(
            config, role="engineer", kind="pi", role_args=["--model", "fallback"],
            seat="peer", lead="lead", run_dir="/run", installed_skill_dir="/skill",
            settings_file="/run/settings.json",
        )
        self.assertEqual(result["argv"], ["--model", "fallback"])

    def test_expand_cli_uses_current_fallback_kind_keys(self):
        config = {
            "engineer-kind": "claude", "engineer-args": ["--model", "engineer-primary"],
            "engineer-fallback": "pi", "engineer-fallback-args": ["--model", "engineer-fallback"],
            "reviewer-kind": "claude", "reviewer-args": ["--model", "reviewer-primary"],
            "reviewer-fallback": "pi", "reviewer-fallback-args": ["--model", "reviewer-fallback"],
            "launch-profiles": {"pi": {"seat-argv": [], "peer-argv": []}},
        }
        path = self._write(config)
        for role in ("engineer", "reviewer"):
            with self.subTest(role=role):
                result = subprocess.run(
                    [sys.executable, str(SCRIPT), "--expand", str(path), "--role", role,
                     "--fallback", "--kind", "pi", "--seat", "peer", "--lead", "lead-demo",
                     "--run-dir", "/run", "--installed-skill-dir", "/installed"],
                    capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL,
                )
                self.assertEqual((result.returncode, result.stderr), (0, ""))
                self.assertEqual(json.loads(result.stdout)["argv"], ["--model", f"{role}-fallback"])

    def test_expand_cli_emits_literal_json_for_the_existing_launcher(self):
        config = {
            "lead-kind": "pi", "lead-args": ["--approve"],
            "launch-profiles": {"pi": {
                "seat-argv": ["--name", "{seat}", "--exclude-tools", "ask_question"],
                "peer-argv": ["--settings", "{settings_file}"],
            }},
        }
        path = self._write(config)
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--expand", str(path), "--role", "lead",
             "--kind", "pi", "--seat", "lead-demo", "--lead", "lead-demo",
             "--run-dir", "/run", "--installed-skill-dir", "/installed"],
            capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL,
        )
        self.assertEqual((result.returncode, result.stderr), (0, ""))
        self.assertEqual(json.loads(result.stdout), {
            "argv": ["--approve", "--name", "lead-demo", "--exclude-tools", "ask_question"],
            "settings_file": None, "settings_json": None, "runtime_state_dir": None,
        })

    def test_peer_settings_are_seat_scoped_and_never_overwrite_different_data(self):
        config = {
            "engineer-kind": "pi", "engineer-args": ["--model", "m"],
            "launch-profiles": {"pi": {
                "seat-argv": [], "peer-argv": ["--settings", "{settings_file}"],
                "peer-settings-json": {"seat": "{seat}"},
            }},
        }
        config_path = self._write(config)
        run_dir = self.path.parent / "run"

        def expand(seat: str, settings: dict) -> subprocess.CompletedProcess:
            config_path.write_text(json.dumps({
                **config, "launch-profiles": {"pi": {
                    **config["launch-profiles"]["pi"], "peer-settings-json": settings,
                }},
            }), encoding="utf-8")
            return subprocess.run(
                [sys.executable, str(SCRIPT), "--expand", str(config_path), "--role", "engineer",
                 "--kind", "pi", "--seat", seat, "--lead", "lead-demo",
                 "--run-dir", str(run_dir), "--installed-skill-dir", "/installed"],
                capture_output=True, text=True, encoding="utf-8", stdin=subprocess.DEVNULL,
            )

        first = expand("peer-one", {"seat": "{seat}"})
        second = expand("peer-two", {"seat": "{seat}"})
        self.assertEqual((first.returncode, second.returncode), (0, 0))
        first_result, second_result = json.loads(first.stdout), json.loads(second.stdout)
        first_path = Path(first_result["settings_file"])
        second_path = Path(second_result["settings_file"])
        self.assertNotEqual(first_path, second_path)
        self.assertEqual(json.loads(first_path.read_text(encoding="utf-8")), {"seat": "peer-one"})
        self.assertEqual(json.loads(second_path.read_text(encoding="utf-8")), {"seat": "peer-two"})
        unchanged = expand("peer-one", {"seat": "{seat}"})
        self.assertEqual(unchanged.returncode, 0, unchanged.stderr)
        conflict = expand("peer-one", {"seat": "different"})
        self.assertEqual(conflict.returncode, 1)
        self.assertIn("already exists with different contents", conflict.stderr)
        self.assertEqual(json.loads(first_path.read_text(encoding="utf-8")), {"seat": "peer-one"})

    def test_the_shipped_template_loads(self):
        project_config.load(SKILL / "templates" / "config.json")


if __name__ == "__main__":
    unittest.main()
