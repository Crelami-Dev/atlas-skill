# Atlas-Skill: Source Repository Audit

**Report Date:** October 30, 2026  
**Status:** Complete (Read-Only Audit)  
**Target Project:** `atlas-skill/`  

---

## 1. Project A: `taste-skill` (v2.1.5)

### 1.1 Overview & Architecture
`taste-skill` is an agent skill developed by Leonxlnx, designed to eliminate "AI slop" and templated aesthetics in web design. It is derived from a quantitative and qualitative study of 247 award-winning websites (Awwwards Site of the Day, One Page Love).

```text
taste-skill/
├── .agents/plugins/marketplace.json        # Manifest: Universal Agent marketplace
├── .claude-plugin/marketplace.json         # Manifest: Claude Code plugin
├── .codex-plugin/plugin.json               # Manifest: OpenAI Codex plugin
├── .github/workflows/check-skills.yml      # CI workflow (Node 22)
├── assets/                                 # Branding & sponsor SVGs/WebP
├── examples/v2/                            # Generated page screenshots & CREDITS.md
├── skills/taste-skill/
│   ├── SKILL.md                            # Main skill instructions (542 lines)
│   ├── README.md                           # Tool reference
│   ├── assets/                             # app.css, base.css, charts.js, scenes/
│   ├── evals/evals.json                    # Benchmark evals cases
│   ├── library/                            # 9 Curated JSON design datasets
│   │   ├── app.json                        # App shells, kinds, and UI styles
│   │   ├── directions.json                 # 20 Art directions
│   │   ├── heroes.json                     # 58 Hero blueprints
│   │   ├── motions.json                    # 18 Motion patterns
│   │   ├── palettes.json                   # 56 Semantic palettes
│   │   ├── photos.json                     # Curated photo query sets
│   │   ├── sections.json                   # 185 Section blueprints
│   │   ├── sites.json                      # 202 Studied site teardowns & scores
│   │   └── type.json                       # 44 Typography pairings & scales
│   ├── references/                         # 11 In-depth design guides
│   │   ├── app-screens.md                  # Working UIs, tables, dashboards (86 KB)
│   │   ├── colour.md, copy.md, critique.md, imagery.md, layout.md, motion.md,
│   │   └── research.md, scenes.md, tells.md, type.md
│   └── scripts/                            # Zero-dependency Node.js CLI suite
│       ├── draw.mjs                        # Direction & blueprint dealer
│       ├── inspect.mjs                     # CDP browser inspector & filmstrip
│       ├── assets.mjs                      # Open-archive imagery search/downloader
│       ├── lint.mjs                        # Static HTML house style linter
│       ├── scenes.mjs                      # Scroll scenes scaffolder
│       └── lib/                            # cdp.mjs, probe.mjs, rules.mjs, etc.
└── tests/                                  # Node.js tests (frontmatter, text-encoding, etc.)
```

### 1.2 Verified Capabilities
* **Curated Design Libraries (`VERIFIED`):** 9 JSON files under `skills/taste-skill/library/` contain rich, production-grade design data. Direct schema inspection verified 20 art directions, 58 hero blueprints, 185 section blueprints, 56 palettes, 44 typography scales, and 202 site teardowns with explicit "design steals".
* **Zero-Dependency CDP Browser Inspector (`VERIFIED`):** `scripts/inspect.mjs` (308 lines) and `scripts/lib/cdp.mjs` (190 lines) drive Chromium or Microsoft Edge directly over native WebSockets using the Chrome DevTools Protocol. It computes computed typography, element geometry, contrast ratios, and captures screenshots at 1440px, 768px, and 390px without installing any `npm` package.
* **Anti-Slop House Rules Engine (`VERIFIED`):** `scripts/lib/rules.mjs` (243 lines) enforces strict prohibitions against AI design clichés:
  * Prohibits centered 3-line headlines with eyebrow kicker pills (`id: eyebrow`).
  * Flags generic gradients (`id: gradient`) and decorative box shadows at rest (`id: shadow`).
  * Bans decorative index numbers (`id: numbering`), unearned monospace fonts in prose (`id: mono`), and emoji icons (`id: emoji`).
  * Prohibits "AI purple" (`hsl(244-295, >42%, 30-80%)`) and dull cream surfaces (`hsl(22-62, >16%, 88-99.5%)`).
