import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import http from 'node:http';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const templates = path.join(root, 'templates');
const mime = { '.html': 'text/html', '.css': 'text/css', '.mjs': 'text/javascript', '.js': 'text/javascript', '.json': 'application/json' };

let browser = null;
let server = null;
let base = '';
let skipReason = '';

test.before(async () => {
  try {
    const { launchBrowser } = await import(pathToFileURL(path.join(root, 'skills/atlas-checker/scripts/browser-runtime.mjs')).href);
    browser = await launchBrowser();
    const probeContext = await browser.newContext({ viewport: { width: 400, height: 700 } });
    const probePage = await probeContext.newPage();
    const capable = typeof probeContext.close === 'function' && probePage.keyboard && typeof probePage.locator === 'function';
    await probeContext.close?.();
    if (!capable) {
      await browser.close?.();
      browser = null;
      skipReason = 'browser lacks Playwright contexts (CDP fallback)';
      return;
    }
  } catch (err) {
    skipReason = `no browser: ${err.message.slice(0, 60)}`;
    return;
  }
  server = http.createServer((req, res) => {
    const file = path.join(templates, decodeURIComponent(req.url.split('?')[0]));
    if (!fs.existsSync(file) || fs.statSync(file).isDirectory()) { res.writeHead(404); res.end(); return; }
    res.writeHead(200, { 'Content-Type': mime[path.extname(file)] || 'application/octet-stream' });
    fs.createReadStream(file).pipe(res);
  });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  base = `http://127.0.0.1:${server.address().port}/atlas-loops-demo.html`;
});

test.after(async () => {
  await browser?.close();
  server?.close();
});

async function open(options = {}, viewport = { width: 1440, height: 900 }, query = '') {
  const context = await browser.newContext({ viewport, ...options });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(base + query, { waitUntil: 'networkidle' });
  await page.waitForTimeout(600);
  // false when Anime.js could not load (the loops then show their static frames) or motion is reduced
  const hasLoops = await page.evaluate(() => Boolean(window.__loops?.animated));
  return { page, context, errors, hasLoops };
}

const center = (page, selector) => page.evaluate((s) => document.querySelector(s).scrollIntoView({ block: 'center', behavior: 'instant' }), selector);
const state = (page, selector) => page.evaluate((s) => document.querySelector(s).dataset.loopState, selector);

test('loops: the demo types, brings in rows, then resets and plays again', async (t) => {
  if (skipReason) return t.skip(skipReason);
  const { page, context, errors, hasLoops } = await open();
  if (!hasLoops) { await context.close(); return t.skip('Anime.js CDN unreachable'); }
  await center(page, '#demo');
  const samples = [];
  for (let i = 0; i < 70; i++) {
    samples.push(await page.evaluate(() => ({
      typed: document.querySelector('#typed').textContent.length,
      row: Number(getComputedStyle(document.querySelector('#demo [data-loop-row]')).opacity),
      foot: Number(getComputedStyle(document.querySelector('#demo [data-loop-foot]')).opacity)
    })));
    await page.waitForTimeout(150);
  }
  const full = 'roasted coffee beans'.length;
  const peak = samples.findIndex((s) => s.typed === full);
  assert.ok(peak >= 0, 'the full line is typed at some point');
  assert.ok(samples.some((s, i) => i > peak && s.row > 0.95 && s.foot > 0.95), 'rows and the result line appear after typing');
  assert.ok(samples.some((s, i) => i > peak && s.typed < full / 2), 'after the hold the demo resets and types again');
  assert.deepEqual(errors, []);
  await context.close();
});

test('loops: everything pauses off screen, with a pause button and a page-level toggle', async (t) => {
  if (skipReason) return t.skip(skipReason);
  const { page, context, hasLoops } = await open();
  if (!hasLoops) { await context.close(); return t.skip('Anime.js CDN unreachable'); }
  await center(page, '#demo');
  await page.waitForTimeout(500);
  assert.equal(await state(page, '#demo'), 'playing');

  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
  await page.waitForTimeout(400);
  assert.equal(await state(page, '#demo'), 'paused', 'off screen');
  const before = await page.evaluate(() => document.querySelector('#typed').textContent);
  await page.waitForTimeout(700);
  assert.equal(await page.evaluate(() => document.querySelector('#typed').textContent), before, 'no typing while off screen');

  await center(page, '#demo');
  await page.waitForTimeout(500);
  assert.equal(await state(page, '#demo'), 'playing');
  const button = page.locator('#demo > .atlas-pause');
  const box = await button.boundingBox();
  assert.ok(box.width >= 44 && box.height >= 44, 'the pause button is a 44px target');
  await button.click();
  assert.equal(await state(page, '#demo'), 'user-paused');
  assert.equal(await button.getAttribute('aria-pressed'), 'true');
  await page.evaluate(() => window.scrollTo({ top: 0, behavior: 'instant' }));
  await page.waitForTimeout(300);
  await center(page, '#demo');
  await page.waitForTimeout(500);
  assert.equal(await state(page, '#demo'), 'user-paused', 'it does not resume by itself after being paused');
  await button.click();
  await page.waitForTimeout(300);
  assert.equal(await state(page, '#demo'), 'playing');

  await page.locator('[data-loops-toggle]').click();
  await page.waitForTimeout(200);
  assert.equal(await state(page, '#demo'), 'user-paused', 'the page-level toggle pauses every loop');
  await page.locator('[data-loops-toggle]').click(); // the toggle sits at the top, so the demo leaves the screen
  await center(page, '#demo');
  await page.waitForTimeout(500);
  assert.equal(await state(page, '#demo'), 'playing', 'toggling back resumes loops that are on screen');
  await context.close();
});

