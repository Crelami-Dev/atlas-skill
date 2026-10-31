# Atlas Skill P7 — Art Direction & Visual Identity Intelligence
## Comprehensive Audit Report & Implementation Proposal

> **Document Status:** Official Audit Report & Proposal  
> **Target Release:** P7 (Art Direction & Visual Identity Intelligence)  
> **Baseline Commit:** `37db70a1bc694db34329ed4ea8c7b0a4bffa372e` (Branch: `main`)  
> **Verification Status:** Evidence-backed audit across Python 3.10.10, Node.js v24.16.0, and Chrome CDP  

---

## Executive Summary

Phase 7 (P7) addresses the transition of Atlas Skill from a **syntactically compliant layout generator** to an **art-directed design intelligence engine**.

While Phase 6 (P6) successfully delivered responsive, collision-free asymmetric Bento Grid layouts with complete zero-dependency standard-library compliance, an in-depth audit of the core engine reveals a critical bottleneck: **The system collapses 20 curated macro art directions, 56 palettes, and 44 typography systems into just 2 repetitive output archetypes across diverse industry briefs**. Furthermore, generated headlines, descriptions, section headings, and CSS spatial tokens remain largely hardcoded and decoupled from the input brief.

This document establishes the verified evidence, gap analysis, benchmark briefs, acceptance criteria, test plan, and staged implementation proposal for P7.

---

## A. Baseline Repository State

The repository was verified prior to drafting this audit report. All measurements are based on execution logs and direct repository inspection:

| Dimension | Verified State | Evidence Source |
|---|---|---|
| **Repository Root** | `D:\tes\skills-staging\atlas-skill` | Working directory check |
| **Active Branch** | `main` | `git branch --show-current` |
| **HEAD Commit** | `37db70a1bc694db34329ed4ea8c7b0a4bffa372e` | `git rev-parse HEAD` |
| **Commit Subject** | `feat(atlas): complete Atlas Skill v2.0.0 release with anti-slop rules and progressive loading` | `git log -1 --oneline` |
| **Working Tree** | Clean (0 modified tracked files, 0 untracked files prior to this report) | `git status --short` |
| **Python Runtime** | `Python 3.10.10` | `py -3 --version` |
| **Node.js Runtime** | `v24.16.0` | `node --version` |
| **Browser Binary** | Google Chrome `156.0.8078.79` | `runtime/browser_qa.py` auto-discovery |
| **Python Unit Tests** | **170 / 170 PASS** (0 failures, 0 errors, 28.5s) | `py -3 -m unittest discover -s tests -p "test_*.py"` |
| **CDP Fixture Suite** | **5 / 5 PASS** (100% accuracy, zero false positives) | `node tests/test_cdp_fixtures.mjs` |
| **Anime.js v4 Suite** | **4 / 4 PASS** (Motion contracts & reduced-motion guards) | `node tests/test_animejs_v4_integration.mjs` |
| **Canonical Library** | 20 Art Directions, 56 Palettes, 44 Typography, 293 Compositions | `data/*.json` |
| **Protected Boundaries** | `taste-skill/` and `projek-webiste/saas-dashboard/` untouched | External boundary check |

---

## B. Existing Art Direction Capabilities

### B.1 Pipeline Execution Architecture

Atlas Skill currently operates an explainable 5-stage synthesis pipeline:

