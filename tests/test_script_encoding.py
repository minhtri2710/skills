#!/usr/bin/env python3
"""Every text-mode file open and subprocess in skill scripts names encoding= (the locale is not UTF-8 everywhere)."""
from __future__ import annotations

import ast
import unittest
from collections import Counter
from collections.abc import Iterator
from pathlib import Path
from tempfile import TemporaryDirectory

SKILLS = Path(__file__).resolve().parents[1] / "skills"


_SCOPES = (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda, ast.ClassDef)


def _origin(expr: ast.AST, names: dict[str, str]) -> str:
    if isinstance(expr, ast.Name):
        return names.get(expr.id, "")
    if isinstance(expr, ast.Attribute):
        owner = _origin(expr.value, names)
        return f"{owner}.{expr.attr}" if owner else ""
    if isinstance(expr, ast.Call) and _origin(expr.func, names) == "urllib.request.build_opener":
        return "urllib.request.OpenerDirector"
    return ""


def _evaluated_nodes(statement: ast.AST) -> Iterator[ast.AST]:
    pending = [statement]
    while pending:
        node = pending.pop()
        yield node
        children = ast.iter_child_nodes(node)
        if isinstance(node, _SCOPES):
            body = node.body
            deferred = set(body) if isinstance(body, list) else {body}
            pending.extend(child for child in children if child not in deferred)
        else:
            pending.extend(children)


def _calls(scope: ast.AST, outer: dict[str, str], indirect: set[str]) -> Iterator[tuple[ast.Call, str]]:
    # Definition headers execute in the surrounding scope, not in the nested body.
    body = getattr(scope, "body")
    groups = [(stmt, list(_evaluated_nodes(stmt)))
              for stmt in (body if isinstance(body, list) else [body])]
    nodes = [node for _, group in groups for node in group]
    writes = Counter(n.id for n in nodes if isinstance(n, ast.Name) and isinstance(n.ctx, (ast.Store, ast.Del)))
    writes.update(indirect)
    if isinstance(scope, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Lambda)):
        writes.update(arg.arg for arg in ast.iter_child_nodes(scope.args) if isinstance(arg, ast.arg))
    writes.update(n.name for n in nodes if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)))
    writes.update(n.name for n in nodes if isinstance(n, (ast.ExceptHandler, ast.MatchAs, ast.MatchStar)) and n.name)
    writes.update(n.rest for n in nodes if isinstance(n, ast.MatchMapping) and n.rest)
    imports: dict[str, set[str]] = {}
    for stmt in nodes:
        if isinstance(stmt, (ast.Import, ast.ImportFrom)):
            for a in stmt.names:
                key = a.asname or a.name.partition(".")[0]
                if isinstance(stmt, ast.Import):
                    value = a.name if a.asname else key
                else:
                    value = "." * stmt.level + f"{stmt.module or ''}.{a.name}"
                imports.setdefault(key, set()).add(value)
    writes.update(key for key, values in imports.items() for _ in values)
    names = {key: value for key, value in outer.items() if key not in writes}
    for stmt, group in groups:
        for node in group:
            if isinstance(node, ast.Call):
                yield node, _origin(node.func, names)
            elif isinstance(node, _SCOPES):
                yield from _calls(node, outer if isinstance(scope, ast.ClassDef) else names, indirect)
        if isinstance(stmt, (ast.Import, ast.ImportFrom)):
            for a in stmt.names:
                key = a.asname or a.name.partition(".")[0]
                if writes[key] == 1:
                    names[key] = next(iter(imports[key]))
        elif isinstance(stmt, (ast.Assign, ast.AnnAssign)) and stmt.value is not None:
            targets = stmt.targets if isinstance(stmt, ast.Assign) else [stmt.target]
            for target in targets:
                if isinstance(target, ast.Name) and writes[target.id] == 1:
                    value = _origin(stmt.value, names)
                    if value:
                        names[target.id] = value


