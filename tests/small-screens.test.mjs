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
    // The repository's CDP fallback has no browser contexts, keyboard or focus: skip instead of failing.
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
  base = `http://127.0.0.1:${server.address().port}/atlas-patterns-demo.html`;
});

test.after(async () => {
  await browser?.close();
  server?.close();
});

async function open(viewport, options = {}) {
  const context = await browser.newContext({ viewport, ...options });
  const page = await context.newPage();
  const errors = [];
  page.on('pageerror', (e) => errors.push(e.message));
  await page.goto(base, { waitUntil: 'networkidle' });
  await page.waitForTimeout(500);
  const hasAnime = await page.evaluate(() => Boolean(window.__atlas?.anime));
  return { page, context, errors, hasAnime };
}

const scrollTo = (page, y) => page.evaluate((top) => window.scrollTo({ top, behavior: 'instant' }), y);

test('small screens: scenes play once at 15% on phones and tablet portrait, and scrub on desktop', async (t) => {
  if (skipReason) return t.skip(skipReason);
  for (const [name, viewport, expected] of [['phone', { width: 375, height: 667 }, 'play'], ['tablet portrait', { width: 768, height: 1024 }, 'play'], ['desktop', { width: 1440, height: 900 }, 'scrub']]) {
    const { page, context, errors, hasAnime } = await open(viewport);
    if (!hasAnime) { await context.close(); return t.skip('Anime.js CDN unreachable'); }
    assert.equal(await page.evaluate(() => document.documentElement.dataset.atlasMotion), expected, `${name} mode`);
    assert.deepEqual(errors, [], `${name} page errors`);
    if (expected === 'play') {
      const classes = await page.evaluate(() => [...document.querySelectorAll('[data-atlas-scene]')].map((s) => s.className));
      assert.ok(classes.every((c) => c.includes('is-play')), `${name}: every scene is playing, got ${classes.join(' | ')}`);
    }
    await context.close();
  }
});

test('small screens: a phone scene stays at its start pose until 15% is visible, then plays to the end', async (t) => {
  if (skipReason) return t.skip(skipReason);
  const { page, context, hasAnime } = await open({ width: 375, height: 667 });
  if (!hasAnime) { await context.close(); return t.skip('Anime.js CDN unreachable'); }
  const state = () => page.evaluate(() => {
    const sc = document.querySelector('[data-atlas-scene="pull-back"]');
    const scale = new DOMMatrix(getComputedStyle(sc.querySelector('.atlas-scene__backdrop img')).transform).a;
    const to = Number(getComputedStyle(sc.querySelector('.atlas-scene__caption--to')).opacity);
    return { scale: Number(scale.toFixed(2)), to: Number(to.toFixed(2)) };
  });
  const top = await page.evaluate(() => document.querySelector('[data-atlas-scene="pull-back"]').getBoundingClientRect().top + scrollY);
  const height = await page.evaluate(() => document.querySelector('[data-atlas-scene="pull-back"]').offsetHeight);
  const vh = 667;

  await scrollTo(page, top - vh + Math.round(vh * 0.08)); // 8% of the screen: below the 15% trigger
  await page.waitForTimeout(500);
  const early = await state();
  assert.ok(early.scale > 1.5 && early.to === 0, `before 15%: should hold the start pose, got ${JSON.stringify(early)}`);

  await scrollTo(page, top - vh + Math.round(vh * 0.3)); // comfortably past 15%
  await page.waitForTimeout(600);
  const mid = await state();
  assert.ok(mid.scale < early.scale, `after 15%: the zoom should be easing out, got ${JSON.stringify(mid)}`);
  await page.waitForTimeout(2200);
  const end = await state();
  assert.ok(end.scale <= 1.02 && end.to >= 0.98, `finished pose expected, got ${JSON.stringify(end)}`);
  assert.ok(height > 0);
  await context.close();
});

