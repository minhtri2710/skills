#!/usr/bin/env python3
"""PreToolUse hook on Bash: refuse rm, rmdir, unlink, shred, mv, find -delete and xargs rm whose target
could expand a pattern, or that names the shared /tmp top level. A guard against mistakes, not a security
boundary: a script file, a computed value or a program that deletes is not seen, nor is a glob that sits
in a `for` list or inside a quoted substitution rather than in rm's own arguments.

Input: the hook JSON on stdin. Exit 0 allows; exit 2 blocks with one message on stderr. Fails closed:
input it cannot parse is blocked. Runs on Python 3.9 (the hook host's /usr/bin/python3): keep 3.9 syntax.
"""
from __future__ import annotations

import json
import posixpath
import re
import sys

DELETERS = {"rm", "rmdir", "unlink", "shred"}
SHELLS = {"sh", "bash", "zsh", "dash", "ksh"}
KEYWORDS = {"if", "then", "else", "elif", "while", "until", "do", "!", "coproc"}
# wrapper -> (options that take a separate argument, positional words before the wrapped command)
WRAPPERS = {"command": (set(), 0), "builtin": (set(), 0), "exec": (set(), 0), "nohup": (set(), 0),
            "time": (set(), 0), "caffeinate": ({"-t", "-w"}, 0), "nice": ({"-n"}, 0),
            "stdbuf": ({"-i", "-o", "-e"}, 0), "ionice": ({"-c", "-n", "-p", "-P", "-u"}, 0),
            "timeout": ({"-s", "-k", "--signal", "--kill-after"}, 1), "doas": ({"-u", "-C"}, 0),
            "sudo": ({"-u", "-g", "-h", "-p", "-C", "-D", "-R", "-T", "-U"}, 0), "env": ({"-u", "-C", "-S"}, 0)}
XARGS_ARG = {"-I", "-J", "-R", "-S", "-n", "-P", "-L", "-s", "-d", "-E", "-a", "--delimiter", "--max-args",
             "--max-procs", "--max-lines", "--max-chars", "--arg-file", "--process-slot-var"}
SHARED = {"/", "/private", "/var", "/private/var", "/tmp", "/private/tmp", "/var/tmp", "/private/var/tmp"}
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
MAX_DEPTH = 8

WAY_OUT = ("Name the literal path you created (for a scratch directory, the exact path mktemp printed). For "
           "many files, list them with find -print or git ls-files and remove each literal path; a computed "
           "path goes through destructive-path-guard first. If this command is legitimate, report it "
           "verbatim to your Lead; do not work around the block.")
MESSAGES = {
    "glob": "an unquoted *, ? or [..] in an rm/mv target expands to whatever matches.",
    "brace": "an unquoted {a,b} or {1..3} in an rm/mv target expands to several paths.",
    "expansion": "an unquoted variable or command substitution in an rm/mv target is split and glob-expanded "
                 "by the shell; quote a variable as \"$VAR\".",
    "shared-tmp": "the target is the shared /tmp (or an ancestor of it), which other agents use.",
    "find": "find -delete or -exec rm/mv starts at the shared /tmp, at a pattern, or at no path.",
    "xargs": "xargs rm/mv deletes a list this hook cannot see.",
    "unparsable": "this command could not be parsed.",
    "internal": "the hook failed.",
}


class Unparsable(Exception):
    pass


def text(word):
    return "".join(c for c, _ in word)


def body_subs(body):
    """The parsed `$(...)` and backtick substitutions of an unquoted heredoc body: the shell runs them."""
    subs, i = [], 0
    while i < len(body):
        if body[i] == "\\":
            i += 2
        elif body.startswith("$(", i):
            sub, i = parse(body, i + 2, True)
            subs.append(sub)
        elif body[i] == "`":
            j = body.find("`", i + 1)
            if j < 0:
                raise Unparsable
            subs.append(parse(body[i + 1:j])[0])
            i = j + 1
        else:
            i += 1
    return subs


