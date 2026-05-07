const { resolveSlideEntries } = require('./deck_helpers.cjs');

function resolvePdfSlideEntries(slidesDir, indexFile) {
  return resolveSlideEntries(slidesDir, indexFile);
}

module.exports = {
  resolvePdfSlideEntries,
};
