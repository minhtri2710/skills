from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXTENSIONS = REPO / "skills" / "herdr-delivery-workflow" / "extensions"
EXTENSION = Path(os.environ.get("REPORT_WAKE_EXTENSION", EXTENSIONS / "report-wake.js"))
HOOK = Path(os.environ.get("REPORT_WAKE_HOOK", EXTENSIONS / "report-wake-claude.js"))
NODE = shutil.which("node")
LEAD = "lead-example"
SEAT = "eng-example"
RUN_DIR = "/run/example"
REPORT = f"{RUN_DIR}/report-{SEAT}.md"
SEND = f"{RUN_DIR}/send-{SEAT}.txt"
D4 = (
    f"report-wake: your turn is ending without a successful report prompt to {LEAD}. Send your report or protocol message now with the report-by-prompt command in your charter: write {REPORT}, then {SEND}, then run herdr agent prompt {LEAD} \"$(cat {SEND})\". If you cannot, send BLOCKED the same way."
)
D5 = (
    f"report-wake: {SEAT} settled (outcome completed) without a successful report prompt to {LEAD} this turn. Read {REPORT} if it is newer than your last processed report from {SEAT}, then the pane: herdr agent read {SEAT}."
)
D5_ERROR = D5.replace("outcome completed", "outcome error")
D5_AUTH = D5.replace("outcome completed", "outcome authentication_failed")
D6 = f"report-wake: {SEND} is older than {REPORT}; rewrite the send file from the current report, then send."

NODE_DRIVER = r'''const extensionPath = process.argv[1];
const scenario = JSON.parse(process.argv[2]);
const handlers = new Map();
const flags = new Map(Object.entries(scenario.flags ?? {
  "report-lead": "lead-example", "report-seat": "eng-example", "report-dir": "/run/example"
}));
const calls = { registered: [], entries: [], notifications: [], exec: [], handlers: [], beforeResults: [] };
const pi = {
  registerFlag(name, options) { calls.registered.push([name, options]); },
  getFlag(name) { return flags.get(name); },
  on(name, handler) {
    if (!handlers.has(name)) handlers.set(name, []);
    handlers.get(name).push(handler);
    calls.handlers.push(name);
  },
  appendEntry(type, data) { calls.entries.push([type, data]); },
  async exec(command, args) {
    calls.exec.push([command, args]);
    return { code: scenario.execCodes?.[calls.exec.length - 1] ?? 0, stdout: "", stderr: "", killed: false };
  },
};
const context = { ui: { notify(message, level) { calls.notifications.push([message, level]); } } };
const module = await import(`file://${extensionPath}`);
module.default(pi);
const invoke = async (name, event = {}) => {
  let result;
  for (const handler of handlers.get(name) ?? []) {
    const next = await handler({ type: name, ...event }, context);
    if (next !== undefined) result = next;
  }
  return result;
};
await invoke("session_start");
for (const step of scenario.steps ?? []) {
  if (step.type === "call") {
    calls.lastCall = await invoke("tool_call", step.event);
  } else if (step.type === "result") {
    await invoke("tool_result", step.event);
  } else if (step.type === "before") {
    calls.beforeResults.push(await invoke("agent_before_settle", step.event));
  } else if (step.type === "settled") {
    await invoke("agent_settled");
  } else if (step.type === "input") {
    await invoke("input", step.event);
  }
}
console.log(JSON.stringify(calls));
'''

