"""charter_render fills the Reviewer charter template from one Lead command line."""
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import support
import backend
import charter_lint
import charter_render
import state_root
from fake_backend import FakeBackend

SCRIPTS = support.ADW / "scripts"
LEAD = "w7:p1"
OPEN_BACKEND = backend.open_backend


def setUpModule() -> None:
    support.never_run("git")


class CharterRenderTest(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory(dir=os.path.realpath("/tmp"))
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        self.repo = root / "repo"
        state = root / "state"
        patched = mock.patch.object(state_root, "STATE_ROOT", state)
        patched.start()
        self.addCleanup(patched.stop)
        self.run_dir = state_root.run_dir("demo", "demo-run")
        self.run_dir.mkdir(parents=True)
        state_root.config("demo").write_text(json.dumps({
            "lead-kind": "claude", "lead-args": ["--model", "claude-opus-5-5"],
            "reviewer-kind": "claude", "reviewer-args": ["--model", "claude-sonnet-5-5"],
            "target-line": "main",
        }), encoding="utf-8")
        (self.run_dir / "evidence-x.log").write_text("Ran 1 OK\n", encoding="utf-8")
        support.temp_git_repo(self.repo)
        for names, subject in ((("AGENTS.md",), "docs: guidance"), (("é/AGENTS.md", "é/b.py"), "feat(é): add b")):
            for name in names:
                (self.repo / name).parent.mkdir(exist_ok=True)
                (self.repo / name).write_text("x\n", encoding="utf-8")
            support.git(self.repo, "add", *names)
            support.git(self.repo, "commit", "-q", "-m", subject)
        self.base, self.head = support.git(self.repo, "rev-parse", "HEAD~1", "HEAD").split()
        self.staffing = self.run_dir / "staffing.txt"
        self.write_staffing("MODE: solo-Lead\nLEAD: kind=claude model=claude-opus-5-5 workspace=w7\n")
        self.fake = FakeBackend()
        opened = mock.patch.object(backend, "open_backend", return_value=self.fake)
        opened.start()
        self.addCleanup(opened.stop)

    def write_staffing(self, seats: str) -> None:
        self.staffing.write_text(
            f"{seats}HEAD: {self.head}\nREVIEWER: review-x kind=claude model=m posture=allowlisted "
            "dialog=absent dialog-tools=none dialog-deny=none dialog-source=inventory skills=none "
            f"extensions=none fence=none(test) seat=w7:p3 workspace=w7 head={self.head}\n",
            encoding="utf-8",
        )

    def render(self, *extra: str) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = charter_render.main([
                "--repo", str(self.repo), "--run-dir", str(self.run_dir), "--base", self.base,
                "--head", self.head, "--pane", "w7:p3", "--lead", LEAD, "--lane", "normal", "--reason", "new script",
                "--boundary", "b.py exists", "--validation", "G1", "--check", "git diff --check",
                "--staffing", str(self.staffing),
                *extra,
            ])
        return code, out.getvalue(), err.getvalue()

    def test_rendered_charter_passes_charter_lint(self):
        code, out, err = self.render()
        self.assertEqual((code, err), (0, ""))
        charter = self.run_dir / f"charter-review-{self.head[:12]}.md"
        self.assertTrue(out.startswith(f"{charter} sha256="))
        text = charter.read_text(encoding="utf-8")
        for expected in (
            f"Reviewed unit: the range {self.base}..{self.head} (1 commit: {self.head[:7]}).",
            "Mode: solo-Lead. Declared source scope: é/AGENTS.md, é/b.py.",
            f"Scope authors (staffing record): {LEAD} (claude claude-opus-5-5).",
            f"Governing contracts: {self.repo}/AGENTS.md, {self.repo}/é/AGENTS.md;",
            "seat w7:p3",
            self.fake.send_block(LEAD, f"{self.run_dir}/report-review-{self.head[:12]}.md").text,
            "1. git diff --check",
            f"`python3 {SCRIPTS / 'bounded_run.py'} --seconds N -- CMD`",
        ):
            self.assertIn(expected, text)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as lint_err:
            lint = charter_lint.main([
                "--charter", str(charter), "--lead", LEAD, "--staffing", str(self.staffing), "--repo", str(self.repo),
            ])
        self.assertEqual((lint, lint_err.getvalue()), (0, ""))

    def render_with_template(self, template: str, pane: str = "w7:p3", lead: str = LEAD) -> tuple[int, str]:
        path = self.run_dir.parent / "template.txt"
        path.write_text(template, encoding="utf-8")
        with mock.patch.object(charter_render, "TEMPLATE", path):
            code, _, err = self.render("--pane", pane, "--lead", lead)
        return code, err

    def test_the_send_block_is_the_backends_block_for_the_run_report(self):
        code, err = self.render_with_template("<pane_id>\n<send_block>\n")
        self.assertEqual((code, err), (0, ""))
        report = f"{self.run_dir}/report-review-{self.head[:12]}.md"
        self.assertEqual(self.fake.calls, [("send_block", LEAD, report)])
        text = (self.run_dir / f"charter-review-{self.head[:12]}.md").read_text(encoding="utf-8")
        self.assertEqual(text, f"w7:p3\n{self.fake.send_block(LEAD, report).text}\n")

    def test_the_seat_handle_is_taken_as_given(self):
        for handle in ("t7", "sess.blk", "w7:p3"):
            with self.subTest(handle=handle):
                code, err = self.render_with_template("<pane_id>", handle)
                self.assertEqual((code, err), (0, ""))
                text = (self.run_dir / f"charter-review-{self.head[:12]}.md").read_text(encoding="utf-8")
                self.assertEqual(text, handle)

    def test_the_lead_handle_is_the_one_given_not_a_name_derived_from_the_project(self):
        code, err = self.render_with_template("<lead_name>\n<send_block>\n", "w7:p3", "t9")
        self.assertEqual((code, err), (0, ""))
        report = f"{self.run_dir}/report-review-{self.head[:12]}.md"
        self.assertEqual(self.fake.calls, [("send_block", "t9", report)])
        text = (self.run_dir / f"charter-review-{self.head[:12]}.md").read_text(encoding="utf-8")
        self.assertEqual(text, f"t9\n{self.fake.send_block('t9', report).text}\n")

    def test_the_backend_flag_reaches_detect_as_explicit(self):
        out, err = io.StringIO(), io.StringIO()
        with mock.patch.object(backend, "open_backend", wraps=OPEN_BACKEND), \
                mock.patch.object(backend, "detect", side_effect=backend.DetectionError("stop")) as detect, \
                contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            code = charter_render.main([
                "--repo", str(self.repo), "--run-dir", str(self.run_dir), "--base", self.base,
                "--head", self.head, "--pane", "w7:p3", "--lead", LEAD, "--lane", "normal", "--reason", "r",
                "--boundary", "b", "--validation", "G1", "--check", "c", "--staffing", str(self.staffing),
                "--backend", "herdr@w7:p3",
            ])
        self.assertEqual((code, err.getvalue()), (1, "charter_render: stop\n"))
        self.assertEqual(detect.call_args.args[1], backend.Explicit("herdr", "w7:p3"))

    def test_a_backend_that_cannot_render_the_send_block_fails_closed(self):
        self.fake.script("send_block", ValueError("not a seat handle"))
        code, err = self.render_with_template("<send_block>")
        self.assertEqual((code, err), (1, "charter_render: not a seat handle\n"))
        self.assertEqual(list(self.run_dir.glob("charter-*")), [])

    def merge_main(self, land: bool) -> str:
        """Merge a later main commit into the head; origin/HEAD is origin/main. Returns the merge."""
        git = lambda *a: support.git(self.repo, *a)
        bare = support.temp_git_repo(self.repo.parent / "origin.git", bare=True)
        git("remote", "add", "origin", str(bare))
        git("checkout", "-q", "-b", "trunk", self.base)
        (self.repo / "main.txt").write_text("main\n", encoding="utf-8")
        git("add", "main.txt")
        git("commit", "-q", "-m", "main")
        git("push", "-q", "origin", f"{self.base if not land else 'HEAD'}:refs/heads/main")
        git("fetch", "-q", "origin")
        git("remote", "set-head", "origin", "main")
        git("checkout", "-q", "-B", "work", self.head)
        git("merge", "-q", "--no-edit", "trunk")
        return git("rev-parse", "HEAD")

    def partitioned(self, owned: str) -> None:
        self.write_staffing(
            "MODE: partitioned\nLEAD: kind=claude model=claude-opus-5-5 workspace=w7\n"
            f"ENGINEER: eng-a kind=claude model=claude-haiku-5-5 posture=bypassed seat=w7:p4 owned={owned} extensions=none\n"
            "ENGINEER: eng-b kind=pi model=luna posture=bypassed seat=w7:p5 owned=docs/ extensions=none\n"
        )

    def test_partitioned_authors_are_the_engineers_owning_the_changed_paths(self):
        self.partitioned("é/")
        code, _, err = self.render()
        self.assertEqual((code, err), (0, ""))
        text = (self.run_dir / f"charter-review-{self.head[:12]}.md").read_text(encoding="utf-8")
        self.assertIn("Mode: partitioned. Declared source scope: é/AGENTS.md, é/b.py. "
                      "Scope authors (staffing record): eng-a (claude claude-haiku-5-5).", text)

    def test_a_changed_path_with_no_engineer_owner_is_refused(self):
        self.partitioned("é/b.py")
        code, _, err = self.render()
        self.assertEqual(code, 1)
        self.assertIn("é/AGENTS.md has no ENGINEER owner", err)

    def test_a_staffing_record_without_a_mode_is_refused(self):
        self.write_staffing("LEAD: kind=claude model=claude-opus-5-5 workspace=w7\n")
        code, _, err = self.render()
        self.assertEqual(code, 1)
        self.assertIn("has no MODE: solo-Lead or MODE: partitioned line", err)

    def test_a_clean_merge_of_landed_main_leaves_main_out_of_the_scope(self):
        self.partitioned("é/")
        head = self.merge_main(land=True)
        code, _, err = self.render("--head", head)
        self.assertEqual((code, err), (0, ""))
        text = (self.run_dir / f"charter-review-{head[:12]}.md").read_text(encoding="utf-8")
        self.assertIn("Declared source scope: é/AGENTS.md, é/b.py.", text)

    def test_an_unlanded_main_commit_needs_an_owner(self):
        self.partitioned("é/")
        code, _, err = self.render("--head", self.merge_main(land=False))
        self.assertEqual(code, 1)
        self.assertIn("main.txt has no ENGINEER owner", err)

    def test_a_conflict_resolving_merge_owner_checks_its_own_content(self):
        git = lambda *a: support.git(self.repo, *a)
        git("checkout", "-q", "-b", "side", self.head)
        (self.repo / "é" / "b.py").write_text("side\n", encoding="utf-8")
        git("commit", "-q", "-am", "side")
        git("checkout", "-q", "-B", "work", self.head)
        (self.repo / "é" / "b.py").write_text("work\n", encoding="utf-8")
        git("commit", "-q", "-am", "work")
        with self.assertRaises(subprocess.CalledProcessError):
            git("merge", "-q", "side")
        (self.repo / "é" / "b.py").write_text("resolved\n", encoding="utf-8")
        (self.repo / "evil.txt").write_text("evil\n", encoding="utf-8")
        git("add", "-A")
        git("commit", "-q", "-m", "merge side")
        self.partitioned("é/")
        code, _, err = self.render("--head", git("rev-parse", "HEAD"))
        self.assertEqual(code, 1)
        self.assertIn("evil.txt has no ENGINEER owner", err)

    def test_a_lead_line_without_kind_and_model_is_refused(self):
        self.write_staffing("MODE: solo-Lead\nLEAD: workspace=w7\n")
        code, _, err = self.render()
        self.assertEqual(code, 1)
        self.assertIn("LEAD line lacks kind= or model=", err)

    def test_owned_globs_cross_directories_only_with_a_double_star(self):
        for entry, path, owned in (
            ("src/*.py", "src/a.py", True), ("src/*.py", "src/x/a.py", False),
            ("*.md", "x/y.md", False), ("a?.md", "a/.md", False),
            ("src/**/*.py", "src/a.py", True), ("src/**/*.py", "src/x/y/a.py", True),
            ("src/**", "src/x/a.py", True), ("docs/", "docs/x/y.md", True),
            ("app/[id].tsx", "app/[id].tsx", True), ("app/[id].tsx", "app/i.tsx", False),
        ):
            with self.subTest(entry=entry, path=path):
                self.assertEqual(charter_render._owns(entry, path), owned)

    def test_refuses_an_abbreviated_head(self):
        code, _, err = self.render("--head", self.head[:12])
        self.assertEqual(code, 1)
        self.assertIn("--head must be the full 40-hex SHA", err)


if __name__ == "__main__":
    unittest.main()
