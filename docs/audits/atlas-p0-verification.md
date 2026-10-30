# Atlas P0 Verification Report — Strict Read-Only Audit

**Document Path:** `atlas-skill/docs/audits/atlas-p0-verification.md`  
**Evaluation Date:** 2026-10-30  
**Evaluator:** Antigravity Pair Programming Agent  
**Execution Scope:** Read-Only Verification in `D:\tes\skills-staging`  
**Actual Test Run:** `py -3 -m unittest discover -s "atlas-skill/tests" -p "test_*.py"`  
**Result:** 135 tests ran in 24.717s — 0 failures, 0 errors (`OK`)  

---

## Executive Summary

This verification report confirms the source code reality of the two P0 findings identified in the Atlas vs. Taste comparison audit:

1. **P0.1 — Reference Loading Isolation (Confirmed):**  
   All 11 Taste reference Markdown documents exist physically in `atlas-skill/knowledge/taste/references/`, but they are entirely orphaned from runtime execution and agent prompting. `atlas-skill/skills/atlas-skill/SKILL.md` never mentions them, and `runtime/retriever.py` merely outputs static string metadata citations without opening or loading any file contents.

2. **P0.2 — Chart & Quantitative Asset Integrity (Confirmed):**  
   The Tier 3 vector fallback generator in `atlas-skill/runtime/assets.py` produces misleading quantitative visualizations. In `_generate_fintech_svg()` and `_generate_saas_svg()`, arbitrary numbers (`$2,485,920.00 USD`, `+14.8% APY`, `$2.50M` gridlines, `84,200 req/s`) and synthetic quadratic Bézier trend curves are hardcoded into SVG assets. Crucially, existing test suites (`test_website_generator.py` and `test_asset_boundary.py`) actively assert the presence of these fabricated values in the generated output.

---

## Task 1 — Verify Reference Loading (P0.1)

### 1. Finding
**CONFIRMED.**  
The design reference manuals are physically packaged within the skill directory structure, but they are genuinely unused at runtime and absent from the LLM prompt instructions.

---

### 2. Evidence & Code Path Tracing

#### A. Prompt-Level Isolation in `SKILL.md`
* **File:** `atlas-skill/skills/atlas-skill/SKILL.md`
* **Lines 11–15 (Section 1 — Architectural Contracts):**
  ```markdown
  - **Canonical Design Library:** Unified datasets in `data/` and `knowledge/taste/library/` (`art-directions.json`, `compositions.json`, `palettes.json`, `typography.json`, `motions.json`, `photos.json`, `app-shells.json`).
  ```
* **Lines 49–63 (Section 5 — The 10-Step Execution Run):**
  * Step 2: *"Retrieve Contextual References: Query `CanonicalLibrary` for eligible art directions, layouts, typographies, and motion patterns."*
  * Step 9: *"Audit Against Anti-Slop Intelligence: Run `runtime/anti_slop.py`..."*
* **Observation:** `SKILL.md` guides the agent to query the JSON datasets and run the Python scripts, but contains **zero instructions** to open or read files in `knowledge/taste/references/`.

#### B. Physical Inventory of Reference Files
The directory `atlas-skill/knowledge/taste/references/` exists and contains 11 active Markdown files:
* `app-screens.md` (86,743 bytes) — Detailed specifications for data-dense dashboards, tables, and ledgers.
* `colour.md` (7,175 bytes) — CSS color token contracts and single-accent rules.
* `copy.md` (9,792 bytes) — Headline constraints and product messaging clarity.
* `critique.md` (11,522 bytes) — 10-pass aesthetic critique rubric.
* `imagery.md` (51,998 bytes) — Subject focal area rules (40% hero focal area).
* `layout.md` (18,788 bytes) — Grid systems, off-center text anchoring, and responsive reflow.
* `motion.md` (56,561 bytes) — Choreography principles and physics curves.
* `research.md` (24,801 bytes) — Panel teardowns and study metrics across 247 sites.
* `scenes.md` (10,172 bytes) — Section transitions and narrative arcs.
* `tells.md` (7,715 bytes) — 3-wave registry of AI design clichés.
* `type.md` (8,844 bytes) — Typographic pairing multipliers and scale rules.