SENT_COMMANDS = [
    f'herdr agent prompt "{LEAD}" "$(cat {SEND})"',
    f"env herdr agent prompt {LEAD} payload",
    f"NAME=value herdr agent prompt {LEAD} payload",
    f"a=(1 2); herdr agent prompt {LEAD} payload",
    f"format-report; herdr agent prompt {LEAD} payload",
    f"command herdr agent prompt {LEAD} payload",
    f"env NAME=value command herdr agent prompt {LEAD} payload",
    f"true; herdr agent prompt {LEAD} payload",
    f"true | herdr agent prompt {LEAD} payload",
    f"true & herdr agent prompt {LEAD} payload",
    f"true\nherdr agent prompt {LEAD} payload",
]
BODY = f'herdr agent prompt {LEAD} "$(cat {SEND})"'
UNSENT_CASES = [
    (
        "quoted commit message",
        f'git commit -m "docs: note; herdr agent prompt {LEAD} is the send"',
    ),
    ("single-quoted text", f"echo 'docs: note; herdr agent prompt {LEAD} payload'"),
    ("comment text", f"echo done; # herdr agent prompt {LEAD} payload"),
    ("unquoted heredoc", f"cat > {REPORT} <<END-{SEAT}\n{BODY}\nEND-{SEAT}"),
    ("single-quoted heredoc", f"cat > {REPORT} <<'END-{SEAT}'\n{BODY}\nEND-{SEAT}"),
    ("double-quoted heredoc", f'cat > {REPORT} <<\"END-{SEAT}\"\n{BODY}\nEND-{SEAT}'),
    ("tab-stripping heredoc", f"cat > {REPORT} <<-END-{SEAT}\n\t{BODY}\n\tEND-{SEAT}"),
    ("backslash-continued command", "echo done " + chr(92) + "\n" + f"herdr agent prompt {LEAD} payload"),
    ("conditional command", f"if false; then\nherdr agent prompt {LEAD} payload\nfi"),
    ("loop command", f"while false; do\nherdr agent prompt {LEAD} payload\ndone"),
    ("or-list whose left side succeeds", f"true || herdr agent prompt {LEAD} payload"),
    ("and-list followed by a successful command", f"false && herdr agent prompt {LEAD} payload; true"),
    (
        "delimiter line with CR under an LF opener",
        f"cat <<EOF\nbody\nEOF\r\nherdr agent prompt {LEAD} payload\nEOF\n",
    ),
    (
        "uncalled function definition",
        f"send-report()\n{{\nherdr agent prompt {LEAD} payload\n}}",
    ),
    (
        "uncalled function keyword definition",
        f"function g {{\nherdr agent prompt {LEAD} payload\n}}",
    ),
]


def step(kind: str, event: dict | None = None) -> dict:
    return {"type": kind, "event": event or {}}


def bash_result(command: str, is_error: bool = False) -> dict:
    return step("result", {"toolName": "bash", "input": {"command": command}, "isError": is_error})


def before(outcome: str = "completed") -> dict:
    return step("before", {"outcome": outcome})