```
┌─────────────────────────────────────────────────────────────┐
│ 1. Input Brief Normalization (runtime/contracts.py)         │
│    ProductBrief: project_name, category, tones, density,    │
│    audience, primary_task, slots, exclude, scoring_weights  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. Composition Engine (runtime/composer.py)                 │
│    ├─ score_art_direction()  ──► Top Macro Art Direction    │
│    ├─ score_composition()    ──► Slot-by-Slot Blueprints    │
│    ├─ score_palette()        ──► Semantic Color Tokens      │
│    ├─ score_typography()     ──► Typeface Pairings & Scale  │
│    └─ plan_motion_for_brief()──► Motion Signature & Curves  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. Asset Boundary Pipeline (runtime/assets.py)              │
│    DEC-003 Resolution: Tier 1 (Native) → Tier 2 (Archive)   │
│    → Tier 3 (Semantic Vector SVG / Structural Fallbacks)    │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 4. Code Generation Engine (runtime/generator.py)            │
│    ├─ render_html()          ──► Semantic HTML5 Document    │
│    ├─ render_css()           ──► CSS Tokens & Responsive CSS│
│    └─ render_js()            ──► Accessible Vanilla Script  │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ 5. Verification & Quality Gates (runtime/browser_qa.py)     │
│    ├─ DOM Quality Gate       ──► tools/atlas_check.py       │
│    ├─ Anti-Slop Audit        ──► runtime/anti_slop.py       │
│    └─ CDP Layout Inspection  ──► runtime/browser_cdp.mjs    │
└─────────────────────────────────────────────────────────────┘
```

### B.2 Proven Functional Strengths

1. **Downstream Cohesion (Palette + Typography follow Art Direction):**
   Once an Art Direction is selected, `score_palette()` and `score_typography()` in `runtime/scorer.py` reward tokens that match the Art Direction's `palette_tags` (+3.0) and `type_classes` (+4.0). For example:
   - Selecting `"The name as a monument"` reliably pairs with `Bodoni Moda / Jost` (serif-display) and `Black and crimson` (two-tone).
   - Selecting `"Dressed as something else"` pairs with `Anton / Work Sans` (extended-heavy) and `Navy and pink` (mono-accent).
2. **Deterministic Reproducibility:**
   `compute_plan_id()` hashes the normalized brief and library version, guaranteeing that identical brief inputs always produce identical plan structures without random drift.
3. **Decoupled 3-Tier Fallback Policy (DEC-003):**
   When external AI generation credentials are missing, `runtime/assets.py` generates clean, category-appropriate architectural SVG graphics without hallucinated financial sparklines or fake analytical telemetry.
4. **Resilient Browser Quality Assurance:**
   The native Node.js 22+ WebSocket CDP runner (`runtime/browser_cdp.mjs`) accurately evaluates 5 standardized viewports for horizontal page overflow (`scrollWidth <= clientWidth`) and uncontained element collisions.

---

## C. Evidence-Based Gap Analysis

A rigorous probe across multiple distinct briefs revealed 6 confirmed gaps, 1 hypothesis requiring further verification, and 1 non-issue (anti-slop rule suitability).

### Summary Priority Table

| Gap ID | Severity | Category | Status | Primary File & Line Reference |
|---|---|---|---|---|
| **GAP-1** | **HIGH** | Scoring / Selection | **Verified Fact** | `runtime/scorer.py:16-67`, `runtime/composer.py:79` |
| **GAP-2** | **HIGH** | Content Synthesis | **Verified Fact** | `runtime/generator.py:877-925, 954-970` |
| **GAP-3** | **HIGH** | Design Tokens / CSS | **Verified Fact** | `runtime/generator.py:100-114, 163-176` |
| **GAP-4** | **MEDIUM** | Color Tokens | **Verified Fact** | `runtime/generator.py:93`, `data/palettes.json` |
| **GAP-5** | **MEDIUM** | Layout Composition | **Verified Fact** | `runtime/generator.py:835-870, 908-1100` |
| **GAP-6** | **MEDIUM** | Input Normalization | **Verified Fact** | `runtime/contracts.py:107-108`, `runtime/scorer.py:16-67` |
| **GAP-7** | **LOW** | Motion Integration | **Hypothesis** | `runtime/generator.py:1221-1227`, `runtime/motion_adapter.py` |
| **GAP-8** | **NONE** | Anti-Slop Rules | **Non-Issue (Confirmed Working)** | `runtime/anti_slop.py:341-430` |

---

### Detailed Gap Findings