test('loops: reduced motion shows finished frames and nothing moves', async (t) => {
  if (skipReason) return t.skip(skipReason);
  const { page, context } = await open({ reducedMotion: 'reduce' });
  for (const selector of ['#demo', '#terminal', '#rotator', '#ticker']) {
    assert.equal(await state(page, selector), 'static', `${selector} is static`);
  }
  assert.equal(await page.evaluate(() => document.querySelector('#typed').textContent), 'roasted coffee beans', 'the typed line shows in full');
  assert.equal(await page.evaluate(() => getComputedStyle(document.querySelector('#ticker .atlas-marquee__track')).animationName), 'none');
  assert.equal(await page.evaluate(() => document.querySelectorAll('#ticker .atlas-marquee__group').length), 1, 'no duplicate ticker group');
  const shown = await page.evaluate(() => [...document.querySelectorAll('.atlas-pause')].filter((b) => getComputedStyle(b).display !== 'none' && b.dataset.loopsToggle === undefined && !b.hasAttribute('data-loops-toggle')).length);
  assert.equal(shown, 0, 'no pause buttons are needed when nothing moves');
  await context.close();
});

test('loops: the rotator keeps its width and cycles through its words', async (t) => {
  if (skipReason) return t.skip(skipReason);
  const { page, context, hasLoops } = await open();
  if (!hasLoops) { await context.close(); return t.skip('Anime.js CDN unreachable'); }
  const widths = new Set();
  const visible = new Set();
  for (let i = 0; i < 16; i++) {
    const sample = await page.evaluate(() => {
      const el = document.querySelector('#rotator');
      const words = [...el.children];
      return { width: Math.round(el.getBoundingClientRect().width), current: words.findIndex((w) => Number(getComputedStyle(w).opacity) > 0.6) };
    });
    widths.add(sample.width);
    if (sample.current >= 0) visible.add(sample.current);
    await page.waitForTimeout(500);
  }
  assert.equal(widths.size, 1, `the width must not change: ${[...widths].join(', ')}`);
  assert.ok(visible.size >= 2, `the words should take turns, saw ${[...visible].join(',')}`);
  await context.close();
});

test('loops: the ticker is seamless, pauses on demand and on hover', async (t) => {
  if (skipReason) return t.skip(skipReason);
  const { page, context } = await open();
  const groups = await page.evaluate(() => [...document.querySelectorAll('#ticker .atlas-marquee__group')].map((g) => g.getAttribute('aria-hidden')));
  assert.deepEqual(groups, [null, 'true'], 'one real group and one hidden copy');
  const play = () => page.evaluate(() => getComputedStyle(document.querySelector('#ticker .atlas-marquee__track')).animationPlayState);
  const position = () => page.evaluate(() => new DOMMatrix(getComputedStyle(document.querySelector('#ticker .atlas-marquee__track')).transform).m41);
  assert.equal(await play(), 'running');
  const a = await position();
  await page.waitForTimeout(400);
  assert.ok((await position()) < a, 'it scrolls');
  await page.locator('#ticker > .atlas-pause').click();
  assert.equal(await play(), 'paused');
  const frozen = await position();
  await page.waitForTimeout(400);
  assert.ok(Math.abs((await position()) - frozen) < 3, 'a paused ticker does not drift (a running one moves about 24px in 400ms)');
  await page.locator('#ticker > .atlas-pause').click();
  await page.mouse.move(300, 120);
  await page.locator('#ticker').hover();
  assert.equal(await play(), 'paused', 'hover pauses');
  await context.close();
});

test('loops: ambient layers obey the page-level pause and cannot restart while paused', async (t) => {
  if (skipReason) return t.skip(skipReason);
  const { page, context, hasLoops } = await open();
  if (!hasLoops) { await context.close(); return t.skip('Anime.js CDN unreachable'); }
  await center(page, '#fx');
  await page.waitForTimeout(400);
  assert.equal(await page.evaluate(() => document.querySelector('#fx').classList.contains('is-paused')), false, 'running while visible');
  await page.locator('[data-loops-toggle]').click();
  await center(page, '#fx');
  await page.waitForTimeout(400);
  assert.equal(await page.evaluate(() => document.querySelector('#fx').classList.contains('is-paused')), true, 'paused globally even when scrolled into view');
  assert.equal(await state(page, '#fx'), 'user-paused');
  await context.close();
});

