// Count sends only at recognized shell command starts; unsupported forms fail noisy.
// By default the send counts only as the call's last executed command, so the call's exit status is the send's.
// { final: false } accepts a send at any command position (the pre-send stale check).
export function promptTarget(command, lead, { final = true } = {}) {
  const invocation = /^[ \t]*(?:env[ \t]+)?(?:[A-Za-z_][A-Za-z0-9_]*=(?:"[^"]*"|'[^']*'|[^\s;&|]+)[ \t]+)*(?:command[ \t]+)?herdr[ \t]+agent[ \t]+prompt[ \t]+(?:"([^"]*)"|'([^']*)'|([^\s;&|]+))/;
  const heredocs = [];
  let index = 0;
  let commandStart = true;
  let quote;
  let escaped = false;
  let comment = false;
  let parentheses = 0;
  let backtick = false;
  let pending = false;
  let ended = false;

  const heredocAt = (start) => {
    if (command[start + 2] === "<") return undefined;
    let cursor = start + 2;
    const stripTabs = command[cursor] === "-";
    if (stripTabs) cursor += 1;
    while (command[cursor] === " " || command[cursor] === "\t") cursor += 1;
    const opener = command[cursor];
    if (opener === "'" || opener === '"') {
      const end = command.indexOf(opener, cursor + 1);
      if (end === -1) return undefined;
      return { delimiter: command.slice(cursor + 1, end), stripTabs, end: end + 1 };
    }
    const end = command.slice(cursor).search(/[\s;&|<>]/);
    if (end === 0) return undefined;
    const delimiterEnd = end === -1 ? command.length : cursor + end;
    if (delimiterEnd === cursor) return undefined;
    return { delimiter: command.slice(cursor, delimiterEnd), stripTabs, end: delimiterEnd };
  };

  const skipHeredocs = (start) => {
    let cursor = start;
    for (const heredoc of heredocs) {
      let found = false;
      while (cursor < command.length) {
        const newline = command.indexOf("\n", cursor);
        const end = newline === -1 ? command.length : newline;
        let line = command.slice(cursor, end);
        if (heredoc.stripTabs) line = line.replace(/^\t+/, "");
        cursor = newline === -1 ? command.length : newline + 1;
        if (line === heredoc.delimiter) {
          found = true;
          break;
        }
      }
      if (!found) return command.length;
    }
    return cursor;
  };

  while (index < command.length) {
    if (commandStart) {
      if (pending && ended && !/[ \t;\n#]/.test(command[index])) pending = false;
      if (/^(?:(?:if|while|until|for|select|case|function)[ \t]|[^\s;&|()<>\"'`$=\\]+[ \t]*\([ \t]*\))/.test(command.slice(index))) return undefined;
      const match = invocation.exec(command.slice(index));
      if (match && (match[1] ?? match[2] ?? match[3]) === lead) {
        if (!final) return lead;
        pending = true;
        ended = false;
      }
      if (command[index] !== " " && command[index] !== "\t") commandStart = false;
    }

    const char = command[index];
    if (comment) {
      if (char !== "\n") {
        index += 1;
        continue;
      }
      comment = false;
    } else if (quote === "'") {
      if (char === "'") quote = undefined;
      index += 1;
      continue;
    } else if (quote === '"') {
      if (escaped) escaped = false;
      else if (char === "\\") escaped = true;
      else if (char === '"') quote = undefined;
      index += 1;
      continue;
    } else if (backtick) {
      if (escaped) escaped = false;
      else if (char === "\\") escaped = true;
      else if (char === "`") backtick = false;
      index += 1;
      continue;
    } else if (escaped) {
      escaped = false;
      index += 1;
      continue;
    } else if (char === "\\") {
      escaped = true;
      index += 1;
      continue;
    } else if (char === "'") {
      quote = "'";
      commandStart = false;
      index += 1;
      continue;
    } else if (char === '"') {
      quote = '"';
      commandStart = false;
      index += 1;
      continue;
    } else if (char === "`") {
      backtick = true;
      commandStart = false;
      index += 1;
      continue;
    } else if (char === "(") {
      parentheses += 1;
      commandStart = false;
      index += 1;
      continue;
    } else if (char === ")" && parentheses > 0) {
      parentheses -= 1;
      index += 1;
      continue;
    }

    if (parentheses > 0) {
      index += 1;
      continue;
    }
    if (char === "#" && (index === 0 || /[\s;|&()>]/.test(command[index - 1]))) {
      comment = true;
      index += 1;
      continue;
    }
    if (char === "<" && command[index + 1] === "<") {
      const heredoc = heredocAt(index);
      if (!heredoc) return undefined;
      heredocs.push(heredoc);
      index = heredoc.end;
      continue;
    }
    if (char === "\n") {
      if (heredocs.length) {
        index = skipHeredocs(index + 1);
        heredocs.length = 0;
      } else {
        index += 1;
      }
      commandStart = true;
      if (pending) ended = true;
      continue;
    }
    if ((char === "&" || char === "|") && command[index + 1] === char) return undefined;
    if (char === ";" || char === "&" || char === "|") {
      const redirect = final && ((char === "&" && (command[index - 1] === ">" || command[index - 1] === "<" || command[index + 1] === ">")) || (char === "|" && command[index - 1] === ">"));
      if (redirect) {
        index += 1;
        continue;
      }
      if (char === ";") ended = true;
      else pending = false;
      if ((char === "|" || char === "&") && command[index + 1] === "&") index += 2;
      else index += 1;
      commandStart = true;
      continue;
    }
    index += 1;
  }
  return pending ? lead : undefined;
}

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
      if (promptTarget(event.input.command, lead) === lead) {
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
      if (promptTarget(event.input.command, lead, { final: false }) !== lead || !event.input.command.includes(sendPath)) return;
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