#### GAP-1: Art Direction Selection Collapse (20 in Library, Only 2 in Production)
- **Classification:** **Verified Fact**
- **Location:** `runtime/scorer.py#L16-L67` (`score_art_direction`) and `runtime/composer.py#L78-L83`
- **Observed Behavior:**
  When testing 7 widely disparate briefs (SaaS, Studio Portfolio, Fintech, Hospitality, AI Product, Physical Product, Music Label), only **2 unique Art Directions** were ever selected:
  - `"Dressed as something else"` (`art-dir:borrowed-category`) won for SaaS, Fintech, AI Product, and Physical Product.
  - `"The name as a monument"` (`art-dir:name-as-monument`) won for Studio Portfolio, Hospitality, and Music.
- **Root Cause:**
  1. The canonical library in `data/art-directions.json` only uses 7 specific tone keywords: `['bold', 'editorial', 'luxury', 'playful', 'quiet', 'technical', 'warm']`. When briefs use common synonyms (e.g. `'precise'`, `'calm'`, `'minimal'`, `'clinical'`), `dir_tones & brief_tones` yields an empty set, resulting in 0 tone points.
  2. For `category: "saas"`, 5 candidate Art Directions tied at exactly `+3.0` points (`sentence-as-layout`, `colour-chapters`, `one-motif`, `borrowed-category`, `the-printed-annual`).
  3. `runtime/composer.py#L79` performs tie-breaking via `ranked_ad.sort(key=lambda x: (-x[0], x[1]["id"]))`. Alphabetically, `art-dir:borrowed-category` starts with `b` and precedes all other tied competitors (`c`, `o`, `s`, `t`). Thus, `borrowed-category` always wins every SaaS tie.
- **Impact:** 18 out of 20 Art Directions are completely starved from selection under standard brief inputs.
- **Priority:** **P0 / High**

#### GAP-2: Static Hardcoded Boilerplate Copy
- **Classification:** **Verified Fact**
- **Location:** `runtime/generator.py#L877-L879, L912-L916, L954-956, L1089-1092`
- **Observed Behavior:**
  Regardless of brief category or selected Art Direction:
  - `H1` is universally hardcoded as `"Engineered for Clarity, Speed, and Depth."`
  - `H2` headers are universally hardcoded as `"Architected Without Compromise"`, `"From Brief to Verified Deployment"`, `"Transparent, Predictable Investment"`, and `"Frequently Asked Questions"`.
  - Feature cards contain Atlas-internal self-promotional terms: `"Deterministic Execution"`, `"Deep Immutability"`, `"3-Tier Visual Asset Pipeline"`, and `"Atlas-Skill"`.
- **Root Cause:**
  `render_html()` in `runtime/generator.py` only interpolates `{project_name}` and `{category}` into raw string literals. The rich editorial guidelines in `art_direction["idea"]`, `art_direction["composition"]`, and `art_direction["imagery"]` are completely ignored during rendering.
- **Impact:** A luxury jewelry atelier and a developer infrastructure tool receive identical headlines and feature copy, destroying visual identity.
- **Priority:** **P0 / High**

#### GAP-3: Static Spatial Scale and Typography Override
- **Classification:** **Verified Fact**
- **Location:** `runtime/generator.py#L100-L114` and `runtime/generator.py#L163-L176`
- **Observed Behavior:**
  - Container spacing is static: `--space-xl: 4rem; --max-width: 1200px;` regardless of whether the brief specifies `density: "low"` (editorial/luxury) or `density: "high"` (dense operational application).
  - Headline sizing is static: `h1 { font-size: clamp(2.25rem, 4vw + 1rem, 4rem); }` is hardcoded in CSS.
- **Root Cause:**
  While `data/typography.json` specifies bespoke fluid clamp multipliers for every type system (e.g. `scale.step-head: "clamp(2rem, 1.3rem + 3.2vw, 4rem)"`), `render_css()` in `runtime/generator.py` never inspects `plan["typography"]["scale"]`.
- **Impact:** Editorial and monument art directions requiring dramatic typographic scale (`font-size: 16–24vw` per `name-as-monument`) cannot be rendered.
- **Priority:** **P1 / High**

#### GAP-4: Hardcoded Border Contrast Token
- **Classification:** **Verified Fact**
- **Location:** `runtime/generator.py#L93`
- **Observed Behavior:**
  `--color-border: rgba(128, 128, 128, 0.18);` is fixed for all palettes.
