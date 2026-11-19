import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const root = path.resolve(__dirname, '..');
const tmp = fs.mkdtempSync(path.join(os.tmpdir(), 'atlas-qa-suite-test-'));

function findPython() {
  for (const candidate of process.platform === 'win32' ? ['python', 'python3'] : ['python3', 'python']) {
    const probe = spawnSync(candidate, ['--version'], { encoding: 'utf8' });
    if (probe.status === 0 && /Python 3\./i.test((probe.stdout || '') + (probe.stderr || ''))) {
      return candidate;
    }
  }
  return null;
}

const py = findPython();

test('QA & Security Python suite functional tests', { skip: !py && 'Python 3 not available' }, async t => {
  const sampleProj = path.join(tmp, 'sample-app');
  fs.mkdirSync(path.join(sampleProj, 'src'), { recursive: true });
  fs.writeFileSync(
    path.join(sampleProj, 'package.json'),
    JSON.stringify({ name: 'sample-app', version: '1.0.0', dependencies: { express: '4.18.2' } }, null, 2)
  );
  fs.writeFileSync(
    path.join(sampleProj, 'package-lock.json'),
    JSON.stringify({
      name: 'sample-app',
      lockfileVersion: 3,
      packages: {
        '': { name: 'sample-app', version: '1.0.0' },
        'node_modules/express': { version: '4.18.2' }
      }
    }, null, 2)
  );
  const fakeStripeKey = ['sk', 'live', '1234567890abcdefghijklmnop'].join('_');
  fs.writeFileSync(
    path.join(sampleProj, 'src/server.js'),
    `const apiKey = '${fakeStripeKey}';\nfunction render(el, html) { el.innerHTML = html; }\n`
  );

  await t.test('all Python scripts compile cleanly with -W error', () => {
    const scripts = [
      'skills/atlas-checker/scripts/visual_dom_inspector.py',
      'suites/project-qa/skills/project-bug-hunter/scripts/project_inventory.py',
      'suites/project-qa/skills/project-bug-hunter/scripts/ui_visual_bug_probe.py',
      'suites/project-qa/skills/project-fix-and-verify/scripts/e2e_visual_regression.py',
      'suites/project-qa/skills/project-fix-and-verify/scripts/verify_feature_coverage.py',
      'suites/project-qa/skills/project-security-auditor/scripts/live_cve_osv_check.py',
      'suites/project-qa/skills/project-security-auditor/scripts/security_scan.py'
    ];
    for (const rel of scripts) {
      const res = spawnSync(py, ['-W', 'error', '-B', '-m', 'py_compile', path.join(root, rel)], { encoding: 'utf8' });
      assert.equal(res.status, 0, `${rel}: ${res.stderr}`);
    }
  });

  await t.test('project_inventory.py scans sample project', () => {
    const script = path.join(root, 'suites/project-qa/skills/project-bug-hunter/scripts/project_inventory.py');
    const res = spawnSync(py, ['-B', script, sampleProj], { encoding: 'utf8' });
    assert.equal(res.status, 0, res.stderr);
    const data = JSON.parse(res.stdout);
    assert.ok(data.total_scanned_files >= 3);
    assert.ok(data.detected_manifests.some(m => m.file === 'package.json'));
    assert.equal(data.code_files_by_extension['.js'], 1);
  });

  await t.test('security_scan.py detects unsafe DOM sink and secret patterns', () => {
    const script = path.join(root, 'suites/project-qa/skills/project-security-auditor/scripts/security_scan.py');
    const res = spawnSync(py, ['-B', script, sampleProj], { encoding: 'utf8' });
    assert.equal(res.status, 0, res.stderr);
    assert.match(res.stdout, /innerHTML|sk_live_/i);
  });

  await t.test('live_cve_osv_check.py parses dependencies in --offline-parse-only mode', () => {
    const script = path.join(root, 'suites/project-qa/skills/project-security-auditor/scripts/live_cve_osv_check.py');
    const res = spawnSync(py, ['-B', script, sampleProj, '--offline-parse-only'], { encoding: 'utf8' });
    assert.equal(res.status, 0, res.stderr);
    assert.match(res.stdout, /express/i);
  });

  await t.test('verify_feature_coverage.py runs cleanly on sample project', () => {
    const script = path.join(root, 'suites/project-qa/skills/project-fix-and-verify/scripts/verify_feature_coverage.py');
    const res = spawnSync(py, ['-B', script, sampleProj], { encoding: 'utf8' });
    assert.equal(res.status, 0, res.stderr);
    assert.ok(res.stdout.trim().length > 0);
  });
});
