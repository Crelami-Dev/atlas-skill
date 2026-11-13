#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { createInterface } from 'node:readline/promises';
import { packageFiles } from '../scripts/package-files.mjs';

const source = path.resolve(import.meta.dirname, '..');
const metadataName = '.atlas-install.json';
const { manifest, files } = packageFiles(source);
const agents = { agents: '.agents/skills/atlas', claude: '.claude/skills/atlas', codex: '.agents/skills/atlas', antigravity: '.agents/skills/atlas' };
const fail = (message, code = 1) => { throw Object.assign(new Error(message), { exitCode: code }); };
const inside = (root, target) => { const rel = path.relative(root, target); return rel === '' || (!rel.startsWith('..') && !path.isAbsolute(rel)); };
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');

function options(argv) {
  const result = { command: 'install', agent: null, dir: null, dryRun: false };
  let commandSet = false;
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--help' || arg === '-h') return { ...result, command: 'help' };
    if (arg === '--version' || arg === '-v') return { ...result, command: 'version' };
    if (arg === '--dry-run') { result.dryRun = true; continue; }
    if (arg === '--agent' || arg === '--dir') {
      if (!argv[i + 1] || argv[i + 1].startsWith('--')) fail(`Missing value for ${arg}`, 2);
      result[arg.slice(2)] = argv[++i]; continue;
    }
    if (arg.startsWith('-') || commandSet) fail(`Unexpected argument: ${arg}`, 2);
    result.command = arg; commandSet = true;
  }
  if (!['help', 'version', 'install', 'update', 'doctor', 'list'].includes(result.command)) fail(`Unknown command: ${result.command}`, 2);
  if (result.agent !== null && !Object.hasOwn(agents, result.agent)) fail(`Unknown agent: ${result.agent}. Use agents or claude (codex and antigravity are aliases for agents).`, 2);
  return result;
}

async function chooseTarget(config) {
  if (config.agent) return;
  if (config.dir) { config.agent = 'agents'; return; }
  if (!process.stdin.isTTY || !process.stdout.isTTY) fail('Choose a target with --agent agents or --agent claude when running without an interactive terminal.', 2);
  const prompt = createInterface({ input: process.stdin, output: process.stdout });
  let answered = false;
  prompt.on('SIGINT', () => { prompt.close(); });
  prompt.on('close', () => { if (!answered) process.exitCode = 130; });
  console.log(`\nAtlas Skill ${manifest.version} — project-local ${config.command}\nProject: ${process.cwd()}\n\n  1. Agents — .agents/skills/atlas\n     For AI tools that discover skills in .agents/skills.\n  2. Claude Code — .claude/skills/atlas\n\nNothing is installed globally. Ctrl+C to cancel.\n`);
  try {
    while (!config.agent) {
      const answer = (await prompt.question('Choose [1/2]: ')).trim().toLowerCase();
      if (['1', 'agents'].includes(answer)) config.agent = 'agents';
      else if (['2', 'claude'].includes(answer)) config.agent = 'claude';
      else console.log('Enter 1 for Agents or 2 for Claude Code.');
    }
    answered = true;
  } catch { fail('Installation cancelled. No files were changed.', 130); }
  finally { prompt.close(); }
}

function destination(config) {
  const target = path.resolve(config.dir || path.join(process.cwd(), agents[config.agent]));
  if (target === path.parse(target).root || target === path.resolve(process.cwd()) || inside(source, target) || inside(target, source) || path.basename(target) === '.git') fail('Choose a dedicated skill directory outside the installer source, not a project/drive root.');
  // Reject symlink/junction ancestors before writing or renaming a computed path.
  for (let current = target; current !== path.dirname(current); current = path.dirname(current)) {
    if (fs.existsSync(current) && fs.lstatSync(current).isSymbolicLink()) fail(`Symlink/junction destination is not supported: ${current}`);
  }
  return target;
}

function inspect(target) {
  if (!fs.existsSync(path.join(target, metadataName))) fail(`No managed Atlas installation at ${target}. Choose an empty directory for install; unmanaged folders are never overwritten.`);
  const record = JSON.parse(fs.readFileSync(path.join(target, metadataName), 'utf8'));
  if (record.name !== 'atlas-skill' || typeof record.version !== 'string' || !record.files || typeof record.files !== 'object' || Array.isArray(record.files) || !Object.keys(record.files).length) fail('Invalid Atlas installation metadata.');
  const changes = [];
  for (const [relative, expected] of Object.entries(record.files)) {
    const file = path.resolve(target, relative);
    if (!inside(target, file) || file === target) fail('Installation metadata contains an invalid file path.');
    if (!fs.existsSync(file) || !fs.statSync(file).isFile() || hash(file) !== expected) changes.push(relative);
  }
  return { record, changes };
}

