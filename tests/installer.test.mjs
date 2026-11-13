import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import os from 'node:os';
import { spawnSync } from 'node:child_process';

const source = path.resolve(import.meta.dirname, '..');
const cli = path.join(source, 'bin/atlas-skill.mjs');
const workspace = fs.mkdtempSync(path.join(os.tmpdir(), 'atlas-installer-test-'));
const target = path.join(workspace, '.claude/skills/atlas');
const run = (args, cwd = workspace) => spawnSync(process.execPath, [cli, ...args], { cwd, encoding: 'utf8' });
const json = result => JSON.parse(result.stdout.split('\nRestart/reload')[0]);

test('installer lifecycle and boundaries', async t => {
  await t.test('version and help are usable', () => {
    assert.equal(run(['--version']).stdout.trim(), '4.0.0');
    assert.match(run(['--help']).stdout, /install.*--agent/);
  });
  await t.test('list exposes all seven skill entry files', () => {
    const result = run(['list']); assert.equal(result.status, 0);
    assert.equal(json(result).skills.length, 7);
  });
  await t.test('dry run validates without creating destination', () => {
    const result = run(['install', '--agent', 'claude', '--dry-run']);
    assert.equal(result.status, 0, result.stderr);
    assert.equal(json(result).dryRun, true); assert.ok(!fs.existsSync(target));
  });
  await t.test('installs the complete allowlisted package', () => {
    const result = run(['install', '--agent', 'claude']);
    assert.equal(result.status, 0, result.stderr);
    assert.equal(json(result).status, 'installed');
    assert.equal(json(result).target, target);
    for (const relative of ['SKILL.md', 'skills/atlas-research/SKILL.md', 'references/typography.md', 'scripts/validate-package.mjs', 'docs/INSTALLATION.md']) assert.ok(fs.existsSync(path.join(target, relative)), relative);
    for (const name of ['node_modules', 'runtime', 'knowledge', 'output', 'demo-codex', '.git']) assert.ok(!fs.existsSync(path.join(target, name)), name);
  });
  await t.test('doctor confirms integrity but not activation', () => {
    const result = run(['doctor', '--agent', 'claude']);
    assert.equal(result.status, 0, result.stderr);
    assert.equal(json(result).status, 'valid');
    assert.equal(json(result).agentActivation, 'not-tested');
  });
  await t.test('existing install is never overwritten by install', () => {
    const before = fs.readFileSync(path.join(target, 'SKILL.md'), 'utf8');
    assert.equal(run(['install', '--agent', 'claude']).status, 1);
    assert.equal(fs.readFileSync(path.join(target, 'SKILL.md'), 'utf8'), before);
  });
  await t.test('unmodified update is idempotent', () => {
    const result = run(['update', '--agent', 'claude']);
    assert.equal(result.status, 0, result.stderr); assert.equal(json(result).status, 'current');
    assert.ok(!fs.existsSync(path.join(workspace, '.atlas-skill-backups')));
  });
  await t.test('doctor detects modified content', () => {
    fs.appendFileSync(path.join(target, 'SKILL.md'), '\nLocal customization\n');
    fs.writeFileSync(path.join(target, 'my-notes.txt'), 'Keep my local notes');
    const result = run(['doctor', '--agent', 'claude']);
    assert.equal(result.status, 1); assert.ok(json(result).changes.includes('SKILL.md'));
  });
  await t.test('update backs up all old content and installs clean package', () => {
    const result = run(['update', '--agent', 'claude']);
    assert.equal(result.status, 0, result.stderr);
    const record = json(result); assert.equal(record.status, 'updated');
    assert.match(fs.readFileSync(path.join(record.backup, 'SKILL.md'), 'utf8'), /Local customization/);
    assert.equal(fs.readFileSync(path.join(record.backup, 'my-notes.txt'), 'utf8'), 'Keep my local notes');
    assert.equal(fs.readFileSync(path.join(target, 'SKILL.md'), 'utf8'), fs.readFileSync(path.join(source, 'SKILL.md'), 'utf8'));
    assert.equal(run(['doctor', '--agent', 'claude']).status, 0);
  });
  await t.test('unmanaged folders are preserved', () => {
    const dir = path.join(workspace, 'manual-atlas'); fs.mkdirSync(dir); fs.writeFileSync(path.join(dir, 'note.txt'), 'Untouched');
    assert.equal(run(['update', '--dir', dir]).status, 1);
    assert.equal(fs.readFileSync(path.join(dir, 'note.txt'), 'utf8'), 'Untouched');
  });
  await t.test('custom dedicated destination works', () => {
    const dir = path.join(workspace, 'custom-atlas');
    assert.equal(run(['install', '--dir', dir]).status, 0);
    assert.equal(run(['doctor', '--dir', dir]).status, 0);
  });
  await t.test('Codex and Antigravity use shared project path', () => {
    const dir = path.join(workspace, 'shared-project'); fs.mkdirSync(dir);
    assert.equal(run(['install', '--agent', 'antigravity'], dir).status, 0);
    assert.ok(fs.existsSync(path.join(dir, '.agents/skills/atlas/SKILL.md')));
    assert.equal(run(['doctor', '--agent', 'codex'], dir).status, 0);
  });
  await t.test('missing installation reports failure', () => assert.equal(run(['doctor', '--dir', path.join(workspace, 'absent')]).status, 1));
  await t.test('unknown commands, agents and incomplete options are usage errors', () => {
    for (const args of [['publish'], ['install', '--agent', 'unknown'], ['install', '--dir'], ['install', '--force']]) assert.equal(run(args).status, 2, args.join(' '));
  });
  await t.test('project root, drive root and installer source are rejected', () => {
    for (const dir of [workspace, path.parse(workspace).root, source]) assert.equal(run(['install', '--dir', dir]).status, 1, dir);
  });
  await t.test('metadata path traversal is rejected', () => {
    const metadata = path.join(target, '.atlas-install.json'); const original = fs.readFileSync(metadata, 'utf8');
    const record = JSON.parse(original); record.files['../../outside.txt'] = 'invalid'; fs.writeFileSync(metadata, JSON.stringify(record));
    const result = run(['doctor', '--agent', 'claude']); assert.equal(result.status, 1); assert.match(result.stderr, /invalid file path/);
    fs.writeFileSync(metadata, original);
  });
});
