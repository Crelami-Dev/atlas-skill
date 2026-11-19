#!/usr/bin/env node
/**
 * Atlas v6.0 — Gate 5: Visual Proof, Surface Cadence, & Anti-Wireframe Scanner
 * Catches visually dry or broken markup before browser screenshot inspection:
 *   1. Hard-fails large crude geometric wireframe SVGs (polygons/rects + >=4 text labels)
 *   2. Hard-fails generic hill/mountain + sun SVG silhouettes (generic-hill-sun-svg)
 *   3. Hard-fails leaked raw Markdown backticks (`code`) inside HTML text elements
 *   4. Checks for real visual proof elements (<img src="...">, <picture>, <canvas>, <video>, data-viz <svg>,
 *      [data-atlas-proof], or [data-photo-placeholder]) ignoring comments and <style>/<script> contents.
 *      Supports opt-out via <!-- atlas-proof: not-applicable -->.
 *   5. Checks multi-surface polarity tokens/classes.
 * By default, missing-visual-proof and flat-surface-monotony are warnings; pass --strict to make them errors.
 */
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
if (args.includes('--help') || args.includes('-h')) {
  console.log('Usage: node check-visual-proof.mjs [project-root] [--strict]\nOpt-out comment for pure docs/typography pages: <!-- atlas-proof: not-applicable -->');
  process.exit(0);
}

const strictMode = args.includes('--strict');
const positional = args.filter((a) => !a.startsWith('--'));
const root = path.resolve(positional[0] || '.');

const uiExts = new Set(['.html', '.jsx', '.tsx', '.vue', '.svelte', '.astro']);
const styleExts = new Set(['.css', '.html', '.jsx', '.tsx', '.svelte', '.vue', '.astro']);
const ignoreDirs = new Set(['node_modules', '.git', '.agents', '.claude', '.cursor', '.windsurf', '.clinerules', 'dist', 'build', '.next', 'out', 'maintenance']);

const uiFiles = [];
const styleFiles = [];

function walk(dir) {
  if (!fs.existsSync(dir)) return;
  for (const item of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ignoreDirs.has(item.name) || item.isSymbolicLink()) continue;
    const full = path.join(dir, item.name);
    if (item.isDirectory()) walk(full);
    else if (item.isFile()) {
      const ext = path.extname(item.name).toLowerCase();
      if (uiExts.has(ext)) uiFiles.push(full);
      if (styleExts.has(ext)) styleFiles.push(full);
    }
  }
}

function stripCommentsAndScripts(raw) {
  return raw
    .replace(/<!--[\s\S]*?-->/g, (s) => ' '.repeat(s.length))
    .replace(/\{\/\*[\s\S]*?\*\/\}/g, (s) => ' '.repeat(s.length))
    .replace(/<(?:script|style)\b[^>]*>[\s\S]*?<\/(?:script|style)>/gi, (s) => ' '.repeat(s.length));
}

walk(root);
const findings = [];
let hasVisualCenterpiece = false;
let hasOptOut = false;
const distinctSurfaceTokensUsed = new Set();
const styledFormControls = new Set();
const usedFormControls = new Map(); // control -> { file, line }

for (const file of styleFiles) {
  const raw = fs.readFileSync(file, 'utf8');
  const cleaned = raw.replace(/\/\*[\s\S]*?\*\//g, '').replace(/<!--[\s\S]*?-->/g, '');
  for (const m of cleaned.matchAll(/var\((--color-(?:bg|surface|surface-elevated|surface-sage|surface-tint|blueprint|blueprint-surface)|--spec-[\w-]+)\)/g)) {
    distinctSurfaceTokensUsed.add(m[1]);
  }
  const cssOnly = path.extname(file).toLowerCase() === '.css'
    ? cleaned
    : [...cleaned.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/gi)].map((m) => m[1]).join('\n');
  if (/(?:^|[},\s])(?:select|\.[\w-]*select[\w-]*)\s*(?:[,{]|\[)/i.test(cssOnly)) styledFormControls.add('select');
  if (/(?:^|[},\s])(?:input(?:\s*:\s*not\([^)]*\)|\s*\[[^\]]+\])?|\.[\w-]*input[\w-]*|\.[\w-]*field[\w-]*)\s*(?:[,{])/i.test(cssOnly)) styledFormControls.add('input');
  if (/(?:^|[},\s])(?:button|\.[\w-]*btn[\w-]*)\s*(?:[,{:])/i.test(cssOnly)) styledFormControls.add('button');
}

