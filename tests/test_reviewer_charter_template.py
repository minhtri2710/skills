"""The Reviewer charter template carries every clause charter_lint requires of a Reviewer."""
from __future__ import annotations

import contextlib
import io
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
import unittest.mock
from pathlib import Path

import support
import backend
import charter_lint
import charter_render
import state_root
from backends import herdr
from fake_backend import FakeBackend

SKILL = support.ADW


def setUpModule() -> None:
    # git and the interpreter are the scripts' own; bash and sandbox-exec run the report-block and fence tests.
    support.never_run("git", sys.executable, "bash", "sandbox-exec")


TEMPLATE = SKILL / "templates" / "reviewer-charter.txt"
REPORT_BLOCK = SKILL / "templates" / "report-by-prompt.txt"
FENCE = SKILL / "templates" / "reviewer-write-fence.sb"
LEAD = "lead-beo-skills"


def staffing(head: str) -> str:
    return (
        "MODE: solo-Lead\n"
        "LEAD: kind=claude model=claude-opus-5-5 workspace=w1\n"
        f"HEAD: {head}\n"
        "REVIEWER: review-aaaaaaaaaaaa kind=claude model=claude-opus-5-5 posture=allowlisted "
        f"dialog=denied dialog-tools=ask_user_question dialog-deny=ask_user_question dialog-source=pi-1.0.4-runtime-inventory skills=none extensions=none fence=none(no OS write fence is needed) "
        f"seat=w1:p1 workspace=w1 head={head}\n"
    )


class ReviewerCharterTemplateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._repo_tmp = tempfile.TemporaryDirectory(dir=os.path.realpath("/tmp"))
        cls.repo = Path(cls._repo_tmp.name)
        cls.addClassCleanup(cls._repo_tmp.cleanup)
        support.temp_git_repo(cls.repo)
        for message in ("base", "head"):
            support.git(cls.repo, "commit", "-q", "--allow-empty", "-m", message)
        cls.base, cls.head = support.git(cls.repo, "rev-parse", "HEAD~1", "HEAD").split()

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=os.path.realpath("/tmp"))
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        patched = unittest.mock.patch.object(state_root, "STATE_ROOT", self.tmp / "state")
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
        self.staffing = self.run_dir / "staffing.txt"
        self.staffing.write_text(staffing(self.head), encoding="utf-8")
        self.peer = f"review-{self.head[:12]}"
        self.filled = self.render(FakeBackend())

    def render(self, seats: backend.Backend) -> str:
        with unittest.mock.patch.object(backend, "open_backend", return_value=seats), \
                contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()) as err:
            code = charter_render.main([
                "--repo", str(self.repo), "--run-dir", str(self.run_dir), "--base", self.base,
                "--head", self.head, "--pane", "w1:p1", "--lead", LEAD, "--lane", "normal",
                "--reason", "r", "--boundary", "b", "--validation", "G1", "--check", "git diff --check",
                "--staffing", str(self.staffing),
            ])
        self.assertEqual((code, err.getvalue()), (0, ""))
        return (self.run_dir / f"charter-{self.peer}.md").read_text(encoding="utf-8")

    def run_lint(self, charter: str, seats: backend.Backend | None = None) -> tuple[int, str]:
        charter_path = self.tmp / "charter.md"
        charter_path.write_text(charter, encoding="utf-8")
        stderr = io.StringIO()
        opened = unittest.mock.patch.object(
            charter_lint.backend, "open_backend", return_value=seats or FakeBackend()
        )
        with opened, contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
            rc = charter_lint.main(
                ["--charter", str(charter_path), "--lead", LEAD, "--staffing", str(self.staffing),
                 "--repo", str(self.repo)]
            )
        return rc, stderr.getvalue()

    def test_placeholders_are_snake_case_slots(self):
        for template in (TEMPLATE, REPORT_BLOCK):
            with self.subTest(template=template.name):
                # A quoted heredoc opener (<<') in the report block is shell syntax, not a slot.
                text = template.read_text(encoding="utf-8").replace("<<'", "'")
                self.assertEqual(
                    charter_lint.PLACEHOLDER_RE.findall(text),
                    [m.group(0) for m in charter_render.SLOT_RE.finditer(text)],
                )

    def test_report_block_names_each_part_of_the_send_block(self):
        text = REPORT_BLOCK.read_text(encoding="utf-8")
        for field in backend.SendBlock._fields:
            with self.subTest(field=field):
                self.assertIn(field.replace("_", " "), text)

    def test_the_filled_charter_holds_the_send_block_of_the_backend_that_rendered_it(self):
        block = herdr.Adapter({}).send_block(LEAD, f"{self.run_dir}/report-{self.peer}.md")
        filled = self.render(herdr.Adapter({}))
        self.assertIn(block.text, filled)
        self.assertEqual(self.run_lint(filled, herdr.Adapter({})), (0, ""))
        rc, err = self.run_lint(filled)
        self.assertEqual(rc, 1)
        self.assertIn("missing report-by-prompt block, as fake renders it", err)

    def test_report_block_no_write_form_writes_hostile_body_verbatim(self):
        form = re.search(
            r"`(cat > <run_dir>/report-<peer_name>\.md <<(\S+))`",
            REPORT_BLOCK.read_text(encoding="utf-8"),
        )
        self.assertIsNotNone(form)
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "ran"
            body = (
                f"Verdict: PASS $HOME `id` $(touch {marker}) \"dq\" 'sq' \\n\n"
                f"EOF\nEND\ntouch {marker}\n"
            )
            command = form.group(1).replace("<run_dir>", tmp).replace("<peer_name>", "review-x")
            delimiter = form.group(2).strip("'\"").replace("<peer_name>", "review-x")
            subprocess.run(["bash", "-c", f"{command}\n{body}{delimiter}\n"], check=True, stdin=subprocess.DEVNULL)
            self.assertEqual((Path(tmp) / "report-review-x.md").read_text(encoding="utf-8"), body)
            self.assertFalse(marker.exists())

    def test_report_block_sends_every_peer_route_by_prompt(self):
        lead = (SKILL / "references" / "lead.md").read_text(encoding="utf-8")
        section = lead.split("\n### Routes\n", 1)[1].split("\n### ", 1)[0]
        routes = re.findall(r"^- `([A-Z_]+)`", section, re.M)
        self.assertGreaterEqual(len(routes), 4)
        lines = [l for l in REPORT_BLOCK.read_text(encoding="utf-8").splitlines() if f"`{routes[0]}`" in l]
        self.assertEqual(len(lines), 1)
        for route in routes:
            self.assertIn(f"`{route}`", lines[0])

    @unittest.skipUnless(shutil.which("sandbox-exec"), "sandbox-exec is macOS-only")
    def test_write_fence_admits_only_its_targets(self):
        if subprocess.run(["sandbox-exec", "-p", "(version 1)(allow default)", "true"], stdin=subprocess.DEVNULL).returncode:
            self.skipTest("inside a sandbox already: sandbox_apply refuses a nested profile")
        # Every temp root is admitted, so the denied targets live outside them.
        with tempfile.TemporaryDirectory(dir="/Users/Shared") as outside:
            root = Path(outside)
            # A kind's runtime-state-paths: a directory and a file it writes beside it.
            state_paths = [f"{root}/state", f"{root}/kind.json"]
            values = {"run_dir": f"{root}/.agent-delivery/projects/p/runs/2026-09-30", "peer_name": "review-45fa5929e7c1"}
            run_dir, name = Path(values["run_dir"]), values["peer_name"]
            # As a Lead fills it: a "." in a slot value becomes "\." on the regex lines.
            fill = lambda line: charter_render.SLOT_RE.sub(
                lambda m: values[m.group(1)].replace(".", "\\.") if "(regex" in line else values[m.group(1)], line)
            profile = root / "fence.sb"
            # Comments stay as written; the <kind_state_path> rule repeats once per runtime-state-paths entry.
            lines = FENCE.read_text(encoding="utf-8").splitlines(True)
            profile.write_text("".join(
                l if l.startswith(";")
                else "".join(fill(l.replace("<kind_state_path>", p.replace(".", "\\."))) for p in state_paths)
                if "<kind_state_path>" in l else fill(l)
                for l in lines))
            for d in (run_dir, root / "state", root / "Xagent-delivery/projects/p/runs/2026-09-30"):
                d.mkdir(parents=True)
            report, send = run_dir / f"report-{name}.md", run_dir / f"send-{name}.txt"
            allowed = [report, send, Path(f"{report}.tmp.17614.7a0e172e9fe4"), Path(f"{send}.tmp.1.0"),
                       root / "state/session", root / "kind.json", Path(f"{root}/kind.json.tmp.1.a"),
                       self.tmp / "scratch"]
            denied = [run_dir / "other.md", run_dir / "report-review-other.md", run_dir / f"send-{name}.md",
                      root / ".agent-delivery/gates.md",
                      root / "checkout-file", root / "stateX", root / "kind.jsonX", root / "kind.json.bak",
                      root / f"Xagent-delivery/projects/p/runs/2026-09-30/report-{name}.md",
                      Path(str(report).replace("45fa5929e7c1.md", "45fa5929e7c1Xmd")),
                      *(Path(f"{report}{s}") for s in (".tmp", ".bak", "x", ".tmp.1.0.x", ".tmp.1.g", ".tmp..a", ".tmp.1.", ".tmpX1.0", ".tmp.1X0", ".tmp.1.d/x"))]
            Path(f"{report}.tmp.1.d").mkdir()
            for path in allowed + denied:
                with self.subTest(path=str(path)):
                    run = subprocess.run(["sandbox-exec", "-f", str(profile), "touch", str(path)],
                                         capture_output=True, text=True, stdin=subprocess.DEVNULL)
                    self.assertEqual(path.exists(), path in allowed, run.stderr)
                    if path in denied:
                        self.assertIn("Operation not permitted", run.stderr)

    def test_the_rendered_floor_guard_command_runs_under_floor_guards_argparse(self):
        command = re.search(r"`python3 (\S+/floor_guard\.py [^`]*)`", self.filled)
        self.assertIsNotNone(command)
        run = subprocess.run([sys.executable, *shlex.split(command.group(1))],
                             capture_output=True, text=True, stdin=subprocess.DEVNULL)
        self.assertEqual((run.returncode, run.stdout, run.stderr), (0, "floor-guard: clean\n", ""))

    def test_removing_any_required_clause_fails_naming_it(self):
        self.assertEqual(self.run_lint(self.filled), (0, ""))
        block = FakeBackend().send_block(LEAD, f"{self.run_dir}/report-{self.peer}.md")
        removals = [
            (f"{clause.name}[{i}]", lambda t, p=pattern: p.sub("", t), f"charter_lint: {clause.message}")
            for clause in charter_lint.REQUIRED_CLAUSES
            if clause.dispositions is None or "reviewer" in clause.dispositions
            for i, pattern in enumerate(clause.patterns)
        ]
        removals += [
            ("disposition", lambda t: charter_lint.DISPOSITION_RE.sub("", t),
             "charter_lint: missing Disposition: Engineer / Reviewer / Architect line"),
            ("report file path", lambda t: charter_lint.REPORT_FILE_RE.sub("", t),
             "charter_lint: missing report-by-prompt block: absolute <run-dir>/report-<peer>.md path"),
        ]
        removals.append(("send command", lambda t: t.replace(block.send_command, ""),
                         "charter_lint: missing report-by-prompt block, as fake renders it:"))
        for name, remove, message in removals:
            with self.subTest(clause=name):
                stripped = remove(self.filled)
                self.assertNotEqual(stripped, self.filled, f"template lacks {name}")
                rc, err = self.run_lint(stripped)
                self.assertEqual(rc, 1)
                problems = [line for line in err.splitlines() if line.startswith("charter_lint:")]  # the send-block problem spans lines
                self.assertEqual(problems, [message], err)


if __name__ == "__main__":
    unittest.main()
