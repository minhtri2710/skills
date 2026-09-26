export default function (pi) {
  const flags = ["report-lead", "report-seat", "report-dir"];
  for (const name of flags) {
    pi.registerFlag(name, { type: "string", description: `Report wake ${name}` });
  }

  let state = { sent: false, nudged: false, outcome: "none" };
  let wakeSent = false;
  let active = false;
  let lead;
  let seat;
  let runDir;
  let reportPath;
  let sendPath;

  function append(data) {
    pi.appendEntry("report-wake", data);
  }

  function promptTarget(command) {
    const invocation = /(?:^|[;&|]+\s*|\n\s*)(?:env\s+)?(?:[A-Za-z_][A-Za-z0-9_]*=(?:"[^"]*"|'[^']*'|[^\s;&|]+)\s+)*(?:command\s+)?herdr\s+agent\s+prompt\s+(?:"([^"]*)"|'([^']*)'|([^\s;&|]+))/g;
    for (const match of command.matchAll(invocation)) {
      if ((match[1] ?? match[2] ?? match[3]) === lead) return lead;
    }
    return undefined;
  }

  pi.on("session_start", (_event, ctx) => {
    const missing = flags.filter((name) => {
      const value = pi.getFlag(name);
      return typeof value !== "string" || value.length === 0;
    });
    if (missing.length) {
      const message = `report-wake: missing required flags: ${missing.map((name) => `--${name}`).join(", ")}`;
      ctx.ui.notify(message, "error");
      append({ decision: "inert", missing });
      return;
    }

    lead = pi.getFlag("report-lead");
    seat = pi.getFlag("report-seat");
    runDir = pi.getFlag("report-dir");
    reportPath = `${runDir}/report-${seat}.md`;
    sendPath = `${runDir}/send-${seat}.txt`;
    active = true;

    pi.on("input", (event) => {
      if (event.source === "interactive" || event.source === "rpc") {
        state = { sent: false, nudged: false, outcome: "none" };
        wakeSent = false;
      }
    });

    pi.on("tool_result", (event) => {
      if (!active || event.toolName !== "bash" || event.isError || typeof event.input?.command !== "string") {
        return;
      }
      if (promptTarget(event.input.command) === lead) {
        state.sent = true;
        wakeSent = true;
        append({ decision: "sent", target: lead });
      }
    });

    pi.on("agent_before_settle", (event) => {
      if (!active) return;
      state.outcome = event.outcome;
      if (state.sent || state.nudged || event.outcome !== "completed") {
        return;
      }
      state.nudged = true;
      const text = `report-wake: your turn is ending without a successful report prompt to ${lead}. Send your report or protocol message now with the report-by-prompt command in your charter: write ${reportPath}, then ${sendPath}, then run herdr agent prompt ${lead} "$(cat ${sendPath})". If you cannot, send BLOCKED the same way.`;
      append({ decision: "nudge", outcome: event.outcome });
      return {
        entries: [{ type: "custom_message", customType: "report-wake", display: true, content: text }],
        continue: true,
      };
    });

    pi.on("agent_settled", async () => {
      if (!active || state.sent || wakeSent) return;
      wakeSent = true;
      const text = `report-wake: ${seat} settled (outcome ${state.outcome}) without a successful report prompt to ${lead} this turn. Read ${runDir}/report-${seat}.md if it is newer than your last processed report from ${seat}, then the pane: herdr agent read ${seat}.`;
      const result = await pi.exec("herdr", ["agent", "prompt", lead, text]);
      append({ decision: "wake", code: result.code, outcome: state.outcome });
      if (result.code !== 0) {
        append({ decision: "notification", code: result.code });
        await pi.exec("herdr", ["notification", "show", `${seat}: report-wake failed`, "--body", reportPath, "--sound", "request"]);
      }
    });

    pi.on("tool_call", (event) => {
      if (!active || event.toolName !== "bash" || typeof event.input?.command !== "string") return;
      if (promptTarget(event.input.command) !== lead || !event.input.command.includes(sendPath)) return;
      const fs = process.getBuiltinModule("node:fs");
      let reportMtime;
      let sendMtime;
      try {
        reportMtime = fs.statSync(reportPath).mtimeMs;
        sendMtime = fs.statSync(sendPath).mtimeMs;
      } catch {
        return;
      }
      if (sendMtime < reportMtime) {
        const reason = `report-wake: ${sendPath} is older than ${reportPath}; rewrite the send file from the current report, then send.`;
        append({ decision: "stale block", reason });
        return { block: true, reason };
      }
    });
  });
}