class ReportWakeTest(unittest.TestCase):
    def run_extension(self, scenario: dict, extension: Path = EXTENSION) -> dict:
        if NODE is None:
            self.fail("node is required to test report-wake")
        result = subprocess.run(
            [NODE, "--input-type=module", "-e", NODE_DRIVER, str(extension), json.dumps(scenario)],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=True,
        )
        return json.loads(result.stdout)

    def test_sent_target_success_skips_nudge_and_wake(self):
        for command in SENT_COMMANDS:
            with self.subTest(command=command):
                result = self.run_extension({"steps": [bash_result(command), before(), step("settled")]})
                self.assertEqual((result["beforeResults"], result["exec"]), ([None], []))

    def test_prompt_text_outside_command_positions_does_not_count_as_sent(self):
        expected_nudge = {
            "entries": [{"type": "custom_message", "customType": "report-wake", "display": True, "content": D4}],
            "continue": True,
        }
        expected_wake = [["herdr", ["agent", "prompt", LEAD, D5]]]
        for shape, command in UNSENT_CASES:
            with self.subTest(shape=shape):
                result = self.run_extension({"steps": [bash_result(command), before(), step("settled")]})
                self.assertEqual((result["beforeResults"][0], result["exec"]), (expected_nudge, expected_wake))

    def test_unsent_completed_nudges_once_then_wakes_once(self):
        unsent = before()
        unsent["event"]["context"] = {"canContinue": False}
        result = self.run_extension({"steps": [unsent, before(), step("settled"), step("settled")]})
        self.assertEqual(
            (result["beforeResults"], result["exec"]),
            ([{"entries": [{"type": "custom_message", "customType": "report-wake", "display": True, "content": D4}], "continue": True}, None], [["herdr", ["agent", "prompt", LEAD, D5]]]),
        )

    def test_error_outcome_skips_nudge_and_wakes(self):
        result = self.run_extension({"steps": [before("error"), step("settled")]})
        self.assertEqual((result["beforeResults"], result["exec"]), ([None], [["herdr", ["agent", "prompt", LEAD, D5_ERROR]]]))

    def test_failed_send_and_other_target_do_not_count_as_sent(self):
        failed = f"herdr agent prompt {LEAD} payload"
        other = "herdr agent prompt another-seat payload"
        result = self.run_extension(
            {"steps": [bash_result(failed, True), bash_result(other), before()]}
        )
        self.assertEqual((result["beforeResults"][0]["continue"], result["exec"]), (True, []))

    def test_new_external_input_resets_run_state(self):
        command = f"herdr agent prompt {LEAD} payload"
        result = self.run_extension({"steps": [before(), step("input", {"source": "extension"}), before(), bash_result(command), step("settled"), step("input", {"source": "rpc"}), before(), step("settled"), step("settled")]})
        self.assertEqual((result["beforeResults"], result["exec"]), ([{"entries": [{"type": "custom_message", "customType": "report-wake", "display": True, "content": D4}], "continue": True}, None, {"entries": [{"type": "custom_message", "customType": "report-wake", "display": True, "content": D4}], "continue": True}], [["herdr", ["agent", "prompt", LEAD, D5]]]) )

    def test_failed_wake_sends_one_notification(self):
        result = self.run_extension({"execCodes": [7], "steps": [before(), step("settled")]})
        self.assertEqual(
            result["exec"],
            [
                ["herdr", ["agent", "prompt", LEAD, D5]],
                ["herdr", ["notification", "show", f"{SEAT}: report-wake failed", "--body", REPORT, "--sound", "request"]],
            ],
        )

    def test_stale_send_blocks_but_newer_equal_or_unrelated_command_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            report = root / f"report-{SEAT}.md"
            send = root / f"send-{SEAT}.txt"
            report.write_text("current report")
            send.write_text("stale send")
            os.utime(report, ns=(2_000_000_000, 2_000_000_000))
            os.utime(send, ns=(1_000_000_000, 1_000_000_000))
            flags = {"report-lead": LEAD, "report-seat": SEAT, "report-dir": directory}
            command = f"herdr agent prompt {LEAD} \"$(cat {send})\""
            blocked = self.run_extension({"flags": flags, "steps": [step("call", {"toolName": "bash", "input": {"command": command}})]})
            blocked_reason = {"block": True, "reason": f"report-wake: {send} is older than {report}; rewrite the send file from the current report, then send."}
            os.utime(send, ns=(2_000_000_000, 2_000_000_000))
            equal = self.run_extension({"flags": flags, "steps": [step("call", {"toolName": "bash", "input": {"command": command}})]})
            os.utime(send, ns=(3_000_000_000, 3_000_000_000))
            newer = self.run_extension({"flags": flags, "steps": [step("call", {"toolName": "bash", "input": {"command": command}})]})
            unrelated = self.run_extension({"flags": flags, "steps": [step("call", {"toolName": "bash", "input": {"command": f"herdr agent prompt {LEAD} payload"}})]})
            self.assertEqual((blocked["lastCall"], equal.get("lastCall"), newer.get("lastCall"), unrelated.get("lastCall")), (blocked_reason, None, None, None))

    def test_missing_flag_is_inert_and_notifies(self):
        result = self.run_extension({"flags": {"report-lead": LEAD, "report-seat": SEAT}, "steps": [before(), step("settled")]})
        self.assertEqual((result["registered"], result["notifications"], result["handlers"], result["exec"]), ([["report-lead", {"type": "string", "description": "Report wake report-lead"}], ["report-seat", {"type": "string", "description": "Report wake report-seat"}], ["report-dir", {"type": "string", "description": "Report wake report-dir"}]], [["report-wake: missing required flags: --report-dir", "error"]], ["session_start"], []))

SESSION = "27a1e2ac-364b-4d0d-b21b-764f2049f18f"
PROMPT_ID = "727c66f4-3b3e-4497-b48e-8eae1c2d7845"
STUB = f"""#!/bin/sh
{{ for a in "$@"; do printf '%s\\n' "$a"; done; echo ---; }} >> "$STUB_LOG"
[ "$2" = prompt ] && exit "${{STUB_PROMPT_CODE:-0}}"
exit 0
"""
WAKE = [["agent", "prompt", LEAD, D5]]


def post_payload(command: object, session: str = SESSION, prompt: str = PROMPT_ID) -> dict:
    """PostToolUse payload in the shape claude 2.1.285 sends (probe/posttooluse)."""
    return {
        "session_id": session, "prompt_id": prompt, "hook_event_name": "PostToolUse", "tool_name": "Bash",
        "tool_input": {"command": command}, "tool_response": {"stdout": "", "stderr": ""}, "tool_use_id": "toolu_1",
    }


def stop_payload(session: str = SESSION, prompt: str = PROMPT_ID, **extra) -> dict:
    """Stop payload in the shape claude 2.1.285 sends (probe/payload-*.json)."""
    return {
        "session_id": session, "prompt_id": prompt, "hook_event_name": "Stop", "stop_hook_active": False,
        "last_assistant_message": "done", "background_tasks": [], "session_crons": [], **extra,
    }


