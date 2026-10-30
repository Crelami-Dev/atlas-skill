# Atlas Skill — Evidence-Driven Defect Remediation Report

**Date:** 2026-10-30  
**Repository:** `D:\tes\skills-staging`  
**Scope:** Remediation of the two defects uncovered during real-world evaluation:
1. Conditional hero asset injection in `runtime/generator.py` (resolves `S021: Missing local image file`).
2. Interactive-control role classification order in `runtime/anti_slop.py` (prevents `rounded-full` buttons from escaping control checks).
**Status:** IMPLEMENTED & FULLY VERIFIED (158/158 Tests Passed, Live Browser QA PASSED)

---

## 1. Executive Summary

During real-world evaluation, two concrete defects were uncovered:
1. **Unconditional Hero Asset Injection:** Generating a high-density SaaS application layout (which has 0 asset requirements) still injected `<img src="assets/hero.svg">` into the template. The file did not exist on disk, triggering DOM quality gate failure `S021` in headless browser QA (`browser_runtime_evaluation: FAIL`).
2. **Control Role Misclassification on Pill Buttons:** In `anti_slop.py`, checking `rounded-full` before `<button>` tag checking caused pill-shaped buttons (`<button class="btn rounded-full">`) to be categorized as `badge-or-avatar` rather than `control`, allowing mixed pill and rectangular buttons to escape detection when only one rectangular button was present.

Both defects have been surgically resolved, covered by 4 new regression tests, and verified via the real Atlas CLI and headless Chrome Browser QA. All 158 tests pass with exit code 0.

---

## 2. Root Cause & Technical Remediation

### Fix A: Conditional Hero Asset Injection
- **Root Cause:** In `runtime/generator.py`, `hero_img_src = hero_asset.get("relative_url", "assets/hero.svg")` defaulted to `"assets/hero.svg"` even when `plan['assets']['requirements']` was empty.
- **Fix Applied:**
  1. Updated `render_html()`: if `hero_asset` is absent or lacks a `relative_url`, `hero_media_html` evaluates to `""` (no `<img>` or `.hero-media` container is rendered).
  2. Added responsive CSS modifier `.hero-grid-single { grid-template-columns: 1fr; max-width: 800px; }` in `render_css()` to ensure balanced visual layout when no hero image is present.
  3. When an asset is required (e.g. marketing landing pages), the image reference and SVG generation behavior are 100% preserved.

### Fix B: Control Role Misclassification on Pill Buttons
- **Root Cause:** In `runtime/anti_slop.py` (`ASTElement.get_role_family`), the shape check `if "rounded-full" in cls.lower(): return "badge-or-avatar"` ran *before* interactive tag checking `if self.tag in ("input", "button", "select", "textarea"): return "control"`.
- **Fix Applied:**
  1. Reordered `get_role_family()` so interactive tags (`button`, `input`, `select`, `textarea`) and control classes (`btn`, `form-control`) take strict precedence over shape-based classes.
  2. Non-interactive circular avatars and badges (`<img class="avatar rounded-full">` or `50%` radius) remain classified as `badge-or-avatar` and excluded from peer card checks.

---

## 3. Exact Files Modified & Diffs

| File Path | Changes Made | Lines Changed |
|---|---|:---:|
| `atlas-skill/runtime/generator.py` | Conditional `hero_media_html` injection + `.hero-grid-single` CSS rule | +16 / -7 |
| `atlas-skill/runtime/anti_slop.py` | Reordered `get_role_family()` to check controls before `rounded-full` | +5 / -5 |
| `atlas-skill/tests/test_website_generator.py` | Added regression tests for zero-asset and asset-required hero generation | +35 / -1 |
| `atlas-skill/tests/test_anti_slop_rules.py` | Added regression tests for mixed pill/rect controls & avatar exemptions | +32 / -0 |

---

## 4. Regression Tests Added

### 4.1 Website Generator (`tests/test_website_generator.py`)
1. `test_zero_asset_plan_omits_hero_image_reference`:
   - Builds a high-density SaaS app plan with 0 asset requirements.
   - Verifies that `index.html` contains NO `assets/hero.svg`, NO `<div class="hero-media">`, and applies `.hero-grid-single`.
2. `test_asset_required_plan_preserves_hero_image_reference`:
   - Builds an asset-required fintech marketing plan.
   - Verifies that `<div class="hero-media">` and `<img src="assets/...">` are preserved, and that the SVG file exists on disk.