#### C. Codebase-Wide Retrieval Inspection
* **File:** `atlas-skill/runtime/retriever.py`
* **Lines 143–211 (`retrieve_design_references`):**
  ```python
  applicable_heuristics = [
      {
          "id": "law-two-line-headline",
          "name": "Two-Line Headline Limit",
          "source": "knowledge/taste/references/copy.md",
          "rule": "Headlines must not wrap past 2 lines; budget 24-32 characters for maximum impact."
      },
      {
          "id": "law-40-percent-focal-point",
          "name": "40% Hero Focal Area",
          "source": "knowledge/taste/references/imagery.md",
          "rule": "Primary visual subject or hero image must command at least 40% of viewport area."
      }
  ]
  if page_type == "app" or getattr(brief, "density", "med") == "high":
      applicable_heuristics.append({
          "id": "guideline-dense-ui-stillness",
          "name": "Operational Stillness & Density",
          "source": "knowledge/taste/references/app-screens.md",
          "rule": "Dense data dashboards prioritize stillness, tabular figures, and structured card grouping over decorative motion."
      })
  ```
* **Finding:** The function returns static dictionary entries with hardcoded strings. Neither `retriever.py` nor `composer.py` executes `open()`, `read()`, or any filesystem retrieval on the target Markdown files.
* **File:** `atlas-skill/tests/test_knowledge_manifest.py`
* **Lines 48–49:** Asserts only that the string paths `"references/motion.md"` and `"references/tells.md"` exist in `knowledge/taste/manifest.json`. No runtime loading is verified.

#### D. Content Guidance in Target Reference Files
1. **`tells.md` (`atlas-skill/knowledge/taste/references/tells.md`):**
   * *Lines 33–42 (Wave 1):* Banned: violet/indigo gradients on hero/buttons, gradient headline text, 3 identical feature cards with icons in rounded squares, emoji bullets.
   * *Lines 46–56 (Wave 2):* Banned/Warned: tiny tracked uppercase eyebrow kickers, pill badges above hero, fake dashboard hero built from grey bars and donut charts.
2. **`colour.md` (`atlas-skill/knowledge/taste/references/colour.md`):**
   * *Lines 42–56:* Declares semantic CSS variables (`--bg`, `--surface`, `--ink`, `--muted`, `--accent`, `--accent-ink`). Mandates single-accent discipline: raw hex values in components create an unauthorized second palette.
3. **`layout.md` (`atlas-skill/knowledge/taste/references/layout.md`):**
   * *Lines 29–46:* Establishes tight margins (`clamp(1rem, 2.2vw, 2rem)`), off-center text anchoring, avoiding default `max-width: 1200px; margin: auto` wrappers, and treating mobile viewports as distinct compositions rather than squeezed desktop grids.
4. **`app-screens.md` (`atlas-skill/knowledge/taste/references/app-screens.md`):**
   * *Lines 12–38:* Directly diagnoses generated dashboards: forbids 4 KPI cards with icons in colored circles and decorative sparklines; mandates that color belongs on data (not chrome); requires flat surfaces (no card shadows), small headings (≤24px), minimal chart chrome (no legends for single series, ≤7 faint gridlines), and honest empty states.

---

### 3. Risk Analysis
* **Prompt Token Bloat:** Loading all 11 files indiscriminately would consume ~280 KB (~65k tokens) on every conversation turn, increasing latency and prompt costs.
* **Schema Breakage:** Modifying `runtime/retriever.py` to dump raw file contents into `DesignPlan` JSON could violate downstream JSON contracts verified in `tests/test_composition_engine.py`.

---

### 4. Minimal Implementation Plan
* **Target File:** `atlas-skill/skills/atlas-skill/SKILL.md`
* **Mechanism:** Progressive instruction disclosure. Instruct the coding agent to conditionally read specific reference files based on context:
  * In Step 2 (Context Retrieval): If `page_type == "app"` or dashboard, read `knowledge/taste/references/app-screens.md`.
  * In Step 7 (Markup & Styling): Read `knowledge/taste/references/colour.md` and `layout.md`.
  * In Step 9 (Anti-Slop Audit): Read `knowledge/taste/references/tells.md`.
