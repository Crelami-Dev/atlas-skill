#!/usr/bin/env node
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { createInterface } from 'node:readline/promises';
import { fileURLToPath } from 'node:url';
import { packageFiles } from '../scripts/package-files.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const source = path.resolve(__dirname, '..');
const metadataName = '.atlas-install.json';
const { manifest, files } = packageFiles(source);

const PROJECT_TARGETS = {
  agents: { skillsRoot: '.agents/skills', mainName: 'atlas-frontend-design', rulesDir: '.agents/rules', ruleAdapter: 'adapters/antigravity-rule.md', ruleFile: 'atlas-frontend-gate.md' },
  codex: { skillsRoot: '.agents/skills', mainName: 'atlas-frontend-design', rulesDir: '.', ruleAdapter: 'adapters/AGENTS.atlas.md', ruleFile: 'AGENTS.atlas.md' },
  antigravity: { skillsRoot: '.agents/skills', mainName: 'atlas-frontend-design', rulesDir: '.agents/rules', ruleAdapter: 'adapters/antigravity-rule.md', ruleFile: 'atlas-frontend-gate.md' },
  claude: { skillsRoot: '.claude/skills', mainName: 'atlas-frontend-design', rulesDir: null, ruleAdapter: null, ruleFile: null },
  cursor: { skillsRoot: '.cursor/skills', mainName: 'atlas-frontend-design', rulesDir: '.cursor/rules', ruleAdapter: 'adapters/cursor-rule.mdc', ruleFile: 'atlas-frontend-gate.mdc' },
  windsurf: { skillsRoot: '.windsurf/skills', mainName: 'atlas-frontend-design', rulesDir: '.windsurf/rules', ruleAdapter: 'adapters/antigravity-rule.md', ruleFile: 'atlas-frontend-gate.md' },
  cline: { skillsRoot: '.clinerules/skills', mainName: 'atlas-frontend-design', rulesDir: '.clinerules', ruleAdapter: 'adapters/antigravity-rule.md', ruleFile: 'atlas-frontend-gate.md' },
  copilot: { skillsRoot: '.github/skills', mainName: 'atlas-frontend-design', rulesDir: '.github', ruleAdapter: 'adapters/AGENTS.atlas.md', ruleFile: 'copilot-instructions.atlas.md' }
};

const GLOBAL_TARGETS = {
  agents: { skillsRoot: '.agents/skills', mainName: 'atlas-frontend-design', rulesDir: '.agents/rules', ruleAdapter: 'adapters/antigravity-rule.md', ruleFile: 'atlas-frontend-gate.md' },
  codex: { skillsRoot: '.agents/skills', mainName: 'atlas-frontend-design', rulesDir: '.agents', ruleAdapter: 'adapters/AGENTS.atlas.md', ruleFile: 'AGENTS.atlas.md' },
  antigravity: { skillsRoot: '.gemini/config/skills', mainName: 'atlas-frontend-design', rulesDir: '.gemini/config/rules', ruleAdapter: 'adapters/antigravity-rule.md', ruleFile: 'atlas-frontend-gate.md' },
  claude: { skillsRoot: '.claude/skills', mainName: 'atlas-frontend-design', rulesDir: null, ruleAdapter: null, ruleFile: null },
  cursor: { skillsRoot: '.cursor/skills', mainName: 'atlas-frontend-design', rulesDir: '.cursor/rules', ruleAdapter: 'adapters/cursor-rule.mdc', ruleFile: 'atlas-frontend-gate.mdc' }
};

const ALL_AGENTS = [...Object.keys(PROJECT_TARGETS), 'all'];
const fail = (message, code = 1) => { throw Object.assign(new Error(message), { exitCode: code }); };
const inside = (root, target) => { const rel = path.relative(root, target); return rel === '' || (!rel.startsWith('..') && !path.isAbsolute(rel)); };
const hash = file => crypto.createHash('sha256').update(fs.readFileSync(file)).digest('hex');

function readQaManifest() {
  const qaPath = path.join(source, 'suites/project-qa/package-manifest.json');
  return fs.existsSync(qaPath) ? JSON.parse(fs.readFileSync(qaPath, 'utf8')) : { skills: [] };
}

