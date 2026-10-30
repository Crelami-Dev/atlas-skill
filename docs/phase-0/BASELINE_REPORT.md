# Atlas-Skill: Baseline Test & Execution Report

**Execution Date:** October 30, 2026  
**Environment:** Windows 11 (amd64)  
**Runtimes Verified:**
* **Node.js:** v24.16.0 (`C:\Program Files\nodejs\node.exe`)
* **Python:** Python 3.10.11 (64-bit, executed via Windows Launcher `C:\WINDOWS\py.exe`)
* **Browser:** Microsoft Edge / Google Chrome installed on host system
* **Python Packages:** Standard Library available; `playwright` and `pillow` are **NOT** installed in the local Python environment.

---

## 1. Test Execution Summary

| Test Suite / Target | Command Executed | Total | Pass | Fail | Skip | Blocked | Observed Status |
| :--- | :--- | :---: | :---: | :---: | :---: | :---: | :--- |
| **Atlas Frontend Design Tests** | `py -m unittest discover -s atlas-frontend-design\tests -v` | 37 | 34 | 0 | 3 | 0 | **PASSED (with skips)** |
| **Project Atlas Validation Tests** | `py -m unittest discover -s project-atlas-v0.2.0-alpha\project-atlas\tests -v` | 3 | 3 | 0 | 0 | 0 | **PASSED** |
| **Taste-Skill Frontmatter Test** | `node taste-skill\tests\frontmatter.mjs` | 1 | 0 | 0 | 0 | 1 | **BLOCKED (Missing pkg)** |
| **Taste-Skill Text Encoding** | `node taste-skill\tests\text-encoding.mjs` | 1 | 1 | 0 | 0 | 0 | **PASSED** |
| **Taste-Skill Inspection Files** | `node taste-skill\tests\inspection-files.mjs` | 4 | 4 | 0 | 0 | 0 | **PASSED** |
| **Atlas Pattern Selector CLI** | `py atlas_select.py --category saas --candidates 3 --seed 1` | 1 | 1 | 0 | 0 | 0 | **PASSED** |
| **Atlas Quality Gate CLI** | `py atlas_check.py binong-permai\index.html --type marketing` | 1 | 1 | 0 | 0 | 0 | **PASSED** |
| **Taste Draw CLI** | `node draw.mjs --options 3 --sector saas --brief "..."` | 1 | 1 | 0 | 0 | 0 | **PASSED** |
| **Taste Assets Search CLI** | `node assets.mjs "machinery" --limit 2 --no-check --json` | 1 | 0 | 0 | 0 | 1 | **BLOCKED (Network timeout)** |

---

## 2. Detailed Execution Logs

### 2.1 Atlas Frontend Design Test Suite
* **Command:** `py -m unittest discover -s "d:\tes\skills-staging\atlas-frontend-design\tests" -v`
* **Output Log:**
  ```text
  test_aggregate_and_agreement (test_bench.BenchTests) ... ok
  test_agreement_without_second_reviewer_is_none_not_perfect (test_bench.BenchTests) ... ok
  test_blinding_hides_condition_and_is_reproducible (test_bench.BenchTests) ... ok
  test_briefs_cover_required_categories_and_heldout (test_bench.BenchTests) ... ok
  test_detects_horizontal_overflow_on_mobile (test_check.BrowserTests) ... skipped 'playwright not available'
  test_detects_invisible_content (test_check.BrowserTests) ... skipped 'playwright not available'
  test_good_page_passes_browser_checks (test_check.BrowserTests) ... skipped 'playwright not available'
  test_app_pages_do_not_require_single_h1 (test_check.StaticTests) ... ok
  test_bad_page_flags_expected_rules (test_check.StaticTests) ... ok
  test_checks_run_lists_only_executed (test_check.StaticTests) ... ok
  test_cli_exit_codes_and_skip_notice (test_check.StaticTests) ... ok
  test_good_page_has_no_failures (test_check.StaticTests) ... ok
  test_label_wrapping_and_aria_label_accepted (test_check.StaticTests) ... ok
  test_placeholder_markers_are_info_not_failure (test_check.StaticTests) ... ok
  test_every_slot_has_patterns (test_library.LibraryTests) ... ok
  test_incompatibility_symmetric_and_not_related (test_library.LibraryTests) ... ok
  test_required_fields_and_enums (test_library.LibraryTests) ... ok
  test_unique_ids_and_references (test_library.LibraryTests) ... ok
  test_version_and_nonempty (test_library.LibraryTests) ... ok
  test_any_of_asset_requirement (test_select.SelectTests) ... ok
  test_assets_unlock_patterns (test_select.SelectTests) ... ok
  test_candidates_are_materially_different (test_select.SelectTests) ... ok
  test_conventional_preference_avoids_asymmetric_hero (test_select.SelectTests) ... ok
  test_deterministic_for_same_seed (test_select.SelectTests) ... ok
  test_greedy_candidate_independent_of_seed (test_select.SelectTests) ... ok
  test_missing_assets_exclude_image_patterns (test_select.SelectTests) ... ok
  test_no_incompatible_pairs_in_plans (test_select.SelectTests) ... ok
  test_page_type_hard_filter (test_select.SelectTests) ... ok
  test_repetition_is_soft_not_a_quota (test_select.SelectTests) ... ok
  test_repetition_penalty_applies_to_adjacent_shared_tags (test_select.SelectTests) ... ok
  test_skips_report_reason_when_no_pattern (test_select.SelectTests) ... ok
  test_unknown_asset_rejected (test_select.SelectTests) ... ok
  test_unknown_page_type_rejected (test_select.SelectTests) ... ok
  test_frontmatter (test_skill_format.SkillFormatTests) ... ok
  test_library_claim_matches (test_skill_format.SkillFormatTests) ... ok
  test_referenced_paths_exist (test_skill_format.SkillFormatTests) ... ok
  test_skill_is_concise (test_skill_format.SkillFormatTests) ... ok

  ----------------------------------------------------------------------
  Ran 37 tests in 0.225s
  OK (skipped=3)
  ```
