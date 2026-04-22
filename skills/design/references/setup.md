# Setup

Use this before running design verification or export scripts. This skill ships scripts and starter assets, not a locked dependency manifest, so install the runtime dependencies in the environment where you run the tools.

## Node Tooling

Run these from `skills/design/` when you need the Node-based export scripts:

```bash
npm install --no-save playwright pdf-lib pptxgenjs
npx playwright install chromium
```

These cover:

- `scripts/render-video.js`
- `scripts/html2pptx.js`
- `scripts/export_deck_pdf.mjs`
- `scripts/export_deck_pptx.mjs`
- `scripts/export_deck_stage_pdf.mjs`
- `scripts/render-showcase-previews.mjs`

## Python Verification

Install Playwright for the screenshot verifier:

```bash
python3 -m pip install playwright
python3 -m playwright install chromium
```

This covers:

- `scripts/verify.py`

## System Tools

Install `ffmpeg`; `ffprobe` ships with the same package.

Examples:

```bash
brew install ffmpeg
sudo apt-get install ffmpeg
```

These cover:

- `scripts/render-video.js`
- `scripts/convert-formats.sh`
- `scripts/add-music.sh`

## Troubleshooting

- If Playwright fails at browser launch with a macOS error that mentions `MachPortRendezvousServer` or `bootstrap_check_in ... Permission denied`, the current runtime is blocking headless browser startup. That is an environment-level sandbox problem, not an HTML authoring problem. Run the export or verification scripts in a normal local macOS session or an automation environment that allows browser launch.
- Reinstalling Playwright packages does not fix that specific launch failure if the sandbox itself is denying the browser process.

## Module Split

- `.mjs` files are ESM entrypoints for the newer deck export scripts.
- `.js` and `.cjs` files stay CommonJS for the older export helpers and the editable PPTX converter.
- `export_deck_pptx.mjs` loads `html2pptx.js` through `createRequire`, so keep that split unless you migrate both sides together.

## Naming Convention

- `assets/` use underscore-separated filenames.
- `scripts/` entrypoints use hyphenated names when practical.
- Existing helper filenames stay as-is unless a change is directly required by the task.
