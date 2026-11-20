#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.argv[2] || '.');
const configFile = path.join(root, '.atlas-slop.json');
const config = fs.existsSync(configFile) ? JSON.parse(fs.readFileSync(configFile, 'utf8')) : { disabled: {} };
const disabled = config.disabled || {};
const extensions = new Set(['.html', '.css', '.jsx', '.tsx', '.js', '.ts', '.vue', '.svelte', '.astro']);
const ignoreDirs = new Set(['node_modules', '.git', '.agents', '.claude', '.cursor', '.windsurf', '.clinerules', '.atlas-skill-backups', 'dist', 'build', '.next', 'out', 'maintenance']);
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
const PHOTO_PLACEHOLDER_LEAK_REGEX = /(?:\b(?:ganti(?:\s+dengan)?\s+(?:foto|gambar)(?:\s+(?:asli|ini))?|replace\s+(?:this\s+)?(?:with\s+)?(?:real\s+|actual\s+)?(?:photo|image)|(?:insert|upload)\s+(?:real\s+)?(?:photo|image)(?:\s+here)?|(?:taruh|masukkan|pasang)\s+(?:foto|gambar)\s+(?:di\s+sini|disini)|(?:foto|gambar)\s+\S+(?:\s+\S+)?\s+di\s+sini|menunggu\s+foto(?:\s+dokumentasi|\s+asli|\s+klien)?|foto\s+menyusul|foto\s+akan\s+(?:ditambahkan|menyusul)|awaiting\s+(?:real\s+|client\s+)?photo(?:graphy|s)?|(?:photo|image)\s+(?:coming\s+soon|tbd)|(?:slot\s+foto|photo\s+slot)\s*(?:#?\d+|hero|utama|banner|produk|menu|galeri)|(?:image|photo|foto)\s+placeholder|placeholder\s+(?:image|photo|foto)|photo-replace-badge|photo-slot-subject|data\s+klien\s+diperlukan)\b|\[\s*(?:ganti\s+dengan\s+foto|replace\s+with\s+photo|insert\s+image|placeholder|data\s+klien\s+diperlukan|(?:foto|image)\s*:[^\]]+|foto[^\]]{0,40}di\s+sini)[^\]]*\])/gi;

for (const file of walk(root)) {
  const ext = path.extname(file).toLowerCase();
  const text = fs.readFileSync(file, 'utf8');
  const noComments = text
    .replace(/\/\*[\s\S]*?\*\//g, (s) => s.replace(/[^\n]/g, ' '))
    .replace(/<!--[\s\S]*?-->/g, (s) => s.replace(/[^\n]/g, ' '));

  // 1. Hard-fail placeholder text
  for (const m of noComments.matchAll(PLACEHOLDER_REGEX)) {
    report('placeholder-copy', 'error', file, m.index, text, `Replace placeholder copy '${m[0]}' with real domain-specific content from the brief (never leak developer notes to visitors).`);
  }

  // 2. Hard-fail Anime.js v3 hallucination in UI/motion code
  for (const m of noComments.matchAll(/import\s+(?:anime|\*\s+as\s+\w+)\s+from\s+['"]animejs['"]|\banime\s*\(\s*\{\s*targets\s*:|\banime\.(?:default|timeline|stagger)\s*\(/g)) {
    report('animejs-v3-hallucination', 'error', file, m.index, text, "Do not use Anime.js v3 syntax. Use Anime.js v4 named imports: import { animate, createTimeline, createScope, stagger } from 'animejs'.");
  }

  if (['.html', '.css', '.jsx', '.tsx', '.vue', '.svelte', '.astro'].includes(ext)) {
    // 2b. Hard-fail leaked internal Atlas skill jargon in visible UI text
    const strippedScriptsStyles = noComments.replace(/<(?:script|style)\b[^>]*>[\s\S]*?<\/(?:script|style)>/gi, (s) => ' '.repeat(s.length));
    for (const m of strippedScriptsStyles.matchAll(/\b(?:ARCHETYPE:\s*[A-Z0-9-]+|SPLIT-SCREEN APPLICATION CALCULATOR|DEALT\s+DIRECTION|ATLAS-BRIEF|Zero fabricated testimonials|Tanpa ulasan bintang rekayasa|DISPATCH\s+v\d+)\b/gi)) {
      report('leaked-skill-jargon', 'error', file, m.index, text, `Do not leak internal skill jargon (${m[0]}) into visitor-facing UI; replace with authentic domain copy.`);
    }

    // 2c. Hard-fail leaked developer photo placeholder instructions in UI markup/text
    for (const m of strippedScriptsStyles.matchAll(PHOTO_PLACEHOLDER_LEAK_REGEX)) {
      report('leaked-photo-placeholder-ui', 'error', file, m.index, text, `Do not render photo placeholder instruction ('${m[0]}') in visitor UI; use domain editorial specimen plates marked silently via data-photo-slot.`);
    }
    for (const m of strippedScriptsStyles.matchAll(/<figure\b[^>]*\b(?:data-photo-placeholder|data-photo-slot)\b[^>]*>(?:(?!(?:<\/figure>|<section\b|<form\b))[\s\S])*?\b(?:Subjek|Subject):\s+[^\n<]{10,}/gi)) {
      report('leaked-photo-placeholder-ui', 'error', file, m.index, text, `Do not display internal brief notes ('Subjek:/Subject: ...') inside UI media slots; write an authentic visitor editorial caption.`);
    }

    // 3. AI copywriting clichés
    for (const m of noComments.matchAll(BUZZWORD_REGEX)) {
      report('ai-buzzword-copy', 'warn', file, m.index, text, `Replace AI marketing cliché '${m[0]}' with concrete nouns, measurable mechanisms, and direct verbs.`);
    }

    // 4. Emoji used inside interactive controls or headings
    for (const m of noComments.matchAll(/<(?:button|a|h1|h2|h3|nav)\b[^>]*>[^<]*[\u{1F300}-\u{1FAFF}\u{2728}\u{1F680}]/gu)) {
      report('emoji-ui', 'warn', file, m.index, text, 'Avoid using emojis as UI icons inside buttons, headings, or nav bars; use plain text or purposeful SVG icons.');
    }

    // 5. Generic purple-blue AI gradient (CSS + Tailwind classes)
    for (const m of noComments.matchAll(/(?:linear|radial)-gradient\([^)]*(?:#(?:6[0-9a-f]|7[0-9a-f]|8[0-9a-f])[0-9a-f]{4}|purple|indigo|violet)[^)]*(?:#(?:0[0-9a-f]|1[0-9a-f]|2[0-9a-f]|3[0-9a-f])[0-9a-f]{4}|blue|cyan)/gi)) {
      report('generic-purple-blue-gradient', 'warn', file, m.index, text, 'Generic purple-blue gradient detected; confirm it belongs to an authentic brand identity rather than a default AI template.');
    }
    for (const m of noComments.matchAll(/\bfrom-(?:indigo|purple|violet)-[4567]00\b[^\n"']*\bto-(?:blue|cyan|pink|fuchsia)-[4567]00\b/g)) {
      report('generic-purple-blue-gradient', 'warn', file, m.index, text, 'Generic Tailwind purple-blue gradient detected; replace with structured solid surfaces or a brand palette.');
    }

    // 6. Gradient clipped headline spam
    const clipMatches = [...noComments.matchAll(/background-clip\s*:\s*text|\bbg-clip-text\b/gi)];
    if (clipMatches.length >= 2) {
      report('gradient-text-spam', 'warn', file, clipMatches[1].index, text, 'Excessive gradient-clipped headlines (bg-clip-text); establish hierarchy via type scale, contrast, and placement.');
    }

    // 7. Unmotivated glassmorphism spam
    const blurMatches = [...noComments.matchAll(/backdrop-filter\s*:\s*blur|\bbackdrop-blur(?:-(?:sm|md|lg|xl|2xl|3xl))?\b/gi)];
    if (blurMatches.length > 2) {
      report('unmotivated-glass', 'warn', file, blurMatches[0].index, text, 'Repeated blur/glassmorphism detected; restrict backdrop-blur to functional overlay layers (such as sticky headers over media).');
    }

    // 8. Font proliferation: allow max 2 proportional families + max 1 monospace family
    const MONO_FONT_RE = /^(?:--font-(?:mono|code|monospace))|\b(?:mono|monospace|ui-monospace|jetbrains\s*mono|fira\s*code|sfmono-regular|menlo|consolas|courier|source\s*code\s*pro|ibm\s*plex\s*mono|inconsolata)\b/i;
    const familyMatches = [...noComments.matchAll(/font-family\s*:\s*([^;}{\r\n<>]+)/gi)];
    const distinctProportional = new Set();
    const distinctMono = new Set();
    let violationIndex = 0;
    for (const fm of familyMatches) {
      const rawFam = fm[1].trim();
      if (/^(?:inherit|initial|unset|revert)$/i.test(rawFam)) continue;
      const primaryTokenOrName = rawFam.startsWith('var(')
        ? rawFam.match(/var\(\s*(--[\w-]+)/)?.[1] || rawFam
        : rawFam.split(',')[0].trim().replace(/^['"]|['"]$/g, '').toLowerCase();
      if (MONO_FONT_RE.test(primaryTokenOrName) || MONO_FONT_RE.test(rawFam)) {
        if (!distinctMono.has(primaryTokenOrName)) {
          distinctMono.add(primaryTokenOrName);
          if (distinctMono.size === 2 && !violationIndex) violationIndex = fm.index;
        }
      } else if (!distinctProportional.has(primaryTokenOrName)) {
        distinctProportional.add(primaryTokenOrName);
        if (distinctProportional.size === 3 && !violationIndex) violationIndex = fm.index;
      }
    }
    if (distinctProportional.size > 2 || distinctMono.size > 1) {
      const allDetected = [...distinctProportional, ...distinctMono].join(', ');
      report('font-proliferation', 'error', file, violationIndex, text, `Excess font families detected (${allDetected}); limit to max 2 proportional families (display & body) + 1 optional monospace.`);
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
        report('leaked-debug-state-switcher', 'error', file, m.index, text, 'Debug state switcher (Populated/Loading/Empty/Error) must not appear in production UI. Remove or hide behind ?debug=1.');
      }
    }
    const debugBtnMatches = [...noComments.matchAll(/<button\b([^>]*)>\s*(?:Populated|Loading|Empty(?:\s+State)?|Error(?:\s+State)?)\s*<\/button>/gi)];
    if (debugBtnMatches.length >= 3) {
      const allHidden = debugBtnMatches.every((bm) => /\bhidden\b/i.test(bm[1] || ''));
      if (!(allHidden && hasDebugParamGuard)) {
        report('leaked-debug-state-switcher', 'error', file, debugBtnMatches[0].index, text, 'Debug state-switcher button group (Populated/Loading/Empty/Error) is visible in production UI. Hide behind ?debug=1.');
      }
    }

    // 9. Repeated uniform card grids
    const cards = (noComments.match(/(?:class|className)=["'][^"']*(?:card|feature-box|bento-item)[^"']*["']/gi) || []).length;
    if (cards >= 3) {
      report('repeated-card-grid', 'warn', file, Math.max(0, noComments.search(/card|feature-box|bento-item/i)), text, 'Verify that repeated cards serve distinct decision functions rather than filling a generic 3-column grid.');
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
