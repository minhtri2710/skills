# Verification

Read `setup.md` before running `scripts/verify.py`.

Verify every HTML artifact before delivery.

## Minimum Check

1. open the file
2. confirm it renders
3. inspect console errors
4. take screenshots

Use `scripts/verify.py` for the default pass.

## Add These When Needed

- multiple viewports for responsive work
- slide-by-slide capture for decks
- interaction checks for prototypes
- longer waits for motion pieces before capture

## What To Look For

- white screen or broken script
- missing fonts
- layout shift
- interaction bugs
- broken navigation
- stale placeholder content

## Common Command Patterns

```bash
python scripts/verify.py path/to/design.html
python scripts/verify.py path/to/design.html --viewports 1920x1080,375x667
python scripts/verify.py path/to/deck.html --slides 10
python scripts/verify.py path/to/design.html --show
```