def parse(src, start=0, nested=False):
    """Split `src` into simple commands: ([{"words", "heredocs", "subs"}], index after the text parsed).

    A word is a list of (char, mode): "u" unquoted, "q" quoted or escaped, "x" an unquoted expansion.
    Redirections are dropped; heredoc bodies and here-strings are kept apart; substitutions are parsed with
    this same parser, so a heredoc inside `$(...)` is read as a heredoc. With `nested` the text ends at the
    unbalanced `)` that closes a `$(` or `<(`; a `case` pattern's `)` does not close it. `<<` inside an
    arithmetic `((...))` is a shift, not a heredoc.
    """
    cmds = []
    state = {"cmd": {"words": [], "heredocs": [], "subs": []}, "word": None, "redir": None, "depth": 0,
             "arith": 0, "cases": []}
    # arith: paren depth of an open `((`. cases: one int per open `case`: -1 in a body, else the open parens
    # of the pattern being read
    pending = []
    n = len(src)

    def add(ch, mode):
        if state["word"] is None:
            state["word"] = []
        state["word"].append((ch, mode))

    def end_word():
        word, state["word"] = state["word"], None
        if word is None:
            return
        redir, state["redir"] = state["redir"], None
        if redir == "here":
            state["cmd"]["heredocs"].append(text(word))
        elif redir in ("plain", "dash"):
            pending.append((state["cmd"], text(word), redir == "dash", all(m != "q" for _, m in word)))
        elif redir is not None:
            pass
        elif text(word) in ("{", "}") and all(m == "u" for _, m in word):
            end_cmd()
        else:
            words, plain = state["cmd"]["words"], all(m == "u" for _, m in word)
            if plain and text(word) == "esac" and state["cases"] and not words:
                state["cases"].pop()
                return
            words.append(word)
            if (plain and text(word) == "in" and len(words) >= 3
                    and text(words[-3]) == "case" and (len(words) == 3 or text(words[-4]) in KEYWORDS)):
                state["cases"].append(0)
                end_cmd()

    def end_cmd():
        end_word()
        cmd = state["cmd"]
        if cmd["words"] or cmd["subs"]:
            cmds.append(cmd)
        state["cmd"] = {"words": [], "heredocs": [], "subs": []}

    def dollar(i, mode):
        """Handle the '$' at src[i]; returns the index after the expansion."""
        nxt = src[i + 1] if i + 1 < n else ""
        if nxt == "(":
            sub, end = parse(src, i + 2, True)
            state["cmd"]["subs"].append(sub)
            j = end - 1
        elif nxt == "{":
            j = src.find("}", i + 2)
            if j < 0:
                raise Unparsable
        elif nxt.isalpha() or nxt == "_":
            j = i + 1
            while j + 1 < n and (src[j + 1].isalnum() or src[j + 1] == "_"):
                j += 1
        elif nxt and nxt in "0123456789@*#?!$-":
            j = i + 1
        else:
            add("$", "q")
            return i + 1
        for ch in src[i:j + 1]:
            add(ch, mode)
        return j + 1

    def backtick(i, mode):
        j = i + 1
        while j < n and src[j] != "`":
            j += 2 if src[j] == "\\" else 1
        if j >= n:
            raise Unparsable
        state["cmd"]["subs"].append(parse(src[i + 1:j])[0])
        for ch in src[i:j + 1]:
            add(ch, mode)
        return j + 1

    i = start
    while i < n:
        c = src[i]
        nxt = src[i + 1] if i + 1 < n else ""
        if c in " \t":
            end_word()
            i += 1
        elif c == "\n":
            end_cmd()
            i += 1
            for cmd, delim, dash, unquoted in pending:
                body = []
                while i < n:
                    j = src.find("\n", i)
                    j = n if j < 0 else j
                    line = src[i:j]
                    i = j + 1
                    if (line.lstrip("\t") if dash else line) == delim:
                        break
                    body.append(line)
                cmd["heredocs"].append("\n".join(body))
                if unquoted:
                    cmd["subs"].extend(body_subs(cmd["heredocs"][-1]))
            pending.clear()
        elif c == "#" and state["word"] is None:
            while i < n and src[i] != "\n":
                i += 1
        elif c == ";":
            end_cmd()
            if state["cases"] and state["cases"][-1] < 0 and nxt in (";", "&"):
                state["cases"][-1] = 0
                i += 3 if src.startswith(";;&", i) else 2
            else:
                i += 1
        elif c == "&" and nxt != ">":
            end_cmd()
            i += 2 if nxt == "&" else 1
        elif c == "|":
            end_cmd()
            i += 2 if nxt in ("|", "&") else 1
        elif c in "()":
            lead = state["word"] is None and not state["cmd"]["words"]
            at_command = state["word"] is None and all(text(w) in KEYWORDS | {"for"} for w in state["cmd"]["words"])
            end_cmd()
            i += 1
            cases = state["cases"]
            if cases and cases[-1] >= 0:
                if c == "(" and not lead:
                    cases[-1] += 1
                elif c == ")":
                    cases[-1] = cases[-1] - 1 if cases[-1] else -1
            elif c == "(":
                if nxt == "(" and at_command:
                    state["depth"] += 2
                    state["arith"] = state["depth"]
                    i += 1
                else:
                    state["depth"] += 1
            elif state["depth"]:
                state["depth"] -= 1
                if state["depth"] < state["arith"]:
                    state["arith"] = 0
            elif nested:
                return cmds, i
        elif c in "<>" and nxt == "(":
            sub, i = parse(src, i + 2, True)
            state["cmd"]["subs"].append(sub)
            add("<", "q")
        elif c in "<>&":
            word = state["word"]
            if word is not None and all(ch.isdigit() and m == "u" for ch, m in word):
                state["word"] = None
            else:
                end_word()
            if state["arith"] and src.startswith("<<", i):
                i += 2
            elif src.startswith("<<<", i):
                state["redir"], i = "here", i + 3
            elif src.startswith("<<-", i):
                state["redir"], i = "dash", i + 3
            elif src.startswith("<<", i):
                state["redir"], i = "plain", i + 2
            else:
                state["redir"] = ""
                i += 1
                if i < n and src[i] in "&|>" and c != "&":
                    i += 1
                elif c == "&":
                    i += 1
        elif c == "'":
            j = src.find("'", i + 1)
            if j < 0:
                raise Unparsable
            if state["word"] is None:
                state["word"] = []
            for ch in src[i + 1:j]:
                add(ch, "q")
            i = j + 1
        elif c == '"':
            if state["word"] is None:
                state["word"] = []
            i += 1
            while True:
                if i >= n:
                    raise Unparsable
                d = src[i]
                if d == '"':
                    i += 1
                    break
                if d == "\\" and i + 1 < n and src[i + 1] in '$`"\\\n':
                    if src[i + 1] != "\n":
                        add(src[i + 1], "q")
                    i += 2
                elif d == "$":
                    i = dollar(i, "q")
                elif d == "`":
                    i = backtick(i, "q")
                else:
                    add(d, "q")
                    i += 1
        elif c == "\\":
            if nxt == "\n":
                i += 2
            else:
                add(nxt or "\\", "q")
                i += 2 if nxt else 1
        elif c == "$" and nxt == "'":
            j = i + 2
            while j < n and src[j] != "'":
                j += 2 if src[j] == "\\" else 1
            if j >= n:
                raise Unparsable
            for ch in src[i + 2:j]:
                add(ch, "q")
            i = j + 1
        elif c == "$":
            i = dollar(i, "x")
        elif c == "`":
            i = backtick(i, "x")
        else:
            add(c, "u")
            i += 1
    if nested:
        raise Unparsable
    end_cmd()
    return cmds, n


