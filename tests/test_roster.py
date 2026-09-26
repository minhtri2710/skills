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

    def test_default_runs_agent_list_even_with_empty_nontty_stdin(self):
        # The live path: an agent's Bash gives an empty non-tty stdin. Without
        # --stdin the script must ignore stdin and run `herdr agent list`.
        completed = subprocess.CompletedProcess(
            args=["herdr", "agent", "list"], returncode=0, stdout=self._SAMPLE, stderr=""
        )
        with mock.patch.object(roster.herdr_cli.subprocess, "run", return_value=completed) as run, \
                mock.patch.object(roster.sys, "stdin", io.StringIO("")):
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
        ), mock.patch.object(roster.sys, "stdin", io.StringIO("")):
            error = io.StringIO()
            with mock.patch("sys.stdout", io.StringIO()), mock.patch("sys.stderr", error):
                rc = roster.main([])
        self.assertEqual(rc, 1)
        self.assertIn("could not run herdr agent list", error.getvalue())

    def test_stdin_flag_reads_stdin_and_skips_subprocess(self):
        with mock.patch.object(roster.herdr_cli.subprocess, "run") as run, \
                mock.patch.object(roster.sys, "stdin", io.StringIO(self._SAMPLE)), \
                mock.patch("sys.stdout", io.StringIO()), mock.patch("sys.stderr", io.StringIO()):
            rc = roster.main(["--stdin", "--workspace", "w1"])
        self.assertEqual(rc, 0)
        run.assert_not_called()

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
            with mock.patch.object(roster.sys, "stdin", io.StringIO(json.dumps(payload))):
                output = io.StringIO()
                with mock.patch("sys.stdout", output):
                    rc = roster.main([
                        "--stdin", "--stalled", "--workspace", "w1",
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
            with mock.patch.object(roster.sys, "stdin", io.StringIO(json.dumps(payload))):
                output = io.StringIO()
                with mock.patch("sys.stdout", output):
                    rc = roster.main([
                        "--stdin", "--never-started", "peer-1", "--workspace", "w1",
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
            with mock.patch.object(roster.sys, "stdin", io.StringIO(json.dumps(payload))):
                output = io.StringIO()
                with mock.patch("sys.stdout", output):
                    rc = roster.main([
                        "--stdin", "--never-started", "peer-1",
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
            with mock.patch.object(roster.sys, "stdin", io.StringIO(json.dumps(payload))):
                output = io.StringIO()
                with mock.patch("sys.stdout", output):
                    rc = roster.main([
                        "--stdin", "--never-started", "peer-1",
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
            with mock.patch.object(roster.sys, "stdin", io.StringIO(json.dumps(payload))):
                output = io.StringIO()
                with mock.patch("sys.stdout", output):
                    rc = roster.main([
                        "--stdin", "--stalled", "--peer", f"peer-1:{report}:{progress}",
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
            with mock.patch.object(roster.sys, "stdin", io.StringIO(json.dumps(payload))):
                output = io.StringIO()
                with mock.patch("sys.stdout", output):
                    rc = roster.main([
                        "--stdin", "--stalled", "--peer", f"peer-1:{report}:{progress}",
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

    _DRIFT_CONFIG = (
        "# Delivery config\n"
        "- engineer-kind: pi\n"
        "- engineer-args: --approve --model prov/luna\n"
        "- engineer-fallback: pi\n"
        "- engineer-fallback-args: --approve --model=prov/flash\n"
        "- reviewer-kind: agy\n"
        "<!-- restore after the override:\n"
        "- engineer-kind: claude\n"
        "- engineer-args: --model claude-opus-5-5\n"
        "-->\n"
    )

    def _drift(
        self, agents, argv_by_pane, seats, config=_DRIFT_CONFIG, extra_argv=(),
        pi_sessions=None, process_start=None, ps_result=(0, None),
    ):
        """Drive main() with isolated pi sessions and mocked process commands."""
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
            config_path = root / "config.md"
            config_path.write_text(config, encoding="utf-8")
            agent_dir = root / "pi-agent"
            for pane, files in (pi_sessions or {}).items():
                process = argv_by_pane[pane]
                cwd = process.get("cwd", "/workspace") if isinstance(process, dict) else "/workspace"
                slug = cwd.removeprefix("/").replace("/", "-").replace(":", "-")
                session_dir = agent_dir / "sessions" / f"--{slug}--"
                session_dir.mkdir(parents=True, exist_ok=True)
                for index, entries in enumerate(files):
                    path = session_dir / f"{pane.replace(':', '-')}-{index}.jsonl"
                    path.write_text("".join(json.dumps(entry) + "\n" for entry in entries), encoding="utf-8")
            output, error = io.StringIO(), io.StringIO()
            with mock.patch.object(roster.herdr_cli.subprocess, "run", side_effect=run), \
                    mock.patch.dict(os.environ, {"PI_CODING_AGENT_DIR": str(agent_dir)}), \
                    mock.patch.object(roster.sys, "stdin", io.StringIO("")), \
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
        ]
        argv = {
            "w1:p1": ["node", "/opt/bin/pi", "--approve", "--model", "prov/luna", "--no-skills"],
            "w1:p2": ["pi", "--model", "prov/flash"],
            "w1:p3": ["pi", "--model", "prov/old"],
            "w1:p4": {
                "argv0": "claude",
                "argv": ["claude", "--model", "claude-opus-5-5", "--effort", "low"],
                "cwd": "/Users/beowulf/Work/beo-skills",
                "name": "2.1.283",
                "pid": 6753,
            },
            "w1:p5": ["agy", "--dangerously-skip-permissions"],
            "w1:p9": {"argv0": "agy", "cwd": "/tmp", "name": "agy", "pid": 100},
            "w1:p7": {
                "argv0": "pi", "cwd": "/Users/beowulf/Work/beo-skills",
                "name": "node", "pid": 14423,
            },
            "w1:p8": {"argv0": "claude", "cwd": "/tmp", "name": "node", "pid": 99},
            "w1:p10": {"argv0": "pi", "cwd": "/workspace:project", "name": "node", "pid": 14410},
            **{
                f"w1:p{i}": {
                    "argv0": "pi", "cwd": "/workspace/project", "name": "node", "pid": 14400 + i,
                }
                for i in range(11, 18)
            },
            "w1:p19": {"argv0": "pi", "cwd": "/workspace/project", "name": "node", "pid": 14419},
        }
        seats = ["eng-primary:engineer", "eng-fallback:engineer", "eng-model:engineer",
                 "eng-kind:engineer", "review-a:reviewer", "eng-noargv:engineer",
                 "review-noargv:reviewer", "review-noargs:reviewer", "eng-named:engineer",
                 "eng-wrong-model:engineer", "eng-no-session:engineer", "eng-old-session:engineer",
                 "eng-other-seat:engineer", "eng-ambiguous:engineer", "eng-last-model:engineer",
                 "eng-bare-route:engineer", "eng-no-model-change:engineer"]
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
        rc, lines, error = self._drift(
            agents, argv, seats, pi_sessions=pi_sessions, process_start=process_start
        )
        self.assertEqual((rc, error), (1, ""))
        expected_lines = [
            "w1:p3 eng-model pi DRIFT role=engineer running=pi --model prov/old "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p4 eng-kind claude DRIFT role=engineer running=claude --model claude-opus-5-5 "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p7 eng-noargv pi UNVERIFIABLE role=engineer reason=no-named-session "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p8 review-noargv claude DRIFT role=reviewer running=claude --model - "
            "expected=agy --model -",
            "w1:p11 eng-wrong-model pi DRIFT role=engineer running=pi --model prov/other "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p12 eng-no-session pi UNVERIFIABLE role=engineer reason=no-named-session "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p13 eng-old-session pi UNVERIFIABLE role=engineer reason=no-named-session "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p14 eng-other-seat pi UNVERIFIABLE role=engineer reason=no-named-session "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p15 eng-ambiguous pi UNVERIFIABLE role=engineer reason=ambiguous-session "
            "expected=pi --model prov/luna or pi --model prov/flash",
            "w1:p19 eng-no-model-change pi UNVERIFIABLE role=engineer reason=no-named-session "
            "expected=pi --model prov/luna or pi --model prov/flash",
        ]
        self.assertEqual(lines, expected_lines)
        bare_config = self._DRIFT_CONFIG.replace(
            "- engineer-fallback-args: --approve --model=prov/flash",
            "- engineer-fallback-args: --approve --model=luna",
        )
        rc, lines, error = self._drift(
            [next(item for item in agents if item["name"] == "eng-bare-route")],
            argv, ["eng-bare-route:engineer"], config=bare_config,
            pi_sessions={"w1:p17": [session("eng-bare-route", [{"type": "model_change", "provider": "other", "modelId": "luna"}])]},
            process_start=process_start,
        )
        self.assertEqual((rc, error, lines), (0, "", []))
        rc, lines, error = self._drift(agents[:5], argv, seats[:5])
        self.assertEqual((rc, error, lines), (0, "", expected_lines[:2]))
        reviewer_agent = agent("w1:p18", "review-unavailable", "agy")
        reviewer_process = {"w1:p18": {"argv0": "agy", "cwd": "/workspace", "pid": 812}}
        reviewer_config = self._DRIFT_CONFIG + "- reviewer-args: --model review/model\n"
        rc, lines, error = self._drift(
            [reviewer_agent], reviewer_process, ["review-unavailable:reviewer"],
            config=reviewer_config,
        )
        self.assertEqual((rc, error, lines), (1, "", [
            "w1:p18 review-unavailable agy UNVERIFIABLE role=reviewer reason=model-unavailable "
            "expected=agy --model review/model",
        ]))

    def test_drift_fails_closed_without_the_role_key_the_seat_process_or_the_seat(self):
        seat = [{"pane_id": "w1:p1", "name": "eng", "agent": "pi", "agent_status": "idle"}]
        pi, claude = {"w1:p1": ["pi"]}, {"w1:p1": ["claude", "--model", "x"]}
        cases = [
            ("- reviewer-kind: agy\n", pi, "eng:engineer", (), "config lacks engineer-kind"),
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