* **Dual Run: Page vs App Screen (`VERIFIED`):** Explicitly routes between scrollable marketing pages and dense functional web applications. Dashboards use `assets/app.css` and `assets/charts.js` (59 KB zero-dependency SVG/Canvas charts).
* **Open Archive Asset Searcher (`PARTIAL`):** `scripts/assets.mjs` implements keyless searches against Openverse, Wikimedia Commons, the Art Institute of Chicago (AIC), the Metropolitan Museum of Art (Met), the Internet Archive, and NASA. While code is complete, network calls depend on external API uptime and firewall configuration.
* **Platform Packaging Manifests (`VERIFIED`):** Fully configured manifests for Claude Code (`.claude-plugin/marketplace.json`), OpenAI Codex (`.codex-plugin/plugin.json`), and general agent engines (`.agents/plugins/marketplace.json`).

### 1.3 License & Attribution
* Code is licensed under **MIT License (Copyright 2026 Leonxlnx)** (`LICENSE`).
* Third-party assets in `examples/v2/CREDITS.md` are documented under CC0, Public Domain, CC BY 2.0, and CC BY-SA 4.0 with required attribution lines for museum and Wikimedia sources.

---

## 2. Project B: `atlas-frontend-design` (v1.0.0)

### 2.1 Overview & Architecture
`atlas-frontend-design` is a Python-based frontend design workflow built to replace unthinking defaults with deliberate, context-driven decisions. It emphasizes reproducible pattern selection and honest quality verification.

```text
atlas-frontend-design/
├── .github/workflows/ci.yml                # CI: python -m unittest
├── benchmark/                              # 12 Briefs and scientific evaluation protocol
│   ├── briefs.json
│   └── PROTOCOL.md
├── compositions/                           # 50 Layout patterns with strict JSON schema
│   ├── library.json
│   └── schema.json
├── examples/binong-permai/                 # End-to-end reference implementation
│   ├── index.html                          # Single-file production HTML
│   ├── DECISIONS.md                        # Verified facts vs assumptions log
│   ├── check-report.json                   # Output of atlas_check.py
│   └── shots/                              # Screenshots at 390, 768, 1440
├── references/                             # 5 Modular engineering references
│   ├── assets.md                           # Asset honesty and licensing rules
│   ├── design-playbook.md                  # Comprehensive ATLAS v1 playbook (17 KB)
│   ├── large-html.md                       # Safeguards for files >500 KB
│   ├── rubric.md                           # Juror scoring rubric
│   └── vanilla-patterns.md                 # Native accessible components (drawer, accordion)
├── scripts/                                # Standard library Python CLI tools
│   ├── atlas_select.py                     # Deterministic & seeded context selector
│   ├── atlas_check.py                      # Static DOM & Playwright quality gate
│   ├── atlas_shoot.py                      # Automated Playwright screenshot utility
│   ├── atlas_compare.py                    # Visual diff pixel comparison (Pillow)
│   └── atlas_bench.py                      # Blinded scoring and agreement metrics
├── tests/                                  # 37 Python unittests (select, check, library, bench)
│   ├── fixtures/                           # bad.html, good.html, overflow.html
│   └── test_*.py
├── CHANGELOG.md, LIMITATIONS.md, README.md, SKILL.md
```