def has_pattern(word):
    """'glob', 'brace' or None for the unquoted pattern characters of a word."""
    chars = word
    for k, (ch, mode) in enumerate(chars):
        if mode != "u":
            continue
        if ch in "*?":
            return "glob"
        if ch == "[" and any(c == "]" and m == "u" for c, m in chars[k + 1:]):
            return "glob"
    for k, (ch, mode) in enumerate(chars):
        if ch == "{" and mode == "u":
            for m in range(k + 1, len(chars)):
                if chars[m] == ("}", "u"):
                    inner = chars[k + 1:m]
                    if (",", "u") in inner or any(inner[p] == inner[p + 1] == (".", "u") for p in range(len(inner) - 1)):
                        return "brace"
                    break
    return None


def has_expansion(word):
    return any(mode == "x" for _, mode in word)


def is_shared_tmp(word, cwd):
    s = text(word)
    if not s:
        return False
    if not s.startswith("/"):
        if not cwd.startswith("/"):
            return False
        s = cwd + "/" + s
    p = posixpath.normpath(s)
    return ("/" + p.lstrip("/")) in SHARED


def resolve(words):
    """(command name, its argument words) after assignments, keywords, path prefixes and wrappers."""
    i = 0
    while i < len(words):
        w = text(words[i])
        if w in KEYWORDS or ASSIGNMENT.match(w):
            i += 1
            continue
        base = w.rsplit("/", 1)[-1]
        if base in WRAPPERS:
            with_argument, positionals = WRAPPERS[base]
            i += 1
            while i < len(words) and text(words[i]).startswith("-"):
                i += 2 if text(words[i]) in with_argument else 1
            i += positionals
            continue
        return base, words[i + 1:]
    return None, []


def shell_script(args):
    """The -c text of a shell's arguments, "" for a shell reading a script from stdin, None otherwise.

    Walks the shell's options, including those that take an argument (-o NAME, -O NAME, --rcfile FILE), up to
    the first operand: that is the -c text when -c was given, else a script file. A `-` or `--` ends the
    options; the -c text is the word after it.
    """
    found_c, skip = False, 0
    for k, w in enumerate(args):
        s = text(w)
        if skip:
            skip -= 1
        elif s in ("-", "--"):
            return text(args[k + 1]) if found_c and k + 1 < len(args) else None
        elif s[:1] not in ("-", "+"):
            return s if found_c else None
        elif s.startswith("--"):
            skip = 1 if s in ("--rcfile", "--init-file") else 0
        else:
            found_c = found_c or (s[0] == "-" and "c" in s[1:])
            skip += sum(ch in "oO" for ch in s[1:])
    return None if found_c else ""