* **Zero changes** to Python loaders or JSON schemas.

---

### 5. Verification Plan
* Run full test suite (`py -3 -m unittest discover -s "atlas-skill/tests" -p "test_*.py"`).
* Verify that an agent invoked on a dashboard brief actively opens `knowledge/taste/references/app-screens.md` without loading unrelated guides.

---

## Task 2 — Verify Chart Integrity (P0.2)

### 1. Finding
**CONFIRMED.**  
Atlas generates **misleading quantitative visuals using hardcoded sample points and synthetic numbers**, presenting them as authentic analytical dashboards. Existing tests explicitly enforce these hardcoded values.

---

### 2. Evidence & Code Path Tracing

#### A. End-to-End Asset Generation Call Site Trace
1. **Trigger:** `runtime/composer.py` calls `AssetResolver.resolve()` (Line 147).
2. **Resolution Pipeline:** `AssetResolver.resolve()` (`runtime/assets.py`, Lines 349–368) invokes `generate_svg_fallback()`.
3. **Category Branching:** `generate_svg_fallback()` (`runtime/assets.py`, Lines 274–284):
   * Categories `fintech`, `finance`, `crypto`, `banking`: invokes `_generate_fintech_svg(w, h, asset_id)` (Line 276).
   * Categories `saas`, `cloud`, `dev-tool`: invokes `_generate_saas_svg(w, h, asset_id)` (Line 279).
   * Other categories: invokes `_generate_generic_svg()` (Line 282).
4. **HTML Embedding:** `runtime/generator.py` (Lines 574–580) writes the resulting SVG to disk and embeds `<img src="assets/hero.svg">`.

#### B. Inspection of Generated SVGs in `atlas-skill/runtime/assets.py`
* **`_generate_fintech_svg()` (Lines 78–167):**
  * *Line 118:* Hardcoded balance headline: `<text ...>$2,485,920.00 USD</text>`
  * *Line 120:* Hardcoded APY badge: `<text ...>+14.8% APY</text>`
  * *Lines 131–134:* Quantitative Y-axis gridlines: `<text>$2.50M</text>`, `<text>$2.00M</text>`, `<text>$1.50M</text>`.
  * *Lines 137–139:* Hardcoded quadratic Bézier curve representing a time-series stock/yield trend:
    ```svg
    <path d="M 40 300 L 40 280 Q 140 270 240 240 T 440 200 T 640 170 L {w - 40} 160 L {w - 40} 300 Z" fill="url(#chart_grad_{asset_id})" />
    ```
  * *Line 147:* Hardcoded tooltip data point: `Peak: $2.51M`.
  * *Lines 156, 161, 166:* Hardcoded percentage breakdown cards: `$1,441,833 (58%)`, `$671,200 (27%)`, `$372,887 (15%)`.
* **`_generate_saas_svg()` (Lines 170–219):**
  * *Lines 199, 203, 207:* Synthetic telemetry cards: `148 / 148 Active Microservices`, `84,200 req/s Throughput`, `4.2 ms P99 Latency`.
  * *Line 214:* Synthetic ingress network flow curve connecting fictional nodes.
* **`_generate_generic_svg()` (Lines 222–248):**
  * Abstract geometric composition utilizing category MD5-hash hues. **Legitimate, non-misleading decorative artwork.**

#### C. Search for Data-Binding Interfaces
* `generate_svg_fallback()` signature (`runtime/assets.py`, lines 251–257):
  ```python
  def generate_svg_fallback(
      asset_id: str,
      asset_type: str,
      aspect_ratio: str,
      category: str,
      art_direction_name: str
  ) -> Dict[str, Any]:
  ```
* **Result:** No dataset, time series array, or metric dictionary is passed into the generator. The visual is rendered purely from static string literals.

#### D. Existing Tests Asserting Invented Values
* **File:** `atlas-skill/tests/test_asset_boundary.py`
  * *Line 64:* `self.assertIn("INSTITUTIONAL TREASURY LEDGER", req.fallback_descriptor["svg_snippet"])`
