#!/usr/bin/env node

import { chromium } from 'playwright';
import pptxgen from 'pptxgenjs';
import fs from 'fs/promises';
import path from 'path';
import os from 'os';
import { fileURLToPath } from 'url';
import deckHelpers from './deck_helpers.cjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const { resolveSlideEntries, toFileHref } = deckHelpers;

function applyDeckLayout(pres, width, height) {
  pres.defineLayout({ name: 'DECK', width: width / 96, height: height / 96 });
  pres.layout = 'DECK';
}

function parseArgs() {
  const args = { width: 1920, height: 1080, mode: 'image' };
  const a = process.argv.slice(2);
  for (let i = 0; i < a.length; i += 2) {
    const k = a[i].replace(/^--/, '');
    args[k] = a[i + 1];
  }
  if (!args.slides || !args.out) {
    console.error('Usage: node export_deck_pptx.mjs --slides <dir> --out <file.pptx> [--mode image|editable] [--index <deck_index.html>] [--width 1920] [--height 1080]');
    process.exit(1);
  }
  args.width = parseInt(args.width);
  args.height = parseInt(args.height);
  if (!['image', 'editable'].includes(args.mode)) {
    console.error(`Unknown --mode: ${args.mode}. Supported values: image, editable`);
    process.exit(1);
  }
  return args;
}

async function exportImage({ outFile, entries, width, height }) {
  console.log(`[image mode] Rendering ${entries.length} slides as PNG...`);

  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width, height } });
  const page = await ctx.newPage();

  const tmpDir = await fs.mkdtemp(path.join(os.tmpdir(), 'deck-pptx-'));
  const pngs = [];
  for (const entry of entries) {
    const url = toFileHref(entry.absPath);
    await page.goto(url, { waitUntil: 'networkidle' }).catch(() => page.goto(url));
    await page.waitForTimeout(1200);
    const out = path.join(tmpDir, entry.file.replace(/[\\/]/g, '__').replace(/\.html$/, '.png'));
    await page.screenshot({ path: out, fullPage: false });
    pngs.push(out);
    console.log(`  [${pngs.length}/${entries.length}] ${entry.file}`);
  }
  await browser.close();

  const pres = new pptxgen();
  applyDeckLayout(pres, width, height);
  for (const png of pngs) {
    const s = pres.addSlide();
    s.addImage({ path: png, x: 0, y: 0, w: pres.width, h: pres.height });
  }
  await pres.writeFile({ fileName: outFile });

  for (const p of pngs) await fs.unlink(p).catch(() => {});
  await fs.rmdir(tmpDir).catch(() => {});

  console.log(`\n✓ Wrote ${outFile}  (${entries.length} slides, image mode, text is not editable)`);
}

async function exportEditable({ outFile, entries, width, height }) {
  console.log(`[editable mode] Converting ${entries.length} slides via html2pptx...`);

  const { createRequire } = await import('module');
  const require = createRequire(import.meta.url);
  let html2pptx;
  try {
    html2pptx = require(path.join(__dirname, 'html2pptx.js'));
  } catch (e) {
    console.error(`✗ Failed to load html2pptx.js: ${e.message}`);
    console.error('  Make sure the required editable-export dependencies are installed, then try again.');
    process.exit(1);
  }

  const pres = new pptxgen();
  applyDeckLayout(pres, width, height);

  const errors = [];
  for (let i = 0; i < entries.length; i++) {
    const entry = entries[i];
    try {
      await html2pptx(entry.absPath, pres);
      console.log(`  [${i + 1}/${entries.length}] ${entry.file} ✓`);
    } catch (e) {
      console.error(`  [${i + 1}/${entries.length}] ${entry.file} ✗  ${e.message}`);
      errors.push({ file: entry.file, error: e.message });
    }
  }

  if (errors.length) {
    console.error(`\n⚠️ ${errors.length} slide conversions failed. The usual cause is HTML that violates the editable-output constraints.`);
    console.error('  See references/editable-pptx.md for the common failure checklist.');
    if (errors.length === entries.length) {
      console.error('✗ All slides failed. No PPTX was generated.');
      process.exit(1);
    }
  }

  await pres.writeFile({ fileName: outFile });
  console.log(`\n✓ Wrote ${outFile}  (${entries.length - errors.length}/${entries.length} slides, editable mode, text is directly editable in PowerPoint)`);
}

async function main() {
  const { slides, out, index, width, height, mode } = parseArgs();
  const slidesDir = path.resolve(slides);
  const outFile = path.resolve(out);

  const entries = resolveSlideEntries(slidesDir, index);
  if (!entries.length) {
    console.error(`No .html files found in ${slidesDir}`);
    process.exit(1);
  }

  if (mode === 'image') {
    await exportImage({ outFile, entries, width, height });
  } else {
    await exportEditable({ outFile, entries, width, height });
  }
}

main().catch(e => { console.error(e); process.exit(1); });