### 2.2 Verified Capabilities
* **Context-Driven Pattern Selector (`VERIFIED`):** `scripts/atlas_select.py` (213 lines) scores patterns using an objective weighting formula:
  $$\text{Score} = \text{Category Match (+3)} + \text{Tone Overlap (+1 per tone)} + \text{Density Fit} + \text{Goal Overlap (+0.75)} - \text{Sequence Repetition Penalty}$$
  Supports hard asset filtering (excludes photo/UI patterns when assets are missing) and reproducible `--seed` exploration. Verified via CLI test with `--seed 1`.
* **Structured Pattern Library (`VERIFIED`):** `compositions/library.json` contains 50 layout patterns across navigation, hero, metrics, features, showcase, story, social proof, pricing, process, faq, cta, and footer. Conforms strictly to Draft 2020-12 JSON Schema (`compositions/schema.json`).
* **Truthful Quality Gate (`VERIFIED`):** `scripts/atlas_check.py` (504 lines) implements static DOM parsing via standard library `html.parser.HTMLParser`. It separates `fail` (hard errors), `warn` (heuristics), and `info` (placeholders), explicitly listing only checks that actually executed. Verified on `binong-permai/index.html` (0 fail, 9 placeholders reported).
* **Visual Benchmarking Suite (`VERIFIED`):** `scripts/atlas_bench.py` and `benchmark/PROTOCOL.md` provide double-blinded review sheets and inter-rater reliability scoring across 12 standardized design briefs (8 public, 4 held-out).
* **Vanilla Component Library (`VERIFIED`):** `references/vanilla-patterns.md` provides native, accessible implementations for drawers with focus traps, accessible accordions, tabs with keyboard navigation, and responsive carousels without npm dependencies.

### 2.3 Limitations & Gaps
* Lacks integration manifests for Claude Code, Codex, and Antigravity plugins.
* Library is limited to 50 structural patterns, lacking pre-packaged color palettes, typography pairing databases, and live charting utilities.
* Browser screenshot capture (`atlas_shoot.py`) and pixel diffing (`atlas_compare.py`) depend on third-party Python packages (`playwright`, `pillow`) not present in standard installations.

---

## 3. Project C: `project-atlas-v0.2.0-alpha`

### 3.1 Overview & Architecture
`project-atlas-v0.2.0-alpha` represents an initial architectural merger scaffold integrating ATLAS with the `crafted-web-design` skill.

```text
project-atlas-v0.2.0-alpha/project-atlas/
├── AGENTS.md                               # Multi-agent role contracts (5 roles)
├── CHANGELOG.md, LICENSE, README.md
├── benchmarks/briefs.json                  # 12 Design briefs (identical to atlas-frontend-design)
├── scripts/validate_library.py             # Schema validator for early library
├── skills/atlas-design/
│   ├── SKILL.md                            # Workflow contract (166 lines)
│   └── references/                         # 8 Reference files
│       ├── composition-library.json        # Stripped-down 20-pattern library (Scaffold)
│       ├── landing-pages.md                # Specialized landing page workflow
│       ├── web-apps.md                     # Specialized web application workflow
│       ├── visual-direction-and-tokens.md  # Token system and visual thesis
│       ├── responsive-and-accessibility.md # Responsive principles & WCAG
│       ├── vanilla-patterns.md             # Vanilla components (duplicate)
│       ├── large-html-files.md             # Large HTML rules (duplicate)
│       └── evaluation-rubric.md            # Juror rubric (duplicate)
└── tests/test_validate_library.py          # Unittest for validate_library.py
```

### 3.2 Usable Assets vs Scaffold Status
* **Usable Core Assets (`VERIFIED`):**
  * `AGENTS.md` defines precise multi-agent contracts for 5 roles: Lead Orchestrator, Product Analyst, Art Director, Frontend Implementer, and QA Critic.
  * `references/landing-pages.md` and `references/web-apps.md` provide clear, high-quality guidelines separating marketing narratives from dense data applications.
