from __future__ import annotations

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
EXTENSION = Path(os.environ.get("REPORT_WAKE_EXTENSION", REPO / "skills" / "herdr-delivery-workflow" / "extensions" / "report-wake.js"))
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
        commands = [
            f'herdr agent prompt "{LEAD}" "$(cat {SEND})"',
            f"env herdr agent prompt {LEAD} payload",
            f"NAME=value herdr agent prompt {LEAD} payload",
            f"a=(1 2); herdr agent prompt {LEAD} payload",
            f"format-report; herdr agent prompt {LEAD} payload",
            f"command herdr agent prompt {LEAD} payload",
            f"env NAME=value command herdr agent prompt {LEAD} payload",
            f"true; herdr agent prompt {LEAD} payload",
            f"true && herdr agent prompt {LEAD} payload",
            f"false || herdr agent prompt {LEAD} payload",
            f"true | herdr agent prompt {LEAD} payload",
            f"true & herdr agent prompt {LEAD} payload",
            f"true\nherdr agent prompt {LEAD} payload",
        ]
        for command in commands:
            with self.subTest(command=command):
                result = self.run_extension({"steps": [bash_result(command), before(), step("settled")]})
                self.assertEqual((result["beforeResults"], result["exec"]), ([None], []))

    def test_prompt_text_outside_command_positions_does_not_count_as_sent(self):
        body = f'herdr agent prompt {LEAD} "$(cat {SEND})"'
        cases = [
            (
                "quoted commit message",
                f'git commit -m "docs: note; herdr agent prompt {LEAD} is the send"',
            ),
            ("single-quoted text", f"echo 'docs: note; herdr agent prompt {LEAD} payload'"),
            ("comment text", f"echo done; # herdr agent prompt {LEAD} payload"),
            ("unquoted heredoc", f"cat > {REPORT} <<END-{SEAT}\n{body}\nEND-{SEAT}"),
            ("single-quoted heredoc", f"cat > {REPORT} <<'END-{SEAT}'\n{body}\nEND-{SEAT}"),
            ("double-quoted heredoc", f'cat > {REPORT} <<\"END-{SEAT}\"\n{body}\nEND-{SEAT}'),
            ("tab-stripping heredoc", f"cat > {REPORT} <<-END-{SEAT}\n\t{body}\n\tEND-{SEAT}"),
            ("backslash-continued command", "echo done " + chr(92) + "\n" + f"herdr agent prompt {LEAD} payload"),
            ("conditional command", f"if false; then\nherdr agent prompt {LEAD} payload\nfi"),
            ("loop command", f"while false; do\nherdr agent prompt {LEAD} payload\ndone"),
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
        expected_nudge = {
            "entries": [{"type": "custom_message", "customType": "report-wake", "display": True, "content": D4}],
            "continue": True,
        }
        expected_wake = [["herdr", ["agent", "prompt", LEAD, D5]]]
        for shape, command in cases:
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


if __name__ == "__main__":
    if NODE is None:
        raise SystemExit("node is required to test report-wake")
    unittest.main()
