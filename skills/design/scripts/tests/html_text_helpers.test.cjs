const test = require('node:test');
const assert = require('node:assert/strict');

const { SUPPORTED_TEXT_TAGS } = require('../html_text_helpers.cjs');

test('SUPPORTED_TEXT_TAGS keeps editable text tags but excludes button controls', () => {
  assert.ok(SUPPORTED_TEXT_TAGS.includes('A'));
  assert.ok(!SUPPORTED_TEXT_TAGS.includes('BUTTON'));
});