test('small screens: reduced motion fades only and shows scenes in their finished state', async (t) => {
  if (skipReason) return t.skip(skipReason);
  const { page, context, hasAnime } = await open({ width: 375, height: 667 }, { reducedMotion: 'reduce' });
  if (!hasAnime) { await context.close(); return t.skip('Anime.js CDN unreachable'); }
  assert.equal(await page.evaluate(() => document.documentElement.dataset.atlasMotion), 'soft');
  const rest = await page.evaluate(() => [...document.querySelectorAll('[data-atlas-scene]')].every((s) => s.classList.contains('is-rest')));
  assert.ok(rest, 'scenes show their rest composition');
  const scale = await page.evaluate(() => new DOMMatrix(getComputedStyle(document.querySelector('[data-atlas-scene="pull-back"] img')).transform).a);
  assert.equal(Number(scale.toFixed(2)), 1);
  await context.close();
});

test('small screens: cards swipe on phones, become 2 columns on tablet portrait and 3 on desktop', async (t) => {
  if (skipReason) return t.skip(skipReason);
  const columns = (page) => page.evaluate(() => getComputedStyle(document.querySelector('#cards .atlas-carousel__track')).gridTemplateColumns.split(' ').length);

  const phone = await open({ width: 375, height: 667 });
  const swipe = await phone.page.evaluate(() => {
    const track = document.querySelector('#cards .atlas-carousel__track');
    return { scrollable: track.scrollWidth > track.clientWidth + 8, dots: document.querySelectorAll('#cards .atlas-carousel__dot').length, controls: getComputedStyle(document.querySelector('#cards .atlas-carousel__controls')).display };
  });
  assert.ok(swipe.scrollable && swipe.dots === 3 && swipe.controls !== 'none', JSON.stringify(swipe));
  await phone.page.locator('#cards .atlas-carousel__btn').nth(1).click();
  await phone.page.waitForTimeout(700);
  const afterNext = await phone.page.evaluate(() => ({ left: document.querySelector('#cards .atlas-carousel__track').scrollLeft, current: [...document.querySelectorAll('#cards .atlas-carousel__dot')].findIndex((d) => d.getAttribute('aria-current') === 'true') }));
  assert.ok(afterNext.left > 100 && afterNext.current === 1, JSON.stringify(afterNext));
  await phone.page.locator('#cards .atlas-carousel__track').focus();
  await phone.page.keyboard.press('End');
  await phone.page.waitForTimeout(700);
  const atEnd = await phone.page.evaluate(() => ({ current: [...document.querySelectorAll('#cards .atlas-carousel__dot')].findIndex((d) => d.getAttribute('aria-current') === 'true'), nextDisabled: document.querySelectorAll('#cards .atlas-carousel__btn')[1].disabled }));
  assert.deepEqual(atEnd, { current: 2, nextDisabled: true });
  assert.equal(await phone.page.evaluate(() => document.documentElement.scrollWidth - innerWidth), 0, 'no horizontal page overflow');
  await phone.context.close();

  const tablet = await open({ width: 768, height: 1024 });
  assert.equal(await columns(tablet.page), 2);
  const tabletLayout = await tablet.page.evaluate(() => {
    const slides = [...document.querySelectorAll('#cards .atlas-carousel__slide')].map((s) => s.getBoundingClientRect());
    return { controls: getComputedStyle(document.querySelector('#cards .atlas-carousel__controls')).display, lastSpansRow: Math.abs(slides[2].width - (slides[1].right - slides[0].left)) < 2 };
  });
  assert.deepEqual(tabletLayout, { controls: 'none', lastSpansRow: true });
  await tablet.context.close();

  const desktop = await open({ width: 1440, height: 900 });
  assert.equal(await columns(desktop.page), 3);
  await desktop.context.close();
});

test('small screens: the bento mosaic is 2 columns below 1024px and 4 above, with no gaps or overflow', async (t) => {
  if (skipReason) return t.skip(skipReason);
  for (const [viewport, cols] of [[{ width: 375, height: 667 }, 2], [{ width: 768, height: 1024 }, 2], [{ width: 1440, height: 900 }, 4]]) {
    const { page, context } = await open(viewport);
    const layout = await page.evaluate(() => {
      const grid = document.querySelector('.atlas-bento');
      const g = grid.getBoundingClientRect();
      const items = [...grid.children].map((el) => el.getBoundingClientRect());
      return {
        cols: getComputedStyle(grid).gridTemplateColumns.split(' ').length,
        inside: items.every((r) => r.left >= g.left - 1 && r.right <= g.right + 1),
        overflow: document.documentElement.scrollWidth - innerWidth
      };
    });
    assert.equal(layout.cols, cols, `${viewport.width}px columns`);
    assert.ok(layout.inside && layout.overflow === 0, `${viewport.width}px: ${JSON.stringify(layout)}`);
    await context.close();
  }
});

