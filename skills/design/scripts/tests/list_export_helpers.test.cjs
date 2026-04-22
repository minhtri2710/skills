const test = require('node:test');
const assert = require('node:assert/strict');

const { decorateListRuns } = require('../list_export_helpers.cjs');

test('decorateListRuns keeps unordered lists as bullets', () => {
  const runs = decorateListRuns({
    listTagName: 'UL',
    index: 0,
    textIndent: 18,
    runs: [{ text: '• First item', options: {} }],
  });

  assert.equal(runs[0].text, 'First item');
  assert.deepEqual(runs[0].options.bullet, { indent: 18 });
});

test('decorateListRuns prefixes ordered list items with numbers', () => {
  const runs = decorateListRuns({
    listTagName: 'OL',
    index: 1,
    textIndent: 18,
    runs: [{ text: 'Second item', options: {} }],
  });

  assert.equal(runs[0].text, '2. Second item');
  assert.equal(runs[0].options.bullet, undefined);
});
