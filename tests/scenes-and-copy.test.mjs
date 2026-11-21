import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath, pathToFileURL } from 'node:url';

const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const run = (script, args) => spawnSync(process.execPath, [path.join(root, script), ...args], { encoding: 'utf8' });
const catalog = JSON.parse(fs.readFileSync(path.join(root, 'templates/scene-catalog.json'), 'utf8'));

test('scene catalog and engine list the same scenes with the same weight', async () => {
  const engine = await import(pathToFileURL(path.join(root, 'templates/atlas-scenes.mjs')).href);
  const fromCatalog = Object.fromEntries(catalog.scenes.map((s) => [s.id, s.mode]));
  assert.deepEqual(engine.ATLAS_SCENE_MODES, fromCatalog);
  assert.equal(catalog.scenes.length, 10);
});

test('every scene has a demo, a guide section and styles', () => {
  const demo = fs.readFileSync(path.join(root, 'templates/atlas-scenes-demo.html'), 'utf8');
  const guide = fs.readFileSync(path.join(root, 'references/scenes.md'), 'utf8');
  const css = fs.readFileSync(path.join(root, 'templates/atlas-scenes.css'), 'utf8');
  for (const scene of catalog.scenes) {
    assert.ok(demo.includes(`data-atlas-scene="${scene.id}"`), `demo missing ${scene.id}`);
    assert.ok(new RegExp(`^###\\s+${scene.id}\\b`, 'm').test(guide), `guide missing ${scene.id}`);
    for (const field of ['look', 'needs', 'never', 'rest', 'fits']) assert.ok(scene[field]?.length, `${scene.id} lacks ${field}`);
  }
  assert.ok(css.includes('.atlas-scene__compare') && css.includes('.atlas-scene__track') && css.includes('.atlas-drift__row'));
});

test('deal-scene: fits the subject, respects budgets and avoids repeats', () => {
  const deal = (prompt, extra = []) => JSON.parse(run('scripts/deal-scene.mjs', ['--prompt', prompt, ...extra]).stdout);
  const villa = deal('Studio arsitektur villa dan restorasi bangunan');
  assert.ok(['split-wipe', 'pull-back', 'window-reveal', 'horizontal-rail'].includes(villa.heavy.id), villa.heavy.id);
  assert.ok(villa.light.length <= 2);
  assert.equal(new Set(villa.light.map((l) => catalog.scenes.find((s) => s.id === l.id).family)).size, villa.light.length, 'one light scene per family');

  const saas = deal('Aplikasi SaaS dashboard untuk developer');
  assert.equal(saas.heavy, null, 'software brief with no photo story gets no heavy scene');

  const docs = deal('Dokumentasi API dan kebijakan hukum');
  assert.equal(docs.heavy, null);

  const again = deal('Studio arsitektur villa dan restorasi bangunan');
  assert.deepEqual(again, villa, 'same prompt and seed is deterministic');
  const avoided = deal('Studio arsitektur villa dan restorasi bangunan', ['--avoid', villa.heavy.id]);
  assert.notEqual(avoided.heavy?.id, villa.heavy.id);
});

test('deal-scene: --write records history and the next run avoids it', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'atlas-deal-'));
  const prompt = 'Fotografer pernikahan portfolio galeri';
  const first = JSON.parse(run('scripts/deal-scene.mjs', ['--prompt', prompt, '--project', dir, '--write']).stdout);
  assert.ok(fs.existsSync(path.join(dir, '.atlas-scenes.json')));
  const second = JSON.parse(run('scripts/deal-scene.mjs', ['--prompt', prompt, '--project', dir]).stdout);
  assert.notEqual(second.heavy.id, first.heavy.id);
});

const page = (body, head = '') => `<!doctype html><html lang="en"><head><meta charset="utf-8"><title>t</title>${head}</head><body><main>${body}</main></body></html>`;
const copyRun = (html, extra = []) => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'atlas-copy-'));
  fs.writeFileSync(path.join(dir, 'index.html'), html);
  const result = run('scripts/check-copy.mjs', [dir, '--json', ...extra]);
  return { status: result.status, report: JSON.parse(result.stdout) };
};
const ids = ({ report }) => report.files.flatMap((f) => f.findings.map((x) => x.id));
const words = (n) => Array.from({ length: n }, (_, i) => `word${i}`).join(' ');

