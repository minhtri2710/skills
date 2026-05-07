const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const { extractDeckManifest } = require('../deck_helpers.cjs');

test('deck_index starter manifest only references bundled slides', () => {
  const deckIndexPath = path.resolve(__dirname, '../../assets/deck_index.html');
  const html = fs.readFileSync(deckIndexPath, 'utf8');
  const manifest = extractDeckManifest(html);

  assert.ok(Array.isArray(manifest) && manifest.length > 0, 'expected starter manifest entries');

  for (const entry of manifest) {
    const slidePath = path.resolve(path.dirname(deckIndexPath), entry.file);
    assert.ok(fs.existsSync(slidePath), `missing starter slide: ${entry.file}`);
  }
});
