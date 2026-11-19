import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const source = path.resolve(__dirname, '..');
const cli = path.join(source, 'bin/atlas-skill.mjs');
const workspace = fs.mkdtempSync(path.join(os.tmpdir(), 'atlas-installer-test-'));
const target = path.join(workspace, '.claude/skills/atlas-frontend-design');
const run = (args, cwd = workspace) => spawnSync(process.execPath, [cli, ...args], { cwd, encoding: 'utf8' });
const json = result => JSON.parse(result.stdout.split('\nRestart/reload')[0]);

test('installer lifecycle, multi-agent flags, QA suite, and boundaries', async t => {
  await t.test('version and help are usable', () => {
    assert.equal(run(['--version']).stdout.trim(), '7.0.0');
    assert.match(run(['--help']).stdout, /install[\s\S]*--agent/);
    assert.match(run(['--help']).stdout, /--with-qa/);
  });

  await t.test('list exposes all 11 core skills and 3 QA skills', () => {
    const result = run(['list']);
    assert.equal(result.status, 0, result.stderr);
    const data = json(result);
    assert.equal(data.version, '7.0.0');
    assert.equal(data.skills.length, 11);
    assert.equal(data.qaSkills.length, 3);
    assert.equal(data.projectDestinations.agents, '.agents/skills/atlas-frontend-design');
    assert.equal(data.projectDestinations.antigravity, '.agents/skills/atlas-frontend-design');
  });

  await t.test('noninteractive missing target never guesses or writes', () => {
    for (const args of [[], ['install'], ['update'], ['doctor'], ['install', '--dry-run']]) {
      const result = run(args);
      assert.equal(result.status, 2);
      assert.match(result.stderr, /--agent/);
      assert.ok(!fs.existsSync(target));
      assert.ok(!fs.existsSync(path.join(workspace, '.agents')));
    }
  });

  await t.test('dry run validates without creating destination', () => {
    const result = run(['install', '--agent', 'claude', '--dry-run']);
    assert.equal(result.status, 0, result.stderr);
    assert.equal(json(result).dryRun, true);
    assert.ok(!fs.existsSync(target));
  });

  await t.test('installs the complete allowlisted package for claude', () => {
    const result = run(['install', '--agent', 'claude']);
    assert.equal(result.status, 0, result.stderr);
    const data = json(result);
    assert.equal(data.status, 'installed');
    assert.equal(data.version, '7.0.0');
    assert.equal(data.target, target);
    for (const relative of ['SKILL.md', 'skills/atlas-research/SKILL.md', 'references/typography.md', 'scripts/validate-package.mjs', 'docs/INSTALLATION.md', 'suites/project-qa/rules/qa-security-gate.md']) {
      assert.ok(fs.existsSync(path.join(target, relative)), relative);
    }
    for (const name of ['node_modules', '.git']) {
      assert.ok(!fs.existsSync(path.join(target, name)), name);
    }
  });

  await t.test('doctor confirms integrity and node version', () => {
    const result = run(['doctor', '--agent', 'claude']);
    assert.equal(result.status, 0, result.stderr);
    const data = json(result);
    assert.equal(data.status, 'valid');
    assert.equal(data.installedVersion, '7.0.0');
    assert.equal(data.agentActivation, 'not-tested');
  });

  await t.test('existing install is never overwritten by install', () => {
    const before = fs.readFileSync(path.join(target, 'SKILL.md'), 'utf8');
    assert.equal(run(['install', '--agent', 'claude']).status, 1);
    assert.equal(fs.readFileSync(path.join(target, 'SKILL.md'), 'utf8'), before);
  });

  await t.test('unmodified update is idempotent', () => {
    const result = run(['update', '--agent', 'claude']);
    assert.equal(result.status, 0, result.stderr);
    assert.equal(json(result).status, 'current');
    assert.ok(!fs.existsSync(path.join(workspace, '.atlas-skill-backups')));
  });

  await t.test('doctor detects modified content', () => {
    fs.appendFileSync(path.join(target, 'SKILL.md'), '\nLocal customization\n');
    fs.writeFileSync(path.join(target, 'my-notes.txt'), 'Keep my local notes');
    const result = run(['doctor', '--agent', 'claude']);
    assert.equal(result.status, 1);
    assert.ok(json(result).changes.includes('SKILL.md'));
  });

  await t.test('update backs up all old content and installs clean package', () => {
    const result = run(['update', '--agent', 'claude']);
    assert.equal(result.status, 0, result.stderr);
    const record = json(result);
    assert.equal(record.status, 'updated');
    assert.match(fs.readFileSync(path.join(record.backup, 'SKILL.md'), 'utf8'), /Local customization/);
    assert.equal(fs.readFileSync(path.join(record.backup, 'my-notes.txt'), 'utf8'), 'Keep my local notes');
    assert.equal(fs.readFileSync(path.join(target, 'SKILL.md'), 'utf8'), fs.readFileSync(path.join(source, 'SKILL.md'), 'utf8'));
    assert.equal(run(['doctor', '--agent', 'claude']).status, 0);
  });

  await t.test('antigravity with --with-rules --expose-subskills --with-qa installs all skills and rules', () => {
    const dir = path.join(workspace, 'ag-project');
    fs.mkdirSync(dir);
    const result = run(['install', '--agent', 'antigravity', '--with-rules', '--expose-subskills', '--with-qa'], dir);
    assert.equal(result.status, 0, result.stderr);
    assert.ok(fs.existsSync(path.join(dir, '.agents/skills/atlas-frontend-design/SKILL.md')));
    assert.ok(fs.existsSync(path.join(dir, '.agents/skills/atlas-motion-animejs/SKILL.md')));
    assert.ok(fs.existsSync(path.join(dir, '.agents/skills/project-bug-hunter/SKILL.md')));
    assert.ok(fs.existsSync(path.join(dir, '.agents/skills/project-security-auditor/SKILL.md')));
    assert.ok(fs.existsSync(path.join(dir, '.agents/skills/project-fix-and-verify/SKILL.md')));
    assert.ok(fs.existsSync(path.join(dir, '.agents/skills/project-fix-and-verify/scripts/verify_feature_coverage.py')));
    assert.ok(fs.existsSync(path.join(dir, '.agents/rules/atlas-frontend-gate.md')));
    assert.ok(fs.existsSync(path.join(dir, '.agents/rules/qa-security-gate.md')));
    assert.equal(run(['doctor', '--agent', 'codex'], dir).status, 0);
  });

  await t.test('agent all installs to .agents, .claude, and .cursor', () => {
    const dir = path.join(workspace, 'all-project');
    fs.mkdirSync(dir);
    const result = run(['install', '--agent', 'all', '--with-rules', '--with-qa'], dir);
    assert.equal(result.status, 0, result.stderr);
    assert.ok(fs.existsSync(path.join(dir, '.agents/skills/atlas-frontend-design/SKILL.md')));
    assert.ok(fs.existsSync(path.join(dir, '.claude/skills/atlas-frontend-design/SKILL.md')));
    assert.ok(fs.existsSync(path.join(dir, '.cursor/skills/atlas-frontend-design/SKILL.md')));
    assert.ok(fs.existsSync(path.join(dir, '.cursor/rules/atlas-frontend-gate.mdc')));
    assert.ok(fs.existsSync(path.join(dir, '.agents/rules/qa-security-gate.md')));
  });

  await t.test('unmanaged folders are preserved', () => {
    const dir = path.join(workspace, 'manual-atlas');
    fs.mkdirSync(dir);
    fs.writeFileSync(path.join(dir, 'note.txt'), 'Untouched');
    assert.equal(run(['update', '--dir', dir]).status, 1);
    assert.equal(fs.readFileSync(path.join(dir, 'note.txt'), 'utf8'), 'Untouched');
  });

  await t.test('unknown commands, agents and incomplete options are usage errors', () => {
    for (const args of [['publish'], ['install', '--agent', 'unknown'], ['install', '--dir'], ['install', '--force']]) {
      assert.equal(run(args).status, 2, args.join(' '));
    }
  });

  await t.test('project root, drive root and installer source are rejected', () => {
    for (const dir of [workspace, path.parse(workspace).root, source]) {
      assert.equal(run(['install', '--dir', dir]).status, 1, dir);
    }
  });

  await t.test('metadata path traversal is rejected', () => {
    const metadata = path.join(target, '.atlas-install.json');
    const original = fs.readFileSync(metadata, 'utf8');
    const record = JSON.parse(original);
    record.files['../../outside.txt'] = 'invalid';
    fs.writeFileSync(metadata, JSON.stringify(record));
    const result = run(['doctor', '--agent', 'claude']);
    assert.equal(result.status, 1);
    assert.match(result.stderr, /invalid file path/);
    fs.writeFileSync(metadata, original);
  });

  await t.test('slop-scan and check-visual-proof block leaked photo placeholder badges but pass clean editorial plates', () => {
    const slopScan = path.join(source, 'skills/atlas-checker/scripts/slop-scan.mjs');
    const visualProof = path.join(source, 'scripts/check-visual-proof.mjs');

    const leakySamples = [
      '<figure data-photo-placeholder="true"><span>GANTI DENGAN FOTO ASLI</span></figure>',
      '<figure data-photo-slot="hero"><span>SLOT FOTO 01 • 16:9</span></figure>',
      '<figure data-photo-slot="hero"><span>Replace with photo</span></figure>',
      '<section><p>[Data Klien Diperlukan]</p></section>',
      '<figure data-photo-slot="hero"><p>Subjek: Meja bar kayu jati dengan pencahayaan pagi</p></figure>'
    ];
    for (let i = 0; i < leakySamples.length; i++) {
      const sampleDir = path.join(workspace, `leak-${i}`);
      fs.mkdirSync(sampleDir);
      fs.writeFileSync(path.join(sampleDir, 'index.html'), `<!doctype html><html><body><main>${leakySamples[i]}</main></body></html>`);
      const sRes = spawnSync(process.execPath, [slopScan, sampleDir], { encoding: 'utf8' });
      const vRes = spawnSync(process.execPath, [visualProof, sampleDir], { encoding: 'utf8' });
      assert.equal(sRes.status, 1, `slop-scan should fail sample ${i}`);
      assert.match(sRes.stdout, /leaked-photo-placeholder-ui/);
      assert.equal(vRes.status, 1, `check-visual-proof should fail sample ${i}`);
      assert.match(vRes.stdout, /leaked-photo-placeholder-ui/);
    }

    const cleanDir = path.join(workspace, 'clean-plate');
    fs.mkdirSync(cleanDir);
    fs.writeFileSync(
      path.join(cleanDir, 'styles.css'),
      ':root{--color-bg:#faf9f6;--color-surface:#f1efe9;--color-surface-elevated:#fff;--font-display:serif;--font-sans:sans-serif}body{background:var(--color-bg);font-family:var(--font-sans)}section{background:var(--color-surface)}.card{background:var(--color-surface-elevated)}input,button{border:1px solid #d8d5cd}'
    );
    fs.writeFileSync(
      path.join(cleanDir, 'index.html'),
      '<!doctype html><html><head><link rel="stylesheet" href="styles.css"></head><body><main><figure data-photo-slot="bar-16x9" data-atlas-proof="editorial-plate"><div role="img" aria-label="Meja seduh kayu jati pagi hari"><span>PLATE 01 · CIBEUNYING</span></div><figcaption>Ruang seduh utama kapasitas 18 kursi.</figcaption></figure><section><form><label for="subj">Subjek: Pertanyaan Kerjasama Acara</label><input id="subj" type="text"><button type="submit">Kirim</button></form></section></main></body></html>'
    );
    const sClean = spawnSync(process.execPath, [slopScan, cleanDir], { encoding: 'utf8' });
    const vClean = spawnSync(process.execPath, [visualProof, cleanDir, '--strict'], { encoding: 'utf8' });
    assert.equal(sClean.status, 0, sClean.stdout + sClean.stderr);
    assert.equal(vClean.status, 0, vClean.stdout + vClean.stderr);
  });
});
