#!/usr/bin/env python3
"""Every text-mode file open in the workflow scripts names encoding= (the locale is not UTF-8 everywhere)."""
from __future__ import annotations

import ast
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "skills" / "herdr-delivery-workflow" / "scripts"


def text_opens_without_encoding(path: Path) -> list[str]:
    """file:line of each open()/Path.open()/os.fdopen() in text mode and each read_text()/write_text() lacking encoding=."""
    found = []
    for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"), str(path))):
        if not isinstance(node, ast.Call):
            continue
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
            if name == "open" and isinstance(owner, ast.Name) and owner.id == "os":
                continue  # os.open returns a file descriptor, never text
            # Path.open(mode) takes the mode first; open(file, mode) and os.fdopen(fd, mode) second.
            position = 0 if owner is not None and name == "open" else 1
            mode = next((k.value for k in node.keywords if k.arg == "mode"),
                        node.args[position] if len(node.args) > position else None)
            if isinstance(mode, ast.Constant) and isinstance(mode.value, str) and "b" in mode.value:
                continue
            found.append(f"{path.name}:{node.lineno}")
    return found


class ScriptEncodingTest(unittest.TestCase):
    def test_every_text_mode_open_names_an_encoding(self):
        scripts = sorted(SCRIPTS.glob("*.py"))
        self.assertTrue(scripts)
        found = [site for path in scripts for site in text_opens_without_encoding(path)]
        self.assertEqual(found, [], "text-mode open without encoding=")


if __name__ == "__main__":
    unittest.main()
