# Slide Decks

Ask the export target before writing the deck.

If you plan to run PDF or PPTX export scripts, read `setup.md` first.

## First Question

Which one matters most?

- browser presentation
- PDF
- editable PPTX

This choice affects the authoring strategy from the first slide.

## Two Deck Architectures

### Single File

Use `assets/deck_stage.js` when:

- the deck is short
- slides share state
- the deck should be easy to preview as one file
- the export target is browser presentation or PDF, not editable PPTX

### Multi File

Use `assets/deck_index.html` when:

- the deck is long
- multiple people or agents may work on different slides
- slide styles should be isolated
- the output must support editable PPTX export through `scripts/export_deck_pptx.mjs`

## Single-File Rules

- author each slide as a section inside the deck shell
- keep canvas sizing consistent
- verify keyboard navigation
- check speaker notes only if the task needs them

## Multi-File Rules

- each slide should be independently viewable
- avoid cross-slide CSS coupling
- keep shared tokens in a small shared stylesheet only when needed
- list slides explicitly in the index manifest

## Editable PPTX Warning

If editable PPTX matters, read `editable-pptx.md` before you start. Retrofitting an image-first deck into editable PPTX later is wasteful.
For editable PPTX, choose the multi-file architecture from the start.

## Verification

Check:

- all slides render
- text is legible at presentation size
- keyboard controls work
- exported page count matches the authored slide count