def operands(name, args):
    ops, options_over, skip, target_dir = [], False, False, False
    for w in args:
        s = text(w)
        if skip:
            skip = False
            continue
        if not options_over and s == "--":
            options_over = True
        elif not options_over and s.startswith("-") and len(s) > 1:
            if name == "mv":
                if s in ("-t", "--target-directory"):
                    target_dir, skip = True, True
                elif s.startswith("--target-directory=") or (s.startswith("-t") and not s.startswith("--")):
                    target_dir = True
        else:
            ops.append(w)
    return ops, (ops if name != "mv" or target_dir else ops[:-1])


def check_delete(name, args, cwd):
    ops, targets = operands(name, args)
    for w in ops:
        if has_pattern(w):
            return has_pattern(w)
    for w in targets:
        if has_expansion(w):
            return "expansion"
        if is_shared_tmp(w, cwd):
            return "shared-tmp"
    return None


def check_find(args, cwd, depth, in_xargs):
    k = 0
    while k < len(args) and text(args[k]) in ("-H", "-L", "-P"):
        k += 1
    paths = []
    while k < len(args) and not text(args[k]).startswith("-") and text(args[k]) not in ("!", "(", ")"):
        paths.append(args[k])
        k += 1
    danger = False
    for j in range(k, len(args)):
        s = text(args[j])
        if s == "-delete":
            danger = True
        elif s in ("-exec", "-execdir", "-ok", "-okdir"):
            end = j + 1
            while end < len(args) and text(args[end]) not in (";", "+"):
                end += 1
            name, rest = resolve(args[j + 1:end])
            if name in DELETERS or name == "mv":
                danger = True
            elif name in SHELLS and shell_script(rest):
                found = scan(shell_script(rest), cwd, depth + 1, in_xargs)
                if found:
                    return found
                danger = danger or bool(scan(shell_script(rest), cwd, depth + 1, True))
    if not danger:
        return None
    if not paths or any(has_pattern(p) or has_expansion(p) or is_shared_tmp(p, cwd) for p in paths):
        return "find"
    return None


def judge(cmd, cwd, depth, in_xargs):
    name, args = resolve(cmd["words"])
    if name in DELETERS or name == "mv":
        return "xargs" if in_xargs else check_delete(name, args, cwd)
    if name == "find":
        return check_find(args, cwd, depth, in_xargs)
    if name == "xargs":
        k = 0
        while k < len(args) and text(args[k]).startswith("-"):
            k += 2 if text(args[k]) in XARGS_ARG else 1
        inner, rest = resolve(args[k:])
        if inner in DELETERS or inner == "mv":
            return "xargs"
        if inner in SHELLS and shell_script(rest):
            return scan(shell_script(rest), cwd, depth + 1, True)
        return None
    if name in SHELLS:
        script = shell_script(args)
        if script:
            return scan(script, cwd, depth + 1, in_xargs)
        if script == "":
            for body in cmd["heredocs"]:
                found = scan(body, cwd, depth + 1, in_xargs)
                if found:
                    return found
    elif name == "eval":
        return scan(" ".join(text(w) for w in args), cwd, depth + 1, in_xargs)
    return None


def scan(src, cwd, depth=0, in_xargs=False):
    """The id of the first refusal in `src`, or None."""
    try:
        return scan_commands(parse(src)[0], cwd, depth, in_xargs)
    except Unparsable:
        return "unparsable"


def scan_commands(cmds, cwd, depth, in_xargs):
    if depth > MAX_DEPTH:
        return "unparsable"
    for cmd in cmds:
        for sub in cmd["subs"]:
            found = scan_commands(sub, cwd, depth + 1, in_xargs)
            if found:
                return found
        found = judge(cmd, cwd, depth, in_xargs)
        if found:
            return found
    return None


def block(ident):
    print("Blocked by block-glob-delete (%s): %s %s" % (ident, MESSAGES[ident], WAY_OUT), file=sys.stderr)
    sys.exit(2)


def main():
    try:
        payload = json.load(sys.stdin)
        command = (payload.get("tool_input") or {}).get("command") or ""
        cwd = payload.get("cwd") or ""
        if not isinstance(command, str) or not isinstance(cwd, str):
            raise ValueError
    except (ValueError, AttributeError):
        print("block-glob-delete: cannot parse the hook input; command blocked.", file=sys.stderr)
        sys.exit(2)
    try:
        found = scan(command, cwd)
    except Exception:
        found = "internal"
    if found:
        block(found)
    sys.exit(0)


if __name__ == "__main__":
    main()
