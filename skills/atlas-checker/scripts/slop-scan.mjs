#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.argv[2] || '.');
const configFile = path.join(root, '.atlas-slop.json');
const config = fs.existsSync(configFile) ? JSON.parse(fs.readFileSync(configFile, 'utf8')) : { disabled: {} };
const disabled = config.disabled || {};
const extensions = new Set(['.html', '.css', '.jsx', '.tsx', '.js', '.ts', '.vue', '.svelte', '.astro']);
const ignoreDirs = new Set(['node_modules', '.git', '.agents', '.claude', '.cursor', '.windsurf', '.clinerules', 'dist', 'build', '.next', 'out', 'maintenance']);
const findings = [];

function report(id, level, file, index, text, advice) {
  if (disabled[id]) {
    if (!String(disabled[id]).trim()) throw new Error(`Disabled rule ${id} needs a reason in .atlas-slop.json`);
    return;
  }
  findings.push({
    id,
    level,
    file: path.relative(root, file).replaceAll('\\', '/'),
    line: text.slice(0, Math.max(0, index)).split('\n').length,
    advice,
  });
}

function walk(dir, output = []) {
  if (!fs.existsSync(dir)) return output;
  for (const item of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ignoreDirs.has(item.name) || item.isSymbolicLink()) continue;
    const full = path.join(dir, item.name);
    if (item.isDirectory()) walk(full, output);
    else if (item.isFile() && extensions.has(path.extname(item.name).toLowerCase())) output.push(full);
  }
  return output;
}

const BUZZWORD_REGEX = /\b(solusi komprehensif|di era digital|transformasi digital menyeluruh|inovasi tanpa batas|unlock the power of|revolutionize your|supercharge your workflow|seamlessly integrate|elevate your digital|next-generation platform|empowering modern teams)\b/gi;
const PLACEHOLDER_REGEX = /\b(lorem ipsum|your company|feature one|feature two|acme corp|john doe|jane doe|123 main st(?:reet)?|info@example\.com|test@example\.com)\b/gi;

