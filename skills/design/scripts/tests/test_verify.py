from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("design_verify", ROOT / "verify.py")
verify = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(verify)


class VerifyNamingTests(unittest.TestCase):
    def test_slide_capture_name_includes_viewport(self) -> None:
        name = verify.slide_capture_name(Path("deck.html"), 0, {"width": 375, "height": 667})
        self.assertEqual(name, "deck-375x667-slide-01.png")

    def test_attach_error_listeners_collects_console_and_page_errors(self) -> None:
        class FakeConsoleMessage:
            def __init__(self, kind: str, text: str) -> None:
                self.type = kind
                self.text = text

        class FakePage:
            def __init__(self) -> None:
                self.handlers: dict[str, object] = {}

            def on(self, event: str, handler: object) -> None:
                self.handlers[event] = handler

        page = FakePage()
        runtime_errors: list[str] = []

        verify.attach_error_listeners(page, runtime_errors)

        page.handlers["console"](FakeConsoleMessage("error", "console boom"))
        page.handlers["pageerror"](RuntimeError("page boom"))

        self.assertEqual(runtime_errors, ["console boom", "page boom"])

    def test_reset_deck_state_clears_persisted_slide_state(self) -> None:
        class FakePage:
            def __init__(self) -> None:
                self.scripts: list[str] = []
                self.waits: list[int] = []

            def evaluate(self, script: str) -> None:
                self.scripts.append(script)

            def wait_for_timeout(self, wait_ms: int) -> None:
                self.waits.append(wait_ms)

        page = FakePage()

        verify.reset_deck_state(page)

        self.assertEqual(len(page.scripts), 1)
        self.assertIn("deck-index-", page.scripts[0])
        self.assertIn("deck-stage-slide-", page.scripts[0])
        self.assertIn("#slide-1", page.scripts[0])
        self.assertIn("#1", page.scripts[0])
        self.assertEqual(page.waits, [100])


if __name__ == "__main__":
    unittest.main()
