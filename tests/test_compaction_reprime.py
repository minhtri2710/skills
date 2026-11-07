from __future__ import annotations

import io
import json
import os
import re
import shutil
import sys
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path
from unittest.mock import patch

import support
import backend
import compaction_reprime
import state_root
from fake_backend import FakeBackend

REFERENCES = support.ADW / "references"

OPEN_BACKEND = backend.open_backend


def setUpModule() -> None:
    support.never_run()


SEAT = "lead-beo-skills"
PI_SESSION = "01abc123"
CLAUDE_SESSION = "058a68e8-ce90-4eae-9624-2310cc7e832f"
ARGS = ["--run-id", "run-1", "--seat", SEAT]


class ReprimeCase(unittest.TestCase):
    """Runs the CLI against a FakeBackend and a temporary state root."""

    def setUp(self) -> None:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name).resolve()
        self.home = self.root / "home"
        self.project = self.root / "project"
        self.home.mkdir()
        self.project.mkdir()
        self.state = self.root / "state"
        self.fake = FakeBackend()
        self.agents: list[backend.Seat] = []
        self.roster_error: Exception | None = None
        self.prompt_outcome: Exception | None = None
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        for patcher in (
            patch.object(compaction_reprime.backend, "open_backend", return_value=self.fake),
            patch.object(state_root, "STATE_ROOT", self.state),
            patch.dict(os.environ, {"HOME": str(self.home)}),
            patch.object(sys, "stdout", self.stdout),
            patch.object(sys, "stderr", self.stderr),
        ):
            patcher.start()
            self.addCleanup(patcher.stop)

    @property
    def prompts(self) -> list[tuple[str, ...]]:
        """The recorded prompt operations, each ("prompt", seat, text)."""
        return [call for call in self.fake.calls if call[0] == "prompt"]

    def run_cli(self, *extra: str, args: list[str] | None = None) -> int:
        self.stdout.seek(0), self.stdout.truncate()
        self.stderr.seek(0), self.stderr.truncate()
        self.fake.script("list_seats", self.roster_error or self.agents)
        for agent in self.agents:
            self.fake.add_seat(agent.handle, name=agent.name, kind=agent.kind, cwd=agent.cwd)
        if self.prompt_outcome is not None:
            self.fake.script("prompt", self.prompt_outcome)
        return compaction_reprime.main((args or ARGS) + ["--project-root", str(self.project), *extra])

    def write_jsonl(self, path: Path, records: list[dict[str, object]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")

    def pi_path(self, session_id: str = PI_SESSION) -> Path:
        return self.home / ".pi" / "agent" / "sessions" / "--project--" / f"2026-09-21T10-00-00-000Z_{session_id}.jsonl"

    def pi_records(self, count: int, session_id: str = PI_SESSION) -> list[dict[str, object]]:
        header = {"type": "session", "version": 3, "id": session_id, "timestamp": "2026-09-21T10:00:00.000Z", "cwd": str(self.project)}
        return [header] + [self.pi_compaction(f"cmp{index}") for index in range(count)]

    def pi_compaction(self, record_id: str) -> dict[str, object]:
        return {
            "type": "compaction", "id": record_id, "parentId": "parent123", "timestamp": "2026-09-21T10:01:00.000Z",
            "summary": "summary", "firstKeptEntryId": "kept123", "tokensBefore": 100,
        }

    def set_pi(self, count: int, *, seat: str = SEAT, session_id: str = PI_SESSION, cwd: Path | None = None) -> None:
        path = self.pi_path(session_id)
        self.write_jsonl(path, self.pi_records(count, session_id))
        self.agents = [backend.Seat(
            handle=f"pane-{seat}", name=seat, kind="pi", cwd=str(cwd or self.project),
            session=backend.Session("path", str(path)),
        )]

    def claude_path(self, session_id: str = CLAUDE_SESSION) -> Path:
        key = re.sub(r"[^A-Za-z0-9]", "-", str(self.project))
        return self.home / ".claude" / "projects" / key / f"{session_id}.jsonl"

    def claude_records(self, pairs: int) -> list[dict[str, object]]:
        records: list[dict[str, object]] = []
        for index in range(pairs):
            records.append({
                "type": "system", "subtype": "compact_boundary", "uuid": f"boundary-{index}", "sessionId": CLAUDE_SESSION,
                "cwd": str(self.project), "compactMetadata": {"trigger": "auto"},
            })
            records.append({
                "type": "user", "isCompactSummary": True, "uuid": f"summary-{index}", "sessionId": CLAUDE_SESSION,
                "cwd": str(self.project),
            })
        return records

    def set_claude(self, records: list[dict[str, object]], session_id: str = CLAUDE_SESSION) -> None:
        self.write_jsonl(self.claude_path(session_id), records)
        self.agents = [backend.Seat(
            handle="pane-claude", name=SEAT, kind="claude", cwd=str(self.project),
            session=backend.Session("id", session_id),
        )]

    def records_dir(self) -> Path:
        return self.state / self.project.name.lower()

    def write_pointer_files(self, *, run_files: tuple[str, ...] = ("intake-record.md", "plan.md", "specification.md", "slices.json")) -> None:
        records = self.records_dir()
        records.mkdir(parents=True, exist_ok=True)
        for name in ("context-pack.md", "gates.md", "supervisor-notebook.md"):
            (records / name).write_text(f"RAW {name} BODY must not be copied", encoding="utf-8")
        run_dir = records / "runs" / "run-1"
        run_dir.mkdir(parents=True, exist_ok=True)
        for name in run_files:
            (run_dir / name).write_text(f"RAW {name} BODY must not be copied", encoding="utf-8")

    def state_files(self) -> list[Path]:
        return sorted((self.records_dir() / "runs" / "coordination").glob("*"))

    def baseline_then_cross(self, baseline: int = 3, crossed: int = 7) -> None:
        """First observation at `baseline` markers, then the file grows to `crossed`."""
        self.write_pointer_files()
        self.set_pi(baseline)
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual(self.prompts, [])
        self.set_pi(crossed)


class CliContractTest(ReprimeCase):
    def test_run_id_seat_and_project_root_are_required(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            compaction_reprime.main([])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("the following arguments are required", self.stderr.getvalue())

    def test_project_root_must_be_absolute(self) -> None:
        with self.assertRaises(SystemExit) as raised:
            compaction_reprime.main(ARGS + ["--project-root", "relative/project"])
        self.assertEqual(raised.exception.code, 2)
        self.assertIn("--project-root must be an absolute path", self.stderr.getvalue())
        self.assertEqual(self.prompts, [])

    def test_runs_from_any_cwd(self) -> None:
        self.baseline_then_cross()
        original = Path.cwd()
        with tempfile.TemporaryDirectory() as elsewhere:
            os.chdir(elsewhere)
            try:
                self.assertEqual(self.run_cli(), 0)
            finally:
                os.chdir(original)
        self.assertEqual(len(self.prompts), 1)
        self.assertIn(f"prompted {SEAT} at threshold 4", self.stdout.getvalue())


class SeatResolutionTest(ReprimeCase):
    def test_seat_resolves_by_name_or_pane_id_and_only_when_unique(self) -> None:
        self.write_pointer_files()
        self.set_pi(0)
        agent = self.agents[0]
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual(self.run_cli(args=["--run-id", "run-1", "--seat", f"pane-{SEAT}"]), 0)
        self.agents = [agent, replace(agent)]
        self.assertEqual(self.run_cli(), 1)
        self.agents = [agent]
        self.assertEqual(self.run_cli(args=["--run-id", "run-1", "--seat", "no-such-seat"]), 1)
        self.assertEqual(self.prompts, [])

    def test_a_seat_given_by_name_is_prompted_and_keyed_by_its_handle(self) -> None:
        self.baseline_then_cross()
        by_name = self.run_cli()
        by_handle = self.run_cli(args=["--run-id", "run-1", "--seat", f"pane-{SEAT}"])
        self.assertEqual((by_name, by_handle), (0, 0))
        self.assertEqual([prompt[1] for prompt in self.prompts], [f"pane-{SEAT}"])
        self.assertEqual(len(self.state_files()), 1)

    def test_unavailable_roster_fails_without_prompt(self) -> None:
        self.baseline_then_cross()
        self.roster_error = backend.BackendUnavailable("tool unavailable")
        self.assertEqual(self.run_cli(), 1)
        self.assertEqual(self.prompts, [])
        self.assertIn("live roster unavailable", self.stderr.getvalue())

    def test_a_seat_without_an_agent_session_fails_closed(self) -> None:
        self.write_pointer_files()
        self.set_pi(7)
        self.agents[0] = replace(self.agents[0], session=None)
        self.assertEqual(self.run_cli(), 1)
        self.assertIn("backend reports no agent session", self.stderr.getvalue())
        self.assertEqual(self.prompts, [])
        self.assertEqual(self.state_files(), [])

    def test_a_session_kind_the_agent_does_not_use_fails_closed(self) -> None:
        self.write_pointer_files()
        self.set_claude(self.claude_records(0))
        for kind, session in (("claude", backend.Session("path", "/x/a.jsonl")), ("pi", backend.Session("id", PI_SESSION))):
            with self.subTest(kind=kind):
                self.agents[0] = replace(self.agents[0], kind=kind, session=session)
                self.assertEqual(self.run_cli(), 1)
        self.assertEqual(self.state_files(), [])

    def test_the_backend_flag_reaches_detect_as_explicit(self) -> None:
        explicit = backend.Explicit("herdr", "w1:p1")
        stop = backend.DetectionError("stop")
        with patch.object(compaction_reprime.backend, "open_backend", wraps=OPEN_BACKEND) as opened, \
                patch.object(backend, "detect", side_effect=stop) as detect:
            self.assertEqual(self.run_cli("--backend", "herdr@w1:p1"), 1)
        detect.assert_called_once()
        self.assertEqual(detect.call_args.args[1], explicit)
        self.assertEqual(opened.call_args.args[1], explicit)
        self.assertIn("compaction_reprime: stop", self.stderr.getvalue())

    def test_the_state_root_is_the_one_state_root_module_patch(self) -> None:
        self.baseline_then_cross()
        self.assertEqual(self.run_cli(), 0)
        (state_file,) = self.state_files()
        self.assertTrue(state_file.is_relative_to(self.state))
        self.assertFalse((self.home / ".agent-delivery").exists())

    def test_roster_cwd_may_be_a_subdirectory_of_the_project_root(self) -> None:
        self.write_pointer_files()
        inside = self.project / "subdir"
        inside.mkdir()
        self.set_pi(3, cwd=inside)
        self.assertEqual(self.run_cli(), 0)
        self.set_pi(7, cwd=inside)
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual(len(self.prompts), 1)

    def test_roster_cwd_outside_project_root_is_refused_before_any_state_or_prompt(self) -> None:
        self.write_pointer_files()
        outside = self.root / "elsewhere"
        outside.mkdir()
        self.set_pi(3, cwd=outside)
        self.assertEqual(self.run_cli(), 1)
        self.set_pi(7, cwd=outside)
        self.assertEqual(self.run_cli(), 1)
        self.assertEqual(self.state_files(), [])
        self.assertEqual(self.prompts, [])


class MarkerCountingTest(ReprimeCase):
    def test_pi_counts_only_compaction_records_and_tolerates_a_partial_last_line(self) -> None:
        self.write_pointer_files()
        self.set_pi(0)
        self.assertEqual(self.run_cli(), 0)
        records = self.pi_records(4) + [{"type": "message", "id": "m1"}]
        self.write_jsonl(self.pi_path(), records)
        with self.pi_path().open("a", encoding="utf-8") as stream:
            stream.write('{"type":"assistant"')
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual(len(self.prompts), 1)

    def test_claude_counts_boundary_summary_pairs(self) -> None:
        self.write_pointer_files()
        self.set_claude(self.claude_records(0) + [{"type": "user", "sessionId": CLAUDE_SESSION}])
        self.assertEqual(self.run_cli(), 0)
        self.set_claude(self.claude_records(3))
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual(self.prompts, [])
        self.set_claude(self.claude_records(4))
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual(len(self.prompts), 1)

    def test_unverified_pi_evidence_fails_closed(self) -> None:
        self.write_pointer_files()
        valid = self.pi_records(1)
        cases = {
            "incomplete marker": [valid[0], {"type": "compaction"}],
            "duplicate marker id": valid + [valid[1]],
            "header id is another session": [{**valid[0], "id": "other-session"}, valid[1]],
            "malformed line": None,
        }
        for name, records in cases.items():
            with self.subTest(name):
                self.set_pi(0)
                if records is None:
                    self.pi_path().write_text("{not-json}\n", encoding="utf-8")
                else:
                    self.write_jsonl(self.pi_path(), records)
                self.assertEqual(self.run_cli(), 1)
                self.assertEqual(self.state_files(), [])
        self.assertEqual(self.prompts, [])

    def test_unverified_claude_evidence_fails_closed(self) -> None:
        self.write_pointer_files()
        pair = self.claude_records(1)
        boundary, summary = pair
        cases = {
            "boundary without summary": [boundary],
            "summary before boundary": [summary, boundary],
            "two boundaries": [boundary, boundary],
            "boundary without trigger": [{**boundary, "compactMetadata": {}}, summary],
            "summary from another session": [boundary, {**summary, "sessionId": "other"}],
            "summary reuses the boundary uuid": [boundary, {**summary, "uuid": boundary["uuid"]}],
        }
        for name, records in cases.items():
            with self.subTest(name):
                self.set_claude(records)
                self.assertEqual(self.run_cli(), 1)
                self.assertEqual(self.state_files(), [])
        self.assertEqual(self.prompts, [])

    def test_claude_storage_key_replaces_every_non_alphanumeric_of_the_project_path(self) -> None:
        self.project = self.root / "my_proj.v2"
        self.project.mkdir()
        self.write_pointer_files()
        self.set_claude(self.claude_records(0))
        self.assertEqual(self.run_cli(), 0)
        self.set_claude(self.claude_records(4))
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual(len(self.prompts), 1)

    def test_claude_session_id_cannot_escape_the_project_directory(self) -> None:
        self.write_pointer_files()
        self.set_claude(self.claude_records(0))
        outside = self.home / ".claude" / "projects" / "outside.jsonl"
        self.write_jsonl(outside, [])
        self.agents[0] = replace(self.agents[0], session=backend.Session("id", "../outside"))
        self.assertEqual(self.run_cli(), 1)
        self.assertEqual(self.state_files(), [])


class ThresholdTest(ReprimeCase):
    def test_first_observation_sets_the_baseline_and_sends_nothing(self) -> None:
        self.write_pointer_files()
        self.set_pi(9)
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual(self.prompts, [])
        self.assertIn(f"no newly crossed threshold for {SEAT}", self.stdout.getvalue())

    def test_only_markers_since_baseline_cross_the_first_threshold_of_four(self) -> None:
        self.write_pointer_files()
        self.set_pi(3)
        self.assertEqual(self.run_cli(), 0)
        self.set_pi(6)
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual(self.prompts, [])
        self.set_pi(7)
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual(len(self.prompts), 1)
        self.assertIn("prompted lead-beo-skills at threshold 4\n", self.stdout.getvalue())

    def test_each_crossed_threshold_prompts_once(self) -> None:
        self.baseline_then_cross(baseline=3, crossed=15)
        for expected in (4, 8, 12):
            with self.subTest(threshold=expected):
                self.assertEqual(self.run_cli(), 0)
                self.assertEqual(len(self.prompts), expected // 4)
                self.assertIn(f"at threshold {expected}", self.stdout.getvalue())
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual(len(self.prompts), 3)
        self.assertIn("no newly crossed threshold", self.stdout.getvalue())

    def test_state_is_one_file_per_seat_session_holding_baseline_and_sent_threshold(self) -> None:
        self.baseline_then_cross()
        self.assertEqual(self.run_cli(), 0)
        (state_file,) = self.state_files()
        self.assertEqual(json.loads(state_file.read_text(encoding="utf-8")), {"baseline": 3, "sent": 4})
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual(self.state_files(), [state_file])
        self.set_pi(8, session_id="02def456")
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual(len(self.state_files()), 2)

    def test_state_is_never_written_through_a_symlink(self) -> None:
        self.write_pointer_files()
        self.set_pi(3)
        outside = self.root / "outside"
        outside.mkdir()
        runs = self.records_dir() / "runs"
        coordination = runs / "coordination"
        self.assertEqual(self.run_cli(), 0)
        (state_file,) = self.state_files()
        state_name = state_file.name
        shutil.rmtree(coordination)

        def plant(case: str) -> None:
            if case == "coordination directory":
                coordination.symlink_to(outside, target_is_directory=True)
                return
            coordination.mkdir()
            if case == "state file":
                (coordination / state_name).symlink_to(outside / "state.json")
            else:
                (coordination / state_name.replace(".json", ".tmp")).symlink_to(outside / "tmp.json")

        for case, returncode in (("coordination directory", 1), ("state file", 1), ("temporary file", 0)):  # a planted fixed temp name is never used
            with self.subTest(case):
                plant(case)
                try:
                    self.assertEqual(self.run_cli(), returncode)
                    self.assertEqual(list(outside.iterdir()), [])
                finally:
                    if coordination.is_symlink():
                        coordination.unlink()
                    else:
                        shutil.rmtree(coordination)
                    for leftover in outside.iterdir():
                        leftover.unlink()

    def test_a_new_session_or_seat_starts_its_own_baseline(self) -> None:
        self.baseline_then_cross()
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual(len(self.prompts), 1)
        self.set_pi(8, session_id="02def456")
        self.assertEqual(self.run_cli(), 0)
        self.set_pi(8, seat="other-seat", session_id="02def456")
        self.assertEqual(self.run_cli(args=["--run-id", "run-1", "--seat", "other-seat"]), 0)
        self.assertEqual(len(self.prompts), 1)
        self.assertEqual(len(self.state_files()), 3)

    def test_unreadable_or_regressed_state_fails_closed(self) -> None:
        self.baseline_then_cross()
        (state_file,) = self.state_files()
        for body in ("{not-json}\n", '{"baseline": "3", "sent": 0}', '{"baseline": 3, "sent": true}', "[]", '{"baseline": 9, "sent": 0}'):
            with self.subTest(body=body):
                state_file.write_text(body, encoding="utf-8")
                self.assertEqual(self.run_cli(), 1)
        self.assertEqual(self.prompts, [])


class PromptTest(ReprimeCase):
    def test_relaunch_is_recommended_from_eight_markers_since_baseline(self) -> None:
        self.baseline_then_cross(baseline=3, crossed=15)
        lead = REFERENCES / "lead.md"
        for threshold in (4, 8, 12):
            with self.subTest(threshold=threshold):
                self.assertEqual(self.run_cli(), 0)
                block = self.prompts[-1][2]
                if threshold == 4:
                    self.assertNotIn("relaunch-recommended", block)
                    self.assertEqual(self.stdout.getvalue(), f"compaction_reprime: prompted {SEAT} at threshold 4\n")
                else:
                    self.assertEqual(
                        block.split("\n")[-1],
                        f"relaunch-recommended: {threshold} compactions since baseline; at the next slice boundary: {lead}#Relaunch and doctrine",
                    )
                    self.assertEqual(
                        self.stdout.getvalue(),
                        f"compaction_reprime: prompted {SEAT} at threshold {threshold}; relaunch recommended at the next slice boundary\n",
                    )

    def test_prompt_is_one_prompt_operation_of_pointers_only(self) -> None:
        self.baseline_then_cross()
        self.assertEqual(self.run_cli(), 0)
        ((operation, seat, block),) = self.prompts
        self.assertEqual((operation, seat), ("prompt", f"pane-{SEAT}"))
        records, run_dir = self.records_dir(), self.records_dir() / "runs" / "run-1"
        for pointer in (
            records / "context-pack.md", records / "gates.md", records / "supervisor-notebook.md", run_dir,
            run_dir / "intake-record.md", run_dir / "plan.md", run_dir / "specification.md", run_dir / "slices.json",
            f"{REFERENCES / 'lead.md'}#Recovery", f"{REFERENCES / 'lead.md'}#Delivery sequence",
            f"{REFERENCES / 'lead.md'}#Gates and ledger", f"{REFERENCES / 'supervisor.md'}#Handoff",
            f"{REFERENCES / 'closeout.md'}#Acceptance custody",
        ):
            self.assertIn(str(pointer), block)
        self.assertNotIn("RAW", block)
        self.assertIn(f"run-id: run-1\nseat: {SEAT}\n", block)

    def test_run_records_absent_from_the_run_directory_are_not_pointed_at(self) -> None:
        self.write_pointer_files(run_files=("intake-record.md",))
        self.set_pi(3)
        self.assertEqual(self.run_cli(), 0)
        self.set_pi(7)
        self.assertEqual(self.run_cli(), 0)
        block = self.prompts[0][2]
        self.assertIn("\nintake: ", block)
        for label in ("plan", "specification", "slices"):
            self.assertNotIn(f"\n{label}:", block)

    def test_named_doctrine_sections_exist(self) -> None:
        self.baseline_then_cross()
        self.assertEqual(self.run_cli(), 0)
        for pointer in re.findall(r"^[a-z-]+: (/\S+\.md)#(.+)$", self.prompts[0][2], re.MULTILINE):
            path, section = pointer
            with self.subTest(section=section):
                self.assertRegex(Path(path).read_text(encoding="utf-8"), rf"(?m)^#{{1,4}} {re.escape(section)}\s*$")

    def test_failed_or_unavailable_prompt_leaves_the_threshold_unsent_and_the_next_run_retries(self) -> None:
        for outcome in (backend.SeatError("blocked", "agent blocked"), backend.BackendUnavailable("tool unavailable")):
            with self.subTest(outcome=outcome):
                self.fake.calls.clear()
                self.baseline_then_cross()
                self.prompt_outcome = outcome
                self.assertEqual(self.run_cli(), 1)
                self.assertEqual(len(self.prompts), 1)
                self.assertIn("prompt failed", self.stderr.getvalue())
                self.prompt_outcome = None
                self.assertEqual(self.run_cli(), 0)
                self.assertEqual(len(self.prompts), 2)
                self.assertIn("at threshold 4", self.stdout.getvalue())
                self.assertEqual(self.run_cli(), 0)
                self.assertEqual(len(self.prompts), 2)
                for state_file in self.state_files():
                    state_file.unlink()

    def test_missing_pointer_file_sends_nothing_and_the_threshold_stays_pending(self) -> None:
        self.baseline_then_cross()
        (self.records_dir() / "context-pack.md").unlink()
        self.assertEqual(self.run_cli(), 1)
        self.assertEqual(self.prompts, [])
        self.assertIn("threshold 4 remains pending", self.stderr.getvalue())
        (self.records_dir() / "context-pack.md").write_text("pack", encoding="utf-8")
        self.assertEqual(self.run_cli(), 0)
        self.assertEqual(len(self.prompts), 1)

    def test_run_id_cannot_escape_the_runs_directory(self) -> None:
        self.baseline_then_cross()
        (self.records_dir() / "outside").mkdir()
        self.assertEqual(self.run_cli(args=["--run-id", "../outside", "--seat", SEAT]), 1)
        self.assertEqual(self.prompts, [])


if __name__ == "__main__":
    unittest.main()
