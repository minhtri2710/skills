---
name: design
description: Create high-fidelity HTML-based visual design artifacts such as clickable prototypes, slide decks, motion demos, infographics, design direction explorations, and structured design critiques. Use for polished visual design work and presentation artifacts, including browser, PDF, video, or editable PPTX outputs. Verify named product or brand facts before designing around them. Not for production frontend implementation.
---

# Design

Build high-fidelity visual work in HTML, CSS, JavaScript, and lightweight export tooling. Use this skill for design artifacts and critiques, not shipped product UI.

## Core Rules

1. Verify named product, brand, release, and spec facts before you design around them.
2. Start from existing context and extract real values before inventing a fallback direction.
3. For branded work, gather assets first and freeze them into `brand-spec.md` with `references/brand-spec-template.md`.
4. Show direction early on ambiguous briefs instead of disappearing into a long first pass.
5. Avoid generic AI design defaults. Use real assets, clear typographic intent, and deliberate composition.

Read `references/setup.md` before running any export or verification script.

## Starter Assets

- `assets/design_canvas.jsx`: side-by-side variation layout
- `assets/ios_frame.jsx`: iPhone shell for app prototypes
- `assets/android_frame.jsx`: Android device shell
- `assets/browser_window.jsx`: browser chrome frame
- `assets/macos_window.jsx`: macOS app window frame
- `assets/animations.jsx`: lightweight stage-and-sprite animation engine
- `assets/deck_stage.js`: single-file slide deck shell
- `assets/deck_index.html`: multi-file deck index shell
- `assets/showcases/INDEX.md`: reusable direction samples

## Route Table

Read only the references you need.

| Task | Read | Start from | Verify / Export | Setup needed |
|---|---|---|---|---|
| Context intake or branded work | `references/workflow.md`, `references/design-context.md`, `references/brand-spec-template.md` | existing assets and screenshots | manual context summary | none unless sourcing or export tooling is needed |
| Direction recommendation or fallback exploration | `references/design-styles.md`, `references/scene-templates.md`, `assets/showcases/INDEX.md` | `assets/design_canvas.jsx`, showcase HTML samples | `scripts/verify.py` for screenshots if needed | Playwright Python only if you capture previews |
| App prototype or flow demo | `references/workflow.md`, `references/design-context.md`, `references/scene-templates.md`, `references/content-guidelines.md` | `assets/ios_frame.jsx`, `assets/android_frame.jsx`, `assets/browser_window.jsx`, `assets/macos_window.jsx` | `scripts/verify.py` | Playwright Python |
| Browser or PDF slide deck | `references/slide-decks.md`, `references/verification.md` | `assets/deck_stage.js` or `assets/deck_index.html` | `scripts/verify.py`, `scripts/export_deck_pdf.mjs`, `scripts/export_deck_stage_pdf.mjs` | Playwright, `pdf-lib` |
| Editable PPTX deck | `references/slide-decks.md`, `references/editable-pptx.md`, `references/verification.md` | `assets/deck_index.html` | `scripts/export_deck_pptx.mjs` | Playwright, `pptxgenjs` |
| Motion demo or video export | `references/animations.md`, `references/animation-pitfalls.md`, `references/animation-best-practices.md`, `references/video-export.md` | `assets/animations.jsx` | `scripts/render-video.js`, `scripts/convert-formats.sh`, `scripts/add-music.sh` | Playwright, `ffmpeg` |
| Motion with audio | `references/audio-design-rules.md`, `references/sfx-library.md` | bundled BGM tracks in `assets/` plus sourced SFX | `scripts/add-music.sh` after base render | `ffmpeg`, `ffprobe` |
| Design critique or scored review | `references/critique-guide.md`, `references/content-guidelines.md` | existing artifact or screenshots | structured written critique, optionally `scripts/verify.py` | none unless screenshots are needed |
| Live tweak panels or specialized motion references | `references/tweaks-system.md`, `references/apple-gallery-showcase.md`, `references/hero-animation-case-study.md`, `references/react-setup.md` | task-specific starter shell | task-specific verification | varies; check `references/setup.md` first |

## Deliverable Rules

- Keep the output proportional to the task.
- Prefer a strong small demo over a sprawling weak one.
- Use placeholders only when a missing asset blocks correct execution.
- Tell the user what is placeholder and what is final.
- End with caveats and next steps, not a long changelog.