- **Root Cause:**
  `data/palettes.json` lacks an explicit border token. For deep dark backgrounds (`#0a0a0a`), `rgba(128, 128, 128, 0.18)` offers insufficient contrast against dark cards (`#151515`). For crisp white backgrounds, it lacks definition.
- **Priority:** **P2 / Medium**

#### GAP-5: Layout Sections Decoupled from Composition Slots
- **Classification:** **Verified Fact**
- **Location:** `runtime/generator.py#L835-L870, L908-L1100`
- **Observed Behavior:**
  `render_html()` renders an invariant sequence: `hero → proof → features → workflow → pricing → faq → cta → footer`.
  If a brief excludes `pricing` (e.g. luxury studio or portfolio), or if `plan["composition"]["slots"]` specifies a different slot order, `render_html()` ignores the plan and renders the full hardcoded suite regardless.
- **Root Cause:**
  `render_html()` only inspects `comp["slots"]` to toggle between Bento Grid and conventional features (`is_bento_features = ...`). All other sections are unconditionally concatenated.
- **Impact:** Commercial pricing tables appear on luxury gallery and fine art portfolio sites where pricing tables are contextually inappropriate.
- **Priority:** **P1 / Medium**

#### GAP-6: Unused `audience` and `primary_task` Fields
- **Classification:** **Verified Fact**
- **Location:** `runtime/contracts.py#L107-L108` and `runtime/scorer.py#L16-L67`
- **Observed Behavior:**
  `ProductBrief` parses `audience` and `primary_task`, but neither `score_art_direction()`, `score_composition()`, `score_palette()`, nor `score_typography()` reads these fields.
- **Root Cause:**
  Scoring functions were authored before audience profiling was integrated.
- **Impact:** A brief specifying `audience: "enterprise CFOs"` scores identically to `audience: "indie developers"`.
- **Priority:** **P2 / Medium**

#### GAP-7: Motion Script Pipeline Verification
- **Classification:** **Hypothesis**
- **Location:** `runtime/generator.py#L1221-L1227`
- **Analysis:**
  `plan["motion_plan"]` is generated by `plan_motion_for_brief()`, and `render_js()` attempts to invoke `generate_motion_runtime_script(plan["motion_plan"])`. However, during initial probing, the motion property output was inconclusive. Needs formal verification in test harness.
- **Priority:** **P3 / Low**

#### GAP-8: Anti-Slop Boundary Compatibility
- **Classification:** **Non-Issue (Confirmed Working)**
- **Location:** `runtime/anti_slop.py#L341-L430`
- **Finding:**
  Auditing confirmed that `runtime/anti_slop.py` correctly distinguishes intentional hierarchy from sloppy code. The rules (`multi-accent-container` and `inconsistent-radius`) allow intentional kicker color accents and lead tile borders when styled with consistent tokens. **No modifications to `runtime/anti_slop.py` are required or permitted.**

---

## D. Benchmark Briefs & Evaluation Methodology

To evaluate P7 objectively without generating premature website code, three distinct benchmark briefs representing three contrasting visual and functional archetypes are defined:

### D.1 The Three Benchmark Briefs

#### 1. Luxury Editorial Studio (`brief_luxury`)
```json
{
  "project_name": "Maison Atelier",
  "category": "studio-portfolio",
  "tones": ["luxury", "editorial", "quiet"],
  "density": "low",
  "page_type": "marketing",
  "audience": "high-net-worth collectors and cultural institutions",
  "primary_task": "portfolio showcase with inquiries"
}
```
- **Expected Aesthetic Archetype:** Display serif typography (e.g. `Bodoni Moda`, `EB Garamond`), two-tone palette (bone/near-black or dark chocolate), generous whitespace (`--space-xl >= 6rem`), tight headline letter-spacing, **zero commercial pricing tables**, museum-grade imagery framing.

