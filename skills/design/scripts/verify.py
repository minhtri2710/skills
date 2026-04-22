#!/usr/bin/env python3

from __future__ import annotations

import argparse
from pathlib import Path
from typing import Any

try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None


def parse_viewports(raw: str) -> list[dict[str, int]]:
    viewports: list[dict[str, int]] = []
    for item in raw.split(","):
        width, height = item.lower().split("x")
        viewports.append({"width": int(width), "height": int(height)})
    return viewports


def slide_capture_name(html_path: Path, slide_index: int, viewport: dict[str, int]) -> str:
    return f"{html_path.stem}-{viewport['width']}x{viewport['height']}-slide-{slide_index + 1:02d}.png"


def attach_error_listeners(page: Any, runtime_errors: list[str]) -> None:
    page.on("console", lambda msg: runtime_errors.append(msg.text) if msg.type == "error" else None)
    page.on("pageerror", lambda err: runtime_errors.append(str(err)))


def reset_deck_state(page: Any) -> None:
    page.evaluate(
        """() => {
            try {
                const keys = [];
                for (let i = 0; i < localStorage.length; i += 1) {
                    const key = localStorage.key(i);
                    if (key && (key.startsWith('deck-index-') || key.startsWith('deck-stage-slide-'))) {
                        keys.push(key);
                    }
                }
                keys.forEach((key) => localStorage.removeItem(key));
            } catch (_) {}

            const stage = document.querySelector('deck-stage');
            if (stage && typeof stage.goTo === 'function') {
                stage.goTo(0);
                history.replaceState(null, '', '#slide-1');
                window.dispatchEvent(new HashChangeEvent('hashchange'));
                return;
            }

            if (Array.isArray(window.DECK_MANIFEST)) {
                history.replaceState(null, '', '#1');
                window.dispatchEvent(new HashChangeEvent('hashchange'));
            }
        }"""
    )
    page.wait_for_timeout(100)


def verify_html(
    html_path: Path,
    output_dir: Path,
    viewports: list[dict[str, int]],
    slides: int | None = None,
    show: bool = False,
    wait_ms: int = 2000,
) -> dict[str, Any]:
    if sync_playwright is None:
        print("ERROR: Playwright is not installed.")
        print("Run: pip install playwright && playwright install chromium")
        raise SystemExit(1)

    if not html_path.exists():
        print(f"ERROR: File does not exist: {html_path}")
        raise SystemExit(1)

    output_dir.mkdir(parents=True, exist_ok=True)
    file_url = html_path.resolve().as_uri()
    runtime_errors: list[str] = []
    screenshots: list[Path] = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=not show)

        for viewport in viewports:
            print(f"\nOpening {file_url} @ {viewport['width']}x{viewport['height']}")

            page = browser.new_page(viewport=viewport)
            attach_error_listeners(page, runtime_errors)
            page.goto(file_url)
            if slides:
                reset_deck_state(page)
            page.wait_for_timeout(wait_ms)

            if slides:
                for slide_index in range(slides):
                    screenshot_path = output_dir / slide_capture_name(html_path, slide_index, viewport)
                    page.screenshot(path=str(screenshot_path))
                    screenshots.append(screenshot_path)
                    print(f"  Saved slide screenshot -> {screenshot_path.name}")
                    if slide_index < slides - 1:
                        page.keyboard.press("ArrowRight")
                        page.wait_for_timeout(300)
            else:
                screenshot_path = output_dir / f"{html_path.stem}-{viewport['width']}x{viewport['height']}.png"
                page.screenshot(path=str(screenshot_path))
                screenshots.append(screenshot_path)
                print(f"  Saved screenshot -> {screenshot_path.name}")

                full_path = output_dir / f"{html_path.stem}-{viewport['width']}x{viewport['height']}-full.png"
                page.screenshot(path=str(full_path), full_page=True)
                screenshots.append(full_path)
                print(f"  Saved full-page screenshot -> {full_path.name}")

            if show:
                print("  Browser window is still open. Press Enter to close it.")
                input()

            page.close()

        browser.close()

    return {
        "html": str(html_path),
        "runtime_errors": runtime_errors,
        "screenshots": [str(path) for path in screenshots],
        "output_dir": str(output_dir),
    }


def print_report(result: dict[str, Any]) -> None:
    print("\nVerification Report")
    print("=" * 60)
    print(f"HTML: {result['html']}")

    runtime_errors = result["runtime_errors"]
    if runtime_errors:
        print(f"\nJavaScript errors: {len(runtime_errors)}")
        for error in runtime_errors[:20]:
            print(f"  - {error}")
        if len(runtime_errors) > 20:
            print(f"  ... and {len(runtime_errors) - 20} more")
    else:
        print("\nNo JavaScript errors.")

    print(f"\nScreenshots saved to: {result['output_dir']}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Verify a local HTML design artifact with Playwright.")
    parser.add_argument("html", help="Path to the HTML file")
    parser.add_argument(
        "--viewports",
        default="1440x900",
        help="Comma-separated viewport list in WxH format",
    )
    parser.add_argument(
        "--slides",
        type=int,
        help="Slide mode: capture the first N slides using ArrowRight",
    )
    parser.add_argument(
        "--output",
        help="Output directory. Defaults to a screenshots folder next to the HTML file.",
    )
    parser.add_argument(
        "--show",
        action="store_true",
        help="Open a visible browser window instead of running headless",
    )
    parser.add_argument(
        "--wait-ms",
        type=int,
        default=2000,
        help="Milliseconds to wait after loading before capture",
    )

    args = parser.parse_args()

    html_path = Path(args.html)
    output_dir = Path(args.output) if args.output else html_path.parent / "screenshots"
    viewports = parse_viewports(args.viewports)

    result = verify_html(
        html_path=html_path,
        output_dir=output_dir,
        viewports=viewports,
        slides=args.slides,
        show=args.show,
        wait_ms=args.wait_ms,
    )
    print_report(result)


if __name__ == "__main__":
    main()
