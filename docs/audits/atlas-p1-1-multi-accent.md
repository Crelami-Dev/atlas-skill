# Atlas P1.1 — AST-Based Multi-Accent Detection Report

**Document Path:** `atlas-skill/docs/audits/atlas-p1-1-multi-accent.md`  
**Execution Date:** 2026-10-30  
**Evaluator & Implementer:** Antigravity Pair Programming Agent  
**Scope:** Strictly P1.1 (Multi-Accent Detection in `anti_slop.py`). P1.2 and P2 changes excluded.  
**Repository Baseline:** `D:\tes\skills-staging`  
**Full Test Suite Result:** 142 tests ran in 24.297s — 0 failures, 0 errors (`OK`)  

---

## 1. Executive Summary

In Phase 1.1, a conservative, AST-based multi-accent color heuristic was designed, implemented, and verified in `atlas-skill/runtime/anti_slop.py`. 

The heuristic directly targets the "rainbow cards" tell (observed in the SubTrack audit, where adjacent metric cards display uncoordinated saturated accents such as cyan, emerald, purple, and amber). Crucially, the implementation is **container-scoped** rather than whole-page, normalizes equivalent color formats (hex, RGB, HSL, Tailwind utilities), and provides robust exemptions for semantic status indicators and data visualizations.

---

## 2. Technical Architecture & Implementation

### A. Zero-Dependency DOM AST Tree Builder
* Reused Python's standard library `html.parser.HTMLParser` via `DOMTreeBuilder` and `ASTElement`.
* Constructs an in-memory parent-child node tree that captures tag names, attribute dictionaries, and structural hierarchy.
* Identifies component container boundaries (`<section>`, `<article>`, `<header>`, `<nav>`, and elements with classes matching `grid`, `metrics`, `card`, `bento`, `panel`, etc.) while explicitly excluding global page shells (`<html>`, `<body>`, `<main>`, `#root`, `#app`).

### B. Color Normalization & Perceptual Classification
* **Color Value Extraction:** Parses inline styles (`color`, `background-color`, `fill`, `stroke`), CSS class rules, and Tailwind color utility classes (`bg-cyan-500`, `text-emerald-400`, etc.).
* **Format Normalization (`parse_color_tuple`):** Normalizes `#rgb`, `#rrggbb`, `rgb()`, `rgba()`, `hsl()`, and `hsla()` into standardized `(r, g, b)` integer tuples.
* **Perceptual Family Mapping (`get_saturated_accent_family`):**
  * Converts RGB to HLS float values using Python's standard library `colorsys.rgb_to_hls()`.
  * **Neutral Filtering:** Excludes low-saturation colors (`saturation < 0.20`) and extreme lightness values (`lightness < 0.12` near-black, `lightness > 0.92` near-white), ensuring body inks, surfaces, backgrounds, and grey borders are never misclassified as accents.
  * **Hue Family Grouping:** Groups saturated colors (`saturation >= 0.20`, `0.12 <= lightness <= 0.92`) into 8 canonical hue family bands (`red`, `amber`, `yellow`, `green`, `cyan`, `blue`, `purple`, `pink`). Different shades of the same family (e.g. `cyan-400` vs `sky-500`) resolve to the same family and are counted as a single accent.

### C. Container Scoping & Deduplication
* Findings are evaluated at the component/container level (`find_multi_accent_containers`).
* **Section Boundary Isolation:** Does not aggregate colors across separate sibling `<section>` or `<article>` components into top-level wrappers.
* **Hierarchical Deduplication:** If an inner component (e.g. `<div class='metrics-grid'>`) exhibits 3+ accents, any ancestor container (e.g. `<div class='section-wrapper'>`) that merely encloses that component is deduplicated to report the most specific container.

### D. False-Positive Protections
1. **Semantic Status Elements (`is_semantic_status`):**
   * Elements with classes (`status`, `alert`, `success`, `warning`, `error`, `danger`, `info`, `badge-success`, etc.) or attributes (`role="alert"`, `data-status`) are exempt. Their colors communicate operational system states, not decorative branding.
