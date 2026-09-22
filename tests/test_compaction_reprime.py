from __future__ import annotations

import importlib.util
import io
import os
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPTS = Path(__file__).parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
SCRIPT = SCRIPTS / "compaction_reprime.py"
sys.path.insert(0, str(SCRIPTS))
SPEC = importlib.util.spec_from_file_location("compaction_reprime", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
compaction_reprime = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = compaction_reprime
SPEC.loader.exec_module(compaction_reprime)


def _guard_unpatched_subprocess_run(command: object, *args: object, **kwargs: object) -> None:
    argv = command if isinstance(command, (list, tuple)) else ()
    if argv and argv[0] == "herdr":
        raise AssertionError("live herdr subprocess must be patched in this test")
    raise AssertionError("unexpected unpatched subprocess.run in this test")


def _install_subprocess_guard(test_case: unittest.TestCase) -> None:
    guard = patch.object(compaction_reprime.herdr_cli.subprocess, "run", side_effect=_guard_unpatched_subprocess_run)
    guard.start()
    test_case.addCleanup(guard.stop)


class CompactionReprimeObserverTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.home = self.root / "home"
        self.project = self.root / "project"
        self.home.mkdir()
        self.project.mkdir()
        _install_subprocess_guard(self)
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        self._stdout_patch = patch.object(sys, "stdout", self.stdout)
        self._stderr_patch = patch.object(sys, "stderr", self.stderr)
        self._stdout_patch.start()
        self._stderr_patch.start()
        self.addCleanup(self._stderr_patch.stop)
        self.addCleanup(self._stdout_patch.stop)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_jsonl(self, path: Path, records: list[dict[str, object]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")

    def roster(
        self,
        *,
        kind: str,
        path: Path | None = None,
        session_id: str | None = None,
        seat: str = "lead-beo-skills",
        pane_id: str = "w2Q:pA",
    ) -> list[dict[str, object]]:
        session: dict[str, object]
        if kind == "pi":
            session = {"source": "herdr:pi", "agent": "pi", "kind": "path", "value": str(path)}
        else:
            session = {"source": "herdr:claude", "agent": "claude", "kind": "id", "value": session_id}
        return [{
            "name": seat,
            "pane_id": pane_id,
            "agent": kind,
            "cwd": str(self.project),
            "agent_session": session,
        }]

    def pi_path(self, session_id: str = "01abc123") -> Path:
        return self.home / ".pi" / "agent" / "sessions" / "--project--" / f"2026-09-21T10-00-00-000Z_{session_id}.jsonl"

    def pi_header(self) -> dict[str, object]:
        return {
            "type": "session",
            "version": 3,
            "id": "01abc123",
            "timestamp": "2026-09-21T10:00:00.000Z",
            "cwd": str(self.project),
        }

    def pi_compaction(self, record_id: str = "cmp123") -> dict[str, object]:
        return {
            "type": "compaction",
            "id": record_id,
            "parentId": "parent123",
            "timestamp": "2026-09-21T10:01:00.000Z",
            "summary": "summary",
            "firstKeptEntryId": "kept123",
            "tokensBefore": 100,
        }

    def test_pi_counts_only_verified_compaction_records(self) -> None:
        path = self.pi_path()
        self.write_jsonl(path, [self.pi_header(), self.pi_compaction(), self.pi_compaction("cmp456")])
        self.assertEqual(
            compaction_reprime.observe_live_seat(
                self.roster(kind="pi", path=path),
                "lead-beo-skills",
                project_root=self.project,
                home_dir=self.home,
            ),
            2,
        )

    def test_pi_valid_records_survive_one_partial_trailing_line(self) -> None:
        path = self.pi_path()
        self.write_jsonl(path, [self.pi_header(), self.pi_compaction()])
        with path.open("a", encoding="utf-8") as stream:
            stream.write('{"type":"assistant"')
        self.assertEqual(
            compaction_reprime.observe_live_seat(
                self.roster(kind="pi", path=path),
                "lead-beo-skills",
                project_root=self.project,
                home_dir=self.home,
            ),
            1,
        )

    def test_pi_malformed_incomplete_or_mismatched_evidence_fails_closed(self) -> None:
        path = self.pi_path()
        cases = [
            [self.pi_header(), {"type": "compaction"}],
            [self.pi_header(), self.pi_compaction(), self.pi_compaction()],
            [{**self.pi_header(), "id": "other-session"}, self.pi_compaction()],
            [self.pi_header(), {**self.pi_compaction(), "cwd": str(self.root / "other")}],
        ]
        for records in cases:
            with self.subTest(records=records):
                self.write_jsonl(path, records)
                self.assertEqual(
                    compaction_reprime.observe_live_seat(
                        self.roster(kind="pi", path=path),
                        "lead-beo-skills",
                        project_root=self.project,
                        home_dir=self.home,
                    ),
                    0,
                )
        path.write_text("{not-json}\n", encoding="utf-8")
        self.assertEqual(
            compaction_reprime.observe_live_seat(
                self.roster(kind="pi", path=path),
                "lead-beo-skills",
                project_root=self.project,
                home_dir=self.home,
            ),
            0,
        )

    def test_claude_counts_boundary_summary_pairs_in_order(self) -> None:
        session_id = "058a68e8-ce90-4eae-9624-2310cc7e832f"
        project_key = "-" + str(self.project.resolve()).lstrip("/").replace("/", "-")
        path = self.home / ".claude" / "projects" / project_key / f"{session_id}.jsonl"
        boundary = {
            "type": "system",
            "subtype": "compact_boundary",
            "uuid": "e6ea46d6-901c-49e5-920a-10d06f333ef6",
            "sessionId": session_id,
            "cwd": str(self.project),
            "compactMetadata": {"trigger": "auto"},
        }
        summary = {
            "type": "user",
            "isCompactSummary": True,
            "uuid": "85ef7c32-1265-4a00-9395-0af4b3171f3e",
            "sessionId": session_id,
            "cwd": str(self.project),
        }
        self.write_jsonl(path, [boundary, summary, {**boundary, "uuid": "fa54338c-1c77-4eae-9624-2310cc7e832f"}, {**summary, "uuid": "b09c0db6-ec20-4036-8289-7dacd32e7e25"}])
        self.assertEqual(
            compaction_reprime.observe_live_seat(
                self.roster(kind="claude", session_id=session_id),
                "lead-beo-skills",
                project_root=self.project,
                home_dir=self.home,
            ),
            2,
        )

    def test_claude_session_cwd_may_change_within_project_root(self) -> None:
        session_id = "058a68e8-ce90-4eae-9624-2310cc7e832f"
        project_key = "-" + str(self.project.resolve()).lstrip("/").replace("/", "-")
        path = self.home / ".claude" / "projects" / project_key / f"{session_id}.jsonl"
        subdirectory = self.project / "subdir"
        subdirectory.mkdir()
        boundary = {
            "type": "system",
            "subtype": "compact_boundary",
            "uuid": "e6ea46d6-901c-49e5-920a-10d06f333ef6",
            "sessionId": session_id,
            "cwd": str(subdirectory),
            "compactMetadata": {"trigger": "auto"},
        }
        summary = {
            "type": "user",
            "isCompactSummary": True,
            "uuid": "85ef7c32-1265-4a00-9395-0af4b3171f3e",
            "sessionId": session_id,
            "cwd": str(self.project),
        }
        self.write_jsonl(path, [boundary, summary])
        self.assertEqual(
            compaction_reprime.observe_live_seat(
                self.roster(kind="claude", session_id=session_id),
                "lead-beo-skills",
                project_root=self.project,
                home_dir=self.home,
            ),
            1,
        )

    def test_claude_missing_or_ambiguous_companion_fails_closed(self) -> None:
        session_id = "058a68e8-ce90-4eae-9624-2310cc7e832f"
        project_key = "-" + str(self.project.resolve()).lstrip("/").replace("/", "-")
        path = self.home / ".claude" / "projects" / project_key / f"{session_id}.jsonl"
        boundary = {
            "type": "system",
            "subtype": "compact_boundary",
            "uuid": "e6ea46d6-901c-49e5-920a-10d06f333ef6",
            "sessionId": session_id,
            "cwd": str(self.project),
            "compactMetadata": {"trigger": "auto"},
        }
        summary = {
            "type": "user",
            "isCompactSummary": True,
            "uuid": "85ef7c32-1265-4eae-9624-2310cc7e832f",
            "sessionId": session_id,
            "cwd": str(self.project),
        }
        for records in ([boundary], [summary, boundary], [boundary, boundary], [{**boundary, "compactMetadata": {}} , summary], [boundary, {**summary, "sessionId": "other"}], [boundary, {**summary, "uuid": boundary["uuid"]}]):
            with self.subTest(records=records):
                self.write_jsonl(path, records)
                self.assertEqual(
                    compaction_reprime.observe_live_seat(
                        self.roster(kind="claude", session_id=session_id),
                        "lead-beo-skills",
                        project_root=self.project,
                        home_dir=self.home,
                    ),
                    0,
                )

    def test_resolution_rejects_ambiguous_or_path_escaping_roster_evidence(self) -> None:
        path = self.pi_path()
        self.write_jsonl(path, [self.pi_header()])
        roster = self.roster(kind="pi", path=path)
        self.assertIsNotNone(compaction_reprime.resolve_live_session(roster, "lead-beo-skills", project_root=self.project, home_dir=self.home))
        self.assertIsNone(compaction_reprime.resolve_live_session(roster + roster, "lead-beo-skills", project_root=self.project, home_dir=self.home))
        escaping = self.roster(kind="pi", path=self.root / "outside.jsonl")
        self.assertIsNone(compaction_reprime.resolve_live_session(escaping, "lead-beo-skills", project_root=self.project, home_dir=self.home))
        self.assertEqual(
            compaction_reprime.observe_live_seat(roster, "../other", project_root=self.project, home_dir=self.home),
            0,
        )

    def test_symlinked_session_root_and_file_are_rejected(self) -> None:
        outside_root = self.root / "outside-sessions"
        outside_root.mkdir()
        symlinked_root = self.home / ".pi" / "agent" / "sessions"
        symlinked_root.parent.mkdir(parents=True, exist_ok=True)
        symlinked_root.symlink_to(outside_root, target_is_directory=True)
        self.assertIsNone(
            compaction_reprime.resolve_live_session(
                self.roster(kind="pi", path=outside_root / "2026-09-21T10-00-00-000Z_01abc123.jsonl"),
                "lead-beo-skills",
                project_root=self.project,
                home_dir=self.home,
            )
        )

        symlinked_root.unlink()
        outside = self.root / "outside.jsonl"
        outside.write_text(json.dumps(self.pi_header()) + "\n" + json.dumps(self.pi_compaction()) + "\n", encoding="utf-8")
        path = self.pi_path()
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(outside)
        self.assertEqual(
            compaction_reprime.observe_live_seat(
                self.roster(kind="pi", path=path),
                "lead-beo-skills",
                project_root=self.project,
                home_dir=self.home,
            ),
            0,
        )

    def test_observer_does_not_prompt_or_write_state(self) -> None:
        path = self.pi_path()
        self.write_jsonl(path, [self.pi_header(), self.pi_compaction()])
        before = sorted(str(item.relative_to(self.home)) for item in self.home.rglob("*") if item.is_file())
        with patch.object(compaction_reprime.herdr_cli.subprocess, "run", side_effect=AssertionError("observer must not invoke commands")):
            self.assertEqual(
                compaction_reprime.observe_live_seat(
                    self.roster(kind="pi", path=path),
                    "lead-beo-skills",
                    project_root=self.project,
                    home_dir=self.home,
                ),
                1,
            )
        after = sorted(str(item.relative_to(self.home)) for item in self.home.rglob("*") if item.is_file())
        self.assertEqual(after, before)


class CompactionReprimeBaselineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.home = self.root / "home"
        self.project = self.root / "project"
        self.home.mkdir()
        self.project.mkdir()
        _install_subprocess_guard(self)
        self.stdout = io.StringIO()
        self.stderr = io.StringIO()
        self._stdout_patch = patch.object(sys, "stdout", self.stdout)
        self._stderr_patch = patch.object(sys, "stderr", self.stderr)
        self._stdout_patch.start()
        self._stderr_patch.start()
        self.addCleanup(self._stderr_patch.stop)
        self.addCleanup(self._stdout_patch.stop)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def write_jsonl(self, path: Path, records: list[dict[str, object]]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("".join(json.dumps(record) + "\n" for record in records), encoding="utf-8")

    def pi_path(self, session_id: str = "01abc123") -> Path:
        return self.home / ".pi" / "agent" / "sessions" / "--project--" / f"2026-09-21T10-00-00-000Z_{session_id}.jsonl"

    def pi_header(self, session_id: str = "01abc123") -> dict[str, object]:
        return {
            "type": "session",
            "version": 3,
            "id": session_id,
            "timestamp": "2026-09-21T10:00:00.000Z",
            "cwd": str(self.project),
        }

    def pi_compaction(self, record_id: str) -> dict[str, object]:
        return {
            "type": "compaction",
            "id": record_id,
            "parentId": "parent123",
            "timestamp": "2026-09-21T10:01:00.000Z",
            "summary": "summary",
            "firstKeptEntryId": "kept123",
            "tokensBefore": 100,
        }

    def roster(self, path: Path, *, seat: str = "lead-beo-skills") -> list[dict[str, object]]:
        return [{
            "name": seat,
            "pane_id": f"pane-{seat}",
            "agent": "pi",
            "cwd": str(self.project),
            "agent_session": {
                "source": "herdr:pi",
                "agent": "pi",
                "kind": "path",
                "value": str(path),
            },
        }]

    def write_pi_count(self, path: Path, count: int, *, session_id: str = "01abc123") -> None:
        self.write_jsonl(
            path,
            [self.pi_header(session_id)] + [self.pi_compaction(f"cmp{index}") for index in range(count)],
        )

    def track(self, path: Path, *, seat: str = "lead-beo-skills", run_id: str = "run-1"):
        return compaction_reprime.track_live_seat(
            self.roster(path, seat=seat),
            seat,
            run_id=run_id,
            project_root=self.project,
            home_dir=self.home,
        )

    def state_path(self, seat: str = "lead-beo-skills") -> Path:
        digest = __import__("hashlib").sha256(seat.encode("utf-8")).hexdigest()
        return self.home / ".herdr" / "projects" / "project" / "runs" / "coordination" / f"baseline-{digest}.json"

    def test_first_observation_initializes_without_eligibility_and_reloads(self) -> None:
        path = self.pi_path()
        self.write_pi_count(path, 3)
        first = self.track(path)
        self.assertIsNotNone(first)
        assert first is not None
        self.assertEqual(first.baseline_count, 3)
        self.assertEqual(first.observed_count, 3)
        self.assertEqual(first.newly_observed, 0)
        self.assertIsNone(first.newly_eligible_threshold)
        self.assertIsNone(first.pending_threshold)
        self.assertEqual(first.next_threshold, 4)
        self.assertEqual(first.state_path.parent.resolve(), self.state_path().parent.resolve())
        self.assertEqual(json.loads(first.state_path.read_text(encoding="utf-8"))["schema_version"], 1)

        reloaded = self.track(path, run_id="run-2")
        self.assertIsNotNone(reloaded)
        assert reloaded is not None
        self.assertEqual(reloaded.baseline_count, 3)
        self.assertEqual(reloaded.observed_count, 3)
        self.assertEqual(reloaded.newly_observed, 0)
        self.assertIsNone(reloaded.newly_eligible_threshold)

    def test_only_newly_observed_markers_cross_threshold_four(self) -> None:
        path = self.pi_path()
        self.write_pi_count(path, 3)
        self.assertIsNotNone(self.track(path))

        self.write_pi_count(path, 6)
        crossed = self.track(path)
        self.assertIsNotNone(crossed)
        assert crossed is not None
        self.assertEqual(crossed.newly_observed, 3)
        self.assertIsNone(crossed.newly_eligible_threshold)

        self.write_pi_count(path, 7)
        crossed = self.track(path)
        self.assertIsNotNone(crossed)
        assert crossed is not None
        self.assertEqual(crossed.newly_observed, 1)
        self.assertEqual(crossed.newly_eligible_threshold, 4)
        self.assertEqual(crossed.pending_threshold, 4)
        self.assertEqual(crossed.eligible_threshold, 4)
        self.assertEqual(crossed.next_threshold, 8)

        repeated = self.track(path)
        self.assertIsNotNone(repeated)
        assert repeated is not None
        self.assertEqual(repeated.newly_observed, 0)
        self.assertIsNone(repeated.newly_eligible_threshold)
        self.assertEqual(repeated.pending_threshold, 4)

    def test_state_isolated_by_seat_and_session_identity(self) -> None:
        first_path = self.pi_path()
        second_path = self.pi_path("02def456")
        self.write_pi_count(first_path, 1)
        self.write_pi_count(second_path, 8, session_id="02def456")
        first = self.track(first_path, seat="lead-beo-skills")
        second = self.track(second_path, seat="other-seat")
        self.assertIsNotNone(first)
        self.assertIsNotNone(second)
        assert first is not None and second is not None
        self.assertNotEqual(first.state_path, second.state_path)
        self.assertEqual(first.baseline_count, 1)
        self.assertEqual(second.baseline_count, 8)
        self.assertIsNone(second.pending_threshold)

        mismatch = self.track(second_path, seat="lead-beo-skills")
        self.assertIsNone(mismatch)
        self.assertEqual(json.loads(first.state_path.read_text(encoding="utf-8"))["session_id"], "01abc123")

    def test_malformed_unknown_version_and_symlink_state_fail_closed(self) -> None:
        path = self.pi_path()
        self.write_pi_count(path, 1)
        self.assertIsNotNone(self.track(path))
        state_path = self.state_path()
        state = json.loads(state_path.read_text(encoding="utf-8"))
        state["schema_version"] = True
        state_path.write_text(json.dumps(state), encoding="utf-8")
        self.assertIsNone(self.track(path))

        state_path.write_text("{not-json}\n", encoding="utf-8")
        self.assertIsNone(self.track(path))

        state_path.unlink()
        outside = self.root / "outside-state.json"
        outside.write_text("{}", encoding="utf-8")
        state_path.symlink_to(outside)
        self.assertIsNone(self.track(path))

    def test_malformed_or_mismatched_state_is_unavailable(self) -> None:
        path = self.pi_path()
        self.write_pi_count(path, 1)
        self.assertIsNotNone(self.track(path))
        state_path = self.state_path()
        state = json.loads(state_path.read_text(encoding="utf-8"))

        state["seat"] = "other-seat"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        self.assertIsNone(self.track(path))

        state["seat"] = "lead-beo-skills"
        state["observed_count"] = "not-an-integer"
        state_path.write_text(json.dumps(state), encoding="utf-8")
        self.assertIsNone(self.track(path))
        self.assertEqual(list(state_path.parent.glob("*.tmp")), [])

    def test_symlinked_coordination_root_is_unavailable_without_fallback(self) -> None:
        outside = self.root / "outside-coordination"
        outside.mkdir()
        project_runs = self.home / ".herdr" / "projects" / "project" / "runs"
        project_runs.mkdir(parents=True)
        (project_runs / "coordination").symlink_to(outside, target_is_directory=True)
        path = self.pi_path()
        self.write_pi_count(path, 1)
        self.assertIsNone(self.track(path))
        self.assertEqual(list(outside.iterdir()), [])


class CompactionReprimeDispatchTest(CompactionReprimeBaselineTest):
    def write_pointer_files(
        self,
        run_id: str = "run-1",
        *,
        run_files: tuple[str, ...] | None = None,
    ) -> None:
        project_records = self.home / ".herdr" / "projects" / "project"
        for name, body in {
            "context-pack.md": "RAW CONTEXT PACK BODY must not be copied",
            "gates.md": "RAW GATE BODY must not be copied",
            "supervisor-notebook.md": "RAW NOTEBOOK BODY must not be copied",
        }.items():
            project_records.joinpath(name).parent.mkdir(parents=True, exist_ok=True)
            project_records.joinpath(name).write_text(body, encoding="utf-8")

        run_dir = project_records / "runs" / run_id
        run_dir.mkdir(parents=True, exist_ok=True)
        run_file_bodies = {
            "intake-record.md": "RAW INTAKE BODY must not be copied",
            "plan.md": "RAW PLAN BODY must not be copied",
            "specification.md": "RAW SPECIFICATION BODY must not be copied",
            "slices.json": '{"raw": "RAW SLICES BODY must not be copied"}',
        }
        selected_run_files = set(run_file_bodies) if run_files is None else set(run_files)
        for name, body in run_file_bodies.items():
            if name in selected_run_files:
                run_dir.joinpath(name).write_text(body, encoding="utf-8")

    def make_pending(self, *, run_id: str = "run-1") -> Path:
        path = self.pi_path()
        self.write_pi_count(path, 3)
        self.assertIsNotNone(self.track(path, run_id=run_id))
        self.write_pi_count(path, 7)
        pending = self.track(path, run_id=run_id)
        self.assertIsNotNone(pending)
        assert pending is not None
        self.assertEqual(pending.eligible_threshold, 4)
        return path

    def dispatch(self, path: Path, *, run_id: str = "run-1"):
        return compaction_reprime.dispatch_live_seat(
            self.roster(path),
            "lead-beo-skills",
            run_id=run_id,
            project_root=self.project,
            home_dir=self.home,
        )

    def test_pointer_only_block_contains_canonical_paths_and_sections(self) -> None:
        self.write_pointer_files()
        block = compaction_reprime.build_reprime_block(
            run_id="run-1",
            seat="lead-beo-skills",
            project_root=self.project,
            home_dir=self.home,
        )
        self.assertIsNotNone(block)
        assert block is not None
        self.assertFalse((self.project / "skills").exists())
        doctrine_root = SCRIPT.resolve().parents[1] / "references"
        expected_pointers = (
            self.home / ".herdr" / "projects" / "project" / "context-pack.md",
            self.home / ".herdr" / "projects" / "project" / "gates.md",
            self.home / ".herdr" / "projects" / "project" / "supervisor-notebook.md",
            self.home / ".herdr" / "projects" / "project" / "runs" / "run-1" / "intake-record.md",
            self.home / ".herdr" / "projects" / "project" / "runs" / "run-1" / "plan.md",
            self.home / ".herdr" / "projects" / "project" / "runs" / "run-1" / "specification.md",
            self.home / ".herdr" / "projects" / "project" / "runs" / "run-1" / "slices.json",
            doctrine_root / "lead.md#Recovery",
            doctrine_root / "lead.md#Delivery sequence",
            doctrine_root / "lead.md#Gates and ledger",
            doctrine_root / "supervisor.md#Handoff",
            doctrine_root / "closeout.md#Acceptance custody",
        )
        for pointer in expected_pointers:
            self.assertIn(str(pointer), block)
        for raw_body in (
            "RAW CONTEXT PACK BODY",
            "RAW GATE BODY",
            "RAW NOTEBOOK BODY",
            "RAW INTAKE BODY",
            "RAW PLAN BODY",
            "RAW SPECIFICATION BODY",
            "RAW SLICES BODY",
            "RAW LEAD DOCTRINE BODY",
            "RAW SUPERVISOR DOCTRINE BODY",
            "RAW CLOSEOUT DOCTRINE BODY",
        ):
            self.assertNotIn(raw_body, block)
        self.assertNotIn("{", block)
        self.assertNotIn("}", block)

    def test_success_dispatch_uses_exact_argv_and_is_idempotent(self) -> None:
        self.write_pointer_files()
        path = self.make_pending()
        with patch.object(compaction_reprime.herdr_cli.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as run:
            first = self.dispatch(path)
        self.assertIsNotNone(first)
        assert first is not None
        self.assertTrue(first.prompt_succeeded)
        self.assertEqual(first.threshold, 4)
        self.assertEqual(run.call_count, 1)
        argv = run.call_args.args[0]
        self.assertEqual(argv[:4], ["herdr", "agent", "prompt", "lead-beo-skills"])
        self.assertEqual(argv[4], first.block)
        self.assertEqual(json.loads(first.state_path.read_text(encoding="utf-8"))["consumed_threshold"], 4)
        self.assertEqual(json.loads(first.state_path.read_text(encoding="utf-8"))["prompt_status"], "consumed")

        with patch.object(compaction_reprime.herdr_cli.subprocess, "run") as repeated_run:
            repeated = self.dispatch(path)
        self.assertIsNotNone(repeated)
        assert repeated is not None
        self.assertFalse(repeated.prompt_attempted)
        self.assertIsNone(repeated.threshold)
        repeated_run.assert_not_called()

    def test_successful_thresholds_progress_one_at_a_time(self) -> None:
        self.write_pointer_files()
        path = self.pi_path()
        self.write_pi_count(path, 3)
        self.assertIsNotNone(self.track(path))
        self.write_pi_count(path, 11)
        pending = self.track(path)
        self.assertIsNotNone(pending)
        assert pending is not None
        self.assertEqual(pending.eligible_threshold, 4)

        with patch.object(compaction_reprime.herdr_cli.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as first_run:
            first = self.dispatch(path)
        self.assertIsNotNone(first)
        assert first is not None
        self.assertEqual(first.threshold, 4)
        self.assertEqual(first.state.next_threshold, 8)
        self.assertEqual(first_run.call_count, 1)

        with patch.object(compaction_reprime.herdr_cli.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as second_run:
            second = self.dispatch(path)
        self.assertIsNotNone(second)
        assert second is not None
        self.assertEqual(second.threshold, 8)
        self.assertEqual(second.state.consumed_threshold, 8)
        self.assertEqual(second_run.call_count, 1)

    def test_unavailable_prompt_is_durable_and_retryable(self) -> None:
        self.write_pointer_files()
        path = self.make_pending()
        with patch.object(
            compaction_reprime.herdr_cli,
            "run",
            side_effect=compaction_reprime.herdr_cli.HerdrUnavailable(
                "herdr agent prompt lead-beo-skills timed out"
            ),
        ) as run:
            failed = self.dispatch(path)
        self.assertIsNotNone(failed)
        assert failed is not None
        self.assertTrue(failed.retryable)
        self.assertFalse(failed.prompt_succeeded)
        self.assertEqual(json.loads(failed.state_path.read_text(encoding="utf-8"))["eligible_threshold"], 4)
        run.assert_called_once()

    def test_failed_prompt_is_durable_and_retryable(self) -> None:
        self.write_pointer_files()
        path = self.make_pending()
        with patch.object(compaction_reprime.herdr_cli.subprocess, "run", return_value=subprocess.CompletedProcess([], 17)) as run:
            failed = self.dispatch(path)
        self.assertIsNotNone(failed)
        assert failed is not None
        self.assertTrue(failed.retryable)
        self.assertFalse(failed.prompt_succeeded)
        state = json.loads(failed.state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["prompt_status"], "failed")
        self.assertEqual(state["eligible_threshold"], 4)
        self.assertEqual(state["consumed_threshold"], 0)
        self.assertEqual(run.call_count, 1)

        with patch.object(compaction_reprime.herdr_cli.subprocess, "run", return_value=subprocess.CompletedProcess([], 0)) as retry:
            succeeded = self.dispatch(path)
        self.assertIsNotNone(succeeded)
        assert succeeded is not None
        self.assertTrue(succeeded.prompt_succeeded)
        self.assertEqual(succeeded.threshold, 4)
        self.assertEqual(retry.call_count, 1)
        state = json.loads(succeeded.state_path.read_text(encoding="utf-8"))
        self.assertEqual(state["prompt_status"], "consumed")
        self.assertIsNone(state["eligible_threshold"])
        self.assertEqual(state["consumed_threshold"], 4)

    def test_missing_pointer_fails_closed_without_prompt(self) -> None:
        self.write_pointer_files()
        path = self.make_pending()
        (self.home / ".herdr" / "projects" / "project" / "context-pack.md").unlink()
        with patch.object(compaction_reprime.herdr_cli.subprocess, "run") as run:
            result = self.dispatch(path)
        self.assertIsNotNone(result)
        assert result is not None
        self.assertFalse(result.prompt_attempted)
        self.assertEqual(result.threshold, 4)
        self.assertEqual(json.loads(result.state_path.read_text(encoding="utf-8"))["eligible_threshold"], 4)
        run.assert_not_called()

    def test_optional_run_pointers_include_only_present_files(self) -> None:
        self.write_pointer_files(run_files=("intake-record.md",))
        block = compaction_reprime.build_reprime_block(
            run_id="run-1",
            seat="lead-beo-skills",
            project_root=self.project,
            home_dir=self.home,
        )
        self.assertIsNotNone(block)
        assert block is not None
        run_dir = (self.home / ".herdr" / "projects" / "project" / "runs" / "run-1").resolve()
        intake = (run_dir / "intake-record.md").resolve()
        self.assertIn(f"run-dir: {run_dir}", block)
        self.assertIn(f"intake: {intake}", block)
        for label in ("plan", "specification", "slices"):
            self.assertNotIn(f"\n{label}:", f"\n{block}")

    def test_symlinked_present_run_pointer_fails_closed(self) -> None:
        self.write_pointer_files()
        plan = self.home / ".herdr" / "projects" / "project" / "runs" / "run-1" / "plan.md"
        outside = self.root / "outside-plan.md"
        outside.write_text("outside", encoding="utf-8")
        plan.unlink()
        plan.symlink_to(outside)
        self.assertIsNone(
            compaction_reprime.build_reprime_block(
                run_id="run-1",
                seat="lead-beo-skills",
                project_root=self.project,
                home_dir=self.home,
            )
        )

    def test_cli_requires_run_id_and_seat(self) -> None:
        with patch.object(compaction_reprime, "_load_live_roster") as load:
            load.return_value = []
            with self.assertRaises(SystemExit) as raised:
                compaction_reprime.main([])
            self.assertEqual(raised.exception.code, 2)
            self.assertIn("the following arguments are required", self.stderr.getvalue())
            load.assert_not_called()

    def test_cli_dispatches_from_explicit_project_root(self) -> None:
        with patch.object(compaction_reprime, "_load_live_roster", return_value={"result": {"agents": []}}), \
                patch.object(compaction_reprime, "dispatch_live_seat", return_value=None) as dispatch:
            with patch("sys.stderr", new_callable=io.StringIO) as stderr:
                result = compaction_reprime.main([
                    "--run-id", "run-1", "--seat", "lead-beo-skills", "--project-root", str(self.project),
                ])
        self.assertEqual(result, 1)
        dispatch.assert_called_once()
        self.assertEqual(dispatch.call_args.kwargs["run_id"], "run-1")
        self.assertEqual(dispatch.call_args.kwargs["project_root"], str(self.project))
        self.assertEqual(dispatch.call_args.args[1], "lead-beo-skills")
        self.assertIn("failed closed", stderr.getvalue())

    def test_cli_from_different_cwd_reaches_prompt_with_explicit_project_root(self) -> None:
        self.write_pointer_files()
        path = self.make_pending()
        roster = {"result": {"agents": self.roster(path)}}
        original_cwd = Path.cwd()
        with tempfile.TemporaryDirectory() as other_cwd:
            os.chdir(other_cwd)
            try:
                with patch.object(compaction_reprime, "_load_live_roster", return_value=roster), \
                        patch.object(
                            compaction_reprime.herdr_cli.subprocess,
                            "run",
                            return_value=subprocess.CompletedProcess([], 0),
                        ) as prompt, \
                        patch.dict(os.environ, {"HOME": str(self.home)}):
                    result = compaction_reprime.main([
                        "--run-id", "run-1", "--seat", "lead-beo-skills", "--project-root", str(self.project),
                    ])
            finally:
                os.chdir(original_cwd)
        self.assertEqual(result, 0)
        prompt.assert_called_once()
        self.assertEqual(prompt.call_args.args[0][:4], ["herdr", "agent", "prompt", "lead-beo-skills"])
        self.assertIn("prompted lead-beo-skills at threshold 4", self.stdout.getvalue())

    def test_cli_requires_absolute_project_root(self) -> None:
        with patch.object(compaction_reprime, "_load_live_roster") as load:
            for project_root in (None, "relative/project"):
                arguments = ["--run-id", "run-1", "--seat", "lead-beo-skills"]
                if project_root is not None:
                    arguments.extend(["--project-root", project_root])
                with self.subTest(project_root=project_root), self.assertRaises(SystemExit) as raised:
                    compaction_reprime.main(arguments)
                self.assertEqual(raised.exception.code, 2)
            self.assertIn("--project-root must be an absolute path", self.stderr.getvalue())
            load.assert_not_called()


if __name__ == "__main__":
    unittest.main()
