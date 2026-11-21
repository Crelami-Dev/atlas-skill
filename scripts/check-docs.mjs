#!/usr/bin/env node
/**
 * Documentation sync & honesty guard (scripts/check-docs.mjs).
 * Exits with code 1 whenever generated or manual docs drift from the repository.
 */
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import {
  REPO_ROOT,
  extractQuickCheckFindings,
  parseSimpleYamlFindings,
  loadSceneCatalog
} from './gen-docs.mjs';

const args = process.argv.slice(2);
const getOpt = (flag) => {
  const idx = args.indexOf(flag);
  return idx >= 0 && args[idx + 1] ? args[idx + 1] : null;
};

const rootDir = path.resolve(getOpt('--root') || REPO_ROOT);
const findingsPath = path.resolve(rootDir, getOpt('--findings') || 'site/content-src/findings.yml');
const catalogPath = path.resolve(rootDir, getOpt('--catalog') || 'templates/scene-catalog.json');
const docsDir = path.resolve(rootDir, getOpt('--docs-dir') || 'site/src/content/docs');

const errors = [];

function listFiles(dir) {
  const out = [];
  if (!fs.existsSync(dir)) return out;
  const walk = (d) => {
    for (const entry of fs.readdirSync(d, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name))) {
      const full = path.join(d, entry.name);
      if (entry.isDirectory()) walk(full);
      else if (entry.isFile()) out.push(full);
    }
  };
  walk(dir);
  return out;
}

// 1. Package version consistency
const pkg = JSON.parse(fs.readFileSync(path.join(rootDir, 'package.json'), 'utf8'));
const expectedVersion = pkg.version;

// 2. Quick-check finding codes vs site/content-src/findings.yml (bidirectional 1-to-1)
const quickCheckPath = path.join(rootDir, 'skills/atlas-checker/scripts/quick-check.mjs');
const extractedFindings = extractQuickCheckFindings(fs.readFileSync(quickCheckPath, 'utf8'));
const extractedCodes = new Set(extractedFindings.map((f) => f.code));

if (!fs.existsSync(findingsPath)) {
  errors.push(`Missing findings dictionary file: ${path.relative(rootDir, findingsPath)}. Run or restore site/content-src/findings.yml.`);
} else {
  const yamlEntries = parseSimpleYamlFindings(fs.readFileSync(findingsPath, 'utf8'));
  const yamlCodes = new Set();
  for (const entry of yamlEntries) {
    if (!entry.code) {
      errors.push(`Malformed item without "code" field in ${path.relative(rootDir, findingsPath)}.`);
      continue;
    }
    if (yamlCodes.has(entry.code)) {
      errors.push(`Duplicate finding code "${entry.code}" in ${path.relative(rootDir, findingsPath)}. Keep exactly one entry per code.`);
    }
    yamlCodes.add(entry.code);
    for (const field of ['severity', 'meaning_id', 'cause_id', 'fix_id', 'meaning_en', 'cause_en', 'fix_en']) {
      if (!entry[field] || !String(entry[field]).trim()) {
        errors.push(`Finding "${entry.code}" is missing required field "${field}" in ${path.relative(rootDir, findingsPath)}.`);
      }
    }
  }
  for (const code of extractedCodes) {
    if (!yamlCodes.has(code)) {
      errors.push(`Finding code "${code}" exists in skills/atlas-checker/scripts/quick-check.mjs but is missing from ${path.relative(rootDir, findingsPath)}. Add an entry "- code: ${code}" with severity and ID/EN fields.`);
    }
  }
  for (const code of yamlCodes) {
    if (!extractedCodes.has(code)) {
      errors.push(`Orphan finding entry "${code}" in ${path.relative(rootDir, findingsPath)} does not exist in skills/atlas-checker/scripts/quick-check.mjs. Remove "${code}" or add it to quick-check.mjs.`);
    }
  }
}

