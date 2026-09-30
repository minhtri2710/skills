// claude hooks. With --record (PostToolUse, matcher Bash) a successful report prompt to the Lead leaves a per-turn marker;
// without it (Stop, StopFailure) the hook wakes the Lead unless the turn's marker exists. Never blocks, prints nothing,
// writes only the marker, always exits 0. Usage: node report-wake-claude.js [--record] --lead <lead> --seat <seat> --dir <run dir>
import { createHash } from "node:crypto";
import { existsSync, mkdirSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join } from "node:path";
import { spawnSync } from "node:child_process";
import { promptTarget } from "./report-wake.js";

const args = process.argv.slice(2);
const option = (name) => args[args.indexOf(`--${name}`) + 1];
const lead = option("lead");
const seat = option("seat");
const runDir = option("dir");
if (!lead || !seat || !runDir) {
  console.error("report-wake-claude: --lead, --seat and --dir are required");
  process.exit(0);
}
const reportPath = `${runDir}/report-${seat}.md`;

let payload = {};
try {
  const parsed = JSON.parse(readFileSync(0, "utf8"));
  if (parsed && typeof parsed === "object") payload = parsed;
} catch {}

// A running background task is the sanctioned wait of charters.md: its completion notice starts a new judged turn.
if (Array.isArray(payload.background_tasks) && payload.background_tasks.some((task) => task?.status === "running")) {
  process.exit(0);
}

// One marker per turn, named by a hash so no session_id or prompt_id value can escape the directory.
const marker = () => {
  if (typeof payload.session_id !== "string" || typeof payload.prompt_id !== "string") return undefined;
  return join(tmpdir(), "report-wake", createHash("sha256").update(`${payload.session_id}\0${payload.prompt_id}`).digest("hex"));
};

if (args.includes("--record")) {
  const file = marker();
  if (file && payload.tool_name === "Bash" && typeof payload.tool_input?.command === "string" && promptTarget(payload.tool_input.command, lead) === lead) {
    try {
      mkdirSync(dirname(file), { recursive: true });
      writeFileSync(file, "");
    } catch {}
  }
  process.exit(0);
}

// A missing or unmatched marker counts as unsent: an extra wake, never a missed one.
let sent = false;
try {
  const file = marker();
  sent = file !== undefined && existsSync(file);
  if (sent) rmSync(file);
} catch {}
if (!sent) {
  const outcome = payload.hook_event_name === "StopFailure" ? String(payload.error ?? "error") : "completed";
  const text = `report-wake: ${seat} settled (outcome ${outcome}) without a successful report prompt to ${lead} this turn. Read ${reportPath} if it is newer than your last processed report from ${seat}, then the pane: herdr agent read ${seat}.`;
  const run = (argv) => spawnSync("herdr", argv, { stdio: "ignore" }).status;
  if (run(["agent", "prompt", lead, text]) !== 0) {
    run(["notification", "show", `${seat}: report-wake failed`, "--body", reportPath, "--sound", "request"]);
  }
}
process.exit(0);
