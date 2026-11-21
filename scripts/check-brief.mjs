#!/usr/bin/env node
import fs from 'node:fs';

const args = process.argv.slice(2);
const lightFlag = args.includes('--light');
const requireImagePlanFlag = args.includes('--require-image-plan');
const positional = args.filter((a) => !a.startsWith('--'));
const file = positional[0] || 'design-brief.md';

const requiredSections = [
  { id: 'visitor', labels: ['Visitor and primary task', 'Pengunjung dan tugas utamanya'] },
  { id: 'content', labels: ['Real content', 'Konten nyata'] },
  { id: 'alternatives', labels: ['Three composition alternatives', 'Tiga alternatif komposisi'] },
  { id: 'choice', labels: ['Final choice and rationale', 'Pilihan akhir dan alasan'] },
  { id: 'rejected', labels: ['Deliberately rejected and why', 'Hal yang sengaja ditolak dan kenapa'] },
  { id: 'verification', labels: ['Verification plan', 'Rencana verifikasi'] }
];

const fail = (message) => {
  console.error(`FAIL: ${message}`);
  process.exitCode = 1;
};

const escapeRegex = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

if (!fs.existsSync(file)) {
  fail(`brief not found: ${file}`);
} else {
  const raw = fs.readFileSync(file, 'utf8');
  const text = raw.replace(/\r\n/g, '\n');
  const isLightBrief = lightFlag || /<!--\s*atlas-brief:\s*light\s*-->/i.test(text);

  if (!text.trim()) fail('empty brief');
  if (text.length > 7000) fail('brief exceeds single-page limit (7000 characters)');
  if (/\b(?:lorem ipsum|your company|acme corp|123 main st(?:reet)?)\b/i.test(text)) fail('brief contains placeholder copy');

  const activeSections = isLightBrief
    ? requiredSections.filter((s) => ['visitor', 'content', 'choice', 'verification'].includes(s.id))
    : requiredSections;

  for (const section of activeSections) {
    const labelPattern = section.labels.map(escapeRegex).join('|');
    const regex = new RegExp(`^##\\s+(?:${labelPattern})\\s*\\n([\\s\\S]*?)(?=^##\\s|(?![\\s\\S]))`, 'mi');
    const match = text.match(regex);
    if (!match || match[1].replace(/<!--[\s\S]*?-->/g, '').trim().length < 12) {
      fail(`missing required section: ${section.labels[0]}`);
    }
  }

  // Require "Image plan" / "Rencana gambar" when the brief targets a visual/photo-dependent domain
  const briefHeaderAndVisitor = (text.split(/^##\s+(?:Konten nyata|Real content)/mi)[0] || text);
  const isVisualDomain = /\b(?:fotografer|fotografi|photographer|photography|restoran|restaurant|kuliner|culinary|produk|product|properti|property|real estate|travel|wisata|pariwisata|fashion|butik|lookbook|event|acara|konferensi|conference|festival|pernikahan|wedding)\b/i.test(briefHeaderAndVisitor);
  if ((requireImagePlanFlag || isVisualDomain) && !isLightBrief) {
    const imgMatch = text.match(/^##\s+(?:Image plan|Rencana gambar)\s*\n([\s\S]*?)(?=^##\s|(?![\s\S]))/mi);
    if (!imgMatch || imgMatch[1].replace(/<!--[\s\S]*?-->/g, '').trim().length < 12) {
      fail('missing required section for visual domain: Image plan');
    }
  }

  if (!isLightBrief) {
    const altMatches = [...text.matchAll(/^###\s+(?:Alternatif|Alternative)\s+(\d+)\b[^\n]*\n([\s\S]*?)(?=^###\s|^##\s|(?![\s\S]))/gmi)];
    const distinctNums = new Set(altMatches.map((m) => m[1]));
    const validBodies = altMatches.filter((m) => m[2].replace(/<!--[\s\S]*?-->/g, '').trim().length >= 12);
    if (distinctNums.size < 3 || validBodies.length < 3) {
      fail('composition alternatives must contain at least 3 distinct numbers (Alternative 1, 2, 3) with adequate detail');
    }
  }

  // Optional but recommended: one distinctive move per page. When present it must name a real scene (or "none").
  const sigMatch = text.match(/^##\s+(?:Signature idea|Ide tanda tangan)\s*\n([\s\S]*?)(?=^##\s|(?![\s\S]))/mi);
  if (!sigMatch && !isLightBrief) {
    console.log('NOTE: no "## Signature idea" section. Add one distinctive move that comes from the subject (see references/creative-direction.md).');
  } else if (sigMatch) {
    const sigBody = sigMatch[1].replace(/<!--[\s\S]*?-->/g, '').trim();
    if (sigBody.length < 12) fail('Signature idea section is empty');
    const sceneRef = sigBody.match(/\bscene\s*[:=]\s*`?([a-z-]+)`?/i);
    if (sceneRef && sceneRef[1].toLowerCase() !== 'none') {
      try {
        const catalogPath = new URL('../templates/scene-catalog.json', import.meta.url);
        const known = JSON.parse(fs.readFileSync(catalogPath, 'utf8')).scenes.map((s) => s.id);
        if (!known.includes(sceneRef[1].toLowerCase())) fail(`Signature idea names an unknown scene "${sceneRef[1]}". Known: ${known.join(', ')}, or "none"`);
      } catch { /* catalog unavailable in a stripped export: skip the id check */ }
    }
  }

  if (!process.exitCode) console.log('PASS: complete brief');
}
