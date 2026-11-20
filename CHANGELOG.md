# Changelog

## 7.0.0 — Unified Atlas Universal + Antigravity QA & Security Suite + `npx` CLI (2026-11-19)

### Suite Consolidation & `npx` Ecosystem
- **Unified `atlas-skill` v6.1.0 Universal + `antigravity-qa-security-suite`:** Merged all 11 frontend/motion modules (`atlas-frontend-design` + 10 sub-skills) with the QA & Security suite (`project-bug-hunter`, `project-security-auditor`, `project-fix-and-verify`) into one unified `atlas-skill` repository.
- **Full QA & Security Governance Integration (`suites/project-qa/`):**
  - Added the mandatory gate rule `suites/project-qa/rules/qa-security-gate.md` (`trigger: always_on`), automatically installed to `.agents/rules/qa-security-gate.md` (or `~/.gemini/config/rules/qa-security-gate.md`) when installing with `--with-qa --with-rules`.
  - Added `verify_feature_coverage.py` to `project-fix-and-verify`, read-only vs gated remediation Decision Tree, 3-layer live CVE intelligence (OSV.dev / NIST NVD / CISA KEV + native audit + live web search), plus 100% all-feature testing and Zero-Defect Loop protocols.
- **`npx`-Ready `bin/atlas-skill.mjs` Installer:**
  - Supports `npx --yes github:Crelami-Dev/atlas-skill`, `npx atlas-skill`, and `node bin/atlas-skill.mjs`.
  - Full support for `--agent <codex|antigravity|claude|cursor|windsurf|cline|copilot|agents|all>`, `--dir <PATH>`, `--global`, `--with-rules`, `--expose-subskills`, `--with-qa`, `--dry-run`, `update` (with atomic backups), `doctor` (SHA-256 integrity verification), and `list`.
- **Version `7.0.0` Alignment:** Synchronized `package.json` (`"name": "atlas-skill"`, `"version": "7.0.0"`), `package-manifest.json`, `plugin.json`, `suites/project-qa/package-manifest.json`, `adapters/`, `README.md`, and `docs/INSTALLATION.md`.

## 6.1.0 — Imagery Architecture, Form Controls, 10 Archetypes, & 3-Round Blind Evaluation (2026-11-18)

### Skill Guidance & Deterministic Gate Upgrades
- **Imagery & Placeholder Strategy (`references/imagery.md`):** Added photo asset decision tree, mandatory `Image plan` brief section, non-overlapping SVG and `nowrap` badge rules, and a hard ban on generic hill-and-sun silhouettes.
- **Form Components & Panel Isolation (`templates/design-tokens.css`, `scripts/deal-direction.mjs`):** Added complete styling for `input`, `select` (`appearance: none` + custom chevron + `text-overflow: ellipsis`), `textarea`, buttons (`text-decoration: none`), `checkbox`/`radio`, segmented controls, and heading color isolation inside `.panel` / `.band-dark .panel`.
- **10 Layout Archetypes & 16 Domain Directions (`references/composition-selection.md`, `scripts/deal-direction.mjs`):** Expanded coverage to 10 macro archetypes and 16 directions (including `#9a3b1e` accent differentiation for `terracotta-artisan-store` and hospitality footer variation) plus calibrated tone fallbacks.
- **Hardened Gates & DOM Inspection (`skills/atlas-checker/scripts/slop-scan.mjs`, `skills/atlas-checker/scripts/visual_dom_inspector.py`, `tests/gates.test.mjs`):** Blocked leaked skill jargon (`leaked-skill-jargon`) and UI placeholder meta strings, added full-page contrast checking without a 40-node cap, `svg-text-overlap` (including `<line>`), `mobile-squeezed-grid`, and `desktop-broken-split-grid`.

### Independent Blind Judge Evaluation (10 A/B Cases, Frozen Non-Stub Baseline A)
- **Round 1:** A `3.11` vs B `4.16` (B won `10/10`, 2 CRITICAL defects on B, 3 similar B pairs).
- **Round 2:** A `3.00` vs B `4.26` (B won `10/10`, 1 CRITICAL defect on B, 1 similar B pair).
- **Round 3 (Final):** A `2.99` (`209/70`) vs B `4.04` (`283/70`), B won `10/10`, layout diversity met (`<= 2` similar pairs), though the Round 3 judge flagged 1 open CRITICAL pattern: visible `"GANTI DENGAN FOTO ASLI"` badges in 5/10 visual-domain cases. Full summaries are recorded in `evals/independent-eval-2026-11-18.md` and `evals/independent-eval-2026-11-18.json`.

### Release Package Hygiene
- Bumped version to `6.1.0` across `package.json`, `package-manifest.json`, `plugin.json`, `suites/project-qa/package-manifest.json`, `README.md`, and `docs/INSTALLATION.md`.
- Excluded `.git`, `evals/results/`, and `evals/archive-invalid/` from exported packages and release archives, and removed all self-reported score claims from `README.md`.

