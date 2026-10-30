# Atlas-Skill: Phase 1 Corrective Audit Report

**Audit Date:** October 30, 2026  
**Auditor:** Senior Software Architect, QA Lead  
**Scope:** Phase 1 Deliverables Re-audit & Corrective Reconciliation  
**Target:** `atlas-skill/`  

---

## 1. Executive Summary

This corrective audit pass was conducted within **Phase 1** to address specific verification gaps and ambiguities identified during review:
1. **Provenance Contract Consistency:** Reconciled `provenance.attribution` across the JSON Schema, Python validator, unit tests, and normalized data. Attribution is now strictly **required** by contract and enforced by hard validator errors.
2. **JSON Schema Compliance Clarification:** Replaced ambiguous claims of "JSON Schema Draft 2020-12 (offline stdlib compliant)" with explicit technical documentation of the custom Python Standard Library validator subset and unverified Draft 2020-12 features.
3. **Dataset `item_count` Semantics:** Resolved ambiguous counting semantics by formally defining `item_count` as the exact record count within an individual dataset file (`len(items)`). Mismatches now trigger hard validation errors and are covered by dedicated negative tests.
4. **Reproducible Integrity & Hash Verification:** Re-executed all integrity checks, confirming 100% SHA-256 hash matches across all 7 manifest entries and zero modifications to source repositories.
5. **Reconciliation of 620 Records & Scaffold Exclusion:** Verified the exact count breakdown of 620 normalized records and documented the empirical evidence justifying the exclusion of 20 obsolete scaffold patterns from `project-atlas-v0.2.0-alpha`.

---

## 2. Task 1: Provenance Contract Consistency

### 2.1 The Issue Identified
In the initial Phase 1 release:
* `SCHEMA_DESIGN.md` documented `attribution` under provenance.
* `schemas/composite-library.schema.json` defined `attribution` under `properties`, but omitted it from `"required": ["source_project", "source_file", "source_id", "license"]`.
* `tools/validate_library.py` checked `source_project`, `source_file`, `source_id`, and `license`, but did not validate `attribution`.

### 2.2 Corrective Actions Taken
1. **Schema Updated (`schemas/composite-library.schema.json`):**
   * Added `"attribution"` to `provenance.required`:
     ```json
     "required": ["source_project", "source_file", "source_id", "license", "attribution"]
     ```
   * Enforced non-empty string constraint:
     ```json
     "attribution": {
       "type": "string",
       "minLength": 1,
       "description": "Mandatory attribution, copyright, or provenance statement"
     }
     ```
2. **Validator Updated (`tools/validate_library.py`):**
   * Lines 154–157 now enforce:
     ```python
     attr = prov.get("attribution")
     if not attr or not isinstance(attr, str) or not attr.strip():
       report.add_error(
           file_path,
           item_id,
           "Missing or empty required field 'attribution' in provenance",
       )
```
3. **Unit Tests Added (`tests/test_validate_library.py`):**
   * `test_missing_attribution_fails`: Negative test verifying that missing `attribution` triggers a validation error.
   * `test_empty_attribution_fails`: Negative test verifying that whitespace-only `attribution` (`"   "`) triggers an error.
   * `test_valid_attribution_passes`: Positive test confirming valid attribution strings pass cleanly.
4. **Data Verification:**
   * Direct audit across all 620 normalized records in `atlas-skill/data/` confirmed that **100% of records already contain non-empty attribution strings** (0 missing, 0 empty).

---

## 3. Task 2: Clarification of JSON Schema Compliance

### 3.1 Clarification of Validation Mechanism
* **Claim Re-evaluated:** The previous phrase *"JSON Schema Draft 2020-12 (offline stdlib compliant)"* was inaccurate because the Python Standard Library does not include an implementation of the JSON Schema specification (such as the third-party `jsonschema` library).
* **Actual Mechanism:** The validation engine (`tools/validate_library.py`) is a **custom, offline Python Standard Library validator** tailored specifically for the Atlas composite library.

### 3.2 Supported Validation Subset vs Unsupported Draft 2020-12 Features

