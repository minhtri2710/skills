# React Setup

Use this when the deliverable is a standalone HTML artifact powered by React and Babel in the browser.

## Use This Pattern For

- clickable prototypes
- tweakable demos
- visual explainers
- self-contained artifacts that should run without a build step

## Base Pattern

1. Load React, ReactDOM, and Babel in the HTML file.
2. Put app code in a `text/babel` script or split it into local `.jsx` files.
3. Export shared helpers onto `window` when multiple files need them.

## Split Files When

- the page grows beyond what is comfortable to edit in one file
- a starter asset like `ios_frame.jsx` or `design_canvas.jsx` is reused
- motion scenes are easier to isolate per section

## Multi-File Rule

If you split browser-side JSX files, make shared exports explicit:

```js
Object.assign(window, {
  IosFrame,
  DesignCanvas,
  Variation,
});
```

Do not rely on module bundlers in this pattern.

## Common Failure Modes

- missing asset load order
- forgetting to attach exports to `window`
- script tag runs before dependent assets load
- JSX syntax error in minified Babel builds that hides the real issue

## Practical Rules

- keep the first running version simple
- prefer pure HTML and CSS if React adds no real benefit
- keep state shallow for prototypes
- avoid premature component abstraction

## When Not To Use This

Do not use this setup if the task is shipping production UI into an existing app codebase.
