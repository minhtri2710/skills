#!/usr/bin/env python3
"""Unit tests for beo_propose.py (G4 — proposal generator)."""
from __future__ import annotations

import contextlib
import io
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

REFERENCE_ROOT = Path(__file__).resolve().parents[1] / "skills" / "beo" / "beo-reference"
SCRIPTS = REFERENCE_ROOT / "scripts"
sys.path.insert(0, str(SCRIPTS))


class ProposalIdTest(unittest.TestCase):
    def test_proposal_id_is_deterministic(self):
        """Same blob must produce the same proposal_id."""
        import beo_propose
        id_a = beo_propose._proposal_id("same trigger")
        id_b = beo_propose._proposal_id("same trigger")
        self.assertEqual(id_a, id_b)

    def test_proposal_id_format(self):
        """proposal_id must match the harness-proposal schema pattern (prop-<sha1 prefix>)."""
        import beo_propose
        pid = beo_propose._proposal_id("any text")
        self.assertRegex(pid, r"^prop-[a-f0-9]{8}$")

    def test_proposal_id_different_inputs_produce_different_ids(self):
        """Different triggers must produce different proposal_ids."""
        import beo_propose
        id_a = beo_propose._proposal_id("trigger A")
        id_b = beo_propose._proposal_id("trigger B")
        self.assertNotEqual(id_a, id_b)


class LoadJsonlTest(unittest.TestCase):
    def test_load_missing_file_returns_empty(self):
        """A missing path must return an empty list, not raise."""
        import beo_propose
        self.assertEqual(beo_propose._load_jsonl(Path("/nonexistent/path.jsonl")), [])

    def test_load_skips_blank_lines(self):
        """Blank lines must be ignored, valid events must be returned."""
        import beo_propose
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write('{"kind": "friction", "payload": {"description": "x"}}\n')
            f.write("\n")
            f.write('   \n')
            f.write('{"kind": "friction", "payload": {"description": "y"}}\n')
            path = Path(f.name)
        try:
            events = beo_propose._load_jsonl(path)
            self.assertEqual(len(events), 2)
            self.assertEqual(events[0]["payload"]["description"], "x")
        finally:
            path.unlink()

    def test_load_skips_malformed_lines(self):
        """A malformed JSON line must be skipped, not crash the whole load."""
        import beo_propose
        with tempfile.NamedTemporaryFile("w", suffix=".jsonl", delete=False) as f:
            f.write('{"kind": "friction", "payload": {"description": "valid"}}\n')
            f.write('this is not json\n')
            f.write('{"kind": "friction", "payload": {"description": "also valid"}}\n')
            path = Path(f.name)
        try:
            events = beo_propose._load_jsonl(path)
            self.assertEqual(len(events), 2)
        finally:
            path.unlink()


class TriggerFromEventTest(unittest.TestCase):
    def test_friction_event_with_description(self):
        """A friction event with a description should produce a friction trigger."""
        import beo_propose
        event = {"kind": "friction", "payload": {"description": "validator crashed"}}
        trigger = beo_propose._trigger_from_event(event)
        self.assertIsNotNone(trigger)
        self.assertIn("friction", trigger)
        self.assertEqual(trigger["friction"], "validator crashed")

    def test_friction_event_uses_reason_as_fallback(self):
        """If description is missing, reason should be used as the friction text."""
        import beo_propose
        event = {"kind": "friction", "payload": {"reason": "stale approval"}}
        trigger = beo_propose._trigger_from_event(event)
        self.assertIsNotNone(trigger)
        self.assertIn("stale approval", trigger["friction"])

    def test_friction_event_with_no_description_returns_none(self):
        """A friction event with no description or reason returns None."""
        import beo_propose
        event = {"kind": "friction", "payload": {}}
        self.assertIsNone(beo_propose._trigger_from_event(event))

    def test_learning_candidate_suggestion(self):
        """A learning_candidate_suggestion event with hypothesis returns a learning trigger."""
        import beo_propose
        event = {"kind": "learning_candidate_suggestion", "payload": {"hypothesis": "tested pattern"}}
        trigger = beo_propose._trigger_from_event(event)
        self.assertIsNotNone(trigger)
        self.assertEqual(trigger["learning"], "tested pattern")

    def test_unknown_kind_returns_none(self):
        """Events with non-proposal kinds return None."""
        import beo_propose
        for kind in ("handoff", "verification_run", "score", "intervention", "user_stop"):
            with self.subTest(kind=kind):
                self.assertIsNone(beo_propose._trigger_from_event({"kind": kind, "payload": {}}))