// 3. Every scene in scene-catalog.json must exist in both id/ and en/ scenes output + index
if (!fs.existsSync(catalogPath)) {
  errors.push(`Missing scene catalog: ${path.relative(rootDir, catalogPath)}.`);
} else {
  const catalog = loadSceneCatalog(catalogPath);
  for (const lang of ['id', 'en']) {
    const indexPath = path.join(docsDir, lang, 'scenes/index.md');
    const indexContent = fs.existsSync(indexPath) ? fs.readFileSync(indexPath, 'utf8') : '';
    if (!indexContent) {
      errors.push(`Missing generated scenes index at ${path.relative(rootDir, indexPath)}. Run "node scripts/gen-docs.mjs".`);
    }
    for (const sc of catalog.scenes) {
      const scenePage = path.join(docsDir, lang, 'scenes', `${sc.id}.md`);
      if (!fs.existsSync(scenePage)) {
        errors.push(`Scene "${sc.id}" in ${path.relative(rootDir, catalogPath)} has no generated doc at ${path.relative(rootDir, scenePage)}. Run "node scripts/gen-docs.mjs".`);
      }
      if (indexContent && !indexContent.includes(sc.id)) {
        errors.push(`Scene "${sc.id}" in ${path.relative(rootDir, catalogPath)} is missing from ${path.relative(rootDir, indexPath)}. Run "node scripts/gen-docs.mjs".`);
      }
    }
  }
}

// 4. Manual i18n parity check (site/content-src/manual/id vs en)
const manualIdDir = path.join(rootDir, 'site/content-src/manual/id');
const manualEnDir = path.join(rootDir, 'site/content-src/manual/en');
const idManualFiles = listFiles(manualIdDir).map((f) => path.relative(manualIdDir, f).replaceAll('\\', '/'));
const enManualFiles = listFiles(manualEnDir).map((f) => path.relative(manualEnDir, f).replaceAll('\\', '/'));
const idSet = new Set(idManualFiles);
const enSet = new Set(enManualFiles);