function options(argv) {
  const result = {
    command: 'install',
    agent: null,
    dir: null,
    global: false,
    withRules: false,
    exposeSubskills: false,
    withQa: false,
    dryRun: false
  };
  let commandSet = false;
  for (let i = 0; i < argv.length; i++) {
    const arg = argv[i];
    if (arg === '--help' || arg === '-h') return { ...result, command: 'help' };
    if (arg === '--version' || arg === '-v') return { ...result, command: 'version' };
    if (arg === '--dry-run') { result.dryRun = true; continue; }
    if (arg === '--global') { result.global = true; continue; }
    if (arg === '--with-rules') { result.withRules = true; continue; }
    if (arg === '--expose-subskills') { result.exposeSubskills = true; continue; }
    if (arg === '--with-qa') { result.withQa = true; continue; }
    if (arg === '--agent' || arg === '--dir') {
      if (!argv[i + 1] || argv[i + 1].startsWith('--')) fail(`Missing value for ${arg}`, 2);
      result[arg.slice(2)] = argv[++i];
      continue;
    }
    if (arg.startsWith('-') || commandSet) fail(`Unexpected argument: ${arg}`, 2);
    result.command = arg;
    commandSet = true;
  }
  if (!['help', 'version', 'install', 'update', 'doctor', 'list'].includes(result.command)) fail(`Unknown command: ${result.command}`, 2);
  if (result.agent !== null && !ALL_AGENTS.includes(result.agent)) {
    fail(`Unknown agent: ${result.agent}. Use one of: ${ALL_AGENTS.join(', ')}.`, 2);
  }
  if (result.dir && result.agent === 'all') fail('Cannot combine --dir with --agent all.', 2);
  return result;
}

async function chooseTarget(config) {
  if (config.agent) return;
  if (config.dir) { config.agent = 'agents'; return; }
  if (!process.stdin.isTTY || !process.stdout.isTTY) {
    fail('Choose a target with --agent <agents|antigravity|codex|claude|cursor|windsurf|cline|copilot|all> or --dir <PATH> when running without an interactive terminal.', 2);
  }
  const prompt = createInterface({ input: process.stdin, output: process.stdout });
  let answered = false;
  prompt.on('SIGINT', () => { prompt.close(); });
  prompt.on('close', () => { if (!answered) process.exitCode = 130; });
  console.log(`\nAtlas Skill v${manifest.version} — ${config.global ? 'global' : 'project-local'} ${config.command}\nBase: ${config.global ? os.homedir() : process.cwd()}\n\n  1. Antigravity / Codex / Agents — .agents/skills/atlas-frontend-design\n  2. Claude Code                  — .claude/skills/atlas-frontend-design\n  3. Cursor                       — .cursor/skills/atlas-frontend-design\n  4. All Major Agents             — .agents + .claude + .cursor\n\nCtrl+C to cancel.\n`);
  try {
    while (!config.agent) {
      const answer = (await prompt.question('Choose [1-4]: ')).trim().toLowerCase();
      if (['1', 'agents', 'antigravity', 'codex'].includes(answer)) config.agent = 'antigravity';
      else if (['2', 'claude'].includes(answer)) config.agent = 'claude';
      else if (['3', 'cursor'].includes(answer)) config.agent = 'cursor';
      else if (['4', 'all'].includes(answer)) config.agent = 'all';
      else console.log('Enter 1, 2, 3, or 4.');
    }
    if (config.command === 'install' || config.command === 'update') {
      const qaAnswer = (await prompt.question('Include Project QA & Security Suite (--with-qa)? [Y/n]: ')).trim().toLowerCase();
      if (qaAnswer === '' || qaAnswer === 'y' || qaAnswer === 'yes') config.withQa = true;
      const rulesAnswer = (await prompt.question('Install native rule gates (--with-rules)? [Y/n]: ')).trim().toLowerCase();
      if (rulesAnswer === '' || rulesAnswer === 'y' || rulesAnswer === 'yes') config.withRules = true;
    }
    answered = true;
  } catch { fail('Installation cancelled. No files were changed.', 130); }
  finally { prompt.close(); }
}

function resolveTargets(config) {
  if (config.dir) {
    return [{ agent: config.agent || 'custom', target: path.resolve(config.dir), rulesDir: null, ruleAdapter: null, ruleFile: null }];
  }
  const baseDir = config.global ? os.homedir() : process.cwd();
  const table = config.global ? GLOBAL_TARGETS : PROJECT_TARGETS;
  const agentList = config.agent === 'all'
    ? (config.global ? ['agents', 'antigravity', 'claude'] : ['agents', 'claude', 'cursor'])
    : [config.agent];

  const resolved = [];
  const seenTargets = new Set();
  for (const agentName of agentList) {
    const spec = table[agentName];
    if (!spec) fail(`Agent "${agentName}" does not have a standard --global path. Use --dir <PATH> instead.`, 2);
    const target = path.resolve(baseDir, spec.skillsRoot, spec.mainName);
    if (seenTargets.has(target)) continue;
    seenTargets.add(target);
    resolved.push({
      agent: agentName,
      target,
      rulesDir: spec.rulesDir ? path.resolve(baseDir, spec.rulesDir) : null,
      ruleAdapter: spec.ruleAdapter,
      ruleFile: spec.ruleFile
    });
  }
  return resolved;
}

