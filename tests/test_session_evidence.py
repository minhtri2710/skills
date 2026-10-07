from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts" / "session_evidence.py"
sys.path.insert(0, str(SCRIPT.parent))
import session_evidence
FIXTURES = Path(__file__).parent / "fixtures" / "session-evidence"


class SessionEvidenceTest(unittest.TestCase):
    def inspect(self, fixture: str, start: int = 1, end: int | None = None):
        path = FIXTURES / fixture
        raw = path.read_bytes()
        lines = raw.splitlines(keepends=True)
        if end is None:
            end = len(lines)
        start_byte = sum(len(line) for line in lines[:start - 1])
        return session_evidence.inspect_range(path, start, end, start_byte, "S1")

    def test_paired_events_are_advisory_only_without_success_inference(self):
        result = self.inspect("paired.jsonl")
        output = "\n".join(result.records)
        self.assertTrue(result.unproven)
        self.assertIn("state=paired-with:R0002 result-unverified", output)
        self.assertNotIn("ID_CANARY", output)
        self.assertIn("state=paired-with:R0001 result-unverified", output)
        self.assertIn("ADVISORY ONLY source=S1 lines=1-4 byte=0", output)
        self.assertIn("no result, exit, head, artifact, or verdict inference", output)
        self.assertNotIn("PASS", output)
        self.assertNotIn("exit=0", output)
        for canary in ("USER_TEXT_CANARY", "ARGUMENT_CANARY", "RESULT_CANARY"):
            self.assertNotIn(canary, output)

    def test_result_before_call_is_ordering_contradiction_without_pair_link(self):
        result = self.inspect("reversed.jsonl")
        output = "\n".join(result.records)
        self.assertTrue(result.unproven)
        self.assertIn("ordering-contradiction", output)
        self.assertNotIn("paired-with", output)
        self.assertNotIn("order-1", output)
        self.assertNotIn("ARGUMENT_CANARY", output)
        self.assertNotIn("RESULT_CANARY", output)

    def test_same_line_call_and_result_is_an_ordering_contradiction(self):
        call = session_evidence.Event(7, "call", "bash", "bash", "same-id", "R0001")
        result = session_evidence.Event(7, "result", "bash", "bash", "same-id", "R0002")
        findings = []
        session_evidence._pair_events([call, result], findings)
        self.assertIn("ordering-contradiction", call.reasons)
        self.assertIn("ordering-contradiction", result.reasons)
        self.assertIsNone(call.paired_with)
        self.assertIsNone(result.paired_with)

    def test_physical_range_pair_does_not_prove_active_pi_branch(self):
        result = self.inspect("branch-ambiguous.jsonl")
        output = "\n".join(result.records)
        self.assertTrue(result.unproven)
        self.assertIn("state=paired-with:R0002 result-unverified", output)
        self.assertIn("no Pi parentId/active-leaf branch proof", output)
        self.assertNotIn("branch-a", output)
        self.assertNotIn("branch-b", output)

    def test_duplicate_ids_are_unproven_and_never_rendered(self):
        result = self.inspect("duplicate.jsonl")
        output = "\n".join(result.records)
        self.assertTrue(result.unproven)
        self.assertIn("duplicate-identifier", output)
        self.assertNotIn("dupe-1", output)

    def test_orphan_result_and_unmatched_request_are_unproven(self):
        for fixture, reason, canary in (
            ("unmatched.jsonl", "unmatched-in-range", "SECRET_CANARY"),
            ("orphan.jsonl", "unmatched-in-range", "ORPHAN_OUTPUT_CANARY"),
        ):
            with self.subTest(fixture=fixture):
                result = self.inspect(fixture)
                output = "\n".join(result.records)
                self.assertTrue(result.unproven)
                self.assertIn(reason, output)
                self.assertNotIn(canary, output)

    def test_counterpart_outside_selected_range_is_not_scanned(self):
        result = self.inspect("paired.jsonl", 4, 4)
        output = "\n".join(result.records)
        self.assertTrue(result.unproven)
        self.assertIn("unmatched-in-range", output)
        self.assertNotIn("line=3", output)

    def test_malformed_and_truncated_records_are_unproven(self):
        result = self.inspect("malformed.jsonl")
        output = "\n".join(result.records)
        self.assertTrue(result.unproven)
        self.assertIn("malformed-line", output)
        self.assertIn("truncated-result", output)
        self.assertNotIn("safe-id", output)
        self.assertNotIn("limit", output)

    def test_final_unterminated_line_is_unproven(self):
        result = self.inspect("unterminated.jsonl")
        output = "\n".join(result.records)
        self.assertTrue(result.unproven)
        self.assertIn("unterminated-line", output)
        self.assertIn("unmatched-in-range", output)

    def test_unsupported_and_missing_sources_fail_closed_without_details(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "unsupported.jsonl"
            path.write_text(
                json.dumps({"type": "future_runtime_event", "secret": "FUTURE_CANARY"}) + "\n",
                encoding="utf-8",
            )
            result = session_evidence.inspect_range(path, 1, 1, 0, "S1")
            self.assertTrue(result.unproven)
            self.assertIn("unsupported-event", "\n".join(result.records))
            self.assertNotIn("FUTURE_CANARY", "\n".join(result.records))
        with tempfile.TemporaryDirectory() as removed:
            missing_path = Path(removed) / "session.jsonl"
        missing = session_evidence.inspect_range(missing_path, 1, 1, 0, "S1")
        self.assertTrue(missing.unproven)
        self.assertIn("UNPROVEN reason=source-unavailable", missing.records)

    def test_attacker_controlled_ids_and_tool_names_never_reach_output(self):
        hostile = "ID_CANARY\u001b[31m\n"
        name = "TOOL_CANARY\u001b[2J"
        document = {
            "type": "message",
            "message": {
                "role": "assistant",
                "content": [{"type": "toolCall", "id": hostile, "name": name, "arguments": {"password": "ARG_CANARY"}}],
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "hostile.jsonl"
            path.write_text(json.dumps(document) + "\n", encoding="utf-8")
            result = session_evidence.inspect_range(path, 1, 1, 0, "S1")
        output = "\n".join(result.records)
        self.assertTrue(result.unproven)
        for canary in ("ID_CANARY", "TOOL_CANARY", "ARG_CANARY", "\\u001b", "\x1b"):
            self.assertNotIn(canary, output)
        self.assertIn("malformed-identifier", output)
        self.assertIn("unsupported-tool", output)

    def test_result_errors_are_visible_but_never_pass(self):
        record = {
            "type": "message",
            "message": {
                "role": "toolResult",
                "toolCallId": "error-1",
                "toolName": "bash",
                "isError": True,
                "content": [],
            },
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "error.jsonl"
            path.write_text(json.dumps(record) + "\n", encoding="utf-8")
            result = session_evidence.inspect_range(path, 1, 1, 0, "S1")
        output = "\n".join(result.records)
        self.assertTrue(result.unproven)
        self.assertIn("tool-error", output)
        self.assertNotIn("PASS", output)

    def test_blank_lines_do_not_desynchronize_the_selected_range(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "blank.jsonl"
            path.write_text("\n".join(("", '{"type":"message","message":{"role":"assistant","content":[]}}', '{"type":"message","message":{"role":"user","content":[]}}', '')),
                            encoding="utf-8")
            result = session_evidence.inspect_range(path, 2, 3, 1, "S1")
            lines = path.read_text(encoding="utf-8").splitlines(keepends=True)
        output = "\n".join(result.records)
        self.assertIn("no-events-in-range", output)
        self.assertTrue(result.unproven)
        self.assertTrue(all(line.endswith("\n") for line in lines[:2]))

    def test_source_reference_is_bounded_and_validated(self):
        path = FIXTURES / "paired.jsonl"
        for source_ref in ("", "fixture-canary", "S0", "S10000", "S1\x1b"):
            with self.subTest(source_ref=source_ref):
                result = session_evidence.inspect_range(path, 1, 1, 0, source_ref)
                output = "\n".join(result.records)
                self.assertTrue(result.unproven)
                self.assertIn("UNPROVEN reason=invalid-source-reference", output)
                if source_ref:
                    self.assertNotIn(source_ref, output)
                self.assertNotIn("fixture-canary", output)

    def test_unsupported_metadata_and_duplicate_json_keys_are_unproven(self):
        records = (
            '{"type":"session_info","id":"ok","unrecognized":"SHAPE_CANARY"}',
            '{"type":"message","type":"message","message":{}}',
            '{"type":"message","message":{"role":"user","content":[],"unknown":"MESSAGE_CANARY"}}',
            '{"type":"message","message":{"role":"assistant","content":[{"type":"toolCall","id":"safe-id","name":"bash","arguments":{},"extra":"BLOCK_CANARY"}]}}',
        )
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "metadata.jsonl"
            path.write_text("\n".join(records) + "\n", encoding="utf-8")
            result = session_evidence.inspect_range(path, 1, 4, 0, "S1")
        output = "\n".join(result.records)
        self.assertTrue(result.unproven)
        self.assertIn("unsupported-event-shape", output)
        self.assertIn("malformed-line", output)
        self.assertIn("unsupported-message-shape", output)
        self.assertIn("unsupported-content-block", output)
        for canary in ("SHAPE_CANARY", "MESSAGE_CANARY", "BLOCK_CANARY", "safe-id"):
            self.assertNotIn(canary, output)

    def test_large_prior_line_is_skipped_by_explicit_byte_offset(self):
        prefix = b"x" * (session_evidence.MAX_LINE_BYTES + 10) + b"\n"
        selected = (FIXTURES / "unmatched.jsonl").read_bytes().splitlines(keepends=True)[0]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "large-prefix.jsonl"
            path.write_bytes(prefix + selected)
            result = session_evidence.inspect_range(path, 2, 2, len(prefix), "S1")
        output = "\n".join(result.records)
        self.assertTrue(result.unproven)
        self.assertIn("line=2", output)
        self.assertNotIn("line-too-large", output)
        self.assertNotIn("x" * 64, output)

    def test_nonregular_and_symlink_sources_are_unproven(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            link = root / "link.jsonl"
            link.symlink_to(FIXTURES / "paired.jsonl")
            for path in (root, link):
                with self.subTest(path_type="symlink" if path.is_symlink() else "directory"):
                    result = session_evidence.inspect_range(path, 1, 1, 0, "S1")
                    self.assertTrue(result.unproven)
                    self.assertIn("UNPROVEN reason=source-unavailable", result.records)
                    self.assertNotIn(str(path), "\n".join(result.records))

    def test_invalid_source_path_is_unproven_without_exception_text(self):
        result = session_evidence.inspect_range("bad-path", 1, 1, 0, "S1")
        self.assertTrue(result.unproven)
        self.assertIn("UNPROVEN reason=invalid-source-path", result.records)
        self.assertNotIn("bad-path", "\n".join(result.records))

    def test_cli_valid_range_is_advisory_and_keeps_source_reference(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--session", str(FIXTURES / "paired.jsonl"),
                "--start-line", "1", "--start-byte", "0", "--end-line", "4",
                "--source-ref", "S1",
            ],
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        self.assertEqual(completed.returncode, 0)
        self.assertIn("ADVISORY ONLY source=S1 lines=1-4 byte=0", completed.stdout)
        self.assertNotIn("ARGUMENT_CANARY", completed.stdout)
        self.assertNotIn("RESULT_CANARY", completed.stdout)
        self.assertIn("no result, exit, head, artifact, or verdict inference", completed.stdout)

    def test_cli_requires_positive_finite_line_range(self):
        for start, end in (("0", "1"), ("2", "1"), ("1", "1001"), ("1x", "2")):
            with self.subTest(start=start, end=end):
                completed = subprocess.run(
                    [sys.executable, str(SCRIPT), "--session", str(FIXTURES / "paired.jsonl"), "--start-line", start, "--start-byte", "0", "--end-line", end, "--source-ref", "S1"],
                    capture_output=True,
                    text=True,
                    encoding="utf-8",
                )
                self.assertEqual(completed.returncode, 0)
                self.assertIn("UNPROVEN reason=invalid-range", completed.stdout)


if __name__ == "__main__":
    unittest.main()
