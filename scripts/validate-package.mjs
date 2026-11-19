#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';
import { packageFiles } from './package-files.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const args = process.argv.slice(2);
const rootIndex = args.indexOf('--root');
const root = rootIndex >= 0 ? path.resolve(args[rootIndex + 1]) : path.resolve(__dirname, '..');
const outputIndex = args.indexOf('--report');
const reportPath = outputIndex >= 0 ? path.resolve(args[outputIndex + 1]) : null;
const { manifest, files } = packageFiles(root);
const included = new Set(files);
const errors = [];
const counts = { skills: 0, markdown: 0, links: 0, scripts: 0, lines: 0 };
const moduleLines = {};
const names = new Set();
const pkgJson = JSON.parse(fs.readFileSync(path.join(root, "package.json"), "utf8"));
const pluginJson = JSON.parse(fs.readFileSync(path.join(root, "plugin.json"), "utf8"));
const readmeText = fs.readFileSync(path.join(root, "README.md"), "utf8");
const changelogText = fs.readFileSync(path.join(root, "CHANGELOG.md"), "utf8");
if (manifest.version !== pkgJson.version) errors.push(`Version mismatch: package-manifest.json (${manifest.version}) !== package.json (${pkgJson.version})`);
if (pluginJson.version !== pkgJson.version) errors.push(`Version mismatch: plugin.json (${pluginJson.version}) !== package.json (${pkgJson.version})`);
if (!readmeText.includes(`v${pkgJson.version}`)) errors.push(`README.md does not reference current package.json version v${pkgJson.version}`);
if (!changelogText.includes(`## ${pkgJson.version}`)) errors.push(`CHANGELOG.md does not contain section for current package.json version ${pkgJson.version}`);


const qaManifestPath = path.join(root, 'suites/project-qa/package-manifest.json');
const qaManifest = fs.existsSync(qaManifestPath) ? JSON.parse(fs.readFileSync(qaManifestPath, 'utf8')) : { skills: [] };
if (qaManifest.version && qaManifest.version !== pkgJson.version) {
  errors.push(`Version mismatch: suites/project-qa/package-manifest.json (${qaManifest.version}) !== package.json (${pkgJson.version})`);
}
for (const skill of [...manifest.skills, ...qaManifest.skills]) {
  if (!included.has(skill.path)) { errors.push(`Skill not included: ${skill.path}`); continue; }
  const text = fs.readFileSync(path.join(root, skill.path), 'utf8').replaceAll('\r\n', '\n');
  const frontmatter = text.match(/^---\nname: ([a-z][a-z0-9-]*)\ndescription: ("(?:[^"\\]|\\.)*")\n---\n/);
  if (!frontmatter) { errors.push(`Use valid, quoted YAML description frontmatter: ${skill.path}`); continue; }
  const description = JSON.parse(frontmatter[2]);
  if (frontmatter[1] !== skill.name || names.has(skill.name)) errors.push(`Invalid/duplicate skill name: ${skill.path}`);
  if (description.length < 30 || description.length > 1024) errors.push(`Description outside supported package bounds: ${skill.path}`);
  names.add(skill.name);
  counts.skills++;
  moduleLines[skill.name] = text.split('\n').length - 1;
}

for (const relative of files) {
  const absolute = path.join(root, relative);
  if (relative.endsWith('.md') || relative.endsWith('.mdc')) {
    counts.markdown++;
    const text = fs.readFileSync(absolute, 'utf8');
    counts.lines += text.split('\n').length - 1;
    if (text.includes('\uFFFD') || /\d\?\d/.test(text) || /^# .* \? /m.test(text)) errors.push(`Likely text encoding corruption: ${relative}`);
    const fenceCount = (text.match(/^\s*```/gm) || []).length;
    if (fenceCount % 2) errors.push(`Unclosed code fence: ${relative}`);
    for (const match of text.matchAll(/\]\(([^)]+)\)/g)) {
      const href = match[1].replace(/^<|>$/g, '');
      if (/^(https?:|mailto:|#)/.test(href)) continue;
      // Adapter templates intentionally reference host project paths after installation
      if (relative.startsWith('adapters/')) continue;
      const local = decodeURIComponent(href.split('#')[0]);
      const target = path.relative(root, path.resolve(path.dirname(absolute), local)).replaceAll('\\', '/');
      counts.links++;
      if (!included.has(target)) errors.push(`Broken/nonportable link: ${relative} -> ${href}`);
    }
  }
  if (relative.endsWith('.json')) {
    try { JSON.parse(fs.readFileSync(absolute, 'utf8')); } catch { errors.push(`Invalid JSON: ${relative}`); }
  }
  if (relative.endsWith('.mjs')) {
    counts.scripts++;
    const check = spawnSync(process.execPath, ['--check', absolute], { encoding: 'utf8' });
    if (check.status !== 0) errors.push(`Script syntax error: ${relative}: ${check.stderr}`);
  }
}

const report = { version: pkgJson.version, root, includedFiles: files.length, counts, moduleLines, errors, result: errors.length ? 'FAIL' : 'PASS', limits: 'Structural validation does not prove instruction quality, current external links, visual judgment or scenario behavior.' };
if (reportPath) {
  fs.mkdirSync(path.dirname(reportPath), { recursive: true });
  fs.writeFileSync(reportPath, JSON.stringify(report, null, 2));
}
console.log(JSON.stringify(report, null, 2));
if (errors.length) process.exitCode = 1;
