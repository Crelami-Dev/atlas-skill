#!/usr/bin/env node
/**
 * Atlas check-copy.mjs — word budgets for landing-page copy (static HTML, no browser).
 *
 * Short copy that still earns attention: a headline that names the offer, one supporting line, a
 * first screen a stranger can finish in five seconds, buttons that say what happens next, and no
 * wall of text between sections.
 *
 *   node scripts/check-copy.mjs <project-root | file.html> [--strict] [--json]
 *
 * FAIL (exit 1): vague button labels, a first screen far over budget, a paragraph far over budget.
 * WARN: budgets exceeded by a little, no concrete fact on the first screen, long sections/pages.
 * `--strict` turns warnings into failures. Opt out of length rules for documentation, legal text or
 * articles with `<!-- atlas-copy: long-form -->` (vague labels are still checked).
 */
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
const strict = args.includes('--strict');
const asJson = args.includes('--json');
const target = path.resolve(args.find((a) => !a.startsWith('--')) || '.');

const BUDGET = {
  h1: { warn: 10, fail: 16 },
  lede: { warn: 28, fail: 45 },
  firstScreen: { warn: 55, fail: 85 },
  heading: { warn: 9 },
  paragraph: { warn: 45, fail: 80 },
  section: { warn: 110 },
  page: { warn: 700 },
  cta: { warn: 5 },
  heroActions: { warn: 2 }
};

const VAGUE_LABEL = /^(?:learn more|read more|click here|discover|explore|more|more info|details?|submit|go|selengkapnya|baca selengkapnya|lihat selengkapnya|pelajari(?: lebih lanjut)?|klik di sini|info|detail)$/i;