for (const file of uiFiles) {
  const rel = path.relative(root, file).replaceAll('\\', '/');
  const text = fs.readFileSync(file, 'utf8');
  const lineOf = (idx) => text.slice(0, Math.max(0, idx)).split('\n').length;

  if (/<!--\s*atlas-proof:\s*not-applicable\s*-->/i.test(text) || /\{\/\*\s*atlas-proof:\s*not-applicable\s*\*\/\}/i.test(text)) {
    hasOptOut = true;
  }

  const cleaned = stripCommentsAndScripts(text);

  for (const ctrl of ['select', 'input', 'button']) {
    const tagRe = new RegExp(`<${ctrl}\\b([^>]*)>`, 'gi');
    for (const m of cleaned.matchAll(tagRe)) {
      const attrs = m[1] || '';
      if (/\btype\s*=\s*["']hidden["']/i.test(attrs)) continue;
      if (/\bstyle\s*=\s*["'][^"']+["']/i.test(attrs)) {
        styledFormControls.add(ctrl);
      } else if (!usedFormControls.has(ctrl)) {
        usedFormControls.set(ctrl, { file: rel, line: lineOf(m.index) });
      }
    }
  }

  if (/<img\b[^>]*\bsrc\s*=\s*(?:["']\s*[^"'\s]+["']|\{[^}]+\})[^>]*>/i.test(cleaned)) {
    hasVisualCenterpiece = true;
  }
  if (/<(?:picture|canvas|video)\b[^>]*>/i.test(cleaned)) {
    hasVisualCenterpiece = true;
  }
  if (/<[a-z][a-z0-9-]*\b[^>]*\b(?:data-atlas-proof|data-photo-placeholder|data-photo-slot)(?:\s*=\s*(?:["'][^"']*["']|[^\s>]+))?[^>]*>/i.test(cleaned)) {
    hasVisualCenterpiece = true;
  }

  // Hard-fail leaked developer photo placeholder instructions in UI markup/text
  const PHOTO_PLACEHOLDER_LEAK_RE = /(?:\b(?:ganti(?:\s+dengan)?\s+(?:foto|gambar)(?:\s+(?:asli|ini))?|replace\s+(?:this\s+)?(?:with\s+)?(?:real\s+|actual\s+)?(?:photo|image)|(?:insert|upload)\s+(?:real\s+)?(?:photo|image)(?:\s+here)?|(?:taruh|masukkan|pasang)\s+(?:foto|gambar)\s+(?:di\s+sini|disini)|(?:foto|gambar)\s+\S+(?:\s+\S+)?\s+di\s+sini|menunggu\s+foto(?:\s+dokumentasi|\s+asli|\s+klien)?|foto\s+menyusul|foto\s+akan\s+(?:ditambahkan|menyusul)|awaiting\s+(?:real\s+|client\s+)?photo(?:graphy|s)?|(?:photo|image)\s+(?:coming\s+soon|tbd)|(?:slot\s+foto|photo\s+slot)\s*(?:#?\d+|hero|utama|banner|produk|menu|galeri)|(?:image|photo|foto)\s+placeholder|placeholder\s+(?:image|photo|foto)|photo-replace-badge|photo-slot-subject|data\s+klien\s+diperlukan)\b|\[\s*(?:ganti\s+dengan\s+foto|replace\s+with\s+photo|insert\s+image|placeholder|data\s+klien\s+diperlukan|(?:foto|image)\s*:[^\]]+|foto[^\]]{0,40}di\s+sini)[^\]]*\])/gi;
  for (const m of cleaned.matchAll(PHOTO_PLACEHOLDER_LEAK_RE)) {
    findings.push({
      level: 'error',
      id: 'leaked-photo-placeholder-ui',
      file: rel,
      line: lineOf(m.index),
      message: `Instruksi placeholder foto/developer ('${m[0]}') bocor ke UI pengunjung. Gunakan pelat spesimen editorial spesifik-domain dengan atribut senyap data-photo-slot.`
    });
  }
  for (const m of cleaned.matchAll(/<figure\b[^>]*\b(?:data-photo-placeholder|data-photo-slot)\b[^>]*>(?:(?!(?:<\/figure>|<section\b|<form\b))[\s\S])*?\bSubjek:\s+[^\n<]{10,}/gi)) {
    findings.push({
      level: 'error',
      id: 'leaked-photo-placeholder-ui',
      file: rel,
      line: lineOf(m.index),
      message: `Catatan brief internal ('Subjek: ...') bocor ke dalam slot media UI. Gunakan caption editorial nyata untuk pengunjung.`
    });
  }

  // Inspect <svg> elements in cleaned markup
  for (const m of cleaned.matchAll(/<svg\b([^>]*)>([\s\S]*?)<\/svg>/gi)) {
    const attrs = m[1] || '';
    const inner = m[2] || '';
    const vbMatch = attrs.match(/viewBox=["']\s*[\d.-]+\s+[\d.-]+\s+([\d.]+)\s+([\d.]+)/i);
    const heightAttrMatch = attrs.match(/\bheight=["']?\s*(\d+)/i);
    const svgHeight = vbMatch ? Number(vbMatch[2]) : (heightAttrMatch ? Number(heightAttrMatch[1]) : 0);
    const shapeCount = (inner.match(/<(?:polygon|rect)\b/gi) || []).length;
    const textCount = (inner.match(/<text\b/gi) || []).length;
    const isCrudeWireframe = (svgHeight >= 180 || (!vbMatch && !heightAttrMatch)) && shapeCount >= 4 && textCount >= 4;

    const hasCircle = /<circle\b/i.test(inner);
    const hasClosedHillPath = /<(?:path|polygon)\b[^>]*\bd=["'][^"']*(?:[QTCS]|L\s*\d+\s+\d+\s+L)[^"']*Z["']/i.test(inner);
    const isGenericHillSun = hasCircle && hasClosedHillPath && shapeCount <= 3 && textCount === 0;

    if (isGenericHillSun) {
      findings.push({
        level: 'error',
        id: 'generic-hill-sun-svg',
        file: rel,
        line: lineOf(m.index),
        message: 'Siluet SVG generik (bukit/gelombang + lingkaran matahari) terdeteksi. Gunakan foto asli atau bingkai placeholder editorial terdesain ([data-photo-placeholder]) sesuai references/imagery.md.'
      });
    } else if (isCrudeWireframe) {
      findings.push({
        level: 'error',
        id: 'crude-wireframe-svg',
        file: rel,
        line: lineOf(m.index),
        message: 'Diagram SVG kotak/poligon kaku terdeteksi. Ganti wireframe SVG kaku dengan komponen UI interaktif nyata atau fotografi asli.'
      });
    } else if (
      /\b(?:data-viz|data-chart|data-atlas-proof)\b/i.test(attrs) ||
      (/<(?:path|polyline|circle|g)\b/i.test(inner) && (/<(?:path|polyline)\b/gi.exec(inner) !== null))
    ) {
      hasVisualCenterpiece = true;
    }
  }

  // Hard-fail visible debug state switcher (Populated/Loading/Empty/Error) without hidden + ?debug=1 guard
  const hasDebugParamGuard = /\?debug=1\b|get\(\s*['"]debug['"]\s*\)\s*===\s*['"]1['"]|searchParams\.has\(\s*['"]debug['"]\s*\)/i.test(text);
  for (const m of cleaned.matchAll(/<select\b([^>]*)>([\s\S]*?)<\/select>/gi)) {
    const selectAttrs = m[1] || '';
    const selectInner = m[2] || '';
    if (/\bhidden\b/i.test(selectAttrs) && hasDebugParamGuard) continue;
    if (
      /<option\b[^>]*>[^<]*\bPopulated\b[^<]*<\/option>/i.test(selectInner) &&
      /<option\b[^>]*>[^<]*\b(?:Loading|Empty|Error|Zero[-\s]?Match)\b[^<]*<\/option>/i.test(selectInner)
    ) {
      findings.push({
        level: 'error',
        id: 'leaked-debug-state-switcher',
        file: rel,
        line: lineOf(m.index),
        message: 'Pemilih state debug (Populated/Loading/Empty/Error) tampil di UI produksi. Sembunyikan dengan atribut hidden di balik ?debug=1.'
      });
    }
  }

  // Hard-fail leaked raw Markdown backticks inside HTML headings/buttons/paragraphs
  const strippedCodeAndPre = cleaned.replace(/<(?:pre|code)\b[^>]*>[\s\S]*?<\/(?:pre|code)>/gi, (s) => ' '.repeat(s.length));
  for (const m of strippedCodeAndPre.matchAll(/<(?:h1|h2|h3|h4|p|button|a|li|span|strong)\b[^>]*>[^<]*`[^`\n]+`[^<]*<\/(?:h1|h2|h3|h4|p|button|a|li|span|strong)>/gi)) {
    findings.push({
      level: 'error',
      id: 'leaked-markdown-backticks',
      file: rel,
      line: lineOf(m.index),
      message: 'Tanda backtick Markdown mentah (`...`) bocor di dalam elemen HTML. Gunakan elemen <code>...</code> yang rapi.'
    });
  }
}

const softLevel = strictMode ? 'error' : 'warn';

if (uiFiles.length > 0 && !hasVisualCenterpiece && !hasOptOut) {
  findings.push({
    level: softLevel,
    id: 'missing-visual-proof',
    file: path.relative(root, uiFiles[0]).replaceAll('\\', '/'),
    line: 1,
    message: 'Halaman belum memiliki panggung bukti visual nyata (<img>, <picture>, <canvas>, <video>, <svg data-viz>, [data-atlas-proof], atau [data-photo-placeholder]). Tambahkan elemen visual nyata atau gunakan <!-- atlas-proof: not-applicable --> untuk halaman dokumentasi/tipografi murni.'
  });
}

if (uiFiles.length > 0 && distinctSurfaceTokensUsed.size < 3 && !hasOptOut) {
  findings.push({
    level: softLevel,
    id: 'flat-surface-monotony',
    file: path.relative(root, uiFiles[0]).replaceAll('\\', '/'),
    line: 1,
    message: `Hanya ${distinctSurfaceTokensUsed.size} peran warna permukaan yang dipakai. Gunakan minimal 3 variasi permukaan tenang (mis. base, elevated, dark-anchor/soft-tint) agar ritme halaman hidup.`
  });
}

const unstyledList = [...usedFormControls.keys()].filter((c) => !styledFormControls.has(c));
if (unstyledList.length > 0 && !hasOptOut) {
  const firstHit = usedFormControls.get(unstyledList[0]);
  findings.push({
    level: 'warn',
    id: 'unstyled-form-controls',
    file: firstHit.file,
    line: firstHit.line,
    message: `Kontrol form (${unstyledList.join(', ')}) dipakai tanpa aturan CSS yang men-style elemen tersebut. Gunakan aturan komponen form dari templates/design-tokens.css (appearance: none, border, focus-visible ring, state disabled/error).`
  });
}

const errors = findings.filter((f) => f.level === 'error').length;
const warnings = findings.filter((f) => f.level === 'warn').length;
console.log(JSON.stringify({ root, strict: strictMode, optOut: hasOptOut, uiFilesScanned: uiFiles.length, distinctSurfaces: [...distinctSurfaceTokensUsed], errors, warnings, findings }, null, 2));
console.log(`${errors ? 'FAIL' : 'PASS'}: check-visual-proof (${errors} error, ${warnings} warning)`);
if (errors > 0) process.exitCode = 1;
