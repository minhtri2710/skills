#!/usr/bin/env node

import { chromium } from 'playwright';
import { PDFDocument } from 'pdf-lib';
import fs from 'fs/promises';
import path from 'path';
import deckHelpers from './deck_helpers.cjs';
import pdfExportHelpers from './pdf_export_helpers.cjs';

const { toFileHref } = deckHelpers;
const { resolvePdfSlideEntries } = pdfExportHelpers;

function parseArgs() {
  const args = { width: 1920, height: 1080 };
  const a = process.argv.slice(2);
  for (let i = 0; i < a.length; i += 2) {
    const k = a[i].replace(/^--/, '');
    args[k] = a[i + 1];
  }
  if (!args.slides || !args.out) {
    console.error('Usage: node export_deck_pdf.mjs --slides <dir> --out <file.pdf> [--width 1920] [--height 1080]');
    process.exit(1);
  }
  args.width = parseInt(args.width);
  args.height = parseInt(args.height);
  return args;
}

async function main() {
  const { slides, out, width, height } = parseArgs();
  const slidesDir = path.resolve(slides);
  const outFile = path.resolve(out);

  const entries = resolvePdfSlideEntries(slidesDir);
  if (!entries.length) {
    console.error(`No .html files found in ${slidesDir}`);
    process.exit(1);
  }
  console.log(`Found ${entries.length} slides in ${slidesDir}`);

  const browser = await chromium.launch();
  const ctx = await browser.newContext({ viewport: { width, height } });

  const pageBuffers = [];
  for (const entry of entries) {
    const page = await ctx.newPage();
    const url = toFileHref(entry.absPath);
    await page.goto(url, { waitUntil: 'networkidle' }).catch(() => page.goto(url));
    await page.waitForTimeout(1200);
    await page.emulateMedia({ media: 'screen' });
    const buf = await page.pdf({
      width: `${width}px`,
      height: `${height}px`,
      printBackground: true,
      margin: { top: 0, right: 0, bottom: 0, left: 0 },
      preferCSSPageSize: false,
    });
    pageBuffers.push(buf);
    await page.close();
    console.log(`  [${pageBuffers.length}/${entries.length}] ${entry.file}`);
  }

  await browser.close();

  const merged = await PDFDocument.create();
  for (const buf of pageBuffers) {
    const src = await PDFDocument.load(buf);
    const copied = await merged.copyPages(src, src.getPageIndices());
    copied.forEach(p => merged.addPage(p));
  }
  const bytes = await merged.save();
  await fs.writeFile(outFile, bytes);

  const kb = (bytes.byteLength / 1024).toFixed(0);
  console.log(`\n✓ Wrote ${outFile}  (${kb} KB, ${entries.length} pages, vector)`);
}

main().catch(e => { console.error(e); process.exit(1); });