def text_opens_without_encoding(path: Path) -> list[str]:
    found = []
    tree = ast.parse(path.read_text(encoding="utf-8"), str(path))
    indirect = {name for node in ast.walk(tree) if isinstance(node, (ast.Global, ast.Nonlocal)) for name in node.names}
    for node, api in _calls(tree, {}, indirect):
        func = node.func
        if isinstance(func, ast.Name):
            name, owner = func.id, None
        elif isinstance(func, ast.Attribute):
            name, owner = func.attr, func.value
        else:
            continue
        keywords = {k.arg for k in node.keywords}
        if "encoding" in keywords:
            continue
        if name in ("read_text", "write_text"):
            found.append(f"{path.name}:{node.lineno}")
        elif name in ("open", "fdopen"):
            if api in ("os.open", "urllib.request.OpenerDirector.open"):
                continue  # Descriptor or HTTP response, not a text file.
            # Path.open(mode) takes mode first; open(file, mode) and fdopen(fd, mode) take it second.
            position = 0 if owner is not None and name == "open" and api not in ("io.open", "builtins.open") else 1
            mode = next((k.value for k in node.keywords if k.arg == "mode"),
                        node.args[position] if len(node.args) > position else None)
            if isinstance(mode, ast.Constant) and isinstance(mode.value, str) and "b" in mode.value:
                continue
            found.append(f"{path.name}:{node.lineno}")
    return found


def text_subprocesses_without_encoding(path: Path) -> list[str]:
    found = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"), str(path))):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not isinstance(func, ast.Attribute) or func.attr not in ("run", "check_output", "Popen"):
            continue
        if not isinstance(func.value, ast.Name) or func.value.id != "subprocess":
            continue
        keywords = {keyword.arg: keyword.value for keyword in node.keywords}
        text_mode = any(
            keyword in keywords
            and isinstance(keywords[keyword], ast.Constant)
            and keywords[keyword].value is True
            for keyword in ("text", "universal_newlines")
        )
        if text_mode and "encoding" not in keywords:
            found.append(f"{path.name}:{node.lineno}")
    return found


class ScriptEncodingTest(unittest.TestCase):
    def test_every_text_mode_open_and_subprocess_names_an_encoding(self):
        scripts = sorted(SKILLS.glob("*/scripts/**/*.py"))
        self.assertTrue(scripts)
        opens = [site for path in scripts for site in text_opens_without_encoding(path)]
        self.assertEqual(opens, [], "text-mode open without encoding=")
        subprocesses = [
            site for path in scripts for site in text_subprocesses_without_encoding(path)
        ]
        self.assertEqual(subprocesses, [], "text-mode subprocess without encoding=")

    def test_file_encoding_rule_distinguishes_a_url_opener_from_a_path(self):
        source = "\n".join((
            "from urllib.request import build_opener as make_client",
            "from pathlib import Path",
            "import os",
            "client = make_client()",
            "client.open(request)",
            "def read(client: Path, mode):",
            "    client.open(mode)",
            "    client.open('rb')",
            "    client.open(encoding='utf-8')",
            "open('document')",
            "os.fdopen(7, 'r')",
            "saved = Path('notes.txt')",
            "def download(cache=saved.open('r')):",
            "    saved = make_client()",
            "    return saved.open(request)",
            "class Config:",
            "    previous = saved.open('r')",
            "    saved = make_client()",
            "    response = saved.open(request)",
            "def reuse(client=client.open(request)):",
            "    return client",
            "remote = make_client()",
            "def choose_file():",
            "    global remote",
            "    remote = Path('notes.txt')",
            "choose_file()",
            "remote.open('r')",
        ))
        with TemporaryDirectory() as tmp:
            sample = Path(tmp) / 'sample.py'
            sample.write_text(source, encoding='utf-8')
            self.assertCountEqual(text_opens_without_encoding(sample),
                                  ["sample.py:7", "sample.py:10", "sample.py:11",
                                   "sample.py:13", "sample.py:17", "sample.py:27"])


if __name__ == "__main__":
    unittest.main()
