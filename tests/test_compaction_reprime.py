from __future__ import annotations

import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


SCRIPT = Path(__file__).parents[1] / "skills" / "herdr-delivery-workflow" / "scripts" / "compaction_reprime.py"
SPEC = importlib.util.spec_from_file_location("compaction_reprime", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
compaction_reprime = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = compaction_reprime
SPEC.loader.exec_module(compaction_reprime)


class CompactionReprimeObserverTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.home = self.root / "home"
        self.project = self.root / "project"
        self.home.mkdir()
        self.project.mkdir()

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
        with patch("subprocess.run", side_effect=AssertionError("observer must not invoke commands")):
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


if __name__ == "__main__":
    unittest.main()
