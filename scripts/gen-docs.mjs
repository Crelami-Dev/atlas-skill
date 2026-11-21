#!/usr/bin/env node
/**
 * Documentation generator for Atlas-skill (scripts/gen-docs.mjs).
 * Pure Node.js ESM with zero external dependencies.
 * Reads single-source-of-truth repository files and emits idempotent
 * bilingual (id/en) Markdown files under site/src/content/docs/.
 */
import fs from 'node:fs';
import path from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
export const REPO_ROOT = path.resolve(__dirname, '..');

const GITHUB_BLOB_BASE = 'https://github.com/Crelami-Dev/atlas-skill/blob/main';
const SITE_BASE = '/atlas-skill';

/**
 * Extract all diagnostic finding codes and severities from quick-check.mjs.
 * Matches fails.push("code: ..."), warns.push(`code: ...`), sweepWarns.push(`code: ...`).
 */
export function extractQuickCheckFindings(sourceText) {
  const map = new Map();
  const re = /(fails|warns|sweepWarns)\.push\((["'`])([a-z0-9-]+):/g;
  for (const m of sourceText.matchAll(re)) {
    const bucket = m[1] === 'fails' ? 'FAIL' : 'WARN';
    const code = m[3];
    if (!map.has(code)) map.set(code, new Set());
    map.get(code).add(bucket);
  }
  return [...map.entries()].map(([code, sevs]) => ({
    code,
    severity: [...sevs].sort().join('/')
  }));
}

/**
 * Parse a simple flat-list YAML dictionary (site/content-src/findings.yml)
 * without external dependencies.
 */
export function parseSimpleYamlFindings(yamlText) {
  const lines = yamlText.replace(/\r\n/g, '\n').split('\n');
  const items = [];
  let current = null;

  const unquote = (val) => {
    const trimmed = val.trim();
    if (
      (trimmed.startsWith('"') && trimmed.endsWith('"')) ||
      (trimmed.startsWith("'") && trimmed.endsWith("'"))
    ) {
      try {
        if (trimmed.startsWith('"')) return JSON.parse(trimmed);
      } catch {
        return trimmed.slice(1, -1);
      }
      return trimmed.slice(1, -1);
    }
    return trimmed;
  };

  for (const rawLine of lines) {
    const line = rawLine.trim();
    if (!line || line.startsWith('#')) continue;
    if (line.startsWith('- ')) {
      if (current) items.push(current);
      current = {};
      const rest = line.slice(2).trim();
      if (rest) {
        const idx = rest.indexOf(':');
        if (idx > 0) {
          current[rest.slice(0, idx).trim()] = unquote(rest.slice(idx + 1));
        }
      }
      continue;
    }
    if (current) {
      const idx = line.indexOf(':');
      if (idx > 0) {
        const key = line.slice(0, idx).trim();
        const val = unquote(line.slice(idx + 1));
        current[key] = val;
      }
    }
  }
  if (current) items.push(current);
  return items;
}

/**
 * Parse and validate templates/scene-catalog.json.
 */
export function loadSceneCatalog(catalogPath) {
  const raw = fs.readFileSync(catalogPath, 'utf8');
  const data = JSON.parse(raw);
  if (!data || !Array.isArray(data.scenes)) {
    throw new Error(`Invalid scene catalog: expected "scenes" array in ${catalogPath}`);
  }
  return data;
}

/**
 * Extract PROJECT_TARGETS and GLOBAL_TARGETS tables from bin/atlas-skill.mjs.
 */
export function parseAgentTargets(cliSourceText) {
  const parseBlock = (constName) => {
    const blockMatch = cliSourceText.match(
      new RegExp(`const\\s+${constName}\\s*=\\s*\\{([\\s\\S]*?)\\n\\};`)
    );
    if (!blockMatch) return [];
    const entries = [];
    for (const line of blockMatch[1].split('\n')) {
      const m = line.match(/^\s*([a-z0-9-]+)\s*:\s*\{(.+)\}\s*,?\s*$/);
      if (!m) continue;
      const agent = m[1];
      const props = {};
      for (const kv of m[2].matchAll(/([a-zA-Z0-9_]+)\s*:\s*(?:'([^']*)'|null)/g)) {
        props[kv[1]] = kv[2] === undefined ? null : kv[2];
      }
      entries.push({ agent, ...props });
    }
    return entries;
  };
  return {
    projectTargets: parseBlock('PROJECT_TARGETS'),
    globalTargets: parseBlock('GLOBAL_TARGETS')
  };
}

/**
 * Extract YAML frontmatter name & quoted description from a SKILL.md file.
 */
export function readSkillMeta(filePath) {
  const raw = fs.readFileSync(filePath, 'utf8').replace(/\r\n/g, '\n');
  const m = raw.match(/^---\nname:\s*([a-z0-9-]+)\ndescription:\s*("(?:[^"\\]|\\.)*")\n---\n/);
  return {
    name: m ? m[1] : path.basename(path.dirname(filePath)),
    description: m ? JSON.parse(m[2]) : '',
    lines: raw.split('\n').length - 1
  };
}

function escapeYamlString(value) {
  return JSON.stringify(String(value));
}

function frontmatter(fields) {
  const lines = ['---'];
  for (const [k, v] of Object.entries(fields)) {
    if (v === undefined || v === null) continue;
    lines.push(`${k}: ${escapeYamlString(v)}`);
  }
  lines.push('---', '');
  return lines.join('\n');
}

function generatedBanner(sourceRel, version, lang) {
  if (lang === 'id') {
    return `> **Catatan Sumber Otomatis:** Halaman ini dibuat otomatis dari \`${sourceRel}\` pada versi \`v${version}\`. Jangan menyunting berkas hasil ini secara langsung.\n`;
  }
  return `> **Automated Source Notice:** Automatically generated from \`${sourceRel}\` at version \`v${version}\`. Do not edit this generated file directly.\n`;
}

function englishDocBanner(sourceRel, lang) {
  if (lang !== 'id') return '';
  return `> **Halaman ini versi Inggris:** Isi referensi di bawah disalin langsung saat build dari \`${sourceRel}\` tanpa duplikasi manual agar tetap akurat terhadap repositori.\n`;
}

function stripLeadingH1(md) {
  return md.replace(/\r\n/g, '\n').replace(/^#\s+[^\n]+\n+/, '');
}

function slugifyHeading(text) {
  return text
    .toLowerCase()
    .replace(/`([^`]+)`/g, '$1')
    .replace(/[^\p{L}\p{N}\s-]/gu, '')
    .trim()
    .replace(/\s+/g, '-');
}

/**
 * Rewrite relative repo links inside Markdown (skipping fenced code blocks)
 * so every link resolves inside Astro Starlight base /atlas-skill/ or points
 * to canonical GitHub repository paths for non-doc source files.
 */
export function rewriteRepoLinks(markdown, sourceRelPath, lang) {
  const routeMap = {
    'SKILL.md': `${SITE_BASE}/${lang}/concepts/architecture/`,
    'README.md': `${SITE_BASE}/${lang}/`,
    'CHANGELOG.md': `${SITE_BASE}/${lang}/changelog/`,
    'docs/INSTALLATION.md': `${SITE_BASE}/${lang}/getting-started/install-by-agent/`,
    'docs/PROMPTS.md': `${SITE_BASE}/${lang}/guides/prompt-instructions/`,
    'package-manifest.json': `${SITE_BASE}/${lang}/concepts/architecture/`,
    'suites/project-qa/package-manifest.json': `${SITE_BASE}/${lang}/qa/project-qa-suite/`,
    'skills/atlas-frontend/SKILL.md': `${SITE_BASE}/${lang}/concepts/architecture/`,
    'skills/atlas-bug-hunter/SKILL.md': `${SITE_BASE}/${lang}/concepts/architecture/`,
    'suites/project-qa/skills/project-fix-and-verify/SKILL.md': `${SITE_BASE}/${lang}/qa/project-qa-suite/`,
    'references/phase-workflow.md': `${SITE_BASE}/${lang}/workflow/phase-workflow/`,
    'references/scenes.md': `${SITE_BASE}/${lang}/scenes/`,
    'references/loops.md': `${SITE_BASE}/${lang}/guides/loops/`,
    'references/composition.md': `${SITE_BASE}/${lang}/guides/components-and-composition/`,
    'references/composition-selection.md': `${SITE_BASE}/${lang}/guides/components-and-composition/`,
    'references/typography.md': `${SITE_BASE}/${lang}/guides/typography/`,
    'references/copy-concise.md': `${SITE_BASE}/${lang}/guides/concise-copy/`,
    'references/imagery.md': `${SITE_BASE}/${lang}/guides/imagery/`,
    'references/mobile-and-tablet.md': `${SITE_BASE}/${lang}/guides/mobile-and-tablet/`,
    'references/slop-patterns.md': `${SITE_BASE}/${lang}/anti-slop/patterns/`,
    'references/accessibility-and-behavior.md': `${SITE_BASE}/${lang}/guides/references/#accessibility-and-behavior-standards`,
    'references/animejs-v4-playbook.md': `${SITE_BASE}/${lang}/guides/references/#animejs-v4-playbook-complete-api-guide`,
    'references/brief-template.md': `${SITE_BASE}/${lang}/guides/references/#brief-template`,
    'references/creative-direction.md': `${SITE_BASE}/${lang}/guides/references/#creative-direction-making-the-site-belong-to-its-subject`,
    'references/critical-review.md': `${SITE_BASE}/${lang}/guides/references/#critical-review`,
    'references/domain-reasoning.md': `${SITE_BASE}/${lang}/guides/references/#domain-reasoning-and-research`,
    'references/engineering-and-performance.md': `${SITE_BASE}/${lang}/guides/references/#engineering-and-performance`,
    'references/idea-development.md': `${SITE_BASE}/${lang}/guides/references/#idea-development`,
    'references/interaction-design.md': `${SITE_BASE}/${lang}/guides/references/#interaction-design`,
    'references/motion.md': `${SITE_BASE}/${lang}/guides/references/#motion-in-service-of-understanding`,
    'references/research-template.md': `${SITE_BASE}/${lang}/guides/references/#research-notes-template`,
    'references/review-template.md': `${SITE_BASE}/${lang}/guides/references/#design-review-template`,
    'references/decision-log-template.md': `${SITE_BASE}/${lang}/guides/references/#decision-log-template`,
    'references/visual-review.md': `${SITE_BASE}/${lang}/guides/references/#visual-review-checklist`,
    'evals/independent-eval-2026-11-18.md': `${SITE_BASE}/${lang}/evaluation/blind-ab/`,
    'evals/independent-eval-2026-11-18.json': `${GITHUB_BLOB_BASE}/evals/independent-eval-2026-11-18.json`,
    'evals/review-2026-11-13.md': `${SITE_BASE}/${lang}/evaluation/blind-ab/#catatan-self-assessment-2026-11-13`,
    'evals/run-protocol.md': `${SITE_BASE}/${lang}/evaluation/blind-ab/`,
    'evals/rubric.md': `${SITE_BASE}/${lang}/evaluation/blind-ab/`,
    'evals/scenarios.md': `${GITHUB_BLOB_BASE}/evals/scenarios.md`
  };

  const sourceDir = path.posix.dirname(sourceRelPath.replaceAll('\\', '/'));
  const lines = markdown.replace(/\r\n/g, '\n').split('\n');
  let inFence = false;

  return lines
    .map((line) => {
      if (/^\s*```/.test(line)) {
        inFence = !inFence;
        return line;
      }
      if (inFence) return line;

      return line.replace(/(!?\[[^\]]*\]\()([^)]+)(\))/g, (full, pre, href, post) => {
        const cleanHref = href.trim().replace(/^<|>$/g, '');
        if (/^(https?:|mailto:|#)/.test(cleanHref) || cleanHref.startsWith(`${SITE_BASE}/`)) {
          return full;
        }
        const [rawPath, hashPart] = cleanHref.split('#');
        const resolved = path.posix.normalize(
          sourceDir === '.' ? rawPath : `${sourceDir}/${rawPath}`
        );
        if (routeMap[resolved]) {
          const target = routeMap[resolved];
          if (hashPart && !target.includes('#')) {
            return `${pre}${target}#${hashPart}${post}`;
          }
          return `${pre}${target}${post}`;
        }
        return `${pre}${GITHUB_BLOB_BASE}/${resolved}${hashPart ? `#${hashPart}` : ''}${post}`;
      });
    })
    .join('\n');
}

