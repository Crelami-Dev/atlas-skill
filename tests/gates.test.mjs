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

const validFullBriefEn = `# Design brief

## Visitor and primary task

Local map visitors on a 375x667 phone check coffee shop opening hours and menu prices within two taps.

## Real content

Manual brew menu list and opening hours at 14 South Cibeunying Park St, Bandung.

## Image plan

Use layered editorial specimen plates marked silently via data-photo-slot="bar-16x9" (16:9 ratio) and request real photos in the closing message.

## Three composition alternatives

### Alternative 1

Full-bleed architectural cover with docked opening-hours bar and two-column print menu ledger.

### Alternative 2

Thin top colophon with asymmetric 16:9 exhibition plates and origin table below.

### Alternative 3

Single 68ch editorial column with compact tariff table and venue map in the footer.

## Final choice and rationale

Select Alternative 1 with editorial typography and Anime.js v4 420ms entrance motion supporting reduced-motion.

## Deliberately rejected and why

Reject SaaS search/filter workbench cards and generic hill+sun SVGs because they do not suit a specialty coffee bar.

## Verification plan

Run run-gates.mjs --mode full --strict and inspect 1440x900 and 375x667 screenshots.
`;

test('deterministic quality gates', async t => {
  await t.test('check-brief validates full, visual-domain, light, and invalid briefs', () => {
    const dir = path.join(tmp, 'briefs');
    fs.mkdirSync(dir);

    const missing = runNode('scripts/check-brief.mjs', [path.join(dir, 'absent.md')]);
    assert.equal(missing.status, 1);

    const fullPath = path.join(dir, 'full.md');
    fs.writeFileSync(fullPath, validFullBriefEn);
    assert.equal(runNode('scripts/check-brief.mjs', [fullPath]).status, 0);

    const dupAltPath = path.join(dir, 'dup-alt.md');
    fs.writeFileSync(dupAltPath, validFullBriefEn.replace('### Alternative 2', '### Alternative 1'));
    assert.equal(runNode('scripts/check-brief.mjs', [dupAltPath]).status, 1);

    const noImagePlanPath = path.join(dir, 'no-img-plan.md');
    fs.writeFileSync(
      noImagePlanPath,
      validFullBriefEn.replace(/## Image plan[\s\S]*?(?=## Three composition)/, '').replace('coffee shop', 'restaurant')
    );
    assert.equal(runNode('scripts/check-brief.mjs', [noImagePlanPath]).status, 1);

    const lightPath = path.join(dir, 'light.md');
    fs.writeFileSync(
      lightPath,
      '<!-- atlas-brief: light -->\n## Visitor and primary task\nRead API documentation.\n## Real content\nGET /v1/health endpoint.\n## Final choice and rationale\nClean 3-pane docs portal.\n## Verification plan\nRun run-gates.mjs --mode light.\n'
    );
    assert.equal(runNode('scripts/check-brief.mjs', [lightPath]).status, 0);

    // Confirm legacy Indonesian headings still remain compatible
    const lightIdPath = path.join(dir, 'light-id.md');
    fs.writeFileSync(
      lightIdPath,
      '<!-- atlas-brief: light -->\n## Pengunjung dan tugas utamanya\nMelihat dokumentasi API.\n## Konten nyata\nEndpoint GET /v1/health.\n## Pilihan akhir dan alasan\nPortal 3-panel sederhana.\n## Rencana verifikasi\nJalankan run-gates.mjs --mode light.\n'
    );
    assert.equal(runNode('scripts/check-brief.mjs', [lightIdPath]).status, 0);
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

    // Verify crude-floorplan-svg (rect tables + circle stools without gradients/bezier curves) is blocked
    const floorplanDir = path.join(tmp, 'visual-floorplan');
    fs.mkdirSync(floorplanDir);
    fs.writeFileSync(
      path.join(floorplanDir, 'index.html'),
      `<!doctype html><html><body><main>
        <svg viewBox="0 0 640 240">
          <rect x="40" y="96" width="380" height="44" rx="4" />
          <circle cx="96" cy="168" r="12" /><circle cx="164" cy="168" r="12" /><circle cx="232" cy="168" r="12" /><circle cx="300" cy="168" r="12" />
          <rect x="468" y="64" width="110" height="110" rx="55" />
        </svg>
      </main></body></html>`
    );
    const fpRes = runNode('scripts/check-visual-proof.mjs', [floorplanDir]);
    assert.equal(fpRes.status, 1);
    assert.match(fpRes.stdout, /crude-floorplan-svg/);

    // Verify fetch-photos.mjs --offline exits 0 cleanly and writes credits.json
    const photoOut = path.join(tmp, 'photos-offline');
    const fpOffline = runNode('scripts/fetch-photos.mjs', ['--query', 'pour over coffee|sourdough bread', '--out', photoOut, '--offline']);
    assert.equal(fpOffline.status, 0, fpOffline.stderr);
    assert.ok(fs.existsSync(path.join(photoOut, 'credits.json')));
  });

  await t.test('deal-direction uses word-boundary matching and selects distinct directions', () => {
    const dir = path.join(tmp, 'direction');
    fs.mkdirSync(dir);
    const r1 = runNode('scripts/deal-direction.mjs', ['--prompt', 'specialty coffee shop roastery & sourdough bakery', '--project', dir]);
    assert.equal(r1.status, 0, r1.stderr);
    const d1 = JSON.parse(r1.stdout);
    assert.ok(d1.dealtPrimaryDirection?.id);

    const r2 = runNode('scripts/deal-direction.mjs', ['--prompt', 'operational finance dashboard', '--project', dir]);
    assert.equal(r2.status, 0, r2.stderr);
    const d2 = JSON.parse(r2.stdout);
    assert.notEqual(d1.dealtPrimaryDirection.id, d2.dealtPrimaryDirection.id);
  });

  await t.test('run-gates runs full --strict and light modes end-to-end', () => {
    const proj = path.join(tmp, 'e2e-project');
    fs.mkdirSync(proj);
    fs.writeFileSync(path.join(proj, 'design-brief.md'), validFullBriefEn);
    fs.writeFileSync(path.join(proj, 'design-tokens.css'), validTokensCss);
    fs.writeFileSync(
      path.join(proj, 'styles.css'),
      'body{background:var(--color-bg);color:var(--color-text);font-family:var(--font-sans)}section{background:var(--color-surface)}.card{background:var(--color-surface-elevated)}'
    );
    fs.writeFileSync(
      path.join(proj, 'index.html'),
      '<!doctype html><html><head><link rel="stylesheet" href="design-tokens.css"><link rel="stylesheet" href="styles.css"></head><body><main><section><figure data-photo-slot="bar-16x9" data-atlas-proof="editorial-plate"><div role="img" aria-label="Morning pour-over counter"><span>PLATE 01</span></div><figcaption>Main brew bar Bandung.</figcaption></figure><button class="btn-primary" type="button">View Menu</button></section></main></body></html>'
    );

    const fullPass = runNode('scripts/run-gates.mjs', [proj, '--mode', 'full', '--strict']);
    assert.equal(fullPass.status, 0, fullPass.stdout + fullPass.stderr);
    assert.equal(JSON.parse(fullPass.stdout).overall, 'PASS');

    fs.unlinkSync(path.join(proj, 'design-brief.md'));
    const lightPass = runNode('scripts/run-gates.mjs', [proj, '--mode', 'light']);
    assert.equal(lightPass.status, 0, lightPass.stdout + lightPass.stderr);
    assert.equal(JSON.parse(lightPass.stdout).overall, 'PASS');
  });

  await t.test('2 proportional + 1 monospace font system passes tokens and slop-scan while 3 proportional fonts fail', () => {
    const dir = path.join(tmp, 'fonts-3');
    fs.mkdirSync(dir);
    const deal = runNode('scripts/deal-direction.mjs', ['--prompt', 'specialty coffee restaurant', '--project', dir, '--write-tokens']);
    assert.equal(deal.status, 0, deal.stderr);
    const generatedTokens = fs.readFileSync(path.join(dir, 'design-tokens.css'), 'utf8');
    assert.match(generatedTokens, /--font-display:/);
    assert.match(generatedTokens, /--font-sans:/);
    assert.match(generatedTokens, /--font-mono:/);

    fs.writeFileSync(
      path.join(dir, 'styles.css'),
      'h1{font-family:var(--font-display)}body{font-family:var(--font-sans)}code{font-family:var(--font-mono)}'
    );
    fs.writeFileSync(path.join(dir, 'index.html'), '<!doctype html><html><body><h1>Title</h1><code>v7.0</code></body></html>');
    assert.equal(runNode('scripts/check-tokens.mjs', [dir, '--tokens', path.join(dir, 'design-tokens.css')]).status, 0);
    assert.equal(runNode('skills/atlas-checker/scripts/slop-scan.mjs', [dir]).status, 0);

    // 3 proportional fonts must still FAIL both gates
    fs.writeFileSync(
      path.join(dir, 'bad-tokens.css'),
      ':root{--font-display:"Fraunces",serif;--font-sans:"Inter",sans-serif;--font-alt:"Lato",sans-serif}'
    );
    assert.equal(runNode('scripts/check-tokens.mjs', [dir, '--tokens', path.join(dir, 'bad-tokens.css')]).status, 1);
    fs.writeFileSync(
      path.join(dir, 'bad.html'),
      '<!doctype html><html><head><style>h1{font-family:"Fraunces",serif}p{font-family:"Inter",sans-serif}.sub{font-family:"Lato",sans-serif}</style></head><body><h1>Test</h1></body></html>'
    );
    assert.equal(runNode('skills/atlas-checker/scripts/slop-scan.mjs', [dir]).status, 1);
  });

  await t.test('brownfield globals.css fallback, 68ch measure, inline SVG hex, and Tailwind classes pass gates', () => {
    const bfDir = path.join(tmp, 'brownfield-tw');
    fs.mkdirSync(path.join(bfDir, 'src/app'), { recursive: true });
    fs.writeFileSync(
      path.join(bfDir, 'src/app/globals.css'),
      ':root{--color-bg:#f8fafc;--color-surface:#f1f5f9;--color-text:#0f172a;--font-sans:"Inter",sans-serif}prose{max-width:68ch}'
    );
    fs.writeFileSync(
      path.join(bfDir, 'src/app/Page.tsx'),
      `export default function Page() {
        return (
          <main className="bg-zinc-50 text-slate-900">
            <section className="bg-white p-6">
              <div className="bg-slate-900 text-white" style={{ maxWidth: '68ch', height: '100svh' }}>
                <svg viewBox="0 0 120 40" data-viz="true"><rect x="4" y="8" width="40" height="24" fill="#1f5c46" /></svg>
                <form>
                  <input className="border rounded px-3 py-2" type="email" />
                  <select className="border rounded px-3 py-2"><option>Monthly</option></select>
                  <button className="bg-emerald-700 text-white px-4 py-2" type="submit">Save</button>
                </form>
              </div>
            </section>
          </main>
        );
      }`
    );
    const tokRes = runNode('scripts/check-tokens.mjs', [bfDir]);
    assert.equal(tokRes.status, 0, tokRes.stdout + tokRes.stderr);
    const vpRes = runNode('scripts/check-visual-proof.mjs', [bfDir, '--strict']);
    assert.equal(vpRes.status, 0, vpRes.stdout + vpRes.stderr);
  });
});
