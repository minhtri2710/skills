# Video Export

Read `setup.md` before running the export scripts.

Use this after the HTML motion piece is visually correct.

## Output Types

- MP4
- 60fps interpolated MP4
- GIF
- MP4 with BGM

## Workflow

1. verify the HTML visually
2. render the base video with `scripts/render-video.js`
3. convert formats with `scripts/convert-formats.sh`
4. add music with `scripts/add-music.sh` if needed

## Before You Export

Check:

- final frame holds well
- fonts are loaded
- recording mode does not restart the loop
- preview-only chrome is explicitly marked for hiding
- canvas size matches the intended aspect ratio

## Practical Advice

- treat 25fps or 30fps as the base unless a smoother look is required
- use 60fps interpolation only when it adds visible value
- optimize GIFs for the key motion, not every subtle transition
