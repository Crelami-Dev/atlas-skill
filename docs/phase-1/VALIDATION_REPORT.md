# Atlas-Skill: Library Validation & Tooling Report

**Tool:** `atlas-skill/tools/validate_library.py`  
**Schema Specification:** `atlas-skill/schemas/composite-library.schema.json`  
**Execution Engine:** Python Standard Library (Offline Custom Validator)  
**Execution Date:** October 30, 2026 (Updated post-corrective audit)  

---

## 1. Validator Architecture & Implementation Subset

`validate_library.py` was built as a zero-dependency Python 3.9+ standard library tool. It runs offline without requiring `pip install jsonschema` or any external package.

### 1.1 Draft 2020-12 Supported Subset vs Unsupported Features
* **Specification Target:** The schema is authored in JSON Schema Draft 2020-12 vocabulary.
* **Validation Mechanism:** Evaluated via a custom offline standard-library engine implementing:
  * Strict root container validation (`version`, `schema_type`, `item_count`, `items`).
  * Per-file count equality assertion (`item_count == len(items)`).
  * Unique ID pattern enforcement (`^[a-z0-9_:-]+$`) with intra-dataset and cross-dataset collision detection.
  * Layer and project enum validation.
  * Mandatory provenance validation, strictly requiring non-empty `attribution`.
  * Composition constraints (`page_types`, `density`, object `requires`).
* **Unverified Features / Limitations:** Advanced Draft 2020-12 features such as `$ref` remote dereferencing, `allOf`/`anyOf` dynamic schema composition, and meta-schema self-validation remain **unverified** because no conforming third-party JSON Schema engine is installed in the offline environment.

---

## 2. Unit Testing & Fixture Results

Validator correctness was verified using fixture-based unit tests in `atlas-skill/tests/test_validate_library.py`:

```text
py tests/test_validate_library.py -v
```

### Execution Results (12 / 12 Passed):
| Test Method | Fixture Tested | Purpose | Result |
| :--- | :--- | :--- | :---: |
| `test_valid_fixture_passes` | `valid_sample.json` | Positive baseline verification | **PASSED** |
| `test_missing_fields_fails` | `missing_fields.json` | Negative test: missing required `name` | **PASSED** |
| `test_invalid_types_and_enums_fails` | `invalid_types.json` | Negative test: bad layer, page_type, project | **PASSED** |
| `test_duplicate_ids_fails` | `duplicate_ids.json` | Negative test: ID collision detection | **PASSED** |
| `test_incomplete_provenance_fails` | `incomplete_provenance.json` | Negative test: missing provenance fields | **PASSED** |
| `test_missing_attribution_fails` | `missing_attribution.json` | Negative test: missing required attribution | **PASSED** |
| `test_empty_attribution_fails` | `empty_attribution.json` | Negative test: whitespace-only attribution | **PASSED** |
| `test_valid_attribution_passes` | `valid_sample.json` | Positive test: non-empty attribution accepted | **PASSED** |
| `test_item_count_matches_actual_items`| `valid_sample.json` | Positive test: count matches len(items) | **PASSED** |
| `test_item_count_mismatch_fails` | `item_count_mismatch.json` | Negative test: count != len(items) rejected | **PASSED** |
| `test_invalid_version_fails` | `invalid_version.json` | Negative test: bad semver version | **PASSED** |
| `test_cli_execution_and_exit_codes` | CLI subprocess | Verify exit code 0 on pass, 1 on fail | **PASSED** |

**Summary:** 12 tests passed in 0.370s with zero failures.

---

## 3. Full Library Validation Results

Execution of `validate_library.py` against all normalized datasets in `atlas-skill/data/`:

* **Command:** `py tools/validate_library.py --dir data/ --json docs/phase-1/VALIDATION_RESULTS.json`
* **Output:**
  ```text
  [PASS] Atlas Composite Library Validation Summary
  Files checked : 6
  Items checked : 620
  Errors        : 0
  Warnings      : 0
  ```
* **Dataset Breakdown & Per-File Counts:**
  * `art-directions.json`: `item_count = 20` (0 errors, 0 warnings)
  * `compositions.json`: `item_count = 293` (0 errors, 0 warnings)
  * `palettes.json`: `item_count = 56` (0 errors, 0 warnings)
  * `typography.json`: `item_count = 44` (0 errors, 0 warnings)
  * `sites.json`: `item_count = 202` (0 errors, 0 warnings)
  * `app-shells.json`: `item_count = 5` (0 errors, 0 warnings)

The complete machine-readable report is persisted in `atlas-skill/docs/phase-1/VALIDATION_RESULTS.json`.
