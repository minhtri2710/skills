// claude Stop and StopFailure hook: wakes the Lead when the turn ended without a successful report prompt.
// Never blocks, never writes a file, always exits 0. Usage: node report-wake-claude.js --lead <lead> --seat <seat> --dir <run dir>
import { readFileSync } from "node:fs";
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

// Any unreadable or unrecognized turn counts as unsent: an extra wake, never a missed one.
function sentThisTurn() {
  if (typeof payload.prompt_id !== "string" || typeof payload.transcript_path !== "string") return false;
  const commands = new Map();
  let sent = false;
  for (const line of readFileSync(payload.transcript_path, "utf8").split("\n")) {
    let entry;
    try {
      entry = JSON.parse(line);
    } catch {
      continue;
    }
    const content = entry?.message?.content;
    if (!Array.isArray(content)) continue;
    for (const item of content) {
      if (item?.type === "tool_use" && item.name === "Bash" && typeof item.input?.command === "string") {
        commands.set(item.id, item.input.command);
      } else if (item?.type === "tool_result" && entry.promptId === payload.prompt_id && item.is_error !== true) {
        if (promptTarget(commands.get(item.tool_use_id) ?? "", lead) === lead) sent = true;
      }
    }
  }
  return sent;
}

let sent = false;
try {
  sent = sentThisTurn();
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
