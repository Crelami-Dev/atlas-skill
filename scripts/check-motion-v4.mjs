#!/usr/bin/env node
/**
 * Deterministic Anime.js v4 Motion & Accessibility Gate (check-motion-v4.mjs)
 * Validates Anime.js v4 syntax, createScope cleanup, reduced-motion safety, and SSR visibility.
 */
import fs from 'node:fs';
import path from 'node:path';

const args = process.argv.slice(2);
if (args.includes('--help') || args.includes('-h')) {
  console.log('Usage: node check-motion-v4.mjs [project-root]\nValidates Anime.js v4 syntax, createScope cleanup, reduced-motion safety, and SSR visibility.');
  process.exit(0);
}

const root = path.resolve(args[0] || '.');
const ignoreDirs = new Set(['node_modules', '.git', '.agents', '.claude', '.cursor', '.windsurf', '.clinerules', '.atlas-skill-backups', 'dist', 'build', '.next', 'out', 'maintenance']);
const codeExts = new Set(['.js', '.jsx', '.ts', '.tsx', '.mjs', '.vue', '.svelte', '.astro', '.html']);
const cssExts = new Set(['.css', '.html', '.vue', '.svelte', '.astro']);

const findings = [];
let usesAnimeJs = false;
let hasReducedMotionGuard = false;

function addFinding(level, id, file, index, text, message) {
  const rel = path.relative(root, file).replaceAll('\\', '/');
  const line = text.slice(0, Math.max(0, index)).split('\n').length;
  findings.push({ level, id, file: rel, line, message });
}

function walk(dir, out = []) {
  if (!fs.existsSync(dir)) return out;
  for (const entry of fs.readdirSync(dir, { withFileTypes: true })) {
    if (ignoreDirs.has(entry.name) || entry.isSymbolicLink()) continue;
    const full = path.join(dir, entry.name);
    if (entry.isDirectory()) walk(full, out);
    else if (entry.isFile() && (codeExts.has(path.extname(entry.name).toLowerCase()) || cssExts.has(path.extname(entry.name).toLowerCase()))) out.push(full);
  }
  return out;
}