* **File:** `atlas-skill/tests/test_website_generator.py`
  * *Lines 97–100:* Asserts that the HTML does not contain invented business metrics (`99.99%`, `10M+`, `3.2x`).
  * *Lines 114–116:* **Contradiction:** Explicitly asserts that the generated SVG asset contains invented metrics:
    ```python
    self.assertIn("INSTITUTIONAL TREASURY LEDGER", svg_content)
    self.assertIn("MULTI-SIG VERIFIED", svg_content)
    self.assertIn("$2,485,920.00 USD", svg_content)
    ```

---

### 3. Risk Analysis
* **Immediate Test Regressions:** If `$2,485,920.00 USD` or `INSTITUTIONAL TREASURY LEDGER` is removed from `_generate_fintech_svg()` without simultaneously updating `test_website_generator.py` and `test_asset_boundary.py`, the test suite will fail.
* **Broken Visual Hierarchy:** Deleting the fallback SVG entirely would cause hero sections to render broken image icons in offline environments.

---

### 4. Minimal Implementation Plan
1. **Refactor `atlas-skill/runtime/assets.py`:**
   * Distinguish between *analytical charts* (which must bind to real data or display an explicit empty state) and *editorial illustrations*.
   * In `_generate_fintech_svg()` and `_generate_saas_svg()`, convert the graphic from a pseudo-analytical chart into an architectural abstraction (or explicitly watermark it with `SAMPLE PREVIEW • NON-ANALYTICAL`). Remove simulated coordinate axes and fake tooltips.
2. **Update Tests (`test_website_generator.py`, `test_asset_boundary.py`):**
   * Change string assertions from checking literal monetary balances (`$2,485,920.00 USD`) to checking structural elements (e.g., `<svg`, `viewBox`, accessibility labels).
3. **Codify in `atlas-skill/skills/atlas-skill/SKILL.md`:**
   * Add a rule under Section 4 prohibiting ungrounded quantitative visuals.

---

### 5. Verification Plan
* Execute targeted unit tests:
  * `py -3 -m unittest atlas-skill/tests/test_asset_boundary.py`
  * `py -3 -m unittest atlas-skill/tests/test_website_generator.py`
* Execute full test suite:
  * `py -3 -m unittest discover -s "atlas-skill/tests" -p "test_*.py"`

---

## Test Execution Record

The existing Atlas Skill test suite was executed in its entirety to establish an empirical baseline before any future implementation:

```powershell
py -3 -m unittest discover -s "atlas-skill/tests" -p "test_*.py"
```

**Output:**
```
.......................................................................................................................................
----------------------------------------------------------------------
Ran 135 tests in 24.717s

OK
```
* **Status:** All 135 unit tests pass on Python 3.10.10.

---

## Distinctions: Verified Findings vs. Unresolved Questions

### Verified Facts
* `atlas-skill/knowledge/taste/references/` contains 11 complete, unreferenced Markdown manuals.
* `atlas-skill/skills/atlas-skill/SKILL.md` does not instruct the agent to read any reference files.
* `_generate_fintech_svg()` and `_generate_saas_svg()` generate static, fabricated quantitative figures.
* `test_website_generator.py` explicitly tests for the existence of `$2,485,920.00 USD` inside the generated SVG.

### Unresolved Design Decisions Requiring Human Judgment
1. **Fallback Graphic Style:** Should Tier 3 fallback assets for fintech/saas be purely abstract geometric compositions (like `_generate_generic_svg`), or should they remain interface wireframes with explicit placeholder watermarks (`--` or `PREVIEW`)?
2. **Automated vs. Manual Reference Reading:** Should the Python `retriever.py` inject relevant reference summaries directly into the `DesignPlan` JSON, or should `SKILL.md` instruct the LLM agent to read the reference markdown files directly using filesystem tools?

---

## Change Audit Confirmation

* **Target File Created:** `D:\tes\skills-staging\atlas-skill\docs\audits\atlas-p0-verification.md`
* **Source Code Changes:** `0` (Zero files modified in `atlas-skill/runtime/`, `atlas-skill/skills/`, or adapters)
* **Test Code Changes:** `0` (Zero files modified in `atlas-skill/tests/`)
* **Reference Repositories:** `0` (Zero files modified in `taste-skill/` or `projek-webiste/`)
* **Total Permitted Mutation:** Exactly 1 file (this report).