class ClaudeReportWakeHookTest(unittest.TestCase):
    def run_hooks(self, *events: tuple[bool, object], prompt_code: int = 0):
        """Runs each (record, stdin) through the hook CLI with herdr stubbed on PATH and TMPDIR private to the run.

        Returns the herdr calls and the marker files left behind."""
        if NODE is None:
            self.fail("node is required to test report-wake")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "herdr").write_text(STUB)
            (root / "herdr").chmod(0o755)
            tmp = root / "tmp"
            tmp.mkdir()
            env = {**os.environ, "PATH": f"{root}{os.pathsep}{os.environ['PATH']}", "TMPDIR": str(tmp), "STUB_LOG": str(root / "log"), "STUB_PROMPT_CODE": str(prompt_code)}
            for record, stdin in events:
                result = subprocess.run(
                    [NODE, str(HOOK), *(["--record"] if record else []), "--lead", LEAD, "--seat", SEAT, "--dir", RUN_DIR],
                    input=stdin if isinstance(stdin, str) else json.dumps(stdin), env=env, capture_output=True, text=True,
                )
                self.assertEqual((result.returncode, result.stdout), (0, ""), result.stderr)
            log = root / "log"
            calls = [c.strip().split("\n") for c in log.read_text().split("---\n") if c.strip()] if log.exists() else []
            markers = sorted(path.name for path in tmp.rglob("*") if path.is_file())
        return calls, markers

    def test_wakes_once_unless_a_successful_send_marks_this_turn(self):
        send = f'herdr agent prompt {LEAD} "$(cat {SEND})"'
        running = [{"id": "b1", "type": "shell", "status": "running", "description": "d", "command": "sleep 25"}]
        cases = [
            ("send then stop", [(True, post_payload(send)), (False, stop_payload())], [], 0),
            ("stop without a marker", [(False, stop_payload())], WAKE, 0),
            ("marker under another prompt_id", [(True, post_payload(send, prompt="previous-turn")), (False, stop_payload())], WAKE, 1),
            ("marker under another session_id", [(True, post_payload(send, session="other")), (False, stop_payload())], WAKE, 1),
            ("running background task", [(False, stop_payload(background_tasks=running))], [], 0),
        ]
        for shape, events, expected, left in cases:
            with self.subTest(shape=shape):
                calls, markers = self.run_hooks(*events)
                self.assertEqual((calls, len(markers)), (expected, left))

    def test_marker_name_is_a_hash_of_the_turn(self):
        send = f"herdr agent prompt {LEAD} payload"
        calls, markers = self.run_hooks((True, post_payload(send, session="../../x", prompt="a/b")))
        self.assertEqual((calls, len(markers), all(re.fullmatch(r"[0-9a-f]{64}", m) for m in markers)), ([], 1, True))

    def test_stop_failure_unsent_wakes_with_the_error_outcome(self):
        extra = {"hook_event_name": "StopFailure", "error": "authentication_failed"}
        calls, _ = self.run_hooks((False, stop_payload(**extra)))
        self.assertEqual(calls, [["agent", "prompt", LEAD, D5_AUTH]])

    def test_failed_wake_shows_the_notification(self):
        calls, _ = self.run_hooks((False, stop_payload()), prompt_code=7)
        self.assertEqual(calls, WAKE + [["notification", "show", f"{SEAT}: report-wake failed", "--body", REPORT, "--sound", "request"]])

    def test_malformed_stop_stdin_wakes_and_malformed_record_records_nothing(self):
        for stdin in ("", "not json", "[]"):
            with self.subTest(stdin=stdin):
                self.assertEqual(self.run_hooks((False, stdin)), (WAKE, []))
                self.assertEqual(self.run_hooks((True, stdin), (False, stop_payload())), (WAKE, []))
        for payload in (post_payload(None), {**post_payload("x"), "tool_input": None}, {**post_payload("x"), "session_id": None}):
            with self.subTest(payload=payload):
                self.assertEqual(self.run_hooks((True, payload)), ([], []))

    def test_recognizer_corpus_holds_on_the_claude_path(self):
        for command in SENT_COMMANDS:
            with self.subTest(sent=command):
                self.assertEqual(self.run_hooks((True, post_payload(command)), (False, stop_payload())), ([], []))
        for shape, command in UNSENT_CASES:
            with self.subTest(unsent=shape):
                self.assertEqual(self.run_hooks((True, post_payload(command)), (False, stop_payload())), (WAKE, []))


if __name__ == "__main__":
    if NODE is None:
        raise SystemExit("node is required to test report-wake")
    unittest.main()
