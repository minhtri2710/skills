# Animations

This file is for engine API and usage how-to.

Use `assets/animations.jsx` for browser-based motion demos unless the task clearly needs a custom engine.

## API Surface

### `Stage`

Props:

- `duration`: total animation length in seconds
- `width`: stage width in pixels
- `height`: stage height in pixels
- `fps`: accepted for compatibility, currently not used by the engine
- `loop`: whether playback loops in preview mode
- `bgColor`: stage background color

Behavior:

- waits for `document.fonts.ready` before the first animation frame when available
- sets `window.__ready = true` on the first animation frame
- disables looping automatically when `window.__recording` is truthy
- uses the full viewport while recording instead of reserving preview-controls space
- treats the built-in controls as preview-only chrome and omits them during recording

### `Sprite`

Props:

- `start`: inclusive start time in seconds
- `end`: exclusive end time in seconds
- `style`: inline style object for the positioned wrapper

### Hooks And Utilities

- `useTime()`: returns the current global stage time in seconds
- `useSprite()`: returns `{ t, elapsed, duration, start, end }`
- `interpolate(t, [inStart, inEnd], [outStart, outEnd], easing?)`: maps one range to another
- `Easing`: exported easing helpers such as `linear`, `easeInOut`, `expoOut`, `overshoot`, and `spring`

### Global Export

When loaded in the browser, the asset exposes:

```js
window.Animations = {
  Stage,
  Sprite,
  useTime,
  useSprite,
  Easing,
  interpolate,
};
```

## Good Uses

- reveal sequences
- launch animations
- explainer visuals
- UI motion demos

## Working Pattern

1. define narrative beats
2. divide them into sprites
3. animate properties with interpolation and easing
4. make the final frame hold cleanly for export

## Export Compatibility

If you build a custom loop, make sure:

- the scene can signal readiness
- recording mode does not keep looping forever
- preview-only chrome is marked with `[data-role="chrome"]`, `[data-record="hidden"]`, or `.no-record`

## Keep It Simple

Most strong motion pieces can be built with:

- opacity
- transform
- clip or mask reveal
- scale
- position
- timed sequencing
