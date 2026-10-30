# Atlas P1.2 — Context-Aware Corner Radius Consistency Implementation & Verification Report

**Date:** 2026-10-30  
**Repository:** `D:\tes\skills-staging\atlas-skill`  
**Target Rule:** `inconsistent-radius` in `runtime/anti_slop.py`  
**Status:** IMPLEMENTED & VERIFIED (149/149 Test Suite Passed)

---

## 1. Executive Summary

In response to the P1.2 specification, an AST- and token-aware corner radius consistency heuristic was designed, implemented, and verified in `runtime/anti_slop.py`. 

The heuristic identifies suspiciously inconsistent corner-radius usage among peer components in coherent UI containers (e.g. peer cards with conflicting radii or form controls mixing rectangular and pill shapes) while strictly preserving intentional design hierarchy (e.g. cards containing smaller-radii buttons, circular avatars/chips, and multi-section layouts).

---

## 2. Architecture & Design Decisions

### 2.1 Token Normalization & Radius Parsing
- **CSS Variable Resolution:** Scans `:root` CSS block for custom properties (e.g. `--radius-sm: 4px`, `--radius-md: 8px`, `--radius-lg: 16px`, `--radius-full: 9999px`). When an inline style or CSS class references `var(--radius-*)`, it resolves to `(px_value, token_name)`. When raw pixel/rem values match the token's value, both are canonicalized to the token name, preventing false positives.
- **Tailwind Class Mapping:** Pre-mapped standard Tailwind border-radius classes (`rounded-none`, `rounded-sm`, `rounded`, `rounded-md`, `rounded-lg`, `rounded-xl`, `rounded-2xl`, `rounded-3xl`, `rounded-full`) to standard pixel equivalents.
- **Unit Support:** Handles `px`, `rem` (16px base), `0`, and percentage values (`50%`).

### 2.2 Role-Family Semantic Classification (`ASTElement.get_role_family()`)
Components are categorized into distinct structural families to avoid comparing apples to oranges:
- **`card`:** Cards, pricing tiers, panels, tiles, feature blocks, modal boxes (`<article>`, `.card`, `.tile`, `.box`, `.panel`, `.pricing-card`).
- **`control`:** Interactive inputs and triggers (`<button>`, `<input>`, `<select>`, `<textarea>`, `.btn`, `.button`, `.input`, `.select`, `.form-control`).
- **`badge-or-avatar`:** Avatars, user photos, chips, tags, circular icon badges (`.avatar`, `.chip`, `.badge`, `rounded-full`, `50%`, `9999px`).
- **`generic-container`:** Grouping parents, layout wrappers, grids, sections, toolbars.

### 2.3 Strict Scope Isolation & Hierarchy Preservation
- **Role Isolation:** Peer cards are evaluated strictly against peer cards. Controls are evaluated strictly against peer controls. A card with `16px` radius containing buttons with `6px` radius is recognized as intentional visual hierarchy and is never flagged.
- **Badge/Avatar Exemption:** Avatars (`50%` / circular) and pill badges within cards or lists are categorized as `badge-or-avatar` and exempted from peer card geometry checks.
- **Section Boundary Isolation:** Child `<section>` and `<article>` tags create containment boundaries; peer elements across different sections (e.g., `#hero` cards vs `#features` cards) are not aggregated into false positives.
- **Deduplication:** If a nested container is flagged, parent containers are automatically deduplicated to surface the exact, most localized component group.

### 2.4 Material Inconsistency Thresholds
To avoid noisy warnings on micro-variations while catching conspicuous design discrepancies:
1. **Cards:** Flagged when `max_radius - min_radius >= 4.0px` AND (`ratio >= 1.5` or `min_radius == 0.0`). For example: `8px` vs `24px` flags `WARN`, whereas `8px` vs `10px` or uniform `8px` passes.
2. **Controls:** Flagged when mixing pill controls (`>= 999px`) with rectangular controls in the same form/container, or when rectangular controls exhibit a material difference ($\ge 4.0\text{px}$ and ratio $\ge 1.5$).
3. **Contextual Tone Override:** When the brief specifies `asymmetric`, `eclectic`, or `experimental` tones, findings are downgraded from `WARN` to `INFO` with a contextual rationale.