test('small screens: a scene already 8% visible when the page loads still waits for 15%', async (t) => {
  if (skipReason) return t.skip(skipReason);
  const { page, context, hasAnime } = await open({ width: 375, height: 667 });
  if (!hasAnime) { await context.close(); return t.skip('Anime.js CDN unreachable'); }
  const top = await page.evaluate(() => document.querySelector('[data-atlas-scene="pull-back"]').getBoundingClientRect().top + scrollY);
  await scrollTo(page, top - 667 + Math.round(667 * 0.08));
  await page.waitForTimeout(300);
  await page.reload({ waitUntil: 'networkidle' }); // the browser restores the scroll position, so the sliver is visible at load
  await page.waitForTimeout(1500);
  const scale = await page.evaluate(() => new DOMMatrix(getComputedStyle(document.querySelector('[data-atlas-scene="pull-back"] .atlas-scene__backdrop img')).transform).a);
  assert.ok(scale > 1.5, `should still hold the start pose, scale ${scale}`);
  await context.close();
});

test('small screens: carousel dots meet the 44px target and previous always moves back', async (t) => {
  if (skipReason) return t.skip(skipReason);
  const phone = await open({ width: 375, height: 667 });
  const dot = await phone.page.evaluate(() => {
    const r = document.querySelector('#cards .atlas-carousel__dot').getBoundingClientRect();
    return { w: Math.round(r.width), h: Math.round(r.height) };
  });
  assert.ok(dot.w >= 44 && dot.h >= 44, JSON.stringify(dot));
  assert.equal(await phone.page.evaluate(() => document.querySelectorAll('#rail .atlas-carousel__dot').length), 0, 'six slides use a counter, not dots');
  await phone.context.close();

  // A carousel that shows several slides at once cannot align its last slides to the left edge:
  // stepping back from the end must still move.
  const desktop = await open({ width: 1440, height: 900 });
  const track = desktop.page.locator('#rail .atlas-carousel__track');
  const next = desktop.page.locator('#rail .atlas-carousel__btn').nth(1);
  const prev = desktop.page.locator('#rail .atlas-carousel__btn').nth(0);
  for (let i = 0; i < 8 && !(await next.isDisabled()); i++) { await next.click(); await desktop.page.waitForTimeout(450); }
  const atEnd = await track.evaluate((el) => el.scrollLeft);
  assert.ok(atEnd > 0);
  await prev.click();
  await desktop.page.waitForTimeout(600);
  const back = await track.evaluate((el) => el.scrollLeft);
  assert.ok(back < atEnd - 4, `previous should move back from the end: ${atEnd} -> ${back}`);
  await desktop.context.close();
});

test('small screens: carousels can be destroyed and initialised again', async (t) => {
  if (skipReason) return t.skip(skipReason);
  const { page, context } = await open({ width: 375, height: 667 });
  const result = await page.evaluate(async () => {
    const { initAtlasCarousels } = await import('./atlas-interact.mjs');
    // A fresh carousel that this test owns (the demo ones belong to initAtlasInteract()).
    const host = document.createElement('div');
    host.innerHTML = '<div class="atlas-carousel" data-carousel><ul class="atlas-carousel__track">' + [1, 2, 3].map((n) => '<li class="atlas-carousel__slide">' + n + '</li>').join('') + '</ul></div>';
    document.body.append(host);
    const el = host.firstElementChild;
    const dots = () => el.querySelectorAll('.atlas-carousel__dot').length;
    const first = initAtlasCarousels(host);
    const built = dots();
    first.destroy();
    const cleared = dots() + (el.dataset.carouselReady ? 1 : 0);
    const second = initAtlasCarousels(host);
    const rebuilt = dots();
    second.destroy();
    host.remove();
    return { built, cleared, rebuilt };
  });
  assert.deepEqual(result, { built: 3, cleared: 0, rebuilt: 3 });
  await context.close();
});
