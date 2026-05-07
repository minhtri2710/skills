#!/usr/bin/env node

import { chromium } from 'playwright';
import fs from 'fs/promises';
import path from 'path';
import { fileURLToPath } from 'url';
import deckHelpers from './deck_helpers.cjs';

const { toFileHref } = deckHelpers;
const __dirname = path.dirname(fileURLToPath(import.meta.url));
const SHOWCASES_ROOT = path.resolve(__dirname, '../assets/showcases');

async function listHtmlFiles(rootDir) {
  const entries = await fs.readdir(rootDir, { withFileTypes: true });
  const files = await Promise.all(entries.map(async (entry) => {
    const fullPath = path.join(rootDir, entry.name);
    if (entry.isDirectory()) {
      return listHtmlFiles(fullPath);
    }
    return entry.isFile() && entry.name.endsWith('.html') ? [fullPath] : [];
  }));
  return files.flat().sort();
}

async function waitForLayout(page) {
  await page.waitForLoadState('load');
  await page.evaluate(async () => {
    if (document.fonts && document.fonts.ready) {
      try {
        await document.fonts.ready;
      } catch (_) {}
    }

    await new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve)));
  });
}

async function readBodySize(page) {
  return page.evaluate(() => {
    const body = document.body;
    const html = document.documentElement;
    return {
      width: Math.max(body.scrollWidth, body.clientWidth, html.scrollWidth, html.clientWidth),
      height: Math.max(body.scrollHeight, body.clientHeight, html.scrollHeight, html.clientHeight)
    };
  });
}

async function main() {
  const htmlFiles = await listHtmlFiles(SHOWCASES_ROOT);
  if (!htmlFiles.length) {
    console.error(`No showcase HTML files found in ${SHOWCASES_ROOT}`);
    process.exit(1);
  }

  const browser = await chromium.launch();

  try {
    for (const htmlFile of htmlFiles) {
      const context = await browser.newContext({ viewport: { width: 1280, height: 720 } });
      const page = await context.newPage();
      const pngFile = htmlFile.replace(/\.html$/, '.png');

      await page.goto(toFileHref(htmlFile));
      await waitForLayout(page);

      const bodySize = await readBodySize(page);
      await page.setViewportSize({
        width: Math.max(1, Math.round(bodySize.width)),
        height: Math.max(1, Math.round(bodySize.height))
      });
      await waitForLayout(page);

      await page.screenshot({ path: pngFile });
      await context.close();

      console.log(`${path.relative(SHOWCASES_ROOT, htmlFile)} -> ${path.relative(SHOWCASES_ROOT, pngFile)}`);
    }
  } finally {
    await browser.close();
  }
}

main().catch((error) => {
  console.error(error);
  process.exit(1);
});
