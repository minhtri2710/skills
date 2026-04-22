const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');
const { fileURLToPath, pathToFileURL } = require('node:url');

function toFileHref(filePath) {
  return pathToFileURL(path.resolve(filePath)).href;
}

function toLocalPath(filePath) {
  if (typeof filePath !== 'string' || !filePath.startsWith('file://')) {
    return filePath;
  }
  return fileURLToPath(filePath);
}

function extractDeckManifest(html) {
  const match = html.match(/window\.DECK_MANIFEST\s*=\s*(\[[\s\S]*?\])\s*;/);
  if (!match) {
    return null;
  }

  const manifest = new vm.Script(`(${match[1]})`).runInNewContext({});
  if (!Array.isArray(manifest)) {
    throw new Error('window.DECK_MANIFEST must evaluate to an array');
  }
  return manifest;
}

function listDirectorySlides(slidesDir) {
  return fs.readdirSync(slidesDir)
    .filter((file) => file.endsWith('.html'))
    .sort()
    .map((file) => ({
      file,
      absPath: path.join(slidesDir, file),
    }));
}

function resolveIndexFile(slidesDir, indexFile) {
  if (indexFile) {
    const resolved = path.resolve(indexFile);
    if (!fs.existsSync(resolved)) {
      throw new Error(`Deck index file not found: ${resolved}`);
    }
    return resolved;
  }

  const candidates = [
    path.resolve(slidesDir, '..', 'deck_index.html'),
    path.resolve(slidesDir, 'deck_index.html'),
  ];

  return candidates.find((candidate) => fs.existsSync(candidate)) || null;
}

function resolveSlideEntries(slidesDir, indexFile) {
  const resolvedSlidesDir = path.resolve(slidesDir);
  const manifestPath = resolveIndexFile(resolvedSlidesDir, indexFile);

  if (!manifestPath) {
    return listDirectorySlides(resolvedSlidesDir);
  }

  const manifest = extractDeckManifest(fs.readFileSync(manifestPath, 'utf8'));
  if (!manifest) {
    if (indexFile) {
      throw new Error(`No window.DECK_MANIFEST found in ${manifestPath}`);
    }
    return listDirectorySlides(resolvedSlidesDir);
  }

  return manifest.map((entry, index) => {
    const file = typeof entry === 'string' ? entry : entry?.file;
    if (typeof file !== 'string' || !file.trim()) {
      throw new Error(`Invalid manifest entry at index ${index}: missing file`);
    }

    const absPath = path.resolve(path.dirname(manifestPath), file);
    if (!fs.existsSync(absPath)) {
      throw new Error(`Manifest slide not found: ${file}`);
    }

    return {
      file: String(file),
      absPath,
      label: typeof entry === 'object' && typeof entry.label === 'string' ? String(entry.label) : undefined,
    };
  });
}

module.exports = {
  extractDeckManifest,
  resolveSlideEntries,
  toFileHref,
  toLocalPath,
};
