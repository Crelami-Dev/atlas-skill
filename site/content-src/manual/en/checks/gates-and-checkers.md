---
title: Deterministic Gates & Checkers
description: How to run run-gates.mjs, quick-check.mjs, check-copy.mjs, check-tokens.mjs, and check-brief.mjs.
---

Atlas pairs skill guidance with executable verification scripts written in Node.js (plus optional Python + Chromium headless auditing) so defects are caught before visual handoff.

## Unified Gate Pipeline

Run all static checks (`1–5` plus `4b`) in one command:

```sh
# Execute Gates 1, 2, 3, 4, 4b, and 5 sequentially
node scripts/run-gates.mjs /path/to/target-project --mode full --strict

# Add Gate 6 (headless browser screenshots & DOM geometry via Python + Playwright)
node scripts/run-gates.mjs /path/to/target-project --mode full --strict --visual /path/to/target-project/index.html --shots-dir ./maintenance/screenshots
```

Passing `--mode light` skips `1. Brief Gate` (`check-brief.mjs`) for light/prose-exempt workflows, while `--strict` turns warnings from `check-copy` and `check-visual-proof` into hard errors (`exit 1`).

## Individual Validators

### 1. Brief Gate (`scripts/check-brief.mjs`)
Validates `design-brief.md` before implementation begins:
- Enforces the single-page limit (`<= 7000` characters) and blocks placeholder copy (`lorem ipsum`, `your company`, `acme corp`).
- Requires core sections in either English or Indonesian: visitor task, real content, final choice and rationale, verification plan, and (in full mode) **3 composition alternatives** (`### Alternative 1..3` / `### Alternatif 1..3`) plus deliberate rejections.
- Supports compact mode via `--light` or `<!-- atlas-brief: light -->`.
- Validates any `scene:` declared under `## Signature idea` against `templates/scene-catalog.json`.

```sh
node scripts/check-brief.mjs /path/to/target-project/design-brief.md
```

### 2. Tokens Gate (`scripts/check-tokens.mjs`)
Guards against hardcoded styling drift outside the token file:
- Reads the token stylesheet passed via `--tokens <path>` (or auto-detects `design-tokens.css`, `src/styles/tokens.css`, `app/globals.css`, etc.).
- Scans `.css`, `.html`, `.jsx`, `.tsx`, `.vue`, `.svelte`, and `.astro` files to ensure raw hex colors, arbitrary pixel/rem values, and un-tokenized inline `style="..."` properties do not bypass CSS variables (explicit exceptions go in `.atlas-token-allowlist.json`).

```sh
node scripts/check-tokens.mjs /path/to/target-project --tokens /path/to/target-project/design-tokens.css
```

### 3. Motion v4 Gate (`scripts/check-motion-v4.mjs`)
Enforces valid Anime.js v4 APIs and progressive enhancement safety:
- Blocks legacy Anime.js v3 syntax (`anime({ targets: ... })`, `easing:`, `import * as anime`).
- Prevents SSR/no-JS invisibility traps such as static `opacity: 0` or `visibility: hidden` on `[data-reveal]` / `[data-hero-title]`.

```sh
node scripts/check-motion-v4.mjs /path/to/target-project
```

### 4. Anti-Slop Scanner (`skills/atlas-checker/scripts/slop-scan.mjs`)
Detects code signals from the 18 AI slop patterns (purple-to-blue neon gradients, emoji icons in UI chrome, font family proliferation `> 2` proportional families, marketing buzzwords, leaked debug state switchers, and leaked photo replacement instructions). See the full table in [Anti-Slop Patterns](/atlas-skill/en/anti-slop/patterns/).

```sh
node skills/atlas-checker/scripts/slop-scan.mjs /path/to/target-project
```

### 4b. Concise Copy Gate (`scripts/check-copy.mjs`)
Checks static HTML copy against the word budgets in [Concise Copy](/atlas-skill/en/guides/concise-copy/):
- First screen budgets: H1 `<= 10` words (`16` fail), lede `<= 28` words (`45` fail), whole first screen `< 55` words (`85` fail), plus at least one concrete fact.
- Section budgets: paragraphs `<= 45` words (`80` fail), landing page `~700` words, CTA labels `<= 5` words avoiding vague verbs (`Learn more`, `Read more`, `Click here`, `Selengkapnya`, `Submit`).
- Documentation and long-form articles can opt out of length limits with `<!-- atlas-copy: long-form -->` (vague CTA labels remain checked).

```sh
node scripts/check-copy.mjs /path/to/target-project --strict
```

### 5. Visual Proof Gate (`scripts/check-visual-proof.mjs`)
Verifies visual proof (`<img>`, `<picture>`, `<canvas>`, `<video>`, `<svg data-viz>`, or `[data-atlas-proof]`), `>= 3` surface color tokens, zero crude wireframe/floorplan SVGs, and zero leaked photo placeholder copy (`<!-- atlas-proof: not-applicable -->` opts out prose-only documents).

### 6. Browser Audit: Gate 6 & `quick-check.mjs`
- **Gate 6 (`skills/atlas-checker/scripts/visual_dom_inspector.py`):** Runs under `run-gates.mjs --visual`, capturing `1440x900`, `820x1180`, and `375x667` PNGs while checking composited text contrast, overlaps, and `mobile-squeezed-grid`.
- **`quick-check.mjs`:** Standalone Node.js + Playwright auditor covering **11 viewports** (`320x568` to `1440x900`), menu/tab interaction checks (`--click-test`), pause controls on loops, long mobile card stacks, and tablet portrait alignment (`600 px` & `768 px`). See every finding code in the [Findings Dictionary](/atlas-skill/en/checks/findings-dictionary/).

```sh
node skills/atlas-checker/scripts/quick-check.mjs /path/to/project/index.html --shots ./maintenance/browser --click-test
```