### 4.2 Anti-Slop Rules (`tests/test_anti_slop_rules.py`)
1. `test_inconsistent_radius_mixed_pill_and_rect_controls_warns`:
   - Tests a toolbar containing exactly one rectangular button (`rounded-md`) and one pill button (`rounded-full`).
   - Asserts that `inconsistent-radius` emits `WARN` referencing conflicting radii (`rounded-full`, `6px`) in `<div class='toolbar'>`.
2. `test_inconsistent_radius_avatar_remains_exempt_from_card_warning`:
   - Tests peer cards with `border-radius: 12px` containing non-interactive circular avatars (`<img class="avatar rounded-full">`).
   - Asserts that avatars remain classified as `badge-or-avatar` and do NOT trigger a false positive against the cards.

---

## 5. Test Suite Execution Results

### 5.1 Targeted Regression Tests
```powershell
py -3 -m unittest atlas-skill/tests/test_website_generator.py atlas-skill/tests/test_anti_slop_rules.py
```
- **Exit Code:** `0`
- **Output:**
  ```
  ............................
  ----------------------------------------------------------------------
  Ran 28 tests in 0.284s

  OK
  ```

### 5.2 Full Repository Test Suite Discovery
```powershell
py -3 -m unittest discover -s "atlas-skill/tests" -p "test_*.py"
```
- **Exit Code:** `0`
- **Output:**
  ```
  ..............................................................................................................................................................
  ----------------------------------------------------------------------
  Ran 158 tests in 23.021s

  OK
  ```
- **Total Tests Ran:** `158` (154 previous + 4 new regression tests)
- **Failures:** `0`
- **Errors:** `0`

---

## 6. Live Browser QA Re-Verification

### 6.1 Real Atlas CLI SaaS Dashboard Verification (Fix A Verification)
```powershell
py -3 -c "import sys; sys.path.insert(0, 'atlas-skill'); from runtime.cli import main; sys.exit(main(['--category', 'saas', '--page-type', 'app', '--density', 'high', '--tones', 'minimal,precise', '--build', 'atlas-skill/tests/artifacts/eval_fix/saas_dashboard', '--qa']))"
```
- **Generated Output:** 3 core files (`index.html`, `styles.css`, `script.js`), 0 assets emitted.
- **Browser Visual QA Result:**
  - Desktop 1440x900: **PASS** (80,022 bytes screenshot)
  - Tablet Portrait 768x1024: **PASS** (67,128 bytes screenshot)
  - Mobile 390x844: **PASS** (46,156 bytes screenshot)
- **DOM Quality Gate Result:**
  - `exit_code: 0`, `passed: true`
  - `summary: {"fail": 0, "warn": 0, "info": 1}`
  - **`S021: Missing local image file` is completely resolved.**
  - **Overall QA Status: PASS.**

### 6.2 Marketing Landing Page Verification (Authentic Visual Preservation)
```powershell
py -3 -c "import sys; sys.path.insert(0, 'atlas-skill'); from runtime.cli import main; sys.exit(main(['--category', 'fintech', '--page-type', 'marketing', '--density', 'med', '--tones', 'editorial,bold', '--build', 'atlas-skill/tests/artifacts/eval_fix/marketing_landing', '--qa']))"
```
- **Generated Output:** 3 core files + 1 asset (`assets/hero.svg`).
- **Browser Visual QA Result:** **PASS** across all viewports (Desktop 147 KB, Tablet 131 KB, Mobile 74 KB).
- **Metric Integrity:** Zero fabricated financial metrics ($2.48M, +14.8%) returned. Renders authentic institutional treasury architectural vector graphics.

---

## 7. Repository Boundary Safeguards

- **`taste-skill/`:** `git -C taste-skill status` confirms `nothing to commit, working tree clean` (**100% UNTOUCHED**).
- **SubTrack (`projek-webiste/saas-dashboard/`):** All source files in `src/styles` and `src/components/views` remain at pre-audit timestamps (`6:39 PM`) (**100% UNTOUCHED**).
- **Working Tree:** `git -C atlas-skill status --short` confirms only intended runtime and test files modified.

---

## 8. Final Verdict

**Verdict:** **PASS (STABLE RELEASE READY)**

Both defects are resolved, verified by automated unit tests and live headless Chrome visual QA, with zero boundary violations.