class TriggerFromLearningNoteTest(unittest.TestCase):
    def test_extracts_first_heading(self):
        """The first H1 heading in the note becomes the trigger summary."""
        import beo_propose
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("# A reusable lesson about beo-validate\n\nbody text\n")
            path = Path(f.name)
        try:
            trigger = beo_propose._trigger_from_learning_note(path)
            self.assertIn("learning_note", trigger)
            self.assertEqual(trigger["learning_note"], "A reusable lesson about beo-validate")
        finally:
            path.unlink()

    def test_falls_back_to_filename_stem(self):
        """A note without an H1 heading should use the filename stem."""
        import beo_propose
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as f:
            f.write("body without a heading\n")
            path = Path(f.name)
        try:
            trigger = beo_propose._trigger_from_learning_note(path)
            self.assertEqual(trigger["learning_note"], path.stem)
        finally:
            path.unlink()


class TriggerFromHarnessProposalTest(unittest.TestCase):
    def test_missing_yaml_module_returns_unreadable_trigger(self):
        """If PyYAML is unavailable, the function returns an 'unreadable' trigger, never raises."""
        import beo_propose
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as f:
            f.write("change_type: bugfix\n")
            path = Path(f.name)
        try:
            with mock.patch.dict(sys.modules, {"yaml": None}):
                trigger = beo_propose._trigger_from_harness_proposal(path)
            self.assertIsNotNone(trigger)
            self.assertIn("harness_proposal", trigger)
            self.assertIn("PyYAML missing", trigger["harness_proposal"])
        finally:
            path.unlink()


