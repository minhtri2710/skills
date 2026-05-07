# Tweaks System

Use tweaks when the user benefits from live comparison without maintaining multiple files.

## Good Tweak Axes

- color palette
- type pairing
- density
- spacing
- hero layout
- motion intensity

## Implementation Pattern

1. define defaults
2. store current values in state
3. persist to `localStorage` when useful
4. drive visual switches through clear mapping logic

## Good Usage

- one HTML artifact
- a small control panel
- 2 to 6 meaningful parameters

## Bad Usage

- a control for every small CSS property
- unrelated controls mixed together
- toggles that create broken intermediate states

## Rule

Tweaks should help the user choose direction, not become a low-level design editor.