function validateSource() {
  const result = spawnSync(process.execPath, [path.join(source, 'scripts/validate-package.mjs')], { encoding: 'utf8' });
  if (result.status !== 0) fail(`Source package failed validation:\n${result.stdout}${result.stderr}`);
}

function install(config, target) {
  const exists = fs.existsSync(target);
  if (config.command === 'install' && exists) fail(`Destination exists: ${target}. Use update for a managed installation or choose an empty --dir.`);
  if (config.command === 'update' && !exists) fail(`No installation at ${target}. Run install first.`);
  const prior = exists ? inspect(target) : null;
  validateSource();
  if (config.dryRun) { console.log(JSON.stringify({ action: config.command, dryRun: true, agent: config.agent, target, version: manifest.version, files: files.length, backupRequired: exists }, null, 2)); return; }
  const hashes = Object.fromEntries(files.map(relative => [relative, hash(path.join(source, relative))]));
  if (prior && !prior.changes.length && JSON.stringify(prior.record.files) === JSON.stringify(hashes)) { console.log(JSON.stringify({ status: 'current', target, version: manifest.version }, null, 2)); return; }

  const parent = path.dirname(target);
  fs.mkdirSync(parent, { recursive: true });
  const stage = path.join(parent, `.atlas-stage-${crypto.randomUUID()}`);
  if (!inside(parent, stage) || stage === target) fail('Invalid staging path.');
  fs.mkdirSync(stage);
  let backup = null;
  try {
    for (const relative of files) {
      const file = path.join(stage, relative);
      fs.mkdirSync(path.dirname(file), { recursive: true });
      fs.copyFileSync(path.join(source, relative), file);
    }
    fs.writeFileSync(path.join(stage, metadataName), JSON.stringify({ name: 'atlas-skill', version: manifest.version, agent: config.agent, installedAt: new Date().toISOString(), source: 'https://github.com/Crelami-Dev/atlas-skill', files: hashes }, null, 2));
    if (exists) {
      const backupRoot = path.resolve(process.cwd(), '.atlas-skill-backups');
      backup = path.join(backupRoot, `atlas-${Date.now()}-${crypto.randomUUID()}`);
      if (inside(target, backup) || inside(backup, target) || !inside(backupRoot, backup)) fail('Backup must be outside the installation.');
      if (fs.existsSync(backupRoot) && fs.lstatSync(backupRoot).isSymbolicLink()) fail('Backup root must not be a symlink.');
      fs.mkdirSync(backupRoot, { recursive: true });
      fs.renameSync(target, backup);
    }
    fs.renameSync(stage, target);
    console.log(JSON.stringify({ status: exists ? 'updated' : 'installed', version: manifest.version, agent: config.agent, target, files: files.length, backup, priorModifiedFiles: prior?.changes || [] }, null, 2));
    console.log('Restart/reload the agent if needed, then explicitly ask it to use Atlas. Installation does not prove agent activation.');
  } catch (error) {
    if (backup && fs.existsSync(backup) && !fs.existsSync(target)) fs.renameSync(backup, target);
    error.message += `\nUncommitted staging, if present: ${stage}`;
    throw error;
  }
}

try {
  const config = options(process.argv.slice(2));
  if (config.command === 'help') console.log(`Atlas Skill ${manifest.version}\n\natlas-skill          Open the interactive project installer\natlas-skill install [--agent agents|claude] [--dir PATH] [--dry-run]\natlas-skill update  [--agent ...] [--dir PATH] [--dry-run]\natlas-skill doctor  [--agent ...] [--dir PATH]\natlas-skill list\natlas-skill --version\n\nChoose Agents or Claude interactively, or pass --agent for automation. codex and antigravity remain aliases for agents. The shared path works only with tools that support .agents/skills discovery. Project-local by default. Updates back up the complete old folder. No network requests, npm installs or agent configuration edits are performed by this CLI.`);
  else if (config.command === 'version') console.log(manifest.version);
  else if (config.command === 'list') console.log(JSON.stringify({ version: manifest.version, skills: manifest.skills, projectDestinations: agents }, null, 2));
  else {
    await chooseTarget(config);
    const target = destination(config);
    if (config.command === 'doctor') {
      const { record, changes } = inspect(target);
      console.log(JSON.stringify({ status: changes.length ? 'modified' : 'valid', target, installedVersion: record.version, installerVersion: manifest.version, checkedFiles: Object.keys(record.files).length, changes, agentActivation: 'not-tested' }, null, 2));
      if (changes.length) process.exitCode = 1;
    } else install(config, target);
  }
} catch (error) { console.error(error.message); process.exitCode = error.exitCode || 1; }