| Feature Category | Specific Rule / Keyword | Implementation Status in `validate_library.py` |
| :--- | :--- | :--- |
| **Container & Types** | Object root, array `items`, string types | **SUPPORTED** via `isinstance()` checks |
| **Required Keys** | `version`, `schema_type`, `item_count`, `items`, `id`, `layer`, `name`, `provenance` | **SUPPORTED** via dict key membership checks |
| **Pattern / Regex** | `id` (`^[a-z0-9_:-]+$`), `version` (`^\d+\.\d+\.\d+$`) | **SUPPORTED** via `re.compile()` |
| **Enums** | `schema_type`, `layer`, `source_project`, `page_types`, `density` | **SUPPORTED** via Python `set` membership |
| **Count Consistency** | `item_count == len(items)` | **SUPPORTED** via Python integer comparison |
| **ID Uniqueness** | Global & local collision detection | **SUPPORTED** via Python set tracking |
| **URI Dereferencing** | `$ref`, remote schemas | **UNSUPPORTED** (No network/remote schema resolution) |
| **Subschema Logic** | `allOf`, `anyOf`, `oneOf`, `not`, `if`/`then`/`else` | **UNSUPPORTED** |
| **Meta-Schema Self-Validation**| Validating schema against Draft 2020-12 core meta-schema | **UNVERIFIED** (No third-party Draft 2020-12 validator in environment) |

* **Offline Trade-off Decision:** Retaining a zero-dependency Python standard library validator remains the correct choice (DEC-001) to ensure the skill operates in sandboxed, air-gapped, or minimal CI environments without forcing `pip install jsonschema`.

---

## 4. Task 3: Dataset `item_count` Semantics

### 4.1 Unambiguous Definition
* **`item_count` Definition:** The exact integer count of normalized records contained within **that individual dataset file** (`len(items)`).
* **Global Total Definition:** The aggregate count across all datasets (620 records), calculated as the sum of all individual `item_count` properties, and tracked in `data/source-map.json` and `docs/phase-1/COUNT_RECONCILIATION.csv`.

### 4.2 Schema, Validator & Test Alignment
1. **Schema Updated:** `item_count` is now in root `required`: `["version", "schema_type", "item_count", "items"]`.
2. **Validator Enforced:** If `item_count != len(items)`, a **HARD ERROR** is raised.
3. **Tests Added:**
   * `test_item_count_matches_actual_items`: Positive verification.
   * `test_item_count_mismatch_fails`: Negative test verifying that `item_count: 999` with 1 item raises an explicit error.
4. **Data Verified:**
   * `art-directions.json`: `item_count = 20` (actual items = 20)
   * `compositions.json`: `item_count = 293` (actual items = 293)
   * `palettes.json`: `item_count = 56` (actual items = 56)
   * `typography.json`: `item_count = 44` (actual items = 44)
   * `sites.json`: `item_count = 202` (actual items = 202)
   * `app-shells.json`: `item_count = 5` (actual items = 5)
   * Sum of declared counts: **620**.

---

## 5. Task 4: Reproduction of Integrity & Hash Verification

* **Command Executed:** SHA-256 verification against `docs/phase-1/HASH_MANIFEST.csv`.
* **Result:** **7 / 7 files MATCH 100%** with zero hash mismatches.
* Evidence recorded in `docs/phase-1/CORRECTIVE_HASH_VERIFICATION.csv`.

---

## 6. Task 5: 620-Record Reconciliation & Scaffold Exclusion

### 6.1 Record Breakdown
* 20 Art Directions (`taste-skill/skills/taste-skill/library/directions.json`)
* 50 Atlas Patterns (`atlas-frontend-design/compositions/library.json`)
* 58 Taste Heroes (`taste-skill/skills/taste-skill/library/heroes.json`)
* 185 Taste Sections (`taste-skill/skills/taste-skill/library/sections.json`)
* 56 Palettes (`taste-skill/skills/taste-skill/library/palettes.json`)
* 44 Typography Systems (`taste-skill/skills/taste-skill/library/type.json`)
* 202 Reference Sites (`taste-skill/skills/taste-skill/library/sites.json`)
* 5 App Shells (`taste-skill/skills/taste-skill/library/app.json`)
* **Total Active Records:** **620**.

### 6.2 Project-Atlas 20 Patterns Exclusion Evidence
* **Source:** `project-atlas-v0.2.0-alpha/project-atlas/skills/atlas-design/references/composition-library.json`
* **Audit Findings:**
  1. Contains 20 patterns with IDs like `hero-type-led`, `hero-split`, `hero-bento`, `pricing-comparison`.
  2. Direct cross-check against `atlas-frontend-design` revealed only 2 shared ID names, with 18 differing.
  3. The schema in `project-atlas` lacks all scoring fields required by `atlas_select.py` (`categories`, `tones`, `density`, `requires.assets`, `goals`).
  4. The 20 scaffold patterns were early conceptual placeholders from `crafted-web-design`. Their concepts are completely represented with higher specificity by Atlas's 50 patterns and Taste's 243 blueprints.
* **Exclusion Confirmation:** The 20 records remain **EXCLUDED** to prevent duplicate, lower-quality records in the unified selector.

