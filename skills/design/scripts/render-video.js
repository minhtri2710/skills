#!/usr/bin/env node

const { chromium } = require('playwright');
const path = require('path');
const fs = require('fs');
const { spawnSync } = require('child_process');
const { toFileHref } = require('./deck_helpers.cjs');

function arg(name, def) {
  const p = process.argv.find(a => a.startsWith('--' + name + '='));
  return p ? p.slice(name.length + 3) : def;
}
function hasFlag(name) {
  return process.argv.includes('--' + name);
}

const HTML_FILE = process.argv[2];
if (!HTML_FILE || HTML_FILE.startsWith('--')) {
  console.error('Usage: node render-video.js <html-file>');
  console.error('Example: NODE_PATH=$(npm root -g) node render-video.js my-animation.html');
  process.exit(1);
}

const DURATION  = parseFloat(arg('duration', '30'));
const WIDTH     = parseInt(arg('width', '1920'));
const HEIGHT    = parseInt(arg('height', '1080'));
const TRIM_OVERRIDE = arg('trim', null);
const FONT_WAIT = parseFloat(arg('fontwait', '1.5'));
const READY_TIMEOUT = parseFloat(arg('readytimeout', '8'));
const KEEP_CHROME = hasFlag('keep-chrome');
const TRIM_VALUE = TRIM_OVERRIDE === null ? null : parseFloat(TRIM_OVERRIDE);

const HTML_ABS = path.resolve(HTML_FILE);
const BASENAME = path.basename(HTML_FILE, path.extname(HTML_FILE));
const DIR      = path.dirname(HTML_ABS);
const TMP_DIR  = path.join(DIR, '.video-tmp-' + Date.now() + '-' + process.pid);
const MP4_OUT  = path.join(DIR, BASENAME + '.mp4');

const HIDE_CHROME_CSS = `
  .no-record,
  [data-role="chrome"], [data-record="hidden"] {
    display: none !important;
  }
`;

function assertFiniteNumber(flagName, value, { integer = false, min = 0, allowZero = false } = {}) {
  if (!Number.isFinite(value)) {
    throw new Error(`--${flagName} must be a finite number`);
  }
  if (integer && !Number.isInteger(value)) {
    throw new Error(`--${flagName} must be an integer`);
  }
  if (allowZero ? value < min : value <= min) {
    const comparator = allowZero ? `>= ${min}` : `> ${min}`;
    throw new Error(`--${flagName} must be ${comparator}`);
  }
}

function validateArgs() {
  if (!fs.existsSync(HTML_ABS)) {
    throw new Error(`HTML file not found: ${HTML_ABS}`);
  }

  assertFiniteNumber('duration', DURATION);
  assertFiniteNumber('width', WIDTH, { integer: true });
  assertFiniteNumber('height', HEIGHT, { integer: true });
  assertFiniteNumber('fontwait', FONT_WAIT, { allowZero: true });
  assertFiniteNumber('readytimeout', READY_TIMEOUT);
  if (TRIM_VALUE !== null) {
    assertFiniteNumber('trim', TRIM_VALUE, { allowZero: true });
  }
}

function assertCommandAvailable(command) {
  const probe = spawnSync(command, ['-version'], { stdio: 'ignore' });
  if (probe.error || probe.status !== 0) {
    throw new Error(`Missing required tool: ${command}. Install it before running render-video.js.`);
  }
}

async function closeQuietly(resource) {
  if (!resource) return;
  await resource.close().catch(() => {});
}

console.log(`▸ Rendering: ${HTML_FILE}`);
console.log(`  size: ${WIDTH}x${HEIGHT} · duration: ${DURATION}s · hide-chrome: ${!KEEP_CHROME}`);
console.log(`  output: ${MP4_OUT}`);