for (const file of walk(root)) {
  const ext = path.extname(file).toLowerCase();
  const text = fs.readFileSync(file, 'utf8');
  const noComments = text
    .replace(/\/\*[\s\S]*?\*\//g, (s) => s.replace(/[^\n]/g, ' '))
    .replace(/<!--[\s\S]*?-->/g, (s) => s.replace(/[^\n]/g, ' '));

  // 1. Hard-fail placeholder text
  for (const m of noComments.matchAll(PLACEHOLDER_REGEX)) {
    report('placeholder-copy', 'error', file, m.index, text, `Ganti teks placeholder '${m[0]}' dengan konten nyata dari brief atau penanda celah yang jujur.`);
  }

  // 2. Hard-fail Anime.js v3 hallucination in UI/motion code
  for (const m of noComments.matchAll(/import\s+(?:anime|\*\s+as\s+\w+)\s+from\s+['"]animejs['"]|\banime\s*\(\s*\{\s*targets\s*:|\banime\.(?:default|timeline|stagger)\s*\(/g)) {
    report('animejs-v3-hallucination', 'error', file, m.index, text, "Jangan gunakan sintaks Anime.js v3. Gunakan named imports Anime.js v4: import { animate, createTimeline, createScope, stagger } from 'animejs'.");
  }

  if (['.html', '.css', '.jsx', '.tsx', '.vue', '.svelte', '.astro'].includes(ext)) {
    // 2b. Hard-fail leaked internal Atlas skill jargon in visible UI text
    const strippedScriptsStyles = noComments.replace(/<(?:script|style)\b[^>]*>[\s\S]*?<\/(?:script|style)>/gi, (s) => ' '.repeat(s.length));
    for (const m of strippedScriptsStyles.matchAll(/\b(?:ARCHETYPE:\s*[A-Z0-9-]+|SPLIT-SCREEN APPLICATION CALCULATOR|DEALT\s+DIRECTION|ATLAS-BRIEF|Zero fabricated testimonials|Tanpa ulasan bintang rekayasa|DISPATCH\s+v\d+)\b/gi)) {
      report('leaked-skill-jargon', 'error', file, m.index, text, `Jangan bocorkan istilah internal skill (${m[0]}) ke UI pengunjung akhir; ganti dengan teks domain nyata.`);
    }

    // 3. AI copywriting clichés
    for (const m of noComments.matchAll(BUZZWORD_REGEX)) {
      report('ai-buzzword-copy', 'warn', file, m.index, text, `Ganti klise pemasaran AI '${m[0]}' dengan kalimat faktual, objek konkret, dan kata kerja langsung.`);
    }

    // 4. Emoji used inside interactive controls or headings
    for (const m of noComments.matchAll(/<(?:button|a|h1|h2|h3|nav)\b[^>]*>[^<]*[\u{1F300}-\u{1FAFF}\u{2728}\u{1F680}]/gu)) {
      report('emoji-ui', 'warn', file, m.index, text, 'Hindari emoji sebagai ikon UI pada tombol/judul/navigasi; gunakan teks jelas atau ikon SVG terarah.');
    }

    // 5. Generic purple-blue AI gradient (CSS + Tailwind classes)
    for (const m of noComments.matchAll(/(?:linear|radial)-gradient\([^)]*(?:#(?:6[0-9a-f]|7[0-9a-f]|8[0-9a-f])[0-9a-f]{4}|purple|indigo|violet)[^)]*(?:#(?:0[0-9a-f]|1[0-9a-f]|2[0-9a-f]|3[0-9a-f])[0-9a-f]{4}|blue|cyan)/gi)) {
      report('generic-purple-blue-gradient', 'warn', file, m.index, text, 'Gradien ungu-biru generik terdeteksi; pastikan berasal dari identitas brand asli, bukan template bawaan AI.');
    }
    for (const m of noComments.matchAll(/\bfrom-(?:indigo|purple|violet)-[4567]00\b[^\n"']*\bto-(?:blue|cyan|pink|fuchsia)-[4567]00\b/g)) {
      report('generic-purple-blue-gradient', 'warn', file, m.index, text, 'Kelas gradien Tailwind ungu-biru generik terdeteksi; ganti dengan permukaan solid terstruktur atau palet brand nyata.');
    }

    // 6. Gradient clipped headline spam
    const clipMatches = [...noComments.matchAll(/background-clip\s*:\s*text|\bbg-clip-text\b/gi)];
    if (clipMatches.length >= 2) {
      report('gradient-text-spam', 'warn', file, clipMatches[1].index, text, 'Terlalu banyak teks bergradien (bg-clip-text); bangun hierarki lewat skala tipografi, kontras, dan posisi.');
    }

    // 7. Unmotivated glassmorphism spam
    const blurMatches = [...noComments.matchAll(/backdrop-filter\s*:\s*blur|\bbackdrop-blur(?:-(?:sm|md|lg|xl|2xl|3xl))?\b/gi)];
    if (blurMatches.length > 2) {
      report('unmotivated-glass', 'warn', file, blurMatches[0].index, text, 'Penggunaan blur/glassmorphism berulang; batasi hanya pada lapisan overlay fungsional (mis. header lengket di atas media).');
    }

    // 8. Font proliferation: count distinct font family declarations (not total rules referencing var(--font-sans))
    const familyMatches = [...noComments.matchAll(/font-family\s*:\s*([^;}{"']+)/gi)];
    const distinctFamilies = new Set();
    let thirdFamilyIndex = 0;
    for (const fm of familyMatches) {
      const rawFam = fm[1].trim();
      if (/^(?:inherit|initial|unset|revert)$/i.test(rawFam)) continue;
      const primaryTokenOrName = rawFam.startsWith('var(')
        ? rawFam.match(/var\(\s*(--[\w-]+)/)?.[1] || rawFam
        : rawFam.split(',')[0].trim().replace(/^['"]|['"]$/g, '').toLowerCase();
      if (!distinctFamilies.has(primaryTokenOrName)) {
        distinctFamilies.add(primaryTokenOrName);
        if (distinctFamilies.size === 3) thirdFamilyIndex = fm.index;
      }
    }
    if (distinctFamilies.size > 2) {
      report('font-proliferation', 'error', file, thirdFamilyIndex, text, `Ditemukan ${distinctFamilies.size} keluarga huruf berbeda (${[...distinctFamilies].join(', ')}); batasi maksimal 2 keluarga huruf (display & teks isi).`);
    }

    
    // 10. Leaked debug state-switcher control in user-facing UI (Populated / Loading / Empty / Error <select> or button group without hidden + ?debug=1)
    const hasDebugParamGuard = /\?debug=1\b|get\(\s*['"]debug['"]\s*\)\s*===\s*['"]1['"]|searchParams\.has\(\s*['"]debug['"]\s*\)/i.test(noComments);
    for (const m of noComments.matchAll(/<select\b([^>]*)>([\s\S]*?)<\/select>/gi)) {
      const selectAttrs = m[1] || '';
      const selectInner = m[2] || '';
      const isHidden = /\bhidden\b/i.test(selectAttrs);
      if (isHidden && hasDebugParamGuard) continue;
      if (
        /<option\b[^>]*>[^<]*\bPopulated\b[^<]*<\/option>/i.test(selectInner) &&
        /<option\b[^>]*>[^<]*\b(?:Loading|Empty|Error|Zero[-\s]?Match)\b[^<]*<\/option>/i.test(selectInner)
      ) {
        report('leaked-debug-state-switcher', 'error', file, m.index, text, 'Pemilih state debug (Populated/Loading/Empty/Error) tidak boleh tampil di UI produksi. Hapus atau sembunyikan dengan atribut hidden di balik ?debug=1.');
      }
    }
    const debugBtnMatches = [...noComments.matchAll(/<button\b([^>]*)>\s*(?:Populated|Loading|Empty(?:\s+State)?|Error(?:\s+State)?)\s*<\/button>/gi)];
    if (debugBtnMatches.length >= 3) {
      const allHidden = debugBtnMatches.every((bm) => /\bhidden\b/i.test(bm[1] || ''));
      if (!(allHidden && hasDebugParamGuard)) {
        report('leaked-debug-state-switcher', 'error', file, debugBtnMatches[0].index, text, 'Grup tombol pemilih state debug (Populated/Loading/Empty/Error) terlihat di UI produksi. Sembunyikan di balik ?debug=1.');
      }
    }

    // 9. Repeated uniform card grids
    const cards = (noComments.match(/(?:class|className)=["'][^"']*(?:card|feature-box|bento-item)[^"']*["']/gi) || []).length;
    if (cards >= 3) {
      report('repeated-card-grid', 'warn', file, Math.max(0, noComments.search(/card|feature-box|bento-item/i)), text, 'Periksa apakah kartu berulang memiliki fungsi keputusan berbeda atau sekadar mengisi grid 3-kolom generik.');
    }
  }
}

const reportData = {
  root,
  findings,
  summary: {
    error: findings.filter((f) => f.level === 'error').length,
    warn: findings.filter((f) => f.level === 'warn').length,
  },
};
console.log(JSON.stringify(reportData, null, 2));
console.log(`${reportData.summary.error ? 'FAIL' : 'PASS'}: ${reportData.summary.error} error, ${reportData.summary.warn} warning`);
if (reportData.summary.error) process.exitCode = 1;