## 6.0.0 — Package Consistency, Deterministic Gate Hardening, QA Suite Separation, & Blind Eval Framework (2026-11-18)

### Key Improvements & Milestones (Phases 1 – 7)
- **Phase 1 (Consistency & Testing):** Made `package.json` (`6.0.0`) the single source of truth for `bin/atlas-skill.mjs`, `scripts/validate-package.mjs`, `README.md`, `docs/INSTALLATION.md`, `plugin.json`, `package-manifest.json`, and `tests/installer.test.mjs`. Computed skill counts dynamically from `package-manifest.json`, updated `run-gates.mjs` test fixtures to include real visual proof (`<img>` + 3 surface tokens), and added text-only page tests in Gate 5.
- **Phase 2 (Gate 5 `scripts/check-visual-proof.mjs` Hardening):** Removed false keyword matching (`chart`, `workbench`, `specimen`, `telemetry`) and accepted only real visual DOM elements (`<img>`, `<picture>`, `<canvas>`, `<video>`, non-wireframe data-viz `<svg>`, or `[data-atlas-proof]`) after stripping HTML/JSX comments and `<style>`/`<script>` blocks. Set `missing-visual-proof` and `flat-surface-monotony` to `warn` by default and `error` under `--strict` (while keeping `leaked-markdown-backticks` and `crude-wireframe-svg` as `error`), and added `<!-- atlas-proof: not-applicable -->` opt-out support.
- **Phase 3 (`scripts/deal-direction.mjs` Hardening):** Replaced substring matching with Unicode word-boundary matching and per-direction scoring so short tokens (`ai`, `dev`, `data`) never match inside unrelated words. Removed folder-path hash fallback in favor of a deterministic default (`alabaster-botanical-studio`). Expanded to 8 directions with 8 distinct font pairings and non-warm-neutral categories (including dark mode `obsidian-terminal-noir`, high-contrast `bauhaus-signal-poster`, and cool clinical `clinical-emerald-trust`), all automatically verified for WCAG AA contrast (`>= 4.5:1`).
- **Phase 4 (Bilingual EN & ID Brief Support):** Updated `scripts/check-brief.mjs` to accept both English and Indonesian section headings along with `### Alternative N` / `### Alternatif N`. Added `templates/design-brief.en.md`, included `PASS`/`FIX` alongside `LOLOS`/`PERBAIKI`, and removed nonexistent `deal-direction.js` references.
- **Phase 5 (`SKILL.md` & Sub-Skill Streamlining):** Condensed root `SKILL.md` under 60 lines and moved phase details to `references/phase-workflow.md`. Rewrote all frontmatter descriptions as clear trigger rules (`"Use when... Do not use for..."`) without promotional claims, added one-sentence rationale per hard rule, and introduced the Compact Track (`<!-- atlas-brief: light -->` / `--light`, skipping `research-notes.md` unless requested or unfamiliar domain).
- **Phase 6 (Bug & Security Suite Separation):** Moved `project-bug-hunter`, `project-security-auditor`, and `project-fix-and-verify` into `suites/project-qa/` with an independent `suites/project-qa/package-manifest.json` and added `--with-qa` to `bin/atlas-skill.mjs`. Explicitly documented in `project-security-auditor/SKILL.md` that `live_cve_osv_check.py` queries OSV.dev/NVD/CISA with dependency names/versions and provides `--offline-parse-only`.
- **Phase 7 (Blind Eval Framework & Transparency):** Added `evals/prepare-blind-eval.mjs` to scaffold `evals/results/YYYY-MM-DD/<prompt>/{A,B}` and randomize blind labels per `evals/run-protocol.md` without fabricating scores. Explicitly labeled `evals/review-2026-11-13.md` as a *"self-assessment by the authoring agent, not an independent blind A/B benchmark"* and noted honestly in `README.md` when independent A/B evidence was pending.

### Post-Design-Review Fixes & Package Hygiene (2026-11-18)
- **Package Hygiene & Eval Artifact Exclusions:** Excluded `evals/results` and `__pycache__` from `package-manifest.json`, `package.json` (`files`), `scripts/package-files.mjs`, `scripts/verify-export.mjs`, and `.gitignore`.
- **No Debug State Dropdowns in Production UI:** Added `leaked-debug-state-switcher` (`error`) in `slop-scan.mjs` and updated `atlas-ui-architecture/SKILL.md` so dev state switchers (`Populated / Loading / Empty / Error`) never leak to end users.
- **Macro Layout Diversity (Anti-Uniformity):** Updated `deal-direction.mjs` and `atlas-design/SKILL.md` to forbid forcing a uniform *"2-column hero + Search/Filter/Reset workbench card"* onto all domains; defined distinct macro archetypes (e.g., *Full-Bleed Atmospheric Cover + Two-Column Print Menu* for hospitality, *Full-Width Swiss Poster + Chronological Timetable* for events, *Exhibition Plate Masonry* for photographers, *Single-Column 68ch Editorial Dossier* for nonprofits, *60/40 Multi-Angle Studio Stage* for physical products, *3-Pane DevDocs* for docs, and *Full-Viewport App Shell* for dashboards).
- **Expanded `deal-direction.mjs` Domain Coverage (12 Directions):** Added 4 directions with English & Indonesian keywords for weddings (`velvet-champagne-atelier`), legal/corporate advisory (`savile-navy-counsel`), physical e-commerce (`terracotta-artisan-store`), and education/courses (`campus-amber-academy`), all WCAG AA contrast verified (`>= 4.5:1`).
- **Non-Stub Baseline A & Removal of Self-Scored Claims:** Rebuilt 8 Baseline A pages as full multi-section pages (never stubs) and removed self-scored claims (`2.16 vs 4.93`) from `README.md`.