const ENTITIES = { amp: '&', nbsp: ' ', quot: '"', apos: "'", lt: '<', gt: '>', mdash: '—', ndash: '–', middot: '·', hellip: '…' };
const decode = (s) => s.replace(/&(?:#x([0-9a-f]+)|#(\d+)|([a-z]+));/gi, (m, hex, dec, name) => (hex ? String.fromCodePoint(parseInt(hex, 16)) : dec ? String.fromCodePoint(Number(dec)) : ENTITIES[name.toLowerCase()] ?? m));
const dropBlocks = (html, tags) => html.replace(new RegExp(`<(${tags.join('|')})\\b[\\s\\S]*?</\\1>`, 'gi'), ' ');
const text = (html) => decode(html.replace(/<[^>]+>/g, ' ')).replace(/\s+/g, ' ').trim();
const words = (s) => s.split(/\s+/).filter((w) => /[\p{L}\p{N}]/u.test(w)).length;
const clip = (s, n = 70) => (s.length > n ? `${s.slice(0, n)}…` : s);

function htmlFiles(root) {
  const stat = fs.statSync(root);
  if (stat.isFile()) return [root];
  const out = [];
  const walk = (dir, depth) => {
    for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
      if (/^(node_modules|maintenance|\.|dist|build|out)/.test(entry.name)) continue;
      const full = path.join(dir, entry.name);
      if (entry.isDirectory()) { if (depth < 2) walk(full, depth + 1); } else if (/\.html?$/i.test(entry.name)) out.push(full);
    }
  };
  walk(root, 0);
  return out;
}

const VOID_TAGS = new Set(['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'source', 'track', 'wbr']);

/**
 * The element that actually contains the h1: the nearest section/header/article, else the first block
 * under <main>. Returns its [start, end) range by matching its own closing tag, so a hero built from a
 * <div> never swallows the sections below it.
 */
function enclosingBlock(html, at, from) {
  const stack = [];
  const tagRe = /<(\/?)([a-z][a-z0-9-]*)\b[^>]*>/gi;
  tagRe.lastIndex = from;
  for (let m = tagRe.exec(html); m && m.index < at; m = tagRe.exec(html)) {
    const name = m[2].toLowerCase();
    if (VOID_TAGS.has(name) || m[0].endsWith('/>')) continue;
    if (m[1]) {
      const i = stack.map((x) => x.name).lastIndexOf(name);
      if (i >= 0) stack.length = i;
    } else stack.push({ name, index: m.index });
  }
  const el = [...stack].reverse().find((x) => ['section', 'header', 'article'].includes(x.name)) || stack.find((x) => !['main', 'body', 'html'].includes(x.name));
  if (!el) return { start: at, end: Math.min(html.length, at + 3000) };
  const pair = new RegExp(`<(/?)${el.name}\\b[^>]*>`, 'gi');
  pair.lastIndex = el.index;
  let depth = 0;
  for (let m = pair.exec(html); m; m = pair.exec(html)) {
    depth += m[1] ? -1 : 1;
    if (depth === 0) return { start: el.index, end: m.index + m[0].length };
  }
  return { start: el.index, end: Math.min(html.length, at + 3000) };
}

function analyse(file) {
  const raw = fs.readFileSync(file, 'utf8');
  const findings = [];
  const add = (level, id, message, sample = '') => findings.push({ level, id, message, ...(sample ? { sample: clip(sample) } : {}) });
  const longForm = /<!--\s*atlas-copy:\s*long-form\s*-->/i.test(raw);

  const html = dropBlocks(raw.replace(/<!--[\s\S]*?-->/g, ' '), ['script', 'style', 'svg', 'noscript', 'template']);
  const mainStart = html.search(/<main\b/i);
  const body = mainStart >= 0 ? html.slice(mainStart) : html;
  const prose = dropBlocks(body, ['footer', 'nav', 'figcaption']);

  // Buttons and calls to action (all pages, long-form included).
  const ctaRe = /<(a|button)\b([^>]*)>([\s\S]*?)<\/\1>/gi;
  const ctas = [];
  for (const m of html.matchAll(ctaRe)) {
    if (/class\s*=\s*["'][^"']*\b(?:btn|button|cta)[\w-]*/i.test(m[2]) || /data-cta|role\s*=\s*["']button/i.test(m[2]) || m[1].toLowerCase() === 'button') {
      const label = text(m[3]);
      if (label && !/^[×x✕☰]$/i.test(label)) ctas.push({ label, index: m.index });
    }
  }
  for (const cta of ctas) {
    if (VAGUE_LABEL.test(cta.label)) add('error', 'copy-cta-vague', 'Button says nothing about what happens next. Use a verb plus what the visitor gets ("Book a visit", "Hitung estimasi").', cta.label);
    else if (words(cta.label) > BUDGET.cta.warn) add('warn', 'copy-cta-long', `Button label over ${BUDGET.cta.warn} words.`, cta.label);
  }

  // First screen: the hero element around the h1. Skipped for long-form pages (docs, legal, articles).
  const h1m = html.match(/<h1\b[\s\S]*?<\/h1>/i);
  if (h1m && !longForm) {
    const h1Text = text(h1m[0]);
    const h1Words = words(h1Text);
    if (h1Words > BUDGET.h1.fail) add('error', 'copy-h1-long', `Headline is ${h1Words} words (limit ${BUDGET.h1.fail}). Say the offer in 2-8.`, h1Text);
    else if (h1Words > BUDGET.h1.warn) add('warn', 'copy-h1-long', `Headline is ${h1Words} words; 2-8 reads faster.`, h1Text);
    else if (h1Words < 2) add('warn', 'copy-h1-short', 'Headline is a single word; name what you offer.', h1Text);

    const at = html.indexOf(h1m[0]);
    const { start, end } = enclosingBlock(html, at, Math.max(mainStart, 0));
    const hero = html.slice(start, end);
    const heroNoNav = dropBlocks(hero, ['nav', 'figcaption']);
    const heroText = text(heroNoNav);
    const heroWords = words(heroText);

    const afterH1 = html.slice(at + h1m[0].length, end);
    const ledeM = afterH1.match(/<p\b[\s\S]*?<\/p>/i);
    if (ledeM) {
      const ledeText = text(ledeM[0]);
      const n = words(ledeText);
      if (n > BUDGET.lede.fail) add('error', 'copy-lede-long', `Supporting line is ${n} words (limit ${BUDGET.lede.fail}). One sentence, one promise.`, ledeText);
      else if (n > BUDGET.lede.warn) add('warn', 'copy-lede-long', `Supporting line is ${n} words; aim for ${BUDGET.lede.warn} or fewer.`, ledeText);
    }
    if (heroWords > BUDGET.firstScreen.fail) add('error', 'copy-first-screen-long', `First screen carries ${heroWords} words (limit ${BUDGET.firstScreen.fail}).`);
    else if (heroWords > BUDGET.firstScreen.warn) add('warn', 'copy-first-screen-long', `First screen carries ${heroWords} words; under ${BUDGET.firstScreen.warn} is easier to finish.`);

    const heroCtas = ctas.filter((c) => c.index >= start && c.index <= end);
    if (heroCtas.length > BUDGET.heroActions.warn) add('warn', 'copy-hero-actions', `${heroCtas.length} actions in the hero; keep one main action and at most one secondary.`);

    // A concrete fact: a number, or a proper noun that is not the first word of a sentence.
    const hasDigit = /\d/.test(heroText);
    const properNoun = heroText.split(/(?<=[.!?])\s+/).flatMap((sentence) => sentence.split(/\s+/).slice(1)).some((w) => /^[A-Z][a-z]{2,}/.test(w));
    if (!hasDigit && !properNoun) add('warn', 'copy-no-hard-fact', 'No concrete fact on the first screen (a number, price, place or date). Specifics earn trust faster than adjectives.');
  }

  if (!longForm) {
    // Section headings.
    for (const m of body.matchAll(/<h([23])\b[\s\S]*?<\/h\1>/gi)) {
      const t = text(m[0]);
      if (words(t) > BUDGET.heading.warn) add('warn', 'copy-heading-long', `Heading is ${words(t)} words; ${BUDGET.heading.warn} or fewer scans better.`, t);
    }
    // Paragraphs.
    for (const m of prose.matchAll(/<p\b[\s\S]*?<\/p>/gi)) {
      const t = text(m[0]);
      const n = words(t);
      if (n > BUDGET.paragraph.fail) add('error', 'copy-paragraph-long', `Paragraph is ${n} words (limit ${BUDGET.paragraph.fail}). Cut it or split it into scannable lines.`, t);
      else if (n > BUDGET.paragraph.warn) add('warn', 'copy-paragraph-long', `Paragraph is ${n} words; ${BUDGET.paragraph.warn} or fewer keeps people reading.`, t);
    }
    // Walls of text per section, and for the whole page.
    for (const m of prose.matchAll(/<section\b[\s\S]*?<\/section>/gi)) {
      const t = text(dropBlocks(m[0], ['form', 'ul', 'ol', 'dl', 'table']));
      const n = words(t);
      if (n > BUDGET.section.warn) {
        const label = text((m[0].match(/<h[1-3]\b[\s\S]*?<\/h[1-3]>/i) || [''])[0]) || 'section';
        add('warn', 'copy-section-wall', `Section "${clip(label, 36)}" holds ${n} words of prose; show it (image, figure, list) or cut it.`);
      }
    }
    const pageWords = words(text(prose));
    if (pageWords > BUDGET.page.warn) add('warn', 'copy-page-long', `Page carries ${pageWords} words; a landing page rarely needs more than ${BUDGET.page.warn}.`);
  }

  return findings;
}

const files = htmlFiles(target);
const report = { target, files: [], summary: { error: 0, warn: 0 } };
if (!files.length) {
  console.log('PASS: no static HTML found; copy not checked (React/Vue projects: apply the same budgets by hand).');
  process.exit(0);
}
for (const file of files) {
  const findings = analyse(file);
  report.files.push({ file: path.relative(process.cwd(), file) || path.basename(file), findings });
  for (const f of findings) report.summary[f.level === 'error' ? 'error' : 'warn']++;
}

if (asJson) {
  console.log(JSON.stringify(report, null, 2));
} else {
  for (const f of report.files) {
    console.log(`${f.file}`);
    if (!f.findings.length) console.log('  ok');
    for (const x of f.findings) console.log(`  ${x.level === 'error' ? 'FAIL' : 'WARN'} [${x.id}] ${x.message}${x.sample ? `  "${x.sample}"` : ''}`);
  }
  const failed = report.summary.error > 0 || (strict && report.summary.warn > 0);
  console.log(`${failed ? 'FAIL' : 'PASS'}: ${report.summary.error} error, ${report.summary.warn} warning`);
}
if (report.summary.error > 0 || (strict && report.summary.warn > 0)) process.exitCode = 1;
