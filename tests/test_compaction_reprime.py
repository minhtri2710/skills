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

    def roster(self, *, kind: str, path: Path | None = None, session_id: str | None = None) -> list[dict[str, object]]:
        session: dict[str, object]
        if kind == "pi":
            session = {"source": "herdr:pi", "agent": "pi", "kind": "path", "value": str(path)}
        else:
            session = {"source": "herdr:claude", "agent": "claude", "kind": "id", "value": session_id}
        return [{
            "name": "lead-beo-skills",
            "pane_id": "w2Q:pA",
            "agent": kind,
            "cwd": str(self.project),
            "agent_session": session,
        }]

    def pi_path(self) -> Path:
        return self.home / ".pi" / "agent" / "sessions" / "--project--" / "2026-09-21T10-00-00-000Z_01abc123.jsonl"

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


if __name__ == "__main__":
    unittest.main()
