#!/usr/bin/env node
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawn, spawnSync } from 'node:child_process';
import assert from 'node:assert/strict';
import { fileURLToPath } from 'node:url';
const __dirname = path.dirname(fileURLToPath(import.meta.url));

const outputIndex = process.argv.indexOf('--out');
const root = outputIndex >= 0 ? path.resolve(process.argv[outputIndex + 1]) : fs.mkdtempSync(path.join(os.tmpdir(), 'atlas-checker-regression-'));
fs.mkdirSync(root, { recursive: true });
const checker = path.join(__dirname, 'quick-check.mjs');
const good = fs.readFileSync(path.join(__dirname, 'fixtures/audit-good.html'), 'utf8');
const bad = good
  .replace('document.getElementById(\'fixture-nav\').hidden = !open;', '// Broken: ARIA changes without visible navigation.')
  .replace("document.getElementById(item.getAttribute('aria-controls')).hidden = !active;", '// Broken: selected state changes without visible panel.')
  .replace('<a data-primary href=', '<a hidden data-primary href=')
  .replace('</main>', '<section style="width:1800px"><h2 style="color:color(srgb 0.94 0.94 0.94)">Low contrast fixture</h2><img src="missing.png" width="200" height="100" alt="Intentionally broken image"></section></main>');
const paths = {};
const minimal = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>No smoke controls</title><link rel="icon" href="data:">${good.match(/<style>[\s\S]*?<\/style>/)[0]}</head><body><main><section data-hero><h1>No applicable smoke controls</h1><a data-primary href="#target">Visible primary action</a></section><section id="target">End</section></main></body></html>`;
const navGap = `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Nav and dead space</title><link rel="icon" href="data:"><style>body{margin:0;font:16px/1.5 sans-serif}header{display:flex;justify-content:space-between;align-items:center;padding:8px 16px}nav a{display:inline-block;min-height:44px;padding:10px}.cta{display:inline-block;min-height:44px;padding:10px}@media(max-width:820px){nav a{display:none}}section{padding:32px 16px}.gap{min-height:900px}</style></head><body><header><span>Brand</span><nav><a href="#a">One</a><a href="#b">Two</a><a href="#c">Three</a></nav><a class="cta" href="#contact">Book</a></header><main><section data-hero id="a"><h1>Nav and dead space</h1><a data-primary class="cta" href="#b">Action</a></section><section class="gap" id="b"><h2>Mostly empty</h2><p>Only a short paragraph sits at the top of a very tall section.</p></section><section id="c"><h2>End</h2></section></main></body></html>`;
// Separate mobile markup: desktop links hidden, a visible mobile nav reaches the same destinations.
const navDup = navGap
  .replace('</style>', '.m{display:none}@media(max-width:820px){.m{display:block}.m a{display:inline-block}}</style>')
  .replace('</header>', '<nav class="m" aria-label="Mobile"><a href="#a">One</a><a href="#b">Two</a><a href="#c">Three</a></nav></header>');
// An unrelated visible button must not mask the missing menu.
const navTheme = navGap.replace('<a class="cta" href="#contact">Book</a>', '<a class="cta" href="#contact">Book</a><button type="button" id="theme" style="min-height:44px">Theme</button>');
// A drawer parked off-canvas with a transform keeps a positive size; it must not count as reachable.
const navDrawer = navGap.replace('@media(max-width:820px){nav a{display:none}}', '@media(max-width:820px){nav{position:fixed;top:0;left:0;transform:translateX(-100%)}}');
// Four tall picture cards stacked in one column (should be a carousel or grid) and one picture left alone in its row.
const fixturePage = (body, css = '') => `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Small screens</title><link rel="icon" href="data:"><style>body{margin:0;font:16px/1.5 sans-serif}main{padding:16px}img{display:block;width:100%;height:100%;object-fit:cover;background:#999}${css}</style></head><body><main><section data-hero><h1>Small screens</h1></section>${body}</main></body></html>`;
const card = (n) => `<article class="c"><img alt="Card ${n}" src="data:image/gif;base64,R0lGODlhAQABAAAAACw="></article>`;
const stackBad = fixturePage(`<div class="col">${[1, 2, 3, 4].map(card).join('')}</div>`, '.col{display:grid;gap:16px}.c{height:420px}');
const stackGood = fixturePage(`<div class="atlas-carousel" data-carousel><div class="track">${[1, 2, 3, 4].map(card).join('')}</div></div>`, '.track{display:flex;gap:16px;overflow-x:auto}.c{flex:0 0 80%;height:420px}');
const halfBad = fixturePage('<div class="row"><figure class="f"><img alt="Lone picture" src="data:image/gif;base64,R0lGODlhAQABAAAAACw="></figure></div>', '.row{width:100%}.f{margin:0;width:62%;height:360px}');
// Stacked CTAs: ragged (different widths) vs equal-width stacking.
const ctaPage = (css) => `<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>CTA</title><link rel="icon" href="data:"><style>body{margin:0;font:16px/1.5 sans-serif}main{padding:16px}.btn{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:0 24px;border:1px solid #333}.row{display:flex;flex-direction:column;gap:12px}${css}</style></head><body><main><section data-hero><h1>CTA fixture</h1><div class="row"><a data-primary class="btn" href="#a">Hitung estimasi biaya</a><a class="btn" href="#b">Jadwalkan konsultasi</a></div></section></main></body></html>`;
const ctaRagged = ctaPage('.row{align-items:flex-start}.btn:last-child{padding:0 40px}');
const ctaEqual = ctaPage('.row{align-items:stretch}');
// Equal width but narrow and left-aligned: the stack does not fill the row.
const ctaNarrow = ctaPage('.row{align-items:flex-start}.btn{width:12rem}');
for (const [name, content] of [['good', good], ['bad', bad], ['read-only', good], ['no-controls', minimal], ['nav-gap', navGap], ['nav-dup', navDup], ['nav-theme', navTheme], ['nav-drawer', navDrawer], ['stack-bad', stackBad], ['stack-good', stackGood], ['half-bad', halfBad], ['cta-ragged', ctaRagged], ['cta-narrow', ctaNarrow], ['cta-equal', ctaEqual]]) {
  paths[name] = path.join(root, `${name}.html`);
  fs.writeFileSync(paths[name], content);
}

function audit(name, clickArgs = ['--click-test']) {
  const shots = path.join(root, name);
  return new Promise((resolve, reject) => {
    const child = spawn(process.execPath, [checker, paths[name], '--shots', shots, ...clickArgs, '--hero', '[data-hero]', '--hero-action', '[data-primary]'], { stdio: ['ignore', 'pipe', 'pipe'] });
    let log = '';
    child.stdout.on('data', chunk => { log += chunk; });
    child.stderr.on('data', chunk => { log += chunk; });
    child.on('error', reject);
    const timer = setTimeout(() => { child.kill(); reject(new Error(`${name} fixture audit timed out`)); }, 180000);
    child.on('close', status => {
      clearTimeout(timer);
      fs.writeFileSync(path.join(root, `${name}.log`), log);
      if (!fs.existsSync(path.join(shots, 'report.json'))) return reject(new Error(`${name} audit produced no report: ${log}`));
      resolve({ name, status, report: JSON.parse(fs.readFileSync(path.join(shots, 'report.json'), 'utf8')) });
    });
  });
}

const cases = [];
function verify(name, fn) { fn(); cases.push({ name, status: 'PASS' }); }
const [positive, negative, readOnly, noControls, navGapRun, navDupRun, navThemeRun, navDrawerRun, stackBadRun, stackGoodRun, halfBadRun, ctaRaggedRun, ctaNarrowRun, ctaEqualRun] = await Promise.all([audit('good'), audit('bad'), audit('read-only', []), audit('no-controls'), audit('nav-gap', []), audit('nav-dup', []), audit('nav-theme', []), audit('nav-drawer', []), audit('stack-bad', []), audit('stack-good', []), audit('half-bad', []), audit('cta-ragged', []), audit('cta-narrow', []), audit('cta-equal', [])]);
const phoneWarns = (run, prefix) => run.report.results.filter(r => r.viewport.width <= 540).flatMap(r => r.warns).filter(w => w.startsWith(prefix));
const mobileNavFails = (run) => run.report.results.filter(r => r.viewport.width <= 820).flatMap(r => r.fails).filter(f => f.startsWith('mobile-nav-missing:'));
verify('Known-good page exits zero with no failures', () => { assert.equal(positive.status, 0); assert.equal(positive.report.totalFails, 0); });
verify('Short phone viewports are actually present', () => {
  for (const height of [568, 667]) assert.ok(positive.report.results.some(result => result.viewport.height === height));
});
verify('Actual primary action is nonzero, visible and within each phone', () => {
  for (const result of positive.report.results.filter(result => result.viewport.width <= 420)) {
    assert.ok(result.metrics.hero.actionVisible);
    assert.ok(result.metrics.hero.actionHeight >= 44);
    assert.ok(result.metrics.hero.actionBottom > 0 && result.metrics.hero.actionBottom <= result.viewport.height + 1);
  }
});
verify('Menu and tab checks both execute and inspect visible panels', () => {
  assert.equal(positive.report.interactive.status, 'passed');
  assert.ok(positive.report.interactive.checks.some(check => check.kind === 'menu' && check.panelVisible));
  assert.ok(positive.report.interactive.checks.some(check => check.kind === 'tab' && check.panelVisible));
});
verify('Known-bad page exits one', () => assert.equal(negative.status, 1));
const failures = negative.report.results.flatMap(result => result.fails);
for (const prefix of ['overflow:', 'contrast:', 'broken-images:', 'hero-visibility:', 'hero-action-fit:']) {
  verify(`Rejects ${prefix}`, () => assert.ok(failures.some(failure => failure.startsWith(prefix))));
}
verify('HTTP missing resource is recorded', () => assert.ok(negative.report.resources.some(resource => resource.includes('404'))));
verify('ARIA-only menu/tab changes do not pass visible behavior', () => {
  assert.equal(negative.report.interactive.status, 'failed');
  assert.equal(negative.report.interactive.issues.length, 2);
});
verify('Default audit performs no clicks and reports skipped', () => {
  assert.equal(readOnly.status, 0);
  assert.equal(readOnly.report.interactive.status, 'skipped');
  assert.equal(readOnly.report.interactive.checks.length, 0);
});
verify('Opt-in smoke with zero applicable controls is skipped, not passed', () => {
  assert.equal(noControls.status, 0);
  assert.equal(noControls.report.interactive.status, 'skipped');
  assert.equal(noControls.report.interactive.checks.length, 0);
});
verify('Hidden mobile navigation links without a menu control are rejected', () => {
  const mobileFails = navGapRun.report.results.filter(r => r.viewport.width <= 820).flatMap(r => r.fails);
  assert.ok(mobileFails.some(f => f.startsWith('mobile-nav-missing:')));
  assert.equal(positive.report.results.flatMap(r => r.fails).filter(f => f.startsWith('mobile-nav-missing:')).length, 0);
});
verify('Separate visible mobile navigation reaching the same destinations passes', () => assert.equal(mobileNavFails(navDupRun).length, 0));
const warnsAt = (run, min, max, prefix) => run.report.results.filter((r) => r.viewport.width >= min && r.viewport.width <= max).flatMap((r) => r.warns).filter((w) => w.startsWith(prefix));
verify('Tablet portrait viewports (600 and 768) are audited', () => {
  for (const width of [600, 768]) assert.ok(positive.report.results.some((r) => r.viewport.width === width), `missing ${width}px`);
});
verify('A long single column of picture cards is flagged on phones and tablets', () => {
  assert.ok(warnsAt(stackBadRun, 0, 820, 'mobile-long-stack:').length > 0);
  assert.equal(warnsAt(stackBadRun, 1200, 4000, 'mobile-long-stack:').length, 0, 'desktop is not flagged');
});
verify('The same cards inside a carousel are not flagged', () => assert.equal(warnsAt(stackGoodRun, 0, 820, 'mobile-long-stack:').length, 0));
verify('A picture alone in part of its row is flagged on tablet portrait only', () => {
  assert.ok(warnsAt(halfBadRun, 600, 1023, 'half-empty-row:').length > 0);
  assert.equal(warnsAt(halfBadRun, 0, 599, 'half-empty-row:').length + warnsAt(halfBadRun, 1024, 4000, 'half-empty-row:').length, 0);
});
verify('The known-good page has neither small-screen warning', () => {
  assert.equal(positive.report.results.flatMap((r) => r.warns).filter((w) => /^(mobile-long-stack|half-empty-row):/.test(w)).length, 0);
});
verify('An off-canvas drawer without a menu control does not count as reachable navigation', () => assert.ok(mobileNavFails(navDrawerRun).length > 0));
verify('Stacked buttons of different widths are flagged on phones', () => assert.ok(phoneWarns(ctaRaggedRun, 'cta-width-mismatch:').length > 0));
verify('Equal-width stacked buttons that do not fill the row are flagged', () => assert.ok(phoneWarns(ctaNarrowRun, 'cta-not-full-width:').length > 0));
verify('Full-width equal stacked buttons pass', () => {
  assert.equal(phoneWarns(ctaEqualRun, 'cta-width-mismatch:').length, 0);
  assert.equal(phoneWarns(ctaEqualRun, 'cta-not-full-width:').length, 0);
});
verify('An unrelated visible button does not mask a missing mobile menu', () => assert.ok(mobileNavFails(navThemeRun).length > 0));
verify('Tall section with empty trailing space is flagged on desktop only', () => {
  const desktopWarns = navGapRun.report.results.filter(r => r.viewport.width >= 1200).flatMap(r => r.warns);
  assert.ok(desktopWarns.some(w => w.startsWith('dead-space:')));
  assert.equal(navGapRun.report.results.filter(r => r.viewport.width < 1200).flatMap(r => r.warns).filter(w => w.startsWith('dead-space:')).length, 0);
});
for (const args of [['--unknown'],['--shots'], ['page.html', '--hero', '#hero']]) {
  verify(`Invalid usage rejects ${args.join(' ')}`, () => assert.equal(spawnSync(process.execPath, [checker, ...args], { encoding: 'utf8' }).status, 2));
}
verify('Help exits successfully', () => assert.equal(spawnSync(process.execPath, [checker, '--help'], { encoding: 'utf8' }).status, 0));
fs.writeFileSync(path.join(root, 'self-test-report.json'), JSON.stringify({ cases, total: cases.length, positive: positive.report, negative: negative.report, readOnly: readOnly.report, noControls: noControls.report, navGap: navGapRun.report, ctaRagged: ctaRaggedRun.report, limitations: 'Controlled regression fixtures verify selected mechanics, not the visual quality or complete accessibility of arbitrary sites.' }, null, 2));
console.log(`PASS ${cases.length} checker regression cases. Evidence: ${root}`);
