const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

function readSource() {
  return fs.readFileSync(path.resolve(__dirname, '../render-video.js'), 'utf8');
}

test('render-video only hides explicit chrome markers', () => {
  const source = readSource();

  assert.match(source, /\.no-record,/);
  assert.match(source, /\[data-role="chrome"\], \[data-record="hidden"\]/);
  assert.doesNotMatch(source, /\.masthead|\.kicker|\.title|\.footer|\.progress|\.counter|\.replay/);
});

test('render-video validates tooling and uses heading-based doc references', () => {
  const source = readSource();

  assert.match(source, /assertCommandAvailable\('ffmpeg'\)/);
  assert.match(source, /async function closeQuietly/);
  assert.match(source, /see references\/animation-pitfalls\.md -> Export Safety/);
  assert.doesNotMatch(source, /§12/);
});
