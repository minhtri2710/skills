const test = require('node:test');
const assert = require('node:assert/strict');

const { getDirectChildListItems } = require('../html_list_helpers.cjs');

test('getDirectChildListItems excludes nested list items', () => {
  const nestedChild = { tagName: 'LI' };
  const directParent = {
    tagName: 'LI',
    children: [nestedChild],
  };
  const directSibling = { tagName: 'LI', children: [] };
  const list = {
    children: [
      directParent,
      { tagName: 'DIV' },
      directSibling,
    ],
  };

  assert.deepEqual(getDirectChildListItems(list), [directParent, directSibling]);
});
