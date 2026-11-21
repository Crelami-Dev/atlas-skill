#!/usr/bin/env node
/**
 * Unified Atlas v7.0.0 Phase Gate Runner (run-gates.mjs)
 * Executes 5 deterministic static gates + optional --visual Headless Browser Screenshot & DOM Aesthetic Gate:
 *   1. Brief Gate (check-brief)
 *   2. Design Tokens Gate (check-tokens)
 *   3. Anime.js v4 Motion & Lifecycle Gate (check-motion-v4)
 *   4. Anti-Slop Scanner (slop-scan)
 *   4b. Concise Copy Gate (check-copy): word budgets, verb-led buttons, concrete first screen
 *   5. Visual Proof, Surface Cadence & Anti-Wireframe Gate (check-visual-proof)
 *   6. [Optional --visual <html-or-url>] Multi-Viewport Screenshot Capture & DOM Geometry Audit
 */
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const atlasRoot = path.resolve(__dirname, '..');
const args = process.argv.slice(2);
const ext = path.extname(fileURLToPath(import.meta.url)); // .mjs or .js

if (args.includes('--help') || args.includes('-h')) {
  console.log(`Usage: node run-gates${ext} [project-root] [--mode full|light] [--brief <path>] [--tokens <path>] [--visual <html-or-url>] [--shots-dir <dir>]`);
  process.exit(0);
}

const getOpt = (flag) => {
  const i = args.indexOf(flag);
  return i >= 0 && args[i + 1] ? args[i + 1] : null;
};

const mode = getOpt('--mode') || 'full';
const strict = args.includes('--strict');
const briefArg = getOpt('--brief');
const tokensArg = getOpt('--tokens');
const visualTarget = getOpt('--visual');
const shotsDir = getOpt('--shots-dir') || path.join(process.cwd(), 'maintenance/screenshots');

const skipIndices = new Set();
for (const fl of ['--mode', '--brief', '--tokens', '--visual', '--shots-dir']) {
  const idx = args.indexOf(fl);
  if (idx >= 0) skipIndices.add(idx + 1);
}
const positional = args.filter((a, i) => !a.startsWith('--') && !skipIndices.has(i));
const projectRoot = path.resolve(positional[0] || '.');
const briefPath = briefArg ? path.resolve(briefArg) : path.join(projectRoot, 'design-brief.md');
const tokensPath = tokensArg ? path.resolve(tokensArg) : path.join(projectRoot, 'design-tokens.css');

const steps = [];
if (mode === 'full') {
  steps.push({ name: '1. Brief Gate', cmd: process.execPath, args: [path.join(atlasRoot, `scripts/check-brief${ext}`), briefPath] });
}
if (fs.existsSync(tokensPath) || mode === 'full') {
  steps.push({ name: '2. Tokens Gate', cmd: process.execPath, args: [path.join(atlasRoot, `scripts/check-tokens${ext}`), projectRoot, '--tokens', tokensPath] });
}
steps.push({ name: '3. Anime.js v4 Motion Gate', cmd: process.execPath, args: [path.join(atlasRoot, `scripts/check-motion-v4${ext}`), projectRoot] });
steps.push({ name: '4. Anti-Slop Gate', cmd: process.execPath, args: [path.join(atlasRoot, `skills/atlas-checker/scripts/slop-scan${ext}`), projectRoot] });
steps.push({ name: '4b. Concise Copy Gate', cmd: process.execPath, args: [path.join(atlasRoot, `scripts/check-copy${ext}`), projectRoot, ...(strict ? ['--strict'] : [])] });
steps.push({ name: '5. Visual Proof & Anti-Wireframe Gate', cmd: process.execPath, args: [path.join(atlasRoot, `scripts/check-visual-proof${ext}`), projectRoot, ...(strict ? ['--strict'] : [])] });

function resolvePython() {
  for (const candidate of process.platform === 'win32' ? ['python', 'python3'] : ['python3', 'python']) {
    const probe = spawnSync(candidate, ['--version'], { encoding: 'utf8' });
    if (probe.status === 0 && /Python 3\./i.test((probe.stdout || '') + (probe.stderr || ''))) {
      return candidate;
    }
  }
  return process.platform === 'win32' ? 'python' : 'python3';
}

if (visualTarget) {
  steps.push({
    name: '6. Browser Screenshot & Aesthetic DOM Gate',
    cmd: resolvePython(),
    args: [path.join(atlasRoot, 'skills/atlas-checker/scripts/visual_dom_inspector.py'), path.resolve(visualTarget), '--out-dir', path.resolve(shotsDir)]
  });
}

const results = [];
let failed = false;

for (const step of steps) {
  const res = spawnSync(step.cmd, step.args, { cwd: projectRoot, encoding: 'utf8' });
  const ok = res.status === 0;
  if (!ok) failed = true;
  results.push({
    gate: step.name,
    status: ok ? 'PASS' : 'FAIL',
    exitCode: res.status,
    output: ((res.stdout || '') + '\n' + (res.stderr || '')).trim().slice(0, 2500),
  });
}

console.log(JSON.stringify({ projectRoot, mode, overall: failed ? 'FAIL' : 'PASS', results }, null, 2));
if (failed) process.exitCode = 1;