#### 2. Enterprise SaaS Infrastructure (`brief_saas`)
```json
{
  "project_name": "Vektor Platform",
  "category": "saas",
  "tones": ["precise", "calm", "minimal"],
  "density": "med",
  "page_type": "marketing",
  "audience": "senior DevOps engineers and CTOs",
  "primary_task": "lead generation and trial conversion"
}
```
- **Expected Aesthetic Archetype:** Engineered neo-grotesk typography (e.g. `Archivo`, `Switzer`, `General Sans`), slate/monochrome base with single vibrant status accent, dense structured data rhythm, verified pricing tiers, explicit trust indicators.

#### 3. Creative Agency & Brand Practice (`brief_creative`)
```json
{
  "project_name": "Bureau Helix",
  "category": "agency",
  "tones": ["bold", "editorial"],
  "density": "low",
  "page_type": "marketing",
  "audience": "brand directors and creative leads at mid-market companies",
  "primary_task": "case study showcase and new business inquiries"
}
```
- **Expected Aesthetic Archetype:** High-contrast display grotesque or condensed headline type, saturated color fields (e.g. Navy and pink), poster-scale statements, narrative case study presentation, conversion action mapped to bespoke project inquiries.

---

### D.2 Quantitative Evaluation Criteria (EV-1 to EV-6)

A run across the three benchmark briefs is considered successful if and only if it fulfills at least **5 of the following 6 objective evaluation criteria**:

| Code | Dimension | Metric / Evaluation Rule | Verification Method |
|---|---|---|---|
| **EV-1** | **Palette Differentiation** | `palette.id` and `--color-bg` must be distinct across all 3 sites | CSS token inspection |
| **EV-2** | **Typographic Pairing** | `--font-display` must resolve to at least 2 distinct font families | CSS font-family regex |
| **EV-3** | **Contextual Headline** | `H1` text must be distinct across all 3 sites; luxury site must not contain `"SaaS"`, `"workflows"`, or `"engineered for clarity"` | HTML AST parsing |
| **EV-4** | **Slot-Driven Rendering** | `#pricing` must be completely omitted from `Maison Atelier` (luxury portfolio) | HTML string search (`id="pricing"`) |
| **EV-5** | **Spatial Density Ratio** | `--space-xl` for `brief_luxury` (low density) must be $\ge 150\%$ of `--space-xl` for `brief_saas` (med/high density) | CSS token float comparison |
| **EV-6** | **Content Integrity** | Generated output must contain zero Atlas self-promotional terms (`"Atlas-Skill"`, `"deep immutability"`, `"tier 3"`) | Text scan on output HTML |

**Anti-Criteria (Invalid Differentiation):**
- Merely changing `--color-accent` while leaving typography, layout, and copy identical.
- Merely swapping project names in identical sentence templates.
- Fabricating unverified quantitative metrics (violates P0 integrity contract).

---

## E. P7 Implementation Proposal & Test Plan

### E.1 Scope and Boundaries

#### In Scope (P7 Work Packages):
1. **WP-1 (Scoring & Diversity):** Expand tone keyword matching via semantic synonym expansion (e.g. `precise` → `technical`/`quiet`). Score `audience` and `primary_task` keywords. Replace alphabetical tie-breaking in `runtime/composer.py` with contextual hashing.
2. **WP-2 (Brief-Aware Copy Resolution):** Implement a deterministic copy synthesis helper (`_resolve_brief_content(plan)`) in `runtime/generator.py` that maps category, art direction, and audience into truthful, authentic copy templates without external LLM runtime calls.
3. **WP-3 (Dynamic Token & Scale Injection):** Inject `typography.scale["step-head"]` directly into `h1` CSS styling. Modulate `--space-xl`, `--space-2xl`, and `--max-width` based on `brief.density`.
4. **WP-4 (Slot-Driven Section Assembler):** Render `<section>` elements dynamically in the exact order specified by `plan["composition"]["slots"]`. Automatically omit sections (such as `#pricing`) when absent from the plan slots.

