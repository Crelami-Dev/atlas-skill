#!/usr/bin/env node
/**
 * Scaffolds evals/results/YYYY-MM-DD/<prompt>/{A,B} and generates a randomized blind A/B assignment
 * (blind-key.json + blind-sheet.md) per evals/run-protocol.md without fabricating any evaluation scores.
 */
import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '..');
const args = process.argv.slice(2);

if (args.includes('--help') || args.includes('-h')) {
  console.log('Usage: node evals/prepare-blind-eval.mjs [--date YYYY-MM-DD] [--out-root evals/results] [--seed <string>]');
  process.exit(0);
}

const getOpt = (flag, fallback) => {
  const idx = args.indexOf(flag);
  return idx >= 0 && args[idx + 1] ? args[idx + 1] : fallback;
};

const dateStr = getOpt('--date', '2026-11-18');
const outRoot = path.resolve(getOpt('--out-root', path.join(repoRoot, 'evals/results')));
const seed = getOpt('--seed', null);

const promptsDir = path.join(repoRoot, 'evals/prompts');
const promptSlugs = fs.readdirSync(promptsDir)
  .filter((f) => f.endsWith('.md'))
  .sort()
  .map((f) => path.basename(f, '.md'));

function decideFlip(promptSlug, index) {
  if (seed) {
    const digest = crypto.createHash('sha256').update(`${seed}:${promptSlug}:${index}`).digest()[0];
    return (digest & 1) === 1;
  }
  return crypto.randomInt(0, 2) === 1;
}

const dateDir = path.join(outRoot, dateStr);
fs.mkdirSync(dateDir, { recursive: true });

const blindAssignments = {};
const sheetRows = [];

promptSlugs.forEach((slug, idx) => {
  const promptBase = path.join(dateDir, slug);
  for (const variant of ['A', 'B']) {
    const variantDir = path.join(promptBase, variant);
    fs.mkdirSync(variantDir, { recursive: true });
    const statusFile = path.join(variantDir, 'status.json');
    if (!fs.existsSync(statusFile)) {
      fs.writeFileSync(statusFile, JSON.stringify({
        prompt: slug,
        variant,
        condition: variant === 'A' ? 'baseline-without-skill' : 'treatment-with-atlas-skill',
        status: 'pending-empirical-run',
        note: 'No empirical run or human score recorded yet. Do not fabricate scores.'
      }, null, 2) + '\n');
    }
  }

  const swap = decideFlip(slug, idx);
  const candidate1 = swap ? 'B' : 'A';
  const candidate2 = swap ? 'A' : 'B';
  blindAssignments[slug] = {
    'Candidate-1': candidate1,
    'Candidate-2': candidate2
  };
  sheetRows.push(`| ${slug} | Candidate-1 | | | | | | | | |`);
  sheetRows.push(`| ${slug} | Candidate-2 | | | | | | | | |`);
});

const blindKeyPath = path.join(dateDir, 'blind-key.json');
fs.writeFileSync(blindKeyPath, JSON.stringify({
  date: dateStr,
  protocol: 'evals/run-protocol.md',
  status: 'unscored-blind-key',
  assignments: blindAssignments
}, null, 2) + '\n');

const blindSheetPath = path.join(dateDir, 'blind-sheet.md');
const sheetContent = `# Blind A/B Evaluation Sheet (${dateStr})

> **Protocol:** Evaluators inspect rendered outputs and screenshots for \`Candidate-1\` and \`Candidate-2\` without opening \`blind-key.json\`. Score each axis 1-5 according to \`evals/rubric.md\`.

| Prompt | Blind label | Hierarchy | Type | Distinctiveness | System | Responsive | Accessibility | Honesty | Notes |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
${sheetRows.join('\n')}
`;
fs.writeFileSync(blindSheetPath, sheetContent);

console.log(JSON.stringify({
  result: 'PREPARED',
  date: dateStr,
  dateDir,
  promptsPrepared: promptSlugs.length,
  blindKeyPath,
  blindSheetPath
}, null, 2));
