#!/usr/bin/env node
/**
 * Atlas v7.0.0 — Zero-Dependency Real Licensed Photography Fetcher (fetch-photos.mjs)
 * Queries the Wikimedia Commons API for high-resolution (>= 1000px), openly licensed
 * (CC0, Public Domain, CC-BY, CC-BY-SA) photographs matching domain queries, downloads them
 * locally into <project>/assets/photos/, and writes a structured credits.json + footer credit line.
 * Falls back gracefully with exitCode 0 in offline/air-gapped environments.
 */
import fs from 'node:fs';
import path from 'node:path';
import https from 'node:https';

const args = process.argv.slice(2);
if (args.includes('--help') || args.includes('-h')) {
  console.log(`Usage: node fetch-photos.mjs --query "<q1>|<q2>|<q3>" [--out <dir>] [--count <n>] [--min-width <px>] [--offline]
Examples:
  node scripts/fetch-photos.mjs --query "espresso machine extraction|pour over coffee v60|sourdough bread oven|coffee roasting drum" --out assets/photos --count 4`);
  process.exit(0);
}

const getOpt = (flag, fallback = null) => {
  const idx = args.indexOf(flag);
  return idx >= 0 && args[idx + 1] && !args[idx + 1].startsWith('--') ? args[idx + 1] : fallback;
};

const rawQuery = getOpt('--query', 'specialty coffee shop|artisan sourdough bread|pour over coffee');
const outDir = path.resolve(getOpt('--out', 'assets/photos'));
const maxCount = Math.max(1, Math.min(20, Number(getOpt('--count', '4')) || 4));
const minWidth = Math.max(600, Number(getOpt('--min-width', '1000')) || 1000);
const offlineMode = args.includes('--offline');

const queries = rawQuery
  .split(/[|;]+/)
  .map((q) => q.trim())
  .filter(Boolean);

const USER_AGENT = 'AtlasSkillPhotoFetcher/7.0 (https://github.com/Crelami-Dev/atlas-skill; opensource@example.org)';
const EXCLUDE_TITLE_RE = /\b(?:logo|icon|map|diagram|chart|graph|stamp|coat_of_arms|flag|signature|scanned|book_page|newspaper|poster|cartoon|drawing|sketch|clipart|banner|vector|symbol|emblem|medal|coin|statue|grave|cemetery|document|pdf|svg)\b/i;
const ALLOWED_LICENSE_RE = /\b(?:cc0|public\s*domain|pd|cc[- ]by(?:[- ]sa)?)\b/i;

function stripHtml(html) {
  return String(html || '')
    .replace(/<[^>]*>/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}

function slugify(str) {
  return String(str || 'photo')
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')
    .slice(0, 28) || 'photo';
}

function httpsGetBuffer(url, redirectsLeft = 4) {
  return new Promise((resolve, reject) => {
    const req = https.get(url, { headers: { 'User-Agent': USER_AGENT, Accept: '*/*' }, timeout: 12000 }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location && redirectsLeft > 0) {
        res.resume();
        const nextUrl = new URL(res.headers.location, url).toString();
        resolve(httpsGetBuffer(nextUrl, redirectsLeft - 1));
        return;
      }
      if (res.statusCode !== 200) {
        res.resume();
        reject(new Error(`HTTP ${res.statusCode} for ${url}`));
        return;
      }
      const chunks = [];
      res.on('data', (c) => chunks.push(c));
      res.on('end', () => resolve(Buffer.concat(chunks)));
    });
    req.on('timeout', () => { req.destroy(new Error(`Timeout fetching ${url}`)); });
    req.on('error', reject);
  });
}

