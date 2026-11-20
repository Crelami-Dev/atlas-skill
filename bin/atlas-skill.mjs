#!/usr/bin/env node
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import crypto from 'node:crypto';
import { spawnSync } from 'node:child_process';
import { createInterface } from 'node:readline/promises';
import readline from 'node:readline';
import { fileURLToPath } from 'node:url';
import { packageFiles } from '../scripts/package-files.mjs';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const source = path.resolve(__dirname, '..');
const metadataName = '.atlas-install.json';
const { manifest, files } = packageFiles(source);

const PROJECT_TARGETS = {
  agents: { skillsRoot: '.agents/skills', mainName: 'atlas-skill', rulesDir: '.agents/rules', ruleAdapter: 'adapters/antigravity-rule.md', ruleFile: 'atlas-frontend-gate.md' },
  codex: { skillsRoot: '.agents/skills', mainName: 'atlas-skill', rulesDir: '.', ruleAdapter: 'adapters/AGENTS.atlas.md', ruleFile: 'AGENTS.atlas.md' },
  antigravity: { skillsRoot: '.agents/skills', mainName: 'atlas-skill', rulesDir: '.agents/rules', ruleAdapter: 'adapters/antigravity-rule.md', ruleFile: 'atlas-frontend-gate.md' },
  claude: { skillsRoot: '.claude/skills', mainName: 'atlas-skill', rulesDir: null, ruleAdapter: null, ruleFile: null },
  cursor: { skillsRoot: '.cursor/skills', mainName: 'atlas-skill', rulesDir: '.cursor/rules', ruleAdapter: 'adapters/cursor-rule.mdc', ruleFile: 'atlas-frontend-gate.mdc' },
  windsurf: { skillsRoot: '.windsurf/skills', mainName: 'atlas-skill', rulesDir: '.windsurf/rules', ruleAdapter: 'adapters/antigravity-rule.md', ruleFile: 'atlas-frontend-gate.md' },
  cline: { skillsRoot: '.clinerules/skills', mainName: 'atlas-skill', rulesDir: '.clinerules', ruleAdapter: 'adapters/antigravity-rule.md', ruleFile: 'atlas-frontend-gate.md' },
  copilot: { skillsRoot: '.github/skills', mainName: 'atlas-skill', rulesDir: '.github', ruleAdapter: 'adapters/AGENTS.atlas.md', ruleFile: 'copilot-instructions.atlas.md' }
};