2. **Data Visualizations & Charts (`is_dataviz`):**
   * Elements within `<svg>`, `<canvas>`, `<chart>`, `<figure>`, or elements with classes like `chart`, `dataviz`, `graph`, `map`, `plot`, `legend`, or `role="img"` are exempt. Multi-series charts legitimately require distinct categorical hues.
3. **Contextual Brief Tone Rationale:**
   * If a product brief specifies `playful`, `creative`, `colorful`, `rainbow`, or `multi-accent` tones, findings are downgraded from `WARN` to `INFO` with contextual design rationale.
   * Rules can be explicitly bypassed using `allow_rules=["multi-accent-container"]`.

---

## 3. Test Coverage & Verification Matrix

7 dedicated test cases were added to `atlas-skill/tests/test_anti_slop_rules.py` to prove correctness and absence of false positives:

| # | Test Method Name | Scenario Tested | Expected Result | Actual Result |
| :-: | :--- | :--- | :--- | :---: |
| 1 | `test_multi_accent_three_distinct_accents_triggers_warning` | 3 distinct saturated accents (cyan, emerald, purple) in one container | Emits `WARN` for `multi-accent-container` | **PASS** |
| 2 | `test_multi_accent_one_or_two_accents_no_warning` | 2 accents plus another shade of the same family | Zero warnings emitted | **PASS** |
| 3 | `test_multi_accent_equivalent_hex_rgb_normalized` | Equivalent hex (`#38bdf8`) and RGB (`rgb(56, 189, 248)`) | Counted as 1 distinct color (no warning) | **PASS** |
| 4 | `test_multi_accent_semantic_status_colors_exempt` | 4 status badges (green, amber, red, blue) marked with status classes | Recognized as semantic status (no warning) | **PASS** |
| 5 | `test_multi_accent_dataviz_chart_exempt` | Multi-series SVG line chart with 4 colored paths | Recognized as dataviz container (no warning) | **PASS** |
| 6 | `test_multi_accent_separate_components_not_combined` | 3 sections each having 1 distinct accent color | Not aggregated across sections (no warning) | **PASS** |
| 7 | `test_multi_accent_output_schema_and_contextual_rationale` | 3 accents evaluated against a "playful" brief | Emits `INFO` with contextual rationale | **PASS** |

---

## 4. Test Execution Records

### Targeted Anti-Slop Test Suite
Command executed:
```powershell
py -3 -m unittest atlas-skill/tests/test_anti_slop_rules.py
```
Output:
```
............
----------------------------------------------------------------------
Ran 12 tests in 0.007s

OK
```
*(All 5 pre-existing tests + 7 new P1.1 tests passed cleanly).*

### Integration Test Suite
Command executed:
```powershell
py -3 -m unittest atlas-skill/tests/test_asset_boundary.py atlas-skill/tests/test_website_generator.py atlas-skill/tests/test_p5_e2e_integration.py
```
Output:
```
.............
----------------------------------------------------------------------
Ran 13 tests in 0.336s

OK
```

### Full Atlas Skill Test Suite
Command executed:
```powershell
py -3 -m unittest discover -s "atlas-skill/tests" -p "test_*.py"
```
Output:
```
..............................................................................................................................................
----------------------------------------------------------------------
Ran 142 tests in 24.297s

OK
```

---

## 5. Scope & Boundary Sign-Off

* **Files Modified in P1.1:**
  1. `atlas-skill/runtime/anti_slop.py` (Color parsing, AST builder, container scanner, rule dispatch).
  2. `atlas-skill/tests/test_anti_slop_rules.py` (7 new test cases).
* **`taste-skill/` Repository:** 100% untouched (`git status: working tree clean`).
* **`projek-webiste/saas-dashboard/`:** 100% untouched (`src/` timestamps preserved from earlier session).
* **Unrelated Atlas Features:** No changes to animation adapters, CDP browser runners, layout contracts, or palettes.
* **P1.2 / P2 Isolation:** No corner-radius token refactoring or performance changes were included.