function extractSceneSectionsFromRef(scenesRefText) {
  const sections = new Map();
  const lines = scenesRefText.replace(/\r\n/g, '\n').split('\n');
  let curId = null;
  let buf = [];

  for (const line of lines) {
    const h3 = line.match(/^###\s+([a-z0-9-]+)(?:\s+\([^)]+\))?\s*$/);
    if (h3) {
      if (curId) sections.set(curId, buf.join('\n').trim());
      curId = h3[1];
      buf = [];
      continue;
    }
    if (/^##\s+/.test(line) && curId) {
      sections.set(curId, buf.join('\n').trim());
      curId = null;
      buf = [];
      continue;
    }
    if (curId) buf.push(line);
  }
  if (curId) sections.set(curId, buf.join('\n').trim());
  return sections;
}

function buildAgentTables(targets, lang) {
  const { projectTargets, globalTargets } = targets;
  const headerProject =
    lang === 'id'
      ? '| Agen (`--agent`) | Folder Skill Proyek | Direktori Rule (`--with-rules`) | Berkas Rule |\n|---|---|---|---|'
      : '| Agent (`--agent`) | Project Skills Folder | Rules Directory (`--with-rules`) | Rule File |\n|---|---|---|---|';
  const projectRows = projectTargets.map((t) => {
    const ruleDir = t.rulesDir ? `\`${t.rulesDir}\`` : '*(tidak ada)*';
    const ruleFile = t.ruleFile ? `\`${t.ruleFile}\`` : '*(lihat docs/CLAUDE.md)*';
    return `| \`${t.agent}\` | \`${t.skillsRoot}/{atlas-skill,atlas-frontend,atlas-bug-hunter}\` | ${ruleDir} | ${ruleFile} |`;
  });

  const headerGlobal =
    lang === 'id'
      ? '| Agen (`--agent` + `--global`) | Folder Skill Global (`~/...`) | Direktori Rule Global |\n|---|---|---|'
      : '| Agent (`--agent` + `--global`) | Global Skills Folder (`~/...`) | Global Rules Directory |\n|---|---|---|';
  const globalRows = globalTargets.map((t) => {
    const ruleDir = t.rulesDir ? `\`~/${t.rulesDir}/${t.ruleFile}\`` : '*(tidak ada)*';
    return `| \`${t.agent}\` | \`~/${t.skillsRoot}/{atlas-skill,atlas-frontend,atlas-bug-hunter}\` | ${ruleDir} |`;
  });

  return {
    agentTable: [headerProject, ...projectRows].join('\n'),
    globalTable: [headerGlobal, ...globalRows].join('\n')
  };
}

function ensureCleanDir(dir) {
  fs.rmSync(dir, { recursive: true, force: true });
  fs.mkdirSync(dir, { recursive: true });
}

function writeOut(outDir, relPath, content) {
  const full = path.join(outDir, relPath);
  fs.mkdirSync(path.dirname(full), { recursive: true });
  // Normalize line endings deterministically for idempotency
  const normalized = content.replace(/\r\n/g, '\n').replace(/\n*$/, '\n');
  fs.writeFileSync(full, normalized, 'utf8');
}

function copyDirFiles(srcDir, callback) {
  if (!fs.existsSync(srcDir)) return;
  const entries = fs.readdirSync(srcDir, { withFileTypes: true }).sort((a, b) => a.name.localeCompare(b.name));
  for (const entry of entries) {
    const full = path.join(srcDir, entry.name);
    if (entry.isDirectory()) copyDirFiles(full, callback);
    else if (entry.isFile()) callback(full);
  }
}

export function generateDocs({ rootDir = REPO_ROOT, outDir = path.join(REPO_ROOT, 'site/src/content/docs') } = {}) {
  const pkg = JSON.parse(fs.readFileSync(path.join(rootDir, 'package.json'), 'utf8'));
  const version = pkg.version;
  const manifest = JSON.parse(fs.readFileSync(path.join(rootDir, 'package-manifest.json'), 'utf8'));
  const qaManifest = JSON.parse(fs.readFileSync(path.join(rootDir, 'suites/project-qa/package-manifest.json'), 'utf8'));
  const cliPath = path.join(rootDir, 'bin/atlas-skill.mjs');
  const cliSource = fs.readFileSync(cliPath, 'utf8');
  const helpRun = spawnSync(process.execPath, [cliPath, '--help'], { cwd: rootDir, encoding: 'utf8' });
  if (helpRun.status !== 0) {
    throw new Error(`Failed running node bin/atlas-skill.mjs --help: ${helpRun.stderr}`);
  }
  const cliHelp = helpRun.stdout.trim().replace(/\r\n/g, '\n');

  const agentTargets = parseAgentTargets(cliSource);
  const sceneCatalog = loadSceneCatalog(path.join(rootDir, 'templates/scene-catalog.json'));
  const scenesRefText = fs.readFileSync(path.join(rootDir, 'references/scenes.md'), 'utf8');
  const sceneDetails = extractSceneSectionsFromRef(scenesRefText);

  const quickCheckSrc = fs.readFileSync(path.join(rootDir, 'skills/atlas-checker/scripts/quick-check.mjs'), 'utf8');
  const extractedFindings = extractQuickCheckFindings(quickCheckSrc);
  const yamlFindings = parseSimpleYamlFindings(
    fs.readFileSync(path.join(rootDir, 'site/content-src/findings.yml'), 'utf8')
  );
  const yamlByCode = new Map(yamlFindings.map((f) => [f.code, f]));

  ensureCleanDir(outDir);

  // Build core data structures deterministically
  const coreSkills = manifest.skills.map((s) => ({
    ...s,
    meta: readSkillMeta(path.join(rootDir, s.path))
  }));
  const topLevelSkills = coreSkills.filter((s) => s.topLevel);
  const internalModules = coreSkills.filter((s) => !s.topLevel);
  const qaSkills = qaManifest.skills.map((s) => ({
    ...s,
    meta: readSkillMeta(path.join(rootDir, s.path))
  }));

  for (const lang of ['id', 'en']) {
    const isId = lang === 'id';
    const { agentTable, globalTable } = buildAgentTables(agentTargets, lang);

    // 1. Copy & hydrate manual files
    const manualRoot = path.join(rootDir, 'site/content-src/manual', lang);
    copyDirFiles(manualRoot, (filePath) => {
      const rel = path.relative(manualRoot, filePath).replaceAll('\\', '/');
      let text = fs.readFileSync(filePath, 'utf8').replace(/\r\n/g, '\n');
      text = text
        .replaceAll('{{VERSION}}', version)
        .replaceAll('{{CLI_HELP}}', cliHelp)
        .replaceAll('{{AGENT_TABLE}}', agentTable)
        .replaceAll('{{GLOBAL_AGENT_TABLE}}', globalTable);
      writeOut(outDir, `${lang}/${rel}`, text);
    });

    // 2. Architecture & Concepts (automatic from package-manifest.json + frontmatter)
    {
      const title = isId ? 'Arsitektur: 3 Skill Utama & 10 Modul' : 'Architecture: 3 Top-Level Skills & 10 Modules';
      const desc = isId
        ? 'Daftar 3 skill inti, 10 modul fase internal, dan 3 skill Suite QA langsung dari package-manifest.json serta frontmatter SKILL.md.'
        : '3 core top-level skills, 10 internal phase modules, and 3 QA suite skills generated from package-manifest.json and SKILL.md frontmatter.';
      const lines = [
        frontmatter({ title, description: desc }),
        generatedBanner('package-manifest.json & skills/*/SKILL.md', version, lang),
        isId
          ? `Atlas-skill \`v${version}\` memisahkan antarmuka pengguna menjadi **${topLevelSkills.length} skill utama** agar menu perintah IDE tetap ringkas, sembari memuat **${internalModules.length} modul fase internal** di belakang layar (ditambah **${qaSkills.length} skill QA opsional** via \`--with-qa\`).\n`
          : `Atlas-skill \`v${version}\` exposes **${topLevelSkills.length} top-level skills** to keep your IDE slash-command list concise, orchestrating **${internalModules.length} internal phase modules** (plus **${qaSkills.length} optional QA skills** via \`--with-qa\`).\n`,
        isId ? '## 3 Skill Utama (Top-Level Entrypoints)\n' : '## 3 Top-Level Entrypoint Skills\n',
        isId
          ? '| Nama Skill | Perintah Slash | Berkas Sumber | Baris | Deskripsi Frontmatter |\n|---|---|---|---:|---|'
          : '| Skill Name | Slash Command | Source File | Lines | Frontmatter Description |\n|---|---|---|---:|---|'
      ];
      for (const s of topLevelSkills) {
        lines.push(`| \`${s.name}\` | \`/${s.name}\` | \`${s.path}\` | ${s.meta.lines} | ${s.meta.description} |`);
      }
      lines.push('');
      lines.push(isId ? '## 10 Modul Fase Internal\n' : '## 10 Internal Phase Modules\n');
      lines.push(
        isId
          ? 'Modul berikut otomatis dipanggil oleh `/atlas-skill` atau `/atlas-frontend` per fase (dan dapat dipaparkan ke menu IDE lewat `--expose-subskills`):\n'
          : 'These modules are automatically orchestrated by `/atlas-skill` or `/atlas-frontend` across Phases 0–6 (or exposed directly with `--expose-subskills`):\n'
      );
      lines.push(
        isId
          ? '| Modul | Berkas Sumber | Baris | Deskripsi Frontmatter |\n|---|---|---:|---|'
          : '| Module | Source File | Lines | Frontmatter Description |\n|---|---|---:|---|'
      );
      for (const s of internalModules) {
        lines.push(`| \`${s.name}\` | \`${s.path}\` | ${s.meta.lines} | ${s.meta.description} |`);
      }
      lines.push('');
      lines.push(isId ? '## 3 Skill Suite QA (`suites/project-qa/`)\n' : '## 3 QA Suite Skills (`suites/project-qa/`)\n');
      lines.push(
        isId
          ? `Dipasang opsional dengan \`--with-qa\` atau dipanggil otomatis pada Fase 7 \`/atlas-skill\`. Lihat detail lengkap di [Suite QA & Keamanan](${SITE_BASE}/id/qa/project-qa-suite/).\n`
          : `Included optionally with \`--with-qa\` or triggered automatically in Phase 7 of \`/atlas-skill\`. See [Project QA & Security Suite](${SITE_BASE}/en/qa/project-qa-suite/).\n`
      );
      lines.push(
        isId
          ? '| Skill QA | Berkas Sumber | Baris | Deskripsi Frontmatter |\n|---|---|---:|---|'
          : '| QA Skill | Source File | Lines | Frontmatter Description |\n|---|---|---:|---|'
      );
      for (const s of qaSkills) {
        lines.push(`| \`${s.name}\` | \`${s.path}\` | ${s.meta.lines} | ${s.meta.description} |`);
      }
      writeOut(outDir, `${lang}/concepts/architecture.md`, lines.join('\n'));
    }

    // 3. Scenes overview + individual scene pages (from scene-catalog.json + references/scenes.md)
    {
      const heavyCount = sceneCatalog.scenes.filter((s) => s.mode === 'heavy').length;
      const lightCount = sceneCatalog.scenes.filter((s) => s.mode === 'light').length;
      const title = isId ? `10 Scene & Aturan Gerak` : `10 Scenes & Scroll Motion`;
      const desc = isId
        ? 'Katalog 10 scene (scrub/play/soft/rest, aturan 15% viewport, dan anggaran per halaman) otomatis dari templates/scene-catalog.json.'
        : 'All 10 scenes, scrub/play/soft/rest modes, 15% visibility trigger, and page budget extracted from templates/scene-catalog.json.';
      const lines = [
        frontmatter({ title, description: desc }),
        generatedBanner('templates/scene-catalog.json & references/scenes.md', version, lang),
        isId
          ? `Atlas menyediakan **${sceneCatalog.scenes.length} scene** (**${heavyCount} heavy**, **${lightCount} light**) yang dipilih melalui \`node scripts/deal-scene.mjs\` berdasarkan jenis subjek.\n`
          : `Atlas ships **${sceneCatalog.scenes.length} scenes** (**${heavyCount} heavy**, **${lightCount} light**) selected via \`node scripts/deal-scene.mjs\` based on subject fit.\n`,
        isId ? '## Anggaran & Empat Mode Gerak\n' : '## Budget & Four Motion Modes\n',
        `> ${sceneCatalog.rule}\n`,
        isId
          ? '| Mode (`<html data-atlas-motion>`) | Kondisi Aktif | Perilaku Scene & Reveal |\n|---|---|---|'
          : '| Mode (`<html data-atlas-motion>`) | Active Condition | Scene & Reveal Behavior |\n|---|---|---|',
        isId
          ? '| `scrub` | Desktop `>= 1024 px`, gerak aktif | Scene heavy menempel (`sticky`) dan progress digerakkan oleh scroll; reveal di **15%**. |'
          : '| `scrub` | Desktop `>= 1024 px`, normal motion | Heavy scene pins (`sticky`) and scrubs progress from scroll position; reveals at **15%**. |',
        isId
          ? '| `play` | Ponsel & tablet `< 1024 px` (atau berlebih anggaran) | Setiap scene diputar **sekali** saat **15%** terlihat (~1.7 s, tanpa pinning/scroll-jacking). |'
          : '| `play` | Phones & tablets `< 1024 px` (or over pinned budget) | Every scene plays **once** smoothly when **15%** visible (~1.7 s, zero pinning). |',
        isId
          ? '| `soft` | `prefers-reduced-motion: reduce` | Hanya pudar halus (*opacity-only*) pada **15%**; scene tampil dalam keadaan akhir tenang. |'
          : '| `soft` | `prefers-reduced-motion: reduce` | Opacity-only fades at **15%**; scenes show their finished calm rest layout. |',
        isId
          ? '| `rest` | Tanpa JavaScript / CDN Anime.js gagal muat | Seluruh konten tetap terbaca penuh tanpa `opacity: 0` statis. |'
          : '| `rest` | No JS or Anime.js unavailable | Full finished layout remains immediately legible with zero static `opacity: 0`. |',
        '',
        isId ? '## Daftar Lengkap Scene (Otomatis dari Katalog)\n' : '## Complete Scene Catalog (Generated)\n',
        isId
          ? '| ID Scene | Mode | Keluarga | Cocok Untuk (`fits`) | Biaya |\n|---|---|---|---|---|'
          : '| Scene ID | Mode | Family | Best Fit (`fits`) | Cost |\n|---|---|---|---|---|'
      ];
      for (const sc of sceneCatalog.scenes) {
        lines.push(
          `| [\`${sc.id}\`](${SITE_BASE}/${lang}/scenes/${sc.id}/) | \`${sc.mode}\` | \`${sc.family}\` | ${sc.fits.map((f) => `\`${f}\``).join(', ')} | \`${sc.cost}\` |`
        );
      }
      lines.push('');
      lines.push(englishDocBanner('references/scenes.md', lang));
      lines.push(isId ? '## Referensi Penggunaan (`references/scenes.md`)\n' : '## Reference Usage (`references/scenes.md`)\n');
      lines.push(rewriteRepoLinks(stripLeadingH1(scenesRefText), 'references/scenes.md', lang));
      writeOut(outDir, `${lang}/scenes/index.md`, lines.join('\n'));

      // Individual page per scene
      for (const sc of sceneCatalog.scenes) {
        const refSnippet = sceneDetails.get(sc.id) || '';
        const scLines = [
          frontmatter({
            title: `Scene: ${sc.id}`,
            description: `${sc.mode.toUpperCase()} (${sc.family}) — ${sc.look}`
          }),
          generatedBanner('templates/scene-catalog.json & references/scenes.md', version, lang),
          isId
            ? `**\`${sc.id}\`** adalah scene mode **\`${sc.mode}\`** dari keluarga **\`${sc.family}\`** (estimasi biaya render: \`${sc.cost}\`).\n`
            : `**\`${sc.id}\`** is a **\`${sc.mode}\`** scene in the **\`${sc.family}\`** family (cost: \`${sc.cost}\`).\n`,
          isId ? '## Spesifikasi Katalog\n' : '## Catalog Specification\n',
          `| ${isId ? 'Atribut' : 'Property'} | ${isId ? 'Nilai' : 'Value'} |\n|---|---|`,
          `| ID | \`${sc.id}\` |`,
          `| Mode | \`${sc.mode}\` |`,
          `| Family | \`${sc.family}\` |`,
          `| Fits | ${sc.fits.map((f) => `\`${f}\``).join(', ')} |`,
          `| Look | ${sc.look} |`,
          `| Needs | ${sc.needs} |`,
          `| Never | ${sc.never} |`,
          `| Rest state | ${sc.rest} |`,
          `| Cost | \`${sc.cost}\` |`,
          ''
        ];
        if (refSnippet) {
          scLines.push(englishDocBanner('references/scenes.md', lang));
          scLines.push(isId ? '## Markup & Catatan Teknis\n' : '## Markup & Implementation Notes\n');
          scLines.push(rewriteRepoLinks(refSnippet, 'references/scenes.md', lang));
        }
        scLines.push('');
        scLines.push(
          isId
            ? `[← Kembali ke daftar semua scene](${SITE_BASE}/id/scenes/)`
            : `[← Back to all scenes](${SITE_BASE}/en/scenes/)`
        );
        writeOut(outDir, `${lang}/scenes/${sc.id}.md`, scLines.join('\n'));
      }
    }

    // 4. Copied reference docs at build time (no duplicated prose!)
    const copiedRefs = [
      {
        outSlug: 'workflow/phase-workflow.md',
        titleId: 'Alur Kerja Fase 0–7',
        titleEn: 'Phase Workflow (Phases 0–7)',
        descId: 'Urutan teknis brief, riset, desain token, bangun UI + Anime.js v4, gate, tinjauan kritikus, hingga QA Fase 7.',
        descEn: 'Technical execution steps for brief, research, tokens, implementation, gates, critique, and Phase 7 QA.',
        srcFiles: ['references/phase-workflow.md'],
        summaryId:
          'Alur kerja Atlas berjalan berurutan dari **Fase 0** (pemilihan arah `deal-direction.mjs`), **Fase 1** (`design-brief.md` + `check-brief.mjs`), **Fase 2** (riset & aset nyata `fetch-photos.mjs`), **Fase 3** (`design-tokens.css`), **Fase 4** (implementasi HTML/CSS/Anime.js v4 15% reveal), **Fase 5** (`run-gates.mjs` & `quick-check.mjs`), **Fase 6** (tinjauan 7-sumbu `atlas-critic`), hingga **Fase 7** (Suite QA & perbaikan otomatis untuk `/atlas-skill`).\n'
      },
      {
        outSlug: 'guides/loops.md',
        titleId: 'Loop Otomatis (atlas-loops)',
        titleEn: 'Self-Playing Loops (atlas-loops)',
        descId: 'Aturan WCAG 2.2.2 tombol jeda, paused off-screen, reduced-motion, rotating words, ticker, dan demo ulang.',
        descEn: 'Polite self-playing demos, rotating words, seamless tickers, ambient FX, off-screen pause, and 44px pause controls.',
        srcFiles: ['references/loops.md'],
        summaryId:
          'Setiap animasi yang berjalan mandiri lebih dari 5 detik wajib memakai `atlas-loops.mjs` + `atlas-loops.css`: dimulai pada **15% visibilitas**, **berhenti saat di luar layar**, menyediakan **tombol jeda >= 44 px** (atau `[data-loops-toggle]` global), dan **berdiri diam** ketika `prefers-reduced-motion` aktif.\n'
      },
      {
        outSlug: 'guides/components-and-composition.md',
        titleId: 'Komposisi, Arketipe & Kepadatan Visual',
        titleEn: 'Composition, Archetypes & Visual Density',
        descId: '10 arketipe struktural (termasuk larangan pola workbench untuk restoran/portofolio), ukuran baca 60-75ch, dan teks min 16px.',
        descEn: '10 structural macro archetypes, workbench hero restriction, 16px minimum body copy, and 60-75ch reading measure.',
        srcFiles: ['references/composition-selection.md', 'references/composition.md'],
        summaryId:
          'Atlas menetapkan **10 arketipe komposisi** untuk mencegah semua domain memakai tata letak hero 2 kolom + filter yang sama, disertai standar keterbacaan: body text **>= 16 px**, panjang baris **60ch–75ch**, dan variasi minimal **3 peran permukaan warna**.\n'
      },
      {
        outSlug: 'guides/typography.md',
        titleId: 'Tipografi sebagai Sistem Desain & Rekayasa',
        titleEn: 'Typography Design & Engineering System',
        descId: 'Batas maksimal 2 keluarga proporsional (+1 mono), fluid scale dengan clamp(), angka tabular, dan uji fallback.',
        descEn: 'Content-first family selection, role scale, 65ch measure, tabular numerals, wrapping checks, and loading fallbacks.',
        srcFiles: ['references/typography.md'],
        summaryId:
          'Atlas membatasi tipografi hingga **maksimal 2 keluarga font proporsional** (Display dan Body) ditambah **1 monospace opsional**, mengutamakan keterbacaan pada bahasa target (ID/EN) pada lebar sempit `320 px` dan `375 px`.\n'
      },
      {
        outSlug: 'guides/concise-copy.md',
        titleId: 'Teks Ringkas (check-copy.mjs)',
        titleEn: 'Concise Copy Budgets (check-copy.mjs)',
        descId: 'Anggaran kata layar pertama (<55 kata), panjang H1 2-8 kata, tombol diawali kata kerja, dan larangan tombol kabur.',
        descEn: 'First-screen word budgets, curiosity + concrete results, paragraph limits, and verb-led CTA button labels.',
        srcFiles: ['references/copy-concise.md'],
        summaryId:
          'Penegakan otomatis pada Gate 4b (`scripts/check-copy.mjs`): judul layar utama **2–8 kata**, satu baris pendukung jelas, **total layar pertama di bawah 55 kata**, fakta konkret wajib hadir di layar awal, serta tombol aksi **diawali kata kerja** tanpa label kabur.\n'
      },
      {
        outSlug: 'guides/imagery.md',
        titleId: 'Citra, AI Image & Foto Berlisensi (fetch-photos.mjs)',
        titleEn: 'Visual Assets, Image Generation & Licensed Photography',
        descId: 'Pohon keputusan media, relevansi foto, larangan wireframe SVG/lencana placeholder UI, serta kredensial credits.json.',
        descEn: 'Media asset decision tree, photo relevance gates, strict ban on crude wireframe SVGs and leaked placeholder badges.',
        srcFiles: ['references/imagery.md'],
        summaryId:
          'Pada domain visual, Atlas mewajibkan gambar raster nyata (hasil generator AI atau foto berlisensi Wikimedia CC0/CC-BY/Public-Domain lewat `scripts/fetch-photos.mjs`) dan **melarang keras** wireframe `<svg>` kasar maupun teks instruksi placeholder seperti `"GANTI DENGAN FOTO ASLI"` tampil di UI pengunjung.\n'
      },
      {
        outSlug: 'guides/mobile-and-tablet.md',
        titleId: 'Mobile & Tablet (3 Pita Ukuran)',
        titleEn: 'Phones & Tablets (Three Size Bands)',
        descId: 'Pola ponsel vs tablet potret (600-1023 px), larangan mobile-long-stack dan half-empty-row, serta mode play di <1024 px.',
        descEn: 'Intentional small-screen compositions using .atlas-carousel, .atlas-bento, equal-width stacked CTAs, and play-once scenes.',
        srcFiles: ['references/mobile-and-tablet.md'],
        summaryId:
          'Menetapkan rancangan tersendiri untuk tiga pita ukuran: **Ponsel (`<= 599 px`)**, **Tablet Potret (`600–1023 px`)**, dan **Desktop (`>= 1024 px`)**, mengganti tumpukan panjang kartu menjadi `.atlas-carousel` atau `.atlas-bento`, serta menjalankan seluruh scene satu kali (`play`) di bawah `1024 px`.\n'
      },
      {
        outSlug: 'anti-slop/patterns.md',
        titleId: 'Anti-Slop: 18 Pola yang Ditolak',
        titleEn: '18 Detectable AI Slop Patterns',
        descId: 'Daftar lengkap 18 pola AI slop (gradasi neon, emoji UI, opacity: 0 statis, placeholder bocor) beserta cara deteksi & penggantinya.',
        descEn: 'Reference table of all 18 AI slop patterns detected by slop-scan.mjs and visual critic review.',
        srcFiles: ['references/slop-patterns.md'],
        summaryId:
          'Atlas memetakan **18 pola AI slop** yang paling sering merusak antarmuka hasil AI. Sebanyak **12 pola** terdeteksi otomatis secara statis/browser oleh `slop-scan.mjs`, `check-motion-v4.mjs`, `check-tokens.mjs`, dan `quick-check.mjs`, sedangkan sisanya diaudit saat inspeksi screenshot.\n'
      },
      {
        outSlug: 'guides/prompt-instructions.md',
        titleId: 'Panduan Instruksi Prompt',
        titleEn: 'Prompt Instructions Guide',
        descId: 'Daftar prompt siap pakai untuk /atlas-skill, /atlas-frontend, /atlas-bug-hunter, Compact Track, dan Redesign 2 Tahap.',
        descEn: 'Ready-to-use prompt templates for /atlas-skill, /atlas-frontend, /atlas-bug-hunter, Compact Track, and Two-Stage Redesign.',
        srcFiles: ['docs/PROMPTS.md'],
        skipEnglishNote: true,
        summaryId: ''
      }
    ];

    for (const ref of copiedRefs) {
      const chunks = [
        frontmatter({
          title: isId ? ref.titleId : ref.titleEn,
          description: isId ? ref.descId : ref.descEn
        }),
        generatedBanner(ref.srcFiles.join(' & '), version, lang)
      ];
      if (isId && ref.summaryId) {
        chunks.push(ref.summaryId);
      }
      if (!ref.skipEnglishNote) {
        chunks.push(englishDocBanner(ref.srcFiles.join(', '), lang));
      } else if (!isId) {
        chunks.push('> **Note:** The canonical prompt handbook in `docs/PROMPTS.md` is maintained in Indonesian with universal slash-command templates usable for both Indonesian and English projects.\n');
      }
      for (const relSrc of ref.srcFiles) {
        const raw = fs.readFileSync(path.join(rootDir, relSrc), 'utf8');
        const headingTitle = raw.match(/^#\s+([^\n]+)/)?.[1] || relSrc;
        if (ref.srcFiles.length > 1) {
          chunks.push(`\n## ${headingTitle} (\`${relSrc}\`)\n`);
        }
        chunks.push(rewriteRepoLinks(stripLeadingH1(raw), relSrc, lang));
      }
      writeOut(outDir, `${lang}/${ref.outSlug}`, chunks.join('\n'));
    }

    // 5. Additional references index page (references/*.md not given standalone pages)
    {
      const extraRefs = [
        { slug: 'creative-direction', file: 'references/creative-direction.md' },
        { slug: 'animejs-v4-playbook', file: 'references/animejs-v4-playbook.md' },
        { slug: 'visual-review', file: 'references/visual-review.md' },
        { slug: 'critical-review', file: 'references/critical-review.md' },
        { slug: 'accessibility-and-behavior', file: 'references/accessibility-and-behavior.md' },
        { slug: 'interaction-design', file: 'references/interaction-design.md' },
        { slug: 'domain-reasoning', file: 'references/domain-reasoning.md' },
        { slug: 'engineering-and-performance', file: 'references/engineering-and-performance.md' },
        { slug: 'idea-development', file: 'references/idea-development.md' },
        { slug: 'motion', file: 'references/motion.md' },
        { slug: 'brief-template', file: 'references/brief-template.md' },
        { slug: 'research-template', file: 'references/research-template.md' },
        { slug: 'review-template', file: 'references/review-template.md' },
        { slug: 'decision-log-template', file: 'references/decision-log-template.md' }
      ];
      const title = isId ? 'Referensi Teknis Tambahan' : 'Additional Technical References';
      const desc = isId
        ? 'Salinan langsung dokumen referensi lanjutan (Anime.js v4 playbook, arah kreatif, tinjauan visual, dan templat brief) dari folder references/.'
        : 'Verbatim copies of remaining technical guides in references/ (Anime.js v4 playbook, creative direction, visual review, brief templates).';
      const chunks = [
        frontmatter({ title, description: desc }),
        generatedBanner('references/*.md', version, lang),
        englishDocBanner('references/*.md', lang),
        isId ? '## Daftar Isi Bagian\n' : '## Sections Included\n'
      ];
      const parsedExtra = extraRefs.map((er) => {
        const raw = fs.readFileSync(path.join(rootDir, er.file), 'utf8');
        const headingTitle = raw.match(/^#\s+([^\n]+)/)?.[1] || er.slug;
        return { ...er, raw, headingTitle, anchor: slugifyHeading(headingTitle) };
      });
      for (const er of parsedExtra) {
        chunks.push(`- [\`${er.file}\` — ${er.headingTitle}](#${er.anchor})`);
      }
      for (const er of parsedExtra) {
        chunks.push(`\n## ${er.headingTitle}\n`);
        chunks.push(`*${isId ? 'Sumber' : 'Source'}: \`${er.file}\`*\n`);
        chunks.push(rewriteRepoLinks(stripLeadingH1(er.raw), er.file, lang));
      }
      writeOut(outDir, `${lang}/guides/references.md`, chunks.join('\n'));
    }

    // 6. Kamus Kode Temuan (quick-check.mjs + site/content-src/findings.yml)
    {
      const title = isId ? 'Kamus Kode Temuan (quick-check.mjs)' : 'Findings Dictionary (quick-check.mjs)';
      const desc = isId
        ? `Daftar otomatis seluruh ${extractedFindings.length} kode temuan quick-check.mjs beserta arti, penyebab, dan perbaikannya.`
        : `Complete reference for all ${extractedFindings.length} diagnostic finding codes extracted from quick-check.mjs with meaning, root cause, and fix.`;
      const lines = [
        frontmatter({ title, description: desc }),
        generatedBanner('skills/atlas-checker/scripts/quick-check.mjs & site/content-src/findings.yml', version, lang),
        isId
          ? `Setiap kode di bawah ini diekstrak secara otomatis dari \`skills/atlas-checker/scripts/quick-check.mjs\` (**${extractedFindings.length} kode unik**) dan dipadankan dengan kamus penjelasan di \`site/content-src/findings.yml\`. Build dokumentasi akan gagal bila ada kode baru yang belum dijelaskan.\n`
          : `Every finding code below is automatically extracted from \`skills/atlas-checker/scripts/quick-check.mjs\` (**${extractedFindings.length} distinct codes**) and paired with \`site/content-src/findings.yml\`. Builds fail automatically if any code lacks an entry.\n`,
        isId ? '## Indeks Cepat Kode Temuan\n' : '## Quick Code Index\n',
        isId
          ? '| Kode Temuan | Tingkat | Ringkasan |\n|---|---|---|'
          : '| Finding Code | Severity | Summary |\n|---|---|---|'
      ];

      for (const item of extractedFindings) {
        const entry = yamlByCode.get(item.code);
        const sev = entry?.severity || item.severity;
        const summary = entry ? (isId ? entry.meaning_id : entry.meaning_en) : 'Missing entry in findings.yml';
        lines.push(`| [\`${item.code}\`](#${item.code}) | \`${sev}\` | ${summary} |`);
      }

      lines.push('');
      lines.push(isId ? '## Rincian Penyebab & Perbaikan\n' : '## Detailed Causes & Fixes\n');

      for (const item of extractedFindings) {
        const entry = yamlByCode.get(item.code);
        const sev = entry?.severity || item.severity;
        lines.push(`### \`${item.code}\``);
        lines.push('');
        lines.push(`- **${isId ? 'Tingkat' : 'Severity'}:** \`${sev}\``);
        if (entry) {
          lines.push(`- **${isId ? 'Arti' : 'Meaning'}:** ${isId ? entry.meaning_id : entry.meaning_en}`);
          lines.push(`- **${isId ? 'Penyebab umum' : 'Common cause'}:** ${isId ? entry.cause_id : entry.cause_en}`);
          lines.push(`- **${isId ? 'Cara memperbaiki' : 'How to fix'}:** ${isId ? entry.fix_id : entry.fix_en}`);
        }
        lines.push('');
      }
      writeOut(outDir, `${lang}/checks/findings-dictionary.md`, lines.join('\n'));
    }

    // 7. Suite QA (suites/project-qa/)
    {
      const title = isId ? 'Suite QA & Keamanan (--with-qa)' : 'QA & Security Suite (--with-qa)';
      const desc = isId
        ? 'Penjelasan project-bug-hunter, project-security-auditor, project-fix-and-verify, aturan gerbang QA, dan kebutuhan Python 3.'
        : 'Overview of project-bug-hunter, project-security-auditor, project-fix-and-verify, governance rules, and Python 3 requirement.';
      const gateRule = fs.readFileSync(path.join(rootDir, 'suites/project-qa/rules/qa-security-gate.md'), 'utf8')
        .replace(/\r\n/g, '\n')
        .replace(/^---[\s\S]*?---\n/, '');
      const chunks = [
        frontmatter({ title, description: desc }),
        generatedBanner('suites/project-qa/package-manifest.json & suites/project-qa/skills/*/SKILL.md', version, lang),
        isId
          ? `Suite QA & Keamanan di \`suites/project-qa/\` (versi \`${qaManifest.version}\`) merupakan paket skill pendamping yang dapat dipasang lewat \`--with-qa\` atau dijalankan otomatis pada **Fase 7** di \`/atlas-skill\`. **Seluruh skrip pemindai statis, dom probe, dan pemeriksa CVE di suite ini membutuhkan Python 3.**\n`
          : `The QA & Security Suite under \`suites/project-qa/\` (version \`${qaManifest.version}\`) adds three specialized skills installed via \`--with-qa\` and invoked automatically during Phase 7 of \`/atlas-skill\`. **Its static inventory, visual bug probe, and CVE scripts require Python 3.**\n`,
        isId ? '## Daftar Skill Suite QA\n' : '## QA Suite Skills\n',
        isId
          ? '| Skill | Peran | Sumber |\n|---|---|---|'
          : '| Skill | Role | Source |\n|---|---|---|',
        ...qaSkills.map((s) => `| \`${s.name}\` | ${s.meta.description} | \`${s.path}\` |`),
        '',
        isId ? '## Mode Baca-Saja vs Perbaikan Otomatis\n' : '## Read-Only Discovery vs Automated Remediation\n',
        isId
          ? '- **`/atlas-bug-hunter` (Mode A — Bawaan):** Bersifat baca-saja (*read-only*); tidak menyentuh kode proyek dan hanya menghasilkan laporan Markdown.\n- **`/atlas-bug-hunter` (Mode B — Saat diminta memperbaiki) atau `/atlas-skill` Fase 7:** Mengaktifkan `project-fix-and-verify` untuk menambal akar masalah, menguji fitur secara menyeluruh, lalu mengaudit ulang.\n- **Audit CVE luring:** Jalankan `live_cve_osv_check.py --offline-parse-only` bila tidak ingin mengirim daftar paket ke OSV.dev / NVD / CISA.\n'
          : '- **`/atlas-bug-hunter` (Mode A — Default):** Strictly read-only discovery producing a Markdown report without editing source files.\n- **`/atlas-bug-hunter` (Mode B — When commanded to fix) or `/atlas-skill` Phase 7:** Activates `project-fix-and-verify` for root-cause patching, feature testing, and zero-defect re-audits.\n- **Offline CVE parsing:** Pass `--offline-parse-only` to `live_cve_osv_check.py` to scan manifests without external OSV/NVD/CISA API queries.\n',
        englishDocBanner('suites/project-qa/rules/qa-security-gate.md', lang),
        isId ? '## Aturan Gerbang QA (`qa-security-gate.md`)\n' : '## QA Governance Gate (`qa-security-gate.md`)\n',
        stripLeadingH1(gateRule)
      ];
      writeOut(outDir, `${lang}/qa/project-qa-suite.md`, chunks.join('\n'));
    }

    // 8. Evaluasi Empiris (evals/)
    {
      const title = isId ? 'Evaluasi Empiris (Blind A/B)' : 'Empirical Evaluation (Blind A/B)';
      const desc = isId
        ? 'Metodologi blind A/B, hasil Round 3 versi 6.1.0 (2.99 vs 4.04), temuan kritis, perbaikan v7.0.0, dan batasan penuh.'
        : 'Blind A/B methodology, v6.1.0 Round 3 benchmark (2.99 vs 4.04), open defect, v7.0.0 fix status, and full limitations.';
      const evalSummary = fs.readFileSync(path.join(rootDir, 'evals/independent-eval-2026-11-18.md'), 'utf8');
      const runProtocol = fs.readFileSync(path.join(rootDir, 'evals/run-protocol.md'), 'utf8');
      const rubric = fs.readFileSync(path.join(rootDir, 'evals/rubric.md'), 'utf8');
      const selfReview = fs.readFileSync(path.join(rootDir, 'evals/review-2026-11-13.md'), 'utf8');

      const chunks = [
        frontmatter({ title, description: desc }),
        generatedBanner('evals/independent-eval-2026-11-18.md & evals/run-protocol.md', version, lang),
        isId
          ? `> **Batasan Wajib Dibaca:** Skor berikut (` +
            `2.99` +
            ` vs ` +
            `4.04` +
            `, ` +
            `10/10` +
            ` kasus) berasal dari pengujian pada **versi \`6.1.0\`** dengan pembanding **Baseline A yang dibangun secara bersih tanpa skill Atlas** (bukan dibandingkan dengan skill atau alat lain). Pada versi \`6.1.0\`, juri independen menolak kelulusan karena **1 temuan kritis terbuka**: lencana \`"GANTI DENGAN FOTO ASLI"\` muncul di UI pengunjung pada 5/10 kasus visual. Temuan tersebut telah **diperbaiki dan diblokir otomatis pada \`v${version}\`**, namun hasil \`v${version}\` **belum dievaluasi ulang secara independen**.\n`
          : `> **Mandatory Scope & Limitations:** The figures below (` +
            `2.99` +
            ` vs ` +
            `4.04` +
            `, ` +
            `10/10` +
            ` wins) were recorded on **package version \`6.1.0\`** comparing against a **clean Baseline A built without the skill** (not benchmarked against third-party skills). On \`6.1.0\`, the independent judge marked graduation **Not ready** due to **1 open critical defect pattern**: visible \`"GANTI DENGAN FOTO ASLI"\` badges in 5/10 visual cases. That defect has been **fixed and blocked automatically in \`v${version}\`**, and **fresh independent re-evaluation is still pending**.\n`,
        englishDocBanner('evals/independent-eval-2026-11-18.md', lang),
        isId ? '## Ringkasan Evaluasi Independen (`evals/independent-eval-2026-11-18.md`)\n' : '## Independent Evaluation Summary (`evals/independent-eval-2026-11-18.md`)\n',
        rewriteRepoLinks(stripLeadingH1(evalSummary), 'evals/independent-eval-2026-11-18.md', lang),
        '',
        isId ? '## Protokol Pengujian Blind (`evals/run-protocol.md`)\n' : '## Blind Evaluation Protocol (`evals/run-protocol.md`)\n',
        rewriteRepoLinks(stripLeadingH1(runProtocol), 'evals/run-protocol.md', lang),
        '',
        isId ? '## Rubrik Penilaian (`evals/rubric.md`)\n' : '## Scoring Rubric (`evals/rubric.md`)\n',
        rewriteRepoLinks(stripLeadingH1(rubric), 'evals/rubric.md', lang),
        '',
        isId
          ? '## Catatan Self-Assessment 2026-11-13\n'
          : '## Self-Assessment Note 2026-11-13\n',
        isId
          ? '> Catatan: `evals/review-2026-11-13.md` adalah evaluasi mandiri (*self-assessment*) oleh pembuat paket, **bukan** benchmark blind A/B independen.\n'
          : '> Note: `evals/review-2026-11-13.md` is an authoring-agent self-assessment, **not** an independent blind A/B benchmark.\n',
        rewriteRepoLinks(stripLeadingH1(selfReview), 'evals/review-2026-11-13.md', lang)
      ];
      writeOut(outDir, `${lang}/evaluation/blind-ab.md`, chunks.join('\n'));
    }

    // 9. Changelog (CHANGELOG.md)
    {
      const changelogText = fs.readFileSync(path.join(rootDir, 'CHANGELOG.md'), 'utf8');
      const title = isId ? `Riwayat Versi (v${version})` : `Changelog (v${version})`;
      const desc = isId
        ? 'Catatan perubahan lengkap tiap versi yang diambil otomatis dari CHANGELOG.md di akar repositori.'
        : 'Complete version history synchronized automatically from repository CHANGELOG.md.';
      const chunks = [
        frontmatter({ title, description: desc }),
        generatedBanner('CHANGELOG.md', version, lang),
        englishDocBanner('CHANGELOG.md', lang),
        rewriteRepoLinks(stripLeadingH1(changelogText), 'CHANGELOG.md', lang)
      ];
      writeOut(outDir, `${lang}/changelog/index.md`, chunks.join('\n'));
    }
  }

  return {
    version,
    findingCount: extractedFindings.length,
    sceneCount: sceneCatalog.scenes.length,
    topLevelCount: topLevelSkills.length,
    moduleCount: internalModules.length,
    qaSkillCount: qaSkills.length
  };
}

if (process.argv[1] && path.resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const summary = generateDocs();
  console.log(JSON.stringify({ status: 'ok', ...summary }));
}
