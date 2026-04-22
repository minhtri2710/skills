const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');

const {
  toFileHref,
  toLocalPath,
  resolveSlideEntries,
} = require('../deck_helpers.cjs');

test('toFileHref encodes file paths for browser navigation', () => {
  const href = toFileHref('/tmp/Launch #1/slide 01?.html');
  assert.equal(href, 'file:///tmp/Launch%20%231/slide%2001%3F.html');
});

test('toLocalPath decodes file URLs back to filesystem paths', () => {
  const localPath = toLocalPath('file:///tmp/my%20image%23v1.png');
  assert.equal(localPath, '/tmp/my image#v1.png');
});

test('resolveSlideEntries honors deck manifest order from deck_index.html', () => {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'deck-helpers-'));
  const slidesDir = path.join(root, 'slides');
  fs.mkdirSync(slidesDir);
  fs.writeFileSync(path.join(slidesDir, '10-second.html'), '<html></html>');
  fs.writeFileSync(path.join(slidesDir, '02-first.html'), '<html></html>');
  fs.writeFileSync(
    path.join(root, 'deck_index.html'),
    `<!doctype html><script>
      window.DECK_MANIFEST = [
        { file: "slides/10-second.html", label: "Second" },
        { file: "slides/02-first.html", label: "First" },
      ];
    </script>`
  );

  const entries = resolveSlideEntries(slidesDir);

  assert.equal(
    entries.map((entry) => entry.file).join('|'),
    'slides/10-second.html|slides/02-first.html'
  );
});
