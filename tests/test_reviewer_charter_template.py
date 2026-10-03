"""The Reviewer charter template carries every clause charter_lint requires of a Reviewer."""
from __future__ import annotations

import ast
import contextlib
import inspect
import io
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow"
sys.path.insert(0, str(SKILL / "scripts"))

import charter_lint  # noqa: E402

TEMPLATE = SKILL / "templates" / "reviewer-charter.txt"
REPORT_BLOCK = SKILL / "templates" / "report-by-prompt.txt"
FENCE = SKILL / "templates" / "reviewer-write-fence.sb"
LEAD = "lead-beo-skills"
SLOT_RE = re.compile(r"<([a-z][a-z0-9_]*)>")
NOT_CLAUSES = {
    "SEAT_RE", "PLACEHOLDER_RE", "RANGE_RE", "STAFFED_HEAD_RE",
    "PRIOR_RE", "PRIOR_GLOSS_RE", "UNIT_RANGE_RE", "SHORT_SHA_RE",
}


def staffing(head: str) -> str:
    return (
        "MODE: solo-Lead\n"
        "LEAD: kind=claude model=claude-opus-5-5 workspace=w1\n"
        f"HEAD: {head}\n"
        "REVIEWER: review-aaaaaaaaaaaa kind=claude model=claude-opus-5-5 posture=allowlisted "
        f"dialog=denied skills=none extensions=none fence=none(no OS write fence is needed) "
        f"pane=w1:p1 workspace=w1 head={head}\n"
    )


def fill(text: str, base: str, head: str) -> str:
    values = {"head_sha": head, "base_sha": base, "lead_name": LEAD, "peer_name": "review-aaaaaaaaaaaa"}
    return SLOT_RE.sub(lambda m: values.get(m.group(1), f"filled-{m.group(1)}"), text)


def lint_patterns() -> dict[str, re.Pattern[str]]:
    patterns = {}
    for name, value in vars(charter_lint).items():
        if name in NOT_CLAUSES:
            continue
        if isinstance(value, re.Pattern):
            patterns[name] = value
        elif isinstance(value, tuple) and value and all(isinstance(v, re.Pattern) for v in value):
            patterns.update({f"{name}[{i}]": v for i, v in enumerate(value)})
    return patterns


def lint_literals() -> list[str]:
    """String clauses _charter_problems tests with `"..." not in text`."""
    tree = ast.parse(inspect.getsource(charter_lint._charter_problems))
    literals = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Compare) and isinstance(node.ops[0], ast.NotIn):
            left = node.left
            if isinstance(left, ast.Constant):
                literals.append(left.value)
            elif isinstance(left, ast.JoinedStr):
                literals.append(
                    "".join(v.value if isinstance(v, ast.Constant) else LEAD for v in left.values)
                )
    return literals


class ReviewerCharterTemplateTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls._repo_tmp = tempfile.TemporaryDirectory(dir=os.path.realpath("/tmp"))
        cls.repo = Path(cls._repo_tmp.name)
        cls.addClassCleanup(cls._repo_tmp.cleanup)
        git = ["git", "-C", str(cls.repo), "-c", "user.name=t", "-c", "user.email=t@example.com"]
        subprocess.run([*git, "init", "-q"], check=True, stdin=subprocess.DEVNULL)
        for message in ("base", "head"):
            subprocess.run([*git, "commit", "-q", "--allow-empty", "-m", message], check=True, stdin=subprocess.DEVNULL)
        cls.base, cls.head = subprocess.run(
            [*git, "rev-parse", "HEAD~1", "HEAD"], check=True, capture_output=True, text=True, stdin=subprocess.DEVNULL
        ).stdout.split()

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=os.path.realpath("/tmp"))
        self.tmp = Path(self._tmp.name)
        self.addCleanup(self._tmp.cleanup)
        self.filled = fill(TEMPLATE.read_text(encoding="utf-8"), self.base, self.head)

    def run_lint(self, charter: str) -> tuple[int, str]:
        charter_path = self.tmp / "charter.md"
        staffing_path = self.tmp / "staffing.txt"
        charter_path.write_text(charter, encoding="utf-8")
        staffing_path.write_text(staffing(self.head), encoding="utf-8")
        stderr = io.StringIO()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(stderr):
            rc = charter_lint.main(
                ["--charter", str(charter_path), "--lead", LEAD, "--staffing", str(staffing_path),
                 "--repo", str(self.repo)]
            )
        return rc, stderr.getvalue()

    def test_placeholders_are_snake_case_and_all_filled(self):
        # A quoted heredoc opener (<<') in the report block is shell syntax, not a slot.
        text = TEMPLATE.read_text(encoding="utf-8").replace("<<'", "'")
        self.assertEqual(
            charter_lint.PLACEHOLDER_RE.findall(text), [m.group(0) for m in SLOT_RE.finditer(text)]
        )
        self.assertIsNone(charter_lint.PLACEHOLDER_RE.search(self.filled.replace("<<'", "'")))

    def test_report_block_matches_report_by_prompt_template(self):
        block = REPORT_BLOCK.read_text(encoding="utf-8").strip()
        block = block.replace("<run-dir>", "<run_dir>").replace("<peer-name>", "<peer_name>")
        block = block.replace("<lead-name>", "<lead_name>")
        self.assertIn(block, TEMPLATE.read_text(encoding="utf-8"))

    def test_check_depth_sentence_matches_lead_doctrine(self):
        lead = (SKILL / "references" / "lead.md").read_text(encoding="utf-8")
        section = lead.split("\n### Light and heavy checks\n", 1)[1].split("\n### ", 1)[0]
        sentence = section.split("carries, by value: ", 1)[1].strip()
        self.assertIn(sentence, TEMPLATE.read_text(encoding="utf-8"))

    def test_report_block_no_write_form_writes_hostile_body_verbatim(self):
        form = re.search(
            r"`(cat > <run-dir>/report-<peer-name>\.md <<(\S+))`",
            REPORT_BLOCK.read_text(encoding="utf-8"),
        )
        self.assertIsNotNone(form)
        with tempfile.TemporaryDirectory() as tmp:
            marker = Path(tmp) / "ran"
            body = (
                f"Verdict: PASS $HOME `id` $(touch {marker}) \"dq\" 'sq' \\n\n"
                f"EOF\nEND\ntouch {marker}\n"
            )
            command = form.group(1).replace("<run-dir>", tmp).replace("<peer-name>", "review-x")
            delimiter = form.group(2).strip("'\"").replace("<peer-name>", "review-x")
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
        self.assertIn("send it with the same command", lines[0])

    @unittest.skipUnless(shutil.which("sandbox-exec"), "sandbox-exec is macOS-only")
    def test_write_fence_admits_only_its_targets(self):
        if subprocess.run(["sandbox-exec", "-p", "(version 1)(allow default)", "true"], stdin=subprocess.DEVNULL).returncode:
            self.skipTest("inside a sandbox already: sandbox_apply refuses a nested profile")
        # Every temp root is admitted, so the denied targets live outside them.
        with tempfile.TemporaryDirectory(dir="/Users/Shared") as outside:
            root = Path(outside)
            values = {"herdr_home": f"{root}/.herdr", "kind_state_dir": f"{root}/state",
                      "run_dir": f"{root}/.herdr/projects/p/runs/2026-09-30", "peer_name": "review-45fa5929e7c1"}
            run_dir, name = Path(values["run_dir"]), values["peer_name"]
            # As a Lead fills it: a "." in a slot value becomes "\." on the regex lines.
            fill = lambda line: SLOT_RE.sub(
                lambda m: values[m.group(1)].replace(".", "\\.") if "(regex" in line else values[m.group(1)], line)
            profile = root / "fence.sb"
            profile.write_text("".join(fill(l) for l in FENCE.read_text(encoding="utf-8").splitlines(True)))
            for d in (run_dir, root / ".herdr/heavy-slots", root / "state", root / "Xherdr/projects/p/runs/2026-09-30"):
                d.mkdir(parents=True)
            report, send = run_dir / f"report-{name}.md", run_dir / f"send-{name}.txt"
            allowed = [report, send, Path(f"{report}.tmp.17614.7a0e172e9fe4"), Path(f"{send}.tmp.1.0"),
                       root / "state/session", self.tmp / "scratch"]
            denied = [run_dir / "other.md", run_dir / "report-review-other.md", run_dir / f"send-{name}.md",
                      root / ".herdr/gates.md", root / ".herdr/heavy-slots/1", root / "checkout-file",
                      root / f"Xherdr/projects/p/runs/2026-09-30/report-{name}.md",
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

    def test_no_mutation_contract_bounds_the_awaited_background_check(self):
        text = TEMPLATE.read_text(encoding="utf-8")
        contract = text.split("No-mutation contract:", 1)[1].split("change no external state", 1)[0]
        for bound in (
            "one charter-named check at a time",
            "runtime task id",
            "is never detached (no `nohup`, `setsid`, `disown`, trailing `&`,",
            "awaited through the runtime's completion notice, not a sleep or poll loop",
            "stopped only by its own task id",
            "reported only after it ends",
            "task id, command, how it started, end state and exit code",
        ):
            with self.subTest(bound=bound):
                self.assertIn(bound, contract)

    def test_filled_template_lints_ok(self):
        self.assertEqual(self.run_lint(self.filled), (0, ""))

    def test_clause_set_is_derived_from_charter_lint(self):
        self.assertGreaterEqual(len(lint_patterns()), 7)
        self.assertIn(f"herdr agent prompt {LEAD}", lint_literals())
        self.assertIn("SEND-FAILED", lint_literals())

    def test_removing_any_required_clause_fails_naming_it(self):
        clauses = [(name, lambda t, p=p: p.sub("", t)) for name, p in lint_patterns().items()]
        clauses += [(lit, lambda t, s=lit: t.replace(s, "")) for lit in lint_literals()]
        for name, remove in clauses:
            with self.subTest(clause=name):
                stripped = remove(self.filled)
                self.assertNotEqual(stripped, self.filled, f"template lacks {name}")
                rc, err = self.run_lint(stripped)
                self.assertEqual(rc, 1)
                problems = err.strip().splitlines()
                self.assertEqual(len(problems), 1, err)
                self.assertTrue(problems[0].startswith("charter_lint: missing "), err)


if __name__ == "__main__":
    unittest.main()