test('check-copy: a tight first screen with a concrete fact passes', () => {
  const result = copyRun(page('<section><h1>Cool houses of earth and teak</h1><p>Villas and pavilions in Ubud, built in 14 weeks.</p><a class="btn" href="#a">Book a site visit</a></section>'));
  assert.equal(result.status, 0);
  assert.deepEqual(ids(result), []);
});

test('check-copy: vague buttons fail, even on long-form pages', () => {
  const result = copyRun(page('<!-- atlas-copy: long-form --><section><h1>Docs for the API</h1><a class="btn" href="#a">Learn more</a><a class="btn" href="#b">Selengkapnya</a></section>'));
  assert.equal(result.status, 1);
  assert.equal(ids(result).filter((id) => id === 'copy-cta-vague').length, 2);
});

test('check-copy: an over-long headline, supporting line and paragraph are caught', () => {
  const result = copyRun(page(`<section><h1>${words(20)}</h1><p>${words(50)}</p><a class="btn" href="#a">Book now</a><p>${words(90)}</p></section>`));
  assert.equal(result.status, 1);
  for (const id of ['copy-h1-long', 'copy-lede-long', 'copy-paragraph-long']) assert.ok(ids(result).includes(id), id);
});

test('check-copy: long-form opt-out skips length rules; --strict makes warnings fail', () => {
  const long = page(`<!-- atlas-copy: long-form --><section><h1>Privacy policy</h1><p>${words(120)}</p></section>`);
  assert.deepEqual(ids(copyRun(long)).filter((id) => id.includes('paragraph') || id.includes('section') || id.includes('page')), []);
  const warnOnly = page(`<section><h1>${words(11)} Ubud</h1><a class="btn" href="#a">Book a visit</a></section>`);
  assert.equal(copyRun(warnOnly).status, 0);
  assert.equal(copyRun(warnOnly, ['--strict']).status, 1);
});

test('check-brief: Signature idea is optional but must name a real scene', () => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'atlas-brief-'));
  const brief = (sig) => `<!-- atlas-brief: light -->\n## Visitor and primary task\nA visitor on a phone wants to book a visit.\n## Real content\nVerified studio facts and photographs of finished work.\n${sig}## Final choice and rationale\nA single column that leads with the work.\n## Verification plan\nRun the gates and inspect screenshots.\n`;
  const file = path.join(dir, 'brief.md');
  fs.writeFileSync(file, brief(''));
  assert.equal(run('scripts/check-brief.mjs', [file]).status, 0);
  fs.writeFileSync(file, brief('## Signature idea\nTruth: joints. Move: detail pulls back. scene: pull-back\n'));
  assert.equal(run('scripts/check-brief.mjs', [file]).status, 0);
  fs.writeFileSync(file, brief('## Signature idea\nTruth: joints. Move: detail pulls back. scene: sparkle-burst\n'));
  const bad = run('scripts/check-brief.mjs', [file]);
  assert.equal(bad.status, 1);
  assert.match(bad.stderr, /unknown scene/);
});

test('deal-scene: an avoided scene is never returned, even when it is the only fit', () => {
  const out = JSON.parse(run('scripts/deal-scene.mjs', ['--prompt', 'restoration', '--avoid', 'split-wipe']).stdout);
  assert.notEqual(out.heavy?.id, 'split-wipe');
  const light = JSON.parse(run('scripts/deal-scene.mjs', ['--prompt', 'Dokumentasi API', '--avoid', 'word-light,parallax-depth,step-assemble,drift-type']).stdout);
  assert.deepEqual(light.light, []);
});

test('check-copy: long-form pages skip first-screen length rules; a div hero is bounded to itself', () => {
  const long = copyRun(page(`<!-- atlas-copy: long-form --><section><h1>Privacy policy</h1><p>${words(100)}</p></section>`));
  assert.equal(long.status, 0);
  assert.deepEqual(ids(long), []);
  const section = (n) => `<section><h2>Part ${n}</h2><p>${words(40)}</p></section>`;
  const divHero = copyRun(page(`<div class="hero"><h1>Cool houses of earth, Ubud</h1><p>Built in 14 weeks.</p><a class="btn" href="#a">Book a visit</a></div>${section(1)}${section(2)}${section(3)}`));
  assert.ok(!ids(divHero).includes('copy-first-screen-long'), ids(divHero).join(','));
  assert.equal(divHero.status, 0);
});
