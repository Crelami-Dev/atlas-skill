#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const root = path.resolve(process.argv[2] || 'evals/results');
if (!fs.existsSync(root)) {
  console.error('No evaluation results directory.');
  process.exit(1);
}

const rows = [];
for (const dateEntry of fs.readdirSync(root, { withFileTypes: true })) {
  if (!dateEntry.isDirectory()) continue;
  const date = dateEntry.name;
  const datePath = path.join(root, date);
  for (const promptEntry of fs.readdirSync(datePath, { withFileTypes: true })) {
    if (!promptEntry.isDirectory()) continue;
    const prompt = promptEntry.name;
    const base = path.join(datePath, prompt);
    const read = (label) => {
      const file = path.join(base, label, 'score.json');
      return fs.existsSync(file) ? JSON.parse(fs.readFileSync(file, 'utf8')) : null;
    };
    rows.push({ date, prompt, A: read('A'), B: read('B') });
  }
}

console.table(rows.map((r) => ({
  date: r.date,
  prompt: r.prompt,
  A: r.A?.average ?? 'pending',
  B: r.B?.average ?? 'pending'
})));
