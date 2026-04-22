# Design Philosophy Showcases

These samples help the agent recommend direction visually instead of describing style in the abstract.

Each showcase ships as HTML source plus a same-stem PNG preview. Regenerate the PNG previews from the skill root with `node scripts/render-showcase-previews.mjs`.

These are sample visual anchors for three house directions only. They do not illustrate all 20 directions in `references/design-styles.md`, and they cover only a subset of the scene types in `references/scene-templates.md`.

## Styles

| Code | Direction | Character |
|---|---|---|
| `Pentagram` | Information architecture | restrained, grid-led, typographic |
| `Build` | Luxury minimalism | quiet, spacious, refined |
| `Takram` | Warm technical design | soft, thoughtful, asymmetric |

## Scene Map

### Content Scenes

| Scene | Size | Pentagram | Build | Takram |
|---|---|---|---|---|
| Cover | 1200×510 | `cover/cover-pentagram` | `cover/cover-build` | `cover/cover-takram` |
| Slide data page | 1920×1080 | `ppt/ppt-pentagram` | `ppt/ppt-build` | `ppt/ppt-takram` |
| Vertical infographic | 1080×1920 | `infographic/infographic-pentagram` | `infographic/infographic-build` | `infographic/infographic-takram` |

### Website Scenes

| Scene | Size | Pentagram | Build | Takram |
|---|---|---|---|---|
| Personal homepage | 1440×900 | `website-homepage/homepage-pentagram` | `website-homepage/homepage-build` | `website-homepage/homepage-takram` |
| AI tools directory | 1440×900 | `website-ai-nav/ainav-pentagram` | `website-ai-nav/ainav-build` | `website-ai-nav/ainav-takram` |
| AI writing app | 1440×900 | `website-ai-writing/aiwriting-pentagram` | `website-ai-writing/aiwriting-build` | `website-ai-writing/aiwriting-takram` |
| SaaS landing page | 1440×900 | `website-saas/saas-pentagram` | `website-saas/saas-build` | `website-saas/saas-takram` |
| Developer docs | 1440×900 | `website-devdocs/devdocs-pentagram` | `website-devdocs/devdocs-build` | `website-devdocs/devdocs-takram` |

## Usage

Use these when recommending directions:

1. choose the closest matching scene
2. show 2 or 3 style variants side by side
3. explain what each style emphasizes

If no scene matches well, skip the showcase and build a fresh sample instead.
