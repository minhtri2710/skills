# Design Context

High-fidelity design should come from existing context whenever possible.

## Context Priority

Use the strongest source available:

1. design system or UI kit
2. codebase
3. shipped product screenshots
4. brand guidelines and assets
5. competitor references the user actually names
6. a fallback design direction

## What To Extract

From code or assets, lift exact values:

- colors
- font stack
- spacing scale
- border radius
- shadow system
- button and card patterns
- grid rhythm

Do not approximate these from memory.

## Reading A Codebase

Start here:

- `theme.*`
- `tokens.*`
- `globals.*`
- representative page shells
- 2 or 3 core components

When you report back, summarize the actual system you found:

```md
Color:
- Primary: #...
- Surface: #...

Type:
- Display: ...
- Body: ...

Spacing:
- 4, 8, 12, 16, 24, 32

Patterns:
- Buttons are ...
- Cards are ...
```

## If The User Says There Is No Context

Do not jump straight to a generic design.

Try to recover context:

- ask for screenshots
- inspect the codebase
- ask for the product URL
- ask for a brand site
- ask for references they actually admire

If nothing exists, say that quality will drop and choose an explicit fallback direction. Make the fallback visible to the user.

## Core Asset Protocol

For branded work, collect:

- logo
- product renders
- UI screenshots
- palette
- fonts
- guidelines

Write the result to `brand-spec.md` with `references/brand-spec-template.md` and include:

- asset paths
- allowed colors
- font stack
- signature details
- forbidden moves
- tone keywords

## Quality Threshold

Prefer fewer better assets over many weak ones.

Check:

- resolution
- source quality
- currentness
- consistency across the set
- whether the asset actually communicates the brand
