const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

test('html2pptx does not keep an unused sharp dependency at module load time', () => {
  const source = fs.readFileSync(path.resolve(__dirname, '../html2pptx.js'), 'utf8');
  assert.doesNotMatch(source, /require\(['"]sharp['"]\)/);
});

test('html2pptx waits for fonts and remeasures after viewport resize', () => {
  const source = fs.readFileSync(path.resolve(__dirname, '../html2pptx.js'), 'utf8');

  assert.match(source, /async function waitForLayoutReady/);
  assert.match(source, /document\.fonts && document\.fonts\.ready/);
  assert.match(source, /const initialBodyDimensions = await getBodyDimensions\(page\);/);
  assert.match(
    source,
    /await page\.setViewportSize\(\{[\s\S]*?initialBodyDimensions\.width[\s\S]*?initialBodyDimensions\.height[\s\S]*?\}\);\s+await waitForLayoutReady\(page\);\s+bodyDimensions = await getBodyDimensions\(page\);/m
  );
});

test('html2pptx uses Playwright chromium without requiring system Chrome on macOS', () => {
  const source = fs.readFileSync(path.resolve(__dirname, '../html2pptx.js'), 'utf8');

  assert.match(source, /const launchOptions = \{\s*env: \{\s*TMPDIR: tmpDir\s*\}\s*\};/);
  assert.match(source, /const browser = await chromium\.launch\(launchOptions\);/);
  assert.doesNotMatch(source, /launchOptions\.channel = 'chrome'/);
  assert.doesNotMatch(source, /process\.platform === 'darwin'/);
});