* **Scaffold / Incomplete Components (`DROP` or `REWRITE`):**
  * `references/composition-library.json` is an obsolete 20-pattern file using a deprecated schema (`schema_version`, `best_for`, `mobile_rule`, `failure_modes`). It is completely superseded by `atlas-frontend-design/compositions/library.json` (50 patterns).
  * Lacks automated browser execution tools, inspection scripts, or plugin manifests.

---

## 4. Project D: `.taste-skill` (Runtime Artifact)

Inspection of `d:\tes\skills-staging\.taste-skill` revealed:
* `inspect/report.json` (47 KB): A real inspection report generated by `taste-skill/scripts/inspect.mjs` against `D:/tes/smk-binong/index.html`.
* `inspect/desktop-fold.jpg`, `mobile-fold.jpg`, `tablet-fold.jpg`: High-resolution viewport captures.
* **Critical Finding:** The report flagged 9 visual and typographic warnings on the Binong Permai site that the static DOM parser missed:
  1. `small-title`: `h1` set at 31px (gallery median is 48px+).
  2. `size-count`: 11 distinct font sizes detected (recommended: <= 6).
  3. `card-rows`: 4 rows of repetitive boxed cards.
  4. `palette-cream`: Background color falls into the generic AI yellow-cream family (`#fbf9f4`).
  5. `ragged-edges`: Text blocks align to 12 different left margins.
  This provides concrete empirical proof that combining static DOM checking with CDP browser rendering is necessary to catch subtle aesthetic defects.

---

## 5. Capabilities Verification Matrix

| Capability | Taste-Skill | Atlas-Frontend-Design | Project-Atlas | Status in Source | Target in Atlas-Skill |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Aesthetic Curated Libraries** | 9 JSONs (247 sites, 185 sections, 58 heroes, 56 palettes, 44 fonts) | 50 patterns (layouts only) | 20 patterns (early scaffold) | `VERIFIED` (Taste) | **MERGE** (Unified Database) |
| **Context Selection Engine** | Random / recent-aware draw (`draw.mjs`) | Deterministic context scoring (`atlas_select.py`) | Manual reference routing | `VERIFIED` (Atlas) | **REUSE & EXTEND** |
| **Static Quality Gate** | Basic linter (`lint.mjs`) | Standard library DOM parser (`atlas_check.py`) | None | `VERIFIED` (Atlas) | **REUSE (Core Gate)** |
| **Browser Inspection (CDP)** | Zero-dep WebSocket client (`cdp.mjs`, `inspect.mjs`) | None (relies on Playwright) | None | `VERIFIED` (Taste) | **REUSE (Core Browser)** |
| **Visual Diff Comparison** | None | Pixel diff via Pillow (`atlas_compare.py`) | None | `PARTIAL` (Needs Pillow) | **REUSE** |
| **Open Archive Imagery** | Keyless search on 5 archives (`assets.mjs`) | None (policy guide only) | None | `PARTIAL` (Network sensitive) | **REUSE (With Fallback)** |
| **AI Image Generation** | None | None | None | `MISSING` | **NEW DESIGN (Adapter)** |
| **Multi-Agent Contracts** | Single sequential agent flow | Single sequential agent flow | Formal 5-role contract (`AGENTS.md`) | `VERIFIED` (Atlas v0.2) | **REUSE (Core Architecture)** |
| **Modular Guides (App vs Page)** | In-depth guides (`references/*.md`) | General playbook (`design-playbook.md`) | Modular guides (`landing-pages.md`, `web-apps.md`) | `VERIFIED` (Both) | **MERGE & DEDUPLICATE** |
| **Multi-Platform Manifests** | Claude, Codex, Antigravity | None | None | `VERIFIED` (Taste) | **REUSE & UPDATE** |
| **Web Chatbot Entry Point** | None (requires Node CLI) | None (requires Python CLI) | None | `MISSING` | **NEW DESIGN (`SKILL.chatbot.md`)** |