async function main() {
  validateArgs();
  assertCommandAvailable('ffmpeg');

  fs.mkdirSync(TMP_DIR, { recursive: true });

  const url = toFileHref(HTML_ABS);
  let browser;
  let warmupCtx;
  let recordCtx;
  let page;

  try {
    browser = await chromium.launch();

    console.log('▸ Warmup (caching fonts)…');
    warmupCtx = await browser.newContext({
      viewport: { width: WIDTH, height: HEIGHT },
    });
    const warmupPage = await warmupCtx.newPage();
    await warmupPage.goto(url, { waitUntil: 'load', timeout: 60000 });
    await warmupPage.waitForTimeout(FONT_WAIT * 1000);
    await closeQuietly(warmupPage);
    await closeQuietly(warmupCtx);
    warmupCtx = null;

    console.log('▸ Recording (clean start)…');
    recordCtx = await browser.newContext({
      viewport: { width: WIDTH, height: HEIGHT },
      deviceScaleFactor: 1,
      recordVideo: {
        dir: TMP_DIR,
        size: { width: WIDTH, height: HEIGHT },
      },
    });

    await recordCtx.addInitScript(() => { window.__recording = true; });

    if (!KEEP_CHROME) {
      await recordCtx.addInitScript((css) => {
        const injectStyle = () => {
          const style = document.createElement('style');
          style.setAttribute('data-inject', 'render-video-chrome-hide');
          style.textContent = css;
          (document.head || document.documentElement).appendChild(style);
        };

        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', injectStyle, { once: true });
        } else {
          injectStyle();
        }
      }, HIDE_CHROME_CSS);
    }

    const T0 = Date.now();
    page = await recordCtx.newPage();
    await page.goto(url, { waitUntil: 'load', timeout: 60000 });

    let animationStartSec;
    const hasReady = await page.waitForFunction(
      () => window.__ready === true,
      { timeout: READY_TIMEOUT * 1000 },
    ).then(() => true).catch(() => false);

    if (hasReady) {
      const seekCorrected = await page.evaluate(() => {
        if (typeof window.__seek === 'function') {
          window.__seek(0);
          return true;
        }
        return false;
      });
      if (seekCorrected) {
        await page.evaluate(() => new Promise((resolve) => requestAnimationFrame(() => requestAnimationFrame(resolve))));
      }
      animationStartSec = (Date.now() - T0) / 1000;
      console.log(`▸ Ready at ${animationStartSec.toFixed(2)}s (from window.__ready${seekCorrected ? ' + __seek(0) correction' : ''})`);
    } else {
      await page.waitForTimeout(FONT_WAIT * 1000);
      animationStartSec = (Date.now() - T0) / 1000;
      console.log('');
      console.log(`  ⚠️  WARNING: window.__ready signal not detected within ${READY_TIMEOUT}s`);
      console.log(`     Recording will use fallback trim of ${animationStartSec.toFixed(2)}s + 0.5s safety margin.`);
      console.log(`     This is UNRELIABLE — your video may start mid-animation or skip frames.`);
      console.log('');
      console.log(`     FIX: in your HTML's animation tick (or rAF first frame), add:`);
      console.log(`        window.__ready = true;`);
      console.log(`     animations.jsx-based HTML does this automatically. If you wrote your`);
      console.log(`     own Stage, see references/animation-pitfalls.md -> Export Safety for the pattern.`);
      console.log('');
    }

    await page.waitForTimeout(DURATION * 1000 + 300);

    await closeQuietly(page);
    page = null;
    await closeQuietly(recordCtx);
    recordCtx = null;
    await closeQuietly(browser);
    browser = null;

    const webmFiles = fs.readdirSync(TMP_DIR).filter((file) => file.endsWith('.webm'));
    if (webmFiles.length === 0) {
      throw new Error('No webm produced');
    }
    const webmPath = path.join(TMP_DIR, webmFiles[0]);
    console.log(`▸ WebM: ${(fs.statSync(webmPath).size / 1024 / 1024).toFixed(1)} MB`);

    const resolvedTrim = TRIM_VALUE !== null
      ? TRIM_VALUE
      : animationStartSec + (hasReady ? 0.05 : 0.5);

    console.log(`▸ ffmpeg: trim=${resolvedTrim.toFixed(2)}s${TRIM_VALUE !== null ? ' (manual)' : ' (auto)'}, encode H.264…`);
    const ffmpeg = spawnSync('ffmpeg', [
      '-y',
      '-ss', String(resolvedTrim),
      '-i', webmPath,
      '-t', String(DURATION),
      '-c:v', 'libx264',
      '-pix_fmt', 'yuv420p',
      '-crf', '18',
      '-preset', 'medium',
      '-movflags', '+faststart',
      MP4_OUT,
    ], { stdio: ['ignore', 'ignore', 'pipe'] });

    if (ffmpeg.status !== 0) {
      throw new Error('ffmpeg failed:\n' + ffmpeg.stderr.toString().slice(-2000));
    }

    const mp4Size = (fs.statSync(MP4_OUT).size / 1024 / 1024).toFixed(1);
    console.log(`✓ Done: ${MP4_OUT} (${mp4Size} MB)`);
  } finally {
    await closeQuietly(page);
    await closeQuietly(recordCtx);
    await closeQuietly(warmupCtx);
    await closeQuietly(browser);
    fs.rmSync(TMP_DIR, { recursive: true, force: true });
  }
}

main().catch((error) => {
  console.error(`✗ ${error.message}`);
  process.exit(1);
});