async function searchWikimedia(query) {
  const api = new URL('https://commons.wikimedia.org/w/api.php');
  api.searchParams.set('action', 'query');
  api.searchParams.set('generator', 'search');
  api.searchParams.set('gsrsearch', `filetype:bitmap ${query}`);
  api.searchParams.set('gsrnamespace', '6');
  api.searchParams.set('gsrlimit', '30');
  api.searchParams.set('prop', 'imageinfo');
  api.searchParams.set('iiprop', 'url|dimensions|mime|extmetadata');
  api.searchParams.set('iiurlwidth', '1600');
  api.searchParams.set('format', 'json');

  const queryTokens = query
    .toLowerCase()
    .split(/[^a-z0-9]+/)
    .filter((w) => w.length >= 3 && !['the', 'and', 'for', 'with', 'from', 'photo', 'image', 'shot'].includes(w));

  const buf = await httpsGetBuffer(api.toString());
  const data = JSON.parse(buf.toString('utf8'));
  const pages = Object.values(data?.query?.pages || {});
  const candidates = [];

  for (const page of pages) {
    const title = String(page.title || '').replace(/^File:/i, '');
    if (!title || EXCLUDE_TITLE_RE.test(title)) continue;
    const ii = page.imageinfo?.[0];
    if (!ii) continue;
    const mime = String(ii.mime || '').toLowerCase();
    if (!['image/jpeg', 'image/jpg', 'image/png', 'image/webp'].includes(mime)) continue;
    const w = Number(ii.thumbwidth || ii.width || 0);
    const h = Number(ii.thumbheight || ii.height || 0);
    if (w < minWidth || h < 500) continue;
    const aspect = w / Math.max(1, h);
    if (aspect < 0.65 || aspect > 2.4) continue;

    const meta = ii.extmetadata || {};
    const licenseShort = stripHtml(meta.LicenseShortName?.value || meta.UsageTerms?.value || '');
    if (!ALLOWED_LICENSE_RE.test(licenseShort)) continue;

    const titleLower = title.toLowerCase();
    const descLower = stripHtml(meta.ImageDescription?.value || meta.ObjectName?.value || '').toLowerCase();
    let titleHits = 0;
    let descHits = 0;
    for (const tok of queryTokens) {
      if (titleLower.includes(tok)) titleHits++;
      if (descLower.includes(tok)) descHits++;
    }
    if (queryTokens.length > 0 && titleHits === 0) continue;

    const artist = stripHtml(meta.Artist?.value || meta.Credit?.value || 'Wikimedia Commons contributor').slice(0, 80);
    const downloadUrl = ii.thumburl || ii.url;
    if (!downloadUrl) continue;

    candidates.push({
      title,
      query,
      relevance: titleHits * 4 + descHits * 2 + (w >= 1400 ? 1 : 0),
      width: w,
      height: h,
      mime,
      license: licenseShort,
      author: artist || 'Wikimedia Commons',
      sourceUrl: ii.descriptionurl || `https://commons.wikimedia.org/wiki/File:${encodeURIComponent(title)}`,
      downloadUrl
    });
  }
  candidates.sort((a, b) => b.relevance - a.relevance);
  return candidates;
}

async function main() {
  fs.mkdirSync(outDir, { recursive: true });
  if (offlineMode) {
    const offlineManifest = {
      status: 'offline-fallback',
      outDir,
      count: 0,
      photos: [],
      creditLine: null,
      advice: 'Offline mode active; use layered editorial SVG specimen plates per references/imagery.md.'
    };
    fs.writeFileSync(path.join(outDir, 'credits.json'), JSON.stringify(offlineManifest, null, 2) + '\n');
    console.log(JSON.stringify(offlineManifest, null, 2));
    return;
  }

  const downloaded = [];
  const usedTitles = new Set();

  try {
    let qIdx = 0;
    const targetPerQuery = Math.max(1, Math.ceil(maxCount / Math.max(1, queries.length)));

    for (const q of queries) {
      if (downloaded.length >= maxCount) break;
      const candidates = await searchWikimedia(q);
      let takenForQuery = 0;
      for (const c of candidates) {
        if (downloaded.length >= maxCount || takenForQuery >= targetPerQuery) break;
        if (usedTitles.has(c.title)) continue;
        try {
          const imgBuf = await httpsGetBuffer(c.downloadUrl);
          if (imgBuf.length < 12000) continue; // Skip suspiciously tiny thumbnails
          usedTitles.add(c.title);
          qIdx++;
          const ext = c.mime.includes('png') ? '.png' : c.mime.includes('webp') ? '.webp' : '.jpg';
          const fileName = `photo-${String(qIdx).padStart(2, '0')}-${slugify(q)}${ext}`;
          const absPath = path.join(outDir, fileName);
          fs.writeFileSync(absPath, imgBuf);
          downloaded.push({
            id: `photo-${String(qIdx).padStart(2, '0')}`,
            file: fileName,
            relativePath: path.relative(process.cwd(), absPath).replaceAll('\\', '/'),
            query: c.query,
            title: c.title,
            width: c.width,
            height: c.height,
            bytes: imgBuf.length,
            author: c.author,
            license: c.license,
            sourceUrl: c.sourceUrl
          });
          takenForQuery++;
        } catch {
          /* Try next candidate */
        }
      }
    }
  } catch (err) {
    console.log(JSON.stringify({
      status: 'offline-fallback',
      outDir,
      error: err.message,
      photos: downloaded,
      creditLine: null,
      advice: 'Network unavailable or Wikimedia unreachable; use layered architectural SVG specimen plates per references/imagery.md.'
    }, null, 2));
    return;
  }

  const creditParts = downloaded.map((p) => `${p.author} (${p.license})`);
  const creditLine = downloaded.length > 0
    ? `Photographs via Wikimedia Commons: ${creditParts.join(' · ')}.`
    : null;

  const manifest = {
    status: downloaded.length > 0 ? 'ok' : 'no-matches',
    outDir,
    count: downloaded.length,
    creditLine,
    photos: downloaded
  };

  if (downloaded.length > 0) {
    fs.writeFileSync(path.join(outDir, 'credits.json'), JSON.stringify(manifest, null, 2) + '\n');
  }
  console.log(JSON.stringify(manifest, null, 2));
}

main();
