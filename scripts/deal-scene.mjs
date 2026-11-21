#!/usr/bin/env node
/**
 * Atlas deal-scene.mjs — picks ONE heavy scene and up to TWO light scenes for a page.
 *
 * The pick is driven by what the subject has to show (fit tags inferred from the prompt), then
 * broken by a seeded jitter so two similar prompts do not end up with the same scene, and it
 * never repeats a scene recorded in the project's history.
 *
 *   node scripts/deal-scene.mjs --prompt "<brief>" [--project <root> --write] [--seed <text>] [--avoid a,b] [--light <0-2>]
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const catalog = JSON.parse(fs.readFileSync(path.join(__dirname, '..', 'templates', 'scene-catalog.json'), 'utf8'));

const args = process.argv.slice(2);
const getOpt = (flag, fallback = '') => {
  const i = args.indexOf(flag);
  return i >= 0 && args[i + 1] && !args[i + 1].startsWith('--') ? args[i + 1] : fallback;
};

if (args.includes('--help') || args.includes('-h') || !getOpt('--prompt')) {
  console.log('Usage: node deal-scene.mjs --prompt "<brief>" [--project <root> --write] [--seed <text>] [--avoid a,b] [--light <0-2>]');
  process.exit(args.includes('--help') || args.includes('-h') ? 0 : 2);
}

const prompt = getOpt('--prompt').toLowerCase();
const seed = getOpt('--seed', '');
const lightCount = Math.min(2, Math.max(0, Number(getOpt('--light', '2'))));
const projectRoot = getOpt('--project') ? path.resolve(getOpt('--project')) : '';
const historyFile = projectRoot ? path.join(projectRoot, '.atlas-scenes.json') : '';

// Subject keywords (Indonesian and English) → fit tags. Every page also counts as a "statement".
const FIT_KEYWORDS = {
  place: /arsitek|architect|villa|hotel|resort|restoran|restaurant|caf[eé]|travel|wisata|properti|property|real estate|interior|kebun|garden|bangunan|building|homestay|penginapan/,
  product: /produk|product|toko|shop|store|fashion|butik|kopi|coffee|skincare|furnitur|furniture|merch|kerajinan|craft|katalog|catalog/,
  process: /layanan|service|agensi|agency|konsultasi|consult|studio|klinik|clinic|bengkel|workflow|cara kerja|onboarding|langkah|step/,
  proof: /renovasi|restorasi|restoration|renovation|before|sebelum|real estate|properti|interior|salon|beauty|dental|cleaning|makeover|transform/,
  portfolio: /fotograf|photograph|portfolio|portofolio|galeri|gallery|seniman|artist|desainer|designer|ilustrat|illustrat/,
  event: /event|acara|wedding|pernikahan|festival|konser|concert|konferensi|conference|pameran|exhibition/,
  software: /\bapp\b|aplikasi|saas|dashboard|\bai\b|\bapi\b|platform|software|developer|startup/,
  docs: /\bdocs?\b|dokumentasi|legal|hukum|riset|research|laporan|report|kebijakan|policy|jurnal|journal/
};

const fitScore = Object.fromEntries(catalog.fits.map((f) => [f, 0]));
fitScore.statement = 0.4;
for (const [fit, re] of Object.entries(FIT_KEYWORDS)) {
  const hits = prompt.match(new RegExp(re.source, 'g'));
  if (hits) fitScore[fit] += Math.min(3, hits.length);
}
// A document-style page never pins the viewport.
const docOnly = fitScore.docs > 0 && fitScore.place + fitScore.product + fitScore.portfolio + fitScore.event === 0;

// FNV-1a → 0..1, stable for the same prompt+seed+scene.
const jitter = (id) => {
  let h = 2166136261;
  for (const ch of `${prompt}|${seed}|${id}`) h = Math.imul(h ^ ch.charCodeAt(0), 16777619);
  return ((h >>> 0) % 1000) / 1000;
};

let history = { heavy: [], light: [] };
if (historyFile && fs.existsSync(historyFile)) {
  try { history = { ...history, ...JSON.parse(fs.readFileSync(historyFile, 'utf8')) }; } catch { /* ignore a corrupt history */ }
}
const avoid = new Set([...getOpt('--avoid').split(',').filter(Boolean), ...history.heavy.slice(-2), ...history.light.slice(-2)]);

const baseFit = (scene) => scene.fits.reduce((sum, fit) => sum + (fitScore[fit] || 0), 0);
const score = (scene) => baseFit(scene) + jitter(scene.id) * 1.1;
const reason = (scene) => {
  const hit = scene.fits.filter((fit) => fitScore[fit] >= 1);
  return hit.length ? `fits ${hit.join(' + ')} in the brief` : 'fits a general brand statement';
};

// Avoided scenes (flag or project history) are not candidates at all: no fitting heavy scene left means none.
const ranked = (mode) => catalog.scenes.filter((s) => s.mode === mode && !avoid.has(s.id)).map((s) => ({ s, score: score(s) })).sort((a, b) => b.score - a.score);

// A heavy scene needs a real fit (a brief signal, not just the generic statement weight); otherwise none.
const heavyPick = docOnly ? null : ranked('heavy').find(({ s }) => baseFit(s) >= 1)?.s || null;
const lights = [];
const usedFamilies = new Set();
for (const { s } of ranked('light')) {
  if (lights.length >= lightCount) break;
  if (usedFamilies.has(s.family)) continue; // one scene per family
  usedFamilies.add(s.family);
  lights.push(s);
}

const out = {
  fits: Object.fromEntries(Object.entries(fitScore).filter(([, v]) => v > 0).sort((a, b) => b[1] - a[1])),
  heavy: heavyPick ? { id: heavyPick.id, reason: reason(heavyPick), needs: heavyPick.needs, rest: heavyPick.rest } : null,
  light: lights.map((s) => ({ id: s.id, reason: reason(s), needs: s.needs, rest: s.rest })),
  note: docOnly ? 'Document-style brief: no pinned scene; light scenes only.' : !heavyPick ? 'No heavy scene fits this brief: use a strong hero and the light scenes.' : undefined,
  markup: 'references/scenes.md (one section per scene id)',
  avoided: [...avoid]
};

if (projectRoot && args.includes('--write')) {
  history.heavy.push(...(heavyPick ? [heavyPick.id] : []));
  history.light.push(...lights.map((s) => s.id));
  fs.writeFileSync(historyFile, JSON.stringify({ heavy: history.heavy.slice(-6), light: history.light.slice(-8) }, null, 2) + '\n');
  out.history = path.relative(process.cwd(), historyFile) || historyFile;
}

console.log(JSON.stringify(out, null, 2));
