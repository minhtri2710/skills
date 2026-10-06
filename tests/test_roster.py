#!/usr/bin/env python3
"""Tests for the compact roster read helper."""
from __future__ import annotations

import io
import json
import os
import subprocess
import sys
import tempfile
import time
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import roster  # noqa: E402


class RosterTest(unittest.TestCase):
    def setUp(self) -> None:
        self._stdout_patch = mock.patch.object(sys, "stdout", io.StringIO())
        self._stderr_patch = mock.patch.object(sys, "stderr", io.StringIO())
        self._stdout_patch.start()
        self._stderr_patch.start()
        self.addCleanup(self._stderr_patch.stop)
        self.addCleanup(self._stdout_patch.stop)

    def test_formats_agents_and_filters_workspace(self):
        payload = {
            "result": {
                "agents": [
                    {
                        "pane_id": "w1:p1",
                        "name": "lead",
                        "agent": "claude",
                        "agent_status": "working",
                        "workspace_id": "w1",
                    },
                    {
                        "pane_id": "w2:p1",
                        "agent": "agy",
                        "agent_status": "idle",
                        "workspace_id": "w2",
                    },
                ]
            }
        }
        self.assertEqual(
            roster.format_roster(payload),
            ["w1:p1 lead claude working", "w2:p1 - agy idle"],
        )
        self.assertEqual(
            roster.format_roster(payload, workspace="w1"),
            ["w1:p1 lead claude working"],
        )

    _SAMPLE = '{"result":{"agents":[{"pane_id":"w1:p1","name":"lead","agent":"claude","agent_status":"working","workspace_id":"w1"}]}}'

    def test_default_prints_the_agent_list(self):
        completed = subprocess.CompletedProcess(
            args=["herdr", "agent", "list"], returncode=0, stdout=self._SAMPLE, stderr=""
        )
        with mock.patch.object(roster.herdr_cli.subprocess, "run", return_value=completed) as run:
            output = io.StringIO()
            error = io.StringIO()
            with mock.patch("sys.stdout", output), mock.patch("sys.stderr", error):
                rc = roster.main(["--workspace", "w1"])
        self.assertEqual(rc, 0)
        self.assertEqual(output.getvalue(), "w1:p1 lead claude working\n")
        self.assertEqual(error.getvalue(), "")
        run.assert_called_once()

    def test_herdr_unavailable_maps_to_the_existing_cli_error(self):
        with mock.patch.object(
            roster.herdr_cli,
            "run",
            side_effect=roster.herdr_cli.HerdrUnavailable("herdr agent list timed out"),
        ):
            error = io.StringIO()
            with mock.patch("sys.stdout", io.StringIO()), mock.patch("sys.stderr", error):
                rc = roster.main([])
        self.assertEqual(rc, 1)
        self.assertIn("could not run herdr agent list", error.getvalue())

    def test_stalled_requires_report_absent_and_stale_progress_across_interval(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "report.md"
            progress = root / "progress.md"
            progress.write_text("old")
            stale_mtime = time.time() - 120
            os.utime(progress, (stale_mtime, stale_mtime))
            previous = root / "previous.json"
            previous.write_text(
                json.dumps({"peers": {"peer-1": {
                    "state": "working", "progress_mtime": stale_mtime,
                }}})
            )
            payload = {"result": {"agents": [{
                "pane_id": "w1:p1", "name": "peer-1", "agent": "claude",
                "agent_status": "idle", "workspace_id": "w1",
            }]}}
            completed = subprocess.CompletedProcess(
                args=["herdr", "agent", "list"], returncode=0,
                stdout=json.dumps(payload), stderr="",
            )
            with mock.patch.object(roster.herdr_cli.subprocess, "run", return_value=completed):
                output = io.StringIO()
                with mock.patch("sys.stdout", output):
                    rc = roster.main([
                        "--stalled", "--workspace", "w1",
                        "--peer", f"peer-1:{report}:{progress}",
                        "--previous-sample", str(previous), "--stale-after", "60",
                    ])
            self.assertEqual(rc, 0)
            self.assertEqual(output.getvalue(), "w1:p1 peer-1 claude STALLED\n")

    def test_never_started_requires_explicit_evidence_and_missing_progress(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "report.md"
            progress = root / "progress.md"
            payload = {"result": {"agents": [{
                "pane_id": "w1:p1", "name": "peer-1", "agent": "claude",
                "agent_status": "idle", "workspace_id": "w1",
                "tokens": {"sort_key": "000000000001"},
            }]}}
            completed = subprocess.CompletedProcess(
                args=["herdr", "agent", "list"], returncode=0,
                stdout=json.dumps(payload), stderr="",
            )
            with mock.patch.object(roster.herdr_cli.subprocess, "run", return_value=completed):
                output = io.StringIO()
                with mock.patch("sys.stdout", output):
                    rc = roster.main([
                        "--never-started", "peer-1", "--workspace", "w1",
                        "--peer", f"peer-1:{report}:{progress}",
                    ])
            self.assertEqual(rc, 0)
            self.assertEqual(output.getvalue(), "w1:p1 peer-1 claude NEVER-STARTED\n")

    def test_never_started_is_not_reported_when_progress_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "report.md"
            progress = root / "progress.md"
            progress.write_text("progress")
            payload = {"result": {"agents": [{
                "pane_id": "w1:p1", "name": "peer-1", "agent": "claude",
                "agent_status": "done", "workspace_id": "w1",
            }]}}
            completed = subprocess.CompletedProcess(
                args=["herdr", "agent", "list"], returncode=0,
                stdout=json.dumps(payload), stderr="",
            )
            with mock.patch.object(roster.herdr_cli.subprocess, "run", return_value=completed):
                output = io.StringIO()
                with mock.patch("sys.stdout", output):
                    rc = roster.main([
                        "--never-started", "peer-1",
                        "--peer", f"peer-1:{report}:{progress}",
                    ])
            self.assertEqual(rc, 0)
            self.assertEqual(output.getvalue(), "")

    def test_never_started_is_not_reported_when_report_exists(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "report.md"
            progress = root / "progress.md"
            report.write_text("done")
            payload = {"result": {"agents": [{
                "pane_id": "w1:p1", "name": "peer-1", "agent": "claude",
                "agent_status": "done", "workspace_id": "w1",
            }]}}
            completed = subprocess.CompletedProcess(
                args=["herdr", "agent", "list"], returncode=0,
                stdout=json.dumps(payload), stderr="",
            )
            with mock.patch.object(roster.herdr_cli.subprocess, "run", return_value=completed):
                output = io.StringIO()
                with mock.patch("sys.stdout", output):
                    rc = roster.main([
                        "--never-started", "peer-1",
                        "--peer", f"peer-1:{report}:{progress}",
                    ])
            self.assertEqual(rc, 0)
            self.assertEqual(output.getvalue(), "")

    def test_stalled_missing_progress_remains_fail_closed(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "report.md"
            progress = root / "progress.md"
            previous = root / "previous.json"
            previous.write_text(json.dumps({"peers": {
                "peer-1": {"state": "working", "progress_mtime": 0},
            }}))
            payload = {"result": {"agents": [{
                "pane_id": "w1:p1", "name": "peer-1", "agent": "claude",
                "agent_status": "idle", "workspace_id": "w1",
            }]}}
            completed = subprocess.CompletedProcess(
                args=["herdr", "agent", "list"], returncode=0,
                stdout=json.dumps(payload), stderr="",
            )
            with mock.patch.object(roster.herdr_cli.subprocess, "run", return_value=completed):
                output = io.StringIO()
                with mock.patch("sys.stdout", output):
                    rc = roster.main([
                        "--stalled", "--peer", f"peer-1:{report}:{progress}",
                        "--previous-sample", str(previous), "--stale-after", "60",
                    ])
            self.assertEqual(rc, 0)
            self.assertEqual(output.getvalue(), "")

    def test_stalled_single_idle_sample_with_report_is_not_stalled(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "report.md"
            report.write_text("done")
            progress = root / "progress.md"
            progress.write_text("old")
            stale_mtime = time.time() - 120
            os.utime(progress, (stale_mtime, stale_mtime))
            previous = root / "previous.json"
            previous.write_text(json.dumps({"peers": {
                "peer-1": {"state": "working", "progress_mtime": stale_mtime},
            }}))
            payload = {"result": {"agents": [{
                "pane_id": "w1:p1", "name": "peer-1", "agent": "claude",
                "agent_status": "idle", "workspace_id": "w1",
            }]}}
            completed = subprocess.CompletedProcess(
                args=["herdr", "agent", "list"], returncode=0,
                stdout=json.dumps(payload), stderr="",
            )
            with mock.patch.object(roster.herdr_cli.subprocess, "run", return_value=completed):
                output = io.StringIO()
                with mock.patch("sys.stdout", output):
                    rc = roster.main([
                        "--stalled", "--peer", f"peer-1:{report}:{progress}",
                        "--previous-sample", str(previous), "--stale-after", "60",
                    ])
            self.assertEqual(rc, 0)
            self.assertEqual(output.getvalue(), "")

    def test_stalled_single_idle_sample_with_fresh_progress_is_not_stalled(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / "report.md"
            progress = root / "progress.md"
            progress.write_text("fresh")
            current_mtime = progress.stat().st_mtime
            previous = {
                "peer-1": {
                    "state": "working",
                    "progress_mtime": current_mtime - 1,
                }
            }
            payload = {"result": {"agents": [{
                "pane_id": "w1:p1", "name": "peer-1", "agent": "claude",
                "agent_status": "idle", "workspace_id": "w1",
            }]}}
            lines = roster.format_stalled_roster(
                payload,
                {"peer-1": (report, progress)},
                previous,
                stale_after=60,
                now=current_mtime + 61,
            )
            self.assertEqual(lines, [])

    _DRIFT_CONFIG = {
        "engineer-kind": "pi",
        "engineer-args": ["--approve", "--model", "prov/luna"],
        "engineer-fallback": "pi",
        "engineer-fallback-args": ["--approve", "--model=prov/flash"],
        "reviewer-kind": "agy",
        "launch-profiles": {
            "pi": {"seat-argv": ["--name", "{seat}"], "peer-argv": []},
            "agy": {"seat-argv": [], "peer-argv": []},
            "claude": {"seat-argv": [], "peer-argv": []},
        },
    }

    def _drift(
        self, agents, argv_by_pane, seats, config=_DRIFT_CONFIG, extra_argv=(),
        pi_sessions=None, process_start=None, ps_result=(0, None),
    ):
        listing = json.dumps({"result": {"agents": agents}})

        def run(command, **_):
            if command[0] == "ps":
                rc, output = ps_result
                start = process_start or datetime(2026, 9, 26, 13).astimezone()
                stamp = start.strftime("%a %b %d %H:%M:%S %Y")
                return subprocess.CompletedProcess(command, rc, output or stamp, "ps failed" if rc else "")
            if command[1:3] == ["agent", "list"]:
                out = listing
            else:
                pane = command[-1]
                if isinstance(argv_by_pane[pane], tuple):
                    return subprocess.CompletedProcess(command, *argv_by_pane[pane], "")
                process = argv_by_pane[pane]
                procs = [{"argv": ["caffeinate", "-i"]}]
                procs.append(process if isinstance(process, dict) else {"argv": process})
                out = json.dumps({"result": {"process_info": {"foreground_processes": procs}}})
            return subprocess.CompletedProcess(command, 0, out, "")

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config_path = root / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            agent_dir = root / "pi-agent"
            for pane, files in (pi_sessions or {}).items():
                process = argv_by_pane[pane]
                cwd = process.get("cwd", "/workspace") if isinstance(process, dict) else "/workspace"
                slug = cwd.removeprefix("/").replace("/", "-").replace(":", "-")
                session_dir = agent_dir / "sessions" / f"--{slug}--"
                session_dir.mkdir(parents=True, exist_ok=True)
                for index, entries in enumerate(files):
                    path = session_dir / f"{pane.replace(':', '-')}-{index}.jsonl"
                    if isinstance(entries, str):
                        path.write_text(entries, encoding="utf-8")
                    else:
                        path.write_text("".join(json.dumps(entry) + "\n" for entry in entries), encoding="utf-8")
            output, error = io.StringIO(), io.StringIO()
            with mock.patch.object(roster.herdr_cli.subprocess, "run", side_effect=run), \
                    mock.patch.dict(os.environ, {"PI_CODING_AGENT_DIR": str(agent_dir)}), \
                    mock.patch("sys.stdout", output), mock.patch("sys.stderr", error):
                argv = ["--drift", str(config_path), *extra_argv]
                for seat in seats:
                    argv += ["--seat", seat]
                rc = roster.main(argv)
        return rc, output.getvalue().splitlines(), error.getvalue()

    def test_drift_flags_only_seats_matching_neither_config_route(self):
        process_start = datetime(2026, 9, 26, 13).astimezone()
        session_timestamp = process_start.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

        def session(name, model_changes, timestamp=session_timestamp, messages=True):
            entries = [
                {"type": "session", "timestamp": timestamp},
                {"type": "session_info", "name": name},
                *model_changes,
            ]
            if messages:
                entries.append({"type": "message"})
            return entries

        def agent(pane, name, kind):
            return {"pane_id": pane, "name": name, "agent": kind, "agent_status": "working"}

        agents = [
            agent("w1:p1", "eng-primary", "pi"),
            agent("w1:p2", "eng-fallback", "pi"),
            agent("w1:p3", "eng-model", "pi"),
            agent("w1:p4", "eng-kind", "claude"),
            agent("w1:p5", "review-a", "agy"),
            agent("w1:p6", "unlisted", "claude"),
            agent("w1:p7", "eng-noargv", "pi"),
            agent("w1:p8", "review-noargv", "claude"),
            agent("w1:p9", "review-noargs", "agy"),
            agent("w1:p10", "eng-named", "pi"),
            agent("w1:p11", "eng-wrong-model", "pi"),
            agent("w1:p12", "eng-no-session", "pi"),
            agent("w1:p13", "eng-old-session", "pi"),
            agent("w1:p14", "eng-other-seat", "pi"),
            agent("w1:p15", "eng-ambiguous", "pi"),
            agent("w1:p16", "eng-last-model", "pi"),
            agent("w1:p17", "eng-bare-route", "pi"),
            agent("w1:p19", "eng-no-model-change", "pi"),
            agent("w1:p20", "eng-after-message", "pi"),
            agent("w1:p21", "eng-malformed-files", "pi"),
        ]
        argv = {
            "w1:p1": ["node", "/opt/bin/pi", "--approve", "--model", "prov/luna", "--name", "eng-primary"],
            "w1:p2": ["pi", "--approve", "--model=prov/flash", "--name", "eng-fallback"],
            "w1:p3": ["pi", "--model", "prov/old", "--name", "eng-model"],
            "w1:p4": {
                "argv0": "claude",
                "argv": ["claude", "--model", "claude-opus-5-5", "--effort", "low", "--name", "eng-kind"],
                "cwd": "/Users/beowulf/Work/beo-skills",
                "name": "2.1.283",
                "pid": 6753,
            },
            "w1:p5": ["agy", "--dangerously-skip-permissions", "--name", "review-a"],
            "w1:p9": {"argv0": "agy", "cwd": "/tmp", "name": "agy", "pid": 100},
            "w1:p7": {
                "argv0": "pi", "cwd": "/Users/beowulf/Work/beo-skills",
                "name": "node", "pid": 14423,
            },
            "w1:p8": {"argv0": "claude", "cwd": "/tmp", "name": "node", "pid": 99},
            "w1:p10": {"argv0": "pi", "cwd": "/workspace:project", "name": "node", "pid": 14410},
            **{
                f"w1:p{i}": {
                    "argv": ["pi", "--model", "prov/other"],
                    "argv0": "pi", "cwd": "/workspace/project", "name": "node", "pid": 14400 + i,
                }
                for i in range(11, 16)
            },
            **{
                f"w1:p{i}": {
                    "argv0": "pi", "cwd": "/workspace/project", "name": "node", "pid": 14400 + i,
                }
                for i in (16, 17)
            },
            "w1:p19": {"argv0": "pi", "cwd": "/workspace/project", "name": "node", "pid": 14419},
            "w1:p20": {"argv0": "pi", "cwd": "/workspace/project", "name": "node", "pid": 14420},
            "w1:p21": {"argv": ["pi", "--model", "prov/luna", "--name", "eng-malformed-files"], "argv0": "pi", "cwd": "/workspace/project", "name": "node", "pid": 14421},
        }
        seats = ["eng-primary:engineer", "eng-fallback:engineer", "eng-model:engineer",
                 "eng-kind:engineer", "review-a:reviewer", "eng-noargv:engineer",
                 "review-noargv:reviewer", "review-noargs:reviewer", "eng-named:engineer",
                 "eng-wrong-model:engineer", "eng-no-session:engineer", "eng-old-session:engineer",
                 "eng-other-seat:engineer", "eng-ambiguous:engineer", "eng-last-model:engineer",
                 "eng-bare-route:engineer", "eng-no-model-change:engineer",
                 "eng-after-message:engineer", "eng-malformed-files:engineer"]
        pi_sessions = {
            "w1:p10": [session("eng-named", [{"type": "model_change", "provider": "prov", "modelId": "luna"}])],
            "w1:p11": [session("eng-wrong-model", [{"type": "model_change", "provider": "prov", "modelId": "other"}])],
            "w1:p13": [session(
                "eng-old-session", [{"type": "model_change", "provider": "prov", "modelId": "luna"}],
                (process_start - timedelta(seconds=1)).astimezone(timezone.utc).isoformat().replace("+00:00", "Z"),
            )],
            "w1:p14": [session("a-different-seat", [{"type": "model_change", "provider": "prov", "modelId": "luna"}])],
            "w1:p15": [
                session("eng-ambiguous", [{"type": "model_change", "provider": "prov", "modelId": "luna"}]),
                session("eng-ambiguous", [{"type": "model_change", "provider": "prov", "modelId": "flash"}]),
            ],
            "w1:p16": [session("eng-last-model", [
                {"type": "model_change", "provider": "prov", "modelId": "old"},
                {"type": "model_change", "provider": "prov", "modelId": "luna"},
            ])],
            "w1:p17": [session("eng-bare-route", [{"type": "model_change", "provider": "prov", "modelId": "luna"}])],
        }
        pi_sessions["w1:p12"] = []
        pi_sessions["w1:p19"] = [session("eng-no-model-change", [])]
        pi_sessions["w1:p20"] = [session("another-seat", [
            {"type": "message"},
            {"type": "session_info", "name": "eng-after-message"},
            {"type": "model_change", "provider": "prov", "modelId": "luna"},
        ], messages=False)]
        pi_sessions["w1:p21"] = [
            session("eng-malformed-files", [{"type": "model_change", "provider": "prov", "modelId": "luna"}]),
            "not-json\n",
            [],
        ]
        rc, lines, error = self._drift(
            agents, argv, seats, pi_sessions=pi_sessions, process_start=process_start
        )
        self.assertEqual((rc, error), (1, ""))
        expected_lines = [
            "w1:p3 eng-model pi DRIFT role=engineer running=pi --model prov/old "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p4 eng-kind claude DRIFT role=engineer running=claude --model claude-opus-5-5 "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p5 review-a agy UNVERIFIABLE role=reviewer reason=reviewer role args are missing",
            "w1:p7 eng-noargv pi UNVERIFIABLE role=engineer reason=no-named-session "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p8 review-noargv claude DRIFT role=reviewer running=claude --model - "
            "expected=agy --model -",
            "w1:p9 review-noargs agy UNVERIFIABLE role=reviewer reason=model-unavailable "
            "expected=agy --model -",
            "w1:p10 eng-named pi UNVERIFIABLE role=engineer reason=launch-argv-hidden "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p11 eng-wrong-model pi DRIFT role=engineer running=pi --model prov/other "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p12 eng-no-session pi DRIFT role=engineer running=pi --model prov/other "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p13 eng-old-session pi DRIFT role=engineer running=pi --model prov/other "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p14 eng-other-seat pi DRIFT role=engineer running=pi --model prov/other "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p15 eng-ambiguous pi DRIFT role=engineer running=pi --model prov/other "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p16 eng-last-model pi UNVERIFIABLE role=engineer reason=launch-argv-hidden "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p17 eng-bare-route pi UNVERIFIABLE role=engineer reason=launch-argv-hidden "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p19 eng-no-model-change pi UNVERIFIABLE role=engineer reason=no-named-session "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p20 eng-after-message pi UNVERIFIABLE role=engineer reason=no-named-session "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p21 eng-malformed-files pi DRIFT role=engineer running=pi --model prov/luna "
            "expected=pi --model prov/luna or pi --model prov/flash missing=--approve --model prov/luna --name eng-malformed-files",
        ]
        self.assertEqual(lines, expected_lines)
        bare_config = {**self._DRIFT_CONFIG, "engineer-fallback-args": ["--approve", "--model=luna"]}
        rc, lines, error = self._drift(
            [next(item for item in agents if item["name"] == "eng-bare-route")],
            argv, ["eng-bare-route:engineer"], config=bare_config,
            pi_sessions={"w1:p17": [session("eng-bare-route", [{"type": "model_change", "provider": "other", "modelId": "luna"}])]},
            process_start=process_start,
        )
        self.assertEqual((rc, error, lines), (1, "", [
            "w1:p17 eng-bare-route pi UNVERIFIABLE role=engineer reason=launch-argv-hidden "
            "expected=pi --model prov/luna or pi --model luna",
        ]))
        rc, lines, error = self._drift(agents[:5], argv, seats[:5])
        self.assertEqual((rc, error, lines), (1, "", expected_lines[:3]))
        reviewer_agent = agent("w1:p18", "review-unavailable", "agy")
        reviewer_process = {"w1:p18": {"argv0": "agy", "cwd": "/workspace", "pid": 812}}
        reviewer_config = {**self._DRIFT_CONFIG, "reviewer-args": ["--model", "review/model"]}
        rc, lines, error = self._drift(
            [reviewer_agent], reviewer_process, ["review-unavailable:reviewer"],
            config=reviewer_config,
        )
        self.assertEqual((rc, error, lines), (1, "", [
            "w1:p18 review-unavailable agy UNVERIFIABLE role=reviewer reason=model-unavailable "
            "expected=agy --model review/model",
        ]))

    def test_drift_reports_peer_settings_mismatch(self):
        config = {
            "reviewer-kind": "pi", "reviewer-args": ["--model", "review-model"],
            "launch-profiles": {"pi": {
                "seat-argv": [], "peer-argv": ["--settings", "{settings_file}"],
                "peer-settings-json": {"mode": "configured"},
            }},
        }
        seat = {"pane_id": "w1:p1", "name": "rev", "agent": "pi", "agent_status": "idle"}
        with tempfile.TemporaryDirectory() as directory:
            settings = roster.project_config.peer_settings_path(directory, "rev")
            process = {"w1:p1": ["pi", "--model", "review-model", "--settings", str(settings)]}
            settings.write_text('{"mode":"drifted"}', encoding="utf-8")
            listing = json.dumps({"result": {"agents": [seat]}})
            commands = []
            def run(command, **_kwargs):
                commands.append(command)
                if command[1:3] == ["agent", "list"]:
                    output = listing
                else:
                    output = json.dumps({"result": {"process_info": {"foreground_processes": [{"argv": process["w1:p1"]}]}}})
                return subprocess.CompletedProcess(command, 0, output, "")
            config["launch-profiles"]["pi"]["peer-settings-json"] = {"mode": "configured"}
            config_path = Path(directory) / "config.json"
            config_path.write_text(json.dumps(config), encoding="utf-8")
            output, error = io.StringIO(), io.StringIO()
            with mock.patch.object(roster.herdr_cli.subprocess, "run", side_effect=run), \
                    mock.patch("sys.stdout", output), mock.patch("sys.stderr", error):
                rc = roster.main(["--drift", str(config_path), "--seat", "rev:reviewer",
                                  "--run-dir", directory, "--lead", "lead-demo",
                                  "--installed-skill-dir", "/installed"])
        self.assertEqual((rc, error.getvalue()), (1, ""))
        self.assertEqual(output.getvalue(), "w1:p1 rev pi UNVERIFIABLE role=reviewer reason=settings-mismatch\n")

    def test_drift_requires_the_matched_routes_args_as_one_contiguous_block(self):
        config = {
            "engineer-kind": "claude",
            "engineer-args": ["--model", "m1", "--permission-mode", "auto"],
            "engineer-fallback": "pi",
            "engineer-fallback-args": ["--approve", "--model", "p1"],
            "launch-profiles": {
                "claude": {"seat-argv": [], "peer-argv": []},
                "pi": {"seat-argv": [], "peer-argv": []},
            },
        }
        launches = {
            "ok": ["claude", "--model", "m1", "--permission-mode", "auto"],
            "split": ["claude", "--model", "m1", "--permission-mode", "auto"],
            "absent": ["claude", "--model", "m1"],
            "fallback-ok": ["pi", "--approve", "--model", "p1", "--name", "x"],
            "fallback-missing": ["pi", "--model", "p1"],
        }
        agents = [
            {"pane_id": f"w1:p{i}", "name": name, "agent": argv[0], "agent_status": "idle"}
            for i, (name, argv) in enumerate(launches.items())
        ]
        argv_by_pane = {f"w1:p{i}": argv for i, argv in enumerate(launches.values())}
        rc, lines, error = self._drift(
            agents, argv_by_pane, [f"{name}:engineer" for name in launches], config
        )
        self.assertEqual((rc, error), (0, ""))
        want = "expected=claude --model m1 or pi --model p1 missing="
        self.assertEqual(lines, [
            "w1:p2 absent claude DRIFT role=engineer running=claude --model m1 "
            f"{want}--model m1 --permission-mode auto",
            "w1:p4 fallback-missing pi DRIFT role=engineer running=pi --model p1 "
            f"{want}--approve --model p1",
        ])

    def test_drift_uses_visible_args_to_distinguish_same_kind_and_model_routes(self):
        config = {
            "engineer-kind": "pi", "engineer-args": ["--model", "same", "--primary"],
            "engineer-fallback": "pi", "engineer-fallback-args": ["--model", "same", "--fallback"],
            "launch-profiles": {"pi": {"seat-argv": [], "peer-argv": []}},
        }
        agent = {"pane_id": "w1:p1", "name": "eng", "agent": "pi", "agent_status": "idle"}
        process = {"w1:p1": ["pi", "--model", "same", "--fallback"]}
        rc, lines, error = self._drift([agent], process, ["eng:engineer"], config)
        self.assertEqual((rc, lines, error), (0, [], ""))

    def test_drift_marks_ambiguous_model_alias_unverifiable(self):
        config = {
            "engineer-kind": "pi", "engineer-args": ["--model", "luna"],
            "engineer-fallback": "pi", "engineer-fallback-args": ["--model", "prov/luna"],
            "launch-profiles": {"pi": {"seat-argv": [], "peer-argv": []}},
        }
        seat = {"pane_id": "w1:p1", "name": "eng", "agent": "pi", "agent_status": "idle"}
        start = datetime(2026, 9, 26, 13).astimezone()
        timestamp = start.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
        process = {"w1:p1": {
            "argv0": "pi", "cwd": "/workspace", "name": "node", "pid": 14423,
        }}
        sessions = {"w1:p1": [[
            {"type": "session", "timestamp": timestamp},
            {"type": "session_info", "name": "eng"},
            {"type": "model_change", "provider": "prov", "modelId": "luna"},
            {"type": "message"},
        ]]}
        rc, lines, error = self._drift(
            [seat], process, ["eng:engineer"], config, pi_sessions=sessions, process_start=start,
        )
        self.assertEqual((rc, error), (1, ""))
        self.assertIn("UNVERIFIABLE role=engineer reason=route-ambiguous", lines[0])

    def test_drift_fails_closed_without_the_role_key_the_seat_process_or_the_seat(self):
        seat = [{"pane_id": "w1:p1", "name": "eng", "agent": "pi", "agent_status": "idle"}]
        pi, claude = {"w1:p1": ["pi"]}, {"w1:p1": ["claude", "--model", "x"]}
        cases = [
            ({"reviewer-kind": "agy"}, pi, "eng:engineer", (), "config lacks engineer-kind"),
            (self._DRIFT_CONFIG, claude, "eng:engineer", (), "no pi process in pane w1:p1"),
            (self._DRIFT_CONFIG, pi, "gone:engineer", (), "no live seat named gone"),
            (self._DRIFT_CONFIG, pi, "eng:engineer", ("--workspace", "w2"), "no live seat named eng"),
            (self._DRIFT_CONFIG, {"w1:p1": (1, "")}, "eng:engineer", (), "process-info w1:p1 failed"),
            (self._DRIFT_CONFIG, {"w1:p1": (0, "{}")}, "eng:engineer", (), "lacks foreground_processes"),
        ]
        for config, argv, name, extra_argv, message in cases:
            with self.subTest(message=message):
                rc, lines, error = self._drift(seat, argv, [name], config, extra_argv)
                self.assertEqual((rc, lines), (1, []))
                self.assertIn(message, error)
        pi_process = {"w1:p1": {"argv0": "pi", "cwd": "/workspace", "pid": 321}}
        rc, lines, error = self._drift(
            seat, pi_process, ["eng:engineer"], ps_result=(1, "")
        )
        self.assertEqual((rc, lines), (1, []))
        self.assertIn("pi process start for pid 321", error)


if __name__ == "__main__":
    unittest.main()
