"""The agent-delivery-workflow references: each backend reference covers the seat operations, and doctrine names no backend command."""
from __future__ import annotations

import re
import unittest

import support
import backend

REFERENCES = support.ADW / "references"
BACKENDS = sorted(REFERENCES.glob("backend-*.md"))
EXTRA_SECTIONS = {"backend-herdr.md": ["Safety"]}


def seat_operations() -> list[str]:
    text = (REFERENCES / "seat-operations.md").read_text(encoding="utf-8")
    section = text.split("\n## Operations\n", 1)[1].split("\n## ", 1)[0]
    return re.findall(r"^### `([a-z]+)`$", section, re.M)


OPERATIONS = seat_operations()


def headings(name: str) -> list[str]:
    return re.findall(r"^## (.+)$", (REFERENCES / name).read_text(encoding="utf-8"), flags=re.MULTILINE)


def sections(name: str) -> dict[str, str]:
    parts = re.split(r"^## (.+)$", (REFERENCES / name).read_text(encoding="utf-8"), flags=re.MULTILINE)
    return dict(zip(parts[1::2], parts[2::2]))


class BackendReferenceTest(unittest.TestCase):
    def test_every_registered_backend_has_a_reference_and_the_operation_list_is_not_empty(self) -> None:
        self.assertEqual({path.stem.removeprefix("backend-") for path in BACKENDS}, set(backend.ADAPTERS))
        self.assertTrue(OPERATIONS)

    def test_each_backend_has_one_section_per_operation_in_order_and_each_is_filled(self) -> None:
        for path in BACKENDS:
            with self.subTest(backend=path.name):
                self.assertEqual(headings(path.name), OPERATIONS + EXTRA_SECTIONS.get(path.name, []))
                found = sections(path.name)
                for operation in OPERATIONS:
                    with self.subTest(backend=path.name, operation=operation):
                        self.assertTrue(found[operation].strip())


class DoctrineTest(unittest.TestCase):
    def test_doctrine_names_no_backend_tool_command(self) -> None:
        commands = {}
        for backend_doc in BACKENDS:
            tool = backend_doc.stem.removeprefix("backend-")
            body = backend_doc.read_text(encoding="utf-8")
            fenced = re.findall(r"^```[a-z]*\n(.*?)^```", body, re.M | re.S)
            prose = re.sub(r"^```[a-z]*\n.*?^```", "", body, flags=re.M | re.S)
            shown = rf"(?:[A-Za-z_][A-Za-z0-9_]*=\S+\s+)*{re.escape(tool)} ([a-z][a-z-]*)\b"
            subcommands = {
                match.group(1)
                for text, pattern in (("\n".join(fenced), rf"^\s*{shown}"), (prose, rf"`{shown}"))
                for match in re.finditer(pattern, text, re.M)
            }
            self.assertTrue(subcommands, backend_doc.name)
            commands[tool] = re.compile(rf"\b{re.escape(tool)} (?:{'|'.join(sorted(subcommands))})\b")
        doctrine = [
            support.ADW / "SKILL.md",
            *sorted((support.ADW / "templates").iterdir()),
            *(path for path in sorted(REFERENCES.glob("*.md")) if path not in BACKENDS),
        ]
        self.assertGreater(len(doctrine), 2)
        for path in doctrine:
            for tool, command in commands.items():
                with self.subTest(path=path.name, tool=tool):
                    self.assertIsNone(command.search(path.read_text(encoding="utf-8")))


if __name__ == "__main__":
    unittest.main()
