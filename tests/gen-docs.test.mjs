import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {
  REPO_ROOT,
  extractQuickCheckFindings,
  parseSimpleYamlFindings,
  loadSceneCatalog,
  parseAgentTargets,
  generateDocs
} from '../scripts/gen-docs.mjs';

test('extractQuickCheckFindings discovers all finding codes from quick-check.mjs', () => {
  const src = fs.readFileSync(
    path.join(REPO_ROOT, 'skills/atlas-checker/scripts/quick-check.mjs'),
    'utf8'
  );
  const findings = extractQuickCheckFindings(src);
  const codes = new Set(findings.map((f) => f.code));

  assert.ok(findings.length >= 26, `expected >= 26 codes, got ${findings.length}`);
  for (const required of [
    'cta-width-mismatch',
    'mobile-long-stack',
    'half-empty-row',
    'partial-opacity',
    'loop-no-pause',
    'mobile-nav-missing',
    'dead-space',
    'cta-not-full-width',
    'overflow',
    'contrast',
    'leaked-photo-placeholder-ui'
  ]) {
    assert.ok(codes.has(required), `missing expected code: ${required}`);
  }
});

test('parseSimpleYamlFindings matches extracted quick-check findings 1-to-1', () => {
  const src = fs.readFileSync(
    path.join(REPO_ROOT, 'skills/atlas-checker/scripts/quick-check.mjs'),
    'utf8'
  );
  const extracted = new Set(extractQuickCheckFindings(src).map((f) => f.code));
  const yaml = parseSimpleYamlFindings(
    fs.readFileSync(path.join(REPO_ROOT, 'site/content-src/findings.yml'), 'utf8')
  );
  const dictCodes = new Set(yaml.map((f) => f.code));

  assert.equal(yaml.length, extracted.size);
  for (const code of extracted) {
    assert.ok(dictCodes.has(code), `findings.yml missing code: ${code}`);
  }
  for (const entry of yaml) {
    assert.ok(entry.meaning_id && entry.meaning_en, `incomplete entry for ${entry.code}`);
    assert.ok(entry.fix_id && entry.fix_en, `missing fix guidance for ${entry.code}`);
  }
});

test('loadSceneCatalog reads 10 valid scenes and agent targets parser reads CLI destinations', () => {
  const catalog = loadSceneCatalog(path.join(REPO_ROOT, 'templates/scene-catalog.json'));
  assert.equal(catalog.scenes.length, 10);
  const heavy = catalog.scenes.filter((s) => s.mode === 'heavy');
  const light = catalog.scenes.filter((s) => s.mode === 'light');
  assert.equal(heavy.length, 6);
  assert.equal(light.length, 4);

  for (const s of catalog.scenes) {
    assert.ok(s.id && s.family && Array.isArray(s.fits) && s.look && s.needs && s.never && s.rest);
  }

  const cliSrc = fs.readFileSync(path.join(REPO_ROOT, 'bin/atlas-skill.mjs'), 'utf8');
  const { projectTargets, globalTargets } = parseAgentTargets(cliSrc);
  assert.ok(projectTargets.some((t) => t.agent === 'claude'));
  assert.ok(projectTargets.some((t) => t.agent === 'codex'));
  assert.ok(projectTargets.some((t) => t.agent === 'antigravity'));
  assert.ok(projectTargets.some((t) => t.agent === 'cursor'));
  assert.ok(projectTargets.some((t) => t.agent === 'windsurf'));
  assert.ok(projectTargets.some((t) => t.agent === 'cline'));
  assert.ok(projectTargets.some((t) => t.agent === 'copilot'));
  assert.ok(globalTargets.some((t) => t.agent === 'antigravity'));
});

test('generateDocs is deterministic and idempotent across consecutive runs', () => {
  const tmpOut = fs.mkdtempSync(path.join(os.tmpdir(), 'atlas-docs-idemp-'));
  try {
    generateDocs({ rootDir: REPO_ROOT, outDir: tmpOut });
    const snapshot = (dir) => {
      const map = new Map();
      const walk = (d) => {
        for (const entry of fs.readdirSync(d, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
          const full = path.join(d, entry.name);
          if (entry.isDirectory()) walk(full);
          else map.set(path.relative(dir, full), fs.readFileSync(full, 'utf8'));
        }
      };
      walk(dir);
      return map;
    };
    const first = snapshot(tmpOut);
    generateDocs({ rootDir: REPO_ROOT, outDir: tmpOut });
    const second = snapshot(tmpOut);

    assert.equal(second.size, first.size);
    for (const [file, content] of first) {
      assert.equal(second.get(file), content, `non-idempotent output in ${file}`);
    }
  } finally {
    fs.rmSync(tmpOut, { recursive: true, force: true });
  }
});