for (const rel of idManualFiles) {
  if (!enSet.has(rel)) {
    errors.push(`Manual page mismatch: "site/content-src/manual/id/${rel}" has no English counterpart at "site/content-src/manual/en/${rel}". Add the English translation.`);
  } else {
    const idText = fs.readFileSync(path.join(manualIdDir, rel), 'utf8').replace(/\r\n/g, '\n');
    const enText = fs.readFileSync(path.join(manualEnDir, rel), 'utf8').replace(/\r\n/g, '\n');
    const getHeadings = (t) => t.replace(/```[\s\S]*?```/g, '').match(/^#{2,3}\s+/gm)?.length || 0;
    const hId = getHeadings(idText);
    const hEn = getHeadings(enText);
    if (hId !== hEn) {
      errors.push(`Manual translation section mismatch in "${rel}": ID has ${hId} headings (##/###) while EN has ${hEn}. Align section headings across both languages.`);
    }
    for (const key of ['title:', 'description:']) {
      if (!idText.includes(key) || !enText.includes(key)) {
        errors.push(`Manual frontmatter key "${key}" missing in ID or EN for "${rel}". Ensure both frontmatters include title and description.`);
      }
    }
  }
}
for (const rel of enManualFiles) {
  if (!idSet.has(rel)) {
    errors.push(`Manual page mismatch: "site/content-src/manual/en/${rel}" has no Indonesian counterpart at "site/content-src/manual/id/${rel}". Add the Indonesian translation.`);
  }
}

// 5. Generated docs checks: version currency, broken internal links, image alt text, forbidden claims
const allDocFiles = listFiles(docsDir).filter((f) => f.endsWith('.md') || f.endsWith('.mdx'));
if (allDocFiles.length === 0) {
  errors.push(`No generated documentation files found in ${path.relative(rootDir, docsDir)}. Run "node scripts/gen-docs.mjs".`);
}

// Build valid route set from generated doc files (with Starlight /atlas-skill/ base)
const validRoutes = new Set();
for (const f of allDocFiles) {
  const rel = path.relative(docsDir, f).replaceAll('\\', '/').replace(/\.(md|mdx)$/, '');
  const route = rel.endsWith('/index')
    ? `/atlas-skill/${rel.slice(0, -'/index'.length)}/`
    : rel === 'index'
      ? '/atlas-skill/'
      : `/atlas-skill/${rel}/`;
  validRoutes.add(route);
}

for (const filePath of allDocFiles) {
  const rel = path.relative(rootDir, filePath).replaceAll('\\', '/');
  const raw = fs.readFileSync(filePath, 'utf8').replace(/\r\n/g, '\n');

  // Version currency check on generated pages
  const bannerMatch = raw.match(/pada versi `v([^`]+)`|at version `v([^`]+)`/);
  if (bannerMatch) {
    const foundVer = bannerMatch[1] || bannerMatch[2];
    if (foundVer !== expectedVersion) {
      errors.push(`Version mismatch in ${rel}: shows v${foundVer} but package.json is ${expectedVersion}. Run "node scripts/gen-docs.mjs".`);
    }
  }
  const titleVer = raw.match(/^title:\s*["']?Atlas-skill v([^\s"']+)["']?/m);
  if (titleVer && titleVer[1] !== expectedVersion) {
    errors.push(`Title version mismatch in ${rel}: shows v${titleVer[1]} instead of ${expectedVersion}. Run "node scripts/gen-docs.mjs".`);
  }

  // Strip code blocks before checking links, images, and prose claims
  const withoutCode = raw.replace(/```[\s\S]*?```/g, '').replace(/`[^`]+`/g, '');

  // Check Markdown image alt text
  for (const imgMatch of withoutCode.matchAll(/!\[([^\]]*)\]\([^)]+\)/g)) {
    if (!imgMatch[1].trim()) {
      errors.push(`Image missing alt text in ${rel}. Provide descriptive alt text inside ![alt](src).`);
    }
  }
  for (const htmlImg of withoutCode.matchAll(/<img\b[^>]*>/gi)) {
    if (!/\balt\s*=\s*["'][^"']+["']/i.test(htmlImg[0])) {
      errors.push(`HTML <img> missing non-empty alt attribute in ${rel}.`);
    }
  }

  // Check internal /atlas-skill/ links (and any MDX href="/atlas-skill/...")
  for (const m of withoutCode.matchAll(/\]\(([^)]+)\)/g)) {
    const href = m[1].trim().replace(/^<|>$/g, '');
    if (href.startsWith('http://') || href.startsWith('https://') || href.startsWith('mailto:') || href.startsWith('#')) {
      continue;
    }
    const [routeOnly] = href.split('#');
    const normalizedRoute = routeOnly.endsWith('/') ? routeOnly : `${routeOnly}/`;
    if (!routeOnly.startsWith('/atlas-skill/') || !validRoutes.has(normalizedRoute)) {
      errors.push(`Broken internal link in ${rel}: "${href}" does not match any generated page under /atlas-skill/.`);
    }
  }
  for (const m of withoutCode.matchAll(/href\s*:\s*(\/atlas-skill\/[^\s]+)|href="(\/atlas-skill\/[^"]+)"/g)) {
    const href = m[1] || m[2];
    const [routeOnly] = href.split('#');
    const normalizedRoute = routeOnly.endsWith('/') ? routeOnly : `${routeOnly}/`;
    if (!validRoutes.has(normalizedRoute)) {
      errors.push(`Broken internal component/hero href in ${rel}: "${href}" has no target page.`);
    }
  }

  // Forbidden unverified claim checks outside verbatim repo eval quotes
  if (/(\d+\+?\s*(github\s+)?stars|\d[\d,.]*\+?\s*bintang\s+github|\d[\d,.]*\+?\s*pengguna\s+aktif|\d[\d,.]*\+?\s*active\s+users|\d[\d,.]*\+?\s*(downloads|unduhan)\b)/i.test(withoutCode)) {
    errors.push(`Forbidden fabricated metric claim found in ${rel}. Remove star, user, or download counts not sourced in the repo.`);
  }
  if (/(2\.99|4\.04)/.test(raw) && (!raw.includes('6.1.0') || !raw.includes('GANTI DENGAN FOTO ASLI'))) {
    errors.push(`Empirical evaluation scores (2.99 / 4.04) in ${rel} must appear together with v6.1.0 and the "GANTI DENGAN FOTO ASLI" limitation.`);
  }
}

const result = {
  status: errors.length ? 'FAIL' : 'PASS',
  version: expectedVersion,
  checkedDocs: allDocFiles.length,
  checkedFindings: extractedCodes.size,
  errors
};

console.log(JSON.stringify(result, null, 2));
if (errors.length > 0) process.exitCode = 1;