#### Non-Goals (Strictly Out of Scope):
- No runtime calls to external LLM APIs for copy generation (preserves zero-dependency offline determinism).
- No modifications to `runtime/anti_slop.py`.
- No modification or breakage of existing P6 Bento Grid contracts (`atlas:features-bento`).
- No modification of `taste-skill/` or `projek-webiste/saas-dashboard/`.
- No new external npm or pip dependencies.

---

### E.2 Test-First Strategy (TDD Red → Green)

All proposed capabilities must be authored first in a standalone test suite:
`tests/test_art_direction_intelligence.py`

#### Proposed 15 Core Unit Tests:

```python
# Group 1: Art Direction Selection Diversity (GAP-1, GAP-6)
1. test_three_benchmark_briefs_produce_three_different_art_directions()
2. test_seven_diverse_briefs_produce_at_least_four_art_directions()
3. test_saas_precise_does_not_always_select_dressed_as_something_else()
4. test_audience_field_influences_art_direction_selection()

# Group 2: Contextual Copy & Content Integrity (GAP-2)
5. test_three_benchmark_briefs_produce_different_h1_text()
6. test_luxury_brief_h1_does_not_contain_saas_boilerplate()
7. test_brief_project_name_and_category_reflected_in_meta_description()
8. test_creative_agency_features_copy_does_not_contain_atlas_self_promo()

# Group 3: CSS Token & Fluid Scale Integration (GAP-3)
9.  test_low_density_brief_has_larger_space_xl_than_high_density()
10. test_typography_scale_step_head_used_for_h1_font_size()
11. test_max_width_reflects_brief_density()

# Group 4: Slot-Driven Section Rendering (GAP-5)
12. test_brief_with_exclude_pricing_omits_pricing_section()
13. test_studio_portfolio_plan_typically_omits_pricing_section()
14. test_plan_slot_order_is_respected_in_html_section_order()

# Group 5: Regression & Safety Guards
15. test_all_170_baseline_tests_still_pass_unaffected()
```

---

## F. Acceptance Criteria & Risk Matrix

### F.1 Objective Acceptance Criteria

| ID | Criterion | Verification Target | Pass Condition |
|---|---|---|---|
| **AC-1** | Art Direction Diversity | 7 diverse test briefs | $\ge 4$ unique Art Directions selected |
| **AC-2** | Distinct Headline Generation | 3 benchmark briefs | 3 distinct `H1` strings; luxury contains no tech jargon |
| **AC-3** | Contextual Pricing Control | `brief_luxury` HTML | `id="pricing"` does not exist in DOM |
| **AC-4** | Spatial Scale Responsiveness | CSS token extraction | `--space-xl` (low density) $\ge 1.5 \times$ `--space-xl` (high density) |
| **AC-5** | Fluid Typography Scale | CSS `h1` font-size | Contains `typography.scale["step-head"]` value |
| **AC-6** | Anti-Slop Cleanliness | All 3 benchmark sites | Zero hard failures (`failures_count == 0`) |
| **AC-7** | CDP Zero-Overflow | Chrome headless inspection | `scrollWidth <= clientWidth` across all 5 standard viewports |
| **AC-8** | Zero Regressions | Full test suite | 100% of all 170 baseline tests PASS |

### F.2 Risk Assessment & Mitigation

| Risk ID | Description | Likelihood | Impact | Mitigation Strategy |
|---|---|---|---|---|
| **R-1** | **Scoring changes alter legacy benchmark outputs** | High | Medium | Run `test_p5_e2e_integration.py` and `test_capabilities.py` on every iteration. Use non-disruptive additive scoring weights for `audience`. |
| **R-2** | **Dynamic copy triggers anti-slop warnings** | Medium | High | Audit copy templates against `runtime/anti_slop.py` rules (no buzzwords like `"next-gen"`, no repetitive card spam, no multi-accent containers). |
| **R-3** | **Slot-driven rendering breaks DOM structure assumptions** | Medium | Medium | Maintain standard semantic landmarks (`<header>`, `<main>`, `<footer>`) regardless of which inner sections are enabled. |
| **R-4** | **Missing typography scale raises KeyErrors** | Low | Low | Implement robust `.get("scale", {}).get("step-head", default)` fallbacks in `render_css()`. |

