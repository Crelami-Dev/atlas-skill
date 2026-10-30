# Atlas-Skill: Data Migration & Count Reconciliation Report

**Execution Date:** October 30, 2026  
**Pipeline Script:** `atlas-skill/tools/normalize_library.py`  
**Mapping Manifest:** `atlas-skill/data/source-map.json`  

---

## 1. Migration Overview & Source Counts

The Phase 1 migration transformed raw datasets from `taste-skill` and `atlas-frontend-design` into the versioned composite library format (`atlas-skill/data/`).

### Reconciled Record Counts

| Target Dataset (`atlas-skill/data/`) | Primary Layer | Source Project & File | Source Record Count | Normalized Record Count | Net Delta | Delta Explanation |
| :--- | :--- | :--- | :---: | :---: | :---: | :--- |
| `art-directions.json` | `art_direction` | `taste-skill/.../directions.json` | 20 | 20 | 0 | 1:1 direct transformation with provenance |
| `compositions.json` | `composition` | `atlas-frontend-design/.../library.json` | 50 | 50 | 0 | Preserved all 50 structural patterns |
| `compositions.json` | `composition` | `taste-skill/.../heroes.json` | 58 | 58 | 0 | Transformed 58 hero blueprints into composition layer |
| `compositions.json` | `composition` | `taste-skill/.../sections.json` | 185 | 185 | 0 | Transformed 185 section blueprints into composition layer |
| `palettes.json` | `palette` | `taste-skill/.../palettes.json` | 56 | 56 | 0 | 1:1 direct transformation with provenance |
| `typography.json` | `typography` | `taste-skill/.../type.json` | 44 | 44 | 0 | 1:1 direct transformation with font links |
| `sites.json` | `site` | `taste-skill/.../sites.json` | 202 | 202 | 0 | 1:1 direct transformation with steal notes |
| `app-shells.json` | `app_shell` | `taste-skill/.../app.json` | 5 | 5 | 0 | Extracted 5 shells; styles/kinds stored in metadata |
| **TOTAL** | — | **ALL SOURCES** | **620** | **620** | **0** | **100% record reconciliation** |

---

## 2. Superseded & Dropped Components

During Phase 0, a third repository (`project-atlas-v0.2.0-alpha`) was audited.
* **Component Dropped:** `project-atlas-v0.2.0-alpha/project-atlas/skills/atlas-design/references/composition-library.json` (20 items).
* **Justification:** Audit proved that this file was an early, truncated scaffold containing only 20 patterns with an obsolete schema (`schema_version`, `best_for`, `mobile_rule`, `failure_modes`). It is an exact subset of the 50 patterns present in `atlas-frontend-design/compositions/library.json`. Migrating both would have created duplicate pattern definitions.
* **Result:** The 20 scaffold records were safely dropped in favor of the canonical 50 patterns from `atlas-frontend-design`.

---

## 3. Duplicate Handling & Conflict Resolution Policy

1. **Namespace Collision Prevention:**
   Because Atlas patterns and Taste blueprints come from independent projects, IDs were prefixed with standard namespaces:
   * Atlas patterns: `atlas:{id}`
   * Taste heroes: `taste:hero:{id}`
   * Taste sections: `taste:section:{id}`
   * Taste art directions: `art-dir:{id}`
   * Taste palettes: `palette:{id}`
   * Taste typography: `type:{id}`
   * Taste sites: `site:{id}`
   * Taste app shells: `app:shell:{id}`
2. **Intra-Dataset Uniqueness:**
   The normalization script and validator enforce that within each target file, `id` values are unique. The validation run confirmed **0 duplicate IDs** across all 620 records.
3. **No Semantic Smearing:**
   No records were merged or deduplicated purely based on similar titles (e.g. `hero-product-shot` in Atlas vs `storefront-drawn-crop` in Taste). Both remain distinct, preserving their unique composition logic and DOM blueprints.

---

## 4. Traceable Source-to-Output Mapping

Every migrated record has an entry in `data/source-map.json` and `docs/phase-1/SOURCE_OUTPUT_MAPPING.csv`.
Sample entry:
```json
{
  "normalized_id": "taste:hero:field-headline-date",
  "layer": "composition",
  "source_project": "taste-skill",
  "source_file": "library/heroes.json",
  "source_id": "field-headline-date",
  "target_dataset": "compositions.json"
}
```
This ensures complete auditability for all future phases.

