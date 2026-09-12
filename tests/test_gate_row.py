#!/usr/bin/env python3
"""Unit tests for gate_row.py (C19 — the ledger row is derived, not typed)."""
from __future__ import annotations

import contextlib
import io
import re
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from types import SimpleNamespace
from unittest import mock
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"
sys.path.insert(0, str(SCRIPTS))

import gate_row  # noqa: E402


def make_repo(tmp: Path) -> Path:
    repo = tmp / "repo"
    repo.mkdir()
    run = lambda *a: subprocess.run(["git", "-C", str(repo), *a], check=True,
                                    capture_output=True, text=True)
    run("init", "-q", "-b", "main")
    run("config", "user.email", "t@example.invalid")
    run("config", "user.name", "t")
    for n in range(3):
        (repo / f"f{n}.txt").write_text(f"{n}\n")
        run("add", "-A")
        run("commit", "-qm", f"c{n}")
    return repo


class GateRowTest(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir="/private/tmp")
        self.tmp = Path(self._tmp.name)
        self.repo = make_repo(self.tmp)
        self.ledger = self.tmp / "gates.md"
        self.ledger.write_text("# Gate ledger — test\n\n")
        self.addCleanup(self._tmp.cleanup)

    def run_main(self, argv: list[str]) -> int:
        """Run the CLI with its stdout and stderr captured, so a test run stays readable.

        stderr is kept on `self.err`: a refusal that exits 1 for the wrong reason
        is still a passing exit code, so the message is part of the assertion.
        """
        self.err = io.StringIO()
        self.out = io.StringIO()
        with contextlib.redirect_stdout(self.out), contextlib.redirect_stderr(self.err):
            return gate_row.main(argv)

    def append(self, *extra: str) -> int:
        return self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "merge", "--status", "resolved:standing-waiver",
            "--words", "human", "--note", "merged the reviewed head", "--quote", "merge it", *extra,
        ])

    def git(self, *args: str) -> str:
        return subprocess.run(["git", "-C", str(self.repo), *args],
                              capture_output=True, text=True, check=True).stdout.strip()

    def rev(self, ref: str) -> str:
        return subprocess.run(["git", "-C", str(self.repo), "rev-parse", ref],
                              capture_output=True, text=True, check=True).stdout.strip()

    def last_row(self) -> str:
        return [l for l in self.ledger.read_text().splitlines()
                if gate_row.ID_RE.match(l)][-1]

    def fixture_row(self, gid: str, status: str, words: str = "human",
                    quote: str = "fixture", resolves: str | None = None,
                    note: str = "fixture") -> str:
        target = f" | resolves={resolves}" if resolves else ""
        return (f"{gid} | 2026-09-06T00:00:00Z | kind=merge | "
                f"main@{self.rev('HEAD')} | status={status} | record=timely"
                f"{target} | words={words} | note={note} | quote=\"{quote}\"")

    def open_gates(self) -> list[str]:
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--open-gates",
        ]), 0)
        return self.out.getvalue().splitlines()

    def test_words_is_required_for_append(self):
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "merge", "--status", "resolved:standing-waiver",
            "--note", "merged the reviewed head", "--quote", "merge it",
        ]), 1)
        self.assertIn("--words is required", self.err.getvalue())
        self.assertEqual(self.ledger.read_text(), "# Gate ledger — test\n\n")

    def test_round_trip(self):
        """A row the script writes is a row --check accepts, unchanged."""
        self.assertEqual(self.append(), 0)
        written = self.last_row()
        self.assertEqual(self.run_main(
            ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]), 0)
        self.assertEqual(self.last_row(), written)

    def test_monotonic_ledger_passes_check(self):
        self.assertEqual(self.append(), 0)
        self.assertEqual(self.append(), 0)
        self.assertEqual(self.run_main(
            ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]), 0)

    def test_backdated_last_row_fails_check_with_timestamp_regression(self):
        self.assertEqual(self.append(), 0)
        existing_rows = gate_row.ledger_rows(self.ledger.read_text(encoding="utf-8"))
        args = SimpleNamespace(
            kind="merge", status="resolved:test", channel="", writer="", record="timely",
            push_base="", boundary=[], resolves=[], words="human", note="backdated",
            quote="backdated", quote_file="",
        )
        with mock.patch.object(gate_row, "datetime") as clock:
            clock.now.return_value = datetime(2000, 1, 1, tzinfo=timezone.utc)
            backdated = gate_row.build(args, self.repo, self.ledger, existing_rows)
        self.ledger.write_text(
            self.ledger.read_text(encoding="utf-8") + backdated + "\n", encoding="utf-8"
        )
        self.assertEqual(self.run_main(
            ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]), 1)
        self.assertIn("timestamp regression", self.err.getvalue())
        self.assertIn("2000-01-01T00:00:00Z", self.err.getvalue())

    def test_quote_file_becomes_quote_and_round_trips(self):
        quote_file = self.tmp / "refused-command.txt"
        quote = "runtime denied command | --flag"
        quote_file.write_text(quote, encoding="utf-8")
        argv = [
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "merge", "--status", "resolved:standing-waiver",
            "--words", "human", "--note", "merged the reviewed head",
            "--quote-file", str(quote_file),
        ]
        self.assertEqual(self.run_main(argv), 0)
        self.assertTrue(self.last_row().endswith(f'quote="{quote}"'))
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo), "--check",
        ]), 0)

    def test_quote_file_strips_one_trailing_newline(self):
        quote_file = self.tmp / "refused-command.txt"
        quote_file.write_text("runtime denied command\n", encoding="utf-8")
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "merge", "--status", "resolved:standing-waiver",
            "--words", "human", "--note", "merged the reviewed head",
            "--quote-file", str(quote_file),
        ]), 0)
        self.assertTrue(self.last_row().endswith('quote="runtime denied command"'))

    def test_quote_file_refuses_an_interior_newline(self):
        quote_file = self.tmp / "refused-command.txt"
        quote_file.write_text("first\nsecond\n", encoding="utf-8")
        before = self.ledger.read_text()
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "merge", "--status", "resolved:standing-waiver",
            "--words", "human", "--note", "merged the reviewed head",
            "--quote-file", str(quote_file),
        ]), 1)
        self.assertIn("quote= is one line", self.err.getvalue())
        self.assertEqual(self.ledger.read_text(), before)

    def test_quote_and_quote_file_are_mutually_exclusive(self):
        quote_file = self.tmp / "refused-command.txt"
        quote_file.write_text("file quote", encoding="utf-8")
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "merge", "--status", "resolved:standing-waiver",
            "--words", "human", "--note", "merged the reviewed head",
            "--quote", "argument quote", "--quote-file", str(quote_file),
        ]), 1)
        self.assertIn("--quote", self.err.getvalue())
        self.assertIn("--quote-file", self.err.getvalue())

    def test_empty_quote_file_requires_words_none(self):
        quote_file = self.tmp / "empty.txt"
        quote_file.write_text("", encoding="utf-8")
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "merge", "--status", "resolved:standing-waiver",
            "--words", "human", "--note", "merged the reviewed head",
            "--quote-file", str(quote_file),
        ]), 1)
        self.assertIn("words=none", self.err.getvalue())

    def test_empty_quote_file_with_none_and_open_lands(self):
        quote_file = self.tmp / "empty.txt"
        quote_file.write_text("", encoding="utf-8")
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--kind", "merge", "--status", "open", "--words", "none",
            "--note", "awaiting review", "--quote-file", str(quote_file),
        ]), 0)
        self.assertIn("status=open", self.last_row())
        self.assertTrue(self.last_row().endswith('quote=""'))

    def test_open_gates_refuses_quote_file_as_an_append_argument(self):
        missing = self.tmp / "not-read.txt"
        self.assertEqual(self.run_main([
            "--ledger", str(self.ledger), "--repo", str(self.repo),
            "--open-gates", "--quote-file", str(missing),
        ]), 1)
        self.assertIn("--open-gates cannot be combined with append arguments", self.err.getvalue())
        self.assertNotIn("could not be read", self.err.getvalue())

    def test_ids_are_consecutive_and_read_from_the_file(self):
        self.assertEqual(self.append(), 0)
        self.assertEqual(self.append(), 0)
        ids = [l.split(" | ")[0] for l in self.ledger.read_text().splitlines()
               if gate_row.ID_RE.match(l)]
        self.assertEqual(ids, ["G1", "G2"])

    def test_resolves_refuses_never_open_and_already_closed_ids_and_accepts_open_id(self):
        self.assertEqual(self.append("--resolves", "G404"), 1)
        self.assertIn("G404", self.err.getvalue())
        self.assertIn("never-open", self.err.getvalue())

        self.assertEqual(self.append("--status", "open", "--words", "none", "--quote", ""), 0)
        self.assertEqual(self.append("--resolves", "G1"), 0)
        self.assertIn("resolves=G1", self.last_row())
        self.assertEqual(self.append("--resolves", "G1"), 1)
        self.assertIn("G1", self.err.getvalue())
        self.assertIn("already-closed", self.err.getvalue())

    def test_open_gate_mode_uses_last_rows_and_structured_resolves_only(self):
        rows = [
            self.fixture_row("G26", "open", "none", ""),
            self.fixture_row("G26", "open", "none", ""),
            self.fixture_row("G26", "resolved:done"),
            self.fixture_row("G27", "open", "none", "", note="prose says resolves=G27"),
            self.fixture_row("G28", "open", "none", ""),
            self.fixture_row("G29", "resolved:done", resolves="G28"),
            self.fixture_row("G30", "open", "none", ""),
        ]
        self.ledger.write_text("# fixture\n" + "\n".join(rows) + "\n")
        self.assertEqual(self.open_gates(), ["G27", "G30"])

    def test_words_values_require_the_matching_quote_presence(self):
        self.assertEqual(self.append("--status", "open", "--words", "none", "--quote", ""), 0)
        for words in ("seat", "human", "selected"):
            self.assertEqual(self.append("--words", words, "--quote", words), 0)
        self.assertEqual(self.append("--words", "none", "--quote", "not empty"), 1)
        self.assertIn("words=none", self.err.getvalue())
        self.assertEqual(self.append("--words", "seat", "--quote", ""), 1)
        self.assertIn("words=none", self.err.getvalue())

    def test_slug_ids_are_resolved_by_first_field(self):
        self.ledger.write_text(self.fixture_row("decision-abc", "open", "none", "") + "\n")
        self.assertEqual(self.append("--resolves", "decision-abc"), 0)
        self.assertIn("resolves=decision-abc", self.last_row())
        self.assertEqual(self.open_gates(), [])

    def test_a_count_that_does_not_match_the_range_is_rejected(self):
        """The recount rule as code: parts that do not sum fail --check."""
        base, head = self.rev("HEAD~2"), self.rev("HEAD")
        row = (f'G9 | 2026-09-06T00:00:00Z | kind=push | main@{head} | '
               f'status=resolved:standing-waiver | record=timely | '
               f'push={base}..{head} count=7 boundary="f1.txt f2.txt" '
               f'boundary-check="" | words=human | note=n | quote="q"')
        with self.assertRaises(gate_row.RowError) as ctx:
            gate_row.check(row, self.repo)
        self.assertIn("carries 2 commits", str(ctx.exception))

    def test_a_pipe_in_note_is_refused(self):
        """note= is the seat's own words, so it fails closed on the delimiter."""
        self.assertEqual(self.append("--note", "a | b"), 1)

    def test_a_pipe_in_quote_is_kept_verbatim(self):
        """G33: the Human typed a literal | inside their own words (G52)."""
        human = "à cho các lead revert lại model từ abc-tunnel về cliproxy gpt luna|zai/glm 5.3 flash đi"
        self.assertEqual(self.append("--quote", human), 0)
        self.assertTrue(self.last_row().endswith(f'quote="{human}"'))
        self.assertEqual(self.run_main(
            ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]), 0)

    def test_quote_marker_text_is_kept_verbatim(self):
        human = 'literal | quote=" text'
        self.assertEqual(self.append("--quote", human), 0)
        self.assertTrue(self.last_row().endswith(f'quote="{human}"'))
        self.assertEqual(self.run_main(
            ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]), 0)

    def test_narrative_over_the_cap_is_refused(self):
        self.assertEqual(self.append("--note", "x" * (gate_row.NOTE_MAX + 1)), 1)

    def test_an_undocumented_key_is_refused(self):
        """The drifted shape this project actually wrote must not pass."""
        head = self.rev("HEAD")
        row = (f'G9 | 2026-09-06T00:00:00Z | kind=push | main@{head} | '
               f'status=resolved:standing-waiver | authority=G64 | project=beo-skills | '
               f'record=timely | words=human | note=n | quote="q"')
        with self.assertRaises(gate_row.RowError) as ctx:
            gate_row.check(row, self.repo)
        self.assertIn("not in the row schema", str(ctx.exception))

    def add_remote(self, ref: str) -> None:
        """A bare origin holding `ref`, so ls-remote answers for real."""
        bare = self.tmp / "origin.git"
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(bare)], check=True)
        subprocess.run(["git", "-C", str(self.repo), "remote", "add", "origin", str(bare)],
                       check=True)
        subprocess.run(["git", "-C", str(self.repo), "push", "-q", "origin",
                        f"{self.rev(ref)}:refs/heads/main"], check=True, capture_output=True)

    def test_a_push_row_whose_push_has_not_landed_is_refused(self):
        """origin is a commit behind, so the row would claim a push that did not happen."""
        self.add_remote("HEAD~1")
        base = self.rev("HEAD~2")
        self.assertEqual(self.append("--kind", "push", "--push-base", base), 1)

    def test_a_landed_push_derives_its_own_count_and_boundary(self):
        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", self.rev("HEAD~2"),
                                     "--boundary", "f1.txt", "--boundary", "f2.txt"), 0)
        row = self.last_row()
        self.assertIn("count=2", row)
        self.assertIn('boundary="f1.txt f2.txt"', row)
        self.assertIn('boundary-check=""', row)

    def test_a_path_outside_the_boundary_is_named(self):
        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", self.rev("HEAD~2"),
                                     "--boundary", "f1.txt"), 0)
        row = self.last_row()
        self.assertIn('boundary="f1.txt"', row)
        self.assertIn('boundary-check="f2.txt"', row)

    def test_a_path_added_and_deleted_inside_the_range_is_still_named(self):
        """S1 F002's own reproduction. The two end trees agree; the union does not.

        This is the one input where a net `diff --name-only <base>..<head>` and the
        doctrine's `rev-list | diff-tree` union disagree, and it disagrees in the
        direction that lets an out-of-boundary write through clean.
        """
        base = self.rev("HEAD")
        (self.repo / "src").mkdir()
        (self.repo / "src" / "out-of-boundary.py").write_text("x\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "add outside the boundary")
        self.git("rm", "-q", "src/out-of-boundary.py")
        self.git("commit", "-qm", "delete it again")

        net = self.git("diff", "--name-only", f"{base}..HEAD")
        self.assertEqual(net, "", "the net tree diff must be empty, or this case proves nothing")

        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", base,
                                     "--boundary", "docs"), 0)
        row = self.last_row()
        self.assertIn("count=2", row)
        self.assertIn('boundary-check="src/out-of-boundary.py"', row)

    def test_a_boundary_flag_holding_several_joined_paths_is_refused(self):
        """The shape three ledgers actually wrote: one --boundary holding a joined list.

        `--boundary` is `action="append"`, one flag per path, so a joined value is a
        single string no path can equal or sit under. Every changed path then reads
        as outside the boundary and the row is indistinguishable from one that
        declared no boundary at all — which is why it fails closed here instead.
        """
        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", self.rev("HEAD~2"),
                                     "--boundary", "f1.txt f2.txt"), 1)

    def test_a_changed_path_holding_a_space_is_refused(self):
        """boundary-check joins paths with spaces, so such a path cannot be read back."""
        base = self.rev("HEAD")
        (self.repo / "two words.txt").write_text("x\n")
        self.git("add", "-A")
        self.git("commit", "-qm", "a path with a space")
        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", base,
                                     "--boundary", "docs"), 1)

    def valid_push_row(self) -> tuple[str, list[str]]:
        """One push row the script built itself, with the boundary it was built against."""
        boundary = ["f1.txt", "f2.txt"]
        self.add_remote("HEAD")
        self.assertEqual(self.append(
            "--kind", "push", "--push-base", self.rev("HEAD~2"),
            "--channel", "supervisor-relay:typed", "--writer", "lead-beo-skills",
            *[a for b in boundary for a in ("--boundary", b)]), 0)
        return self.last_row(), boundary

    def test_the_control_row_still_checks_out(self):
        """The matrix below only means something if the unmodified row passes."""
        row, boundary = self.valid_push_row()
        gate_row.check(row, self.repo)

    def test_every_tamper_the_receive_record_found_passing_is_now_refused(self):
        """S1 F001's six-of-six matrix: one field hand-edited at a time, re-checked."""
        row, boundary = self.valid_push_row()
        tampers = {
            "boundary-check": ('boundary-check=""', 'boundary-check="src/fabricated.py"'),
            "boundary": ('boundary="f1.txt f2.txt"', 'boundary="f1.txt"'),
            "record": ("record=timely", "record=bogus"),
            "quote": ('quote="merge it"', 'quote=""'),
            "head": (f"main@{self.rev('HEAD')}", f"main@{'0' * 40}"),
            "channel": ("channel=supervisor-relay:typed", "channel=bogus:bogus"),
            "writer": ("writer=lead-beo-skills", "writer=NOT_A_SEAT"),
        }
        for name, (before, after) in tampers.items():
            with self.subTest(name):
                tampered = row.replace(before, after)
                self.assertNotEqual(tampered, row, "the tamper did not change the row")
                with self.assertRaises(gate_row.RowError):
                    gate_row.check(tampered, self.repo)

    def test_check_derives_a_push_row_with_no_boundary_flag(self):
        """The point of the slice: every input the check needs is in the row.

        Before the boundary was carried in the block, this exact invocation was
        refused — the caller had to re-supply the declared paths from memory,
        which is a derived field taking an underived input.
        """
        self.valid_push_row()
        self.assertEqual(self.run_main(
            ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]), 0)

    def test_a_push_row_with_no_declared_boundary_never_reaches_the_ledger(self):
        """The append-only file does not get a row the same command then rejects.

        The refusal moved from after the write to before it: `build` needs the
        boundary to derive the block at all, so a missing one fails while the
        ledger is still untouched.
        """
        self.add_remote("HEAD")
        before = self.ledger.read_text()
        self.assertEqual(self.append("--kind", "push",
                                     "--push-base", self.rev("HEAD~2")), 1)
        self.assertIn("a push row needs --boundary", self.err.getvalue())
        self.assertEqual(self.ledger.read_text(), before, "the refused row landed anyway")

    def test_a_row_declaring_an_empty_boundary_is_refused(self):
        """`build` cannot write one, so only a hand-edited row carries it."""
        row, _ = self.valid_push_row()
        empty = row.replace('boundary="f1.txt f2.txt"', 'boundary=""')
        self.assertNotEqual(empty, row)
        with self.assertRaises(gate_row.RowError) as ctx:
            gate_row.check(empty, self.repo)
        self.assertIn("empty boundary", str(ctx.exception))

    def test_a_dot_boundary_covers_the_whole_repository(self):
        """`.` prefixes no repo-relative path, so it used to invert its own meaning.

        Declaring the whole tree produced the whole changed set as *outside* it —
        the over-claiming shape, from the one declaration that means the opposite.
        """
        self.add_remote("HEAD")
        self.assertEqual(self.append("--kind", "push", "--push-base", self.rev("HEAD~2"),
                                     "--boundary", "."), 0)
        row = self.last_row()
        self.assertIn('boundary="."', row)
        self.assertIn('boundary-check=""', row)

    def test_a_row_outlives_the_branch_that_named_it(self):
        """G104 and G109: a merge deletes the branch, the row stays checkable.

        The head is verified as an object, so the row is re-derivable from the
        checkout for as long as the commit is reachable.
        """
        self.git("checkout", "-q", "-b", "topic")
        self.assertEqual(self.append(), 0)
        row = self.last_row()
        self.assertIn("topic@", row)
        self.git("checkout", "-q", "main")
        self.git("branch", "-D", "topic")
        gate_row.check(row, self.repo)

    def test_the_branch_label_is_no_longer_verified_and_that_is_the_trade(self):
        """Stated as a test so the loss is on the record, not discovered later.

        A row names the branch its head sat on. That is history, not a fact any
        command re-derives: once the branch is deleted or moved, nothing in the
        repository says what a commit was on. Verifying it against live refs
        made the same row pass today and fail tomorrow, which is the failure
        `test_a_row_outlives_the_branch_that_named_it` records. The head SHA
        carries the verification instead, and the label is read as prose.
        """
        row, _ = self.valid_push_row()
        relabelled = row.replace("main@", "nonexistent-branch@")
        self.assertNotEqual(relabelled, row)
        gate_row.check(relabelled, self.repo)
        with self.assertRaises(gate_row.RowError):
            gate_row.check(row.replace(f"main@{self.rev('HEAD')}", f"main@{'0' * 40}"),
                           self.repo)

    def test_a_kind_push_row_carries_all_four_push_fields_or_no_row_exists(self):
        """The acceptance criterion stated on row CONTENT, not on --check's verdict.

        `--check` is the instrument that could not see this defect: on the parent
        it printed a byte-identical `ok` for a verified push row and for a
        vacuous one, so a criterion phrased as "--check passes" is satisfied by
        exactly the row the slice exists to prevent. Phrased on content, it is
        not: either the row holds the range, the count, the declared boundary and
        the boundary-check, or the append was refused and no row exists at all.
        """
        self.add_remote("HEAD")
        before = self.ledger.read_text()

        # Arm A: kind=push with no --push-base. No row may exist.
        self.assertEqual(self.append("--kind", "push", "--boundary", "f1.txt"), 1)
        self.assertEqual(self.ledger.read_text(), before)

        # Arm B: the same row supplied properly. Every field present, by content.
        self.assertEqual(self.append(
            "--kind", "push", "--push-base", self.rev("HEAD~2"),
            "--boundary", "f1.txt", "--boundary", "f2.txt"), 0)
        row = self.last_row()
        self.assertIn("kind=push", row)
        for field in ("push=", "count=", 'boundary="', 'boundary-check="'):
            self.assertIn(field, row, f"a kind=push row must carry {field}")
        self.assertRegex(row, r"push=[0-9a-f]{7,40}\.\.[0-9a-f]{7,40} count=\d+ "
                              r'boundary="[^"]+" boundary-check="[^"]*"')

    def test_a_push_row_without_push_base_never_reaches_the_ledger(self):
        """The live defect B7 hit: kind and block were controlled independently.

        The parent gated the whole block on `--push-base`, so this exact
        invocation appended `kind=push` with no range, no count, no boundary and
        no boundary-check, skipped the `ls-remote` proof that the push landed,
        and silently dropped the `--boundary` that was passed. The row asserted a
        push and carried nothing that could contradict it.
        """
        self.add_remote("HEAD")
        before = self.ledger.read_text()
        self.assertEqual(self.append("--kind", "push", "--boundary", "f1.txt"), 1)
        self.assertIn("a push row needs --push-base", self.err.getvalue())
        self.assertEqual(self.ledger.read_text(), before, "the refused row landed anyway")

    def test_a_kind_push_row_with_no_push_block_is_refused_by_check(self):
        """The other half: the checker confirmed such a row instead of failing it.

        `check` validated a push block only where one was present, so a
        `kind=push` row without one was checked against nothing and returned
        `ok`. Both halves are needed — repairing `build` alone still passes every
        row already written that way.
        """
        row, _ = self.valid_push_row()
        blockless = re.sub(r" \| push=[^|]+", " ", row)
        self.assertNotIn("push=", blockless)
        self.assertIn("kind=push", blockless)
        self.ledger.write_text(blockless + "\n")
        self.assertEqual(self.run_main(
            ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]), 1)
        self.assertIn("carries no push block", self.err.getvalue())

    def test_push_base_on_a_non_push_row_is_refused_rather_than_dropped(self):
        """An argument accepted and silently ignored is the same defect mirrored.

        The parent emitted a push block on any row given `--push-base`, whatever
        its kind. Tying the block to the kind closes that direction too, and says
        so instead of quietly doing nothing.
        """
        self.add_remote("HEAD")
        before = self.ledger.read_text()
        self.assertEqual(self.append("--push-base", self.rev("HEAD~2"),
                                     "--boundary", "f1.txt"), 1)
        self.assertIn("only meaningful on a push row", self.err.getvalue())
        self.assertEqual(self.ledger.read_text(), before, "the refused row landed anyway")

    def test_boundary_on_a_non_push_row_is_refused_rather_than_dropped(self):
        """The other half of the mirror, and the defect this slice itself left.

        The first pass refused `--push-base` on a non-push row and left
        `--boundary` accepted and silently discarded — the same class the slice
        exists to close, reintroduced one line away from the fix. Both arguments
        only mean anything inside a push block, so both are refused when there is
        no block to put them in.
        """
        before = self.ledger.read_text()
        self.assertEqual(self.append("--boundary", "f1.txt"), 1)
        self.assertIn("--boundary is only meaningful on a push row", self.err.getvalue())
        self.assertEqual(self.ledger.read_text(), before, "the refused row landed anyway")

    def test_a_row_over_claiming_the_whole_changed_set_is_refused(self):
        """The shape six rows across two ledgers already carry.

        `--boundary` is `action="append"`, one flag per path; a seat that passes
        all its paths joined in a single flag declares one string no path can
        match, so every path lands outside and the row records the entire
        changed set. That row asserts a breach that did not happen, and against
        an empty boundary the derivation reproduces it exactly.
        """
        row, boundary = self.valid_push_row()
        p = re.search(r'boundary-check="([^"]*)"', row)
        self.assertEqual(p.group(1), "", "the control row declares no breach")
        base = self.rev("HEAD~2")
        changed = sorted({
            path
            for commit in self.git("rev-list", f"{base}..HEAD").splitlines()
            for path in self.git("diff-tree", "--root", "-m", "--no-commit-id",
                                 "--name-only", "-r", commit).splitlines()
            if path
        })
        self.assertTrue(set(boundary) & set(changed), "the range touches the boundary")
        over = row.replace('boundary-check=""', f'boundary-check="{" ".join(changed)}"')
        self.assertNotEqual(over, row)
        self.ledger.write_text(over + "\n")
        argv = ["--ledger", str(self.ledger), "--repo", str(self.repo), "--check"]
        self.assertEqual(self.run_main(argv), 1)
        self.assertIn("outside the declared boundary", self.err.getvalue())


if __name__ == "__main__":
    unittest.main()
