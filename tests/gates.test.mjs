import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'atlas-gates-test-'));
const runNode = (scriptRel, args = [], cwd = tmp) =>
  spawnSync(process.execPath, [path.join(root, scriptRel), ...args], { cwd, encoding: 'utf8' });

const validTokensCss = fs.readFileSync(path.join(root, 'templates/design-tokens.css'), 'utf8');

const validFullBriefId = `# Design brief

## Pengunjung dan tugas utamanya

Pengunjung dari peta lokal di layar 375x667 memeriksa jam buka kedai kopi dan kisaran harga menu dalam dua langkah.

## Konten nyata

Daftar menu seduh manual dan jam buka Jl. Taman Cibeunying Selatan No. 14 Bandung.

## Rencana gambar

Menggunakan pelat spesimen editorial dengan atribut data-photo-slot="bar-16x9" rasio 16:9 dan meminta foto asli ke pengguna di pesan akhir.

## Tiga alternatif komposisi

### Alternatif 1

Full-bleed cover dengan bar jam buka di bagian atas dan daftar menu dua kolom.

### Alternatif 2

Kolofon tipis di atas dengan pelat pameran asimetris 16:9 dan catatan origin di bawah.

### Alternatif 3

Satu kolom editorial 68ch dengan tabel harga ringkas dan peta lokasi di kaki halaman.

## Pilihan akhir dan alasan

Memilih Alternatif 1 dengan arketipe editorial dan Anime.js v4 durasi masuk 420ms serta dukungan reduced-motion.

## Hal yang sengaja ditolak dan kenapa

Menolak kartu workbench filter SaaS dan siluet SVG bukit+matahari karena tidak sesuai untuk kedai kopi.

## Rencana verifikasi

Menjalankan run-gates.mjs --mode full --strict dan memeriksa tangkapan layar 1440x900 dan 375x667.
`;

