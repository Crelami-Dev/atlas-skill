#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.argv[2] || '.');
const tokenFlag = process.argv.indexOf('--tokens');
const brownfieldTokenCandidates = [
  'design-tokens.css',
  'src/styles/design-tokens.css',
  'styles/design-tokens.css',
  'src/styles/tokens.css',
  'src/app/globals.css',
  'app/globals.css',
  'src/index.css',
  'styles/globals.css'
];
let tokens = path.resolve(tokenFlag >= 0 ? process.argv[tokenFlag + 1] : path.join(root, 'design-tokens.css'));
if (tokenFlag < 0 && !fs.existsSync(tokens)) {
  for (const relCandidate of brownfieldTokenCandidates) {
    const absCandidate = path.join(root, relCandidate);
    if (fs.existsSync(absCandidate) && /--[\w-]+\s*:/.test(fs.readFileSync(absCandidate, 'utf8'))) {
      tokens = absCandidate;
      break;
    }
  }
}
const configPath = path.join(root, '.atlas-token-allowlist.json');
const allow = fs.existsSync(configPath) ? JSON.parse(fs.readFileSync(configPath, 'utf8')).files || [] : [];
const styleExtensions = new Set(['.css', '.html', '.jsx', '.tsx', '.vue', '.svelte', '.astro']);
const ignoreDirs = new Set(['node_modules', '.git', '.agents', '.claude', '.cursor', '.windsurf', '.clinerules', '.atlas-skill-backups', 'dist', 'build', '.next', 'out', 'maintenance']);
const files = [];

function walk(dir) {
  if (!fs.existsSync(dir)) return;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ignoreDirs.has(entry.name) || entry.isSymbolicLink()) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full);
    else if (entry.isFile() && styleExtensions.has(path.extname(entry.name).toLowerCase())) files.push(full);
  }
}

function stripCommentsPreserveLength(str) {
  return str
    .replace(/\/\*[\s\S]*?\*\//g, (s) => s.replace(/[^\n]/g, ' '))
    .replace(/<!--[\s\S]*?-->/g, (s) => s.replace(/[^\n]/g, ' '));
}

if (!fs.existsSync(tokens)) {
  console.error(`FAIL: token file not found: ${tokens}\nFIX: Copy templates/design-tokens.css into the project and customize palette, typography scale, and motion tokens before writing UI code.`);
  process.exit(1);
}

walk(root);
const errors = [];

function isSafeScaleValue(rawVal) {
  const val = rawVal.replace(/!important/gi, '').trim();
  if (!val) return true;
  if (/^(?:calc|clamp|min|max)\([\s\S]*var\(--[\w-]+\)[\s\S]*\)$/i.test(val)) return true;
  const parts = val.split(/\s+/);
  const safeAtom = /^(?:0(?:px|rem|em|%|vh|vw|dvh|svh|lvh|ch)?|auto|inherit|initial|unset|revert|none|normal|50%|100%|fit-content|max-content|min-content|\d+(?:\.\d+)?ch|(?:100|50)(?:vh|vw|dvh|svh|lvh)|-?[12]px|\d+(?:\.\d+)?fr|var\(--[\w-]+(?:\s*,\s*[^)]+)?\))$/i;
  return parts.every((p) => safeAtom.test(p));
}

for (const file of files) {
  const rel = path.relative(root, file).replaceAll('\\', '/');
  if (path.resolve(file) === tokens || allow.includes(rel)) continue;
  const rawText = fs.readFileSync(file, 'utf8');
  const text = stripCommentsPreserveLength(rawText);
  const lineOf = (index) => rawText.slice(0, index).split('\n').length;
  const ext = path.extname(file).toLowerCase();
  const colorScanText = ext === '.css'
    ? text
    : text.replace(/<svg\b[^>]*>[\s\S]*?<\/svg>/gi, (s) => s.replace(/[^\n]/g, ' '));

  // Detect raw hex / rgb / hsl colors while ignoring URL anchors like href="#section", SVG refs url(#id), and <svg> artwork
  for (const match of colorScanText.matchAll(/(?<![\w-]|href=["']|url\()#[0-9a-f]{3,8}\b|\b(?:rgb|hsl|oklch)a?\(\s*(?!var\()[^)]*\)/gi)) {
    const start = Math.max(0, match.index - 16);
    const prefix = colorScanText.slice(start, match.index);
    if (/(?:href|xlink:href|src|fill=["']url\(|stroke=["']url\()=["']?[^"']*$/i.test(prefix)) continue;
    errors.push(`${rel}:${lineOf(match.index)} raw color '${match[0]}' -> use a CSS custom property from design-tokens.css (e.g., var(--color-accent))`);
  }

  // Inspect CSS declarations in .css files, <style> blocks, AND inline style="..." attributes
  const cssBlocks = [];
  if (ext === '.css') {
    cssBlocks.push({ content: text, offset: 0 });
  } else {
    for (const m of text.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/gi)) {
      cssBlocks.push({ content: m[1], offset: m.index + m[0].indexOf(m[1]) });
    }
    for (const m of text.matchAll(/\bstyle\s*=\s*(["'])([\s\S]*?)\1/gi)) {
      cssBlocks.push({ content: m[2], offset: m.index + m[0].indexOf(m[2]) });
    }
  }

  for (const block of cssBlocks) {
    for (const match of block.content.matchAll(/(?<![\w-])(font-size|margin(?:-(?:top|right|bottom|left|inline|block))?|padding(?:-(?:top|right|bottom|left|inline|block))?|gap|row-gap|column-gap|border-radius)\s*:\s*([^;}{"']+)/gi)) {
      const value = match[2].trim();
      if (!isSafeScaleValue(value)) {
        errors.push(`${rel}:${lineOf(block.offset + match.index)} raw scale value '${match[1]}: ${value}' -> use var(--space-*), var(--text-*), or var(--radius-*)`);
      }
    }
  }
}

const MONO_FONT_RE = /\b(?:mono|monospace|ui-monospace|jetbrains\s*mono|fira\s*code|sfmono-regular|menlo|consolas|courier|source\s*code\s*pro|ibm\s*plex\s*mono|inconsolata)\b/i;
const tokenText = stripCommentsPreserveLength(fs.readFileSync(tokens, 'utf8'));
const proportionalFamilies = new Set();
const monoFamilies = new Set();
for (const m of tokenText.matchAll(/(--font-[\w-]+)\s*:\s*([^;]+)/g)) {
  const tokenName = m[1];
  const primary = m[2].split(',')[0].trim().replace(/^['"]|['"]$/g, '');
  if (!primary) continue;
  if (/^--font-(?:mono|code|monospace)$/i.test(tokenName) || MONO_FONT_RE.test(primary)) {
    monoFamilies.add(primary.toLowerCase());
  } else {
    proportionalFamilies.add(primary.toLowerCase());
  }
}
if (proportionalFamilies.size > 2) {
  errors.push(`${path.relative(root, tokens)}: found more than 2 proportional font families (${[...proportionalFamilies].join(', ')}) -> limit to max 2 proportional roles (display & sans/body)`);
}
if (monoFamilies.size > 1) {
  errors.push(`${path.relative(root, tokens)}: found more than 1 monospace font family (${[...monoFamilies].join(', ')}) -> limit to max 1 monospace role`);
}

if (errors.length) {
  console.error(`FAIL: ${errors.length} design token violation(s) found:\n${errors.slice(0, 40).join('\n')}`);
  process.exitCode = 1;
} else {
  console.log('PASS: token usage valid');
}
