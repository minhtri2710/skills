#!/usr/bin/env python3
"""SessionStart / SessionEnd hook: give each Claude session its own TMPDIR.

`session-tmpdir.py start` creates <TMPDIR>/claude-<session_id> (0700) and appends `export TMPDIR=...` to
$CLAUDE_ENV_FILE, which Claude Code sources before every Bash command. `session-tmpdir.py end` removes
exactly that directory: its path is a function of the hook's TMPDIR and the session id, never a pattern.
Input: the hook JSON on stdin. Exit 2 on start and 1 on end when it refuses. Runs on Python 3.9.
"""
from __future__ import annotations

import json
import os
import re
import shlex
import shutil
import stat
import sys

SESSION_ID = re.compile(r"^[A-Za-z0-9_-]{8,64}$")


def refuse(message, code):
    print("session-tmpdir: %s" % message, file=sys.stderr)
    sys.exit(code)


def session_dir(code):
    try:
        session_id = json.load(sys.stdin)["session_id"]
    except (ValueError, KeyError, TypeError):
        refuse("cannot read session_id from the hook input.", code)
    if not isinstance(session_id, str) or not SESSION_ID.match(session_id):
        refuse("session_id is not a plain id.", code)
    name = "claude-" + session_id
    root = os.path.realpath(os.environ.get("TMPDIR") or "/tmp")
    if os.path.basename(root) == name:  # a hook that already sees the per-session TMPDIR
        root = os.path.dirname(root)
    return root, os.path.join(root, name)


def owned_directory(path):
    st = os.lstat(path)
    return stat.S_ISDIR(st.st_mode) and st.st_uid == os.getuid()


def start():
    _, path = session_dir(2)
    env_file = os.environ.get("CLAUDE_ENV_FILE")
    if not env_file:
        refuse("CLAUDE_ENV_FILE is not set; this session keeps the shared TMPDIR.", 2)
    if os.path.lexists(path):
        if not owned_directory(path):
            refuse("%s exists and is not a directory this user owns." % path, 2)
    else:
        os.mkdir(path, 0o700)
    line = "export TMPDIR=%s\n" % shlex.quote(path + "/")
    try:
        with open(env_file, encoding="utf-8") as handle:
            known = line in handle.read().splitlines(keepends=True)
    except FileNotFoundError:
        known = False
    if not known:
        with open(env_file, "a", encoding="utf-8") as handle:
            handle.write(line)


def end():
    _, path = session_dir(1)
    if not os.path.lexists(path):
        return
    if not owned_directory(path):
        refuse("%s is not a directory this user owns; left in place." % path, 1)
    shutil.rmtree(path)


if __name__ == "__main__":
    if sys.argv[1:] == ["start"]:
        start()
    elif sys.argv[1:] == ["end"]:
        end()
    else:
        refuse("usage: session-tmpdir.py start|end", 2)