function validateDestinationPath(target) {
  const cwd = path.resolve(process.cwd());
  if (target === path.parse(target).root || target === cwd || target === os.homedir() || inside(source, target) || inside(target, source) || path.basename(target) === '.git') {
    fail(`Choose a dedicated skill directory outside the installer source and project/home root: ${target}`);
  }
  for (let current = target; current !== path.dirname(current); current = path.dirname(current)) {
    if (fs.existsSync(current) && fs.lstatSync(current).isSymbolicLink()) {
      fail(`Symlink/junction destination is not supported: ${current}`);
    }
  }
}

function inspect(target) {
  if (!fs.existsSync(path.join(target, metadataName))) fail(`No managed Atlas installation at ${target}. Choose an empty directory for install; unmanaged folders are never overwritten.`);
  const record = JSON.parse(fs.readFileSync(path.join(target, metadataName), 'utf8'));
  if (record.name !== 'atlas-skill' || typeof record.version !== 'string' || !record.files || typeof record.files !== 'object' || Array.isArray(record.files) || !Object.keys(record.files).length) {
    fail('Invalid Atlas installation metadata.');
  }
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

function copyTree(srcDir, dstDir) {
  fs.mkdirSync(dstDir, { recursive: true });
  for (const entry of fs.readdirSync(srcDir, { withFileTypes: true })) {
    if (entry.name === '__pycache__' || entry.name.endsWith('.pyc')) continue;
    const s = path.join(srcDir, entry.name);
    const d = path.join(dstDir, entry.name);
    if (entry.isDirectory()) copyTree(s, d);
    else fs.copyFileSync(s, d);
  }
}

function installExtras(config, entry) {
  const skillsParent = path.dirname(entry.target);
  const exposed = [];
  const qaSkills = [];
  const rulesWritten = [];

  if (config.exposeSubskills) {
    for (const skill of manifest.skills) {
      if (skill.path === 'SKILL.md') continue;
      const srcSkillDir = path.dirname(path.join(source, skill.path));
      const dstSkillDir = path.join(skillsParent, skill.name);
      copyTree(srcSkillDir, dstSkillDir);
      exposed.push(dstSkillDir);
    }
  }

  if (config.withQa) {
    const qaManifest = readQaManifest();
    for (const skill of qaManifest.skills) {
      const srcSkillDir = path.dirname(path.join(source, skill.path));
      const dstSkillDir = path.join(skillsParent, skill.name);
      copyTree(srcSkillDir, dstSkillDir);
      qaSkills.push(dstSkillDir);
    }
  }

  if (config.withRules && entry.rulesDir && entry.ruleAdapter && entry.ruleFile) {
    fs.mkdirSync(entry.rulesDir, { recursive: true });
    const dstRule = path.join(entry.rulesDir, entry.ruleFile);
    if (!fs.existsSync(dstRule)) {
      fs.copyFileSync(path.join(source, entry.ruleAdapter), dstRule);
      rulesWritten.push(dstRule);
    }
    if (config.withQa) {
      const qaRuleSrc = path.join(source, 'suites/project-qa/rules/qa-security-gate.md');
      const qaRuleDst = path.join(entry.rulesDir, 'qa-security-gate.md');
      if (fs.existsSync(qaRuleSrc) && !fs.existsSync(qaRuleDst) && entry.ruleFile.endsWith('.md')) {
        fs.copyFileSync(qaRuleSrc, qaRuleDst);
        rulesWritten.push(qaRuleDst);
      }
    }
  }

  return { exposed, qaSkills, rulesWritten };
}

function installOne(config, entry) {
  const target = entry.target;
  validateDestinationPath(target);
  const exists = fs.existsSync(target);
  if (config.command === 'install' && exists) fail(`Destination exists: ${target}. Use update for a managed installation or choose an empty --dir.`);
  if (config.command === 'update' && !exists) fail(`No installation at ${target}. Run install first.`);
  const prior = exists ? inspect(target) : null;

  if (config.dryRun) {
    return {
      action: config.command,
      dryRun: true,
      agent: entry.agent,
      target,
      version: manifest.version,
      files: files.length,
      backupRequired: exists,
      withRules: config.withRules,
      exposeSubskills: config.exposeSubskills,
      withQa: config.withQa
    };
  }

  const hashes = Object.fromEntries(files.map(relative => [relative, hash(path.join(source, relative))]));
  if (prior && !prior.changes.length && JSON.stringify(prior.record.files) === JSON.stringify(hashes) && !config.withQa && !config.exposeSubskills && !config.withRules) {
    return { status: 'current', agent: entry.agent, target, version: manifest.version };
  }

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
    fs.writeFileSync(path.join(stage, metadataName), JSON.stringify({
      name: 'atlas-skill',
      version: manifest.version,
      agent: entry.agent,
      installedAt: new Date().toISOString(),
      source: 'https://github.com/Crelami-Dev/atlas-skill',
      options: { global: config.global, withRules: config.withRules, exposeSubskills: config.exposeSubskills, withQa: config.withQa },
      files: hashes
    }, null, 2));

    if (exists) {
      const backupBase = config.global ? os.homedir() : process.cwd();
      const backupRoot = path.resolve(backupBase, '.atlas-skill-backups');
      backup = path.join(backupRoot, `atlas-${Date.now()}-${crypto.randomUUID()}`);
      if (inside(target, backup) || inside(backup, target) || !inside(backupRoot, backup)) fail('Backup must be outside the installation.');
      if (fs.existsSync(backupRoot) && fs.lstatSync(backupRoot).isSymbolicLink()) fail('Backup root must not be a symlink.');
      fs.mkdirSync(backupRoot, { recursive: true });
      fs.renameSync(target, backup);
    }
    fs.renameSync(stage, target);
    const extras = installExtras(config, entry);
    return {
      status: exists ? 'updated' : 'installed',
      version: manifest.version,
      agent: entry.agent,
      target,
      files: files.length,
      backup,
      priorModifiedFiles: prior?.changes || [],
      ...extras
    };
  } catch (error) {
    if (backup && fs.existsSync(backup) && !fs.existsSync(target)) fs.renameSync(backup, target);
    error.message += `\nUncommitted staging, if present: ${stage}`;
    throw error;
  }
}

