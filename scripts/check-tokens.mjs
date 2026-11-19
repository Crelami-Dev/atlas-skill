#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.argv[2] || '.');
const tokenFlag = process.argv.indexOf('--tokens');
const tokens = path.resolve(tokenFlag >= 0 ? process.argv[tokenFlag + 1] : path.join(root, 'design-tokens.css'));
const configPath = path.join(root, '.atlas-token-allowlist.json');
const allow = fs.existsSync(configPath) ? JSON.parse(fs.readFileSync(configPath, 'utf8')).files || [] : [];
const styleExtensions = new Set(['.css', '.html', '.jsx', '.tsx', '.vue', '.svelte', '.astro']);
const ignoreDirs = new Set(['node_modules', '.git', '.agents', '.claude', '.cursor', '.windsurf', '.clinerules', 'dist', 'build', '.next', 'out', 'maintenance']);
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
  console.error(`FAIL: token file tidak ditemukan: ${tokens}\nFIX: Salin templates/design-tokens.css ke proyek dan sesuaikan palet, skala tipografi, serta token motion sebelum mulai coding UI.`);
  process.exit(1);
}

walk(root);
const errors = [];

function isSafeScaleValue(rawVal) {
  const val = rawVal.replace(/!important/gi, '').trim();
  if (!val) return true;
  if (/^(?:calc|clamp|min|max)\([\s\S]*var\(--[\w-]+\)[\s\S]*\)$/i.test(val)) return true;
  const parts = val.split(/\s+/);
  const safeAtom = /^(?:0(?:px|rem|em|%|vh|vw|dvh|ch)?|auto|inherit|initial|unset|revert|none|normal|50%|100%|fit-content|max-content|min-content|var\(--[\w-]+(?:\s*,\s*[^)]+)?\))$/i;
  return parts.every((p) => safeAtom.test(p));
}

for (const file of files) {
  const rel = path.relative(root, file).replaceAll('\\', '/');
  if (path.resolve(file) === tokens || allow.includes(rel)) continue;
  const rawText = fs.readFileSync(file, 'utf8');
  const text = stripCommentsPreserveLength(rawText);
  const lineOf = (index) => rawText.slice(0, index).split('\n').length;

  // Detect raw hex / rgb / hsl colors while ignoring URL anchors like href="#section" or SVG refs url(#id)
  for (const match of text.matchAll(/(?<![\w-]|href=["']|url\()#[0-9a-f]{3,8}\b|\b(?:rgb|hsl|oklch)a?\(\s*(?!var\()[^)]*\)/gi)) {
    const start = Math.max(0, match.index - 16);
    const prefix = text.slice(start, match.index);
    if (/(?:href|xlink:href|src|fill=["']url\(|stroke=["']url\()=["']?[^"']*$/i.test(prefix)) continue;
    errors.push(`${rel}:${lineOf(match.index)} raw color '${match[0]}' -> gunakan CSS custom property dari design-tokens.css (mis. var(--color-accent))`);
  }

  // Inspect CSS declarations in .css files, <style> blocks, AND inline style="..." attributes
  const ext = path.extname(file).toLowerCase();
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
        errors.push(`${rel}:${lineOf(block.offset + match.index)} raw scale value '${match[1]}: ${value}' -> gunakan var(--space-*), var(--text-*), atau var(--radius-*)`);
      }
    }
  }
}

const tokenText = stripCommentsPreserveLength(fs.readFileSync(tokens, 'utf8'));
const fontFamilies = [...tokenText.matchAll(/--font-[\w-]+\s*:\s*([^;]+)/g)]
  .map((m) => m[1].split(',')[0].trim().replace(/^['"]|['"]$/g, ''))
  .filter(Boolean);
if (new Set(fontFamilies).size > 2) {
  errors.push(`${path.relative(root, tokens)}: ditemukan lebih dari 2 font family (${[...new Set(fontFamilies)].join(', ')}) -> batasi maksimal 2 peran (display & sans/body)`);
}

if (errors.length) {
  console.error(`FAIL: ${errors.length} pelanggaran design token ditemukan:\n${errors.slice(0, 40).join('\n')}`);
  process.exitCode = 1;
} else {
  console.log('PASS: token usage valid');
}