---

## G. Projected File Modifications

### Target Implementation Files (Production Code):
1. **`runtime/scorer.py`**:
   - Add `TONE_SYNONYMS` dictionary.
   - Update `score_art_direction()` to score expanded tone affinities, audience keywords, and primary task keywords.
2. **`runtime/composer.py`**:
   - Update `ranked_ad.sort()` to use sector prominence ranking and deterministic brief context hashing rather than static alphabetical ID tie-breaking.
3. **`runtime/contracts.py`**:
   - Update `ProductBrief.__init__()` to filter `self.slots` against `self.exclude` and contextually omit `pricing` for portfolio/studio categories when slots are not explicitly supplied.
4. **`runtime/generator.py`**:
   - Update `render_css()` to inject density-responsive spacing tokens and typography scale values.
   - Implement `_resolve_brief_content(plan)` for category-aware copy synthesis.
   - Refactor `render_html()` to assemble sections dynamically based on `plan["composition"]["slots"]`.
5. **`skills/atlas-skill/SKILL.md`**:
   - Document the Art Direction & Visual Identity Intelligence contract in Section 2.

### Target Test Files:
1. **`tests/test_art_direction_intelligence.py`**:
   - Standalone test suite covering all 15 unit tests.

### Strictly Protected / Untouched Files:
- `runtime/anti_slop.py` (Rule definitions remain invariant)
- `tests/test_bento_grid_layout.py` (P6 regression guard)
- `tests/test_cdp_fixtures.mjs` (CDP fixture baseline)
- `taste-skill/` (Protected external repository)
- `projek-webiste/saas-dashboard/` (Protected external project)

---

## H. Recommended Implementation Sequence & Checkpoints

To ensure safe, reviewable progress, implementation should proceed in three distinct phases with mandatory user review checkpoints:

```
[CHECKPOINT 0: AUDIT APPROVAL (Current State)]
      │
      ▼
┌─────────────────────────────────────────────────────────────┐
│ TAHAP 1 — TDD RED (Author Test Suite)                       │
│ • Create tests/test_art_direction_intelligence.py           │
│ • Verify that new P7 tests FAIL as expected                 │
│ • Verify that 170 baseline tests REMAIN PASSING             │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
[CHECKPOINT 1: TDD RED VERIFICATION APPROVAL]
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ TAHAP 2 — TDD GREEN (Core Production Implementation)        │
│ • Update runtime/scorer.py (synonyms & audience scoring)    │
│ • Update runtime/composer.py (contextual tie-break)         │
│ • Update runtime/contracts.py (slot filtering)              │
│ • Update runtime/generator.py (CSS scale & dynamic copy)    │
│ • Update skills/atlas-skill/SKILL.md (contracts)            │
│ • Verify all tests PASS (170 baseline + new P7 tests)       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
[CHECKPOINT 2: TDD GREEN VERIFICATION APPROVAL]
                               │
                               ▼
┌─────────────────────────────────────────────────────────────┐
│ TAHAP 3 — VISUAL BENCHMARK QA & SCREENSHOT REVIEW           │
│ • Generate benchmark_luxury, benchmark_saas, benchmark_agency│
│ • Execute BrowserQAHarness multi-viewport CDP layout audits │
│ • Inspect screenshots and verify zero-overflow / collisions │
│ • Compile final P7 release report                           │
└──────────────────────────────┬──────────────────────────────┘
                               │
                               ▼
[CHECKPOINT 3: FINAL P7 SIGN-OFF & STAGING]
```

---

## Confirmation of Audit Hygiene

- **File Modifications during Audit:** Exactly one new file created: `docs/phase-7/P7_ART_DIRECTION_AUDIT_REPORT.md`.
- **Zero Code Changes:** No files in `runtime/`, `tests/`, `data/`, or `skills/` have been staged, committed, or permanently modified.
- **Protected Boundaries:** `taste-skill/` and `projek-webiste/saas-dashboard/` remain untouched.
- **Execution Stop:** Execution halted immediately following report generation, awaiting explicit user authorization.