try {
  const config = options(process.argv.slice(2));
  if (config.command === 'help') {
    console.log(`Atlas Skill v${manifest.version}

Usage:
  npx --yes github:Crelami-Dev/atlas-skill [command] [options]
  atlas-skill [command] [options]

Commands:
  install   Install Atlas into target agent folder(s) (default)
  update    Atomically update an existing managed installation (creates backup)
  doctor    Verify SHA-256 integrity of installed files
  list      Show available frontend & QA skills and agent destinations
  --version Print version (${manifest.version})
  --help    Show this help message

Options:
  --agent <name>       agents, antigravity, codex, claude, cursor, windsurf, cline, copilot, all
  --dir <PATH>         Install into a custom dedicated skill directory
  --global             Install into user home directory (~/.agents, ~/.gemini/config, ~/.claude, etc.)
  --with-rules         Write native rule gate files without overwriting existing user rules
  --expose-subskills   Expose sibling sub-skill folders for direct /slash-command discovery
  --with-qa            Include Project QA & Security Suite (bug-hunter, security-auditor, fix-and-verify + qa-security-gate)
  --dry-run            Validate source package and print install plan without writing files`);
  } else if (config.command === 'version') {
    console.log(manifest.version);
  } else if (config.command === 'list') {
    const qaManifest = readQaManifest();
    console.log(JSON.stringify({
      version: manifest.version,
      skills: manifest.skills,
      qaSkills: qaManifest.skills,
      projectDestinations: Object.fromEntries(Object.entries(PROJECT_TARGETS).map(([k, v]) => [k, `${v.skillsRoot}/${v.mainName}`])),
      globalDestinations: Object.fromEntries(Object.entries(GLOBAL_TARGETS).map(([k, v]) => [k, `${v.skillsRoot}/${v.mainName}`]))
    }, null, 2));
  } else {
    await chooseTarget(config);
    const targets = resolveTargets(config);
    if (config.command === 'doctor') {
      const results = [];
      for (const entry of targets) {
        validateDestinationPath(entry.target);
        const { record, changes } = inspect(entry.target);
        if (changes.length) process.exitCode = 1;
        results.push({
          status: changes.length ? 'modified' : 'valid',
          agent: entry.agent,
          target: entry.target,
          installedVersion: record.version,
          installerVersion: manifest.version,
          nodeVersion: process.version,
          checkedFiles: Object.keys(record.files).length,
          changes,
          agentActivation: 'not-tested'
        });
      }
      console.log(JSON.stringify(results.length === 1 ? results[0] : { results }, null, 2));
    } else {
      validateSource();
      const results = targets.map(entry => installOne(config, entry));
      console.log(JSON.stringify(results.length === 1 ? results[0] : { results }, null, 2));
      if (!config.dryRun) {
        console.log('Restart/reload the agent if needed, then explicitly ask it to use Atlas. Installation does not prove agent activation.');
      }
    }
  }
} catch (error) {
  console.error(error.message);
  process.exitCode = error.exitCode || 1;
}
