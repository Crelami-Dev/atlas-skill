#!/usr/bin/env node
import fs from 'node:fs';

const args = process.argv.slice(2);
const lightFlag = args.includes('--light');
const requireImagePlanFlag = args.includes('--require-image-plan');
const positional = args.filter((a) => !a.startsWith('--'));
const file = positional[0] || 'design-brief.md';

const requiredSections = [
  { id: 'visitor', labels: ['Pengunjung dan tugas utamanya', 'Visitor and primary task'] },
  { id: 'content', labels: ['Konten nyata', 'Real content'] },
  { id: 'alternatives', labels: ['Tiga alternatif komposisi', 'Three composition alternatives'] },
  { id: 'choice', labels: ['Pilihan akhir dan alasan', 'Final choice and rationale'] },
  { id: 'rejected', labels: ['Hal yang sengaja ditolak dan kenapa', 'Deliberately rejected and why'] },
  { id: 'verification', labels: ['Rencana verifikasi', 'Verification plan'] }
];

const fail = (message) => {
  console.error(`FAIL: ${message}`);
  process.exitCode = 1;
};

const escapeRegex = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');

if (!fs.existsSync(file)) {
  fail(`brief tidak ditemukan / brief not found: ${file}`);
} else {
  const raw = fs.readFileSync(file, 'utf8');
  const text = raw.replace(/\r\n/g, '\n');
  const isLightBrief = lightFlag || /<!--\s*atlas-brief:\s*light\s*-->/i.test(text);

  if (!text.trim()) fail('brief kosong / empty brief');
  if (text.length > 7000) fail('brief melebihi satu halaman (7000 karakter)');
  if (/\b(?:lorem ipsum|your company|acme corp|123 main st(?:reet)?)\b/i.test(text)) fail('brief berisi placeholder');

  const activeSections = isLightBrief
    ? requiredSections.filter((s) => ['visitor', 'content', 'choice', 'verification'].includes(s.id))
    : requiredSections;

  for (const section of activeSections) {
    const labelPattern = section.labels.map(escapeRegex).join('|');
    const regex = new RegExp(`^##\\s+(?:${labelPattern})\\s*\\n([\\s\\S]*?)(?=^##\\s|(?![\\s\\S]))`, 'mi');
    const match = text.match(regex);
    if (!match || match[1].replace(/<!--[\s\S]*?-->/g, '').trim().length < 12) {
      fail(`bagian wajib kosong / missing required section: ${section.labels.join(' / ')}`);
    }
  }

  // Require "Rencana gambar" / "Image plan" when the brief targets a visual/photo-dependent domain
  const briefHeaderAndVisitor = (text.split(/^##\s+(?:Konten nyata|Real content)/mi)[0] || text);
  const isVisualDomain = /\b(?:fotografer|fotografi|photographer|photography|restoran|restaurant|kuliner|produk|product|properti|property|real estate|travel|wisata|pariwisata|fashion|butik|lookbook|event|acara|konferensi|festival|pernikahan|wedding)\b/i.test(briefHeaderAndVisitor);
  if ((requireImagePlanFlag || isVisualDomain) && !isLightBrief) {
    const imgMatch = text.match(/^##\s+(?:Rencana gambar|Image plan)\s*\n([\s\S]*?)(?=^##\s|(?![\s\S]))/mi);
    if (!imgMatch || imgMatch[1].replace(/<!--[\s\S]*?-->/g, '').trim().length < 12) {
      fail('bagian wajib kosong untuk domain visual / missing required section for visual domain: Rencana gambar / Image plan');
    }
  }

  if (!isLightBrief) {
    const altMatches = [...text.matchAll(/^###\s+(?:Alternatif|Alternative)\s+(\d+)\b[^\n]*\n([\s\S]*?)(?=^###\s|^##\s|(?![\s\S]))/gmi)];
    const distinctNums = new Set(altMatches.map((m) => m[1]));
    const validBodies = altMatches.filter((m) => m[2].replace(/<!--[\s\S]*?-->/g, '').trim().length >= 12);
    if (distinctNums.size < 3 || validBodies.length < 3) {
      fail('alternatif komposisi harus memiliki minimal 3 nomor berbeda (Alternatif/Alternative 1, 2, 3) dengan isi memadai');
    }
  }

  if (!process.exitCode) console.log('PASS: brief lengkap / complete brief');
}
