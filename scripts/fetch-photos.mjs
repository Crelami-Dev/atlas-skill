#!/usr/bin/env node
/**
 * Atlas v7.0.0 — Zero-Dependency Real Licensed Photography Fetcher (fetch-photos.mjs)
 * Queries the Wikimedia Commons API for high-resolution (>= 1000px), openly licensed
 * (CC0, Public Domain, CC-BY, CC-BY-SA) photographs matching domain queries, downloads them
 * locally into <project>/assets/photos/, and writes a structured credits.json + footer credit line.
 * Falls back gracefully with exitCode 0 in offline/air-gapped environments.
 *
 * Reliability: every request has a hard wall-clock limit (a server that trickles bytes cannot hang
 * the run), transient failures retry once, one failed query never cancels the others, and
 * credits.json is rewritten after every download so an interrupted run still attributes its files.
 */
import fs from 'node:fs';
import path from 'node:path';
import https from 'node:https';
import http from 'node:http';

const args = process.argv.slice(2);
if (args.includes('--help') || args.includes('-h')) {
  console.log(`Usage: node fetch-photos.mjs --query "<q1>|<q2>|<q3>" [--out <dir>] [--count <n>] [--min-width <px>] [--offline]
                          [--timeout <sec>] [--request-timeout <sec>] [--width <px>]
  --width            Download width in pixels (default 1600, max 3840). Use 3200 for photos that get zoomed (pull-back).
  --timeout          Total run budget in seconds (default 120). Photos downloaded so far are kept and credited.
  --request-timeout  Hard limit per HTTP request in seconds (default 30), including slow trickling downloads.
Tip: keep each query to 2-3 words (e.g. "Bali villa"); long phrases usually return nothing.
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
const downloadWidth = Math.min(3840, Math.max(800, Number(getOpt('--width', '1600')) || 1600));
const totalBudgetMs = Math.max(5, Number(getOpt('--timeout', '120')) || 120) * 1000;
const requestTimeoutMs = Math.max(1, Number(getOpt('--request-timeout', '30')) || 30) * 1000;
const deadline = Date.now() + totalBudgetMs;
const API_URL = process.env.ATLAS_WIKIMEDIA_API || 'https://commons.wikimedia.org/w/api.php';
const MAX_BYTES = 30 * 1024 * 1024;
const MAX_ATTEMPTS = 2;
const MIN_USEFUL_MS = 1000;

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

const remainingMs = () => deadline - Date.now();

class FetchError extends Error {
  constructor(message, retryable) {
    super(message);
    this.retryable = retryable;
  }
}

/**
 * One attempt with a hard wall-clock limit. The socket `timeout` option only fires on silence, so a
 * server that keeps trickling bytes would never trip it; the separate timer below always does.
 */
function getOnce(url, redirectsLeft, limitMs) {
  return new Promise((resolve, reject) => {
    const hardDeadline = Date.now() + limitMs;
    let settled = false;
    let hardTimer;
    let req;
    const finish = (fn, value) => {
      if (settled) return;
      settled = true;
      clearTimeout(hardTimer);
      fn(value);
    };
    hardTimer = setTimeout(() => {
      req?.destroy();
      finish(reject, new FetchError(`Request exceeded ${Math.round(limitMs / 1000)}s: ${url}`, true));
    }, limitMs);

    const transport = url.startsWith('http:') ? http : https;
    req = transport.get(url, { headers: { 'User-Agent': USER_AGENT, Accept: '*/*' }, timeout: 12000 }, (res) => {
      if (res.statusCode >= 300 && res.statusCode < 400 && res.headers.location && redirectsLeft > 0) {
        res.resume();
        const nextUrl = new URL(res.headers.location, url).toString();
        const left = hardDeadline - Date.now();
        if (left < 50) {
          finish(reject, new FetchError(`Request exceeded ${Math.round(limitMs / 1000)}s while following redirects: ${url}`, true));
          return;
        }
        // Pass only the real time left so a redirect chain can never outlive the request limit.
        finish(resolve, getOnce(nextUrl, redirectsLeft - 1, left));
        return;
      }
      if (res.statusCode !== 200) {
        res.resume();
        finish(reject, new FetchError(`HTTP ${res.statusCode} for ${url}`, res.statusCode === 429 || res.statusCode >= 500));
        return;
      }
      const chunks = [];
      let size = 0;
      res.on('data', (c) => {
        size += c.length;
        if (size > MAX_BYTES) {
          req.destroy();
          finish(reject, new FetchError(`Response over ${MAX_BYTES} bytes: ${url}`, false));
          return;
        }
        chunks.push(c);
      });
      res.on('end', () => finish(resolve, Buffer.concat(chunks)));
      res.on('error', (err) => finish(reject, new FetchError(err.message, true)));
    });
    req.on('timeout', () => {
      req.destroy();
      finish(reject, new FetchError(`Socket idle timeout: ${url}`, true));
    });
    req.on('error', (err) => finish(reject, new FetchError(err.message, true)));
  });
}

async function httpsGetBuffer(url) {
  let lastError;
  for (let attempt = 1; attempt <= MAX_ATTEMPTS; attempt++) {
    const limit = Math.min(requestTimeoutMs, remainingMs());
    if (limit < MIN_USEFUL_MS) throw new FetchError('Total --timeout budget exhausted', false);
    try {
      return await getOnce(url, 4, limit);
    } catch (err) {
      lastError = err;
      if (!err.retryable || attempt === MAX_ATTEMPTS || remainingMs() < 3000) break;
      await new Promise((r) => setTimeout(r, 800 * attempt));
    }
  }
  throw lastError;
}

async function searchWikimedia(query) {
  const api = new URL(API_URL);
  api.searchParams.set('action', 'query');
  api.searchParams.set('generator', 'search');
  api.searchParams.set('gsrsearch', `filetype:bitmap ${query}`);
  api.searchParams.set('gsrnamespace', '6');
  api.searchParams.set('gsrlimit', '30');
  api.searchParams.set('prop', 'imageinfo');
  api.searchParams.set('iiprop', 'url|dimensions|mime|extmetadata');
  api.searchParams.set('iiurlwidth', String(downloadWidth));
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
      advice: 'Offline mode active; use a typographic specification plate per references/imagery.md (never a hand-drawn SVG scene).'
    };
    fs.writeFileSync(path.join(outDir, 'credits.json'), JSON.stringify(offlineManifest, null, 2) + '\n');
    console.log(JSON.stringify(offlineManifest, null, 2));
    return;
  }

  const downloaded = [];
  const usedTitles = new Set();
  const problems = [];
  let searchesRun = 0;
  let searchesFailed = 0;
  let outOfBudget = false;

  const buildManifest = (status) => ({
    status,
    outDir,
    count: downloaded.length,
    creditLine: downloaded.length > 0
      ? `Photographs via Wikimedia Commons: ${downloaded.map((p) => `${p.author} (${p.license})`).join(' · ')}.`
      : null,
    ...(problems.length ? { problems } : {}),
    photos: downloaded
  });
  // Rewritten after every download so an interrupted run never leaves photos without attribution.
  const saveCredits = () => fs.writeFileSync(path.join(outDir, 'credits.json'), JSON.stringify(buildManifest('partial'), null, 2) + '\n');

  let qIdx = 0;
  const targetPerQuery = Math.max(1, Math.ceil(maxCount / Math.max(1, queries.length)));

  for (const q of queries) {
    if (downloaded.length >= maxCount) break;
    if (remainingMs() < MIN_USEFUL_MS * 3) {
      outOfBudget = true;
      problems.push(`Skipped "${q}": total --timeout budget used up`);
      continue;
    }
    let candidates;
    searchesRun++;
    try {
      candidates = await searchWikimedia(q);
    } catch (err) {
      searchesFailed++;
      problems.push(`Search "${q}" failed: ${err.message}`);
      continue;
    }
    let takenForQuery = 0;
    for (const c of candidates) {
      if (downloaded.length >= maxCount || takenForQuery >= targetPerQuery) break;
      if (usedTitles.has(c.title)) continue;
      if (remainingMs() < MIN_USEFUL_MS * 3) {
        outOfBudget = true;
        problems.push('Stopped downloading: total --timeout budget used up');
        break;
      }
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
        saveCredits();
      } catch (err) {
        problems.push(`Skipped "${c.title}": ${err.message}`);
      }
    }
  }

  // Every search that ran failed: the network or Wikimedia is unreachable, not "no matches".
  if (downloaded.length === 0 && searchesRun > 0 && searchesFailed === searchesRun) {
    console.log(JSON.stringify({
      status: 'offline-fallback',
      outDir,
      problems,
      photos: [],
      creditLine: null,
      advice: 'Network unavailable or Wikimedia unreachable; use a typographic specification plate per references/imagery.md (never a hand-drawn SVG scene).'
    }, null, 2));
    return;
  }

  const status = downloaded.length === 0 ? 'no-matches' : outOfBudget || problems.length ? 'partial' : 'ok';
  const manifest = buildManifest(status);
  if (downloaded.length > 0) {
    fs.writeFileSync(path.join(outDir, 'credits.json'), JSON.stringify(manifest, null, 2) + '\n');
  }
  console.log(JSON.stringify(manifest, null, 2));
}

main().catch((err) => {
  console.log(JSON.stringify({ status: 'error', error: err.message, photos: [], creditLine: null }, null, 2));
});