---

## 3. Implementation Details

### 3.1 Modified Code: `runtime/anti_slop.py`
1. **Helper Functions & Constants:**
   - `TAILWIND_RADIUS_MAP`: Normalization dictionary for utility classes.
   - `parse_px_radius(val)`: Regex parser for `px` and `rem`.
   - `normalize_radius(val, css_tokens)`: Token-aware normalizer returning `(px_value, token_name)`.
2. **`ASTElement` Extensions:**
   - `get_role_family()`: Discovers whether node is a card, control, badge/avatar, or generic container.
   - `extract_radius(css_tokens, css_class_radii)`: Extracts inline and class-level corner radii.
3. **Core Analysis Algorithm:**
   - `find_inconsistent_radius_containers(html, css)`: Walks the DOM tree, analyzes scoped children by role family, and returns `[(container_desc, role_family, conflicting_radii, recommended_token), ...]`.
4. **Integration into `audit_website_content()`:**
   - Registered under rule ID `inconsistent-radius`.
   - Supports suppressions via `allow=["inconsistent-radius"]` or `allow=["radius"]`.
   - Downgrades severity to `INFO` for `asymmetric` / `eclectic` / `experimental` briefs.

---

## 4. Test Suite & Verification Results

### 4.1 Unit Tests Added in `tests/test_anti_slop_rules.py`
Seven dedicated, isolated test scenarios were implemented:

| # | Test Name | Scenario Tested | Result |
|---|---|---|:---:|
| 1 | `test_inconsistent_radius_peer_cards_warns` | Peer cards in `.pricing-grid` with `8px` vs `24px` radii | **PASS** (WARN emitted) |
| 2 | `test_inconsistent_radius_peer_cards_matching_passes` | Peer cards sharing unified `rounded-lg` utility token | **PASS** (Clean) |
| 3 | `test_inconsistent_radius_hierarchy_card_vs_button_passes` | Card (`16px`) containing Button (`6px`) (Intentional hierarchy) | **PASS** (Clean) |
| 4 | `test_inconsistent_radius_card_with_avatar_pill_passes` | Card (`12px`) containing circular Avatar (`50%`) and pill badge (`9999px`) | **PASS** (Clean) |
| 5 | `test_inconsistent_radius_separate_sections_not_aggregated` | Hero Section (`16px`) vs Features Section (`8px`) | **PASS** (Clean) |
| 6 | `test_inconsistent_radius_css_variable_token_normalization` | Card A with `var(--radius-md)` vs Card B with raw `8px` (`:root { --radius-md: 8px; }`) | **PASS** (Clean) |
| 7 | `test_inconsistent_radius_output_schema_and_asymmetric_tone` | Asymmetric brief tone downgrades warning to INFO with full schema compliance | **PASS** (INFO emitted) |

### 4.2 Test Execution Output
```
$ py -3 -m unittest atlas-skill/tests/test_anti_slop_rules.py
...................
----------------------------------------------------------------------
Ran 19 tests in 0.016s

OK

$ py -3 -m unittest discover -s "atlas-skill/tests" -p "test_*.py"
Ran 149 tests in 24.362s

OK
```

---

## 5. Strict Safety Boundary Verification

- [x] **`taste-skill/`:** 100% untouched (`git -C taste-skill status` confirms `nothing to commit, working tree clean`).
- [x] **`projek-webiste/saas-dashboard/`:** 100% untouched (source files confirm no modifications since baseline).
- [x] **P0 & P1.1 Preserved:** All 142 existing tests plus 7 new tests passed without any regressions.
- [x] **P2 Boundary:** No P2 changes implemented.
- [x] **Zero Dependencies:** Pure Python standard library implementation (`colorsys`, `html.parser`, `re`).