test('deterministic quality gates', async t => {
  await t.test('check-brief validates full, visual-domain, light, and invalid briefs', () => {
    const dir = path.join(tmp, 'briefs');
    fs.mkdirSync(dir);

    const missing = runNode('scripts/check-brief.mjs', [path.join(dir, 'absent.md')]);
    assert.equal(missing.status, 1);

    const fullPath = path.join(dir, 'full.md');
    fs.writeFileSync(fullPath, validFullBriefId);
    assert.equal(runNode('scripts/check-brief.mjs', [fullPath]).status, 0);

    const dupAltPath = path.join(dir, 'dup-alt.md');
    fs.writeFileSync(dupAltPath, validFullBriefId.replace('### Alternatif 2', '### Alternatif 1'));
    assert.equal(runNode('scripts/check-brief.mjs', [dupAltPath]).status, 1);

    const noImagePlanPath = path.join(dir, 'no-img-plan.md');
    fs.writeFileSync(
      noImagePlanPath,
      validFullBriefId.replace(/## Rencana gambar[\s\S]*?(?=## Tiga alternatif)/, '').replace('kedai kopi', 'restoran')
    );
    assert.equal(runNode('scripts/check-brief.mjs', [noImagePlanPath]).status, 1);

    const lightPath = path.join(dir, 'light.md');
    fs.writeFileSync(
      lightPath,
      '<!-- atlas-brief: light -->\n## Pengunjung dan tugas utamanya\nMelihat dokumentasi API.\n## Konten nyata\nEndpoint GET /v1/health.\n## Pilihan akhir dan alasan\nPortal 3-panel sederhana.\n## Rencana verifikasi\nJalankan run-gates.mjs --mode light.\n'
    );
    assert.equal(runNode('scripts/check-brief.mjs', [lightPath]).status, 0);
  });

  await t.test('check-tokens blocks raw hex/scale values and passes tokenized CSS', () => {
    const badDir = path.join(tmp, 'tokens-bad');
    fs.mkdirSync(badDir);
    fs.writeFileSync(path.join(badDir, 'design-tokens.css'), validTokensCss);
    fs.writeFileSync(
      path.join(badDir, 'index.html'),
      '<!doctype html><html><body><div style="color:#ff0000;padding:17px"><a href="#top">Top</a></div></body></html>'
    );
    const badRes = runNode('scripts/check-tokens.mjs', [badDir, '--tokens', path.join(badDir, 'design-tokens.css')]);
    assert.equal(badRes.status, 1);
    assert.match(badRes.stderr + badRes.stdout, /raw color|raw scale/i);

    const goodDir = path.join(tmp, 'tokens-good');
    fs.mkdirSync(goodDir);
    fs.writeFileSync(path.join(goodDir, 'design-tokens.css'), validTokensCss);
    fs.writeFileSync(
      path.join(goodDir, 'styles.css'),
      'body{background:var(--color-bg);color:var(--color-text);padding:var(--space-4);margin:0 auto;border-radius:50%}'
    );
    fs.writeFileSync(path.join(goodDir, 'index.html'), '<!doctype html><html><body><a href="#sec">Go</a></body></html>');
    const goodRes = runNode('scripts/check-tokens.mjs', [goodDir, '--tokens', path.join(goodDir, 'design-tokens.css')]);
    assert.equal(goodRes.status, 0, goodRes.stderr);
  });

  await t.test('check-motion-v4 blocks v3 syntax and static opacity:0 traps', () => {
    const badDir = path.join(tmp, 'motion-bad');
    fs.mkdirSync(badDir);
    fs.writeFileSync(
      path.join(badDir, 'app.js'),
      "import anime from 'animejs';\nanime({ targets: '.card', easing: 'easeOutExpo' });\n"
    );
    fs.writeFileSync(path.join(badDir, 'styles.css'), '[data-hero-title] { opacity: 0; }\n');
    const badRes = runNode('scripts/check-motion-v4.mjs', [badDir]);
    assert.equal(badRes.status, 1);
    assert.match(badRes.stdout, /anime-v3-default-import/);

    const goodDir = path.join(tmp, 'motion-good');
    fs.mkdirSync(goodDir);
    fs.writeFileSync(
      path.join(goodDir, 'app.js'),
      "import { animate, createScope } from 'animejs';\nconst scope = createScope({ root: document.body, mediaQueries: { reduce: '(prefers-reduced-motion: reduce)' } }).add(() => {\n  animate('.card', { opacity: [0, 1], ease: 'outQuart', duration: 420 });\n});\nscope.revert();\n"
    );
    const goodRes = runNode('scripts/check-motion-v4.mjs', [goodDir]);
    assert.equal(goodRes.status, 0, goodRes.stdout + goodRes.stderr);
  });

  await t.test('check-visual-proof and slop-scan catch wireframe SVG, debug switchers, and backticks', () => {
    const badDir = path.join(tmp, 'visual-bad');
    fs.mkdirSync(badDir);
    fs.writeFileSync(
      path.join(badDir, 'index.html'),
      `<!doctype html><html><body><main>
        <p>Use \`npm run dev\` here.</p>
        <select><option>Populated</option><option>Empty</option></select>
        <svg viewBox="0 0 200 120"><circle cx="50" cy="40" r="15"/><path d="M0 100 Q50 40 100 100 Z"/></svg>
      </main></body></html>`
    );
    const vpRes = runNode('scripts/check-visual-proof.mjs', [badDir]);
    assert.equal(vpRes.status, 1);
    assert.match(vpRes.stdout, /generic-hill-sun-svg/);
    assert.match(vpRes.stdout, /leaked-debug-state-switcher/);
    assert.match(vpRes.stdout, /leaked-markdown-backticks/);

    const slopRes = runNode('skills/atlas-checker/scripts/slop-scan.mjs', [badDir]);
    assert.equal(slopRes.status, 1);
    assert.match(slopRes.stdout, /leaked-debug-state-switcher/);

    const optOutDir = path.join(tmp, 'visual-optout');
    fs.mkdirSync(optOutDir);
    fs.writeFileSync(
      path.join(optOutDir, 'index.html'),
      '<!doctype html><html><body><!-- atlas-proof: not-applicable --><main><h1>API Reference</h1><p>Endpoint documentation.</p></main></body></html>'
    );
    assert.equal(runNode('scripts/check-visual-proof.mjs', [optOutDir, '--strict']).status, 0);
  });

  await t.test('deal-direction uses word-boundary matching and selects distinct directions', () => {
    const dir = path.join(tmp, 'direction');
    fs.mkdirSync(dir);
    const r1 = runNode('scripts/deal-direction.mjs', ['--prompt', 'restoran kopi nusantara ramai pengunjung', '--project', dir]);
    assert.equal(r1.status, 0, r1.stderr);
    const d1 = JSON.parse(r1.stdout);
    assert.ok(d1.dealtPrimaryDirection?.id);

    const r2 = runNode('scripts/deal-direction.mjs', ['--prompt', 'dashboard keuangan operasional', '--project', dir]);
    assert.equal(r2.status, 0, r2.stderr);
    const d2 = JSON.parse(r2.stdout);
    assert.notEqual(d1.dealtPrimaryDirection.id, d2.dealtPrimaryDirection.id);
  });

  await t.test('run-gates runs full --strict and light modes end-to-end', () => {
    const proj = path.join(tmp, 'e2e-project');
    fs.mkdirSync(proj);
    fs.writeFileSync(path.join(proj, 'design-brief.md'), validFullBriefId);
    fs.writeFileSync(path.join(proj, 'design-tokens.css'), validTokensCss);
    fs.writeFileSync(
      path.join(proj, 'styles.css'),
      'body{background:var(--color-bg);color:var(--color-text);font-family:var(--font-sans)}section{background:var(--color-surface)}.card{background:var(--color-surface-elevated)}'
    );
    fs.writeFileSync(
      path.join(proj, 'index.html'),
      '<!doctype html><html><head><link rel="stylesheet" href="design-tokens.css"><link rel="stylesheet" href="styles.css"></head><body><main><section><figure data-photo-slot="bar-16x9" data-atlas-proof="editorial-plate"><div role="img" aria-label="Meja seduh pagi hari"><span>PLATE 01</span></div><figcaption>Ruang seduh utama Bandung.</figcaption></figure><button class="btn-primary" type="button">Lihat Menu</button></section></main></body></html>'
    );

    const fullPass = runNode('scripts/run-gates.mjs', [proj, '--mode', 'full', '--strict']);
    assert.equal(fullPass.status, 0, fullPass.stdout + fullPass.stderr);
    assert.equal(JSON.parse(fullPass.stdout).overall, 'PASS');

    fs.unlinkSync(path.join(proj, 'design-brief.md'));
    const lightPass = runNode('scripts/run-gates.mjs', [proj, '--mode', 'light']);
    assert.equal(lightPass.status, 0, lightPass.stdout + lightPass.stderr);
    assert.equal(JSON.parse(lightPass.stdout).overall, 'PASS');
  });
});