class MainSmokeTest(unittest.TestCase):
    def test_main_no_triggers_returns_zero(self):
        """main() with no events/proposals/notes should return 0 and emit an OK payload."""
        import beo_propose
        with tempfile.TemporaryDirectory() as tmp:
            argv = ["beo_propose.py", "--root", tmp, "--dry-run"]
            with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()) as out:
                rc = beo_propose.main()
            self.assertEqual(rc, 0)
            payload = json.loads(out.getvalue())
            self.assertTrue(payload["ok"])
            self.assertEqual(payload["proposals_created"], 0)
            self.assertEqual(payload["proposals_skipped"], 0)

    def test_main_dry_run_does_not_write(self):
        """--dry-run must not create the proposals/pending directory or any files."""
        import beo_propose
        with tempfile.TemporaryDirectory() as tmp:
            artifacts = Path(tmp) / ".beads" / "artifacts" / "br-99"
            artifacts.mkdir(parents=True)
            (artifacts / "runtime-events.jsonl").write_text(
                '{"issue_id": "br-99", "kind": "friction", "payload": {"description": "x"}}\n',
                encoding="utf-8",
            )
            argv = ["beo_propose.py", "--root", tmp, "--dry-run"]
            with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()) as out:
                rc = beo_propose.main()
            self.assertEqual(rc, 0)
            payload = json.loads(out.getvalue())
            self.assertGreaterEqual(payload["proposals_created"], 1)
            proposal_dir = Path(tmp) / "skills" / "beo" / "beo-climate" / "proposals" / "pending"
            self.assertFalse(proposal_dir.exists(), "dry-run must not create the proposal directory")

    def test_main_writes_proposal_file(self):
        """A friction runtime event should produce a proposal markdown file in pending/."""
        import beo_propose
        with tempfile.TemporaryDirectory() as tmp:
            artifacts = Path(tmp) / ".beads" / "artifacts" / "br-99"
            artifacts.mkdir(parents=True)
            (artifacts / "runtime-events.jsonl").write_text(
                '{"issue_id": "br-99", "kind": "friction", "payload": {"description": "audit emits false positive"}}\n',
                encoding="utf-8",
            )
            argv = ["beo_propose.py", "--root", tmp]
            with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()) as out:
                rc = beo_propose.main()
            self.assertEqual(rc, 0)
            payload = json.loads(out.getvalue())
            self.assertEqual(payload["proposals_created"], 1)
            proposal_dir = Path(tmp) / "skills" / "beo" / "beo-climate" / "proposals" / "pending"
            self.assertTrue(proposal_dir.exists())
            files = list(proposal_dir.glob("prop-*.md"))
            self.assertEqual(len(files), 1)
            text = files[0].read_text(encoding="utf-8")
            self.assertIn("proposal_id: prop-", text)
            self.assertIn("audit emits false positive", text)

    def test_main_is_idempotent(self):
        """Running main() twice in a row must not create extra proposal files."""
        import beo_propose
        with tempfile.TemporaryDirectory() as tmp:
            artifacts = Path(tmp) / ".beads" / "artifacts" / "br-99"
            artifacts.mkdir(parents=True)
            (artifacts / "runtime-events.jsonl").write_text(
                '{"issue_id": "br-99", "kind": "friction", "payload": {"description": "x"}}\n',
                encoding="utf-8",
            )
            argv = ["beo_propose.py", "--root", tmp]
            for _ in range(2):
                with mock.patch.object(sys, "argv", argv), contextlib.redirect_stdout(io.StringIO()) as out:
                    beo_propose.main()
            proposal_dir = Path(tmp) / "skills" / "beo" / "beo-climate" / "proposals" / "pending"
            files = list(proposal_dir.glob("prop-*.md"))
            self.assertEqual(len(files), 1, f"expected 1 proposal, got {len(files)}: {files}")


class HarnessProposalAuthorityTest(unittest.TestCase):
    """M5: harness_proposal per-field authority."""

    def setUp(self):
        import beo_state
        self.authority = beo_state.HARNESS_PROPOSAL_FIELD_AUTHORITY

    def test_beo_author_may_write_status(self):
        """beo-author must be allowed to write status."""
        from beo_state import validate_harness_proposal_write
        validate_harness_proposal_write({"status": "applied"}, "beo-author")

    def test_beo_execute_may_not_write_status(self):
        """beo-execute must be rejected when trying to write status."""
        from beo_state import validate_harness_proposal_write
        with self.assertRaises(ValueError) as ctx:
            validate_harness_proposal_write({"status": "applied"}, "beo-execute")
        self.assertIn("beo-execute", str(ctx.exception))
        self.assertIn("status", str(ctx.exception))
        self.assertIn("beo-author", str(ctx.exception))

    def test_all_three_may_write_proposal_id(self):
        """beo-execute, beo-review, and beo-author may all write non-status fields."""
        from beo_state import validate_harness_proposal_write
        for actor in ("beo-execute", "beo-review", "beo-author"):
            try:
                validate_harness_proposal_write({"proposal_id": "prop-abcdef01"}, actor)
            except ValueError as exc:
                self.fail(f"{actor} should be allowed to write proposal_id: {exc}")

    def test_unknown_field_raises(self):
        """Writing an unknown field must raise ValueError."""
        from beo_state import validate_harness_proposal_write
        with self.assertRaises(ValueError) as ctx:
            validate_harness_proposal_write({"nonexistent": True}, "beo-author")
        self.assertIn("unknown", str(ctx.exception).lower())


if __name__ == "__main__":
    unittest.main()
