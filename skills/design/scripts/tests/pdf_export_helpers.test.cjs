const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const { resolvePdfSlideEntries } = require('../pdf_export_helpers.cjs');

test('resolvePdfSlideEntries honors manifest order', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'pdf-export-'));
  const slidesDir = path.join(root, 'slides');
  fs.mkdirSync(slidesDir);
  fs.writeFileSync(path.join(slidesDir, '10-second.html'), '<html></html>');
  fs.writeFileSync(path.join(slidesDir, '02-first.html'), '<html></html>');
  fs.writeFileSync(
    path.join(root, 'deck_index.html'),
    `<!doctype html><script>
      window.DECK_MANIFEST = [
        { file: "slides/10-second.html" },
        { file: "slides/02-first.html" }
      ];
    </script>`
  );

  const entries = resolvePdfSlideEntries(slidesDir);

  assert.equal(
    entries.map((entry) => entry.file).join('|'),
    'slides/10-second.html|slides/02-first.html'
  );
});
