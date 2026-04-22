const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');

const HOMEPAGE_VARIANTS = [
  '../../assets/showcases/website-homepage/homepage-build.html',
  '../../assets/showcases/website-homepage/homepage-pentagram.html',
  '../../assets/showcases/website-homepage/homepage-takram.html',
];

for (const relativePath of HOMEPAGE_VARIANTS) {
  test(`${path.basename(relativePath)} has matching ids for in-page anchors`, () => {
    const absolutePath = path.resolve(__dirname, relativePath);
    const html = fs.readFileSync(absolutePath, 'utf8');
    const ids = new Set([...html.matchAll(/id="([^"]+)"/g)].map((match) => match[1]));
    const anchors = [...html.matchAll(/href="#([^"]+)"/g)].map((match) => match[1]);

    assert.ok(anchors.length > 0, 'expected at least one in-page anchor');
    for (const anchor of anchors) {
      assert.ok(ids.has(anchor), `missing id="${anchor}" in ${path.basename(relativePath)}`);
    }
  });
}