for (const file of walk(root)) {
  const ext = path.extname(file).toLowerCase();
  const text = fs.readFileSync(file, 'utf8');

  if (/prefers-reduced-motion/i.test(text) || /reduceMotion/.test(text)) {
    hasReducedMotionGuard = true;
  }

  if (codeExts.has(ext)) {
    const fileImportsAnime =
      /from\s+['"](?:[^'"]*\/)?animejs(?:@[^/'"]+)?(?:\/[^'"]*)?['"]|import\(\s*['"](?:[^'"]*\/)?animejs(?:@[^/'"]+)?(?:\/[^'"]*)?['"]\s*\)|require\(\s*['"]animejs['"]\s*\)/.test(text);
    if (fileImportsAnime) usesAnimeJs = true;

    // 1. Block v3 default or namespace import: import anime from 'animejs' or import * as anime from 'animejs'
    for (const m of text.matchAll(/\bimport\s+(?:anime|\*\s+as\s+\w+)\s*(?:,|\s+from)\s*['"](?:[^'"]*\/)?animejs(?:@[^/'"]+)?(?:\/[^'"]*)?['"]|const\s+anime\s*=\s*require\(\s*['"]animejs['"]\s*\)/g)) {
      usesAnimeJs = true;
      addFinding('error', 'anime-v3-default-import', file, m.index, text,
        "Anime.js v4 does not expose a default/namespace 'anime' export. Use named imports: import { animate, createTimeline, createScope, stagger, spring, onScroll } from 'animejs'.");
    }

    // 2. Block v3 global object API calls: anime({...}), anime.default({...}), anime.timeline(), anime.stagger(), anime.set()
    for (const m of text.matchAll(/\banime\s*\(\s*\{|\banime\.(default|timeline|stagger|set|remove|running|random)\b/g)) {
      usesAnimeJs = true;
      addFinding('error', 'anime-v3-legacy-call', file, m.index, text,
        "Anime.js v3 API detected ('anime(...)' / 'anime.default' / 'anime.timeline' / 'anime.stagger'). In v4 use: animate(targets, params), createTimeline(), stagger(), utils.set(), utils.remove().");
    }

    // 3. Block v3 targets inside options object: animate({ targets: ... })
    for (const m of text.matchAll(/\banimate\s*\(\s*\{\s*targets\s*:/g)) {
      addFinding('error', 'anime-v3-targets-key', file, m.index, text,
        "In Anime.js v4, 'targets' must be the first argument: animate(targets, { opacity: [0, 1], y: [16, 0] }), not a property inside options.");
    }

    // 4. Block v3 'easing:' property inside Anime.js calls
    if (fileImportsAnime) {
      for (const m of text.matchAll(/\beasing\s*:\s*['"`a-zA-Z]/g)) {
        addFinding('error', 'anime-v3-easing-prop', file, m.index, text,
          "In Anime.js v4, 'easing' was renamed to 'ease' (e.g., ease: 'outQuart' or ease: spring({ bounce: 0.2, duration: 500 })).");
      }

      // 5. Block v3 ease names starting with 'easeOut...' / 'easeInOut...' / 'easeIn...'
      for (const m of text.matchAll(/\bease\s*:\s*['"]ease(?:In|Out|InOut)[A-Z]\w*['"]/g)) {
        addFinding('error', 'anime-v3-ease-name', file, m.index, text,
          "Anime.js v4 ease names drop the 'ease' prefix. Replace e.g. 'easeOutExpo' -> 'outExpo', 'easeInOutQuad' -> 'inOutQuad', 'easeOutQuart' -> 'outQuart'.");
      }

      // 6. Block v3 direction: 'alternate' | 'reverse'
      for (const m of text.matchAll(/\bdirection\s*:\s*['"](?:alternate|reverse)['"]/g)) {
        addFinding('error', 'anime-v3-direction-prop', file, m.index, text,
          "In Anime.js v4, use boolean 'alternate: true' or 'reversed: true' instead of direction: 'alternate'.");
      }

      // 7. Warn if component uses animate/createTimeline in React/Vue/Svelte without createScope or revert()
      if (/\.(jsx|tsx|vue|svelte)$/.test(ext) && /\b(?:animate|createTimeline|onScroll|createDraggable|splitText)\s*\(/.test(text)) {
        if (!/\bcreateScope\s*\(/.test(text) && !/\.revert\s*\(/.test(text)) {
          addFinding('warn', 'missing-motion-cleanup', file, text.search(/\b(?:animate|createTimeline|onScroll|createDraggable|splitText)\s*\(/), text,
            "Component uses Anime.js without createScope() or .revert(). Wrap animations with createScope({ root }) and call scope.revert() on unmount.");
        }
      }

      // 8. Warn on layout-thrashing properties inside animate()
      for (const m of text.matchAll(/\banimate\s*\([^,]+,\s*\{[^}]*\b(top|left|width|height|marginTop|marginLeft)\s*:/gs)) {
        addFinding('warn', 'layout-thrash-property', file, m.index, text,
          `Animating '${m[1]}' triggers per-frame layout reflow. Use GPU transforms (x, y, scaleX, scaleY), clipPath, or Anime.js v4 createLayout() (FLIP).`);
      }
    }
  }

  // 9. Block static CSS hiding essential content (SSR / no-JS blank page trap)
  if (cssExts.has(ext)) {
    const styleChunks = ext === '.css'
      ? [{ content: text, offset: 0 }]
      : [...text.matchAll(/<style[^>]*>([\s\S]*?)<\/style>/gi)].map((m) => ({ content: m[1], offset: m.index + m[0].indexOf(m[1]) }));
    for (const chunk of styleChunks) {
      const cleanedCss = chunk.content.replace(/\/\*[\s\S]*?\*\//g, (s) => ' '.repeat(s.length));
      for (const m of cleanedCss.matchAll(/(?<!\.js-motion-ready\s+)(\[(?:data-animate|data-reveal|data-enter|data-hero|data-card|data-section)[^\]]*\]|\.(?:reveal|animate-on-scroll|hero|section|js-fade|fade-in))\s*\{[^}]*\b(?:opacity\s*:\s*0\b|visibility\s*:\s*hidden\b)/gis)) {
        addFinding('error', 'ssr-hidden-content-trap', file, chunk.offset + m.index, text,
          `Static CSS hides '${m[1]}' with opacity: 0 or visibility: hidden. If JS is slow/disabled or during SSR, the page renders blank. Keep elements visible by default.`);
      }
    }
  }
}

if (usesAnimeJs && !hasReducedMotionGuard) {
  findings.push({
    level: 'warn',
    id: 'missing-reduced-motion-guard',
    file: '(project-wide)',
    line: 1,
    message: "Project imports 'animejs' without a 'prefers-reduced-motion' guard. Use createScope({ mediaQueries: { reduceMotion: '(prefers-reduced-motion: reduce)' } })."
  });
}

const errors = findings.filter((f) => f.level === 'error');
const warnings = findings.filter((f) => f.level === 'warn');
const summary = { root, usesAnimeJs, errors: errors.length, warnings: warnings.length, findings };

console.log(JSON.stringify(summary, null, 2));
console.log(`${errors.length ? 'FAIL' : 'PASS'}: check-motion-v4 (${errors.length} error, ${warnings.length} warning)`);
if (errors.length) process.exitCode = 1;
