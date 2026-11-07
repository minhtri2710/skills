#!/usr/bin/env python3
"""Tests for the repository-owned, seat-level closeout checker."""
from __future__ import annotations

import contextlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import support
import backend
import closeout_check
import gate_row
from fake_backend import FakeBackend


def setUpModule() -> None:
    support.never_run("git")


def add_peer(fake: FakeBackend, canonical: Path, name: str, seat: str, *, agent: bool = True,
             processes: list[backend.Process] | None = None) -> None:
    """An open peer seat; `agent=False` leaves its terminal open with no agent registered for it."""
    if agent:
        fake.add_seat(seat, name=name, state="idle", cwd=str(canonical), processes=processes)
    else:
        fake.add_terminal(seat, cwd=str(canonical), processes=processes)


def count_folds(run):
    """Run `run()` and return (its result, how many rows it folded into a LedgerState)."""
    folded: list[str] = []
    real_add = gate_row.LedgerState.add

    def counting_add(state, row):
        folded.append(row)
        real_add(state, row)

    with mock.patch.object(gate_row.LedgerState, "add", counting_add):
        result = run()
    return result, len(folded)


class CloseoutCheckTest(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.canonical = support.temp_git_repo(Path(self.tmp.name) / "checkout")
        (self.canonical / "tracked.txt").write_text("base\n", encoding="utf-8")
        support.git(self.canonical, "add", "tracked.txt")
        support.git(self.canonical, "commit", "-qm", "base")
        self.fake = FakeBackend()
        self.project_dir = Path(self.tmp.name) / "closeout-project"
        self.project_dir.mkdir()
        self.ledger = self.project_dir / "gates.md"
        self.ledger.write_text("# Gate ledger — test\n\n", encoding="utf-8")
        self.record = {
            "canonical_checkout": str(self.canonical),
            "gates_ledger": str(self.ledger),
            "persistent": [
                {"role": "Lead", "name": "lead-beo-skills", "seat": "w1:p1"},
                {"role": "Human Supervisor", "name": "supervisor", "seat": "w1:p2"},
            ],
            "peers": [
                {"issue": "teardown-clarify", "role": "Engineer",
                 "name": "eng-teardown", "seat": "w1:p3"},
                {"issue": "teardown-clarify", "role": "Reviewer",
                 "name": "review-teardown", "seat": "w1:p4"},
            ],
        }
        self.fake.add_terminal("w1:p1", cwd=str(self.canonical))
        self.fake.add_terminal("w1:p2", cwd=str(self.canonical))
        add_peer(self.fake, self.canonical, "eng-teardown", "w1:p3", agent=False)
        add_peer(self.fake, self.canonical, "review-teardown", "w1:p4")
        self.addCleanup(self.tmp.cleanup)

    def test_closeout_reports_a_ledger_that_fails_check(self):
        origin = Path(self.tmp.name) / "origin.git"
        support.temp_git_repo(origin, bare=True)
        git = support.git

        def row(*args: str) -> None:
            out, err = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                code = gate_row.main([
                    "--ledger", str(self.ledger), "--repo", str(self.canonical), *args,
                ])
            self.assertEqual(code, 0, err.getvalue())

        base = git(self.canonical, "rev-parse", "HEAD")
        (self.canonical / "tracked.txt").write_text("pushed\n", encoding="utf-8")
        git(self.canonical, "add", "tracked.txt")
        git(self.canonical, "commit", "-qm", "pushed")
        tip = git(self.canonical, "rev-parse", "HEAD")
        git(self.canonical, "remote", "add", "origin", str(origin))
        git(self.canonical, "push", "-q", "-u", "origin", "main")
        row("--kind", "review", "--status", "recorded:review-pass", "--review-base", base,
            "--words", "seat", "--note", "review passed", "--quote", "PASS")
        row("--kind", "push", "--status", "resolved:push", "--push-base", base,
            "--boundary", "tracked.txt",
            "--words", "human", "--brief", "Record that the push landed.",
            "--note", "push landed", "--quote", "")

        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        miscounted = rows[-1].replace(" count=1 ", " count=2 ", 1)
        self.ledger.write_text(
            "# Gate ledger — test\n\n" + "\n".join([*rows[:-1], miscounted]) + "\n",
            encoding="utf-8",
        )
        self.fake.remove("w1:p3")
        self.fake.remove("w1:p4")

        result = closeout_check.check_closeout(self.record, self.fake)
        self.assertFalse(result.passed)
        self.assertEqual(len(result.findings), 1)
        self.assertIn("gate ledger could not be checked:", result.findings[0])
        self.assertIn(f"count=2 but {base}..{tip} carries 1 commits", result.findings[0])

    def test_reviewed_unpushed_commit_needs_an_open_push_gate(self):
        temp = Path(self.tmp.name) / "d4"
        repo = temp / "repo"
        origin = temp / "origin.git"
        git = support.git
        support.temp_git_repo(origin, bare=True)
        support.temp_git_repo(repo)
        (repo / "tracked.txt").write_text("base\n", encoding="utf-8")
        git(repo, "add", "tracked.txt")
        git(repo, "commit", "-qm", "base")
        base = git(repo, "rev-parse", "HEAD")
        git(repo, "remote", "add", "origin", str(origin))
        git(repo, "push", "-q", "-u", "origin", "main")

        (repo / "tracked.txt").write_text("pushed\n", encoding="utf-8")
        git(repo, "commit", "-qam", "pushed")
        pushed_commit = git(repo, "rev-parse", "HEAD")
        git(repo, "push", "-q", "origin", "main")

        (repo / "tracked.txt").write_text("reviewed\n", encoding="utf-8")
        git(repo, "commit", "-qam", "reviewed")
        reviewed = git(repo, "rev-parse", "HEAD")
        self.record["canonical_checkout"] = str(repo)
        self.fake.remove("w1:p3")
        self.fake.remove("w1:p4")
        self.ledger.write_text(
            f"G1 | 2026-09-28T00:00:00Z | kind=review | main@{reviewed} | "
            f"status=recorded:review-pass | record=timely | review={base}..{reviewed} count=2 | "
            "words=seat | note=review passed | quote=\"PASS\"\n",
            encoding="utf-8",
        )

        missing_gate = closeout_check.check_closeout(self.record, self.fake)
        self.assertFalse(missing_gate.passed)
        self.assertEqual(len(missing_gate.findings), 1)
        self.assertIn("reviewed unpushed commit", missing_gate.findings[0])
        self.assertIn("no open push-gate row", missing_gate.findings[0])
        self.assertIn(reviewed, missing_gate.findings[0])
        self.assertNotIn(pushed_commit, missing_gate.findings[0])

        review_row = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))[0]
        push_gate = (
            f"G2 | 2026-09-28T00:00:01Z | kind=push-gate | main@{reviewed} | status=open | "
            f"record=timely | prev_hash={gate_row.row_hash(review_row)} | words=none | "
            "note=push awaits the Human | quote=\"\"\n"
        )
        self.ledger.write_text(self.ledger.read_text(encoding="utf-8") + push_gate, encoding="utf-8")
        gated = closeout_check.check_closeout(self.record, self.fake)
        self.assertTrue(gated.passed, gated.findings)

        git(repo, "push", "-q", "origin", "main")
        pushed = closeout_check.check_closeout(self.record, self.fake)
        self.assertTrue(pushed.passed, pushed.findings)

        (repo / "tracked.txt").write_text("unreviewed\n", encoding="utf-8")
        git(repo, "commit", "-qam", "unreviewed")
        unreviewed = closeout_check.check_closeout(self.record, self.fake)
        self.assertTrue(unreviewed.passed, unreviewed.findings)

    def test_closeout_folds_each_ledger_row_once(self):
        def git(*args: str) -> str:
            return support.git(self.canonical, *args)

        base = git("rev-parse", "HEAD")
        (self.canonical / "tracked.txt").write_text("next\n", encoding="utf-8")
        git("commit", "-qam", "next")
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            self.assertEqual(gate_row.main([
                "--ledger", str(self.ledger), "--repo", str(self.canonical),
                "--kind", "review", "--status", "recorded:review-pass", "--review-base", base,
                "--words", "seat", "--note", "review passed", "--quote", "PASS",
            ]), 0)
        rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        _, folds = count_folds(lambda: closeout_check.check_closeout(self.record, self.fake))
        self.assertEqual(folds, len(rows))

    def test_open_recorded_peer_fails_even_when_agent_is_not_found_then_passes_after_close(self):
        result = closeout_check.check_closeout(self.record, self.fake)
        self.assertFalse(result.passed)
        self.assertIn("eng-teardown", "\n".join(result.findings))
        self.assertIn("agent_not_found", "\n".join(result.findings))
        self.assertEqual(self.fake.calls, [
            ("get_terminal", "w1:p3"), ("get_seat", "eng-teardown"), ("processes", "w1:p3"),
            ("get_terminal", "w1:p4"), ("get_seat", "review-teardown"), ("processes", "w1:p4"),
        ])

        self.fake.remove("w1:p3")
        self.fake.remove("w1:p4")
        result = closeout_check.check_closeout(self.record, self.fake)
        self.assertTrue(result.passed, result.findings)
        self.assertEqual(result.checked_seats, ("w1:p3", "w1:p4"))

    def test_server_detection_matches_argv_tokens_not_substrings(self):
        cases = (
            (["node", "vitest"], False),
            (["tail", "-f", "/dev/null"], False),
            (["vim", "server.py"], False),
            (["npm", "run", "dev"], True),
            (["vite"], True),
            (["/usr/bin/python3", "-m", "http.server"], True),
            (["next", "dev"], True),
            (["uvicorn", "app:app"], True),
            (["node", "server.js"], True),
            (["python3", "serve.py"], True),
            (["bun", "./src/server.ts"], True),
            (["deno", "run", "-A", "server.ts"], True),
            (["/usr/local/bin/node", "--inspect", "dev.mjs"], True),
            (["cat", "server.js"], False),
            (["less", "dev.log"], False),
            (["node", "build.js", "server.js"], False),
            (["python3", "-c", "import server"], False),
            (["node", "-e", "require('./server.js')"], False),
        )
        for argv, expected in cases:
            with self.subTest(argv=argv):
                add_peer(self.fake, self.canonical, "eng-teardown", "w1:p3", agent=False,
                         processes=[backend.Process(tuple(argv), cwd=str(self.canonical))])
                result = closeout_check.check_closeout(self.record, self.fake)
                self.assertEqual(
                    any("squatting-server anti-pattern" in finding for finding in result.findings),
                    expected,
                )

    def test_a_server_outside_the_canonical_checkout_is_not_squatting(self):
        add_peer(self.fake, self.canonical, "eng-teardown", "w1:p3", agent=False,
                 processes=[backend.Process(("npm", "run", "dev"), cwd=str(self.canonical.parent / "elsewhere"))])
        result = closeout_check.check_closeout(self.record, self.fake)
        self.assertFalse(any("squatting-server" in finding for finding in result.findings))

    def test_a_process_without_a_cwd_takes_the_terminals(self):
        add_peer(self.fake, self.canonical, "eng-teardown", "w1:p3", agent=False,
                 processes=[backend.Process(("npm", "run", "dev"))])
        result = closeout_check.check_closeout(self.record, self.fake)
        self.assertTrue(any("squatting-server" in finding for finding in result.findings))

    def test_lead_only_persistent_record_passes_validation_and_closeout(self):
        record = dict(self.record)
        record["persistent"] = [self.record["persistent"][0]]
        self.fake.remove("w1:p3")
        self.fake.remove("w1:p4")
        result = closeout_check.check_closeout(record, self.fake)
        self.assertTrue(result.passed, result.findings)

    def test_persistent_record_without_exactly_one_lead_or_with_extra_roles_refuses(self):
        lead, supervisor = self.record["persistent"][0], self.record["persistent"][1]
        cases = {
            "zero lead": [supervisor],
            "two human supervisors": [
                lead, supervisor,
                {"role": "Human Supervisor", "name": "supervisor-2", "seat": "w1:p5"},
            ],
            "unknown role": [lead, {"role": "Architect", "name": "architect", "seat": "w1:p5"}],
        }
        for label, persistent in cases.items():
            with self.subTest(label):
                record = dict(self.record)
                record["persistent"] = persistent
                result = closeout_check.check_closeout(record, self.fake)
                self.assertFalse(result.passed)
                self.assertIn(
                    "persistent must record exactly one Lead and at most one Human Supervisor",
                    result.findings[0],
                )

    def test_duplicate_persistent_seat_is_rejected(self):
        record = dict(self.record)
        record["persistent"] = [
            self.record["persistent"][0],
            {"role": "Human Supervisor", "name": "supervisor", "seat": "w1:p1"},
        ]
        with self.assertRaisesRegex(ValueError, "persistent seat 'w1:p1' is duplicated"):
            closeout_check._validate_record(record)

    def test_duplicate_persistent_name_is_rejected(self):
        record = dict(self.record)
        record["persistent"] = [
            self.record["persistent"][0],
            {"role": "Human Supervisor", "name": "lead-beo-skills", "seat": "w1:p2"},
        ]
        with self.assertRaisesRegex(ValueError, "persistent name 'lead-beo-skills' is duplicated"):
            closeout_check._validate_record(record)

    def test_terminal_read_failure_fails_closed(self):
        self.fake.script("get_terminal", backend.BackendUnavailable("get_terminal timed out"))
        result = closeout_check.check_closeout(self.record, self.fake)
        self.assertFalse(result.passed)
        self.assertTrue(any("w1:p3: terminal read failed" in finding for finding in result.findings))

    def test_mismatched_terminal_evidence_fails_closed(self):
        self.fake.script("get_terminal", backend.Seat(handle="w1:p9", cwd=str(self.canonical)))
        result = closeout_check.check_closeout(self.record, self.fake)
        self.assertFalse(result.passed)
        self.assertTrue(any("w1:p3: backend returned mismatched terminal evidence" in finding
                            for finding in result.findings))

    def test_agent_and_process_read_failures_are_findings_not_passes(self):
        self.fake.script("get_seat", backend.BackendUnavailable("agent get timed out"))
        self.fake.script("processes", backend.BackendError("process-info lacks foreground_processes"))
        result = closeout_check.check_closeout(self.record, self.fake)
        self.assertFalse(result.passed)
        text = "\n".join(result.findings)
        self.assertIn("w1:p3: agent read failed: agent get timed out", text)
        self.assertIn("eng-teardown seat w1:p3 remains open", text)
        self.assertNotIn("despite agent_not_found", text)
        self.assertIn("w1:p3: process read failed: process-info lacks foreground_processes", text)

    def test_malformed_opaque_handle_is_rejected_without_boundary_call(self):
        record = dict(self.record)
        record["peers"] = [dict(self.record["peers"][0], seat="$(touch should-not-run)")]
        result = closeout_check.check_closeout(record, self.fake)
        self.assertFalse(result.passed)
        self.assertIn("malformed staffing record", result.findings[0])
        self.assertEqual(self.fake.calls, [])

    def test_template_loads_and_validates(self):
        template = (
            Path(__file__).resolve().parents[1]
            / "skills"
            / "agent-delivery-workflow"
            / "templates"
            / "staffing-closeout.json"
        )
        with template.open(encoding="utf-8") as handle:
            record = json.load(handle)
        canonical, peers, ledger = closeout_check._validate_record(record)
        self.assertTrue(canonical.is_absolute())
        self.assertTrue(ledger.is_absolute())
        self.assertEqual([peer["role"] for peer in peers], ["Engineer", "Reviewer"])
        self.assertEqual(
            record["persistent"],
            [
                {"role": "Lead", "name": "lead-project-slug", "seat": "w0:pLead"},
                {"role": "Human Supervisor", "name": "supervisor", "seat": "w0:pSupervisor"},
            ],
        )

    def test_cli_reads_json_closeout_staffing_record_and_returns_pass(self):
        self.fake.remove("w1:p3")
        self.fake.remove("w1:p4")
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "staffing.json"
            path.write_text(json.dumps(self.record), encoding="utf-8")
            stdout = io.StringIO()
            stderr = io.StringIO()
            with contextlib.ExitStack() as stack:
                stack.enter_context(mock.patch.object(backend, "open_backend", return_value=self.fake))
                stack.enter_context(contextlib.redirect_stdout(stdout))
                stack.enter_context(contextlib.redirect_stderr(stderr))
                code = closeout_check.main(["--staffing", str(path)])
        self.assertEqual(code, 0)
        self.assertIn("PASS:", stdout.getvalue())
        self.assertEqual(stderr.getvalue(), "")

    def test_cli_fails_closed_when_the_backend_cannot_open_and_passes_the_flag_to_detect(self):
        explicit = backend.Explicit("herdr", "w1:p1")
        stderr = io.StringIO()
        with mock.patch.object(backend, "detect", side_effect=backend.DetectionError("no match")) as detect, \
                contextlib.redirect_stderr(stderr):
            code = closeout_check.main(["--staffing", "unused.json", "--backend", "herdr@w1:p1"])
        self.assertEqual(code, 1)
        self.assertEqual(stderr.getvalue(), "FAIL: no match\n")
        self.assertEqual(detect.call_args.args[1], explicit)


if __name__ == "__main__":
    unittest.main()