### Independent Audit, Gate Adversarial Tests, & 8-Prompt End-to-End Evaluation (2026-11-18)
- **Round 1 (Regression, Adversarial Gate, & Consistency Audit):**
  - Fixed `font-proliferation` false positives in `slop-scan.mjs` that counted property declarations rather than distinct font families.
  - Fixed `ENOENT` crashes on broken symlinks and spaced paths in `check-tokens.mjs`, `check-motion-v4.mjs`, `slop-scan.mjs`, and `check-visual-proof.mjs`.
  - Hardened `check-brief.mjs` against duplicate `### Alternative 1` headings, empty files, and Windows CRLF line endings.
  - Hardened `check-tokens.mjs` to ignore CSS/HTML comments, accept mixed shorthands (`margin: 0 auto var(--space-4)`, `border-radius: 50%`), and inspect inline `style="..."` attributes.
  - Hardened `check-motion-v4.mjs` to catch `import * as anime` / `anime.default()` and SSR traps (`[data-hero-title] { opacity: 0 }`, `visibility: hidden`).
  - Hardened `check-visual-proof.mjs` to reject empty `<img src="">` and catch crude wireframe SVGs lacking `viewBox`.
  - Aligned `package-lock.json` (`6.0.0`), added `--with-rules` support for `--agent copilot`, and enriched `deal-direction.mjs` keywords so all 8 test domains map 1-to-1 to 8 unique directions.
- **Round 2 (End-to-End 8-Prompt A/B & Chromium Screenshots):**
  - Discovered via PNG inspection (`view_file`) that Chromium policies block `file://*` navigation (`This page is blocked`); fixed `visual_dom_inspector.py`, `ui_visual_bug_probe.py`, and `e2e_visual_regression.py` by inlining local stylesheets and images via `Page.setDocumentContent` and adding `820x1180` tablet screenshots.
  - Fixed raw hex token violations on `02-photographer/B`, font family counts on `07-donation/B`, `320px` rail heading size on `02-photographer/B`, `375x667` mobile layout order on `05-product/B` and `07-donation/B` so the primary CTA fits above the `667px` fold, and `#retry-semantics` anchor targets on `08-docs/B`.
- **Rounds 3 & 4 (Two Consecutive Clean Verification Rounds):**
  - All 39 unit & adversarial tests passed (`39/39`), `npm run validate` and `npm run test:export` passed, and all 8 B pages passed `run-gates.mjs --mode full --strict` plus multi-viewport browser checks (`1440`, `820`, `375`, 200% zoom, 5-state UI, keyboard focus, 0 console errors) across 2 consecutive clean rounds.

## 5.0.0 - 2026-11-18

- Added dedicated `atlas-motion-animejs` module, `references/animejs-v4-playbook.md`, `templates/animejs-v4-scope.ts`, and `scripts/check-motion-v4.mjs` enforcing authentic Anime.js v4 APIs (`animate`, `createTimeline`, `createScope`, `onScroll`, `spring`, `splitText`, `createLayout`, `svg`, `waapi`) while blocking v3 hallucinations and SSR invisibility traps.
- Added `atlas-ui-architecture` (5-state view contract, responsive app shells, accessible forms/tables/filters) and `atlas-fullstack-contracts` (typed API/mock adapters, auth state boundaries, SEO/OpenGraph readiness) for complete project delivery.
- Upgraded `bin/atlas-skill.mjs` and added `adapters/` for universal compatibility across OpenAI Codex, Google Antigravity IDE, Claude Code, Cursor, Windsurf, Cline, GitHub Copilot, and any `AGENTS.md`-aware agent (including `--global`, `--with-rules`, and `--expose-subskills`).
- Upgraded `check-tokens.mjs`, `slop-scan.mjs`, `run-gates.mjs`, and all 7 existing sub-skills with concrete Bad-vs-Good code contrasts and deterministic guardrails.
- Fixed UTF-8 corruption in `SKILL.md` and replaced Node 22-only `import.meta.dirname` calls with `fileURLToPath` across all scripts and tests for full Node 18-24+ compatibility.

## 4.0.0 - 2026-11-13

- Replaced legacy Python preset runtime with a dependency-free Node.js installer, modular instruction set, phase gates, and Playwright verification tools.