test('loops: a page with rotators or ambient layers and no toggle gets a pause control automatically', async (t) => {
  if (skipReason) return t.skip(skipReason);
  const { page, context, hasLoops } = await open({}, { width: 1440, height: 900 }, '?bare=1');
  if (!hasLoops) { await context.close(); return t.skip('Anime.js CDN unreachable'); }
  const button = page.locator('.atlas-pause--floating[data-loops-toggle]');
  assert.equal(await button.count(), 1, 'one automatic page-level toggle');
  const box = await button.boundingBox();
  assert.ok(box.width >= 44 && box.height >= 44, 'a 44px target');
  assert.equal(await state(page, '#rotator'), 'playing');
  await button.click();
  assert.equal(await state(page, '#rotator'), 'user-paused', 'the rotator can be stopped');
  await button.click();
  await page.waitForTimeout(300);
  assert.equal(await state(page, '#rotator'), 'playing');
  await context.close();
});

test('loops: a short ticker is repeated until each half covers a wide viewport', async (t) => {
  if (skipReason) return t.skip(skipReason);
  const { page, context } = await open({}, { width: 1920, height: 1080 });
  const metrics = await page.evaluate(() => {
    const host = document.querySelector('#ticker');
    const groups = [...host.querySelectorAll('.atlas-marquee__group')];
    return { host: host.clientWidth, half: groups[0].scrollWidth, groups: groups.length };
  });
  assert.equal(metrics.groups, 2);
  assert.ok(metrics.half >= metrics.host, `each half (${metrics.half}px) must cover the viewport (${metrics.host}px)`);
  await context.close();
});

test('loops: the demo card keeps its height while a long line is typed on a narrow screen', async (t) => {
  if (skipReason) return t.skip(skipReason);
  const { page, context, hasLoops } = await open({}, { width: 390, height: 844 });
  if (!hasLoops) { await context.close(); return t.skip('Anime.js CDN unreachable'); }
  await center(page, '#terminal');
  const heights = new Set();
  for (let i = 0; i < 34; i++) {
    heights.add(await page.evaluate(() => Math.round(document.querySelector('#terminal').getBoundingClientRect().height)));
    await page.waitForTimeout(200);
  }
  assert.equal(heights.size, 1, `the card must not change height: ${[...heights].join(', ')}`);
  await context.close();
});

test('loops: the caret stops blinking when its demo is paused', async (t) => {
  if (skipReason) return t.skip(skipReason);
  const { page, context, hasLoops } = await open();
  if (!hasLoops) { await context.close(); return t.skip('Anime.js CDN unreachable'); }
  // the demo is below the fold, so it is paused; pretend it was mid-typing when it stopped
  const result = await page.evaluate(() => {
    const demo = document.querySelector('#demo');
    demo.dataset.loopPhase = 'type';
    return { state: demo.dataset.loopState, play: getComputedStyle(demo.querySelector('.atlas-loop__caret')).animationPlayState };
  });
  assert.equal(result.state, 'paused');
  assert.equal(result.play, 'paused');
  await context.close();
});

test('loops: hover and focus holds are independent', async (t) => {
  if (skipReason) return t.skip(skipReason);
  const { page, context } = await open();
  const held = () => page.evaluate(() => document.querySelector('#ticker .atlas-marquee__track').classList.contains('is-paused'));
  await page.locator('#tick-link').focus();
  assert.equal(await held(), true, 'focus holds');
  await page.locator('#ticker').hover();
  await page.mouse.move(5, 5);
  await page.waitForTimeout(150);
  assert.equal(await held(), true, 'leaving with the pointer must not release a focus hold');
  await page.evaluate(() => document.activeElement.blur());
  await page.waitForTimeout(150);
  assert.equal(await held(), false, 'released once neither hover nor focus is active');
  await context.close();
});

test('loops: ticker copies never duplicate ids or join the tab order', async (t) => {
  if (skipReason) return t.skip(skipReason);
  const { page, context } = await open();
  const result = await page.evaluate(() => ({
    sameId: document.querySelectorAll('#tick-link').length,
    copyLinks: [...document.querySelectorAll('#ticker [aria-hidden="true"] a')].map((a) => a.getAttribute('tabindex'))
  }));
  assert.equal(result.sameId, 1, 'ids stay unique');
  assert.ok(result.copyLinks.length > 0 && result.copyLinks.every((v) => v === '-1'), 'links in copies are not focusable');
  await context.close();
});