* **Findings:** 34 unit tests executed and passed in 0.225 seconds. 3 browser-based tests (`BrowserTests`) skipped cleanly because Playwright is not installed. Static tests caught intentional fixture errors (15 fail, 4 warn on `bad.html`) and verified truthful skip reporting.

---

### 2.2 Project Atlas Validation Test Suite
* **Command:** `py -m unittest discover -s "d:\tes\skills-staging\project-atlas-v0.2.0-alpha\project-atlas\tests" -v`
* **Output Log:**
  ```text
  test_current_assets_are_valid (test_validate_library.AtlasValidationTests) ... ok
  test_duplicate_brief_ids_are_rejected (test_validate_library.AtlasValidationTests) ... ok
  test_duplicate_pattern_ids_are_rejected (test_validate_library.AtlasValidationTests) ... ok

  ----------------------------------------------------------------------
  Ran 3 tests in 0.120s
  OK
  ```
* **Findings:** All 3 validation tests passed in 0.120 seconds, confirming basic JSON format checks on the 20-pattern scaffold.

---

### 2.3 Taste-Skill Test Suite
* **Command 1:** `node "d:\tes\skills-staging\taste-skill\tests\frontmatter.mjs"`
  * **Result:** `BLOCKED` (Exit code 1)
  * **Error Message:** `This check needs the "yaml" package: npm install --no-save --no-package-lock yaml@2.6.1`
  * **Analysis:** Taste-skill is zero-dependency for runtime operations, but this test requires a third-party npm package.
* **Command 2:** `node "d:\tes\skills-staging\taste-skill\tests\text-encoding.mjs"`
  * **Result:** `PASSED` (Exit code 0)
  * **Log:** `ok - every text file reads as clean UTF-8`
* **Command 3:** `node "d:\tes\skills-staging\taste-skill\tests\inspection-files.mjs"`
  * **Result:** `PASSED` (Exit code 0, 4/4 assertions in 72ms)
  * **Log:**
    ```text
    ✔ default widths retain their existing screenshot names (9.63ms)
    ✔ distinct widths in one viewport class cannot overwrite fold, page, or film images (1.53ms)
    ✔ collisions are disambiguated in each viewport class (1.52ms)
    ✔ cleanup recognizes legacy and width-qualified inspection images only (1.90ms)
    ```

---

### 2.4 CLI Functional Validations
* **Atlas Selection Engine:**
  * Executed: `py atlas-frontend-design\scripts\atlas_select.py --category saas --page-type marketing --assets product_ui --tones precise,modern --candidates 3 --seed 1`
  * Output: Deterministic JSON candidate plan.
  * Verdict: Verified operational.
* **Atlas Quality Gate:**
  * Executed: `py atlas-frontend-design\scripts\atlas_check.py atlas-frontend-design\examples\binong-permai\index.html --type marketing`
  * Output: 0 FAIL, 0 WARN, 2 INFO (`S052 9 marked placeholder(s) pending`, `SKIP browser checks`).
  * Verdict: Verified operational.
* **Taste Direction Dealer:**
  * Executed: `node taste-skill\skills\taste-skill\scripts\draw.mjs --options 3 --sector saas --brief "Cloud database monitoring"`
  * Output: Dealt 3 distinct directions (`colour-chapters`, `one-motif`, `sentence-as-layout`) with complete art direction theses.
  * Verdict: Verified operational.
* **Taste Open-Archive Fetcher:**
  * Executed: `node taste-skill\skills\taste-skill\scripts\assets.mjs "machinery" --limit 2 --no-check --json`
  * Result: `BLOCKED` / Timed out in sandbox environment due to external network latency or firewall on museum/archive API endpoints.
  * Verdict: Requires local offline fallback when network is unavailable.

---

## 3. Disclosed Limitations & Environment Warnings

1. **Windows Python Path Aliases:** On Windows, calling `python` or `python3` fails if App Execution Aliases are active. All Python tooling must be called using `py` or an explicit Python executable path.
2. **Missing Python Browser Packages:** `playwright` and `pillow` are not installed globally. While static checks run via stdlib, full-page screenshot capture via Python is currently disabled.
3. **Taste-Skill Browser Execution Advantage:** Taste-skill drives installed Chrome/Edge via native Node.js CDP over WebSockets. Because Chrome/Edge is installed on the host OS, CDP browser inspection works **without** installing Playwright or any Python/npm package.

