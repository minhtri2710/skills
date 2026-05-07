# Editable PPTX

This file is for editable PowerPoint constraints and exporter limits. Read `setup.md` before running the export scripts.

Use this when the user needs a PowerPoint file with editable text objects rather than flattened slide images.

## Export Modes

- `image`: highest visual fidelity, not editable
- `editable`: lower tolerance for fancy HTML, but text remains editable

## Hard Constraints For Editable Output

1. Keep layout structure simple and explicit.
2. Prefer real text nodes over decorative text effects.
3. Avoid CSS that depends on browser-only rendering tricks.
4. Keep absolute positioning predictable and intentional.

## Supported

- solid fills, borders, and simple rounded rectangles on `div`
- plain text in `<p>`, `<h1>` to `<h6>`, `<ul>`, and `<ol>`
- simple inline formatting such as bold, italic, underline, and color spans
- images inserted with `<img>`
- simple rotation and vertical writing modes

## Risky

- overlapping layers: export order follows DOM order, so DOM order should already match the intended paint order
- whitespace in inline runs: the exporter normalizes repeated whitespace aggressively
- single outer box shadows: simple shadows can work, but treat them as approximate
- nested transforms: basic rotation is supported, nested or compound transforms are only partially supported
- nested lists: single-level lists are safest; deeper nesting may need cleanup after export
- bottom-edge text: the exporter warns when large text boxes end within 0.5" of the slide bottom

## Unsupported

- background images on `div`
- native form controls such as `<button>`; use supported text elements and shape layers instead
- gradients, masks, filters, and blend-mode-dependent rendering
- inset, multiple, or complex layered shadows
- manual bullet characters outside real `<ul>` or `<ol>` lists
- browser-only layout tricks that depend on exact paint behavior

## Authoring Advice

- use strong hierarchy without exotic blend modes
- avoid relying on masks, filters, or browser-specific effects
- favor block layout plus measured offsets
- keep line breaks intentional

## Export Workflow

1. author HTML with the constraints above
2. verify browser rendering
3. export with `scripts/export_deck_pptx.mjs`
4. open the PPTX and inspect actual editability

## What Usually Breaks

- text rendered as effect-heavy decoration
- nested transforms
- layout that depends on browser flow quirks
- overlapping elements that should really be grouped differently