const GLOBAL_TARGETS = {
  agents: { skillsRoot: '.agents/skills', mainName: 'atlas-skill', rulesDir: '.agents/rules', ruleAdapter: 'adapters/antigravity-rule.md', ruleFile: 'atlas-frontend-gate.md' },
  codex: { skillsRoot: '.agents/skills', mainName: 'atlas-skill', rulesDir: '.agents', ruleAdapter: 'adapters/AGENTS.atlas.md', ruleFile: 'AGENTS.atlas.md' },
  antigravity: { skillsRoot: '.gemini/config/skills', mainName: 'atlas-skill', rulesDir: '.gemini/config/rules', ruleAdapter: 'adapters/antigravity-rule.md', ruleFile: 'atlas-frontend-gate.md' },
  claude: { skillsRoot: '.claude/skills', mainName: 'atlas-skill', rulesDir: null, ruleAdapter: null, ruleFile: null },
  cursor: { skillsRoot: '.cursor/skills', mainName: 'atlas-skill', rulesDir: '.cursor/rules', ruleAdapter: 'adapters/cursor-rule.mdc', ruleFile: 'atlas-frontend-gate.mdc' }
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

const AGENT_MENU_ITEMS = [
  {
    id: 'claude',
    name: 'Claude Code',
    badge: 'RECOMMENDED',
    dest: '.claude/skills',
    desc: 'Pasang ke Claude Code (.claude/skills/{atlas-skill,atlas-frontend,atlas-bug-hunter})'
  },
  {
    id: 'antigravity',
    name: 'Antigravity / Codex',
    badge: 'STANDALONE',
    dest: '.agents/skills',
    desc: 'Pasang ke Antigravity & OpenAI Codex (.agents/skills/{atlas-skill,atlas-frontend,atlas-bug-hunter})'
  },
  {
    id: 'cursor',
    name: 'Cursor IDE',
    badge: 'IDE',
    dest: '.cursor/skills',
    desc: 'Pasang ke Cursor AI (.cursor/skills/{atlas-skill,atlas-frontend,atlas-bug-hunter})'
  },
  {
    id: 'windsurf',
    name: 'Windsurf (Codeium)',
    badge: 'IDE',
    dest: '.windsurf/skills',
    desc: 'Pasang ke Windsurf IDE (.windsurf/skills/{atlas-skill,atlas-frontend,atlas-bug-hunter})'
  },
  {
    id: 'cline',
    name: 'Cline / Roo Code',
    badge: 'EXT',
    dest: '.clinerules/skills',
    desc: 'Pasang ke Cline & Roo Code (.clinerules/skills/{atlas-skill,atlas-frontend,atlas-bug-hunter})'
  },
  {
    id: 'copilot',
    name: 'GitHub Copilot',
    badge: 'WORKSPACE',
    dest: '.github/skills',
    desc: 'Pasang ke GitHub Copilot instructions & skills'
  },
  {
    id: 'all',
    name: 'Semua Agent Sekaligus',
    badge: 'ALL-IN-ONE',
    dest: '.claude + .agents + .cursor',
    desc: 'Pasang otomatis ke Claude Code, Antigravity/Codex, dan Cursor IDE'
  }
];

const PROFILE_MENU_ITEMS = [
  {
    id: 'standard',
    name: 'Standar (Direkomendasikan)',
    badge: 'RECOMMENDED',
    dest: '3 Core Skills + Native Rule Gates',
    desc: 'Memasang atlas-skill, atlas-frontend, atlas-bug-hunter & rule gates',
    withRules: true,
    withQa: false
  },
  {
    id: 'minimal',
    name: 'Minimal (Skills Saja)',
    badge: 'LEAN',
    dest: '3 Core Skills tanpa rule files',
    desc: 'Hanya memasang skills ke folder agent tanpa menambahkan file rule',
    withRules: false,
    withQa: false
  },
  {
    id: 'full',
    name: 'Lengkap (Full Suite + QA & Security)',
    badge: 'ENTERPRISE',
    desc: 'Termasuk Project QA & Security Python suite (CVE audit, inventory, DOM scanner)',
    withRules: true,
    withQa: true
  }
];

function interactiveMenu({ banner, promptText, items, defaultIndex = 0 }) {
  return new Promise((resolve) => {
    let selectedIndex = defaultIndex;
    let linesRendered = 0;

    const render = () => {
      if (linesRendered > 0) {
        process.stdout.write(`\x1b[${linesRendered}A\x1b[0J`);
      }

      const out = [];
      if (banner) out.push(banner);
      out.push(promptText);
      out.push('');

      items.forEach((item, idx) => {
        const isSelected = idx === selectedIndex;
        const pointer = isSelected ? '\x1b[36m\x1b[1m❯\x1b[0m' : ' ';
        const bullet = isSelected ? '\x1b[36m\x1b[1m●\x1b[0m' : '\x1b[90m○\x1b[0m';
        const name = isSelected ? `\x1b[36m\x1b[1m${item.name}\x1b[0m` : `\x1b[37m${item.name}\x1b[0m`;
        const dest = `\x1b[90m[${item.dest}]\x1b[0m`;
        const badge = item.badge ? ` \x1b[33m\x1b[1m${item.badge}\x1b[0m` : '';

        out.push(`  ${pointer} ${bullet} ${name.padEnd(30)} ${dest.padEnd(28)}${badge}`);
        if (item.desc) {
          const descColor = isSelected ? '\x1b[36m' : '\x1b[90m';
          out.push(`       ${descColor}${item.desc}\x1b[0m`);
        }
      });

      out.push('');
      out.push(`  \x1b[90m[↑/↓ / j/k] Geser Pilihan   [Enter] Pilih   [Ctrl+C] Batal\x1b[0m`);

      const text = out.join('\n');
      linesRendered = text.split('\n').length;
      process.stdout.write(text + '\n');
    };

    readline.emitKeypressEvents(process.stdin);
    if (process.stdin.isTTY) {
      process.stdin.setRawMode(true);
    }
    process.stdin.resume();
    process.stdout.write('\x1b[?25l');

    render();

    const cleanup = () => {
      process.stdout.write('\x1b[?25h');
      process.stdin.removeListener('keypress', onKeypress);
      if (process.stdin.isTTY) {
        process.stdin.setRawMode(false);
      }
      process.stdin.pause();
    };

    const onKeypress = (str, key) => {
      if (!key) return;

      if ((key.ctrl && key.name === 'c') || key.name === 'escape') {
        cleanup();
        console.log('\n\x1b[33mInstalasi dibatalkan.\x1b[0m\n');
        process.exit(130);
      }

      if (key.name === 'up' || key.name === 'k') {
        selectedIndex = (selectedIndex - 1 + items.length) % items.length;
        render();
      } else if (key.name === 'down' || key.name === 'j') {
        selectedIndex = (selectedIndex + 1) % items.length;
        render();
      } else if (key.name === 'return' || key.name === 'enter') {
        cleanup();
        resolve(items[selectedIndex]);
      } else if (key.name && /^[1-9]$/.test(key.name)) {
        const num = parseInt(key.name, 10) - 1;
        if (num < items.length) {
          selectedIndex = num;
          render();
        }
      }
    };

    process.stdin.on('keypress', onKeypress);
  });
}

async function chooseTarget(config) {
  if (config.agent) return;
  if (config.dir) { config.agent = 'agents'; return; }
  if (!process.stdin.isTTY || !process.stdout.isTTY) {
    fail('Choose a target with --agent <agents|antigravity|codex|claude|cursor|windsurf|cline|copilot|all> or --dir <PATH> when running without an interactive terminal.', 2);
  }

  const cwdPath = config.global ? os.homedir() : process.cwd();
  const banner = [
    '',
    '\x1b[36m\x1b[1m  ╭─────────────────────────────────────────────────────────────╮\x1b[0m',
    `\x1b[36m\x1b[1m  │   ▲ T L ▲ S   F R O N T E N D   E N G I N E   v${manifest.version.padEnd(8)}   │\x1b[0m`,
    '\x1b[36m\x1b[1m  │   Design System, Gates & Anime.js v4 Scenes Installer       │\x1b[0m',
    '\x1b[36m\x1b[1m  ╰─────────────────────────────────────────────────────────────╯\x1b[0m',
    `  \x1b[37m📁 Target Workspace:\x1b[0m \x1b[32m${cwdPath}\x1b[0m`,
    ''
  ].join('\n');

  try {
    const selectedAgent = await interactiveMenu({
      banner,
      promptText: '\x1b[1mPilih Agent Target yang ingin dipasang:\x1b[0m',
      items: AGENT_MENU_ITEMS,
      defaultIndex: 0
    });

    config.agent = selectedAgent.id;
    console.log(`\n\x1b[32m✔ Target terpilih:\x1b[0m \x1b[1m${selectedAgent.name}\x1b[0m \x1b[90m(${selectedAgent.dest})\x1b[0m\n`);

    if (config.command === 'install' || config.command === 'update') {
      const selectedProfile = await interactiveMenu({
        banner: null,
        promptText: '\x1b[1mPilih Profil Instalasi:\x1b[0m',
        items: PROFILE_MENU_ITEMS,
        defaultIndex: 0
      });

      config.withRules = selectedProfile.withRules;
      config.withQa = selectedProfile.withQa;
      console.log(`\n\x1b[32m✔ Profil terpilih:\x1b[0m \x1b[1m${selectedProfile.name}\x1b[0m \x1b[90m(${selectedProfile.dest})\x1b[0m\n`);
    }
  } catch {
    fail('Installation cancelled. No files were changed.', 130);
  }
}

function resolveTargets(config) {
  if (config.dir) {
    const resolvedDir = path.resolve(config.dir);
    return [{ agent: config.agent || 'custom', baseDir: path.dirname(resolvedDir), target: resolvedDir, rulesDir: null, ruleAdapter: null, ruleFile: null }];
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
      baseDir,
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
  if (record.extraFiles && typeof record.extraFiles === 'object' && !Array.isArray(record.extraFiles)) {
    const baseRoot = typeof record.baseDir === 'string' ? path.resolve(record.baseDir) : path.dirname(path.dirname(target));
    for (const [relative, expected] of Object.entries(record.extraFiles)) {
      const file = path.resolve(baseRoot, relative);
      if (!inside(baseRoot, file) || file === baseRoot) fail('Installation metadata contains an invalid extra file path.');
      if (!fs.existsSync(file) || !fs.statSync(file).isFile() || hash(file) !== expected) changes.push(relative);
    }
  }
  return { record, changes };
}

function detectRuntime() {
  let pythonCmd = null;
  let pythonVersion = null;
  let selenium = false;
  for (const candidate of process.platform === 'win32' ? ['python', 'python3'] : ['python3', 'python']) {
    const probe = spawnSync(candidate, ['--version'], { encoding: 'utf8' });
    const text = ((probe.stdout || '') + (probe.stderr || '')).trim();
    if (probe.status === 0 && /Python 3\./i.test(text)) {
      pythonCmd = candidate;
      pythonVersion = text;
      const selProbe = spawnSync(candidate, ['-c', 'import importlib.util, sys; sys.exit(0 if importlib.util.find_spec("selenium") else 1)'], { encoding: 'utf8' });
      selenium = selProbe.status === 0;
      break;
    }
  }
  return { node: process.version, python: pythonVersion ? `${pythonCmd} (${pythonVersion})` : null, selenium };
}

function validateSource() {
  const result = spawnSync(process.execPath, [path.join(source, 'scripts/validate-package.mjs')], { encoding: 'utf8' });
  if (result.status !== 0) fail(`Source package failed validation:\n${result.stdout}${result.stderr}`);
}

function copyTree(srcDir, dstDir, collected = []) {
  fs.mkdirSync(dstDir, { recursive: true });
  for (const entry of fs.readdirSync(srcDir, { withFileTypes: true })) {
    if (entry.name === '__pycache__' || entry.name.endsWith('.pyc')) continue;
    const s = path.join(srcDir, entry.name);
    const d = path.join(dstDir, entry.name);
    if (entry.isDirectory()) copyTree(s, d, collected);
    else {
      fs.copyFileSync(s, d);
      collected.push(d);
    }
  }
  return collected;
}

function installExtras(config, entry, backup) {
  const skillsParent = path.dirname(entry.target);
  const exposed = [];
  const qaSkills = [];
  const rulesWritten = [];
  const extraFiles = {};
  const recordFile = (absPath) => {
    const rel = path.relative(entry.baseDir, absPath).replaceAll('\\', '/');
    if (rel && !rel.startsWith('..') && !path.isAbsolute(rel)) {
      extraFiles[rel] = hash(absPath);
    }
  };
  const backupExistingDir = (dstDir, group, name) => {
    if (backup && fs.existsSync(dstDir)) {
      const bakDst = path.join(backup, '.atlas-extras-backup', group, name);
      copyTree(dstDir, bakDst);
      fs.rmSync(dstDir, { recursive: true, force: true });
    }
  };

  // Always install the 2 sibling top-level entrypoints (atlas-frontend & atlas-bug-hunter) for standard agent installs
  if (!config.dir) {
    for (const skill of manifest.skills) {
      if (skill.path === 'SKILL.md' || !skill.topLevel) continue;
      const srcSkillDir = path.dirname(path.join(source, skill.path));
      const dstSkillDir = path.join(skillsParent, skill.name);
      backupExistingDir(dstSkillDir, 'top-level-skills', skill.name);
      const written = copyTree(srcSkillDir, dstSkillDir);
      for (const f of written) recordFile(f);
      exposed.push(dstSkillDir);
    }
  }

  if (config.exposeSubskills) {
    for (const skill of manifest.skills) {
      if (skill.path === 'SKILL.md' || skill.topLevel) continue;
      const srcSkillDir = path.dirname(path.join(source, skill.path));
      const dstSkillDir = path.join(skillsParent, skill.name);
      backupExistingDir(dstSkillDir, 'skills', skill.name);
      const written = copyTree(srcSkillDir, dstSkillDir);
      for (const f of written) recordFile(f);
      exposed.push(dstSkillDir);
    }
  }

  if (config.withQa) {
    const qaManifest = readQaManifest();
    for (const skill of qaManifest.skills) {
      const srcSkillDir = path.dirname(path.join(source, skill.path));
      const dstSkillDir = path.join(skillsParent, skill.name);
      backupExistingDir(dstSkillDir, 'qa-skills', skill.name);
      const written = copyTree(srcSkillDir, dstSkillDir);
      for (const f of written) recordFile(f);
      qaSkills.push(dstSkillDir);
    }
  }

  if (config.withRules && entry.rulesDir && entry.ruleAdapter && entry.ruleFile) {
    fs.mkdirSync(entry.rulesDir, { recursive: true });
    const dstRule = path.join(entry.rulesDir, entry.ruleFile);
    if (!fs.existsSync(dstRule)) {
      fs.copyFileSync(path.join(source, entry.ruleAdapter), dstRule);
      rulesWritten.push(dstRule);
      recordFile(dstRule);
    }
    if (config.withQa) {
      const qaRuleSrc = path.join(source, 'suites/project-qa/rules/qa-security-gate.md');
      const qaRuleDst = path.join(entry.rulesDir, 'qa-security-gate.md');
      if (fs.existsSync(qaRuleSrc) && !fs.existsSync(qaRuleDst) && entry.ruleFile.endsWith('.md')) {
        fs.copyFileSync(qaRuleSrc, qaRuleDst);
        rulesWritten.push(qaRuleDst);
        recordFile(qaRuleDst);
      }
    }
  }

  return { exposed, qaSkills, rulesWritten, extraFiles };
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
    const extras = installExtras(config, entry, backup);
    if (Object.keys(extras.extraFiles).length > 0) {
      const metaPath = path.join(target, metadataName);
      const metaObj = JSON.parse(fs.readFileSync(metaPath, 'utf8'));
      metaObj.baseDir = entry.baseDir;
      metaObj.extraFiles = extras.extraFiles;
      fs.writeFileSync(metaPath, JSON.stringify(metaObj, null, 2));
    }
    return {
      status: exists ? 'updated' : 'installed',
      version: manifest.version,
      agent: entry.agent,
      target,
      files: files.length,
      backup,
      priorModifiedFiles: prior?.changes || [],
      exposed: extras.exposed,
      qaSkills: extras.qaSkills,
      rulesWritten: extras.rulesWritten
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
      topLevelSkills: manifest.topLevelSkills || ['atlas-skill', 'atlas-frontend', 'atlas-bug-hunter'],
      skills: manifest.skills,
      qaSkills: qaManifest.skills,
      projectDestinations: Object.fromEntries(Object.entries(PROJECT_TARGETS).map(([k, v]) => [k, `${v.skillsRoot}/${v.mainName}`])),
      globalDestinations: Object.fromEntries(Object.entries(GLOBAL_TARGETS).map(([k, v]) => [k, `${v.skillsRoot}/${v.mainName}`]))
    }, null, 2));
  } else {
    await chooseTarget(config);
    const targets = resolveTargets(config);
    if (config.command === 'doctor') {
      const runtime = detectRuntime();
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
          runtime,
          checkedFiles: Object.keys(record.files).length + Object.keys(record.extraFiles || {}).length,
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
